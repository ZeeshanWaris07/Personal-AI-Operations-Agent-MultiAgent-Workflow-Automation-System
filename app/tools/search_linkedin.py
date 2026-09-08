from tavily import AsyncTavilyClient
from langchain_core.tools import tool

from app.config import TAVILY_API_KEY


client = AsyncTavilyClient(
    api_key=TAVILY_API_KEY
)


@tool
async def search_linkedin(query: str) -> str:
    """
    Search for publicly available LinkedIn profiles and company pages.

    Use this tool when the user asks to find people, companies,
    employees, founders, recruiters, or other information specifically
    related to LinkedIn.

    Args:
        query: Specific LinkedIn search query.

    Returns:
        Relevant publicly available LinkedIn search results.
    """

    try:
        response = await client.search(
            query=f"site:linkedin.com {query}",
            max_results=5,
        )

        results = response.get("results", [])

        if not results:
            return "No relevant public LinkedIn results were found."

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
            f"LinkedIn search failed: {str(e)}"
        ) from e