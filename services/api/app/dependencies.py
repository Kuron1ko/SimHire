from __future__ import annotations

from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.scenario_repository import ScenarioRepository
from app.repositories.session_repository import SessionRepository
from app.services.evaluation_service import EvaluationService
from app.services.interview_orchestrator import InterviewOrchestrator
from app.services.question_agent import QuestionAgent


scenario_repository = ScenarioRepository()
session_repository = SessionRepository()
evaluation_repository = EvaluationRepository()
question_agent = QuestionAgent()

interview_orchestrator = InterviewOrchestrator(
    scenario_repository=scenario_repository,
    session_repository=session_repository,
    question_agent=question_agent,
)
evaluation_service = EvaluationService(
    session_repository=session_repository,
    evaluation_repository=evaluation_repository,
)
