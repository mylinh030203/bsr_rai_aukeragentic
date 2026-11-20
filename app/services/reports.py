"""Reports: frozen content, immutable versions, source ledger and PDF export."""

from __future__ import annotations

import json
from datetime import datetime

from ..db import utc_now
from ..errors import ApiError
from ..permissions import can_export, can_read, rank, visible_rows
from . import pdf
from .audit import record, record_restricted_view


def _parse_date(value, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ApiError(422, "invalid_time", f"{field} must be an ISO 8601 timestamp.")
    if parsed.tzinfo is None:
        raise ApiError(422, "invalid_time", f"{field} must include a UTC offset.")
    return parsed


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def _version_payload(db, row) -> dict:
    sources = [
        {"kind": source["source_kind"], "id": source["source_id"], "label": source["label"]}
        for source in db.execute(
            "SELECT * FROM report_sources WHERE report_version_id = ? ORDER BY position",
            (row["id"],),
        )
    ]
    return {
        "version": row["version"],
        "content": json.loads(row["content"]),
        "data_cutoff": row["data_cutoff"],
        "requester_id": row["requester_id"],
        "created_at": row["created_at"],
        "sources": sources,
    }


def list_reports(db, user) -> list[dict]:
    rows = visible_rows(
        db.execute("SELECT * FROM reports ORDER BY created_at DESC, id").fetchall(), user
    )
    result = []
    for row in rows:
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "report", row["id"])
        latest = db.execute(
            "SELECT * FROM report_versions WHERE report_id = ? ORDER BY version DESC LIMIT 1",
            (row["id"],),
        ).fetchone()
        result.append(
            {
                "id": row["id"],
                "type": row["type"],
                "title": row["title"],
                "range_start": row["range_start"],
                "range_end": row["range_end"],
                "classification": row["classification"],
                "created_at": row["created_at"],
                "version": latest["version"] if latest is not None else None,
                "data_cutoff": latest["data_cutoff"] if latest is not None else None,
            }
        )
    return result


def _next_report_id(db) -> str:
    latest = db.execute(
        "SELECT MAX(CAST(SUBSTR(id, 8) AS INTEGER)) AS number FROM reports WHERE id LIKE 'R-%'"
    ).fetchone()
    number = (latest["number"] or 0) + 1
    return f"R-2026-{number:03d}"


def create_report(db, user, payload: dict) -> dict:
    report_type = str(payload.get("type") or "").strip()
    if not report_type:
        raise ApiError(422, "validation_error", "type is required.")
    range_start = _parse_date(payload.get("range_start"), "range_start")
    range_end = _parse_date(payload.get("range_end"), "range_end")
    if range_end < range_start:
        raise ApiError(422, "invalid_range", "range_end must be after range_start.")

    observations = visible_rows(
        db.execute(
            "SELECT * FROM market_observations WHERE market_time >= ? AND market_time <= ? "
            "ORDER BY market_time DESC LIMIT 50",
            (_iso(range_start), _iso(range_end)),
        ).fetchall(),
        user,
    )
    news_rows = visible_rows(
        db.execute(
            "SELECT * FROM news_items WHERE published_at >= ? AND published_at <= ? "
            "ORDER BY published_at DESC LIMIT 20",
            (_iso(range_start), _iso(range_end)),
        ).fetchall(),
        user,
    )

    classifications = [row["classification"] for row in observations] + [
        row["classification"] for row in news_rows
    ]
    classification = max(classifications, key=rank) if classifications else "internal"
    title = f"{report_type} - {range_start.date()} to {range_end.date()}"
    cutoff = utc_now()
    content = {
        "title": title,
        "summary": "Report generated from records the requester may read.",
        "generated_at": cutoff,
        "sections": [
            {
                "heading": "Market observations",
                "body": f"{len(observations)} permitted observations in range.",
                "items": [
                    {
                        "instrument_id": row["instrument_id"],
                        "value": row["value"],
                        "unit": row["unit"],
                        "market_time": row["market_time"],
                    }
                    for row in observations[:20]
                ],
            },
            {
                "heading": "News",
                "body": f"{len(news_rows)} permitted news items in range.",
                "items": [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "published_at": row["published_at"],
                    }
                    for row in news_rows[:10]
                ],
            },
        ],
    }

    report_id = _next_report_id(db)
    db.execute(
        "INSERT INTO reports (id, type, title, range_start, range_end, classification, "
        "created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            report_id,
            report_type,
            title,
            range_start.date().isoformat(),
            range_end.date().isoformat(),
            classification,
            user["id"],
            cutoff,
        ),
    )
    cursor = db.execute(
        "INSERT INTO report_versions (report_id, version, content, data_cutoff, requester_id, created_at) "
        "VALUES (?, 1, ?, ?, ?, ?)",
        (report_id, json.dumps(content), cutoff, user["id"], cutoff),
    )
    version_id = cursor.lastrowid
    seen = set()
    position = 0
    for observation in observations:
        if observation["source_id"] in seen:
            continue
        seen.add(observation["source_id"])
        db.execute(
            "INSERT INTO report_sources (report_version_id, source_kind, source_id, label, position) "
            "VALUES (?, 'observation_source', ?, ?, ?)",
            (version_id, observation["source_id"], observation["source_id"], position),
        )
        position += 1
    for news in news_rows:
        db.execute(
            "INSERT INTO report_sources (report_version_id, source_kind, source_id, label, position) "
            "VALUES (?, 'news', ?, ?, ?)",
            (version_id, news["id"], news["title"], position),
        )
        position += 1
    db.commit()
    record(
        db,
        action="report_generated",
        result="succeeded",
        actor=user,
        object_type="report",
        object_id=report_id,
        classification=classification,
        detail="version 1",
    )
    return get_report(db, user, report_id)


