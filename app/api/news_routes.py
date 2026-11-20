"""News routes: feed, detail, intake, upload, feedback, coverage."""

from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from ..auth import rate_limit, require_role
from ..db import get_db
from ..errors import ApiError
from ..services import news

news_bp = Blueprint("news", __name__)


@news_bp.get("/news")
def feed():
    args = request.args
    return jsonify(
        {
            "news": news.list_news(
                get_db(),
                g.user,
                topic=args.get("topic") or None,
                source=args.get("source") or None,
                from_time=args.get("from") or None,
                to_time=args.get("to") or None,
                status=args.get("status") or None,
                query=args.get("q") or None,
            )
        }
    )


@news_bp.get("/news/coverage")
def coverage():
    event_id = request.args.get("event_id")
    if not event_id:
        raise ApiError(422, "validation_error", "event_id is required.")
    return jsonify(news.coverage(get_db(), g.user, event_id))


@news_bp.get("/news/<news_id>")
def detail(news_id: str):
    return jsonify(news.get_news(get_db(), g.user, news_id))


@news_bp.post("/news")
@require_role("mi")
def create_news():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request", "Expected a JSON object.")
    return jsonify(news.create_news(get_db(), g.user, body)), 201


@news_bp.post("/news/upload")
@require_role("mi")
def upload_news():
    rate_limit("upload", g.user["id"])
    file_storage = request.files.get("file")
    if file_storage is None:
        raise ApiError(422, "validation_error", "The multipart field 'file' is required.")
    payload = news.create_news_from_upload(get_db(), g.user, file_storage, request.form)
    return jsonify(payload), 201


@news_bp.post("/news/<news_id>/feedback")
def add_feedback(news_id: str):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request", "Expected a JSON object.")
    return jsonify(news.add_feedback(get_db(), g.user, news_id, body)), 201
