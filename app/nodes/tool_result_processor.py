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
        # Safely extract tool_call_id from object or dictionary representation
        if isinstance(result, dict):
            res_call_id = result.get("tool_call_id")
            res_status = result.get("status")
            res_error_type = result.get("error_type")
            res_message = result.get("message")
            res_value = result.get("result")
            res_retryable = result.get("retryable", False)
        else:
            res_call_id = getattr(result, "tool_call_id", None)
            res_status = getattr(result, "status", None)
            res_error_type = getattr(result, "error_type", None)
            res_message = getattr(result, "message", None)
            res_value = getattr(result, "result", None)
            res_retryable = getattr(result, "retryable", False)

        # Update matching pending history entry
        for entry in reversed(runtime.context.tool_call_history):
            if (
                res_call_id
                and entry["tool_call_id"] == res_call_id
                and entry["status"] == "pending"
            ):
                entry["status"] = "success" if res_status == "success" else "failed"
                entry["error_type"] = res_error_type
                entry["message"] = res_message
                entry["result"] = res_value
                break

        # Track batch status for retry policy
        if res_status != "success":
            any_failed = True
            if res_retryable:
                any_retryable = True

    if not any_failed:
        runtime.context.retry_count = 0
    elif any_retryable:
        runtime.context.retry_count += 1

    return {}