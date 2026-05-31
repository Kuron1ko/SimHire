from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import create_app
from app.schemas import (
    AbilityDimensions,
    AbilityEvaluation,
    ActionItem,
    EvaluationReport,
    InterviewScenario,
    PracticeType,
    PsychologyDimensions,
    PsychologyEvaluation,
    ScoreItem,
    ScenarioCategory,
    Difficulty,
    ActionPriority,
    TurnFeedback,
)


def _score(max_score: int) -> ScoreItem:
    return ScoreItem(
        score=max_score * 0.8,
        max_score=max_score,
        evidence=["clear example"],
        suggestion="Add more quantified results.",
    )


def test_health_endpoint_returns_contract_shape() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_schema_aliases_serialize_to_camel_case() -> None:
    scenario = InterviewScenario(
        id="campus_general",
        name="Campus interview",
        description="General campus interview practice.",
        category=ScenarioCategory.CAMPUS,
        default_question_count=4,
        difficulty=Difficulty.MEDIUM,
        rubric_id="default_v1",
        opening_prompt="Please introduce yourself.",
    )

    payload = scenario.model_dump(by_alias=True, mode="json")

    assert "defaultQuestionCount" in payload
    assert "rubricId" in payload
    assert "openingPrompt" in payload
    assert "default_question_count" not in payload


def test_openapi_includes_contract_schema_components() -> None:
    schema = create_app().openapi()

    components = schema["components"]["schemas"]
    required = {
        "InterviewScenario",
        "InterviewSession",
        "InterviewTurn",
        "CandidateAnswer",
        "EvaluationReport",
        "ErrorResponse",
        "StartSessionRequest",
        "SubmitAnswerResponse",
    }

    assert set(schema["paths"]) == {
        "/api/health",
        "/api/scenarios",
        "/api/interviews/sessions",
        "/api/interviews/sessions/{session_id}/answers",
        "/api/interviews/sessions/{session_id}/finish",
        "/api/evaluations/reports/{report_id}",
    }
    assert required.issubset(components)


def test_evaluation_report_schema_accepts_expected_shape() -> None:
    report = EvaluationReport(
        id="report_123",
        session_id="session_123",
        overall_score=82,
        ability=AbilityEvaluation(
            total=50,
            dimensions=AbilityDimensions(
                logical_structure=_score(15),
                relevance=_score(10),
                specificity=_score(15),
                professional_depth=_score(10),
                communication_clarity=_score(10),
            ),
        ),
        psychology=PsychologyEvaluation(
            total=32,
            dimensions=PsychologyDimensions(
                stress_tolerance=_score(10),
                confidence=_score(10),
                adaptability=_score(10),
                emotional_stability=_score(10),
            ),
        ),
        turn_feedback=[
            TurnFeedback(
                turn_id="turn_1",
                summary="Structured answer with a concrete project example.",
                score=82,
                highlights=["Good structure"],
                improvements=["Quantify the result"],
            )
        ],
        strengths=["Clear structure", "Relevant experience"],
        risks=["Needs more quantified evidence", "Speech pace may be high"],
        action_plan=[
            ActionItem(
                title="Practice STAR examples",
                description="Prepare three quantified project stories.",
                priority=ActionPriority.HIGH,
                practice_type=PracticeType.STRUCTURE,
            )
        ],
        generated_at=datetime.now(timezone.utc),
    )

    payload = report.model_dump(by_alias=True, mode="json")

    assert payload["overallScore"] == 82
    assert "logicalStructure" in payload["ability"]["dimensions"]
    assert "stressTolerance" in payload["psychology"]["dimensions"]
    assert payload["actionPlan"][0]["practiceType"] == "structure"
