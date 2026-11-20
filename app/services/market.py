"""Market data service: overview, series, observations, formulas, calculations."""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone

from ..db import utc_now
from ..errors import ApiError
from ..permissions import can_read, rank, visible_rows
from . import analytics
from .audit import record, record_restricted_view

RANGE_DAYS = {"7D": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
CLASSIFICATIONS = ("public", "internal", "confidential", "restricted")
DATA_STATUSES = ("real-time", "delayed", "eod", "manual")
QUALITY_STATUSES = ("valid", "pending", "rejected", "corrected")


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def _parse_time(value, field: str = "market_time") -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ApiError(422, "invalid_time", f"{field} must be an ISO 8601 timestamp.")
    if parsed.tzinfo is None:
        raise ApiError(422, "invalid_time", f"{field} must include a UTC offset.")
    return parsed


def instrument_payload(row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "short_name": row["short_name"],
        "ticker": row["ticker"],
        "group": row["group_name"],
        "unit": row["unit"],
        "price_type": row["price_type"],
        "decimals": row["decimals"],
        "classification": row["classification"],
        "description": row["description"],
        "formula_id": row["formula_id"],
    }


def observation_payload(row, source_name: str | None = None) -> dict:
    return {
        "id": row["id"],
        "instrument_id": row["instrument_id"],
        "value": row["value"],
        "unit": row["unit"],
        "market_time": row["market_time"],
        "ingested_at": row["ingested_at"],
        "data_status": row["data_status"],
        "quality_status": row["quality_status"],
        "classification": row["classification"],
        "source": {"id": row["source_id"], "name": source_name or row["source_id"]},
        "formula_id": row["formula_id"],
        "calculated_at": row["calculated_at"],
    }


def formula_payload(row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "version": row["version"],
        "expression": row["expression"],
        "inputs": json.loads(row["input_instruments"]),
        "allow_mixed_price_types": bool(row["allow_mixed_price_types"]),
        "unit": row["unit"],
    }


def _latest(db, instrument_id: str):
    return db.execute(
        "SELECT o.*, s.name AS source_name FROM market_observations o "
        "JOIN sources s ON s.id = o.source_id WHERE o.instrument_id = ? "
        "ORDER BY o.market_time DESC LIMIT 1",
        (instrument_id,),
    ).fetchone()


def _previous(db, instrument_id: str):
    return db.execute(
        "SELECT o.*, s.name AS source_name FROM market_observations o "
        "JOIN sources s ON s.id = o.source_id WHERE o.instrument_id = ? "
        "ORDER BY o.market_time DESC LIMIT 1 OFFSET 1",
        (instrument_id,),
    ).fetchone()


def _visible_instrument(db, user, instrument_id: str):
    row = db.execute("SELECT * FROM instruments WHERE id = ?", (instrument_id,)).fetchone()
    if row is None or not can_read(row, user):
        raise ApiError(404, "not_found", "Instrument not found.")
    return row


def overview(db, user) -> dict:
    instruments = visible_rows(
        db.execute("SELECT * FROM instruments ORDER BY display_order").fetchall(), user
    )
    cards, tape, latest_times, statuses = [], [], [], set()
    for instrument in instruments:
        latest = _latest(db, instrument["id"])
        if latest is None or not can_read(latest, user):
            continue
        previous = _previous(db, instrument["id"])
        change = None
        change_pct = None
        if previous is not None and can_read(previous, user):
            change = analytics.absolute_change(previous["value"], latest["value"])
            change_pct = analytics.percentage_change(previous["value"], latest["value"])
        card = {
            "instrument": instrument_payload(instrument),
            "value": latest["value"],
            "change": change,
            "change_pct": change_pct,
            "market_time": latest["market_time"],
            "ingested_at": latest["ingested_at"],
            "data_status": latest["data_status"],
            "quality_status": latest["quality_status"],
            "classification": latest["classification"],
            "source": {"id": latest["source_id"], "name": latest["source_name"]},
            "formula": None,
        }
        if instrument["formula_id"]:
            formula = db.execute(
                "SELECT * FROM formulas WHERE id = ?", (instrument["formula_id"],)
            ).fetchone()
            if formula is not None:
                card["formula"] = formula_payload(formula)
        if latest["classification"] == "restricted":
            record_restricted_view(db, user, "market_observation", latest["id"])
        cards.append(card)
        latest_times.append(latest["market_time"])
        statuses.add(latest["data_status"])
        if len(tape) < 6:
            tape.append(
                {
                    "instrument_id": instrument["id"],
                    "short_name": instrument["short_name"],
                    "value": latest["value"],
                    "unit": latest["unit"],
                    "change": change,
                    "change_pct": change_pct,
                    "data_status": latest["data_status"],
                }
            )

    drivers = visible_rows(
        db.execute("SELECT * FROM drivers ORDER BY strength DESC, id").fetchall(), user
    )
    news_rows = db.execute(
        "SELECT n.*, s.name AS source_name FROM news_items n "
        "JOIN sources s ON s.id = n.source_id ORDER BY n.published_at DESC LIMIT 6"
    ).fetchall()
    highlights = [
        {
            "id": row["id"],
            "title": row["title"],
            "source": {"id": row["source_id"], "name": row["source_name"]},
            "published_at": row["published_at"],
            "classification": row["classification"],
            "attribution": "source fact",
        }
        for row in visible_rows(news_rows, user)[:3]
    ]
    restricted_hidden = any(
        not can_read(row, user)
        for row in db.execute("SELECT classification FROM instruments").fetchall()
    )

    return {
        "as_of": max(latest_times) if latest_times else None,
        "freshness": "mixed" if len(statuses) > 1 else (next(iter(statuses)) if statuses else "unknown"),
        "tape": tape,
        "cards": cards,
        "drivers": [
            {
                "group": row["group_name"],
                "label": row["label"],
                "detail": row["detail"],
                "direction": row["direction"],
                "strength": row["strength"],
                "as_of": row["as_of"],
            }
            for row in drivers
        ],
        "highlights": highlights,
        "briefing": _latest_briefing(db, user),
        "restricted_hidden": restricted_hidden,
    }


def _latest_briefing(db, user):
    row = db.execute(
        "SELECT bv.*, b.title AS briefing_title FROM briefing_versions bv "
        "JOIN briefings b ON b.id = bv.briefing_id ORDER BY bv.generated_at DESC, bv.version DESC LIMIT 1"
    ).fetchone()
    if row is None or not can_read(row, user):
        return None
    if row["classification"] == "restricted":
        record_restricted_view(db, user, "briefing_version", row["id"])
    return {
        "briefing_id": row["briefing_id"],
        "title": row["briefing_title"],
        "version": row["version"],
        "generated_at": row["generated_at"],
        "data_cutoff": row["data_cutoff"],
        "headline": row["headline"],
        "moves": json.loads(row["moves"]),
        "drivers": json.loads(row["drivers"]),
        "watchlist": json.loads(row["watchlist"]),
        "classification": row["classification"],
    }


def list_instruments(db, user) -> list[dict]:
    instruments = visible_rows(
        db.execute("SELECT * FROM instruments ORDER BY display_order").fetchall(), user
    )
    for instrument in instruments:
        if instrument["classification"] == "restricted":
            record_restricted_view(db, user, "instrument", instrument["id"])
    result = []
    for instrument in instruments:
        latest = _latest(db, instrument["id"])
        payload = instrument_payload(instrument)
        payload["latest"] = None
        if latest is not None and can_read(latest, user):
            if latest["classification"] == "restricted":
                record_restricted_view(db, user, "market_observation", latest["id"])
            payload["latest"] = observation_payload(latest, latest["source_name"])
        result.append(payload)
    return result


def get_instrument(db, user, instrument_id: str) -> dict:
    instrument = _visible_instrument(db, user, instrument_id)
    latest = _latest(db, instrument["id"])
    payload = instrument_payload(instrument)
    readable_latest = latest is not None and can_read(latest, user)
    payload["latest"] = (
        observation_payload(latest, latest["source_name"]) if readable_latest else None
    )
    if instrument["classification"] == "restricted":
        record_restricted_view(db, user, "instrument", instrument["id"])
    elif readable_latest and latest["classification"] == "restricted":
        record_restricted_view(db, user, "market_observation", latest["id"])
    payload["formula"] = None
    if instrument["formula_id"]:
        formula = db.execute(
            "SELECT * FROM formulas WHERE id = ?", (instrument["formula_id"],)
        ).fetchone()
        if formula is not None:
            payload["formula"] = formula_payload(formula)
    return payload


def _series_points(db, user, instrument_id: str, days: int) -> dict:
    rows = db.execute(
        "SELECT market_time, value, classification FROM market_observations "
        "WHERE instrument_id = ? ORDER BY market_time",
        (instrument_id,),
    ).fetchall()
    rows = [row for row in rows if can_read(row, user)]
    if not rows:
        return {"points": [], "start": None}
    parsed = [(datetime.fromisoformat(row["market_time"]), row["value"]) for row in rows]
    anchor = max(moment for moment, _value in parsed)
    start = (anchor - timedelta(days=days - 1)).date()
    by_day = {moment.date(): value for moment, value in parsed if moment.date() >= start}
    points = []
    day = start
    while day <= anchor.date():
        points.append({"t": day.isoformat(), "v": by_day.get(day)})
        day += timedelta(days=1)
    return {"points": points, "start": start.isoformat()}


def series(db, user, instrument_id: str, range_key: str = "1M", compare_id: str | None = None) -> dict:
    if range_key not in RANGE_DAYS:
        raise ApiError(422, "invalid_range", "range must be 7D, 1M, 3M, 6M or 1Y.")
    instrument = _visible_instrument(db, user, instrument_id)
    if instrument["classification"] == "restricted":
        record_restricted_view(db, user, "instrument", instrument["id"])
    days = RANGE_DAYS[range_key]
    primary = _series_points(db, user, instrument["id"], days)
    result = {
        "range": range_key,
        "series": [
            {
                "instrument": instrument_payload(instrument),
                "unit": instrument["unit"],
                "points": primary["points"],
            }
        ],
        "events": [],
    }
    if compare_id:
        compare = _visible_instrument(db, user, compare_id)
        secondary = _series_points(db, user, compare["id"], days)
        result["series"].append(
            {
                "instrument": instrument_payload(compare),
                "unit": compare["unit"],
                "points": secondary["points"],
            }
        )
    if primary["start"]:
        events = db.execute(
            "SELECT e.*, s.name AS source_name FROM events e "
            "LEFT JOIN sources s ON s.id = e.source_id "
            "JOIN event_instruments ei ON ei.event_id = e.id "
            "WHERE ei.instrument_id = ? AND e.occurred_at >= ? ORDER BY e.occurred_at",
            (instrument["id"], primary["start"]),
        ).fetchall()
        result["events"] = [
            {
                "id": row["id"],
                "title": row["title"],
                "type": row["event_type"],
                "occurred_at": row["occurred_at"],
                "status": row["status"],
                "classification": row["classification"],
                "source": {"id": row["source_id"], "name": row["source_name"]},
                "instruments": [
                    link["instrument_id"]
                    for link in db.execute(
                        "SELECT instrument_id FROM event_instruments WHERE event_id = ? "
                        "ORDER BY instrument_id",
                        (row["id"],),
                    )
                ],
            }
            for row in visible_rows(events, user)
        ]
    return result


def list_observations(
    db,
    user,
    instrument_id: str | None = None,
    from_time: str | None = None,
    to_time: str | None = None,
    limit: int = 100,
) -> list[dict]:
    sql = (
        "SELECT o.*, s.name AS source_name FROM market_observations o "
        "JOIN sources s ON s.id = o.source_id WHERE 1 = 1"
    )
    params: list = []
    if instrument_id:
        sql += " AND o.instrument_id = ?"
        params.append(instrument_id)
    if from_time:
        sql += " AND o.market_time >= ?"
        params.append(_iso(_parse_time(from_time, "from")))
    if to_time:
        sql += " AND o.market_time <= ?"
        params.append(_iso(_parse_time(to_time, "to")))
    sql += " ORDER BY o.market_time DESC LIMIT ?"
    params.append(max(1, min(int(limit), 500)))
    rows = visible_rows(db.execute(sql, params).fetchall(), user)
    for row in rows:
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "market_observation", row["id"])
    return [observation_payload(row, row["source_name"]) for row in rows]


