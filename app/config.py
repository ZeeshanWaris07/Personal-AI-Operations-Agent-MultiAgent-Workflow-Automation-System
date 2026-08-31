import os

from dotenv import load_dotenv


load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not configured")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not configured")