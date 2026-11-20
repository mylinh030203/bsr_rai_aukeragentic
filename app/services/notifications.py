"""User and broadcast notifications."""

from __future__ import annotations

from ..db import utc_now
from ..errors import ApiError


def list_notifications(db, user) -> list[dict]:
    rows = db.execute(
        "SELECT * FROM notifications WHERE user_id IS NULL OR user_id = ? "
        "ORDER BY created_at DESC, id DESC",
        (user["id"],),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "body": row["body"],
            "route": row["route"],
            "created_at": row["created_at"],
            "read_at": row["read_at"],
        }
        for row in rows
    ]


def mark_read(db, user, notification_id: int) -> None:
    row = db.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,)).fetchone()
    if row is None or (row["user_id"] is not None and row["user_id"] != user["id"]):
        raise ApiError(404, "not_found", "Notification not found.")
    db.execute(
        "UPDATE notifications SET read_at = ? WHERE id = ?", (utc_now(), notification_id)
    )
    db.commit()
