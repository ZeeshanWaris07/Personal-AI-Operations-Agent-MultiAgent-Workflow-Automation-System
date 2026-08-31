from tavily import AsyncTavilyClient
from langchain_core.tools import tool

from app.config import TAVILY_API_KEY


client = AsyncTavilyClient(
    api_key=TAVILY_API_KEY
)


@tool
async def search_web(query: str) -> str:
    """
    Search the web for current information.

    Args:
        query: Search query.

    Returns:
        Relevant search results.
    """

    try:

        response = await client.search(
            query=query,
            max_results=5,
        )

        return str(response)

    except Exception as e:

        return f"Web search failed: {str(e)}"