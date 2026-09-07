from pydantic import BaseModel
from app.state import PlanningState
from app.llm import llm
from app.models.models import Plan, PlanReview

def Planner(state:PlanningState):

    iterations = state.get('num_iterations',0)
    objective = state.get('objective')
    research_results = state.get('research_results')
    review = state.get('review',None)

    if review is None:

        prompt = f"""
You are a planning agent.

Create a clear and actionable plan for the user's objective.

USER OBJECTIVE:
{objective}

RESEARCH RESULTS:
{research_results}

The plan should:
- directly address the objective
- use the available research
- contain logical actionable steps
- identify priorities
- identify potential risks
"""

    else:

         current_plan = state.get('plan')
         prompt = f"""
You are a planning agent revising an existing plan.

USER OBJECTIVE:
{objective}

RESEARCH RESULTS:
{research_results}

CURRENT PLAN:
{current_plan}

REVIEWER FEEDBACK:
{review.feedback}

MISSING ITEMS:
{review.missing_items}

Create an improved version of the plan.

You must address the reviewer's feedback and
include the missing items where appropriate.

Do not blindly change the plan.
Keep good parts of the existing plan while
fixing the identified problems.
"""

    planner_llm = llm.with_structured_output(Plan,method='json_mode')

    plan = planner_llm.invoke(prompt)

    return {
        'plan' : plan,
        'review' : None,
        'num_iterations' : iterations + 1
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
    