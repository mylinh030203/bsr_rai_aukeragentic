"""Administration, search and notifications."""

from __future__ import annotations

from tests.conftest import csrf_headers, login_as


def test_admin_routes_reject_non_admins(seeded_client):
    login_as(seeded_client, "leadership")
    for path in (
        "/api/admin/users",
        "/api/admin/sources",
        "/api/admin/audit",
        "/api/admin/ai-executions",
    ):
        response = seeded_client.get(path)
        assert response.status_code == 403, path
        assert response.get_json()["error"]["code"] == "forbidden"


def test_admin_lists_users_sources_and_executions(seeded_client):
    login_as(seeded_client, "mi")
    users = seeded_client.get("/api/admin/users").get_json()["users"]
    assert len(users) == 3
    assert {user["role"] for user in users} == {"leadership", "mi", "internal"}

    sources = seeded_client.get("/api/admin/sources").get_json()["sources"]
    assert len(sources) == 10

    executions = seeded_client.get("/api/admin/ai-executions").get_json()["executions"]
    assert len(executions) == 4
    assert {row["task_type"] for row in executions} >= {"market_briefing", "chat_query"}

    alias = seeded_client.get("/api/ai/executions").get_json()["executions"]
    assert len(alias) == 4


def test_permission_change_is_audited(seeded_client, seeded_app):
    session = login_as(seeded_client, "mi")
    response = seeded_client.patch(
        "/api/admin/users/u-int",
        json={"can_export": True, "max_classification": "confidential"},
        headers=csrf_headers(session),
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["can_export"] is True
    assert response.get_json()["max_classification"] == "confidential"

    with seeded_app.app_context():
        from app.db import get_db

        rows = get_db().execute(
            "SELECT action, object_id, result FROM audit_log WHERE action = 'permission_change'"
        ).fetchall()
    assert [(row["action"], row["object_id"], row["result"]) for row in rows] == [
        ("permission_change", "u-int", "succeeded")
    ]


def test_audit_log_is_read_only(seeded_client):
    login_as(seeded_client, "mi")
    assert seeded_client.put("/api/admin/audit").status_code == 405
    assert seeded_client.delete("/api/admin/audit").status_code == 405


def test_search_is_permission_scoped(seeded_client):
    login_as(seeded_client, "internal")
    body = seeded_client.get("/api/search?q=Brent").get_json()
    instrument_ids = {row["id"] for row in body["instruments"]}
    assert "brent_futures" in instrument_ids
    assert "brent_physical" not in instrument_ids
    assert "N-2405" not in {row["id"] for row in body["news"]}
    assert "R-2026-039" not in {row["id"] for row in body["reports"]}


def test_notifications_are_scoped_and_markable(seeded_client):
    login_as(seeded_client, "leadership")
    leadership = seeded_client.get("/api/notifications").get_json()["notifications"]
    assert len(leadership) == 3
    own = next(item for item in leadership if item["title"] == "Report ready")

    login_as(seeded_client, "internal")
    internal = seeded_client.get("/api/notifications").get_json()["notifications"]
    assert len(internal) == 2
    assert all(item["title"] != "Report ready" for item in internal)

    session = login_as(seeded_client, "leadership")
    marked = seeded_client.post(
        f"/api/notifications/{own['id']}/read", headers=csrf_headers(session)
    )
    assert marked.status_code == 204
    refreshed = seeded_client.get("/api/notifications").get_json()["notifications"]
    assert next(item for item in refreshed if item["id"] == own["id"])["read_at"]

    login_as(seeded_client, "internal")
    session = login_as(seeded_client, "internal")
    denied = seeded_client.post(
        f"/api/notifications/{own['id']}/read", headers=csrf_headers(session)
    )
    assert denied.status_code == 404
