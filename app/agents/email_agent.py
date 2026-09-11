from langchain_core.messages import HumanMessage
from app.llm import llm
from app.nodes.mail_tools import search_mail, get_mail, send_mail
from app.state import EmailState


tools = [
    search_mail,
    get_mail,
    send_mail,
]

email_agent = llm.bind_tools(tools)


def email_agent_node(state: EmailState):

    messages = state.get("messages", [])

    if not messages:
        messages = [
            HumanMessage(
                content=f"""
You are an email operations agent.

OBJECTIVE:
{state["purpose"]}

RECIPIENTS:
{state.get("recipient", [])}

Use search_mail when you need to find emails.

Use get_mail when you need to read a specific email.

Use send_mail when an email needs to be sent.

You may make multiple send_mail calls when needed.

Do not invent information.
"""
            )
        ]

        response = email_agent.invoke(messages)

        return {
            "messages": [
                messages[0],
                response
            ]
        }

    response = email_agent.invoke(messages)

    return {
        "messages": [response]
    }