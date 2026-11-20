"""Forecast register: current versions, immutable history, deterministic evaluation."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from ..db import utc_now
from ..errors import ApiError
from ..permissions import can_read, visible_rows
from . import analytics
from .audit import record, record_restricted_view

HORIZONS = ("1-month", "3-month", "6-month", "12-month")


def _parse_time(value, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ApiError(422, "invalid_time", f"{field} must be an ISO 8601 timestamp.")
    if parsed.tzinfo is None:
        raise ApiError(422, "invalid_time", f"{field} must include a UTC offset.")
    return parsed


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def _latest_version(db, forecast_id: str):
    return db.execute(
        "SELECT * FROM forecast_versions WHERE forecast_id = ? ORDER BY version DESC LIMIT 1",
        (forecast_id,),
    ).fetchone()


def _evaluation_row(db, version_id: int):
    return db.execute(
        "SELECT * FROM forecast_evaluations WHERE forecast_version_id = ?", (version_id,)
    ).fetchone()


def _actual_value(db, user, evaluation) -> float | None:
    if evaluation is None or evaluation["actual_observation_id"] is None:
        return None
    observation = db.execute(
        "SELECT value, classification FROM market_observations WHERE id = ?",
        (evaluation["actual_observation_id"],),
    ).fetchone()
    if observation is None or not can_read(observation, user):
        return None
    return observation["value"]


def _forecast_payload(db, row, user) -> dict:
    version = _latest_version(db, row["id"])
    evaluation = _evaluation_row(db, version["id"]) if version is not None else None
    actual = _actual_value(db, user, evaluation)
    source = db.execute("SELECT name FROM sources WHERE id = ?", (row["source_id"],)).fetchone()
    instrument = db.execute(
        "SELECT name, unit FROM instruments WHERE id = ?", (row["instrument_id"],)
    ).fetchone()
    error = (
        analytics.forecast_error(version["value"], actual)
        if version is not None and actual is not None
        else {"absolute_error": None, "percentage_error": None, "note": "actual missing"}
    )
    return {
        "id": row["id"],
        "instrument": {
            "id": row["instrument_id"],
            "name": instrument["name"] if instrument else row["instrument_id"],
            "unit": instrument["unit"] if instrument else None,
        },
        "source": {"id": row["source_id"], "name": source["name"] if source else row["source_id"]},
        "horizon": row["horizon"],
        "period": row["period"],
        "classification": row["classification"],
        "version": version["version"] if version is not None else None,
        "value": version["value"] if version is not None else None,
        "methodology": version["methodology"] if version is not None else None,
        "published_at": version["published_at"] if version is not None else None,
        "ingested_at": version["ingested_at"] if version is not None else None,
        "actual": actual,
        "absolute_error": error["absolute_error"],
        "percentage_error": error["percentage_error"],
        "note": error["note"],
    }


def list_forecasts(
    db,
    user,
    instrument: str | None = None,
    source: str | None = None,
    horizon: str | None = None,
) -> list[dict]:
    sql = "SELECT * FROM forecasts WHERE 1 = 1"
    params: list = []
    if instrument:
        sql += " AND instrument_id = ?"
        params.append(instrument)
    if source:
        sql += " AND source_id = ?"
        params.append(source)
    if horizon:
        sql += " AND horizon = ?"
        params.append(horizon)
    sql += " ORDER BY id"
    rows = visible_rows(db.execute(sql, params).fetchall(), user)
    for row in rows:
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "forecast", row["id"])
    return [_forecast_payload(db, row, user) for row in rows]


def get_versions(db, user, forecast_id: str) -> list[dict]:
    forecast = db.execute("SELECT * FROM forecasts WHERE id = ?", (forecast_id,)).fetchone()
    if forecast is None or not can_read(forecast, user):
        raise ApiError(404, "not_found", "Forecast not found.")
    if forecast["classification"] == "restricted":
        record_restricted_view(db, user, "forecast", forecast_id)
    rows = db.execute(
        "SELECT * FROM forecast_versions WHERE forecast_id = ? ORDER BY version DESC",
        (forecast_id,),
    ).fetchall()
    result = []
    for row in rows:
        evaluation = _evaluation_row(db, row["id"])
        actual = _actual_value(db, user, evaluation)
        error = analytics.forecast_error(row["value"], actual)
        result.append(
            {
                "version": row["version"],
                "value": row["value"],
                "methodology": row["methodology"],
                "published_at": row["published_at"],
                "ingested_at": row["ingested_at"],
                "actual": actual,
                "absolute_error": error["absolute_error"],
                "percentage_error": error["percentage_error"],
                "note": error["note"],
            }
        )
    return result


def add_version(db, user, forecast_id: str, payload: dict) -> dict:
    forecast = db.execute("SELECT * FROM forecasts WHERE id = ?", (forecast_id,)).fetchone()
    if forecast is None or not can_read(forecast, user):
        raise ApiError(404, "not_found", "Forecast not found.")
    value = payload.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ApiError(422, "invalid_value", "value must be a finite number.")
    methodology = str(payload.get("methodology") or "").strip()
    if not methodology:
        raise ApiError(422, "validation_error", "methodology is required.")
    published_at = _parse_time(payload.get("published_at"), "published_at")
    if published_at > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ApiError(422, "future_publish_time", "published_at cannot be in the future.")

    latest = _latest_version(db, forecast_id)
    next_version = (latest["version"] + 1) if latest is not None else 1
    db.execute(
        "INSERT INTO forecast_versions (forecast_id, version, value, methodology, "
        "published_at, ingested_at, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            forecast_id,
            next_version,
            float(value),
            methodology,
            _iso(published_at),
            utc_now(),
            user["id"],
        ),
    )
    db.commit()
    record(
        db,
        action="forecast_version",
        result="succeeded",
        actor=user,
        object_type="forecast",
        object_id=forecast_id,
        classification=forecast["classification"],
        detail=f"version {next_version}",
    )
    return _forecast_payload(db, forecast, user)


def evaluation(
    db,
    user,
    instrument: str | None = None,
    horizon: str | None = None,
) -> dict:
    items = list_forecasts(db, user, instrument=instrument, horizon=horizon)
    groups: dict[tuple[str, str], list[tuple[float, float | None]]] = defaultdict(list)
    for item in items:
        groups[(item["source"]["name"], item["horizon"])].append((item["value"], item["actual"]))
    aggregates = []
    for (source_name, group_horizon), pairs in sorted(groups.items()):
        usable = [pair for pair in pairs if pair[1] is not None]
        aggregates.append(
            {
                "source": source_name,
                "horizon": group_horizon,
                "count": len(usable),
                "missing": len(pairs) - len(usable),
                "mae": analytics.mae(pairs),
                "mape": analytics.mape(pairs),
                "bias": analytics.bias(pairs),
            }
        )
    return {"items": items, "aggregates": aggregates}
