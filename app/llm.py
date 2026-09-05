from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
)