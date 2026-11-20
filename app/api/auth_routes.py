"""Session endpoints: demo sign-in, current user, sign-out."""

from __future__ import annotations

from flask import Blueprint, current_app, g, jsonify, request

from ..auth import COOKIE_NAME, create_session, rate_limit, revoke_session, user_payload
from ..db import get_db
from ..errors import ApiError
from ..services.audit import record

auth_bp = Blueprint("auth", __name__)

VALID_ROLES = ("leadership", "mi", "internal")


@auth_bp.post("/auth/session")
def create_session_route():
    rate_limit("login", request.remote_addr or "unknown")
    body = request.get_json(silent=True) or {}
    role = body.get("role")
    if role not in VALID_ROLES:
        raise ApiError(422, "invalid_role", "role must be leadership, mi or internal.")
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE role = ? ORDER BY created_at, id LIMIT 1", (role,)
    ).fetchone()
    if user is None:
        raise ApiError(401, "unknown_demo_role", "No demo account exists for this role.")
    token, csrf_token = create_session(user["id"])
    record(db, action="sign_in", result="succeeded", actor=user)
    response = jsonify({"user": user_payload(user), "csrf_token": csrf_token})
    response.status_code = 201
    # A production process always marks the cookie Secure; otherwise the flag
    # follows the request scheme so local HTTP development still works.
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=int(current_app.config["SESSION_TTL_SECONDS"]),
        httponly=bool(current_app.config["SESSION_COOKIE_HTTPONLY"]),
        samesite=current_app.config["SESSION_COOKIE_SAMESITE"],
        secure=request.is_secure or bool(current_app.config["SESSION_COOKIE_SECURE"]),
        path="/",
    )
    return response


@auth_bp.get("/me")
def me():
    return jsonify({"user": user_payload(g.user), "csrf_token": g.session["csrf_token"]})


@auth_bp.delete("/auth/session")
def delete_session_route():
    token = request.cookies.get(current_app.config["SESSION_COOKIE_NAME"])
    revoke_session(token)
    record(get_db(), action="sign_out", result="succeeded", actor=g.user)
    response = jsonify({})
    response.status_code = 204
    response.delete_cookie(COOKIE_NAME, path="/")
    return response
