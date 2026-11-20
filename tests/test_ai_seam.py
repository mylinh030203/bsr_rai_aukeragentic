"""The shared AI seam: one task + one execution per call, fallback included."""

from __future__ import annotations

import pytest

from app.ai import provider
from app.db import get_db
from app.services.ai_runs import execute


@pytest.fixture()
def seeded_app(app):
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO users (id, name, role, department, max_classification, "
            "can_view_restricted, can_export, is_admin, created_at) "
            "VALUES ('u-mi', 'Ha', 'mi', 'Market Intelligence', 'restricted', 1, 1, 1, "
            "'2026-11-14T00:00:00+00:00')"
        )
        db.commit()
    return app


def _user(db):
    return db.execute("SELECT * FROM users WHERE id = 'u-mi'").fetchone()


def test_execute_records_one_task_and_one_execution(seeded_app):
    with seeded_app.app_context():
        db = get_db()
        result = execute(
            db,
            task_type="news_summarization",
            user=_user(db),
            task_input={"title": "OPEC+", "body": "Output guidance unchanged."},
            context={"title": "OPEC+", "body": "Output guidance unchanged.", "topics": ["OPEC+"]},
        )
        assert result["status"] == "succeeded"
        assert result["output"]["summary"].startswith("Output guidance")
        tasks = db.execute("SELECT COUNT(*) FROM ai_tasks").fetchone()[0]
        executions = db.execute("SELECT COUNT(*) FROM ai_executions").fetchone()[0]
        assert tasks == 1
        assert executions == 1
        row = db.execute("SELECT * FROM ai_executions").fetchone()
        assert row["task_id"] == result["task_id"]
        assert row["status"] == "succeeded"
        assert row["validation"] == "passed"
        assert row["latency_ms"] >= 1


def test_provider_is_deterministic():
    context = {"question": "What moved?", "evidence": [{"kind": "observation", "id": "1", "label": "Brent"}],
               "calculations": [{"label": "5-day return", "value": "+2.1%"}], "tools_used": ["observations"]}
    first = provider.run("chat_query", context)
    second = provider.run("chat_query", context)
    assert first == second


def test_failing_provider_becomes_a_labelled_fallback(seeded_app, monkeypatch):
    with seeded_app.app_context():
        db = get_db()

        def broken(task_type, context):
            raise RuntimeError("adapter offline")

        monkeypatch.setattr(provider, "run", broken)
        result = execute(
            db,
            task_type="chat_query",
            user=_user(db),
            task_input={"question": "Brent?"},
            context={"question": "Brent?"},
        )
        assert result["status"] == "fallback"
        assert result["output"]["fallback"] is True
        row = db.execute("SELECT status, validation FROM ai_executions").fetchone()
        assert row["status"] == "fallback"
        assert row["validation"] == "fallback"


def test_unknown_task_type_is_a_caller_error(seeded_app):
    with seeded_app.app_context():
        db = get_db()
        with pytest.raises(ValueError):
            execute(
                db,
                task_type="not_a_task",
                user=_user(db),
                task_input={},
                context={},
            )
        assert db.execute("SELECT COUNT(*) FROM ai_tasks").fetchone()[0] == 0
