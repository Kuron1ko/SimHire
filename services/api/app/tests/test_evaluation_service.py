from fastapi.testclient import TestClient

from app.main import create_app


def test_get_report_after_completed_interview_returns_evaluation_report() -> None:
    client = TestClient(create_app())
    start_payload = _complete_interview(client, question_count_target=2)
    session_id = start_payload["session"]["id"]
    finish_response = client.post(f"/api/interviews/sessions/{session_id}/finish")
    assert finish_response.status_code == 200
    report_id = finish_response.json()["reportId"]

    response = client.get(f"/api/evaluations/reports/{report_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == report_id
    assert payload["sessionId"] == session_id
    assert 0 <= payload["overallScore"] <= 100
    assert payload["ability"]
    assert payload["psychology"]
    assert payload["turnFeedback"]
    assert payload["strengths"]
    assert payload["risks"]
    assert len(payload["actionPlan"]) >= 3


def test_report_score_items_are_legal_and_include_evidence() -> None:
    client = TestClient(create_app())
    start_payload = _complete_interview(client, question_count_target=2)
    session_id = start_payload["session"]["id"]
    report_id = client.post(f"/api/interviews/sessions/{session_id}/finish").json()["reportId"]

    payload = client.get(f"/api/evaluations/reports/{report_id}").json()
    dimensions = [
        *payload["ability"]["dimensions"].values(),
        *payload["psychology"]["dimensions"].values(),
    ]

    for item in dimensions:
        assert 0 <= item["score"] <= item["maxScore"]
        assert item["evidence"]
        assert item["suggestion"]


def test_manual_answer_sets_psychology_to_zero_and_marks_report() -> None:
    client = TestClient(create_app())
    start_payload = _complete_interview(client, question_count_target=2, transcript_source="manual")
    session_id = start_payload["session"]["id"]
    report_id = client.post(f"/api/interviews/sessions/{session_id}/finish").json()["reportId"]

    payload = client.get(f"/api/evaluations/reports/{report_id}").json()
    psychology = payload["psychology"]

    assert psychology["total"] == 0
    for item in psychology["dimensions"].values():
        assert item["score"] == 0
        assert "手动输入" in item["evidence"][0]
    assert any("非语音回答" in risk for risk in payload["risks"])
    assert any("全语音" in item["title"] for item in payload["actionPlan"])


def test_browser_stt_answer_keeps_psychology_score_when_speech_metrics_are_missing() -> None:
    client = TestClient(create_app())
    start_payload = _complete_interview(client, question_count_target=2, transcript_source="browser_stt")
    session_id = start_payload["session"]["id"]
    report_id = client.post(f"/api/interviews/sessions/{session_id}/finish").json()["reportId"]

    payload = client.get(f"/api/evaluations/reports/{report_id}").json()

    assert payload["psychology"]["total"] > 0
    assert any("缺少语音指标" in risk for risk in payload["risks"])


def test_get_report_is_idempotent_for_cached_report() -> None:
    client = TestClient(create_app())
    start_payload = _complete_interview(client, question_count_target=1)
    session_id = start_payload["session"]["id"]
    report_id = client.post(f"/api/interviews/sessions/{session_id}/finish").json()["reportId"]

    first = client.get(f"/api/evaluations/reports/{report_id}")
    second = client.get(f"/api/evaluations/reports/{report_id}")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json() == first.json()


def test_get_report_rejects_unfinished_session() -> None:
    client = TestClient(create_app())
    start_payload = _start_session(client, question_count_target=2)
    session_id = start_payload["session"]["id"]

    response = client.get(f"/api/evaluations/reports/report_{session_id}")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_SESSION_STATE"


def test_get_report_returns_not_found_for_missing_session() -> None:
    client = TestClient(create_app())

    response = client.get("/api/evaluations/reports/report_session_missing")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SESSION_NOT_FOUND"


def test_get_report_returns_not_found_for_invalid_report_id() -> None:
    client = TestClient(create_app())

    response = client.get("/api/evaluations/reports/unknown_report")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "EVALUATION_FAILED"


def test_openapi_includes_evaluation_report_path() -> None:
    schema = create_app().openapi()

    assert "/api/evaluations/reports/{report_id}" in schema["paths"]


def _complete_interview(client: TestClient, question_count_target: int, transcript_source: str = "manual") -> dict:
    start_payload = _start_session(client, question_count_target=question_count_target)
    session_id = start_payload["session"]["id"]
    turn_id = start_payload["turn"]["id"]

    for index in range(question_count_target):
        response = _submit_answer(
            client,
            session_id,
            turn_id,
            (
                f"第 {index + 1} 题我会首先说明背景，其次介绍我负责的行动，"
                f"最后用 20% 的结果提升和复盘说明个人贡献。"
            ),
            transcript_source=transcript_source,
        )
        assert response.status_code == 200
        payload = response.json()
        next_turn = payload.get("nextTurn")
        if next_turn is None:
            break
        turn_id = next_turn["id"]

    return start_payload


def _start_session(client: TestClient, question_count_target: int) -> dict:
    response = client.post(
        "/api/interviews/sessions",
        json={
            "scenarioId": "campus_general",
            "mode": "text",
            "language": "zh-CN",
            "questionCountTarget": question_count_target,
        },
    )
    assert response.status_code == 201
    return response.json()


def _submit_answer(client: TestClient, session_id: str, turn_id: str, text: str, transcript_source: str = "manual"):
    return client.post(
        f"/api/interviews/sessions/{session_id}/answers",
        json={
            "turnId": turn_id,
            "answer": {
                "text": text,
                "transcriptSource": transcript_source,
            },
        },
    )
