from langchain_core.messages import ToolMessage
from app.state import AgentState
def handle_duplicate_tools_node(state: AgentState):
    """
    If all tool calls were filtered out, create dummy ToolMessage responses
    informing the LLM that these exact calls were already processed.
    """
    messages = state.get("messages", [])
    last_message = messages[-1]
    
    # Extract tool calls from the last message
    tool_calls = (
        last_message.get("tool_calls", [])
        if isinstance(last_message, dict)
        else getattr(last_message, "tool_calls", [])
    )
    
    synthetic_messages = []
    for tc in tool_calls:
        tool_call_id = tc.get("id", "unknown_id")
        tool_name = tc.get("name", "tool")
        
        # Inject a message telling the model the result is already in context
        synthetic_messages.append(
            ToolMessage(
                content=f"[System Notice]: The tool call '{tool_name}' with these arguments was already executed previously. Please rely on the previous tool results in the conversation history to formulate your response.",
                tool_call_id=tool_call_id,
            )
        )
        
    return {"messages": synthetic_messages}