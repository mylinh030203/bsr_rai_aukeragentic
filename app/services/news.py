"""News intelligence service: feed, intake, processing, feedback, coverage."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone

from flask import current_app

from ..db import utc_now
from ..errors import ApiError
from ..permissions import can_read, rank, visible_rows
from . import ai_runs
from .audit import record, record_restricted_view

CLASSIFICATIONS = ("public", "internal", "confidential", "restricted")
FEEDBACK_KINDS = ("important", "comment")
DUPLICATE_THRESHOLD = 0.6


def _parse_time(value, field: str = "published_at") -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ApiError(422, "invalid_time", f"{field} must be an ISO 8601 timestamp.")
    if parsed.tzinfo is None:
        raise ApiError(422, "invalid_time", f"{field} must include a UTC offset.")
    return parsed


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def _topics_for(db, news_id: str) -> list[str]:
    return [
        row["label"]
        for row in db.execute(
            "SELECT t.label FROM news_topics nt JOIN topics t ON t.id = nt.topic_id "
            "WHERE nt.news_id = ? ORDER BY t.label",
            (news_id,),
        )
    ]


def _topic_id(label: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"t-{slug}"


def _ensure_topic(db, label: str) -> str:
    existing = db.execute("SELECT id FROM topics WHERE label = ?", (label,)).fetchone()
    if existing is not None:
        return existing["id"]
    topic_id = _topic_id(label)
    if db.execute("SELECT id FROM topics WHERE id = ?", (topic_id,)).fetchone() is not None:
        topic_id = f"{topic_id}-{hashlib.md5(label.encode('utf-8')).hexdigest()[:6]}"
    db.execute("INSERT INTO topics (id, label) VALUES (?, ?)", (topic_id, label))
    return topic_id


def news_payload(db, row, user=None) -> dict:
    source = db.execute("SELECT name FROM sources WHERE id = ?", (row["source_id"],)).fetchone()
    return {
        "id": row["id"],
        "title": row["title"],
        "source": {"id": row["source_id"], "name": source["name"] if source else row["source_id"]},
        "published_at": row["published_at"],
        "ingested_at": row["ingested_at"],
        "body": row["body"],
        "summary": row["summary"],
        "insight": row["insight"],
        "classification": row["classification"],
        "processing_status": row["processing_status"],
        "relevance": row["relevance"],
        "duplicate_of": row["duplicate_of"],
        "coverage_note": row["coverage_note"],
        "topics": _topics_for(db, row["id"]),
        "instruments": [
            item["instrument_id"]
            for item in db.execute(
                "SELECT instrument_id FROM news_instruments WHERE news_id = ? ORDER BY instrument_id",
                (row["id"],),
            )
        ],
    }


def list_news(
    db,
    user,
    topic: str | None = None,
    source: str | None = None,
    from_time: str | None = None,
    to_time: str | None = None,
    status: str | None = None,
    query: str | None = None,
) -> list[dict]:
    sql = "SELECT * FROM news_items WHERE 1 = 1"
    params: list = []
    if topic:
        sql += " AND id IN (SELECT nt.news_id FROM news_topics nt JOIN topics t ON t.id = nt.topic_id WHERE t.label = ?)"
        params.append(topic)
    if source:
        sql += " AND source_id = ?"
        params.append(source)
    if from_time:
        sql += " AND published_at >= ?"
        params.append(_iso(_parse_time(from_time, "from")))
    if to_time:
        sql += " AND published_at <= ?"
        params.append(_iso(_parse_time(to_time, "to")))
    if status:
        sql += " AND processing_status = ?"
        params.append(status)
    if query:
        sql += " AND (title LIKE ? OR body LIKE ? OR summary LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
    sql += " ORDER BY published_at DESC, id"
    rows = visible_rows(db.execute(sql, params).fetchall(), user)
    for row in rows:
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "news_item", row["id"])
    return [news_payload(db, row, user) for row in rows]


def get_news(db, user, news_id: str) -> dict:
    row = db.execute("SELECT * FROM news_items WHERE id = ?", (news_id,)).fetchone()
    if row is None or not can_read(row, user):
        raise ApiError(404, "not_found", "News item not found.")
    if row["classification"] == "restricted":
        record_restricted_view(db, user, "news_item", row["id"])
    payload = news_payload(db, row, user)
    payload["feedback"] = [
        {
            "id": feedback["id"],
            "kind": feedback["kind"],
            "body": feedback["body"],
            "user_id": feedback["user_id"],
            "created_at": feedback["created_at"],
        }
        for feedback in db.execute(
            "SELECT * FROM news_feedback WHERE news_id = ? ORDER BY created_at",
            (news_id,),
        )
    ]
    return payload


def _extract_topics(title: str, body: str) -> list[str]:
    text = f"{title} {body}".lower()
    topics = []
    rules = [
        ("opec", "OPEC+"),
        ("freight", "Shipping & freight"),
        ("red sea", "Shipping & freight"),
        ("inventor", "Inventory"),
        ("refin", "Refining operations"),
        ("dung quat", "Refining operations"),
        ("gasoline", "Refined products"),
        ("diesel", "Refined products"),
        ("crude", "Crude supply"),
        ("brent", "Crude supply"),
    ]
    for needle, label in rules:
        if needle in text and label not in topics:
            topics.append(label)
    return topics


def _normalized_tokens(title: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", title.lower()) if len(token) > 2}


def _duplicate_of(db, title: str) -> str | None:
    candidate = _normalized_tokens(title)
    if not candidate:
        return None
    for row in db.execute("SELECT id, title FROM news_items ORDER BY published_at DESC LIMIT 100"):
        other = _normalized_tokens(row["title"])
        if not other:
            continue
        overlap = len(candidate & other) / len(candidate | other)
        if overlap >= DUPLICATE_THRESHOLD:
            return row["id"]
    return None


def _next_news_id(db) -> str:
    latest = db.execute(
        "SELECT MAX(CAST(SUBSTR(id, 3) AS INTEGER)) AS number FROM news_items WHERE id LIKE 'N-%'"
    ).fetchone()
    number = (latest["number"] or 0) + 1
    return f"N-{number}"


def _process_and_store(
    db,
    user,
    *,
    title: str,
    body: str,
    source_id: str,
    published_at: str,
    classification: str,
    topics: list[str],
    instrument_ids: list[str],
    coverage_note: str | None,
) -> dict:
    source = db.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
    if source is None:
        raise ApiError(422, "invalid_source", "source_id does not exist.")
    if classification not in CLASSIFICATIONS:
        raise ApiError(422, "invalid_classification", "Unknown classification.")
    if rank(classification) > rank(user["max_classification"]):
        raise ApiError(422, "classification_above_user", "Classification exceeds your access.")
    published = _parse_time(published_at)
    if published > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ApiError(422, "future_publish_time", "published_at cannot be in the future.")

    labels = topics or _extract_topics(title, body)
    task_input = {"title": title, "body": body, "topics": labels}
    execution = ai_runs.execute(
        db,
        task_type="news_summarization",
        user=user,
        task_input=task_input,
        context=task_input,
    )
    output = execution["output"]
    if execution["status"] != "succeeded":
        summary = body[:180]
        insight = "AI interpretation unavailable; source content retained."
        relevance = None
    else:
        summary = output.get("summary")
        insight = output.get("insight")
        relevance = output.get("relevance")

    duplicate_of = _duplicate_of(db, title)
    status = "duplicate_candidate" if duplicate_of else "processed"
    news_id = _next_news_id(db)
    db.execute(
        "INSERT INTO news_items (id, title, source_id, published_at, ingested_at, body, summary, "
        "insight, classification, processing_status, relevance, duplicate_of, coverage_note, "
        "created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            news_id, title, source_id, _iso(published), utc_now(), body, summary, insight,
            classification, status, relevance, duplicate_of, coverage_note, user["id"],
            utc_now(),
        ),
    )
    for label in labels:
        topic_id = _ensure_topic(db, label)
        db.execute(
            "INSERT OR IGNORE INTO news_topics (news_id, topic_id) VALUES (?, ?)",
            (news_id, topic_id),
        )
    for instrument_id in instrument_ids:
        instrument = db.execute(
            "SELECT * FROM instruments WHERE id = ?", (instrument_id,)
        ).fetchone()
        if instrument is not None and can_read(instrument, user):
            db.execute(
                "INSERT OR IGNORE INTO news_instruments (news_id, instrument_id) VALUES (?, ?)",
                (news_id, instrument_id),
            )
    db.commit()
    return db.execute("SELECT * FROM news_items WHERE id = ?", (news_id,)).fetchone()


def create_news(db, user, payload: dict) -> dict:
    title = str(payload.get("title") or "").strip()
    body = str(payload.get("body") or "").strip()
    source_id = payload.get("source_id")
    published_at = payload.get("published_at")
    if not title or not body or not source_id or not published_at:
        raise ApiError(
            422, "validation_error", "title, body, source_id and published_at are required."
        )
    classification = str(payload.get("classification") or "internal").lower()
    topics = [str(label) for label in payload.get("topics") or []]
    instrument_ids = [str(value) for value in payload.get("instruments") or []]
    row = _process_and_store(
        db,
        user,
        title=title,
        body=body,
        source_id=source_id,
        published_at=published_at,
        classification=classification,
        topics=topics,
        instrument_ids=instrument_ids,
        coverage_note=payload.get("coverage_note"),
    )
    record(
        db,
        action="news_intake",
        result="succeeded",
        actor=user,
        object_type="news_item",
        object_id=row["id"],
        classification=row["classification"],
    )
    return news_payload(db, row, user)


def create_news_from_upload(db, user, file_storage, form: dict) -> dict:
    filename = file_storage.filename or ""
    extension = ""
    if "." in filename:
        extension = "." + filename.rsplit(".", 1)[1].lower()
    if extension not in current_app.config["ALLOWED_UPLOAD_EXTENSIONS"]:
        raise ApiError(
            422,
            "unsupported_type",
            "Supported formats: CSV, XLSX, PDF, DOC, DOCX.",
        )
    data = file_storage.read()
    max_bytes = current_app.config["MAX_UPLOAD_BYTES"]
    if len(data) > max_bytes:
        raise ApiError(413, "payload_too_large", "File exceeds the 5 MB limit.")
    if not data:
        raise ApiError(422, "empty_file", "The selected file is empty.")

    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    if extension == ".csv":
        body = data.decode("utf-8", errors="replace")[:5000]
    else:
        body = f"Uploaded document {filename} ({len(data)} bytes). Text extraction is simulated in the demo."
    row = _process_and_store(
        db,
        user,
        title=str(form.get("title") or stem or filename),
        body=body,
        source_id=str(form.get("source_id") or ""),
        published_at=str(form.get("published_at") or ""),
        classification=str(form.get("classification") or "internal").lower(),
        topics=[],
        instrument_ids=[],
        coverage_note=f"Uploaded file: {filename}",
    )
    record(
        db,
        action="news_upload",
        result="succeeded",
        actor=user,
        object_type="news_item",
        object_id=row["id"],
        classification=row["classification"],
        detail=filename,
    )
    return news_payload(db, row, user)


def add_feedback(db, user, news_id: str, payload: dict) -> dict:
    get_news(db, user, news_id)
    kind = str(payload.get("kind") or "")
    if kind not in FEEDBACK_KINDS:
        raise ApiError(422, "invalid_kind", "kind must be important or comment.")
    body = payload.get("body")
    if kind == "comment" and not (body and str(body).strip()):
        raise ApiError(422, "validation_error", "A comment needs a body.")
    cursor = db.execute(
        "INSERT INTO news_feedback (news_id, user_id, kind, body, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (news_id, user["id"], kind, str(body).strip() if body else None, utc_now()),
    )
    db.commit()
    row = db.execute("SELECT * FROM news_feedback WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return {
        "id": row["id"],
        "news_id": row["news_id"],
        "kind": row["kind"],
        "body": row["body"],
        "user_id": row["user_id"],
        "created_at": row["created_at"],
    }


def coverage(db, user, event_id: str) -> dict:
    event = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if event is None or not can_read(event, user):
        raise ApiError(404, "not_found", "Event not found.")
    rows = db.execute(
        "SELECT n.* FROM news_items n JOIN event_news en ON en.news_id = n.id "
        "WHERE en.event_id = ? ORDER BY n.published_at",
        (event_id,),
    ).fetchall()
    articles = []
    topic_sets = []
    for row in visible_rows(rows, user):
        if row["classification"] == "restricted":
            record_restricted_view(db, user, "news_item", row["id"])
        labels = _topics_for(db, row["id"])
        topic_sets.append(set(labels))
        source = db.execute("SELECT name FROM sources WHERE id = ?", (row["source_id"],)).fetchone()
        articles.append(
            {
                "id": row["id"],
                "title": row["title"],
                "source": {"id": row["source_id"], "name": source["name"] if source else row["source_id"]},
                "published_at": row["published_at"],
                "topics": labels,
                "coverage_note": row["coverage_note"],
            }
        )
    shared = set.intersection(*topic_sets) if topic_sets else set()
    return {
        "event": {
            "id": event["id"],
            "title": event["title"],
            "occurred_at": event["occurred_at"],
            "status": event["status"],
            "classification": event["classification"],
        },
        "articles": articles,
        "shared_topics": sorted(shared),
        "counts": {"articles": len(articles), "sources": len({article["source"]["id"] for article in articles})},
    }
