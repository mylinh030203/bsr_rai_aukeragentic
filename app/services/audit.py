"""Append-only audit log writer."""

from __future__ import annotations

from flask import g, has_app_context

from ..db import utc_now


def record(
    db,
    *,
    action: str,
    result: str,
    actor=None,
    object_type: str | None = None,
    object_id: str | None = None,
    classification: str | None = None,
    detail: str | None = None,
) -> None:
    """Insert one audit row. There is deliberately no update or delete helper."""
    actor_id = None
    actor_role = None
    if actor is not None:
        try:
            actor_id = actor["id"]
            actor_role = actor["role"]
        except (KeyError, IndexError, TypeError):
            actor_id = None
    db.execute(
        "INSERT INTO audit_log "
        "(actor_id, actor_role, action, object_type, object_id, result, classification, detail, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            actor_id,
            actor_role,
            action,
            object_type,
            object_id,
            result,
            classification,
            detail,
            utc_now(),
        ),
    )
    db.commit()


def record_restricted_view(db, user, object_type: str, object_id) -> None:
    """Record that a restricted object was serialized to an authorized user.

    Deduplicated per request so one response does not write a row per field.
    """
    if user is None:
        return
    seen = None
    if has_app_context():
        seen = g.get("restricted_views")
        if seen is None:
            seen = set()
            g.restricted_views = seen
    key = (object_type, str(object_id))
    if seen is not None:
        if key in seen:
            return
        seen.add(key)
    record(
        db,
        action="restricted_view",
        result="allowed",
        actor=user,
        object_type=object_type,
        object_id=str(object_id),
        classification="restricted",
    )
