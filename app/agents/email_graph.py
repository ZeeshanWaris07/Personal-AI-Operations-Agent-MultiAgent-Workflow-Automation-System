from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.state import EmailState
from app.agents.email_agent import email_agent_node
from app.nodes.human_approval import human_approval
from app.nodes.gmail_sender import send_email
from app.nodes.mail_tools import send_mail, get_mail,search_mail


mail_tools = [
    send_mail,
    get_mail,
    search_mail
]


def route_mail_agent(state: EmailState):

    last_message = state["messages"][-1]

    if not last_message.tool_calls:
        return "end"

    tool_calls = last_message.tool_calls
    tool_names = [call["name"] for call in tool_calls]

    if "send_mail" in tool_names:
        return "approval"

    return "tools"


def make_email_decision(state: EmailState):

    if state.get("approved"):
        return "send"

    return "reject"


def build_email_graph():

    builder = StateGraph(EmailState)

    builder.add_node(
        "mail_agent",
        email_agent_node
    )

    builder.add_node(
        "tools",
        ToolNode(mail_tools)
    )

    builder.add_node(
        "approval",
        human_approval
    )

    builder.add_node(
        "send_email",
        send_email
    )

    builder.add_edge(
        START,
        "mail_agent"
    )

    builder.add_conditional_edges(
        "mail_agent",
        route_mail_agent,
        {
            "tools": "tools",
            "approval": "approval",
            "end": END
        }
    )

    builder.add_edge(
        "tools",
        "mail_agent"
    )

    builder.add_conditional_edges(
        "approval",
        make_email_decision,
        {
            "send": "send_email",
            "reject": END
        }
    )

    builder.add_edge(
        "send_email",
        END
    )

    return builder.compile()