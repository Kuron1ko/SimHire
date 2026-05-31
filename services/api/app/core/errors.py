from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import ErrorCode, ErrorDetail, ErrorResponse


class APIException(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def _error_payload(code: ErrorCode, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    response = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            details=details or {},
        )
    )
    return response.model_dump(by_alias=True, mode="json")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIException)
    async def api_exception_handler(_: Request, exc: APIException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        code = detail.get("code", ErrorCode.INTERNAL_ERROR)
        try:
            error_code = ErrorCode(code)
        except ValueError:
            error_code = ErrorCode.INTERNAL_ERROR
        message = detail.get("message") if isinstance(detail, dict) else str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(error_code, message or "Request failed", detail.get("details", {})),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                ErrorCode.INTERNAL_ERROR,
                "Request validation failed",
                {"errors": exc.errors()},
            ),
        )
