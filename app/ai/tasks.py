"""AI task definitions for the deterministic demo adapter."""

from __future__ import annotations

TASKS = {
    "market_briefing": {
        "model": "demo-orchestrator/large",
        "reasoning": "deep",
        "cost_usd": 0.041,
        "tools": ("observations", "news", "analytics"),
        "required": ("moves", "drivers", "watchlist"),
    },
    "news_summarization": {
        "model": "demo-orchestrator/small",
        "reasoning": "standard",
        "cost_usd": 0.008,
        "tools": ("news",),
        "required": ("title", "body"),
    },
    "chat_query": {
        "model": "demo-orchestrator/standard",
        "reasoning": "standard",
        "cost_usd": 0.018,
        "tools": ("observations", "news", "analytics"),
        "required": ("question",),
    },
    "report_generation": {
        "model": "demo-orchestrator/standard",
        "reasoning": "standard",
        "cost_usd": 0.02,
        "tools": ("observations", "news", "analytics"),
        "required": ("title",),
    },
    "analysis": {
        "model": "demo-orchestrator/large",
        "reasoning": "deep",
        "cost_usd": 0.03,
        "tools": ("observations", "news", "analytics"),
        "required": ("question",),
    },
}
