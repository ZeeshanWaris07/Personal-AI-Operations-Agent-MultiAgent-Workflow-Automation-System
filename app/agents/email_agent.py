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

USER OBJECTIVE:
{state["purpose"]}

RECIPIENT:
{state.get("recipient", "Not specified")}

You can perform email operations using the available tools.

Available operations:

1. get_mail
   Use this when you need to inspect existing emails or obtain
   information from the user's mailbox.

2. send_mail
   Use this when an email needs to be sent.
   Sending an email requires human approval.

Decide what action is required to accomplish the user's objective.

If you need information from an existing email, use get_mail first.

If an email needs to be sent, create the appropriate email content
and call send_mail.

Do not invent information.
"""
            }
        ]

    response = email_agent.invoke(messages)

    return {
        "messages": [response]
    }