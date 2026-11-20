"""Market data behavior: overview, series, observations, calculations, permissions."""

from __future__ import annotations

from tests.conftest import csrf_headers, login_as


def test_overview_shape_and_latest_values(seeded_client):
    login_as(seeded_client, "leadership")
    response = seeded_client.get("/api/overview")
    assert response.status_code == 200
    body = response.get_json()
    assert body["tape"]
    card = next(card for card in body["cards"] if card["instrument"]["id"] == "brent_futures")
    assert card["value"] == 78.42
    assert card["instrument"]["unit"] == "USD/bbl"
    assert card["source"]["name"] == "ICE (demo)"
    assert card["market_time"]
    assert card["ingested_at"]
    assert card["data_status"] == "real-time"
    assert card["quality_status"] == "valid"
    assert card["change"] is not None
    assert len(body["drivers"]) == 6
    assert body["highlights"]
    assert body["briefing"]["briefing_id"] == "B-1"
    assert body["briefing"]["version"] == 3
    assert body["restricted_hidden"] is False


def test_overview_hides_restricted_values_from_internal(seeded_client):
    login_as(seeded_client, "internal")
    body = seeded_client.get("/api/overview").get_json()
    ids = {card["instrument"]["id"] for card in body["cards"]}
    assert "brent_physical" not in ids
    assert all(card["classification"] != "restricted" for card in body["cards"])
    assert body["restricted_hidden"] is True
    assert "77.9" not in seeded_client.get("/api/overview").get_data(as_text=True)


def test_instruments_are_filtered_by_role(seeded_client):
    login_as(seeded_client, "internal")
    internal = seeded_client.get("/api/instruments").get_json()["instruments"]
    assert {row["id"] for row in internal}.isdisjoint({"brent_physical", "bsr_margin"})
    assert len(internal) == 11

    login_as(seeded_client, "leadership")
    leadership = seeded_client.get("/api/instruments").get_json()["instruments"]
    assert len(leadership) == 13


def test_restricted_instrument_detail_is_not_found_for_internal(seeded_client):
    login_as(seeded_client, "internal")
    response = seeded_client.get("/api/instruments/brent_physical")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"


def test_series_returns_points_compare_and_events(seeded_client):
    login_as(seeded_client, "leadership")
    response = seeded_client.get(
        "/api/instruments/brent_futures/series?range=7D&compare=wti_futures"
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body["series"]) == 2
    primary = body["series"][0]
    assert primary["unit"] == "USD/bbl"
    assert len(primary["points"]) == 7
    assert primary["points"][-1]["v"] == 78.42
    assert body["series"][1]["instrument"]["id"] == "wti_futures"
    assert body["events"]


def test_series_rejects_unknown_range(seeded_client):
    login_as(seeded_client, "leadership")
    response = seeded_client.get("/api/instruments/brent_futures/series?range=42")
    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "invalid_range"


def test_observations_list_includes_provenance(seeded_client):
    login_as(seeded_client, "leadership")
    response = seeded_client.get("/api/observations?instrument=brent_futures&limit=5")
    assert response.status_code == 200
    rows = response.get_json()["observations"]
    assert len(rows) == 5
    assert rows[0]["source"]["name"] == "ICE (demo)"
    assert rows[0]["market_time"] >= rows[1]["market_time"]


def test_formulas_are_listed_with_inputs(seeded_client):
    login_as(seeded_client, "leadership")
    formulas = seeded_client.get("/api/formulas").get_json()["formulas"]
    assert {formula["id"] for formula in formulas} == {
        "CS-GAS-2.1",
        "CS-DSL-2.0",
        "CS-321-1.3",
        "CS-STRICT-1.0",
    }
    gas = next(formula for formula in formulas if formula["id"] == "CS-GAS-2.1")
    assert gas["inputs"] == ["ron95", "brent_futures"]
    assert gas["allow_mixed_price_types"] is True


def test_crack_calculation_is_stored_and_deterministic(seeded_client):
    session = login_as(seeded_client, "mi")
    payload = {"formula_id": "CS-GAS-2.1", "as_of": "2026-11-14T09:42:00+07:00"}
    first = seeded_client.post(
        "/api/calculations/crack", json=payload, headers=csrf_headers(session)
    )
    assert first.status_code == 201, first.get_json()
    body = first.get_json()
    assert body["value"] == 13.68
    assert body["unit"] == "USD/bbl"
    assert body["formula"]["id"] == "CS-GAS-2.1"
    assert body["inputs"]
    assert body["calculated_at"]

    second = seeded_client.post(
        "/api/calculations/crack", json=payload, headers=csrf_headers(session)
    )
    assert second.status_code == 201
    assert second.get_json()["observation_id"] == body["observation_id"]
    assert second.get_json()["value"] == body["value"]


