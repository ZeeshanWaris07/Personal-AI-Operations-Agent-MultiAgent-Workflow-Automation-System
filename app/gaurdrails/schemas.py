from pydantic import BaseModel
from typing import Literal

class GaurdrailDecision(BaseModel):
    allowed:bool
    category:Literal[
        'safe',
        'prompt_injection',
        'unsafe',
        'out_of_scope'
    ]
    reason:str


class OutputGaurdrailDecision(BaseModel):
    allowed: bool
    category: Literal[
        "safe",
        "unsafe",
        "data_leak",
        "unsupported_claim"
    ]
    reason: str