def list_formulas(db) -> list[dict]:
    rows = db.execute("SELECT * FROM formulas ORDER BY id").fetchall()
    return [formula_payload(row) for row in rows]


def create_observation(db, user, payload: dict) -> dict:
    instrument_id = payload.get("instrument_id")
    instrument = db.execute("SELECT * FROM instruments WHERE id = ?", (instrument_id,)).fetchone()
    if instrument is None or not can_read(instrument, user):
        raise ApiError(404, "not_found", "Instrument not found.")

    value = payload.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ApiError(422, "invalid_value", "value must be a finite number.")
    unit = payload.get("unit") or instrument["unit"]
    if unit != instrument["unit"]:
        raise ApiError(422, "invalid_unit", "unit does not match the instrument.")
    market_time = _parse_time(payload.get("market_time"))
    if market_time > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ApiError(422, "future_market_time", "market_time cannot be in the future.")

    source_id = payload.get("source_id")
    source = db.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
    if source is None:
        raise ApiError(422, "invalid_source", "source_id does not exist.")

    data_status = str(payload.get("data_status") or "").lower()
    if data_status not in DATA_STATUSES:
        raise ApiError(422, "invalid_data_status", "Unknown data_status.")
    quality_status = str(payload.get("quality_status") or "").lower()
    if quality_status not in QUALITY_STATUSES:
        raise ApiError(422, "invalid_quality_status", "Unknown quality_status.")
    classification = str(payload.get("classification") or "").lower()
    if classification not in CLASSIFICATIONS:
        raise ApiError(422, "invalid_classification", "Unknown classification.")
    if rank(classification) > rank(user["max_classification"]):
        raise ApiError(422, "classification_above_user", "Classification exceeds your access.")
    if rank(classification) < rank(instrument["classification"]):
        raise ApiError(
            422,
            "classification_below_instrument",
            "Classification cannot be lower than the instrument's own classification.",
        )

    try:
        cursor = db.execute(
            "INSERT INTO market_observations (instrument_id, source_id, value, unit, market_time, "
            "ingested_at, data_status, quality_status, classification, created_by) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                instrument["id"],
                source["id"],
                float(value),
                unit,
                _iso(market_time),
                utc_now(),
                data_status,
                quality_status,
                classification,
                user["id"],
            ),
        )
        db.commit()
    except Exception as error:  # UNIQUE (instrument, source, market_time)
        db.rollback()
        if "UNIQUE" in str(error):
            raise ApiError(409, "duplicate_observation", "This observation already exists.")
        raise

    record(
        db,
        action="manual_observation",
        result="succeeded",
        actor=user,
        object_type="market_observation",
        object_id=str(cursor.lastrowid),
        classification=classification,
    )
    row = db.execute(
        "SELECT o.*, s.name AS source_name FROM market_observations o "
        "JOIN sources s ON s.id = o.source_id WHERE o.id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    return observation_payload(row, row["source_name"])


def compute_crack(db, user, formula_id: str, as_of: str) -> dict:
    """Deterministic crack computation without writing a row.

    The assistant and analysis workspace use this so a labelled formula number
    always comes from the same versioned rule as the stored calculation.
    """
    formula = db.execute("SELECT * FROM formulas WHERE id = ?", (formula_id,)).fetchone()
    if formula is None:
        raise ApiError(404, "not_found", "Formula not found.")
    as_of_time = _parse_time(as_of, "as_of")
    as_of_iso = _iso(as_of_time)

    input_ids = json.loads(formula["input_instruments"])
    inputs = []
    for input_id in input_ids:
        instrument = db.execute("SELECT * FROM instruments WHERE id = ?", (input_id,)).fetchone()
        if instrument is None or not can_read(instrument, user):
            raise ApiError(404, "not_found", "A formula input is not available to you.")
        observation = db.execute(
            "SELECT * FROM market_observations WHERE instrument_id = ? AND market_time <= ? "
            "ORDER BY market_time DESC LIMIT 1",
            (input_id, as_of_iso),
        ).fetchone()
        if observation is None or not can_read(observation, user):
            raise ApiError(422, "missing_input", "A formula input has no observation at this time.")
        if observation["classification"] == "restricted":
            record_restricted_view(db, user, "market_observation", observation["id"])
        inputs.append((instrument, observation))

    price_types = {instrument["price_type"] for instrument, _observation in inputs}
    if not formula["allow_mixed_price_types"] and len(price_types) > 1:
        raise ApiError(
            422,
            "mixed_price_types",
            "This formula does not allow mixing price types.",
        )

    values = [observation["value"] for _instrument, observation in inputs]
    if len(values) == 2:
        value = values[0] - values[1]
    elif len(values) == 3:
        value = (2 * values[0] + values[1] - 3 * values[2]) / 3
    else:
        raise ApiError(422, "unsupported_formula", "Only two- and three-input formulas are supported.")
    value = round(value, 6)

    target = db.execute(
        "SELECT * FROM instruments WHERE formula_id = ? ORDER BY display_order LIMIT 1",
        (formula_id,),
    ).fetchone()
    if target is None:
        raise ApiError(422, "no_calculated_instrument", "No calculated instrument uses this formula.")

    return {
        "formula": formula,
        "target": target,
        "value": value,
        "unit": formula["unit"],
        "as_of_iso": as_of_iso,
        "inputs": [observation["id"] for _instrument, observation in inputs],
        "derived_classification": max(
            (observation["classification"] for _instrument, observation in inputs), key=rank
        ),
    }


def calculate_crack(db, user, formula_id: str, as_of: str) -> dict:
    computed = compute_crack(db, user, formula_id, as_of)
    formula = computed["formula"]
    target = computed["target"]
    as_of_iso = computed["as_of_iso"]
    calculation_inputs = json.dumps(computed["inputs"])
    derived_classification = computed["derived_classification"]

    existing = db.execute(
        "SELECT * FROM market_observations WHERE instrument_id = ? AND source_id = 'SRC-BSR-AN' "
        "AND market_time = ?",
        (target["id"], as_of_iso),
    ).fetchone()
    if existing is not None:
        if existing["formula_id"] == formula_id and existing["calculation_inputs"] == calculation_inputs:
            return _calculation_payload(db, existing, formula)
        raise ApiError(
            409,
            "calculation_exists",
            "A different calculation already exists for this timestamp.",
        )

    try:
        cursor = db.execute(
            "INSERT INTO market_observations (instrument_id, source_id, value, unit, market_time, "
            "ingested_at, data_status, quality_status, classification, formula_id, calculation_inputs, "
            "calculated_at, created_by) VALUES (?, 'SRC-BSR-AN', ?, ?, ?, ?, 'eod', 'valid', ?, ?, ?, ?, ?)",
            (
                target["id"],
                computed["value"],
                computed["unit"],
                as_of_iso,
                utc_now(),
                derived_classification,
                formula_id,
                calculation_inputs,
                utc_now(),
                user["id"],
            ),
        )
        db.commit()
    except Exception as error:  # concurrent duplicate on the UNIQUE constraint
        db.rollback()
        if "UNIQUE" not in str(error):
            raise
        existing = db.execute(
            "SELECT * FROM market_observations WHERE instrument_id = ? AND source_id = 'SRC-BSR-AN' "
            "AND market_time = ?",
            (target["id"], as_of_iso),
        ).fetchone()
        if (
            existing is not None
            and existing["formula_id"] == formula_id
            and existing["calculation_inputs"] == calculation_inputs
        ):
            return _calculation_payload(db, existing, formula)
        raise ApiError(
            409,
            "calculation_exists",
            "A different calculation already exists for this timestamp.",
        )

    record(
        db,
        action="calculation",
        result="succeeded",
        actor=user,
        object_type="formula",
        object_id=formula_id,
        classification=derived_classification,
        detail=json.dumps({"observation_id": cursor.lastrowid, "value": computed["value"]}),
    )
    row = db.execute("SELECT * FROM market_observations WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _calculation_payload(db, row, formula)


def _calculation_payload(db, row, formula) -> dict:
    source = db.execute("SELECT name FROM sources WHERE id = ?", (row["source_id"],)).fetchone()
    return {
        "observation_id": row["id"],
        "value": row["value"],
        "unit": row["unit"],
        "market_time": row["market_time"],
        "classification": row["classification"],
        "calculated_at": row["calculated_at"],
        "inputs": json.loads(row["calculation_inputs"] or "[]"),
        "formula": formula_payload(formula),
        "source": {"id": row["source_id"], "name": source["name"] if source else row["source_id"]},
    }
