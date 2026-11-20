"""Administration service: users, sources, audit and AI executions."""

from __future__ import annotations

from ..db import utc_now
from ..errors import ApiError
from ..permissions import RANK
from .audit import record

PERMISSION_FIELDS = ("can_view_restricted", "can_export", "is_admin")


def list_users(db) -> list[dict]:
    rows = db.execute("SELECT * FROM users ORDER BY role, name").fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "role": row["role"],
            "department": row["department"],
            "max_classification": row["max_classification"],
            "can_view_restricted": bool(row["can_view_restricted"]),
            "can_export": bool(row["can_export"]),
            "is_admin": bool(row["is_admin"]),
        }
        for row in rows
    ]


def update_user(db, actor, user_id: str, payload: dict) -> dict:
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        raise ApiError(404, "not_found", "User not found.")
    updates = {}
    if "max_classification" in payload:
        classification = str(payload["max_classification"]).lower()
        if classification not in RANK:
            raise ApiError(422, "invalid_classification", "Unknown classification.")
        updates["max_classification"] = classification
    for field in PERMISSION_FIELDS:
        if field in payload:
            updates[field] = 1 if payload[field] else 0
    if not updates:
        raise ApiError(422, "validation_error", "No supported permission fields supplied.")
    assignments = ", ".join(f"{field} = ?" for field in updates)
    db.execute(
        f"UPDATE users SET {assignments} WHERE id = ?",
        (*updates.values(), user_id),
    )
    db.commit()
    record(
        db,
        action="permission_change",
        result="succeeded",
        actor=actor,
        object_type="user",
        object_id=user_id,
        classification=updates.get("max_classification", user["max_classification"]),
        detail=", ".join(sorted(updates)),
    )
    updated = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return {
        "id": updated["id"],
        "name": updated["name"],
        "role": updated["role"],
        "max_classification": updated["max_classification"],
        "can_view_restricted": bool(updated["can_view_restricted"]),
        "can_export": bool(updated["can_export"]),
        "is_admin": bool(updated["is_admin"]),
    }


def list_sources(db) -> list[dict]:
    rows = db.execute("SELECT * FROM sources ORDER BY id").fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "kind": row["kind"],
            "classification": row["classification"],
            "licence_note": row["licence_note"],
            "active": bool(row["active"]),
        }
        for row in rows
    ]


def list_audit(
    db,
    action: str | None = None,
    actor: str | None = None,
    from_time: str | None = None,
    to_time: str | None = None,
    limit: int = 100,
) -> list[dict]:
    sql = "SELECT * FROM audit_log WHERE 1 = 1"
    params: list = []
    if action:
        sql += " AND action = ?"
        params.append(action)
    if actor:
        sql += " AND (actor_id = ? OR actor_role = ?)"
        params.extend([actor, actor])
    if from_time:
        sql += " AND created_at >= ?"
        params.append(str(from_time))
    if to_time:
        sql += " AND created_at <= ?"
        params.append(str(to_time))
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(max(1, min(int(limit), 500)))
    return [
        {
            "id": row["id"],
            "actor_id": row["actor_id"],
            "actor_role": row["actor_role"],
            "action": row["action"],
            "object_type": row["object_type"],
            "object_id": row["object_id"],
            "result": row["result"],
            "classification": row["classification"],
            "detail": row["detail"],
            "created_at": row["created_at"],
        }
        for row in db.execute(sql, params)
    ]


def list_ai_executions(db) -> list[dict]:
    rows = db.execute(
        "SELECT e.*, t.task_type, t.user_id FROM ai_executions e "
        "JOIN ai_tasks t ON t.id = e.task_id ORDER BY e.created_at DESC, e.id DESC"
    ).fetchall()
    return [
        {
            "id": row["id"],
            "task_id": row["task_id"],
            "task_type": row["task_type"],
            "user_id": row["user_id"],
            "model": row["model"],
            "reasoning": row["reasoning"],
            "tools_used": row["tools_used"],
            "latency_ms": row["latency_ms"],
            "cost_usd": row["cost_usd"],
            "status": row["status"],
            "validation": row["validation"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
