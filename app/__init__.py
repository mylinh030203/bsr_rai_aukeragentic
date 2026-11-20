"""BSR Market Intelligence application factory."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .auth import init_auth
from .config import load_config, validate_production_config
from .db import apply_migrations, close_db, get_db
from .errors import ApiError, register_error_handlers


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(Path(__file__).resolve().parent / "static"),
        static_url_path="",
    )
    app.config.from_mapping(load_config())
    if test_config:
        app.config.update(test_config)

    # Every entry point builds the app here, so a production process cannot
    # start with a placeholder secret regardless of how it is launched.
    validate_production_config(app.config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(close_db)

    with app.app_context():
        apply_migrations(get_db(), Path(app.config["MIGRATIONS_DIR"]))
        # Synthetic demo accounts accept passwordless role sign-in, so demo data
        # is never written by a production process even if seeding is forced on
        # through a stray environment variable.
        if app.config.get("SEED_ON_START") and app.config.get("ENV") != "production":
            from .services.seed import seed

            seed(get_db())

    register_error_handlers(app)
    init_auth(app)

    from .api import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'",
        )
        return response

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify(error.to_dict()), error.status

    @app.errorhandler(413)
    def handle_too_large(_error):
        limit_mb = int(app.config["MAX_CONTENT_LENGTH"]) // (1024 * 1024)
        return (
            jsonify(
                {
                    "error": {
                        "code": "payload_too_large",
                        "message": f"Request body exceeds the {limit_mb} MB limit.",
                    }
                }
            ),
            413,
        )

    @app.errorhandler(404)
    def handle_not_found(error):
        if request.path.startswith("/api/"):
            return (
                jsonify({"error": {"code": "not_found", "message": "Resource not found."}}),
                404,
            )
        return error

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {"error": {"code": "method_not_allowed", "message": "Method not allowed."}}
                ),
                405,
            )
        return error

    return app
