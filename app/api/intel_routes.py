"""Briefing and analysis routes."""

from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from ..auth import require_role
from ..db import get_db
from ..errors import ApiError
from ..services import analysis, briefings

intel_bp = Blueprint("intel", __name__)


@intel_bp.get("/briefings")
def list_briefings():
    return jsonify({"briefings": briefings.list_briefings(get_db(), g.user)})


@intel_bp.post("/briefings")
@require_role("mi")
def generate_briefing():
    return jsonify(briefings.generate(get_db(), g.user)), 201


@intel_bp.get("/analysis")
def build_analysis():
    question = str(request.args.get("question") or "").strip()
    if not question:
        raise ApiError(422, "validation_error", "question is required.")
    return jsonify(analysis.build(get_db(), g.user, question))
