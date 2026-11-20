"""Forecast register: current versions, immutable history, evaluation."""

from __future__ import annotations

from tests.conftest import csrf_headers, login_as


def test_forecast_list_is_filtered_by_role(seeded_client):
    login_as(seeded_client, "leadership")
    leadership = seeded_client.get("/api/forecasts").get_json()["forecasts"]
    assert len(leadership) == 6
    assert {row["id"] for row in leadership} >= {"F-101", "F-104"}

    login_as(seeded_client, "internal")
    internal = seeded_client.get("/api/forecasts").get_json()["forecasts"]
    assert len(internal) == 5
    assert "F-104" not in {row["id"] for row in internal}


def test_forecast_filters(seeded_client):
    login_as(seeded_client, "leadership")
    brent = seeded_client.get("/api/forecasts?instrument=brent_futures").get_json()["forecasts"]
    assert {row["id"] for row in brent} == {"F-101", "F-102"}
    eia = seeded_client.get("/api/forecasts?source=SRC-EIA").get_json()["forecasts"]
    assert {row["id"] for row in eia} == {"F-101", "F-106"}
    monthly = seeded_client.get("/api/forecasts?horizon=1-month").get_json()["forecasts"]
    assert {row["id"] for row in monthly} == {"F-103", "F-104"}


def test_version_history_is_newest_first(seeded_client):
    login_as(seeded_client, "leadership")
    versions = seeded_client.get("/api/forecasts/F-101/versions").get_json()["versions"]
    assert [row["version"] for row in versions] == [3, 2, 1]
    assert versions[0]["value"] == 79.5
    assert versions[1]["value"] == 80.2
    assert versions[0]["actual"] == 78.42
    assert versions[0]["absolute_error"] == 1.08


def test_new_version_never_overwrites_history(seeded_client, seeded_app):
    session = login_as(seeded_client, "mi")
    with seeded_app.app_context():
        from app.db import get_db

        before = [
            dict(row)
            for row in get_db().execute(
                "SELECT version, value, methodology FROM forecast_versions "
                "WHERE forecast_id = 'F-101' ORDER BY version"
            )
        ]

    response = seeded_client.post(
        "/api/forecasts/F-101/versions",
        json={
            "value": 80.1,
            "methodology": "Updated STEO baseline",
            "published_at": "2026-11-14T09:00:00+07:00",
        },
        headers=csrf_headers(session),
    )
    assert response.status_code == 201, response.get_json()
    assert response.get_json()["version"] == 4
    assert response.get_json()["value"] == 80.1

    with seeded_app.app_context():
        from app.db import get_db

        after = [
            dict(row)
            for row in get_db().execute(
                "SELECT version, value, methodology FROM forecast_versions "
                "WHERE forecast_id = 'F-101' ORDER BY version"
            )
        ]
    assert after[: len(before)] == before
    assert len(after) == len(before) + 1


def test_evaluation_reports_errors_and_missing_actuals(seeded_client):
    login_as(seeded_client, "leadership")
    body = seeded_client.get("/api/forecasts/evaluation").get_json()
    items = {item["id"]: item for item in body["items"]}
    assert items["F-101"]["absolute_error"] == 1.08
    assert items["F-101"]["percentage_error"] == round(1.08 / 78.42 * 100, 6)
    assert items["F-102"]["note"] == "actual missing"
    assert items["F-102"]["absolute_error"] is None
    assert body["aggregates"]
    eia = next(
        row for row in body["aggregates"] if row["source"] == "EIA (demo)" and row["horizon"] == "3-month"
    )
    assert eia["count"] == 1
    assert eia["missing"] == 1
    assert eia["mae"] == 1.08


def test_new_version_is_limited_to_mi(seeded_client):
    session = login_as(seeded_client, "leadership")
    response = seeded_client.post(
        "/api/forecasts/F-101/versions",
        json={"value": 80.1, "methodology": "x", "published_at": "2026-11-14T09:00:00+07:00"},
        headers=csrf_headers(session),
    )
    assert response.status_code == 403


def test_actual_value_is_filtered_when_the_observation_is_not_readable(seeded_app, seeded_client):
    with seeded_app.app_context():
        from app.db import get_db

        db = get_db()
        cursor = db.execute(
            "INSERT INTO market_observations (instrument_id, source_id, value, unit, market_time, "
            "ingested_at, data_status, quality_status, classification) "
            "VALUES ('brent_futures', 'SRC-PLATTS', 81.0, 'USD/bbl', "
            "'2026-11-14T07:00:00+07:00', '2026-11-14T07:01:00+07:00', 'eod', 'valid', 'restricted')"
        )
        observation_id = cursor.lastrowid
        version = db.execute(
            "SELECT id FROM forecast_versions WHERE forecast_id = 'F-101' ORDER BY version DESC LIMIT 1"
        ).fetchone()
        db.execute(
            "UPDATE forecast_evaluations SET actual_observation_id = ? WHERE forecast_version_id = ?",
            (observation_id, version["id"]),
        )
        db.commit()

    login_as(seeded_client, "internal")
    forecasts = seeded_client.get("/api/forecasts").get_json()["forecasts"]
    brent = next(item for item in forecasts if item["id"] == "F-101")
    assert brent["actual"] is None
    assert brent["note"] == "actual missing"
