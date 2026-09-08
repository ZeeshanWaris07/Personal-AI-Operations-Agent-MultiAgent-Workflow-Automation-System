from app.llm import llm
from app.nodes.mail_tools import send_mail, get_mail
from app.state import EmailState

tools = [
    send_mail,
    get_mail,
]

email_agent = llm.bind_tools(tools)


def email_agent_node(state: EmailState):

    messages = state.get("messages", [])

    if not messages:
        messages = [
            {
                "role": "user",
                "content": f"""
You are an email operations agent.

OBJECTIVE:
{state["purpose"]}

RECIPIENTS:
{state.get("recipients", [])}

Use get_mail when you need to read existing emails.
Use send_mail when an email needs to be sent.

You may make multiple tool calls in the same turn when needed,
including one send_mail call for each recipient.

Do not invent information.
"""
            }
        ]

    response = email_agent.invoke(messages)

    return {
        "messages": [response]
    }