from app.state import AgentState


def research_placeholder(state: AgentState):

    return {
        "messages": [
            {
                "role": "assistant",
                "content": "Research Agent will handle this request."
            }
        ]
    }


def planning_placeholder(state: AgentState):

    return {
        "messages": [
            {
                "role": "assistant",
                "content": "Planning Agent will handle this request."
            }
        ]
    }


def email_placeholder(state: AgentState):

    return {
        "messages": [
            {
                "role": "assistant",
                "content": "Email Agent will handle this request."
            }
        ]
    }