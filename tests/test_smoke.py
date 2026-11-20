def test_health_reports_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "db": "ok"}


def test_index_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"BSR Market Intelligence" in response.data


def test_unknown_api_route_uses_error_shape(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    body = response.get_json()
    assert body["error"]["code"] == "not_found"


def test_wrong_method_uses_error_shape(client):
    response = client.put("/api/overview")
    assert response.status_code == 405
    assert response.get_json()["error"]["code"] == "method_not_allowed"


def test_schema_created(app):
    with app.app_context():
        from app.db import get_db

        tables = {
            row["name"]
            for row in get_db().execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
    assert {"users", "sessions", "market_observations", "news_items", "reports", "audit_log"} <= tables
