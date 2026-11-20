"""Assistant: citations, deterministic numbers, restricted refusal, fallback, limits."""

from __future__ import annotations

from app.ai import provider
from tests.conftest import csrf_headers, login_as


def test_assistant_answers_with_citations_and_an_execution(seeded_client, seeded_app):
    session = login_as(seeded_client, "leadership")
    response = seeded_client.post(
        "/api/assistant/query",
        json={"question": "What is driving Brent today?"},
        headers=csrf_headers(session),
    )
    assert response.status_code == 201, response.get_json()
    body = response.get_json()
    assert "AI interpretation" in body["answer"]
    assert body["citations"]
    assert all(citation["id"] for citation in body["citations"])
    assert body["execution"]["status"] == "succeeded"
    assert body["execution"]["task_id"].startswith("AI-")

    with seeded_app.app_context():
        from app.db import get_db

        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM ai_tasks").fetchone()[0] == 5
        assert db.execute("SELECT COUNT(*) FROM ai_executions").fetchone()[0] == 5
        actions = [row["action"] for row in db.execute("SELECT action FROM audit_log")]
        audit_rows = {
            (row["object_type"], row["object_id"])
            for row in db.execute(
                "SELECT object_type, object_id FROM audit_log WHERE action = 'restricted_view'"
            )
        }
    assert "ai_request" in actions
    assert ("news_item", "N-2405") in audit_rows or ("market_observation", "1095") in audit_rows


def test_restricted_question_gets_a_refusal_without_restricted_records(seeded_client):
    session = login_as(seeded_client, "internal")
    response = seeded_client.post(
        "/api/assistant/query",
        json={"question": "What is the dated Brent physical price?"},
        headers=csrf_headers(session),
    )
    assert response.status_code == 201
    body = response.get_json()
    assert "not available in your scope" in body["refusal"]
    text = response.get_data(as_text=True)
    assert "N-2405" not in text
    assert "77.9" not in text
    assert "brent_physical" not in text
    assert all(citation["kind"] != "news" or citation["id"] != "N-2405" for citation in body["citations"])


def test_calculation_questions_use_deterministic_analytics(seeded_client):
    session = login_as(seeded_client, "leadership")
    body = seeded_client.post(
        "/api/assistant/query",
        json={"question": "What is the gasoline crack spread?"},
        headers=csrf_headers(session),
    ).get_json()
    crack = next(
        item for item in body["calculations"] if item["label"].startswith("Gasoline crack")
    )
    assert crack["value"] == 13.68
    assert "CS-GAS-2.1" in crack["method"]
    assert "Deterministic calculations" in body["answer"]


def test_failing_provider_is_reported_as_fallback(seeded_client, monkeypatch):
    session = login_as(seeded_client, "leadership")
    monkeypatch.setattr(provider, "run", lambda task_type, context: (_ for _ in ()).throw(RuntimeError("down")))
    response = seeded_client.post(
        "/api/assistant/query",
        json={"question": "Brent?"},
        headers=csrf_headers(session),
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["execution"]["status"] == "fallback"
    assert "could not interpret" in body["answer"]


def test_assistant_is_rate_limited_per_user(seeded_app, seeded_client):
    seeded_app.config["RATE_LIMITS"] = {
        **seeded_app.config["RATE_LIMITS"],
        "assistant": {"limit": 2, "window_seconds": 300},
    }
    session = login_as(seeded_client, "leadership")
    for _ in range(2):
        assert (
            seeded_client.post(
                "/api/assistant/query",
                json={"question": "Brent?"},
                headers=csrf_headers(session),
            ).status_code
            == 201
        )
    blocked = seeded_client.post(
        "/api/assistant/query",
        json={"question": "Brent?"},
        headers=csrf_headers(session),
    )
    assert blocked.status_code == 429
