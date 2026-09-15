from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers import BM25Retriever
import os

def load_documents(folder_name):

    documents = []

    for file in os.listdir(folder_name):
        if file.endswith('.pdf'):

            loader = PyPDFLoader(os.path.join(folder_name,file))
            documents.extend(loader.load())

    return documents

def ingestion():
    doc_pages = load_documents('user_docs')

    print(len(doc_pages))
    print(doc_pages[0].page_content)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 400,
        chunk_overlap = 40
    )

    chunks = splitter.split_documents(doc_pages)

    bm25_retriever = BM25Retriever.from_documents(chunks)

    embeddings = HuggingFaceEmbeddings(
        model_name = 'BAAI/bge-small-en-v1.5'
    )

    persist_directory = 'vector_db'

    if not os.path.exists(persist_directory):
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )

    else:
        vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )

    return vector_db,bm25_retriever