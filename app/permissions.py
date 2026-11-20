"""The single authorization policy for BSR Market Intelligence.

Every read and write asks this module; routes and services never re-implement
classification rank, restricted access, export or admin checks.
"""

from __future__ import annotations

RANK = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}


def _get(row, key, default=None):
    if row is None:
        return default
    try:
        return row[key]
    except (KeyError, IndexError, TypeError):
        return default


def rank(classification: str | None) -> int:
    """Return the numeric rank of a classification; unknown values rank highest."""
    return RANK.get(str(classification or "").lower(), 99)


def can_read(row, user) -> bool:
    """True when the user may read this row, including the restricted rule."""
    if user is None:
        return False
    classification = str(_get(row, "classification", "") or "").lower()
    if rank(classification) > rank(_get(user, "max_classification")):
        return False
    if classification == "restricted" and not _get(user, "can_view_restricted", 0):
        return False
    return True


def visible_rows(rows, user) -> list:
    """Filter rows before serialization; the only sanctioned visibility helper."""
    return [row for row in rows if can_read(row, user)]


def can_export(user) -> bool:
    return bool(_get(user, "can_export", 0))


def is_admin(user) -> bool:
    return bool(_get(user, "is_admin", 0))


def permission_scope(user) -> dict:
    """The scope recorded on AI tasks and audit rows."""
    if user is None:
        return {
            "max_classification": None,
            "can_view_restricted": False,
            "can_export": False,
            "is_admin": False,
        }
    return {
        "max_classification": _get(user, "max_classification"),
        "can_view_restricted": bool(_get(user, "can_view_restricted", 0)),
        "can_export": can_export(user),
        "is_admin": is_admin(user),
    }
