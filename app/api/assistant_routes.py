"""Assistant route."""

from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from ..auth import rate_limit
from ..db import get_db
from ..errors import ApiError
from ..services import assistant

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.post("/assistant/query")
def query():
    rate_limit("assistant", g.user["id"])
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request", "Expected a JSON object.")
    question = str(body.get("question") or "").strip()
    if not question:
        raise ApiError(422, "validation_error", "question is required.")
    return jsonify(assistant.query(get_db(), g.user, question)), 201
