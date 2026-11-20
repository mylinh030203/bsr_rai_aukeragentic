"""Idempotent synthetic demo data, mirroring docs/design/prototype/assets/data.js."""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone

DEMO_NOW = datetime(2026, 11, 14, 9, 42, tzinfo=timezone(timedelta(hours=7)))
DEMO_TZ = timezone(timedelta(hours=7))
DAY = timedelta(days=1)

USERS = [
    ("u-lead", "Lê Minh Anh", "leadership", "Executive Office", "restricted", 1, 0, 0),
    ("u-mi", "Nguyễn Thu Hà", "mi", "Market Intelligence", "restricted", 1, 1, 1),
    ("u-int", "Trần Quốc Bảo", "internal", "Commercial", "internal", 0, 0, 0),
]

SOURCES = [
    ("SRC-ICE", "ICE (demo)", "market", "internal", "Synthetic ICE assessment."),
    ("SRC-CME", "CME (demo)", "market", "internal", "Synthetic CME assessment."),
    ("SRC-PLATTS", "Platts (demo)", "market", "internal", "Synthetic Platts assessment."),
    ("SRC-SBV", "SBV (demo)", "market", "internal", "Synthetic reference rate."),
    ("SRC-BSR-AN", "BSR Analytical", "analytical", "internal", "BSR deterministic analytics."),
    ("SRC-BSR-IN", "BSR Internal", "internal", "confidential", "Internal operations data."),
    ("SRC-REUTERS", "Reuters (demo)", "news", "internal", "Synthetic news feed."),
    ("SRC-EIA", "EIA (demo)", "news", "public", "Synthetic public statistics."),
    ("SRC-IEA", "IEA (demo)", "news", "internal", "Synthetic agency outlook."),
    ("SRC-BLOOMBERG", "Bloomberg (demo)", "news", "internal", "Synthetic news feed."),
]

FORMULAS = [
    (
        "CS-GAS-2.1",
        "Gasoline crack versus Brent",
        "2.1",
        "RON95 physical - Brent futures, converted to USD/bbl",
        json.dumps(["ron95", "brent_futures"]),
        1,
        "USD/bbl",
    ),
    (
        "CS-DSL-2.0",
        "Diesel crack versus Brent",
        "2.0",
        "Diesel physical - Brent futures, converted to USD/bbl",
        json.dumps(["diesel", "brent_futures"]),
        1,
        "USD/bbl",
    ),
    (
        "CS-321-1.3",
        "3-2-1 composite crack",
        "1.3",
        "(2 x gasoline + 1 x diesel - 3 x Brent) / 3",
        json.dumps(["ron95", "diesel", "brent_futures"]),
        1,
        "USD/bbl",
    ),
    (
        "CS-STRICT-1.0",
        "Strict product crack (no price-type mixing)",
        "1.0",
        "Product assessment - Brent futures; rejects mixed price types by configuration",
        json.dumps(["ron95", "brent_futures"]),
        0,
        "USD/bbl",
    ),
]

