from langchain_core.messages import AIMessage

def create_filter_ai_message(state):

    last_message = state['messages'][-1]

    allowed_tool_calls = state.get(
        'allowed_tool_calls',
        []
    )

    print(allowed_tool_calls)

    filtered_message = AIMessage(
        content=getattr(last_message, "content", ""),
        tool_calls=allowed_tool_calls,
    )

    return {
        'messages' : [filtered_message]
    }