"""Production configuration gate and release backup behavior."""

from __future__ import annotations

import sqlite3

import pytest

from app import create_app
from app.config import (
    ConfigurationError,
    DEV_SECRET_FALLBACK,
    load_config,
    validate_production_config,
)

PRODUCTION = {
    "ENV": "production",
    "SECRET_KEY": "a" * 48,
    "SESSION_COOKIE_SECURE": True,
}


def _production(**overrides) -> dict:
    return {**PRODUCTION, **overrides}


def test_development_config_needs_no_secret(monkeypatch):
    monkeypatch.delenv("BSR_SECRET_KEY", raising=False)
    monkeypatch.setenv("BSR_ENV", "development")
    validate_production_config(load_config())


def test_production_rejects_the_development_fallback_secret():
    with pytest.raises(ConfigurationError, match="placeholder"):
        validate_production_config(_production(SECRET_KEY=DEV_SECRET_FALLBACK))


@pytest.mark.parametrize(
    "secret",
    [
        "replace-me-with-a-long-random-value",
        "replace-me-with-something-i-invented",
        "local-demo-secret-not-for-a-real-host",
        "changeme",
    ],
)
def test_production_rejects_documented_placeholder_secrets(secret):
    with pytest.raises(ConfigurationError, match="placeholder"):
        validate_production_config(_production(SECRET_KEY=secret))


def test_production_reports_a_missing_secret_as_missing():
    """An unset key must not be reported as a placeholder: the fixes differ."""
    for secret in ("", None):
        with pytest.raises(ConfigurationError, match="is not set"):
            validate_production_config(_production(SECRET_KEY=secret))


def test_production_rejects_a_short_secret():
    with pytest.raises(ConfigurationError, match="at least 32 characters"):
        validate_production_config(_production(SECRET_KEY="short-secret"))


def test_production_requires_secure_cookies():
    with pytest.raises(ConfigurationError, match="SESSION_COOKIE_SECURE"):
        validate_production_config(_production(SESSION_COOKIE_SECURE=False))


def test_production_with_a_real_secret_is_accepted():
    validate_production_config(_production())


def test_create_app_refuses_to_build_a_production_app_without_a_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("BSR_ENV", "production")
    monkeypatch.delenv("BSR_SECRET_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="is not set"):
        create_app({"DATABASE": str(tmp_path / "prod.db"), "SEED_ON_START": False})


def test_create_app_refuses_a_placeholder_secret_supplied_by_the_caller(tmp_path):
    with pytest.raises(ConfigurationError, match="placeholder"):
        create_app(
            {
                "ENV": "production",
                "SECRET_KEY": "local-demo-secret-not-for-a-real-host",
                "SESSION_COOKIE_SECURE": True,
                "DATABASE": str(tmp_path / "prod.db"),
                "SEED_ON_START": False,
            }
        )


def test_create_app_builds_a_production_app_with_a_real_secret(tmp_path):
    app = create_app(
        {
            "ENV": "production",
            "SECRET_KEY": "b" * 48,
            "SESSION_COOKIE_SECURE": True,
            "DATABASE": str(tmp_path / "prod.db"),
            "SEED_ON_START": False,
        }
    )
    assert app.config["ENV"] == "production"


def test_production_login_cookie_is_secure_over_plain_http(tmp_path):
    """HTTP is served behind a TLS-terminating proxy, so the flag cannot follow the scheme."""
    app = create_app(
        {
            "ENV": "production",
            "SECRET_KEY": "c" * 48,
            "SESSION_COOKIE_SECURE": True,
            "DATABASE": str(tmp_path / "prod.db"),
            "SEED_ON_START": False,
        }
    )
    # Production never seeds, so the account is created here explicitly.
    with app.app_context():
        from app.db import get_db

        db = get_db()
        db.execute(
            "INSERT INTO users (id, name, role, department, max_classification, "
            "can_view_restricted, can_export, is_admin, created_at) "
            "VALUES ('u-prod', 'Production User', 'mi', 'Market Intelligence', "
            "'restricted', 1, 1, 1, '2026-11-15T00:00:00+00:00')"
        )
        db.commit()
    response = app.test_client().post("/api/auth/session", json={"role": "mi"})
    assert response.status_code == 201, response.get_json()
    set_cookie = response.headers["Set-Cookie"]
    assert "Secure" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=Lax" in set_cookie


def test_production_does_not_seed_demo_data_by_default(monkeypatch, tmp_path):
    monkeypatch.setenv("BSR_ENV", "production")
    monkeypatch.delenv("BSR_SEED_ON_START", raising=False)
    assert load_config()["SEED_ON_START"] is False
    app = create_app(
        {
            "SECRET_KEY": "d" * 48,
            "SESSION_COOKIE_SECURE": True,
            "DATABASE": str(tmp_path / "prod.db"),
        }
    )
    with app.app_context():
        from app.db import get_db

        assert get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0


def test_production_never_seeds_even_when_the_flag_is_forced_on(tmp_path):
    """A stray BSR_SEED_ON_START must not create passwordless demo accounts."""
    app = create_app(
        {
            "ENV": "production",
            "SECRET_KEY": "e" * 48,
            "SESSION_COOKIE_SECURE": True,
            "DATABASE": str(tmp_path / "prod.db"),
            "SEED_ON_START": True,
        }
    )
    with app.app_context():
        from app.db import get_db

        assert get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0


# --- backup ---------------------------------------------------------------


@pytest.fixture()
def live_db(tmp_path):
    path = tmp_path / "live.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
        conn.execute("INSERT INTO t (v) VALUES ('kept')")
        conn.commit()
    return path


def _backup_module():
    import importlib.util
    from pathlib import Path

    module_path = Path(__file__).resolve().parents[1] / "scripts" / "backup_db.py"
    spec = importlib.util.spec_from_file_location("backup_db", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_backup_copies_rows_and_verifies_integrity(live_db, tmp_path):
    module = _backup_module()
    destination = module.backup(live_db, tmp_path / "copy.db")
    with sqlite3.connect(destination) as conn:
        assert conn.execute("SELECT v FROM t").fetchone()[0] == "kept"


def test_backup_refuses_to_overwrite_an_existing_copy(live_db, tmp_path):
    module = _backup_module()
    destination = tmp_path / "copy.db"
    destination.write_bytes(b"previous")
    with pytest.raises(module.BackupError, match="already exists"):
        module.backup(live_db, destination)
    assert destination.read_bytes() == b"previous"

    module.backup(live_db, destination, force=True)
    with sqlite3.connect(destination) as conn:
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1


def test_failed_backup_leaves_no_partial_file(tmp_path, monkeypatch):
    """A copy that fails the integrity check must not land at the destination."""
    module = _backup_module()
    source = tmp_path / "live.db"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY)")
        conn.commit()
    destination = tmp_path / "copy.db"
    staging = destination.with_name(destination.name + ".partial")

    def corrupt_check(_connection):
        return "corrupt"

    monkeypatch.setattr(module, "verify_integrity", corrupt_check)
    with pytest.raises(module.BackupError, match="integrity"):
        module.backup(source, destination)
    assert not destination.exists()
    assert not staging.exists()
    assert not staging.with_name(staging.name + "-wal").exists()
