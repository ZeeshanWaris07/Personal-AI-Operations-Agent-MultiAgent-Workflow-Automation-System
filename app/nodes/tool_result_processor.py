from app.state import AgentState
from app.context import AgentContext


def handle_tool_result(
    state: AgentState,
    runtime: AgentContext,
):

    result = state.get("tool_result")

    if result is None:
        return {}

    for entry in reversed(runtime.context.tool_call_history):
        if entry["tool"] != result.tool or entry["status"] != "pending":
            continue

        entry["status"] = "success" if result.status == "success" else "failed"
        entry["error_type"] = result.error_type
        entry["message"] = result.message
        entry["result"] = result.result
        break

    if result.status == "success":

        runtime.context.retry_count = 0

        return {}

    if result.retryable:

        runtime.context.retry_count += 1

    return {}