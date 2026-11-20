"""Environment-driven application settings."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEV_SECRET_FALLBACK = "dev-only-not-for-production"

RATE_LIMITS = {
    "login": {"limit": 10, "window_seconds": 300},
    "assistant": {"limit": 20, "window_seconds": 300},
    "upload": {"limit": 10, "window_seconds": 300},
    "export": {"limit": 10, "window_seconds": 300},
}


class ConfigurationError(RuntimeError):
    """Raised when a production start is missing a safe setting."""


def _rate_limits() -> dict:
    limits = {}
    for action, settings in RATE_LIMITS.items():
        limits[action] = {
            "limit": int(os.environ.get(f"BSR_RATE_LIMIT_{action.upper()}", settings["limit"])),
            "window_seconds": settings["window_seconds"],
        }
    return limits


def _env_flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def load_config() -> dict:
    """Return the default configuration for the application factory."""
    environment = os.environ.get("BSR_ENV", "development").strip().lower()
    production = environment == "production"
    # Demo data is useful on a workstation and dangerous on a shared host, so a
    # production process never seeds unless it is explicitly asked to.
    seed_default = not production
    return {
        "ENV": environment,
        # A production process gets no fallback secret, so the validator can tell
        # "not set" (its own message) from "set to a placeholder value".
        "SECRET_KEY": os.environ.get(
            "BSR_SECRET_KEY", None if production else DEV_SECRET_FALLBACK
        ),
        "DATABASE": os.environ.get("BSR_DATABASE", str(PROJECT_ROOT / "instance" / "bsr.db")),
        "MIGRATIONS_DIR": str(PROJECT_ROOT / "migrations"),
        "SESSION_COOKIE_NAME": "bsr_session",
        "SESSION_TTL_SECONDS": 8 * 3600,
        # Cookies are always issued with these flags; the login route adds
        # `Secure` whenever the request arrives over HTTPS.
        "SESSION_COOKIE_SECURE": production,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_HTTPONLY": True,
        "MAX_CONTENT_LENGTH": 6 * 1024 * 1024,
        "MAX_UPLOAD_BYTES": 5 * 1024 * 1024,
        "ALLOWED_UPLOAD_EXTENSIONS": (".csv", ".xlsx", ".pdf", ".doc", ".docx"),
        "SEED_ON_START": _env_flag("BSR_SEED_ON_START", seed_default),
        "RATE_LIMITS": _rate_limits(),
        "JSON_SORT_KEYS": False,
    }


MIN_SECRET_LENGTH = 32

# Values a copy-pasted deployment guide leaves behind. Matching any of them
# means nobody chose a secret, so the start is refused.
PLACEHOLDER_SECRETS = frozenset(
    {
        DEV_SECRET_FALLBACK,
        "replace-me-with-a-long-random-value",
        "local-demo-secret-not-for-a-real-host",
        "changeme",
    }
)


def validate_production_config(config: dict) -> None:
    """Refuse to serve production traffic with demo-grade security settings.

    `create_app` calls this whenever ENV is production, so every entry point
    (waitress, gunicorn, `flask run`, Docker) is covered. Tests and the
    development server use ENV=development and need no secret.
    """
    if config.get("ENV") != "production":
        return
    raw_secret = config.get("SECRET_KEY")
    if raw_secret is None or raw_secret == "":
        raise ConfigurationError(
            "BSR_SECRET_KEY is not set; set a random value when BSR_ENV=production "
            "(python -c \"import secrets; print(secrets.token_urlsafe(48))\")."
        )
    secret = str(raw_secret)
    # The development fallback is a placeholder too, so it is reported as one:
    # an unset variable never reaches this branch.
    if secret in PLACEHOLDER_SECRETS or secret.startswith("replace-me"):
        raise ConfigurationError(
            "BSR_SECRET_KEY is still a documented placeholder; set a random value "
            "when BSR_ENV=production."
        )
    if len(secret) < MIN_SECRET_LENGTH:
        raise ConfigurationError(
            f"BSR_SECRET_KEY must be at least {MIN_SECRET_LENGTH} characters when "
            "BSR_ENV=production; generate one with secrets.token_urlsafe(48)."
        )
    if not config.get("SESSION_COOKIE_SECURE"):
        raise ConfigurationError(
            "SESSION_COOKIE_SECURE must be on when BSR_ENV=production; serve behind HTTPS."
        )
