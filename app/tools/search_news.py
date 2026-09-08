from tavily import AsyncTavilyClient
from langchain_core.tools import tool

from app.config import TAVILY_API_KEY


client = AsyncTavilyClient(
    api_key=TAVILY_API_KEY
)


@tool
async def search_news(query: str) -> str:
    """
    Search the web for recent news and developments.

    Use this tool when the user asks about recent events,
    company news, product launches, announcements, or other
    time-sensitive information.

    Args:
        query: Specific news search query.

    Returns:
        Relevant recent news results.
    """

    try:

        response = await client.search(
            query=query,
            topic="news",
            max_results=5,
        )

        results = response.get("results", [])

        if not results:
            return "No relevant news results were found."

        formatted_results = []

        for index, result in enumerate(results, start=1):

            title = result.get("title", "No title")
            url = result.get("url", "No URL")
            content = result.get("content", "No content")

            formatted_results.append(
                f"""
Result {index}:
Title: {title}
URL: {url}
Content: {content}
"""
            )

        return "\n".join(formatted_results)

    except Exception as e:

        raise RuntimeError(
            f"News search failed: {str(e)}"
        ) from e