# id, name, short, ticker, group, unit, price_type, decimals, classification,
# value, drift, vol, seed, source_id, data_status, quality, formula_id
INSTRUMENTS = [
    ("brent_futures", "Brent Crude Futures", "Brent", "BRN", "Crude oil", "USD/bbl", "futures", 2, "internal",
     78.42, 0.02, 1.8, 3, "SRC-ICE", "real-time", "valid", None),
    ("wti_futures", "WTI Crude Futures", "WTI", "CL", "Crude oil", "USD/bbl", "futures", 2, "internal",
     74.18, 0.015, 1.4, 7, "SRC-CME", "real-time", "valid", None),
    ("brent_physical", "Brent Physical Dated", "Brent Dated", "BRD", "Crude oil", "USD/bbl", "physical", 2, "restricted",
     77.9, 0.018, 1.6, 11, "SRC-PLATTS", "eod", "valid", None),
    ("ron95", "Gasoline RON95 (FOB Singapore)", "RON95", "RON95", "Refined products", "USD/bbl", "physical", 2, "internal",
     92.1, -0.01, 2.0, 15, "SRC-PLATTS", "eod", "valid", None),
    ("diesel", "Diesel 10ppm (FOB Singapore)", "Diesel", "DIESEL", "Refined products", "USD/bbl", "physical", 2, "internal",
     96.4, 0.01, 1.8, 19, "SRC-PLATTS", "eod", "valid", None),
    ("jet", "Jet Fuel A-1 (FOB Singapore)", "Jet A-1", "JET", "Refined products", "USD/bbl", "physical", 2, "internal",
     99.2, 0.012, 2.0, 23, "SRC-PLATTS", "eod", "valid", None),
    ("fuel_oil", "Fuel Oil 180 CST (FOB Singapore)", "Fuel oil", "FO180", "Refined products", "USD/bbl", "physical", 2, "internal",
     68.3, -0.005, 1.2, 27, "SRC-PLATTS", "eod", "pending", None),
    ("usd_vnd", "USD/VND", "USD/VND", "USDVND", "FX & macro", "VND", "index", 0, "internal",
     25480, 0.004, 90, 31, "SRC-SBV", "delayed", "valid", None),
    ("dxy", "US Dollar Index", "DXY", "DXY", "FX & macro", "index", "index", 2, "internal",
     104.12, -0.002, 0.55, 35, "SRC-ICE", "delayed", "valid", None),
    ("crack_gasoline", "Gasoline Crack Spread", "Gasoline crack", "CS-GAS", "Crack spreads", "USD/bbl", "calculated", 2, "internal",
     18.35, 0.03, 1.0, 39, "SRC-BSR-AN", "eod", "valid", "CS-GAS-2.1"),
    ("crack_diesel", "Diesel Crack Spread", "Diesel crack", "CS-DSL", "Crack spreads", "USD/bbl", "calculated", 2, "internal",
     21.1, 0.015, 0.9, 43, "SRC-BSR-AN", "eod", "valid", "CS-DSL-2.0"),
    ("crack_321", "3-2-1 Composite Crack", "3-2-1 crack", "CS-321", "Crack spreads", "USD/bbl", "calculated", 2, "internal",
     19.4, 0.02, 0.9, 47, "SRC-BSR-AN", "eod", "valid", "CS-321-1.3"),
    ("bsr_margin", "BSR Indicative Refining Margin", "BSR margin", "BSR-M", "Refinery operations", "USD/bbl", "calculated", 2, "confidential",
     8.24, 0.02, 0.55, 51, "SRC-BSR-IN", "manual", "valid", None),
]

TOPICS = {
    "OPEC+": "t-opec",
    "Crude supply": "t-crude-supply",
    "Shipping & freight": "t-freight",
    "Refined products": "t-products",
    "Inventory": "t-inventory",
    "Crude demand": "t-crude-demand",
    "Asia demand": "t-asia-demand",
    "Refining operations": "t-refining",
    "Geopolitics": "t-geopolitics",
    "Cross-market": "t-cross-market",
}

