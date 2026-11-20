"""Permission-scoped global search."""

from __future__ import annotations

from ..permissions import visible_rows
from .audit import record_restricted_view


def search(db, user, query: str) -> dict:
    if not query:
        raise ValueError("query is required")
    pattern = f"%{query}%"
    instruments = visible_rows(
        db.execute(
            "SELECT * FROM instruments WHERE name LIKE ? OR short_name LIKE ? OR ticker LIKE ? "
            "ORDER BY display_order LIMIT 20",
            (pattern, pattern, pattern),
        ).fetchall(),
        user,
    )
    news = visible_rows(
        db.execute(
            "SELECT * FROM news_items WHERE title LIKE ? OR body LIKE ? ORDER BY published_at DESC LIMIT 20",
            (pattern, pattern),
        ).fetchall(),
        user,
    )
    reports = visible_rows(
        db.execute(
            "SELECT * FROM reports WHERE title LIKE ? OR type LIKE ? ORDER BY created_at DESC LIMIT 20",
            (pattern, pattern),
        ).fetchall(),
        user,
    )
    for row in instruments:
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "instrument", row["id"])
    for row in news:
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "news_item", row["id"])
    for row in reports:
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "report", row["id"])
    return {
        "instruments": [
            {"id": row["id"], "name": row["name"], "group": row["group_name"]} for row in instruments
        ],
        "news": [{"id": row["id"], "title": row["title"], "published_at": row["published_at"]} for row in news],
        "reports": [{"id": row["id"], "title": row["title"], "type": row["type"]} for row in reports],
    }
