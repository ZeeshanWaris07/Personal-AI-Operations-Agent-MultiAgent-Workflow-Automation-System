from app.context import AgentContext
from app.state import AgentState


def handle_tool_result(
    state: AgentState,
    runtime: AgentContext,
):
    results = state.get("tool_result")

    if not results:
        return {}


    result_list = results if isinstance(results, list) else [results]

    any_failed = False
    any_retryable = False

    for result in result_list:

        for entry in reversed(runtime.context.tool_call_history):
            if (
                entry["tool_call_id"] == result.tool_call_id
                and entry["status"] == "pending"
            ):
                entry["status"] = "success" if result.status == "success" else "failed"
                entry["error_type"] = getattr(result, "error_type", None)
                entry["message"] = getattr(result, "message", None)
                entry["result"] = getattr(result, "result", None)
                break  


        if result.status != "success":
            any_failed = True
            if getattr(result, "retryable", False):
                any_retryable = True


    if not any_failed:
        runtime.context.retry_count = 0
    elif any_retryable:
        runtime.context.retry_count += 1

    return {}