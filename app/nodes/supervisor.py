from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage,HumanMessage
from app.state import MainState
from typing import Literal
from pydantic import BaseModel,Field
import asyncio 

class SupervisorDecision(BaseModel):
    next_agent : Literal[
        "research",
        "planning",
        "email",
        "final"
    ] = Field(
        description = "The next agent that should handle the request"
    )
    email_required: bool = Field(
        description="Whether the workflow requires sending or drafting email"
    )

    multiple_emails: bool = Field(
        description="Whether more than one email needs to be drafted or sent"
    )

    recipients: list[str] = Field(
        default_factory=list,
        description="Email addresses explicitly provided by the user"
    )

llm = ChatGoogleGenerativeAI(
    model = 'gemini-3.6-flash'
)

decision_llm = llm.with_structured_output(SupervisorDecision)

SUPERVISOR_PROMPT = """
You are the Supervisor Agent of a Personal AI Operations Agent.

Your responsibility is to orchestrate the overall workflow.

You do NOT perform the actual research, planning, or email operations.
Instead, determine which specialized agent should handle the next step.

AVAILABLE AGENTS:

1. research
Use when the workflow requires gathering, verifying, or discovering
information from external sources.

Examples:
- Find companies or people.
- Research a company.
- Find contact information.
- Compare available options.
- Gather facts needed for a later task.

2. planning
Use when sufficient information has been gathered and the workflow
requires creating, organizing, prioritizing, or reviewing a plan.

Examples:
- Create an outreach strategy.
- Prioritize research results.
- Break an objective into actionable steps.
- Decide what actions should be performed.

3. email
Use when the workflow requires drafting, reviewing, or sending emails.

Examples:
- Draft an email.
- Send an approved email.
- Contact one or more recipients.

4. final
Use when the requested workflow has been completed and no further
specialized agent is required.

WORKFLOW RULES:

- Always consider the user's original objective.
- Consider what has already been completed in the current MainState.
- Do not repeat work that has already been successfully completed.
- Choose only ONE next agent.
- Do not skip required dependencies.
- Research should normally happen before planning when the plan depends
  on external information.
- Planning should normally happen before execution when the user requires
  a strategy or structured sequence of actions.
- Email should only be selected when the required information for the
  email operation is available.
- Select final only when the workflow is actually complete.
- If required information is missing, route to the agent that can obtain it.

EMAIL RULES:

- email_required should be true when the user's objective requires an
  email operation.
- email_action must describe the requested email operation:
    "none"  = no email operation is required
    "draft" = an email should be prepared but not sent
    "send"  = an email should ultimately be sent
- multiple_emails should be true when the workflow requires emails to
  multiple recipients.
- Extract email addresses only when they are explicitly present in the
  user's request or have been reliably discovered by the research step.
- Never invent, guess, or fabricate an email address.
- If the user asks you to find an email address and none is available,
  leave recipients empty and route to research.
- Preserve explicitly provided email addresses exactly.
- If multiple recipients are available, include all relevant recipients.

DECISION PROCESS:

Before selecting the next agent, determine:

1. What is the user's overall objective?
2. What information has already been gathered?
3. Has the required planning been completed?
4. Does the workflow require email?
5. Is the required recipient information available?
6. What is the next unfinished step?
7. Is the entire workflow complete?

Return a structured decision containing the next agent and the relevant
email information.
"""

async def supervisor(state: MainState):

    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT),

        HumanMessage(
            content=f"""
USER OBJECTIVE:
{state["objective"]}

CURRENT WORKFLOW STATE:

RESEARCH RESULTS:
{state.get("research_results")}

PLAN:
{state.get("plan")}

EMAIL DRAFT:
{state.get("email_draft")}

EMAIL APPROVED:
{state.get("email_approved")}

EMAIL SEND RESULT:
{state.get("email_send_result")}

PREVIOUS EMAIL RECIPIENTS:
{state.get("recipients")}
"""
        )
    ]

    decision = await decision_llm.ainvoke(messages)

    return {
        "next_agent": decision.next_agent,
        "email_required": decision.email_required,
        "email_action": decision.email_action,
        "multiple_emails": decision.multiple_emails,
        "recipients": decision.recipients,
    }