"""Deterministic local AI adapter.

The adapter interprets context that callers have already filtered and computed.
It never computes a market number itself; those come from the analytical service.
"""

from __future__ import annotations

from .tasks import TASKS


def _require(definition: dict, context: dict) -> None:
    missing = [key for key in definition["required"] if key not in context]
    if missing:
        raise ValueError(f"missing context: {', '.join(missing)}")


def _news_summary(context: dict) -> dict:
    body = str(context.get("body") or "")
    summary = body[:180] if body else "Summary unavailable."
    topics = list(context.get("topics") or [])
    relevance = 60 + (len(topics) * 5) % 40
    return {
        "summary": summary,
        "insight": "AI interpretation: the item is retained with its source attribution; "
        "no market number is inferred.",
        "topics": topics,
        "relevance": relevance,
    }


def _chat_answer(context: dict) -> dict:
    evidence = list(context.get("evidence") or [])
    calculations = list(context.get("calculations") or [])
    citations = [
        {"kind": item.get("kind"), "id": item.get("id"), "label": item.get("label")}
        for item in evidence
    ]
    if not evidence and not calculations:
        answer = (
            "AI interpretation: no permitted records match this question, so the data is "
            "unavailable in your scope."
        )
    else:
        parts = [
            f"AI interpretation: {len(evidence)} permitted record(s) were retrieved."
        ]
        if calculations:
            labels = ", ".join(str(item.get("label")) for item in calculations)
            parts.append(f"Deterministic calculations: {labels}.")
        if context.get("refusal"):
            parts.append(str(context["refusal"]))
        answer = " ".join(parts)
    return {
        "answer": answer,
        "citations": citations,
        "tool_trace": [
            {"tool": tool, "status": "ok"} for tool in context.get("tools_used", [])
        ],
        "calculations": calculations,
    }


def _briefing(context: dict) -> dict:
    moves = list(context.get("moves") or [])
    return {
        "headline": context.get("headline")
        or "AI interpretation: markets are mixed; product cracks carry the signal.",
        "moves": moves,
        "drivers": list(context.get("drivers") or []),
        "watchlist": list(context.get("watchlist") or []),
    }


def _analysis(context: dict) -> dict:
    return {
        "facts": list(context.get("facts") or []),
        "calculations": list(context.get("calculations") or []),
        "assumptions": list(context.get("assumptions") or []),
        "recommendation": context.get("recommendation")
        or {
            "title": "Keep watching; no decision is executed.",
            "confidence": "Low",
            "rationale": "AI interpretation with limited evidence.",
            "watch": [],
        },
    }


def _report(context: dict) -> dict:
    return {
        "title": context.get("title") or "Market report",
        "sections": list(context.get("sections") or []),
        "sources": list(context.get("sources") or []),
    }


BUILDERS = {
    "market_briefing": _briefing,
    "news_summarization": _news_summary,
    "chat_query": _chat_answer,
    "report_generation": _report,
    "analysis": _analysis,
}


def run(task_type: str, context: dict) -> dict:
    """Run one deterministic task and return the recorded execution metadata."""
    definition = TASKS.get(task_type)
    if definition is None:
        raise ValueError(f"unknown task type: {task_type}")
    _require(definition, context)
    output = BUILDERS[task_type](context)
    if not isinstance(output, dict) or not output:
        raise ValueError("adapter produced an invalid output shape")
    return {
        "output": output,
        "model": definition["model"],
        "reasoning": definition["reasoning"],
        "cost_usd": definition["cost_usd"],
        "tools_used": len(definition["tools"]),
        "validation": "passed",
    }