NEWS = [
    {
        "id": "N-2411",
        "title": "OPEC+ signals patience on output as Brent tests $78",
        "source_id": "SRC-REUTERS",
        "published_at": "2026-11-14T07:50:00+07:00",
        "ingested_at": "2026-11-14T08:02:00+07:00",
        "classification": "internal",
        "status": "processed",
        "relevance": 94,
        "summary": "Delegates indicated the group is unlikely to accelerate unwinding voluntary cuts before the next ministerial meeting, keeping near-term supply expectations tight.",
        "body": "Sourced reporting placeholder for the demo. The original article remains accessible from the licensed provider in production.",
        "insight": "AI interpretation: the signal supports the front of the Brent curve, but the market reaction is modest because the decision was partly expected.",
        "topics": ["OPEC+", "Crude supply"],
        "instruments": ["brent_futures", "wti_futures"],
        "duplicate_of": None,
        "coverage_note": "3 sources - 2 unique details",
    },
    {
        "id": "N-2410",
        "title": "Red Sea diversions add a week to Gulf-Asia product voyages",
        "source_id": "SRC-PLATTS",
        "published_at": "2026-11-14T06:40:00+07:00",
        "ingested_at": "2026-11-14T06:58:00+07:00",
        "classification": "internal",
        "status": "processed",
        "relevance": 88,
        "summary": "Freight assessments for Gulf-Asia routes rose again as operators extended diversions, tightening effective product availability in the east.",
        "body": "Sourced reporting placeholder for the demo.",
        "insight": "AI interpretation: the freight move is more material for product arb economics than for absolute crude direction.",
        "topics": ["Shipping & freight", "Refined products"],
        "instruments": ["diesel", "jet"],
        "duplicate_of": None,
        "coverage_note": "4 sources - 3 unique details",
    },
    {
        "id": "N-2409",
        "title": "US crude inventories fall more than expected: EIA",
        "source_id": "SRC-EIA",
        "published_at": "2026-11-13T22:30:00+07:00",
        "ingested_at": "2026-11-13T22:41:00+07:00",
        "classification": "public",
        "status": "processed",
        "relevance": 76,
        "summary": "Commercial crude stocks declined while gasoline inventories built modestly, a mixed signal for the crude-product complex.",
        "body": "Sourced reporting placeholder for the demo.",
        "insight": "AI interpretation: crude draws support flat price, but the product build limits the read-through to cracks.",
        "topics": ["Inventory", "Crude demand"],
        "instruments": ["wti_futures", "crack_gasoline"],
        "duplicate_of": None,
        "coverage_note": "2 sources - 1 unique detail",
    },
    {
        "id": "N-2408",
        "title": "Dung Quat begins planned maintenance on CDU",
        "source_id": "SRC-BSR-IN",
        "published_at": "2026-11-13T16:20:00+07:00",
        "ingested_at": "2026-11-13T16:25:00+07:00",
        "classification": "confidential",
        "status": "processed",
        "relevance": 91,
        "summary": "A planned crude distillation unit maintenance window begins, with product output and crude intake adjusted according to the internal plan.",
        "body": "Internal operations note (demo placeholder).",
        "insight": "AI interpretation: the maintenance window is already reflected in the internal plan; monitor product cracks for unintended tightening.",
        "topics": ["Refining operations"],
        "instruments": ["bsr_margin", "crack_gasoline"],
        "duplicate_of": None,
        "coverage_note": "1 source - 2 unique details",
    },
    {
        "id": "N-2407",
        "title": "OPEC+ keeps output path steady, delegates say",
        "source_id": "SRC-BLOOMBERG",
        "published_at": "2026-11-14T07:58:00+07:00",
        "ingested_at": "2026-11-14T08:06:00+07:00",
        "classification": "internal",
        "status": "duplicate_candidate",
        "relevance": 93,
        "summary": "A near-identical account of the OPEC+ signal, adding one detail on the next ministerial date.",
        "body": "Sourced reporting placeholder for the demo.",
        "insight": "AI interpretation: duplicate candidate linked to N-2411. Adds the ministerial date, so the source is retained and linked, not removed.",
        "topics": ["OPEC+", "Crude supply"],
        "instruments": ["brent_futures"],
        "duplicate_of": "N-2411",
        "coverage_note": "Linked to N-2411 - 1 additive detail",
    },
    {
        "id": "N-2406",
        "title": "Asian refiners trim spot crude purchases for December",
        "source_id": "SRC-REUTERS",
        "published_at": "2026-11-13T14:10:00+07:00",
        "ingested_at": "2026-11-13T14:23:00+07:00",
        "classification": "internal",
        "status": "processed",
        "relevance": 72,
        "summary": "Several regional refiners reduced December spot requirements, pointing to softer near-term crude demand in Asia.",
        "body": "Sourced reporting placeholder for the demo.",
        "insight": "AI interpretation: a demand-side offset to the supply narrative; keep it in the watch list rather than the base case.",
        "topics": ["Crude demand", "Asia demand"],
        "instruments": ["brent_futures", "diesel"],
        "duplicate_of": None,
        "coverage_note": "2 sources - 1 unique detail",
    },
    {
        "id": "N-2405",
        "title": "Platts physical Brent assessment: dated cargoes firm",
        "source_id": "SRC-PLATTS",
        "published_at": "2026-11-13T18:30:00+07:00",
        "ingested_at": "2026-11-14T07:05:00+07:00",
        "classification": "restricted",
        "status": "processed",
        "relevance": 85,
        "summary": "Restricted physical assessment detail. Visible only to roles with Restricted access.",
        "body": "Licensed physical assessment placeholder.",
        "insight": "AI interpretation is withheld from unauthorized roles at retrieval time.",
        "topics": ["Crude supply", "Refining operations"],
        "instruments": ["brent_physical"],
        "duplicate_of": None,
        "coverage_note": "Restricted source",
    },
]

