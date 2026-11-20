"""Reports: frozen content, versions, export gate and audit."""

from __future__ import annotations

from tests.conftest import csrf_headers, login_as


def test_report_list_is_filtered_by_role(seeded_client):
    login_as(seeded_client, "leadership")
    assert len(seeded_client.get("/api/reports").get_json()["reports"]) == 3

    login_as(seeded_client, "internal")
    ids = {row["id"] for row in seeded_client.get("/api/reports").get_json()["reports"]}
    assert ids == {"R-2026-041", "R-2026-040"}


def test_confidential_report_is_not_found_for_internal(seeded_client):
    login_as(seeded_client, "internal")
    response = seeded_client.get("/api/reports/R-2026-039")
    assert response.status_code == 404


def test_report_generation_freezes_content_and_sources(seeded_client, seeded_app):
    session = login_as(seeded_client, "leadership")
    response = seeded_client.post(
        "/api/reports",
        json={
            "type": "On-demand Market Analysis",
            "range_start": "2026-11-01T00:00:00+07:00",
            "range_end": "2026-11-14T23:59:00+07:00",
        },
        headers=csrf_headers(session),
    )
    assert response.status_code == 201, response.get_json()
    body = response.get_json()
    assert body["id"].startswith("R-2026-")
    # The range includes a restricted physical observation, so the report
    # inherits the highest classification of its inputs.
    assert body["classification"] == "restricted"
    assert body["versions"][0]["content"]["sections"]
    assert body["versions"][0]["sources"]

    frozen = body["versions"][0]["content"]
    with seeded_app.app_context():
        from app.db import get_db

        db = get_db()
        db.execute(
            "UPDATE market_observations SET value = 999 WHERE instrument_id = 'brent_futures'"
        )
        db.commit()

    reread = seeded_client.get(f"/api/reports/{body['id']}").get_json()
    assert reread["versions"][0]["content"] == frozen


def test_export_returns_a_pdf_for_an_authorized_role(seeded_client):
    login_as(seeded_client, "mi")
    response = seeded_client.get("/api/reports/R-2026-041/export.pdf")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF-1.4")
    assert b"Morning briefing" in response.data


def test_export_is_denied_and_audited_without_permission(seeded_client, seeded_app):
    login_as(seeded_client, "leadership")
    response = seeded_client.get("/api/reports/R-2026-041/export.pdf")
    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "export_denied"
    with seeded_app.app_context():
        from app.db import get_db

        rows = get_db().execute(
            "SELECT action, result FROM audit_log WHERE action = 'export_attempt'"
        ).fetchall()
    assert [(row["action"], row["result"]) for row in rows] == [("export_attempt", "denied")]


def test_export_is_rate_limited(seeded_app, seeded_client):
    seeded_app.config["RATE_LIMITS"] = {
        **seeded_app.config["RATE_LIMITS"],
        "export": {"limit": 2, "window_seconds": 300},
    }
    login_as(seeded_client, "mi")
    for _ in range(2):
        assert seeded_client.get("/api/reports/R-2026-041/export.pdf").status_code == 200
    blocked = seeded_client.get("/api/reports/R-2026-041/export.pdf")
    assert blocked.status_code == 429
