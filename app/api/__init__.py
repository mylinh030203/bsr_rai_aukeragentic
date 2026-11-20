"""API blueprint registration."""

from __future__ import annotations

from flask import Blueprint, jsonify

from ..db import get_db
from .admin_routes import admin_bp
from .assistant_routes import assistant_bp
from .auth_routes import auth_bp
from .forecast_routes import forecast_bp
from .intel_routes import intel_bp
from .market_routes import market_bp
from .news_routes import news_bp
from .report_routes import report_bp

api_bp = Blueprint("api", __name__)
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(market_bp)
api_bp.register_blueprint(news_bp)
api_bp.register_blueprint(forecast_bp)
api_bp.register_blueprint(assistant_bp)
api_bp.register_blueprint(intel_bp)
api_bp.register_blueprint(report_bp)
api_bp.register_blueprint(admin_bp)


@api_bp.get("/health")
def health():
    db = get_db()
    db.execute("SELECT 1").fetchone()
    return jsonify({"status": "ok", "db": "ok"})
