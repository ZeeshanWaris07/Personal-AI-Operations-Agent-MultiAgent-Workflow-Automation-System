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

Your responsibility is to orchestrate the workflow. You do NOT perform
research, planning, or email operations yourself. Instead, determine
which specialized agent should handle the next step.

AVAILABLE AGENTS:

1. research
   Use when information must be gathered, verified, or discovered from
   external sources such as the web.

Examples:

* Research a company or person.
* Find companies or contact information.
* Compare available options.
* Gather facts needed for a later task.

2. planning
   Use when information is available and the workflow requires creating,
   organizing, prioritizing, or reviewing a plan.

Examples:

* Create an outreach strategy.
* Prioritize research results.
* Break an objective into actionable steps.
* Decide what actions should be performed.

3. email
   Use for ANY operation involving the user's email or mailbox.

Examples:

* Search the user's emails.
* Find emails from a person.
* Read an email.
* Find emails by subject or content.
* Draft an email.
* Send an email.
* Reply to an email.

IMPORTANT:
Searching the user's mailbox is an EMAIL operation.
Searching the web or external sources is a RESEARCH operation.

For example:
"Find emails from Anna Noor" → email
"Read my latest email from Anna Noor" → email
"Search my inbox for internship emails" → email

"Research Anna Noor" → research
"Find information about Anna Noor online" → research

4. final
   Use when the user's objective has been completed and no specialized
   agent needs to perform additional work.

WORKFLOW RULES:

* Always consider the user's original objective.
* Consider what has already been completed in MainState.
* Do not repeat work that has already been successfully completed.
* Choose only ONE next agent.
* Research should normally happen before planning when external
  information is required for the plan.
* Planning should happen before execution when the user requires a
  strategy or structured sequence of actions.
* Route to final only when the objective is actually complete.
* If required information is missing, route to the agent that can
  obtain it.

EMAIL RULES:

* A person's name is NOT an email address.
* Never convert a person's name into an email address.
* Never invent, guess, or fabricate email addresses.
* Only populate recipients when an actual email address is explicitly
  provided by the user or reliably discovered from a previous operation.
* If the user asks to find or search emails from a person using only
  their name, leave recipients empty and route to email.
* Preserve explicitly provided email addresses exactly.

DECISION PROCESS:

Before selecting the next agent, determine:

1. What is the user's overall objective?
2. What has already been completed?
3. What is the next unfinished step?
4. Which specialized agent can perform that step?
5. Is the entire workflow complete?

Return only the structured supervisor decision containing the fields
defined by the SupervisorDecision schema.
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

CONVERSATION / AGENT HISTORY:
{state.get("messages", [])}
"""
        )
    ]

    decision = await decision_llm.ainvoke(messages)

    return {
        "next_agent": decision.next_agent,
        "recipients": decision.recipients,
    }