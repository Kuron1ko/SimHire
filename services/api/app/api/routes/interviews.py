from fastapi import APIRouter, status

from app.dependencies import interview_orchestrator
from app.schemas import (
    ErrorResponse,
    FinishSessionResponse,
    StartSessionRequest,
    StartSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)

router = APIRouter(prefix="/interviews", tags=["interviews"])
orchestrator = interview_orchestrator


@router.post(
    "/sessions",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Start an interview session",
)
async def start_session(request: StartSessionRequest) -> StartSessionResponse:
    return await orchestrator.start_session(request)


@router.post(
    "/sessions/{session_id}/answers",
    response_model=SubmitAnswerResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Submit an answer and get the next interview step",
)
async def submit_answer(session_id: str, request: SubmitAnswerRequest) -> SubmitAnswerResponse:
    return await orchestrator.submit_answer(session_id, request)


@router.post(
    "/sessions/{session_id}/finish",
    response_model=FinishSessionResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Finish an interview session",
)
async def finish_session(session_id: str) -> FinishSessionResponse:
    return await orchestrator.finish_session(session_id)
