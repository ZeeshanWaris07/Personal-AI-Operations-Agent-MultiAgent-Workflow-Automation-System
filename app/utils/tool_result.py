from typing import Any, Optional
from pydantic import BaseModel


class ToolExecutionResult(BaseModel):
    tool: str
    tool_call_id: Optional[str] = None  
    status: str
    result: Any = None
    error_type: Optional[str] = None
    message: Optional[str] = None
    retryable: bool = False