from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage,HumanMessage
from app.state import MainState
from typing import Literal
from pydantic import BaseModel,Field
import asyncio 
from app.llm import llm

class SupervisorDecision(BaseModel):
    next_agent : Literal[
        "research",
        "planning",
        "email",
        "final"
    ] = Field(
        description = "The next agent that should handle the request"
    )

    recipients: list[str] = Field(
        default_factory=list,
        description="Email addresses explicitly provided by the user"
    )



decision_llm = llm.with_structured_output(SupervisorDecision)

SUPERVISOR_PROMPT = """
You are the Supervisor Agent of a Personal AI Operations Agent.

Your job is to decide WHICH specialized agent should handle the next step.
You do not perform the work yourself.

AVAILABLE AGENTS:

1. research
Use when information must be gathered, verified, or discovered.

The research agent can:
- Search the web and retrieve webpages.
- Retrieve information from the user's private knowledge base.

Route to research for:
- External information or research.
- User-specific information or documents.
- Resume, skills, education, experience, projects, or notes.
- Tasks requiring both private and external information.

Examples:
"Tell me about my ML projects" → research
"Find companies matching my experience" → research
"Research five ML companies in Lahore" → research

The research agent decides whether to use web search, private document
retrieval, or both.

2. planning
Use when information is available and the user needs:
- A strategy.
- A structured plan.
- Prioritization.
- An organized sequence of actions.
- Review or refinement of a plan.

Planning normally happens after required information has been gathered.

3. email
Use for ANY operation involving the user's mailbox.

Examples:
- Search emails.
- Read emails.
- Find emails by person, subject, or content.
- Draft emails.
- Send emails.
- Reply to emails.

Mailbox operations are always handled by the email agent.
Web research about a person is handled by research.

4. final
Use only when the user's objective has been completed and no additional
specialized agent needs to perform work.

ROUTING RULES:

- Consider the USER OBJECTIVE and WORKFLOW STATUS.
- Choose exactly ONE next agent.
- Do not repeat work that has already been completed.
- External or private information needed → research.
- Planning or organization needed → planning.
- Mailbox operation needed → email.
- Objective completely satisfied → final.
- If required information is missing, route to the agent that can obtain it.
- Research normally occurs before planning when research is required.
- Do not perform research, planning, or email operations yourself.

IMPORTANT:
The supervisor decides WHICH AGENT works next.
The specialized agent decides HOW to perform its work.

EMAIL RECIPIENT RULES:

- A person's name is not an email address.
- Never invent or guess an email address.
- Only populate recipients when an email address was explicitly provided
  by the user or reliably discovered by a previous operation.
- Searching for emails using a person's name does not populate recipients.
- Preserve explicitly provided email addresses exactly.

DECISION:

Determine:
1. What does the user want?
2. What has already been completed?
3. What is still missing?
4. Which agent can perform the missing step?
5. Is the objective complete?

Return only the structured SupervisorDecision.

"""

async def supervisor(state: MainState):

    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT),
HumanMessage(
    content=f"""
USER OBJECTIVE:
{state["objective"]}

WORKFLOW STATUS:

Research completed:
{bool(state.get("research_results"))}

Research Results:
{state.get('research_results')}

Planning completed:
{bool(state.get("plan"))}

Email workflow started:
{bool(
    state.get("email_draft")
    or state.get("email_approved") is not None
    or state.get("email_send_result")
)}

Email approved:
{state.get("email_approved")}

Email completed:
{bool(state.get("email_send_result"))}

Email recipients:
{state.get("recipients")}

RECENT CONVERSATION:
{state.get("chat_history", [])[-6:]}
"""
)


    ]

    decision = await decision_llm.ainvoke(messages)

    return {
        "next_agent": decision.next_agent,
        "recipients": decision.recipients,
    }
