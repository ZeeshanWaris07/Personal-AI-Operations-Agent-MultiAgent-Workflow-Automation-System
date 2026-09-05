from tavily import AsyncTavilyClient
from langchain_core.tools import tool

from app.config import TAVILY_API_KEY


client = AsyncTavilyClient(
    api_key=TAVILY_API_KEY
)


@tool
async def fetch_webpage(url: str) -> str:
    """
    Extract the main content from a webpage.

    Args:
        url: URL of the webpage.

    Returns:
        Extracted webpage content.
    """

    try:
        response = await client.extract(
            urls=[url]
        )

        results = response.get("results", [])

        if not results:
            return "Could not extract content from the webpage."

        return results[0].get("raw_content", "")

    except Exception as e:
        raise RuntimeError(
            f"Webpage extraction failed: {str(e)}"
        ) from e