from langgraph.runtime import Runtime

from app.context import AgentContext
from app.state import AgentState

from app.utils.tool_history import (
    create_tool_signature,
    find_previous_call,
    record_tool_call,
)


def tool_controller(
    state: AgentState,
    runtime: Runtime[AgentContext],
):


    messages = state.get("messages", [])
    if not messages:
        print("No messages found in state")
        return {"allowed_tool_calls": []}

    last_message = messages[-1]
    
    if isinstance(last_message, dict):
        tool_calls = last_message.get("tool_calls", [])
    else:
        tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls:
        print("No tool calls")
        return {"allowed_tool_calls": []}

    print("Tool Calls")

    allowed_calls = []

    for tool_call in tool_calls:

        tool_name = tool_call["name"]

        arguments = tool_call.get(
            "args",
            {},
        )

        signature = create_tool_signature(
            tool_name,
            arguments,
        )

        previous = find_previous_call(
            runtime.context.tool_call_history,
            signature,
        )

        if previous:

            if previous["status"] == "success":

                print(
                    f"[Tool Controller] "
                    f"Skipping duplicate: {signature}"
                )

                continue

        tool_call_id = tool_call.get("id") or f"{tool_name}:{signature}:{len(runtime.context.tool_call_history)}"

        record_tool_call(
            runtime.context.tool_call_history,
            tool_name=tool_name,
            tool_call_id=tool_call_id,
            signature=signature,
            status="pending",
        )

        allowed_calls.append(tool_call)

    return {
        "allowed_tool_calls": allowed_calls
    }