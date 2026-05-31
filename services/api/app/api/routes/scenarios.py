from fastapi import APIRouter

from app.dependencies import scenario_repository
from app.schemas import ErrorResponse, ScenariosResponse

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get(
    "",
    response_model=ScenariosResponse,
    responses={500: {"model": ErrorResponse}},
    summary="List interview scenarios",
)
async def list_scenarios() -> ScenariosResponse:
    scenarios = await scenario_repository.list_scenarios()
    return ScenariosResponse(items=scenarios)
