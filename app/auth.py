"""Server-side sessions, double-submit CSRF and rate limits."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timezone

from flask import current_app, g, request

from .db import get_db, utc_now
from .errors import ApiError

COOKIE_NAME = "bsr_session"
PUBLIC_API_PATHS = {"/api/health", "/api/auth/session"}


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def user_payload(row) -> dict:
    """The public user shape from docs/API.md."""
    return {
        "id": row["id"],
        "name": row["name"],
        "role": row["role"],
        "department": row["department"],
        "max_classification": row["max_classification"],
        "can_view_restricted": bool(row["can_view_restricted"]),
        "can_export": bool(row["can_export"]),
        "is_admin": bool(row["is_admin"]),
    }


def create_session(user_id: str) -> tuple[str, str]:
    """Issue a new opaque session; only the SHA-256 hash is stored."""
    db = get_db()
    token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(24)
    ttl = int(current_app.config["SESSION_TTL_SECONDS"])
    now = datetime.now(timezone.utc)
    expires = datetime.fromtimestamp(now.timestamp() + ttl, timezone.utc)
    db.execute(
        "INSERT INTO sessions (token_hash, user_id, csrf_token, created_at, expires_at, last_seen_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            hash_token(token),
            user_id,
            csrf_token,
            now.isoformat(timespec="seconds"),
            expires.isoformat(timespec="seconds"),
            now.isoformat(timespec="seconds"),
        ),
    )
    db.execute("DELETE FROM sessions WHERE expires_at <= ?", (utc_now(),))
    db.commit()
    return token, csrf_token


def resolve_session(token: str | None):
    """Return the session row joined with its user, or None when missing/expired."""
    if not token:
        return None
    db = get_db()
    row = db.execute(
        "SELECT s.token_hash, s.csrf_token, s.expires_at, s.user_id, "
        "u.id, u.name, u.role, u.department, u.max_classification, "
        "u.can_view_restricted, u.can_export, u.is_admin "
        "FROM sessions s JOIN users u ON u.id = s.user_id "
        "WHERE s.token_hash = ? AND s.expires_at > ?",
        (hash_token(token), utc_now()),
    ).fetchone()
    if row is None:
        return None
    db.execute(
        "UPDATE sessions SET last_seen_at = ? WHERE token_hash = ?",
        (utc_now(), row["token_hash"]),
    )
    db.commit()
    return row


def revoke_session(token: str | None) -> None:
    if not token:
        return
    db = get_db()
    db.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(token),))
    db.commit()


def check_csrf(session, provided: str | None) -> bool:
    if session is None or not provided:
        return False
    return hmac.compare_digest(session["csrf_token"], provided)


def rate_limit(action: str, scope: str) -> None:
    """Atomically count one attempt; raise 429 when the window limit is exceeded."""
    limits = current_app.config["RATE_LIMITS"]
    if action not in limits:
        raise KeyError(f"unknown rate limit action {action}")
    limit = int(limits[action]["limit"])
    window = int(limits[action]["window_seconds"])
    now = int(time.time())
    window_start = now - (now % window)
    key = f"{action}:{scope}:{window_start}"
    expires = datetime.fromtimestamp(window_start + window, timezone.utc)
    db = get_db()
    row = db.execute(
        "INSERT INTO rate_limits (limit_key, count, window_start, expires_at) VALUES (?, 1, ?, ?) "
        "ON CONFLICT(limit_key) DO UPDATE SET count = count + 1 RETURNING count",
        (key, datetime.fromtimestamp(window_start, timezone.utc).isoformat(), expires.isoformat()),
    ).fetchone()
    db.execute("DELETE FROM rate_limits WHERE expires_at <= ?", (utc_now(),))
    db.commit()
    if row[0] > limit:
        raise ApiError(429, "rate_limited", "Too many attempts. Try again later.")


def require_role(*roles: str):
    """Decorator for actions limited to specific roles."""

    def decorator(view):
        def wrapped(*args, **kwargs):
            user = getattr(g, "user", None)
            if user is None:
                raise ApiError(401, "unauthorized", "Sign in required.")
            if user["role"] not in roles:
                raise ApiError(403, "forbidden", "Your role cannot perform this action.")
            return view(*args, **kwargs)

        wrapped.__name__ = view.__name__
        return wrapped

    return decorator


def require_admin(view):
    """Decorator for administration endpoints."""

    def wrapped(*args, **kwargs):
        user = getattr(g, "user", None)
        if user is None:
            raise ApiError(401, "unauthorized", "Sign in required.")
        if not user["is_admin"]:
            raise ApiError(403, "forbidden", "Administration requires an admin account.")
        return view(*args, **kwargs)

    wrapped.__name__ = view.__name__
    return wrapped


def load_request_identity() -> None:
    """Resolve the session cookie before every request and enforce CSRF."""
    g.user = None
    g.session = None
    g.session_token = None

    if not request.path.startswith("/api/"):
        return

    if request.url_rule is None or request.endpoint == "static":
        # Unknown route (the static catch-all matches /api/* too): let Flask
        # answer with the documented 404 shape instead of a misleading 401.
        return

    token = request.cookies.get(current_app.config["SESSION_COOKIE_NAME"])
    row = resolve_session(token)
    if row is not None:
        g.session_token = token
        g.session = {"token_hash": row["token_hash"], "csrf_token": row["csrf_token"]}
        g.user = row

    if request.path in PUBLIC_API_PATHS:
        if request.path == "/api/health" or request.method == "POST":
            return

    if g.user is None:
        raise ApiError(401, "unauthorized", "Sign in required.")

    if request.method not in ("GET", "HEAD", "OPTIONS"):
        if not check_csrf(g.session, request.headers.get("X-CSRF-Token")):
            raise ApiError(403, "csrf_failed", "CSRF token missing or invalid.")


def init_auth(app) -> None:
    app.before_request(load_request_identity)