EVENTS = [
    ("E-1", "OPEC+ agrees November output path", "Policy", "2026-10-06", "SRC-REUTERS",
     ["brent_futures", "wti_futures"], ["N-2411"], "internal"),
    ("E-2", "Red Sea freight disruption widens", "Logistics", "2026-10-19", "SRC-PLATTS",
     ["brent_futures", "diesel"], ["N-2410"], "internal"),
    ("E-3", "Dung Quat unit maintenance begins", "Refining", "2026-11-03", "SRC-BSR-IN",
     ["crack_gasoline", "bsr_margin"], ["N-2408"], "confidential"),
    ("E-4", "US crude inventories fall more than expected", "Inventory", "2026-11-11", "SRC-EIA",
     ["wti_futures", "brent_futures"], ["N-2409"], "public"),
]

DRIVERS = [
    ("supply", "OPEC+ discipline", "Voluntary cuts extended through Q4; compliance signal firming.", "tightening", 82),
    ("supply", "Middle East risk", "Shipping insurance costs elevated along the Gulf routes.", "tightening", 68),
    ("demand", "Asia gasoline demand", "Regional cracks supported by resilient mobility demand.", "firming", 61),
    ("demand", "Industrial diesel demand", "Soft manufacturing prints cap upside in middle distillates.", "softening", 47),
    ("logistics", "Freight & insurance", "Red Sea diversions keep product arb windows uneven.", "tightening", 57),
    ("macro", "USD / VND", "Stable reference rate reduces imported-cost volatility.", "neutral", 36),
]

FORECASTS = [
    ("F-101", "EIA (demo)", "SRC-EIA", "brent_futures", 79.5, "Q1 2027", "3-month", "STEO baseline", 3, "internal", 78.42, 80.2, "2026-11-12"),
    ("F-102", "IEA (demo)", "SRC-IEA", "brent_futures", 77.8, "Q1 2027", "3-month", "Balances + inventory model", 2, "internal", None, 78.4, "2026-11-10"),
    ("F-103", "Platts (demo)", "SRC-PLATTS", "ron95", 93.4, "Dec 2026", "1-month", "Analytics spot outlook", 4, "internal", 92.1, 92.9, "2026-11-13"),
    ("F-104", "BSR Internal", "SRC-BSR-IN", "crack_gasoline", 17.9, "Dec 2026", "1-month", "Demo internal scenario", 1, "confidential", 18.35, None, "2026-11-11"),
    ("F-105", "IEA (demo)", "SRC-IEA", "wti_futures", 72.6, "Q1 2027", "3-month", "Balances + inventory model", 2, "internal", 74.18, 73.9, "2026-11-10"),
    ("F-106", "EIA (demo)", "SRC-EIA", "wti_futures", 74.1, "Q1 2027", "3-month", "STEO baseline", 3, "internal", None, 75.0, "2026-11-12"),
]

