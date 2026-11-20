"""Report routes, including the permission-gated PDF export."""

from __future__ import annotations

from flask import Blueprint, Response, g, jsonify, request

from ..auth import rate_limit
from ..db import get_db
from ..errors import ApiError
from ..services import reports

report_bp = Blueprint("report", __name__)


@report_bp.get("/reports")
def list_reports():
    return jsonify({"reports": reports.list_reports(get_db(), g.user)})


@report_bp.post("/reports")
def create_report():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request", "Expected a JSON object.")
    return jsonify(reports.create_report(get_db(), g.user, body)), 201


@report_bp.get("/reports/<report_id>")
def get_report(report_id: str):
    return jsonify(reports.get_report(get_db(), g.user, report_id))


@report_bp.get("/reports/<report_id>/export.pdf")
def export_pdf(report_id: str):
    rate_limit("export", g.user["id"])
    payload = reports.export_pdf(get_db(), g.user, report_id)
    return Response(
        payload,
        status=200,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{report_id}.pdf"'},
    )
