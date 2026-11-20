"""Administration and global routes."""

from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from ..auth import require_admin
from ..db import get_db
from ..errors import ApiError
from ..services import admin, notifications, search

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/admin/users")
@require_admin
def list_users():
    return jsonify({"users": admin.list_users(get_db())})


@admin_bp.patch("/admin/users/<user_id>")
@require_admin
def update_user(user_id: str):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request", "Expected a JSON object.")
    return jsonify(admin.update_user(get_db(), g.user, user_id, body))


@admin_bp.get("/admin/sources")
@require_admin
def list_sources():
    return jsonify({"sources": admin.list_sources(get_db())})


@admin_bp.get("/admin/audit")
@require_admin
def list_audit():
    args = request.args
    try:
        limit = int(args.get("limit", 100))
    except ValueError:
        raise ApiError(422, "invalid_limit", "limit must be an integer.")
    return jsonify(
        {
            "audit": admin.list_audit(
                get_db(),
                action=args.get("action") or None,
                actor=args.get("actor") or None,
                from_time=args.get("from") or None,
                to_time=args.get("to") or None,
                limit=limit,
            )
        }
    )


@admin_bp.get("/admin/ai-executions")
@require_admin
def list_ai_executions():
    return jsonify({"executions": admin.list_ai_executions(get_db())})


@admin_bp.get("/ai/executions")
@require_admin
def list_ai_executions_alias():
    """Documented alias kept for API consumers that use the short path."""
    return jsonify({"executions": admin.list_ai_executions(get_db())})


@admin_bp.get("/search")
def global_search():
    query = str(request.args.get("q") or "").strip()
    if not query:
        raise ApiError(422, "validation_error", "q is required.")
    return jsonify(search.search(get_db(), g.user, query))


@admin_bp.get("/notifications")
def list_notifications():
    return jsonify({"notifications": notifications.list_notifications(get_db(), g.user)})


@admin_bp.post("/notifications/<int:notification_id>/read")
def mark_notification_read(notification_id: int):
    notifications.mark_read(get_db(), g.user, notification_id)
    return jsonify({}), 204
