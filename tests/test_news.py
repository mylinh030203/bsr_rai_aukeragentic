"""News intelligence: feed filters, intake, duplicates, uploads, feedback, coverage."""

from __future__ import annotations

from io import BytesIO

from tests.conftest import csrf_headers, login_as


def test_feed_is_filtered_by_role_and_filters(seeded_client):
    login_as(seeded_client, "internal")
    internal = seeded_client.get("/api/news").get_json()["news"]
    assert len(internal) == 5
    assert all(item["classification"] in ("public", "internal") for item in internal)
    assert "Platts physical Brent assessment" not in seeded_client.get("/api/news").get_data(
        as_text=True
    )

    login_as(seeded_client, "leadership")
    assert len(seeded_client.get("/api/news").get_json()["news"]) == 7

    opec = seeded_client.get("/api/news?topic=OPEC%2B").get_json()["news"]
    assert {item["id"] for item in opec} == {"N-2411", "N-2407"}

    reuters = seeded_client.get("/api/news?source=SRC-REUTERS").get_json()["news"]
    assert {item["id"] for item in reuters} == {"N-2411", "N-2406"}

    search = seeded_client.get("/api/news?q=freight").get_json()["news"]
    assert [item["id"] for item in search] == ["N-2410"]

    duplicates = seeded_client.get("/api/news?status=duplicate_candidate").get_json()["news"]
    assert [item["id"] for item in duplicates] == ["N-2407"]


def test_detail_separates_source_summary_and_insight(seeded_client):
    login_as(seeded_client, "leadership")
    body = seeded_client.get("/api/news/N-2411").get_json()
    assert body["body"]
    assert body["summary"]
    assert body["insight"].startswith("AI interpretation")
    assert body["topics"] == ["Crude supply", "OPEC+"]
    assert body["duplicate_of"] is None
    assert body["feedback"] == []


def test_duplicate_candidate_links_to_the_original(seeded_client):
    login_as(seeded_client, "leadership")
    body = seeded_client.get("/api/news/N-2407").get_json()
    assert body["duplicate_of"] == "N-2411"
    assert body["processing_status"] == "duplicate_candidate"


def test_restricted_news_detail_is_not_found_for_internal(seeded_client):
    login_as(seeded_client, "internal")
    response = seeded_client.get("/api/news/N-2405")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"


def test_intake_records_an_ai_execution_and_audit(seeded_client, seeded_app):
    session = login_as(seeded_client, "mi")
    payload = {
        "title": "New product crack signal emerges",
        "body": "Refiners report stronger gasoline blending economics this week.",
        "source_id": "SRC-REUTERS",
        "published_at": "2026-11-14T09:00:00+07:00",
        "classification": "internal",
        "topics": ["Refined products"],
        "instruments": ["crack_gasoline"],
        "coverage_note": "1 source - 1 unique detail",
    }
    response = seeded_client.post("/api/news", json=payload, headers=csrf_headers(session))
    assert response.status_code == 201, response.get_json()
    body = response.get_json()
    assert body["processing_status"] == "processed"
    assert body["summary"]
    assert body["insight"].startswith("AI interpretation")
    assert body["topics"] == ["Refined products"]

    with seeded_app.app_context():
        from app.db import get_db

        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM ai_tasks").fetchone()[0] == 5
        assert db.execute("SELECT COUNT(*) FROM ai_executions").fetchone()[0] == 5
        actions = [row["action"] for row in db.execute("SELECT action FROM audit_log")]
    assert "news_intake" in actions


def test_intake_marks_similar_titles_as_duplicate_candidates(seeded_client):
    session = login_as(seeded_client, "mi")
    payload = {
        "title": "OPEC+ signals patience on output as Brent tests $78",
        "body": "A repeat report with the same wording as the earlier item.",
        "source_id": "SRC-BLOOMBERG",
        "published_at": "2026-11-14T09:10:00+07:00",
        "classification": "internal",
    }
    body = seeded_client.post("/api/news", json=payload, headers=csrf_headers(session)).get_json()
    assert body["processing_status"] == "duplicate_candidate"
    assert body["duplicate_of"] == "N-2411"


