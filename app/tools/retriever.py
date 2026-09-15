from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from app.main import vector_store,bm25_retriever,reranker
from sentence_transformers import CrossEncoder


def make_pairs(question,documents):
        pairs = []

        for doc in documents:
            pairs.append((question,doc.page_content))

        return pairs


def format_docs(docs):

            context = []

            for doc in docs:
                context.append(
                    f"""
Source: {doc.metadata['source']}
Page: {doc.metadata['page']}


{doc.page_content}
                    """
                )
            return "\n\n".join(context)

def make_reranked_docs(scores,docs):
    reranked_docs = sorted(
        zip(scores,docs),
        key= lambda x: x[0],
        reverse=True
    )
    return [doc for score,doc in reranked_docs]


@tool
def retrieve_documents(query: str):
    """
    Retrieve relevant information from the user's private
    knowledge base, including uploaded documents, resume,
    projects, notes, and other stored personal information.

    Use this tool when answering requires information about
    the user or their private documents.

    Do not use this tool for general web or external information.
    """

    search_retriever = vector_store.as_retriever(
            search_type = "mmr",
            search_kwargs = {
                "k" : 10,
                "fetch_k" : 20
            }
        )

    retriever = EnsembleRetriever(
        retrievers=[bm25_retriever,search_retriever],
        weights=[0.4,0.6]
    )

    retrieved_chunks = retriever.invoke(query)

    for i, doc in enumerate(retrieved_chunks):
            print("=" * 80)
            print(f"BEFORE RERANKING - CHUNK {i + 1}")
            print("PAGE:", doc.metadata.get("page"))
            print(doc.page_content[:500])

    pairs = make_pairs(query,retrieved_chunks)

    scores = reranker.predict(pairs)

    reranked_docs = make_reranked_docs(scores,retrieved_chunks)

    top_chunks = reranked_docs[:5]

    for i, doc in enumerate(top_chunks):
        print("=" * 80)
        print(f"CHUNK {i + 1}")
        print("SOURCE:", doc.metadata.get("source"))
        print("PAGE:", doc.metadata.get("page"))
        print(doc.page_content)

    return format_docs(top_chunks)