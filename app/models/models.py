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



class EmailDraft(BaseModel):
    recipient: str
    subject: str
    body: str



class FinalResponse(BaseModel):
    summary: str
    research_summary: str | None
    plan_summary: str | None
    email_status: str | None
    message: str