def test_conflicting_recalculation_is_rejected(seeded_client):
    session = login_as(seeded_client, "mi")
    payload = {"formula_id": "CS-GAS-2.1", "as_of": "2026-11-14T09:42:00+07:00"}
    assert (
        seeded_client.post(
            "/api/calculations/crack", json=payload, headers=csrf_headers(session)
        ).status_code
        == 201
    )
    newer_input = {
        "instrument_id": "ron95",
        "value": 95.0,
        "unit": "USD/bbl",
        "market_time": "2026-11-14T09:00:00+07:00",
        "source_id": "SRC-PLATTS",
        "data_status": "eod",
        "quality_status": "valid",
        "classification": "internal",
    }
    created = seeded_client.post(
        "/api/observations", json=newer_input, headers=csrf_headers(session)
    )
    assert created.status_code == 201, created.get_json()
    conflict = seeded_client.post(
        "/api/calculations/crack", json=payload, headers=csrf_headers(session)
    )
    assert conflict.status_code == 409
    assert conflict.get_json()["error"]["code"] == "calculation_exists"


def test_mixed_price_types_formula_is_rejected(seeded_client):
    session = login_as(seeded_client, "mi")
    response = seeded_client.post(
        "/api/calculations/crack",
        json={"formula_id": "CS-STRICT-1.0", "as_of": "2026-11-14T09:42:00+07:00"},
        headers=csrf_headers(session),
    )
    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "mixed_price_types"


def test_manual_observation_is_validated_and_audited(seeded_client, seeded_app):
    session = login_as(seeded_client, "mi")
    body = {
        "instrument_id": "wti_futures",
        "value": 75.25,
        "unit": "USD/bbl",
        "market_time": "2026-11-14T08:00:00+07:00",
        "source_id": "SRC-CME",
        "data_status": "real-time",
        "quality_status": "valid",
        "classification": "internal",
    }
    response = seeded_client.post("/api/observations", json=body, headers=csrf_headers(session))
    assert response.status_code == 201, response.get_json()
    assert response.get_json()["value"] == 75.25

    with seeded_app.app_context():
        from app.db import get_db

        actions = [row["action"] for row in get_db().execute("SELECT action FROM audit_log")]
    assert "manual_observation" in actions


def test_manual_observation_rejects_unit_and_classification_errors(seeded_client):
    session = login_as(seeded_client, "mi")
    base = {
        "instrument_id": "wti_futures",
        "value": 75.25,
        "unit": "USD/bbl",
        "market_time": "2026-11-14T08:00:00+07:00",
        "source_id": "SRC-CME",
        "data_status": "real-time",
        "quality_status": "valid",
        "classification": "internal",
    }
    wrong_unit = seeded_client.post(
        "/api/observations", json={**base, "unit": "VND"}, headers=csrf_headers(session)
    )
    assert wrong_unit.status_code == 422
    assert wrong_unit.get_json()["error"]["code"] == "invalid_unit"

    future = seeded_client.post(
        "/api/observations",
        json={**base, "market_time": "2030-01-01T00:00:00+07:00"},
        headers=csrf_headers(session),
    )
    assert future.status_code == 422
    assert future.get_json()["error"]["code"] == "future_market_time"

    below = seeded_client.post(
        "/api/observations",
        json={
            **base,
            "instrument_id": "brent_physical",
            "classification": "internal",
        },
        headers=csrf_headers(session),
    )
    assert below.status_code == 422
    assert below.get_json()["error"]["code"] == "classification_below_instrument"


def test_manual_observation_is_limited_to_mi(seeded_client):
    session = login_as(seeded_client, "leadership")
    response = seeded_client.post(
        "/api/observations",
        json={
            "instrument_id": "wti_futures",
            "value": 75.25,
            "unit": "USD/bbl",
            "market_time": "2026-11-14T08:00:00+07:00",
            "source_id": "SRC-CME",
            "data_status": "real-time",
            "quality_status": "valid",
            "classification": "internal",
        },
        headers=csrf_headers(session),
    )
    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "forbidden"


