"""Permission-scoped assistant: retrieval, deterministic tools, citations, fallback."""

from __future__ import annotations

from ..permissions import can_read, visible_rows
from . import ai_runs, analytics, market
from .audit import record, record_restricted_view


def _latest_observation(db, user, instrument_id: str):
    row = db.execute(
        "SELECT * FROM market_observations WHERE instrument_id = ? "
        "ORDER BY market_time DESC LIMIT 1",
        (instrument_id,),
    ).fetchone()
    if row is None or not can_read(row, user):
        return None
    return row


def _series_values(db, user, instrument_id: str, limit: int) -> list[float]:
    rows = db.execute(
        "SELECT value, classification FROM market_observations WHERE instrument_id = ? "
        "ORDER BY market_time DESC LIMIT ?",
        (instrument_id, limit),
    ).fetchall()
    values = [row["value"] for row in reversed(rows) if can_read(row, user)]
    return values


def _evidence(db, user) -> tuple[list[dict], list[dict]]:
    instruments = visible_rows(
        db.execute("SELECT * FROM instruments ORDER BY display_order").fetchall(), user
    )
    observations = []
    for instrument in instruments:
        row = _latest_observation(db, user, instrument["id"])
        if row is None:
            continue
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "market_observation", row["id"])
        observations.append(
            {
                "kind": "observation",
                "id": str(row["id"]),
                "label": f"{instrument['short_name']} {row['value']} {row['unit']}",
                "value": row["value"],
                "unit": row["unit"],
                "instrument_id": instrument["id"],
                "market_time": row["market_time"],
            }
        )
        if len(observations) >= 8:
            break
    news_rows = db.execute(
        "SELECT * FROM news_items ORDER BY published_at DESC LIMIT 5"
    ).fetchall()
    visible_news = visible_rows(news_rows, user)
    for row in visible_news:
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "news_item", row["id"])
    news = [
        {
            "kind": "news",
            "id": row["id"],
            "label": row["title"],
            "published_at": row["published_at"],
        }
        for row in visible_news
    ]
    return observations, news


def _calculations(db, user, question: str) -> list[dict]:
    text = question.lower()
    calculations = []
    if "crack" in text or "spread" in text:
        crude = _latest_observation(db, user, "brent_futures")
        if crude is not None:
            try:
                computed = market.compute_crack(
                    db, user, "CS-GAS-2.1", crude["market_time"]
                )
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
                # A formula that cannot be evaluated is omitted, never guessed.
                pass
        wti = _latest_observation(db, user, "wti_futures")
        if crude is not None and wti is not None:
            calculations.append(
                {
                    "label": "Brent-WTI spread",
                    "value": analytics.spread(crude["value"], wti["value"]),
                    "unit": "USD/bbl",
                    "method": "Brent futures - WTI futures",
                }
            )
    if "return" in text:
        values = _series_values(db, user, "brent_futures", 6)
        value = analytics.return_over(values, 5)
        if value is not None:
            calculations.append(
                {
                    "label": "5-session return, Brent",
                    "value": round(value, 2),
                    "unit": "%",
                    "method": "close-to-close, 5 sessions",
                }
            )
    if "volatil" in text:
        values = _series_values(db, user, "brent_futures", 30)
        value = analytics.annualized_volatility(values)
        if value is not None:
            calculations.append(
                {
                    "label": "30-session annualized volatility, Brent",
                    "value": round(value, 2),
                    "unit": "%",
                    "method": "annualized stdev of daily log returns",
                }
            )
    return calculations


def query(db, user, question: str) -> dict:
    observations, news = _evidence(db, user)
    evidence = observations + news
    refusal = None
    if ("physical" in question.lower() or "dated" in question.lower()) and not user["can_view_restricted"]:
        refusal = "Restricted physical assessments are not available in your scope."
    calculations = _calculations(db, user, question)
    context = {
        "question": question,
        "evidence": evidence,
        "calculations": calculations,
        "tools_used": ["observations", "news", "analytics"],
        "refusal": refusal,
    }
    execution = ai_runs.execute(
        db,
        task_type="chat_query",
        user=user,
        task_input={"question": question},
        context=context,
    )
    output = execution["output"]
    record(
        db,
        action="ai_request",
        result=execution["status"],
        actor=user,
        object_type="ai_task",
        object_id=execution["task_id"],
        classification=user["max_classification"],
        detail="chat_query",
    )
    return {
        "answer": output.get("answer") or output.get("message") or "AI interpretation unavailable.",
        "citations": output.get("citations", []),
        "tool_trace": output.get("tool_trace", []),
        "calculations": output.get("calculations", []),
        "refusal": refusal,
        "execution": {
            "task_id": execution["task_id"],
            "status": execution["status"],
            "model": execution["model"],
            "latency_ms": execution["latency_ms"],
            "cost_usd": execution["cost_usd"],
            "validation": execution["validation"],
        },
    }
