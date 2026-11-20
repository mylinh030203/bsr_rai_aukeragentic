#!/usr/bin/env python
"""Consistent backup of the SQLite database while the app is running.

    python scripts/backup_db.py instance/bsr.db backups/bsr-2026-11-15.db

Uses SQLite's online backup API, so the copy is transactionally consistent even
with the WAL active; a plain file copy of a live database can miss the WAL. The
copy is written to a temporary file, integrity-checked there, and only then
moved into place, so a failed run never leaves a corrupt file at the
destination. An existing destination is refused unless --force is passed.
"""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


class BackupError(RuntimeError):
    """Raised when a backup cannot be produced or does not verify."""


def verify_integrity(destination: sqlite3.Connection) -> str:
    """Return SQLite's integrity_check verdict for the copy being written."""
    return destination.execute("PRAGMA integrity_check").fetchone()[0]


def backup(source: Path, destination: Path, force: bool = False) -> Path:
    if not source.exists():
        raise BackupError(f"database not found: {source}")
    if destination.exists() and not force:
        raise BackupError(f"destination already exists: {destination} (pass --force to replace)")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(destination.name + ".partial")
    for leftover in (staging, staging.with_name(staging.name + "-wal"), staging.with_name(staging.name + "-shm")):
        if leftover.exists():
            leftover.unlink()
    try:
        # sqlite3's context manager commits but never closes, and Windows keeps
        # a moved file locked while a handle is open, so both connections are
        # closed explicitly and the copy is left in rollback-journal mode so no
        # -wal/-shm siblings can stay behind holding the staging path.
        src = sqlite3.connect(source)
        dst = sqlite3.connect(staging)
        try:
            src.backup(dst)
            dst.execute("PRAGMA journal_mode=DELETE").fetchone()
            check = verify_integrity(dst)
        finally:
            dst.close()
            src.close()
        if check != "ok":
            raise BackupError(f"backup failed integrity check: {check}")
        os.replace(staging, destination)
    except BaseException:
        for leftover in (staging, staging.with_name(staging.name + "-wal"), staging.with_name(staging.name + "-shm")):
            try:
                leftover.unlink(missing_ok=True)
            except PermissionError:
                pass
        raise
    return destination


def default_destination(root: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return root / "backups" / f"bsr-{stamp}.db"


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent.parent
    args = [arg for arg in argv[1:] if arg != "--force"]
    force = "--force" in argv[1:]
    source = Path(args[0]) if args else root / "instance" / "bsr.db"
    destination = Path(args[1]) if len(args) > 1 else default_destination(root)
    try:
        written = backup(source, destination, force=force)
    except BackupError as error:
        print(f"backup failed: {error}", file=sys.stderr)
        return 1
    print(f"backup written: {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
