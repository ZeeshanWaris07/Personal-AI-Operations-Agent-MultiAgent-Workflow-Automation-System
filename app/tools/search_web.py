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

    Use this tool when you need to discover relevant
    webpages, articles, companies, documentation, or
    other publicly available information.

    Args:
        query: A clear and specific web search query.

    Returns:
        A formatted list of search results containing
        the title, URL, and relevant content snippet.
    """

    try:

        response = await client.search(
            query=query,
            max_results=5,
        )

        results = response.get("results", [])

        if not results:
            return "No relevant search results were found."

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
            f"Web search failed: {str(e)}"
        ) from e