def test_restricted_view_is_audited_for_an_authorized_role(seeded_client, seeded_app):
    login_as(seeded_client, "leadership")
    assert seeded_client.get("/api/instruments/brent_physical").status_code == 200
    with seeded_app.app_context():
        from app.db import get_db

        rows = get_db().execute(
            "SELECT object_id FROM audit_log WHERE action = 'restricted_view'"
        ).fetchall()
    assert [row["object_id"] for row in rows] == ["brent_physical"]


def test_restricted_view_is_not_audited_for_an_unauthorized_role(seeded_client, seeded_app):
    login_as(seeded_client, "internal")
    assert seeded_client.get("/api/instruments/brent_physical").status_code == 404
    with seeded_app.app_context():
        from app.db import get_db

        count = get_db().execute(
            "SELECT COUNT(*) FROM audit_log WHERE action = 'restricted_view'"
        ).fetchone()[0]
    assert count == 0


def test_series_events_include_source_and_linked_instruments(seeded_client):
    login_as(seeded_client, "leadership")
    events = seeded_client.get(
        "/api/instruments/brent_futures/series?range=1M"
    ).get_json()["events"]
    inventory_event = next(event for event in events if event["id"] == "E-4")
    assert inventory_event["source"]["name"] == "EIA (demo)"
    assert "wti_futures" in inventory_event["instruments"]
    assert "brent_futures" in inventory_event["instruments"]


def test_instrument_list_audits_restricted_view(seeded_client, seeded_app):
    login_as(seeded_client, "leadership")
    assert seeded_client.get("/api/instruments").status_code == 200
    with seeded_app.app_context():
        from app.db import get_db

        rows = get_db().execute(
            "SELECT object_id FROM audit_log WHERE action = 'restricted_view'"
        ).fetchall()
    assert "brent_physical" in {row["object_id"] for row in rows}


def test_search_audits_restricted_view(seeded_client, seeded_app):
    login_as(seeded_client, "leadership")
    assert seeded_client.get("/api/search?q=Brent").status_code == 200
    with seeded_app.app_context():
        from app.db import get_db

        rows = get_db().execute(
            "SELECT object_id FROM audit_log WHERE action = 'restricted_view'"
        ).fetchall()
    assert "brent_physical" in {row["object_id"] for row in rows}


def test_restricted_observation_on_a_visible_instrument_is_audited(seeded_client, seeded_app):
    session = login_as(seeded_client, "mi")
    payload = {
        "instrument_id": "ron95",
        "value": 91.5,
        "unit": "USD/bbl",
        "market_time": "2026-11-14T09:10:00+07:00",
        "source_id": "SRC-PLATTS",
        "data_status": "eod",
        "quality_status": "valid",
        "classification": "restricted",
    }
    created = seeded_client.post("/api/observations", json=payload, headers=csrf_headers(session))
    assert created.status_code == 201, created.get_json()
    observation_id = created.get_json()["id"]

    login_as(seeded_client, "leadership")
    listing = seeded_client.get("/api/instruments").get_json()["instruments"]
    ron95 = next(item for item in listing if item["id"] == "ron95")
    assert ron95["latest"]["id"] == observation_id
    with seeded_app.app_context():
        from app.db import get_db

        rows = get_db().execute(
            "SELECT object_type, object_id FROM audit_log WHERE action = 'restricted_view'"
        ).fetchall()
    assert ("market_observation", str(observation_id)) in {
        (row["object_type"], row["object_id"]) for row in rows
    }


def test_unauthorized_roles_create_no_restricted_view_rows(seeded_client, seeded_app):
    session = login_as(seeded_client, "mi")
    payload = {
        "instrument_id": "ron95",
        "value": 91.4,
        "unit": "USD/bbl",
        "market_time": "2026-11-14T09:11:00+07:00",
        "source_id": "SRC-PLATTS",
        "data_status": "eod",
        "quality_status": "valid",
        "classification": "restricted",
    }
    assert (
        seeded_client.post("/api/observations", json=payload, headers=csrf_headers(session)).status_code
        == 201
    )

    login_as(seeded_client, "internal")
    listing = seeded_client.get("/api/instruments").get_json()["instruments"]
    ron95 = next(item for item in listing if item["id"] == "ron95")
    assert ron95["latest"] is None
    assert seeded_client.get("/api/instruments/ron95").get_json()["latest"] is None
    assert seeded_client.get("/api/search?q=RON95").status_code == 200
    with seeded_app.app_context():
        from app.db import get_db

        count = get_db().execute(
            "SELECT COUNT(*) FROM audit_log WHERE action = 'restricted_view'"
        ).fetchone()[0]
    assert count == 0
