from fastapi import APIRouter

from app.dependencies import evaluation_service
from app.schemas import ErrorResponse, EvaluationReport

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get(
    "/reports/{report_id}",
    response_model=EvaluationReport,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Get an evaluation report",
)
async def get_evaluation_report(report_id: str) -> EvaluationReport:
    return await evaluation_service.get_report(report_id)
