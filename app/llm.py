from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

load_dotenv()

# llm = ChatGroq(
#     model="openai/gpt-oss-120b",  # Switched to a higher-capacity model
#     temperature=0.0,              # Enforce a safe cap under the minute limit
#     max_retries=3                 # Automatically pauses and retries if a 429 hits
# )

llm = ChatOllama(
    model = 'qwen3:8b'
)