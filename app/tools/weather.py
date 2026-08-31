import httpx

from langchain_core.tools import tool


@tool
async def get_weather(city: str) -> str:
    """
    Get the current weather for a city.

    Args:
        city: Name of the city.

    Returns:
        Current weather information.
    """

    try:

        url = "https://wttr.in"

        async with httpx.AsyncClient(timeout=10) as client:

            response = await client.get(
                f"{url}/{city}",
                params={
                    "format": "3"
                },
            )

            response.raise_for_status()

            return response.text

    except httpx.TimeoutException:

        return "Weather service timed out."

    except httpx.HTTPError as e:

        return f"Weather service error: {str(e)}"

    except Exception as e:

        return f"Unexpected weather error: {str(e)}"