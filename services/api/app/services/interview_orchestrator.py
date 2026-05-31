from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.errors import APIException
from app.repositories.scenario_repository import ScenarioRepository
from app.repositories.session_repository import SessionRepository
from app.schemas import (
    ErrorCode,
    FinishSessionResponse,
    FinishStatus,
    InterviewSession,
    InterviewTurn,
    NextAction,
    SessionStatus,
    StartSessionRequest,
    StartSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.question_agent import QuestionAgent


class InterviewOrchestrator:
    def __init__(
        self,
        scenario_repository: ScenarioRepository,
        session_repository: SessionRepository,
        question_agent: QuestionAgent,
    ) -> None:
        self._scenario_repository = scenario_repository
        self._session_repository = session_repository
        self._question_agent = question_agent

    async def start_session(self, command: StartSessionRequest) -> StartSessionResponse:
        scenario = await self._scenario_repository.get_scenario(command.scenario_id)
        if scenario is None:
            raise APIException(
                ErrorCode.SCENARIO_NOT_FOUND,
                "面试场景不存在",
                status_code=404,
                details={"scenarioId": command.scenario_id},
            )

        now = datetime.now(timezone.utc)
        session = InterviewSession(
            id=_make_id("session"),
            scenario_id=scenario.id,
            status=SessionStatus.IN_PROGRESS,
            mode=command.mode,
            language=command.language,
            question_count_target=command.question_count_target,
            current_turn_index=1,
            created_at=now,
        )
        question = await self._question_agent.generate_first_question(scenario, command.candidate_profile)
        turn = InterviewTurn(
            id=_make_id("turn"),
            session_id=session.id,
            index=1,
            question=question,
            created_at=now,
        )

        await self._session_repository.create_session(session)
        await self._session_repository.append_turn(turn)
        return StartSessionResponse(session=session, turn=turn)

    async def submit_answer(self, session_id: str, command: SubmitAnswerRequest) -> SubmitAnswerResponse:
        session = await self._get_in_progress_session(session_id)
        answer_text = command.answer.text.strip()
        if not answer_text:
            raise APIException(
                ErrorCode.EMPTY_ANSWER,
                "回答内容不能为空",
                status_code=400,
                details={"sessionId": session_id, "turnId": command.turn_id},
            )

        turns = await self._session_repository.list_turns(session.id)
        current_turn = _find_turn(turns, command.turn_id)
        if current_turn is None:
            raise APIException(
                ErrorCode.TURN_NOT_FOUND,
                "面试轮次不存在",
                status_code=404,
                details={"sessionId": session.id, "turnId": command.turn_id},
            )

        if current_turn.answer is not None or current_turn.index != session.current_turn_index:
            raise APIException(
                ErrorCode.INVALID_SESSION_STATE,
                "当前会话状态不允许提交该轮回答",
                status_code=409,
                details={
                    "sessionId": session.id,
                    "turnId": command.turn_id,
                    "currentTurnIndex": session.current_turn_index,
                },
            )

        now = datetime.now(timezone.utc)
        normalized_answer = command.answer.model_copy(update={"text": answer_text})
        answered_turn = await self._session_repository.save_answer(
            session.id,
            current_turn.id,
            normalized_answer,
            answered_at=now,
        )
        if answered_turn is None:
            raise APIException(
                ErrorCode.TURN_NOT_FOUND,
                "面试轮次不存在",
                status_code=404,
                details={"sessionId": session.id, "turnId": command.turn_id},
            )

        answered_turns = [*turns]
        for index, turn in enumerate(answered_turns):
            if turn.id == answered_turn.id:
                answered_turns[index] = answered_turn
                break

        if answered_turn.index >= session.question_count_target:
            return SubmitAnswerResponse(
                next_action=NextAction.FINISH_AVAILABLE,
                assistant_ack="本轮回答已记录，当前题数已经完成，可以结束面试。",
                next_turn=None,
            )

        scenario = await self._scenario_repository.get_scenario(session.scenario_id)
        if scenario is None:
            raise APIException(
                ErrorCode.SCENARIO_NOT_FOUND,
                "面试场景不存在",
                status_code=404,
                details={"scenarioId": session.scenario_id},
            )

        decision = await self._question_agent.generate_next_question(scenario, answered_turns)
        if decision.question is None:
            return SubmitAnswerResponse(
                next_action=NextAction.FINISH_AVAILABLE,
                assistant_ack=decision.assistant_ack or "当前题数已经完成，可以结束面试。",
                next_turn=None,
            )

        next_index = answered_turn.index + 1
        next_turn = InterviewTurn(
            id=_make_id("turn"),
            session_id=session.id,
            index=next_index,
            question=decision.question,
            created_at=now,
        )
        await self._session_repository.append_turn(next_turn)
        await self._session_repository.update_session(
            session.model_copy(update={"current_turn_index": next_index})
        )
        return SubmitAnswerResponse(
            next_action=decision.next_action,
            assistant_ack=decision.assistant_ack,
            next_turn=next_turn,
        )

    async def finish_session(self, session_id: str) -> FinishSessionResponse:
        session = await self._session_repository.get_session(session_id)
        if session is None:
            raise APIException(
                ErrorCode.SESSION_NOT_FOUND,
                "面试会话不存在",
                status_code=404,
                details={"sessionId": session_id},
            )

        if session.status == SessionStatus.COMPLETED:
            return FinishSessionResponse(report_id=f"report_{session_id}", status=FinishStatus.GENERATED)

        turns = await self._session_repository.list_turns(session_id)
        answered_count = sum(1 for turn in turns if turn.answer is not None)
        if answered_count < session.question_count_target:
            raise APIException(
                ErrorCode.INVALID_SESSION_STATE,
                "当前会话回答数量不足，不能结束面试",
                status_code=409,
                details={
                    "sessionId": session_id,
                    "answeredCount": answered_count,
                    "questionCountTarget": session.question_count_target,
                },
            )

        completed = session.model_copy(
            update={
                "status": SessionStatus.COMPLETED,
                "completed_at": datetime.now(timezone.utc),
            }
        )
        await self._session_repository.update_session(completed)

        return FinishSessionResponse(report_id=f"report_{session_id}", status=FinishStatus.GENERATED)

    async def _get_in_progress_session(self, session_id: str) -> InterviewSession:
        session = await self._session_repository.get_session(session_id)
        if session is None:
            raise APIException(
                ErrorCode.SESSION_NOT_FOUND,
                "面试会话不存在",
                status_code=404,
                details={"sessionId": session_id},
            )
        if session.status != SessionStatus.IN_PROGRESS:
            raise APIException(
                ErrorCode.INVALID_SESSION_STATE,
                "当前会话状态不允许提交回答",
                status_code=409,
                details={"sessionId": session_id, "status": session.status},
            )
        return session


def _make_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _find_turn(turns: list[InterviewTurn], turn_id: str) -> InterviewTurn | None:
    for turn in turns:
        if turn.id == turn_id:
            return turn
    return None
