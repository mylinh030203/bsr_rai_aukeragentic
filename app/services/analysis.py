"""Computed analysis workspace: facts, calculations, assumptions, recommendation."""

from __future__ import annotations

from ..permissions import can_read
from . import ai_runs, analytics, market


def _latest(db, user, instrument_id: str):
    row = db.execute(
        "SELECT * FROM market_observations WHERE instrument_id = ? "
        "ORDER BY market_time DESC LIMIT 1",
        (instrument_id,),
    ).fetchone()
    if row is None or not can_read(row, user):
        return None
    return row


def _values(db, user, instrument_id: str, limit: int) -> list[float]:
    rows = db.execute(
        "SELECT value, classification FROM market_observations WHERE instrument_id = ? "
        "ORDER BY market_time DESC LIMIT ?",
        (instrument_id, limit),
    ).fetchall()
    return [row["value"] for row in reversed(rows) if can_read(row, user)]


def build(db, user, question: str) -> dict:
    brent = _latest(db, user, "brent_futures")
    wti = _latest(db, user, "wti_futures")
    ron95 = _latest(db, user, "ron95")
    crack = _latest(db, user, "crack_gasoline")

    facts = []
    evidence = []
    if brent is not None:
        facts.append(f"Brent futures are {brent['value']} {brent['unit']}.")
        evidence.append({"kind": "observation", "id": str(brent["id"]), "label": "Brent futures"})
    if wti is not None:
        facts.append(f"WTI futures are {wti['value']} {wti['unit']}.")
        evidence.append({"kind": "observation", "id": str(wti["id"]), "label": "WTI futures"})
    if crack is not None:
        facts.append(f"Gasoline crack (CS-GAS-2.1) is {crack['value']} {crack['unit']}.")
        evidence.append({"kind": "observation", "id": str(crack["id"]), "label": "Gasoline crack"})

    calculations = []
    brent_values = _values(db, user, "brent_futures", 30)
    five_day = analytics.return_over(brent_values, 5)
    if five_day is not None:
        calculations.append(
            {
                "label": "5-session return, Brent",
                "value": round(five_day, 2),
                "unit": "%",
                "method": "close-to-close, 5 sessions",
            }
        )
    volatility = analytics.annualized_volatility(brent_values)
    if volatility is not None:
        calculations.append(
            {
                "label": "30-session annualized volatility, Brent",
                "value": round(volatility, 2),
                "unit": "%",
                "method": "annualized stdev of daily log returns",
            }
        )
    if brent is not None and wti is not None:
        calculations.append(
            {
                "label": "Brent-WTI spread",
                "value": analytics.spread(brent["value"], wti["value"]),
                "unit": "USD/bbl",
                "method": "Brent futures - WTI futures",
            }
        )
    if brent is not None:
        try:
            computed = market.compute_crack(db, user, "CS-GAS-2.1", brent["market_time"])
            formula = computed["formula"]
            calculations.append(
                {
                    "label": f"Gasoline crack ({formula['id']} v{formula['version']})",
                    "value": computed["value"],
                    "unit": computed["unit"],
                    "method": f"{formula['expression']}, formula {formula['id']}",
                }
            )
        except Exception:
            pass

    assumptions = [
        "Demo series are illustrative and are not official BSR or licensed assessments.",
        "The freight signal is treated as a product-arbitrage input, not proof of crude supply loss.",
    ]
    if not user["can_view_restricted"]:
        assumptions.append("No restricted physical assessment is included for your role.")

    recommendation = {
        "title": "Keep product cracks as the primary watch item; do not extrapolate a crude-supply shock from one signal.",
        "confidence": "Medium",
        "rationale": "The evidence supports a watch stance, not a trading instruction.",
        "watch": ["Gasoline crack vs 20-day average", "OPEC+ ministerial commentary"],
    }

    context = {
        "question": question,
        "facts": facts,
        "calculations": calculations,
        "assumptions": assumptions,
        "recommendation": recommendation,
    }
    execution = ai_runs.execute(
        db,
        task_type="analysis",
        user=user,
        task_input={"question": question},
        context=context,
    )
    return {
        "question": question,
        "as_of": brent["market_time"] if brent is not None else None,
        "status": "computed",
        "facts": facts,
        "calculations": calculations,
        "assumptions": assumptions,
        "recommendation": recommendation,
        "evidence": evidence,
        "execution": {
            "task_id": execution["task_id"],
            "status": execution["status"],
            "model": execution["model"],
        },
    }
