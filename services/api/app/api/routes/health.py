from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas import ErrorResponse, HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Health check",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version=get_settings().version)
