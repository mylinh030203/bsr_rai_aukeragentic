"""Briefing versions: generated from permitted sources, immutable once stored."""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from ..db import utc_now
from ..errors import ApiError
from ..permissions import can_read, rank, visible_rows
from . import ai_runs, analytics
from .audit import record, record_restricted_view

BRIEFING_ID = "B-1"
BRIEFING_TITLE = "Morning market briefing"


def _sources(db, version_id: int) -> list[dict]:
    return [
        {
            "kind": row["source_kind"],
            "id": row["source_id"],
            "label": row["label"],
        }
        for row in db.execute(
            "SELECT * FROM briefing_sources WHERE briefing_version_id = ? ORDER BY position",
            (version_id,),
        )
    ]


def _payload(db, row) -> dict:
    return {
        "briefing_id": row["briefing_id"],
        "title": row["title"],
        "version": row["version"],
        "generated_at": row["generated_at"],
        "data_cutoff": row["data_cutoff"],
        "headline": row["headline"],
        "moves": json.loads(row["moves"]),
        "drivers": json.loads(row["drivers"]),
        "watchlist": json.loads(row["watchlist"]),
        "classification": row["classification"],
        "sources": _sources(db, row["id"]),
    }


def list_briefings(db, user) -> list[dict]:
    rows = db.execute(
        "SELECT bv.*, b.title FROM briefing_versions bv "
        "JOIN briefings b ON b.id = bv.briefing_id "
        "ORDER BY bv.generated_at DESC, bv.version DESC"
    ).fetchall()
    visible = visible_rows(rows, user)
    for row in visible:
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "briefing_version", row["id"])
    return [_payload(db, row) for row in visible]


def _latest_observation(db, user, instrument_id: str):
    row = db.execute(
        "SELECT * FROM market_observations WHERE instrument_id = ? "
        "ORDER BY market_time DESC LIMIT 1",
        (instrument_id,),
    ).fetchone()
    if row is None or not can_read(row, user):
        return None
    return row


def generate(db, user) -> dict:
    moves = []
    cited = []
    for instrument_id, label in (
        ("brent_futures", "Brent"),
        ("wti_futures", "WTI"),
        ("crack_gasoline", "Gasoline crack"),
    ):
        latest = _latest_observation(db, user, instrument_id)
        if latest is None:
            continue
        previous = db.execute(
            "SELECT value, classification FROM market_observations "
            "WHERE instrument_id = ? AND market_time <= ? ORDER BY market_time DESC LIMIT 1",
            (
                instrument_id,
                (
                    datetime.fromisoformat(latest["market_time"]) - timedelta(days=1)
                ).isoformat(timespec="seconds"),
            ),
        ).fetchone()
        change = None
        change_pct = None
        if previous is not None and can_read(previous, user):
            change = analytics.absolute_change(previous["value"], latest["value"])
            change_pct = analytics.percentage_change(previous["value"], latest["value"])
        moves.append(
            {
                "instrument": label,
                "value": latest["value"],
                "unit": latest["unit"],
                "market_time": latest["market_time"],
                "change": change,
                "pct": change_pct,
            }
        )
        cited.append(latest)

    drivers = [
        row["label"]
        for row in visible_rows(
            db.execute("SELECT * FROM drivers ORDER BY strength DESC LIMIT 3").fetchall(), user
        )
    ]
    news_rows = visible_rows(
        db.execute("SELECT * FROM news_items ORDER BY published_at DESC LIMIT 3").fetchall(), user
    )
    watchlist = [row["title"] for row in news_rows]
    context = {
        "moves": moves,
        "drivers": drivers,
        "watchlist": watchlist,
        "headline": "Supply risk meets product strength",
    }
    execution = ai_runs.execute(
        db,
        task_type="market_briefing",
        user=user,
        task_input={"briefing_id": BRIEFING_ID},
        context=context,
    )
    output = execution["output"]
    if execution["status"] != "succeeded":
        output = {
            "headline": "Briefing unavailable; source facts are unchanged.",
            "moves": moves,
            "drivers": drivers,
            "watchlist": watchlist,
        }

    classifications = [row["classification"] for row in cited] + [
        row["classification"] for row in news_rows
    ]
    classification = max(classifications, key=rank) if classifications else "internal"

    briefing = db.execute("SELECT * FROM briefings WHERE id = ?", (BRIEFING_ID,)).fetchone()
    if briefing is None:
        db.execute(
            "INSERT INTO briefings (id, title, created_at, classification) VALUES (?, ?, ?, ?)",
            (BRIEFING_ID, BRIEFING_TITLE, utc_now(), classification),
        )
    else:
        # The parent stays at the highest classification ever generated; each
        # version also stores its own classification for per-version filtering.
        parent_classification = max(briefing["classification"], classification, key=rank)
        db.execute(
            "UPDATE briefings SET classification = ? WHERE id = ?",
            (parent_classification, BRIEFING_ID),
        )
    latest = db.execute(
        "SELECT MAX(version) AS version FROM briefing_versions WHERE briefing_id = ?",
        (BRIEFING_ID,),
    ).fetchone()
    next_version = (latest["version"] or 0) + 1
    cursor = db.execute(
        "INSERT INTO briefing_versions (briefing_id, version, generated_at, data_cutoff, headline, "
        "moves, drivers, watchlist, ai_execution_id, classification) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            BRIEFING_ID,
            next_version,
            utc_now(),
            utc_now(),
            output.get("headline") or "Market update",
            json.dumps(output.get("moves") or moves),
            json.dumps(output.get("drivers") or drivers),
            json.dumps(output.get("watchlist") or watchlist),
            execution["execution_id"],
            classification,
        ),
    )
    version_id = cursor.lastrowid
    position = 0
    for observation in cited:
        db.execute(
            "INSERT INTO briefing_sources (briefing_version_id, source_kind, source_id, label, position) "
            "VALUES (?, 'observation', ?, ?, ?)",
            (version_id, observation["source_id"], observation["source_id"], position),
        )
        position += 1
    for news in news_rows:
        db.execute(
            "INSERT INTO briefing_sources (briefing_version_id, source_kind, source_id, label, position) "
            "VALUES (?, 'news', ?, ?, ?)",
            (version_id, news["id"], news["title"], position),
        )
        position += 1
    db.commit()
    record(
        db,
        action="briefing_generated",
        result=execution["status"],
        actor=user,
        object_type="briefing",
        object_id=BRIEFING_ID,
        classification=classification,
        detail=f"version {next_version}",
    )
    row = db.execute(
        "SELECT bv.*, b.title FROM briefing_versions bv "
        "JOIN briefings b ON b.id = bv.briefing_id WHERE bv.id = ?",
        (version_id,),
    ).fetchone()
    return _payload(db, row)
