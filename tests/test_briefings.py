"""Briefings and the computed analysis workspace."""

from __future__ import annotations

from tests.conftest import csrf_headers, login_as


def test_seeded_briefing_versions_are_newest_first(seeded_client):
    login_as(seeded_client, "leadership")
    briefings = seeded_client.get("/api/briefings").get_json()["briefings"]
    assert [item["version"] for item in briefings] == [3, 2, 1]
    assert briefings[0]["headline"] == "Supply risk meets product strength"
    assert briefings[0]["classification"] == "internal"
    assert briefings[0]["sources"]
    assert briefings[0]["moves"]


def test_regeneration_adds_a_version_and_keeps_history(seeded_client, seeded_app):
    session = login_as(seeded_client, "mi")
    with seeded_app.app_context():
        from app.db import get_db

        before = [
            dict(row)
            for row in get_db().execute(
                "SELECT version, headline, moves FROM briefing_versions "
                "WHERE briefing_id = 'B-1' ORDER BY version"
            )
        ]

    response = seeded_client.post("/api/briefings", headers=csrf_headers(session))
    assert response.status_code == 201, response.get_json()
    body = response.get_json()
    assert body["version"] == 4
    assert body["classification"] == "internal"
    assert body["sources"]

    with seeded_app.app_context():
        from app.db import get_db

        db = get_db()
        after = [
            dict(row)
            for row in db.execute(
                "SELECT version, headline, moves FROM briefing_versions "
                "WHERE briefing_id = 'B-1' ORDER BY version"
            )
        ]
        assert after[: len(before)] == before
        assert db.execute("SELECT COUNT(*) FROM ai_tasks").fetchone()[0] == 5
        actions = [row["action"] for row in db.execute("SELECT action FROM audit_log")]
    assert "briefing_generated" in actions


def test_confidential_briefing_is_hidden_from_internal(seeded_app, seeded_client):
    with seeded_app.app_context():
        from app.db import get_db

        db = get_db()
        db.execute(
            "INSERT INTO briefings (id, title, created_at, classification) "
            "VALUES ('B-2', 'Restricted operations briefing', '2026-11-14T00:00:00+00:00', 'confidential')"
        )
        db.execute(
            "INSERT INTO briefing_versions (briefing_id, version, generated_at, data_cutoff, headline, "
            "moves, drivers, watchlist, classification) VALUES ('B-2', 1, '2026-11-14T00:00:00+00:00', "
            "'2026-11-13T00:00:00+00:00', 'Internal only', '[]', '[]', '[]', 'confidential')"
        )
        db.commit()

    login_as(seeded_client, "internal")
    ids = {item["briefing_id"] for item in seeded_client.get("/api/briefings").get_json()["briefings"]}
    assert ids == {"B-1"}

    login_as(seeded_client, "mi")
    ids = {item["briefing_id"] for item in seeded_client.get("/api/briefings").get_json()["briefings"]}
    assert ids == {"B-1", "B-2"}


def test_analysis_is_computed_with_an_evidence_ledger(seeded_client):
    login_as(seeded_client, "leadership")
    body = seeded_client.get("/api/analysis?question=What is driving cracks?").get_json()
    assert body["status"] == "computed"
    assert body["facts"]
    assert body["evidence"]
    crack = next(item for item in body["calculations"] if item["label"].startswith("Gasoline crack"))
    assert crack["value"] == 13.68
    assert body["assumptions"]
    assert body["recommendation"]["title"]
    assert body["execution"]["task_id"].startswith("AI-")


def test_internal_analysis_states_the_restricted_boundary(seeded_client):
    login_as(seeded_client, "internal")
    body = seeded_client.get("/api/analysis?question=What moved?").get_json()
    assert any("restricted" in assumption.lower() for assumption in body["assumptions"])
    assert "brent_physical" not in seeded_client.get(
        "/api/analysis?question=What moved?"
    ).get_data(as_text=True)


def test_briefing_generation_is_limited_to_mi(seeded_client):
    session = login_as(seeded_client, "leadership")
    response = seeded_client.post("/api/briefings", headers=csrf_headers(session))
    assert response.status_code == 403


def test_older_confidential_version_stays_hidden_after_internal_regeneration(
    seeded_client, seeded_app
):
    session = login_as(seeded_client, "mi")
    confidential = {
        "title": "Dung Quat confidential maintenance detail",
        "body": "Internal operations detail for the maintenance window.",
        "source_id": "SRC-BSR-IN",
        "published_at": "2026-11-14T09:30:00+07:00",
        "classification": "confidential",
    }
    assert (
        seeded_client.post("/api/news", json=confidential, headers=csrf_headers(session)).status_code
        == 201
    )
    first = seeded_client.post("/api/briefings", headers=csrf_headers(session))
    assert first.status_code == 201
    assert first.get_json()["classification"] == "confidential"

    for index in range(3):
        item = {
            "title": f"Internal market note {index}",
            "body": "A newer internal item that pushes the confidential item out of the top three.",
            "source_id": "SRC-REUTERS",
            "published_at": f"2026-11-14T09:4{index}:00+07:00",
            "classification": "internal",
        }
        assert (
            seeded_client.post("/api/news", json=item, headers=csrf_headers(session)).status_code
            == 201
        )
    second = seeded_client.post("/api/briefings", headers=csrf_headers(session))
    assert second.status_code == 201
    assert second.get_json()["classification"] == "internal"

    login_as(seeded_client, "internal")
    versions = seeded_client.get("/api/briefings").get_json()["briefings"]
    assert all(item["classification"] != "confidential" for item in versions)
    assert all(item["version"] != first.get_json()["version"] for item in versions)

    login_as(seeded_client, "mi")
    mi_versions = seeded_client.get("/api/briefings").get_json()["briefings"]
    assert any(item["version"] == first.get_json()["version"] for item in mi_versions)