def test_upload_rejects_unsupported_and_oversized_files(seeded_client, seeded_app):
    session = login_as(seeded_client, "mi")
    with seeded_app.app_context():
        from app.db import get_db

        before = get_db().execute("SELECT COUNT(*) FROM news_items").fetchone()[0]

    unsupported = seeded_client.post(
        "/api/news/upload",
        data={"file": (BytesIO(b"MZ..."), "feed.exe"), "source_id": "SRC-REUTERS",
              "published_at": "2026-11-14T09:00:00+07:00", "classification": "internal"},
        content_type="multipart/form-data",
        headers=csrf_headers(session),
    )
    assert unsupported.status_code == 422
    assert unsupported.get_json()["error"]["code"] == "unsupported_type"

    oversized = seeded_client.post(
        "/api/news/upload",
        data={"file": (BytesIO(b"a" * 5_500_000), "big.csv"), "source_id": "SRC-REUTERS",
              "published_at": "2026-11-14T09:00:00+07:00", "classification": "internal"},
        content_type="multipart/form-data",
        headers=csrf_headers(session),
    )
    assert oversized.status_code == 413
    assert oversized.get_json()["error"]["code"] == "payload_too_large"

    with seeded_app.app_context():
        from app.db import get_db

        after = get_db().execute("SELECT COUNT(*) FROM news_items").fetchone()[0]
    assert after == before


def test_upload_accepts_a_supported_file(seeded_client):
    session = login_as(seeded_client, "mi")
    response = seeded_client.post(
        "/api/news/upload",
        data={
            "file": (BytesIO(b"title,body\nBrent,Supply risk rises\n"), "notes.csv"),
            "source_id": "SRC-REUTERS",
            "published_at": "2026-11-14T09:05:00+07:00",
            "classification": "internal",
            "title": "Brent supply risk rises",
        },
        content_type="multipart/form-data",
        headers=csrf_headers(session),
    )
    assert response.status_code == 201, response.get_json()
    assert response.get_json()["processing_status"] == "processed"


def test_feedback_persists_per_user(seeded_client):
    session = login_as(seeded_client, "leadership")
    important = seeded_client.post(
        "/api/news/N-2411/feedback",
        json={"kind": "important"},
        headers=csrf_headers(session),
    )
    assert important.status_code == 201
    assert important.get_json()["kind"] == "important"

    empty_comment = seeded_client.post(
        "/api/news/N-2411/feedback",
        json={"kind": "comment", "body": "  "},
        headers=csrf_headers(session),
    )
    assert empty_comment.status_code == 422

    comment = seeded_client.post(
        "/api/news/N-2411/feedback",
        json={"kind": "comment", "body": "Watch the next ministerial date."},
        headers=csrf_headers(session),
    )
    assert comment.status_code == 201
    detail = seeded_client.get("/api/news/N-2411").get_json()
    assert len(detail["feedback"]) == 2


def test_coverage_compares_sources_without_a_trust_score(seeded_client):
    login_as(seeded_client, "leadership")
    body = seeded_client.get("/api/news/coverage?event_id=E-1").get_json()
    assert body["event"]["id"] == "E-1"
    assert body["shared_topics"] == ["Crude supply", "OPEC+"]
    assert body["counts"]["articles"] == 1
    assert "trust" not in body
    assert "score" not in body


def test_intake_and_upload_are_limited_to_mi(seeded_client):
    session = login_as(seeded_client, "leadership")
    response = seeded_client.post(
        "/api/news",
        json={"title": "x", "body": "y", "source_id": "SRC-REUTERS",
              "published_at": "2026-11-14T09:00:00+07:00"},
        headers=csrf_headers(session),
    )
    assert response.status_code == 403


def test_coverage_audits_restricted_view(seeded_client, seeded_app):
    with seeded_app.app_context():
        from app.db import get_db

        db = get_db()
        db.execute("INSERT OR IGNORE INTO event_news (event_id, news_id) VALUES ('E-1', 'N-2405')")
        db.commit()

    login_as(seeded_client, "leadership")
    response = seeded_client.get("/api/news/coverage?event_id=E-1")
    assert response.status_code == 200
    assert any(article["id"] == "N-2405" for article in response.get_json()["articles"])
    with seeded_app.app_context():
        from app.db import get_db

        rows = get_db().execute(
            "SELECT object_id FROM audit_log WHERE action = 'restricted_view'"
        ).fetchall()
    assert "N-2405" in {row["object_id"] for row in rows}
