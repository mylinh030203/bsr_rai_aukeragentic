"""Forecast routes."""

from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from ..auth import require_role
from ..db import get_db
from ..errors import ApiError
from ..services import forecasts

forecast_bp = Blueprint("forecast", __name__)


@forecast_bp.get("/forecasts")
def list_forecasts():
    args = request.args
    return jsonify(
        {
            "forecasts": forecasts.list_forecasts(
                get_db(),
                g.user,
                instrument=args.get("instrument") or None,
                source=args.get("source") or None,
                horizon=args.get("horizon") or None,
            )
        }
    )


@forecast_bp.get("/forecasts/evaluation")
def evaluation():
    args = request.args
    return jsonify(
        forecasts.evaluation(
            get_db(),
            g.user,
            instrument=args.get("instrument") or None,
            horizon=args.get("horizon") or None,
        )
    )


@forecast_bp.get("/forecasts/<forecast_id>/versions")
def versions(forecast_id: str):
    return jsonify({"versions": forecasts.get_versions(get_db(), g.user, forecast_id)})


@forecast_bp.post("/forecasts/<forecast_id>/versions")
@require_role("mi")
def add_version(forecast_id: str):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request", "Expected a JSON object.")
    return jsonify(forecasts.add_version(get_db(), g.user, forecast_id, body)), 201
