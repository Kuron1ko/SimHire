from fastapi.testclient import TestClient

from app.main import create_app


def test_list_scenarios_returns_seed_data_with_camel_case_fields() -> None:
    client = TestClient(create_app())

    response = client.get("/api/scenarios")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 4
    first = payload["items"][0]
    assert first["id"] == "campus_general"
    assert first["defaultQuestionCount"] == 4
    assert first["rubricId"] == "default_v1"
    assert first["openingPrompt"] == "请先做一个 1 分钟自我介绍。"
    assert "default_question_count" not in first


def test_start_session_returns_session_and_first_opening_turn() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/interviews/sessions",
        json={
            "scenarioId": "campus_general",
            "mode": "voice",
            "language": "zh-CN",
            "questionCountTarget": 4,
            "candidateProfile": {
                "targetRole": "产品经理实习生",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()
    session = payload["session"]
    turn = payload["turn"]

    assert session["id"].startswith("session_")
    assert session["scenarioId"] == "campus_general"
    assert session["status"] == "in_progress"
    assert session["currentTurnIndex"] == 1
    assert session["questionCountTarget"] == 4
    assert "current_turn_index" not in session

    assert turn["id"].startswith("turn_")
    assert turn["sessionId"] == session["id"]
    assert turn["index"] == 1
    assert turn["question"]["id"].startswith("q_")
    assert turn["question"]["text"] == "请先做一个 1 分钟自我介绍。"
    assert turn["question"]["type"] == "opening"
    assert turn["question"]["intent"] == "ask"
    assert turn["question"]["expectedSignals"] == ["表达结构", "经历匹配", "自信程度"]


def test_start_session_returns_not_found_for_unknown_scenario() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/interviews/sessions",
        json={
            "scenarioId": "missing",
            "mode": "text",
            "language": "zh-CN",
            "questionCountTarget": 3,
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SCENARIO_NOT_FOUND"
