"""Release smoke: exercise the hosted build the way the runbook claims it works.

    python scripts/release_smoke.py http://127.0.0.1:8000

Prints one line per case with PASS/FAIL and exits non-zero if any case fails.
Run against a freshly seeded demo database; it changes one user's permission
and writes audit rows, which is exactly what the release evidence needs.
"""

from __future__ import annotations

import http.cookiejar
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}{('  — ' + detail) if detail else ''}")


class Client:
    def __init__(self, base: str) -> None:
        self.base = base.rstrip("/")
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )
        self.csrf: str | None = None

    def request(self, method: str, path: str, body: dict | None = None, csrf: bool = True):
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"} if data else {}
        if csrf and self.csrf and method not in ("GET", "HEAD"):
            headers["X-CSRF-Token"] = self.csrf
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with self.opener.open(req, timeout=10) as response:
                return response.status, response.headers, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.headers, error.read()

    def login(self, role: str) -> dict:
        status, _, payload = self.request("POST", "/api/auth/session", {"role": role})
        assert status == 201, (status, payload)
        self.csrf = json.loads(payload)["csrf_token"]
        return json.loads(payload)


def main(base: str) -> int:
    anonymous = Client(base)
    status, _, payload = anonymous.request("GET", "/api/health")
    check("health endpoint reports ok", status == 200 and json.loads(payload)["status"] == "ok")

    # --- leadership: restricted visibility, no export right -------------------
    lead = Client(base)
    lead.login("leadership")
    status, _, payload = lead.request("GET", "/api/reports")
    lead_ids = {row["id"] for row in json.loads(payload)["reports"]} if status == 200 else set()
    check("leadership sees all three seeded reports", status == 200 and len(lead_ids) == 3,
          f"{sorted(lead_ids)}")
    status, headers, payload = lead.request("GET", "/api/reports/R-2026-039")
    check("leadership reads the confidential report", status == 200, f"status={status}")
    status, _, payload = lead.request("GET", "/api/reports/R-2026-041/export.pdf")
    body = json.loads(payload) if payload[:1] == b"{" else {}
    check("leadership without can_export is denied export",
          status == 403 and body.get("error", {}).get("code") == "export_denied",
          f"status={status} code={body.get('error', {}).get('code')}")

    # --- internal: restricted is invisible, not forbidden --------------------
    internal = Client(base)
    internal.login("internal")
    status, _, payload = internal.request("GET", "/api/reports")
    internal_ids = {row["id"] for row in json.loads(payload)["reports"]} if status == 200 else set()
    check("internal cannot list the confidential report",
          status == 200 and internal_ids == {"R-2026-040", "R-2026-041"}, f"{sorted(internal_ids)}")
    status, _, payload = internal.request("GET", "/api/reports/R-2026-039")
    hidden = json.loads(payload)
    check("confidential report answers 404 (not 403) for internal",
          status == 404 and hidden.get("error", {}).get("code") == "not_found", f"status={status}")

    # --- mi: export works and produces a PDF --------------------------------
    mi = Client(base)
    mi.login("mi")
    status, headers, payload = mi.request("GET", "/api/reports/R-2026-041/export.pdf")
    check("mi export returns a PDF",
          status == 200 and headers.get("Content-Type", "").startswith("application/pdf")
          and payload.startswith(b"%PDF-1.4"),
          f"status={status} type={headers.get('Content-Type')} bytes={len(payload)}")

    # --- state change, then audit trail ------------------------------------
    status, _, payload = lead.request("PATCH", "/api/admin/users/u-int", {"can_export": True})
    check("permission change requires admin (leadership refused)",
          status == 403 and json.loads(payload)["error"]["code"] == "forbidden", f"status={status}")
    status, _, payload = mi.request("PATCH", "/api/admin/users/u-int", {"can_export": False})
    check("admin permission change succeeds", status == 200, f"status={status}")

    status, _, payload = mi.request("GET", "/api/admin/audit?limit=200")
    audit = json.loads(payload)["audit"] if status == 200 else []
    pairs = {(row["action"], row["result"]) for row in audit}
    for needed in (
        ("sign_in", "succeeded"),
        ("export_attempt", "denied"),
        ("export_attempt", "allowed"),
        ("permission_change", "succeeded"),
    ):
        check(f"audit log contains {needed[0]}/{needed[1]}", needed in pairs, f"{len(audit)} rows")

    # --- CSRF still enforced on the hosted build ---------------------------
    status, _, payload = mi.request("DELETE", "/api/auth/session", csrf=False)
    check("state change without CSRF token is rejected",
          status == 403 and json.loads(payload)["error"]["code"] == "csrf_failed", f"status={status}")

    # --- backup round-trip -------------------------------------------------
    check("release host serves the SPA shell",
          anonymous.request("GET", "/")[0] == 200)

    database = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if database is not None:
        # The smoke run changes permission state, so it starts from a clean copy
        # and leaves the destination in place for the operator to inspect.
        backup_path = database.parent / f"backup-check-{os.getpid()}.db"
        result = subprocess.run(
            [sys.executable, "scripts/backup_db.py", str(database), str(backup_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        ok = result.returncode == 0 and backup_path.exists() and backup_path.stat().st_size > 0
        check("online backup produces an integrity-checked copy", ok,
              (result.stdout or result.stderr).strip().splitlines()[-1][:120] if (result.stdout or result.stderr).strip() else "")

    failed = [name for name, ok, _ in RESULTS if not ok]
    print()
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} cases passed")
    if failed:
        print("failed:", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"))
