from typing import Any
from pydantic import BaseModel

class ExecuteSuccessResponse(BaseModel):
    result: Any
    stdout: str

class ErrorInfo(BaseModel):
    type: str
    message: str

class ExecuteErrorResponse(BaseModel):
    error: ErrorInfo

