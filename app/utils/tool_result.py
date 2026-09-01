from typing import Literal

from pydantic import BaseModel


class ToolExecutionResult(BaseModel):

    tool: str

    status: Literal[
        "success",
        "failed",
    ]

    result: str | None = None

    error_type: str | None = None

    message: str | None = None

    retryable: bool = False