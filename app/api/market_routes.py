"""Market data routes."""

from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from ..auth import require_role
from ..db import get_db
from ..errors import ApiError
from ..services import market

market_bp = Blueprint("market", __name__)


@market_bp.get("/overview")
def overview():
    return jsonify(market.overview(get_db(), g.user))


@market_bp.get("/instruments")
def instruments():
    return jsonify({"instruments": market.list_instruments(get_db(), g.user)})


@market_bp.get("/instruments/<instrument_id>")
def instrument_detail(instrument_id: str):
    return jsonify(market.get_instrument(get_db(), g.user, instrument_id))


@market_bp.get("/instruments/<instrument_id>/series")
def instrument_series(instrument_id: str):
    args = request.args
    return jsonify(
        market.series(
            get_db(),
            g.user,
            instrument_id,
            range_key=args.get("range", "1M"),
            compare_id=args.get("compare") or None,
        )
    )


@market_bp.get("/observations")
def observations():
    args = request.args
    try:
        limit = int(args.get("limit", 100))
    except ValueError:
        raise ApiError(422, "invalid_limit", "limit must be an integer.")
    return jsonify(
        {
            "observations": market.list_observations(
                get_db(),
                g.user,
                instrument_id=args.get("instrument") or None,
                from_time=args.get("from") or None,
                to_time=args.get("to") or None,
                limit=limit,
            )
        }
    )


@market_bp.post("/observations")
@require_role("mi")
def create_observation():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request", "Expected a JSON object.")
    payload = market.create_observation(get_db(), g.user, body)
    return jsonify(payload), 201


@market_bp.get("/formulas")
def formulas():
    return jsonify({"formulas": market.list_formulas(get_db())})


@market_bp.post("/calculations/crack")
def calculate_crack():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request", "Expected a JSON object.")
    formula_id = body.get("formula_id")
    as_of = body.get("as_of")
    if not formula_id or not as_of:
        raise ApiError(422, "validation_error", "formula_id and as_of are required.")
    payload = market.calculate_crack(get_db(), g.user, formula_id, as_of)
    return jsonify(payload), 201
