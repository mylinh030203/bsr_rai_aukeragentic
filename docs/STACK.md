# Stack decision — BSR Market Intelligence

Status: decided for the MVP. Every choice below is one sentence of justification.

## Frontend

**Vanilla ES modules + static HTML/CSS, served by the Python app.** The design prototype is already a hash-route SPA in plain JavaScript, the machine has no Node runtime, and the product has no build-time needs that justify adding one.

**Hand-authored CSS with the design tokens from `docs/design/specs/design-tokens.md`.** The visual system is already specified as CSS custom properties; a utility framework would duplicate it and fight the editorial typography.

## Backend

**Python 3.14 + Flask 3.1 (already installed).** Flask is the boring, proven choice for a small permission-aware JSON API, and it keeps the whole product runnable with one interpreter and no package install.

**Application factory + blueprints, one blueprint per module.** This keeps route registration, error handling and test configuration in one place while letting each module own its routes.

## Database

**SQLite via the standard-library `sqlite3` module, WAL mode, foreign keys on.** The MVP is a single-node demo with modest write volume; SQLite removes an external service and still gives real constraints, transactions and indexes.

**Plain SQL migrations applied by a small runner.** The schema is the contract, and SQL files are reviewable without an ORM layer that would hide the constraints the permission model depends on.

## Auth

**Server-side opaque sessions stored in SQLite, delivered as an HttpOnly `SameSite=Lax` cookie, with a double-submit CSRF token for state-changing requests.** Demo role sign-in needs no password, but the session, CSRF and permission checks must still be real because the PRD's security acceptance criteria are backend obligations.

**Authorization in one policy module, enforced in services and repositories.** Classification rank, restricted-view, export and admin rights are decided once and applied to pages, API responses, AI retrieval and exports.

## Hosting

**Development: `python run.py` (Flask development server). Release: waitress via `wsgi.py` / `run_prod.py`, packaged in `Dockerfile` + `docker-compose.yml`.** One process serves the API and the static SPA; SQLite lives on a mounted volume (`/data/bsr.db`). `BSR_ENV=production` refuses to start with a placeholder `BSR_SECRET_KEY`, forces Secure cookies (so TLS terminates in front) and stops seeding demo data. Single instance only while the store is SQLite; the runbook, environment table and backup procedure are in `docs/RELEASE.md`.

## Tests

**pytest 9.2 for unit and integration tests, using Flask's test client against a temporary SQLite database.** It is installed, fast, and exercises the real request path including cookies, CSRF and permission checks.

**Playwright 1.65 (Python) for end-to-end browser flows.** It is installed and is the only way to prove the SPA renders and the critical journeys work in a real browser.

## System shape

```
┌──────────────┐   HTTP/JSON + session cookie   ┌──────────────────┐
│  Browser SPA │ ─────────────────────────────► │  Flask app       │
│  static/     │ ◄───────────────────────────── │  api/ services/  │
└──────────────┘                                └────────┬─────────┘
                                                         │
                        ┌────────────────────────────────┼─────────────────┐
                        ▼                                ▼                 ▼
                 ┌─────────────┐                  ┌─────────────┐   ┌─────────────┐
                 │ SQLite      │                  │ Analytical  │   │ AI adapter  │
                 │ bsr.db      │                  │ service     │   │ deterministic│
                 └─────────────┘                  └─────────────┘   └─────────────┘
```

The browser never receives a restricted record it is not entitled to: filtering happens in the service layer before serialization, and the AI adapter receives only the already-filtered context.

## Critical Files for Implementation

- `app/__init__.py` — application factory, blueprint registration, error handlers, security headers.
- `app/db.py` — connection lifecycle, migration runner, transaction helper.
- `app/permissions.py` — the single authorization policy used by every route and service.
- `app/api/__init__.py` — the route surface and status-code contract in one place.
- `app/static/index.html` — the SPA entry that wires the design prototype to the API.
