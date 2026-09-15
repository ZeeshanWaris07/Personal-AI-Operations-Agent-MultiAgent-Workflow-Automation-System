from langchain_classic.retrievers import EnsembleRetriever
from sentence_transformers import CrossEncoder

class RAGPipeline():
    def __init__(self,vector_store,bm25_retriever):

        self.vector_store = vector_store
        self.bm25_retriever = bm25_retriever

        self.search_retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 10,
                "fetch_k": 20
        }
        )

        self.retriever = EnsembleRetriever(
            retrievers=[self.bm25_retriever,self.search_retriever],
            weights=[0.4, 0.6]
        )

        self.reranker = CrossEncoder(
            "BAAI/bge-reranker-base"
        )

    def _make_pairs(self, query, documents):

        return [
            (query, doc.page_content)
            for doc in documents
        ]

    def _rerank(self, query, documents):

        pairs = self._make_pairs(query, documents)

        scores = self.reranker.predict(pairs)

        ranked = sorted(
            zip(scores, documents),
            key=lambda x: x[0],
            reverse=True
        )

        return [
            doc
            for score, doc in ranked
        ]

    def _format_docs(self, documents):

        context = []

        for doc in documents:

            context.append(
                f"""
Source: {doc.metadata.get("source")}
Page: {doc.metadata.get("page")}

{doc.page_content}
"""
            )

        return "\n\n".join(context)

    def retrieve(self, query):

        documents = self.retriever.invoke(query)

        reranked_docs = self._rerank(
            query,
            documents
        )

        top_chunks = reranked_docs[:5]

        return self._format_docs(top_chunks)

