from pydantic import BaseModel
from app.state import PlanningState
from app.llm import llm

class Plan(BaseModel):

    objective: str

    steps: list[str]

    priorities: list[str]

    risks: list[str]

class PlanReview(BaseModel):
    approved: bool
    feedback: str
    missing_items: list[str]

def Planner(state:PlanningState):

    objective = state.get('objective')
    research_results = state.get('research_results')

    prompt = f"""
You are a planning agent.

Your job is to create a clear, actionable plan
for the user's objective.

USER OBJECTIVE:
{objective}

RESEARCH RESULTS:
{research_results}

Create a plan that:
- directly addresses the objective
- uses the available research
- contains logical steps
- identifies priorities
- identifies potential risks
"""

    structured_llm = llm.with_structured_output(Plan)

    response = structured_llm.invoke(prompt)

    return {
        'plan' : response
    }


def reviewer(state:PlanningState):

    plan = state.get('plan')

    prompt = f"""
You are a planning reviewer.

Review the following plan.

PLAN OBJECTIVE:
{plan.objective}

STEPS:
{plan.steps}

PRIORITIES:
{plan.priorities}

RISKS:
{plan.risks}

Determine whether the plan:

1. Directly addresses the objective.
2. Has logical and actionable steps.
3. Has appropriate priorities.
4. Identifies important risks.
5. Does not contain unnecessary steps.

Return:
- approved = true if the plan is sufficiently good.
- approved = false if it needs improvement.
- feedback explaining your decision.
- missing_items containing anything important that should be added.
"""

    reviewer_llm = llm.with_structured_output(PlanReview)

    review = reviewer_llm.invoke(prompt)

    return {
        'review' : review
    }
    