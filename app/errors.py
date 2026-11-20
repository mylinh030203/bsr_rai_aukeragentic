"""API error type and Flask error registration."""

from __future__ import annotations

from flask import Flask, jsonify


class ApiError(Exception):
    """A controlled API failure with an HTTP status and stable code."""

    def __init__(self, status: int, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        body = {"error": {"code": self.code, "message": self.message}}
        if self.details:
            body["error"]["details"] = self.details
        return body


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(_error):
        return jsonify({"error": {"code": "bad_request", "message": "Malformed request."}}), 400

    @app.errorhandler(500)
    def server_error(_error):
        return (
            jsonify({"error": {"code": "internal_error", "message": "Unexpected server error."}}),
            500,
        )
