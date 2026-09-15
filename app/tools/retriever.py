
from langchain_core.tools import tool


def create_rag_tools(rag_pipeline):

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

        result = rag_pipeline.retrieve(query)

        print("=" * 80)
        print("RETRIEVED DOCUMENTS")
        print(result)

        return result

    return [retrieve_documents]
