# RAI.md — BSR Market Intelligence

## What We Are Building

A permission-aware market-intelligence workspace for BSR: one place to see what moved, why, what the evidence is and what to watch next. It unifies market observations, news, versioned forecasts, deterministic analytics, cited AI assistance and immutable reports under backend-enforced role and classification rules. The UI is a static SPA served by a Python API; demo data is synthetic and labelled.

## Stack

- Python 3.14 + Flask 3.1, application factory with one blueprint per module.
- SQLite via stdlib `sqlite3`, WAL, foreign keys on, plain SQL migrations.
- Vanilla ES modules + hand-authored CSS using the design tokens; no build step.
- Server-side opaque sessions in SQLite, HttpOnly `SameSite=Lax` cookie, double-submit CSRF.
- Authorization in one policy module, enforced in services before serialization.
- Deterministic local AI adapter with auditable `ai_tasks` / `ai_executions`.
- pytest for unit/integration; Playwright (Python) for browser E2E.

## Project Structure

```
app/
  __init__.py        application factory, security headers, error handlers
  config.py          (reserved) environment-driven settings
  db.py              connection lifecycle, migration runner
  errors.py          ApiError and JSON error shape
  permissions.py     classification rank, row filters, capability checks
  auth.py            session issue/verify, CSRF, login rate limit
  api/               one blueprint per module; routes and status codes
  services/          market, analytics, news, forecasts, assistant, reports, audit, seed
  ai/                deterministic provider and task definitions
  static/            index.html + assets (app.js, styles.css, i18n.js)
migrations/          numbered SQL schema files
tests/               pytest unit/integration; tests/e2e for Playwright
docs/                PRD, SCREENS, STACK, DATA_MODEL, API, design artifacts
run.py               development entry point
```

## Commands

All commands are run from the project root and have been executed at least once.

```
python run.py                     — start the development server on http://127.0.0.1:5000
python run_prod.py                — serve the release build with waitress on $BSR_PORT (default 8000)
docker compose -f docker-compose.yml -f compose.demo.yml up -d --build — host the seeded demo workspace on http://localhost:8000
docker compose up -d --build      — host with the production posture (needs BSR_SECRET_KEY, HTTPS in front)
python -m pytest -q               — run unit and integration tests
python -m pytest tests/e2e -m e2e — run browser end-to-end tests (server must be running; needs the -m e2e marker)
python -m compileall -q app run.py wsgi.py run_prod.py scripts — syntax check every Python module
python scripts/backup_db.py       — consistent online backup of the SQLite database
```

Runtime dependencies are `requirements.txt`; test and browser tooling is
`requirements-dev.txt`. The release runbook lives in `docs/RELEASE.md`.

There is no Node toolchain and no build step. Do not add one without a concrete need.

## Non-Negotiable Rules

1. **Authorization is server-side.** Every read and write passes through `app/permissions.py`; hiding a control in the UI is never the enforcement. Why: the PRD's security criteria are backend obligations.
2. **Filter before serialization.** Restricted rows are removed in the service layer, before JSON, before AI context, before PDF content. Why: a filtered response cannot leak through a forgotten template or prompt.
3. **Deterministic numbers come from the analytical service.** The AI adapter interprets; it never computes a spread, return, volatility or error metric. Why: US-03 and US-07 require reproducible numbers.
4. **Versions are immutable.** Forecast, briefing and report updates insert a new version; no update or delete path exists for stored versions. Why: US-06, US-08, US-10.
5. **Audit every sensitive action.** Sign-in, restricted view, manual observation, news intake, upload, AI request, report generation, export attempt and permission change write an `audit_log` row. Why: US-09.
6. **Validate at the boundary.** Request bodies, uploads, query parameters and classification values are validated in the route/service before touching the database; errors use the documented shape. Why: US-04 and the service baseline.
7. **Preserve regression coverage.** Never weaken or delete a test to get green; retire coverage only for explicitly retired behavior.
8. **Every bug fix ships with a regression test that first reproduces the bug.**
9. **E2E tests use semantic locators only** — `get_by_role`, `get_by_label`, `get_by_text`, `get_by_test_id`. Never CSS class selectors, never XPath.
10. **No secrets in code or logs.** Demo accounts are public by design; session tokens and CSRF values are never logged.

## Coding Conventions

- Python: 4-space indent, `from __future__ import annotations`, type hints on public functions, module-level docstrings only where they add information.
- SQL: uppercase keywords, one column per line in migrations, explicit `CHECK` constraints for every enum.
- JSON: `snake_case` keys; timestamps ISO 8601 with offset; numbers unformatted (formatting is the UI's job).
- JavaScript: ES modules, one module per concern, no framework, no build step; DOM access through small helpers.
- CSS: design tokens from `docs/design/specs/design-tokens.md`; no hard-coded colors outside the token block.
- Tests: one behavior per test, named for the rule it protects, using the Flask test client for API behavior and Playwright for browser journeys.

## Design Principles

- **One policy owner.** `app/permissions.py` owns classification rank, restricted view, export and admin checks. Routes ask it; they do not re-implement it.
- **Services own transactions.** Routes parse and validate input, call a service, and serialize the result. Services own SQL and invariants.
- **The analytical service is pure.** Given observations and a formula version it returns the same result; it does not read the clock or the session.
- **The AI adapter is a seam.** `app/ai/provider.py` exposes one `run(task, context)` contract; the deterministic implementation is the only production adapter, and tests can substitute a failing adapter to prove fallback.
- **Stable contracts:** API paths, status codes, error codes, cookie name `bsr_session`, CSRF header `X-CSRF-Token`, and the `classification` vocabulary must not change casually. The SPA and the tests consume them.
- **No speculative layers.** Add an abstraction when a current caller or test needs it, not in anticipation.

## Definition of Done Checklist

- [ ] Feature works per the acceptance criteria in the plan
- [ ] Relevant behavior and regression tests pass
- [ ] Permission boundaries tested for all three roles, including direct API access
- [ ] Runtime behavior verified against the running app, not only unit tests
- [ ] No syntax or import errors (`python -m compileall -q app run.py`)
- [ ] Audit rows written for sensitive actions
- [ ] UI matches the design contract in `docs/design/` for the changed screen

## Known Patterns

- **Repository/service split:** SQL lives in `app/services/*`; routes never build SQL strings.
- **Session lookup:** `app/auth.py` resolves the cookie to a user on every request; `g.user` is the single source of identity.
- **Permission filter:** `visible_rows(rows, user)` and `can_read(row, user)` are the only sanctioned ways to decide visibility.
- **AI execution record:** every AI call creates an `ai_tasks` row and one `ai_executions` row, even on fallback or failure.
- **Seed data:** `app/services/seed.py` is idempotent and runs on first start; it mirrors the synthetic data in `docs/design/prototype/assets/data.js`.
