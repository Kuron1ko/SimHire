from typing import Any

from pydantic import Field

from app.schemas.base import APIModel
from app.schemas.enums import ErrorCode


class ErrorDetail(APIModel):
    code: ErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(APIModel):
    error: ErrorDetail
