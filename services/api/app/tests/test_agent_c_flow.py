import asyncio

from fastapi.testclient import TestClient

from app.api.routes import interviews
from app.main import create_app
from app.schemas import SessionStatus


def test_submit_answer_returns_next_question() -> None:
    client = TestClient(create_app())
    start_payload = _start_session(client, question_count_target=3)

    response = _submit_answer(
        client,
        start_payload["session"]["id"],
        start_payload["turn"]["id"],
        "我会用背景、行动和结果来说明这个经历，并补充具体贡献和复盘。",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["nextAction"] == "next_question"
    assert payload["assistantAck"]
    assert payload["nextTurn"]["sessionId"] == start_payload["session"]["id"]
    assert payload["nextTurn"]["index"] == 2
    assert payload["nextTurn"]["question"]["text"]


def test_submit_answer_returns_finish_available_when_target_reached() -> None:
    client = TestClient(create_app())
    start_payload = _start_session(client, question_count_target=2)

    first_response = _submit_answer(
        client,
        start_payload["session"]["id"],
        start_payload["turn"]["id"],
        "我会先说明背景，再讲自己的行动，最后用结果和反思收束回答。",
    )
    assert first_response.status_code == 200
    next_turn = first_response.json()["nextTurn"]

    second_response = _submit_answer(
        client,
        start_payload["session"]["id"],
        next_turn["id"],
        "第二题我会继续保持结构化表达，并补充岗位匹配、数据结果和下一步计划。",
    )

    assert second_response.status_code == 200
    payload = second_response.json()
    assert payload["nextAction"] == "finish_available"
    assert payload["nextTurn"] is None


def test_short_answer_returns_follow_up() -> None:
    client = TestClient(create_app())
    start_payload = _start_session(client, question_count_target=3)

    response = _submit_answer(
        client,
        start_payload["session"]["id"],
        start_payload["turn"]["id"],
        "还行",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["nextAction"] == "follow_up"
    assert payload["nextTurn"]["question"]["type"] == "follow_up"


def test_finish_marks_session_completed() -> None:
    client = TestClient(create_app())
    start_payload = _start_session(client, question_count_target=1)
    session_id = start_payload["session"]["id"]

    submit_response = _submit_answer(
        client,
        session_id,
        start_payload["turn"]["id"],
        "我会用结构化方式完成这道题，并补充行动、结果和复盘。",
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["nextAction"] == "finish_available"

    response = client.post(f"/api/interviews/sessions/{session_id}/finish")

    assert response.status_code == 200
    assert response.json() == {"reportId": f"report_{session_id}", "status": "generated"}

    session = asyncio.run(interviews.orchestrator._session_repository.get_session(session_id))
    assert session is not None
    assert session.status == SessionStatus.COMPLETED
    assert session.completed_at is not None


def test_finish_rejects_session_with_insufficient_answers() -> None:
    client = TestClient(create_app())
    start_payload = _start_session(client, question_count_target=2)
    session_id = start_payload["session"]["id"]

    response = client.post(f"/api/interviews/sessions/{session_id}/finish")

    assert response.status_code == 409
    payload = response.json()
    assert payload["error"]["code"] == "INVALID_SESSION_STATE"
    assert payload["error"]["details"]["answeredCount"] == 0
    assert payload["error"]["details"]["questionCountTarget"] == 2


def test_submit_answer_returns_not_found_for_missing_session() -> None:
    client = TestClient(create_app())

    response = _submit_answer(
        client,
        "session_missing",
        "turn_missing",
        "这是一段有效回答，用于确认缺失 session 会返回约定错误。",
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SESSION_NOT_FOUND"


def test_submit_answer_returns_not_found_for_missing_turn() -> None:
    client = TestClient(create_app())
    start_payload = _start_session(client, question_count_target=3)

    response = _submit_answer(
        client,
        start_payload["session"]["id"],
        "turn_missing",
        "这是一段有效回答，用于确认缺失 turn 会返回约定错误。",
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TURN_NOT_FOUND"


def test_submit_answer_returns_empty_answer_error() -> None:
    client = TestClient(create_app())
    start_payload = _start_session(client, question_count_target=3)

    response = _submit_answer(
        client,
        start_payload["session"]["id"],
        start_payload["turn"]["id"],
        "   ",
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_ANSWER"


def test_submit_answer_rejects_completed_session() -> None:
    client = TestClient(create_app())
    start_payload = _start_session(client, question_count_target=1)
    session_id = start_payload["session"]["id"]

    submit_response = _submit_answer(
        client,
        session_id,
        start_payload["turn"]["id"],
        "这是一段有效回答，用于先完成面试题数，再验证已完成会话拒绝继续提交。",
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["nextAction"] == "finish_available"

    finish_response = client.post(f"/api/interviews/sessions/{session_id}/finish")
    assert finish_response.status_code == 200

    response = _submit_answer(
        client,
        session_id,
        start_payload["turn"]["id"],
        "这是一段有效回答，但会话已经完成，应该被拒绝提交。",
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_SESSION_STATE"


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


def _submit_answer(client: TestClient, session_id: str, turn_id: str, text: str):
    return client.post(
        f"/api/interviews/sessions/{session_id}/answers",
        json={
            "turnId": turn_id,
            "answer": {
                "text": text,
                "transcriptSource": "manual",
            },
        },
    )
