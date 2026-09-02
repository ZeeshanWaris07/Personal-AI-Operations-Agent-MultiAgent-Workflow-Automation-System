from pydantic import BaseModel

class Plan(BaseModel):

    objective: str

    steps: list[str]

    priorities: list[str]

    risks: list[str]

class PlanReview(BaseModel):
    approved: bool
    feedback: str
    missing_items: list[str]