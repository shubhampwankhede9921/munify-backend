from typing import Any, Optional, List
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    loc: Optional[List[Any]] = None
    msg: str
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    errors: Optional[List[ErrorDetail]] = None

    class Config:
        from_attributes = True


