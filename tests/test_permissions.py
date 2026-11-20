"""Policy and audit rules: rank, visibility, restricted access, append-only log."""

from __future__ import annotations

import pytest

from app.db import get_db
from app.permissions import (
    RANK,
    can_export,
    can_read,
    is_admin,
    permission_scope,
    rank,
    visible_rows,
)
from app.services.audit import record

LEADERSHIP = {
    "id": "u-lead",
    "role": "leadership",
    "max_classification": "restricted",
    "can_view_restricted": 1,
    "can_export": 0,
    "is_admin": 0,
}
MI = {
    "id": "u-mi",
    "role": "mi",
    "max_classification": "restricted",
    "can_view_restricted": 1,
    "can_export": 1,
    "is_admin": 1,
}
INTERNAL = {
    "id": "u-int",
    "role": "internal",
    "max_classification": "internal",
    "can_view_restricted": 0,
    "can_export": 0,
    "is_admin": 0,
}


def test_rank_matches_the_documented_order():
    assert [rank(value) for value in ("public", "internal", "confidential", "restricted")] == [
        0,
        1,
        2,
        3,
    ]
    assert rank("Internal") == 1
    assert rank(None) == 99
    assert rank("unknown") == 99
    assert RANK["restricted"] == 3


def test_internal_role_cannot_read_above_its_rank():
    assert can_read({"classification": "public"}, INTERNAL) is True
    assert can_read({"classification": "internal"}, INTERNAL) is True
    assert can_read({"classification": "confidential"}, INTERNAL) is False
    assert can_read({"classification": "restricted"}, INTERNAL) is False


def test_restricted_requires_both_rank_and_the_flag():
    no_flag = {**LEADERSHIP, "can_view_restricted": 0}
    assert can_read({"classification": "restricted"}, no_flag) is False
    assert can_read({"classification": "confidential"}, no_flag) is True
    assert can_read({"classification": "restricted"}, LEADERSHIP) is True


def test_no_user_reads_nothing():
    assert can_read({"classification": "public"}, None) is False


def test_visible_rows_filters_before_serialization():
    rows = [
        {"id": "1", "classification": "public"},
        {"id": "2", "classification": "internal"},
        {"id": "3", "classification": "confidential"},
        {"id": "4", "classification": "restricted"},
    ]
    assert [row["id"] for row in visible_rows(rows, INTERNAL)] == ["1", "2"]
    assert [row["id"] for row in visible_rows(rows, MI)] == ["1", "2", "3", "4"]
    assert visible_rows(rows, None) == []


def test_export_admin_and_scope_come_from_one_policy():
    assert can_export(MI) is True
    assert can_export(LEADERSHIP) is False
    assert is_admin(MI) is True
    assert is_admin(INTERNAL) is False
    assert permission_scope(MI) == {
        "max_classification": "restricted",
        "can_view_restricted": True,
        "can_export": True,
        "is_admin": True,
    }
    assert permission_scope(None)["max_classification"] is None


def test_audit_record_appends_and_keeps_prior_rows(app):
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO users (id, name, role, department, max_classification, "
            "can_view_restricted, can_export, is_admin, created_at) "
            "VALUES ('u-mi', 'Ha', 'mi', 'Market Intelligence', 'restricted', 1, 1, 1, '2026-11-14T00:00:00+00:00')"
        )
        db.commit()
        actor = db.execute("SELECT * FROM users WHERE id = 'u-mi'").fetchone()

        record(db, action="sign_in", result="succeeded", actor=actor)
        record(
            db,
            action="export_attempt",
            result="denied",
            actor=actor,
            object_type="report",
            object_id="R-1",
            classification="internal",
            detail="no export permission",
        )

        rows = db.execute("SELECT * FROM audit_log ORDER BY id").fetchall()
        assert len(rows) == 2
        assert rows[0]["action"] == "sign_in"
        assert rows[0]["actor_id"] == "u-mi"
        assert rows[0]["actor_role"] == "mi"
        assert rows[1]["action"] == "export_attempt"
        assert rows[1]["result"] == "denied"
        assert rows[1]["object_id"] == "R-1"
        assert rows[1]["classification"] == "internal"
        assert rows[1]["created_at"]
