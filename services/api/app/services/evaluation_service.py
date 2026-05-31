from __future__ import annotations

from datetime import datetime, timezone

from app.core.errors import APIException
from app.domain.scoring import DeterministicScoringEngine, calculate_overall_score
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.session_repository import SessionRepository
from app.schemas import ErrorCode, EvaluationReport, InterviewSession, InterviewTurn, SessionStatus


class EvaluationService:
    def __init__(
        self,
        session_repository: SessionRepository,
        evaluation_repository: EvaluationRepository,
        scoring_engine: DeterministicScoringEngine | None = None,
    ) -> None:
        self._session_repository = session_repository
        self._evaluation_repository = evaluation_repository
        self._scoring_engine = scoring_engine or DeterministicScoringEngine()

    async def get_report(self, report_id: str) -> EvaluationReport:
        cached_report = await self._evaluation_repository.get_report(report_id)
        if cached_report is not None:
            return cached_report

        session_id = self._parse_session_id(report_id)
        session = await self._session_repository.get_session(session_id)
        if session is None:
            raise APIException(
                ErrorCode.SESSION_NOT_FOUND,
                "评价报告对应的面试会话不存在",
                status_code=404,
                details={"reportId": report_id, "sessionId": session_id},
            )

        turns = await self._session_repository.list_turns(session_id)
        self._ensure_report_can_be_generated(session, turns, report_id)

        profile = self._scoring_engine.build_profile(turns)
        ability = self._evaluate_ability(profile)
        psychology = self._evaluate_psychology(profile)
        turn_feedback = self._evaluate_turns(profile)
        action_plan = self._build_action_plan(profile, ability, psychology)
        strengths = self._scoring_engine.build_strengths(ability, psychology)
        risks = self._scoring_engine.build_risks(profile, ability, psychology)

        report = EvaluationReport(
            id=report_id,
            session_id=session.id,
            overall_score=calculate_overall_score(ability, psychology),
            ability=ability,
            psychology=psychology,
            turn_feedback=turn_feedback,
            strengths=strengths,
            risks=risks,
            action_plan=action_plan,
            generated_at=datetime.now(timezone.utc),
        )
        return await self._evaluation_repository.save_report(report)

    def _parse_session_id(self, report_id: str) -> str:
        if not report_id.startswith("report_") or report_id == "report_":
            raise APIException(
                ErrorCode.EVALUATION_FAILED,
                "评价报告不存在",
                status_code=404,
                details={"reportId": report_id},
            )
        return report_id.removeprefix("report_")

    def _ensure_report_can_be_generated(
        self,
        session: InterviewSession,
        turns: list[InterviewTurn],
        report_id: str,
    ) -> None:
        if session.status != SessionStatus.COMPLETED:
            raise APIException(
                ErrorCode.INVALID_SESSION_STATE,
                "面试尚未完成，不能生成评价报告",
                status_code=409,
                details={"reportId": report_id, "sessionId": session.id, "status": session.status},
            )

        answered_count = sum(1 for turn in turns if turn.answer is not None)
        if answered_count < session.question_count_target:
            raise APIException(
                ErrorCode.INVALID_SESSION_STATE,
                "面试回答数量不足，不能生成评价报告",
                status_code=409,
                details={
                    "reportId": report_id,
                    "sessionId": session.id,
                    "answeredCount": answered_count,
                    "questionCountTarget": session.question_count_target,
                },
            )

    def _evaluate_ability(self, profile):
        return self._scoring_engine.evaluate_ability(profile)

    def _evaluate_psychology(self, profile):
        return self._scoring_engine.evaluate_psychology(profile)

    def _evaluate_turns(self, profile):
        return self._scoring_engine.evaluate_turns(profile)

    def _build_action_plan(self, profile, ability, psychology):
        return self._scoring_engine.build_action_plan(profile, ability, psychology)
