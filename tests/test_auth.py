"""Session, CSRF and rate-limit behavior."""

from __future__ import annotations

import pytest

from app.db import get_db

USERS = [
    ("u-lead", "Lê Minh Anh", "leadership", "Executive Office", "restricted", 1, 0, 0),
    ("u-mi", "Nguyễn Thu Hà", "mi", "Market Intelligence", "restricted", 1, 1, 1),
    ("u-int", "Trần Quốc Bảo", "internal", "Commercial", "internal", 0, 0, 0),
]


@pytest.fixture()
def client(app):
    with app.app_context():
        db = get_db()
        for user_id, name, role, department, max_classification, view, export, admin in USERS:
            db.execute(
                "INSERT INTO users (id, name, role, department, max_classification, "
                "can_view_restricted, can_export, is_admin, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, '2026-11-14T00:00:00+00:00')",
                (user_id, name, role, department, max_classification, view, export, admin),
            )
        db.commit()
    return app.test_client()


def login(client, role="leadership"):
    response = client.post("/api/auth/session", json={"role": role})
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def test_login_sets_httponly_lax_cookie(client):
    body = login(client)
    assert body["user"]["role"] == "leadership"
    assert body["csrf_token"]
    cookie = client.get("/api/me").headers.get("Set-Cookie")
    assert cookie is None  # /api/me does not re-issue the cookie
    set_cookie = client.post("/api/auth/session", json={"role": "mi"}).headers["Set-Cookie"]
    assert "bsr_session=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=Lax" in set_cookie
    assert "Path=/" in set_cookie


def test_secure_cookie_on_https(client):
    response = client.post(
        "/api/auth/session",
        json={"role": "leadership"},
        base_url="https://localhost",
    )
    assert "Secure" in response.headers["Set-Cookie"]


def test_me_requires_a_session(client):
    response = client.get("/api/me")
    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "unauthorized"


def test_me_returns_user_and_csrf(client):
    body = login(client, "mi")
    response = client.get("/api/me")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["user"]["id"] == "u-mi"
    assert payload["user"]["can_export"] is True
    assert payload["csrf_token"] == body["csrf_token"]


def test_csrf_is_required_for_state_changing_requests(client):
    body = login(client)
    denied = client.delete("/api/auth/session")
    assert denied.status_code == 403
    assert denied.get_json()["error"]["code"] == "csrf_failed"
    allowed = client.delete(
        "/api/auth/session", headers={"X-CSRF-Token": body["csrf_token"]}
    )
    assert allowed.status_code == 204


def test_sign_out_invalidates_the_server_side_session(client):
    body = login(client)
    token = client.get_cookie("bsr_session").value
    client.delete("/api/auth/session", headers={"X-CSRF-Token": body["csrf_token"]})
    client.set_cookie("bsr_session", token)
    response = client.get("/api/me")
    assert response.status_code == 401


def test_login_is_rate_limited_per_address(client):
    for _ in range(10):
        assert client.post("/api/auth/session", json={"role": "leadership"}).status_code == 201
    blocked = client.post("/api/auth/session", json={"role": "leadership"})
    assert blocked.status_code == 429
    assert blocked.get_json()["error"]["code"] == "rate_limited"


def test_invalid_role_is_rejected(client):
    response = client.post("/api/auth/session", json={"role": "admin"})
    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "invalid_role"


def test_sign_in_and_sign_out_are_audited(app, client):
    body = login(client)
    client.delete("/api/auth/session", headers={"X-CSRF-Token": body["csrf_token"]})
    with app.app_context():
        actions = [
            row["action"]
            for row in get_db().execute("SELECT action FROM audit_log ORDER BY id")
        ]
    assert actions == ["sign_in", "sign_out"]