def get_report(db, user, report_id: str) -> dict:
    row = db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if row is None or not can_read(row, user):
        raise ApiError(404, "not_found", "Report not found.")
    if row["classification"] == "restricted":
        record_restricted_view(db, user, "report", report_id)
    versions = [
        _version_payload(db, version)
        for version in db.execute(
            "SELECT * FROM report_versions WHERE report_id = ? ORDER BY version DESC",
            (report_id,),
        )
    ]
    return {
        "id": row["id"],
        "type": row["type"],
        "title": row["title"],
        "range_start": row["range_start"],
        "range_end": row["range_end"],
        "classification": row["classification"],
        "created_at": row["created_at"],
        "requester_id": row["created_by"],
        "versions": versions,
    }


def export_pdf(db, user, report_id: str) -> bytes:
    report = get_report(db, user, report_id)
    if not can_export(user):
        record(
            db,
            action="export_attempt",
            result="denied",
            actor=user,
            object_type="report",
            object_id=report_id,
            classification=report["classification"],
            detail="no export permission",
        )
        raise ApiError(403, "export_denied", "Your role cannot export reports.")
    latest = report["versions"][0]["content"] if report["versions"] else {}
    lines = [
        report["title"],
        f"Type: {report['type']}",
        f"Range: {report['range_start']} to {report['range_end']}",
        f"Classification: {report['classification']}",
        f"Data cut-off: {report['versions'][0]['data_cutoff'] if report['versions'] else ''}",
        "",
        str(latest.get("summary") or ""),
        "",
    ]
    for section in latest.get("sections", []):
        lines.append(str(section.get("heading") or ""))
        lines.append(str(section.get("body") or ""))
        for item in section.get("items", []):
            if "title" in item:
                lines.append(f"- {item['title']}")
            else:
                lines.append(
                    f"- {item.get('instrument_id')}: {item.get('value')} {item.get('unit')} "
                    f"at {item.get('market_time')}"
                )
        lines.append("")
    if report["versions"]:
        lines.append("Sources")
        for source in report["versions"][0]["sources"]:
            lines.append(f"- {source['id']}: {source['label']}")
    record(
        db,
        action="export_attempt",
        result="allowed",
        actor=user,
        object_type="report",
        object_id=report_id,
        classification=report["classification"],
    )
    return pdf.build_pdf(lines)
