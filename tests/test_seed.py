"""Seed data: counts, key values and idempotency."""

from __future__ import annotations

import pytest

from app import create_app
from app.db import get_db
from app.services.seed import seed

TABLES = [
    "users",
    "sources",
    "instruments",
    "formulas",
    "market_observations",
    "news_items",
    "topics",
    "news_topics",
    "news_instruments",
    "events",
    "event_instruments",
    "event_news",
    "drivers",
    "forecasts",
    "forecast_versions",
    "forecast_evaluations",
    "reports",
    "report_versions",
    "report_sources",
    "notifications",
    "ai_tasks",
    "ai_executions",
]


@pytest.fixture()
def seeded_app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "seed.db"),
            "SEED_ON_START": True,
        }
    )


def _counts(db) -> dict[str, int]:
    return {table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in TABLES}


def test_seed_inserts_the_demo_dataset(seeded_app):
    with seeded_app.app_context():
        db = get_db()
        counts = _counts(db)
        assert counts["users"] == 3
        assert counts["sources"] == 10
        assert counts["instruments"] == 13
        assert counts["formulas"] == 4
        assert counts["market_observations"] == 13 * 365
        assert counts["news_items"] == 7
        assert counts["events"] == 4
        assert counts["drivers"] == 6
        assert counts["forecasts"] == 6
        assert counts["reports"] == 3
        assert counts["notifications"] == 4
        assert counts["ai_tasks"] == 4
        assert counts["ai_executions"] == 4


def test_seed_matches_the_prototype_key_values(seeded_app):
    with seeded_app.app_context():
        db = get_db()

        def latest(instrument_id):
            return db.execute(
                "SELECT value, unit, classification, formula_id, calculation_inputs, calculated_at "
                "FROM market_observations WHERE instrument_id = ? "
                "ORDER BY market_time DESC LIMIT 1",
                (instrument_id,),
            ).fetchone()

        assert latest("brent_futures")["value"] == 78.42
        assert latest("wti_futures")["value"] == 74.18
        assert latest("ron95")["value"] == 92.1
        assert latest("crack_gasoline")["value"] == 13.68
        assert latest("crack_gasoline")["formula_id"] == "CS-GAS-2.1"
        assert latest("crack_gasoline")["calculation_inputs"]
        assert latest("crack_diesel")["value"] == round(
            latest("diesel")["value"] - latest("brent_futures")["value"], 2
        )
        assert latest("usd_vnd")["value"] == 25480
        assert latest("brent_physical")["classification"] == "restricted"


def test_seed_keeps_news_duplicates_and_missing_actuals(seeded_app):
    with seeded_app.app_context():
        db = get_db()
        duplicate = db.execute("SELECT duplicate_of FROM news_items WHERE id = 'N-2407'").fetchone()
        assert duplicate["duplicate_of"] == "N-2411"
        restricted = db.execute(
            "SELECT classification FROM news_items WHERE id = 'N-2405'"
        ).fetchone()
        assert restricted["classification"] == "restricted"
        missing = db.execute(
            "SELECT note, absolute_error FROM forecast_evaluations WHERE note = 'actual missing'"
        ).fetchone()
        assert missing["note"] == "actual missing"
        assert missing["absolute_error"] is None


def test_seed_is_idempotent(seeded_app):
    with seeded_app.app_context():
        db = get_db()
        before = _counts(db)
        seed(db)
        seed(db)
        assert _counts(db) == before


def test_seeded_crack_values_equal_the_formula_output(seeded_app):
    with seeded_app.app_context():
        from app.services import market

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE role = 'mi'").fetchone()
        as_of = "2026-11-14T09:42:00+07:00"
        for formula_id, instrument_id, expected in (
            ("CS-GAS-2.1", "crack_gasoline", 13.68),
            ("CS-DSL-2.0", "crack_diesel", 17.98),
        ):
            computed = market.compute_crack(db, user, formula_id, as_of)
            stored = db.execute(
                "SELECT value FROM market_observations WHERE instrument_id = ? "
                "ORDER BY market_time DESC LIMIT 1",
                (instrument_id,),
            ).fetchone()
            assert stored["value"] == round(computed["value"], 2) == expected