REPORTS = [
    ("R-2026-041", "Morning Briefing", "Morning briefing - supply risk meets product strength",
     "2026-11-13", "2026-11-14", "internal", 2, "2026-11-14T09:20:00+07:00", "2026-11-14T09:15:00+07:00",
     ["SRC-ICE", "SRC-PLATTS", "SRC-REUTERS", "SRC-EIA"]),
    ("R-2026-040", "Weekly Market Report", "Week 46 - cracks carry the narrative",
     "2026-11-09", "2026-11-15", "internal", 1, "2026-11-13T17:40:00+07:00", "2026-11-13T17:30:00+07:00",
     ["SRC-ICE", "SRC-CME", "SRC-PLATTS"]),
    ("R-2026-039", "Event-driven Analysis", "Hormuz disruption - exposure and watch list",
     "2026-11-01", "2026-11-12", "confidential", 1, "2026-11-12T15:10:00+07:00", "2026-11-12T15:00:00+07:00",
     ["SRC-ICE", "SRC-PLATTS", "SRC-BSR-AN"]),
]

NOTIFICATIONS = [
    (None, "Morning briefing published", "Version 3 of the morning briefing is available.", "#overview", "2026-11-14T09:20:00+07:00"),
    ("u-mi", "News intake needs review", "Two new items await validation.", "#news", "2026-11-14T08:10:00+07:00"),
    (None, "Forecast revision", "EIA revised the Brent Q1 2027 outlook.", "#forecast", "2026-11-12T10:00:00+07:00"),
    ("u-lead", "Report ready", "R-2026-041 version 2 is ready to review.", "#reports", "2026-11-14T09:21:00+07:00"),
]

AI_RUNS = [
    ("AI-8F2A", "market_briefing", "deep", 4, 2800, 0.041, "succeeded", "2026-11-14T09:42:00+07:00"),
    ("AI-8F19", "news_summarization", "standard", 2, 1400, 0.008, "succeeded", "2026-11-14T08:02:00+07:00"),
    ("AI-8F11", "chat_query", "standard", 3, 2100, 0.018, "fallback", "2026-11-13T16:40:00+07:00"),
    ("AI-8EF0", "chat_query", "simple", 2, 900, 0.004, "succeeded", "2026-11-13T15:10:00+07:00"),
]


def _series(base: float, drift: float, vol: float, seed: int, n: int = 365, integer: bool = False) -> list[float]:
    values = []
    for i in range(n - 1, -1, -1):
        t = (n - i) / n
        noise = math.sin((i + seed) * 1.31) * vol + math.cos((i + seed * 2.1) * 0.43) * vol * 0.55
        value = base * (1 - drift * t) + noise + math.sin(i * 0.11 + seed) * base * 0.012
        values.append(round(value) if integer else round(value, 2))
    values[-1] = base
    return values


def _already_seeded(db) -> bool:
    return db.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0


