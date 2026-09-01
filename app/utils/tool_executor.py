from app.utils.error_classifier import classify_error
from app.utils.tool_result import ToolExecutionResult


async def execute_tool_async(
    tool,
    arguments: dict,
) -> ToolExecutionResult:

    tool_name = tool.name

    try:

        result = await tool.ainvoke(
            arguments
        )

        return ToolExecutionResult(
            tool=tool_name,
            status="success",
            result=str(result),
        )

    except Exception as error:

        error_info = classify_error(error)

        return ToolExecutionResult(
            tool=tool_name,
            status="failed",
            error_type=error_info["error_type"],
            message=str(error),
            retryable=error_info["retryable"],
        )