def seed(db) -> None:
    """Insert the demo dataset once; a second call changes nothing."""
    if _already_seeded(db):
        return

    now_iso = DEMO_NOW.isoformat(timespec="seconds")
    db.executemany(
        "INSERT INTO users (id, name, role, department, max_classification, can_view_restricted, "
        "can_export, is_admin, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(*user, now_iso) for user in USERS],
    )
    db.executemany(
        "INSERT INTO sources (id, name, kind, classification, licence_note, active) VALUES (?, ?, ?, ?, ?, 1)",
        SOURCES,
    )
    db.executemany(
        "INSERT INTO formulas (id, name, version, expression, input_instruments, "
        "allow_mixed_price_types, unit, created_at, active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
        [(*formula, now_iso) for formula in FORMULAS],
    )

    for order, instrument in enumerate(INSTRUMENTS):
        (instrument_id, name, short_name, ticker, group_name, unit, price_type, decimals,
         classification, _value, _drift, _vol, _seed, _source_id, _status, _quality,
         formula_id) = instrument
        db.execute(
            "INSERT INTO instruments (id, name, short_name, ticker, group_name, unit, price_type, "
            "decimals, classification, description, formula_id, display_order) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (instrument_id, name, short_name, ticker, group_name, unit, price_type, decimals,
             classification, f"Synthetic demo series for {short_name}.", formula_id, order),
        )

    observation_inputs: dict[str, list[int]] = {}
    for instrument in INSTRUMENTS:
        (instrument_id, _name, _short, _ticker, _group, unit, _price_type, _decimals,
         classification, base, drift, vol, series_seed, source_id, data_status,
         quality_status, formula_id) = instrument
        integer = instrument_id == "usd_vnd"
        values = _series(base, drift, vol, series_seed, integer=integer)
        rows = []
        for offset in range(len(values) - 1, -1, -1):
            market_day = DEMO_NOW - timedelta(days=offset)
            market_time = market_day.replace(hour=8, minute=30, second=0, microsecond=0)
            ingested_at = market_time + timedelta(minutes=2)
            rows.append(
                (
                    instrument_id, source_id, values[len(values) - 1 - offset], unit,
                    market_time.isoformat(timespec="seconds"),
                    ingested_at.isoformat(timespec="seconds"),
                    data_status, quality_status, classification, formula_id, None, None,
                )
            )
        db.executemany(
            "INSERT INTO market_observations (instrument_id, source_id, value, unit, market_time, "
            "ingested_at, data_status, quality_status, classification, formula_id, "
            "calculation_inputs, calculated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        observation_inputs[instrument_id] = [
            row["id"]
            for row in db.execute(
                "SELECT id FROM market_observations WHERE instrument_id = ? "
                "ORDER BY market_time DESC LIMIT 1",
                (instrument_id,),
            )
        ]

    # Calculated rows reference the observation ids they were computed from.
    formula_inputs = {
        "crack_gasoline": ["ron95", "brent_futures"],
        "crack_diesel": ["diesel", "brent_futures"],
        "crack_321": ["ron95", "diesel", "brent_futures"],
    }
    for instrument_id, inputs in formula_inputs.items():
        input_ids = [observation_inputs[input_id][0] for input_id in inputs]
        latest = db.execute(
            "SELECT id, formula_id FROM market_observations WHERE instrument_id = ? "
            "ORDER BY market_time DESC LIMIT 1",
            (instrument_id,),
        ).fetchone()
        db.execute(
            "UPDATE market_observations SET calculation_inputs = ?, calculated_at = ? WHERE id = ?",
            (json.dumps(input_ids), now_iso, latest["id"]),
        )

    # Seeded calculated rows are the deterministic formula output over the same
    # latest inputs, so the stored value never contradicts the formula.
    for instrument_id, inputs in formula_inputs.items():
        values = []
        for input_id in inputs:
            row = db.execute(
                "SELECT value FROM market_observations WHERE instrument_id = ? "
                "ORDER BY market_time DESC LIMIT 1",
                (input_id,),
            ).fetchone()
            values.append(row["value"])
        if len(values) == 2:
            calculated = values[0] - values[1]
        else:
            calculated = (2 * values[0] + values[1] - 3 * values[2]) / 3
        db.execute(
            "UPDATE market_observations SET value = ? WHERE id = ("
            "SELECT id FROM market_observations WHERE instrument_id = ? "
            "ORDER BY market_time DESC LIMIT 1)",
            (round(calculated, 2), instrument_id),
        )

    for label, topic_id in TOPICS.items():
        db.execute("INSERT INTO topics (id, label) VALUES (?, ?)", (topic_id, label))

    for item in NEWS:
        db.execute(
            "INSERT INTO news_items (id, title, source_id, published_at, ingested_at, body, summary, "
            "insight, classification, processing_status, relevance, duplicate_of, coverage_note, "
            "created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                item["id"], item["title"], item["source_id"], item["published_at"],
                item["ingested_at"], item["body"], item["summary"], item["insight"],
                item["classification"], item["status"], item["relevance"],
                item["duplicate_of"], item["coverage_note"], "u-mi", item["ingested_at"],
            ),
        )
        for topic in item["topics"]:
            db.execute(
                "INSERT INTO news_topics (news_id, topic_id) VALUES (?, ?)",
                (item["id"], TOPICS[topic]),
            )
        for instrument_id in item["instruments"]:
            db.execute(
                "INSERT INTO news_instruments (news_id, instrument_id) VALUES (?, ?)",
                (item["id"], instrument_id),
            )

    for event_id, title, event_type, occurred, source_id, instrument_ids, news_ids, classification in EVENTS:
        db.execute(
            "INSERT INTO events (id, title, event_type, occurred_at, source_id, status, classification) "
            "VALUES (?, ?, ?, ?, ?, 'confirmed', ?)",
            (event_id, title, event_type, f"{occurred}T12:00:00+07:00", source_id, classification),
        )
        for instrument_id in instrument_ids:
            db.execute(
                "INSERT INTO event_instruments (event_id, instrument_id) VALUES (?, ?)",
                (event_id, instrument_id),
            )
        for news_id in news_ids:
            db.execute(
                "INSERT INTO event_news (event_id, news_id) VALUES (?, ?)",
                (event_id, news_id),
            )

    db.executemany(
        "INSERT INTO drivers (group_name, label, detail, direction, strength, as_of, classification) "
        "VALUES (?, ?, ?, ?, ?, ?, 'internal')",
        [(*driver, now_iso) for driver in DRIVERS],
    )

    for forecast in FORECASTS:
        (forecast_id, _source, source_id, instrument_id, value, period, horizon, methodology,
         latest_version, classification, actual, previous, published) = forecast
        db.execute(
            "INSERT INTO forecasts (id, instrument_id, source_id, horizon, period, classification, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (forecast_id, instrument_id, source_id, horizon, period, classification, now_iso),
        )
        for version in range(1, latest_version + 1):
            if version == latest_version:
                version_value = value
            elif version == latest_version - 1 and previous is not None:
                version_value = previous
            else:
                version_value = round(value - 0.5 * (latest_version - version), 2)
            db.execute(
                "INSERT INTO forecast_versions (forecast_id, version, value, methodology, "
                "published_at, ingested_at, created_by) VALUES (?, ?, ?, ?, ?, ?, 'u-mi')",
                (forecast_id, version, version_value, methodology,
                 f"{published}T12:00:00+07:00", f"{published}T12:05:00+07:00"),
            )
        latest_row = db.execute(
            "SELECT id FROM forecast_versions WHERE forecast_id = ? ORDER BY version DESC LIMIT 1",
            (forecast_id,),
        ).fetchone()
        if actual is None:
            db.execute(
                "INSERT INTO forecast_evaluations (forecast_version_id, actual_observation_id, "
                "absolute_error, percentage_error, note, evaluated_at) VALUES (?, NULL, NULL, NULL, ?, ?)",
                (latest_row["id"], "actual missing", now_iso),
            )
        else:
            absolute = round(abs(value - actual), 2)
            percentage = round(abs(value - actual) / actual * 100, 2)
            db.execute(
                "INSERT INTO forecast_evaluations (forecast_version_id, actual_observation_id, "
                "absolute_error, percentage_error, note, evaluated_at) VALUES (?, ?, ?, ?, NULL, ?)",
                (latest_row["id"], observation_inputs[instrument_id][0], absolute, percentage, now_iso),
            )

    for report in REPORTS:
        (report_id, report_type, title, range_start, range_end, classification, latest_version,
         created_at, data_cutoff, source_ids) = report
        db.execute(
            "INSERT INTO reports (id, type, title, range_start, range_end, classification, "
            "created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, 'u-lead', ?)",
            (report_id, report_type, title, range_start, range_end, classification, created_at),
        )
        for version in range(1, latest_version + 1):
            content = json.dumps(
                {
                    "title": title,
                    "summary": "Synthetic demo report content frozen at generation.",
                    "sections": [{"heading": "Market overview", "body": "Demo content."}],
                    "version": version,
                }
            )
            cursor = db.execute(
                "INSERT INTO report_versions (report_id, version, content, data_cutoff, "
                "requester_id, created_at) VALUES (?, ?, ?, ?, 'u-lead', ?)",
                (report_id, version, content, data_cutoff, created_at),
            )
            version_id = cursor.lastrowid
            for position, source_id in enumerate(source_ids):
                db.execute(
                    "INSERT INTO report_sources (report_version_id, source_kind, source_id, label, position) "
                    "VALUES (?, 'source', ?, ?, ?)",
                    (version_id, source_id, source_id, position),
                )

    db.execute(
        "INSERT INTO briefings (id, title, created_at, classification) VALUES ('B-1', ?, ?, 'internal')",
        ("Morning market briefing", now_iso),
    )
    briefing_moves = json.dumps(
        [
            {"instrument": "Brent", "value": 78.42, "unit": "USD/bbl", "change": 1.07, "pct": 1.38},
            {"instrument": "WTI", "value": 74.18, "unit": "USD/bbl", "change": 0.52, "pct": 0.71},
            {"instrument": "Gasoline crack", "value": 13.68, "unit": "USD/bbl", "change": 0.62, "pct": 3.5},
        ]
    )
    briefing_drivers = json.dumps(
        ["OPEC+ discipline", "Red Sea freight", "Asia gasoline demand"]
    )
    briefing_watchlist = json.dumps(
        ["Gasoline crack vs 20-day average", "OPEC+ ministerial commentary"]
    )
    for version in (1, 2, 3):
        cursor = db.execute(
            "INSERT INTO briefing_versions (briefing_id, version, generated_at, data_cutoff, "
            "headline, moves, drivers, watchlist, ai_execution_id, classification) "
            "VALUES ('B-1', ?, ?, ?, ?, ?, ?, ?, NULL, 'internal')",
            (
                version,
                f"2026-11-14T09:1{version}:00+07:00",
                "2026-11-14T09:00:00+07:00",
                "Supply risk meets product strength" if version == 3 else "Market update",
                briefing_moves,
                briefing_drivers,
                briefing_watchlist,
            ),
        )
        for position, source_id in enumerate(["SRC-ICE", "SRC-PLATTS", "SRC-REUTERS"]):
            db.execute(
                "INSERT INTO briefing_sources (briefing_version_id, source_kind, source_id, label, position) "
                "VALUES (?, 'source', ?, ?, ?)",
                (cursor.lastrowid, source_id, source_id, position),
            )

    db.executemany(
        "INSERT INTO notifications (user_id, title, body, route, created_at, read_at) "
        "VALUES (?, ?, ?, ?, ?, NULL)",
        NOTIFICATIONS,
    )

    for task_id, task_type, reasoning, tools_used, latency_ms, cost_usd, status, created_at in AI_RUNS:
        db.execute(
            "INSERT INTO ai_tasks (id, task_type, user_id, permission_scope, input, created_at) "
            "VALUES (?, ?, 'u-mi', ?, ?, ?)",
            (
                task_id, task_type,
                json.dumps({"max_classification": "restricted", "can_view_restricted": True,
                            "can_export": True, "is_admin": True}),
                json.dumps({"demo": True}),
                created_at,
            ),
        )
        db.execute(
            "INSERT INTO ai_executions (task_id, model, reasoning, tools_used, latency_ms, "
            "cost_usd, status, validation, output, created_at) "
            "VALUES (?, 'demo-orchestrator/standard', ?, ?, ?, ?, ?, 'passed', NULL, ?)",
            (task_id, reasoning, tools_used, latency_ms, cost_usd, status, created_at),
        )

    db.commit()
