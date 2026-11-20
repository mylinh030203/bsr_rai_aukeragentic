# Release and hosting

The product is a single Python process (Flask + waitress) that serves the API
and the static SPA from one origin, with SQLite holding all state. Everything
below was run from the project root and its result is recorded with it.

## Two ways to host it

| Goal | Command | Posture |
|---|---|---|
| Local demo workspace | `docker compose -f docker-compose.yml -f compose.demo.yml up -d --build` | `development`: synthetic data seeded, demo role sign-in, HTTP cookies |
| Real host | `docker compose up -d --build` (or the `Procfile` / `Dockerfile` on a platform) | `production` by default: refuses to start without a real secret, Secure cookies, no seeding |

The base compose file inherits the production posture, so a forgotten
`BSR_ENV` cannot silently turn a deployment into the demo. The demo workspace
is a named overlay you have to ask for: it declares its own Compose project
(`name: bsr-demo`), its own container and its own `bsr-demo-data` volume, so
demo users can never land in the production `bsr-data` volume and demo
teardown can never delete it. Never run the overlay on a shared or
internet-facing host: it seeds demo users and accepts role sign-in without a
password.

Compose does not refuse a missing secret by itself: the base file passes
`BSR_SECRET_KEY` through as an empty string, and `create_app` then refuses to
start with `ConfigurationError: BSR_SECRET_KEY must be at least 32 characters`.
Because the service is `restart: unless-stopped`, that refusal shows up as a
restarting container rather than an idle one; the reason is in
`docker compose logs`.

Teardown, per mode:

```bash
docker compose down                                  # production: keeps bsr-data
docker compose -f docker-compose.yml -f compose.demo.yml down -v   # demo only: wipes bsr-demo-data
```

`down -v` removes the named volumes of the project it runs in. Because the
demo runs as project `bsr-demo`, its `down -v` cannot touch the production
project's `bsr-data` volume. Do not add a `-v` to a production teardown unless
you intend to delete the real database.

## Running outside Docker

`docker compose` reads a `.env` file itself; `python run_prod.py` does **not**.
Set the variables in the shell instead:

```powershell
# Windows PowerShell
$env:BSR_ENV = "production"
$env:BSR_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(48))")
$env:BSR_DATABASE = "C:\bsr-data\bsr.db"
$env:BSR_SEED_ON_START = "0"
$env:BSR_PORT = "8000"
python run_prod.py
```

```bash
# Linux / macOS
export BSR_ENV=production
export BSR_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export BSR_DATABASE=/var/lib/bsr/bsr.db
export BSR_SEED_ON_START=0
python run_prod.py
```

## Production settings

| Variable | Purpose |
|---|---|
| `BSR_ENV=production` | Enables the startup checks and Secure cookies |
| `BSR_SECRET_KEY` | Random value, at least 32 characters; a missing, short or documented placeholder value refuses startup |
| `BSR_DATABASE` | Persistent path, e.g. `/data/bsr.db` |
| `BSR_SEED_ON_START` | Defaults to `0` in production; keep demo data out |
| `BSR_HOST` / `BSR_PORT` | Bind address and port (most platforms inject `PORT`) |
| `BSR_THREADS` | waitress worker threads (default 4) |

The checks run inside `create_app()`, so every entry point is covered:
`run_prod.py`, `gunicorn wsgi:application`, `waitress-serve --call
wsgi:application`, `flask run --app wsgi:app` and the Docker `CMD`. A
misconfigured process exits before it can accept traffic; the proof is in
`tests/test_release_config.py` and `docs/qa/RELEASE.md`.

`production` also forces the session cookie `Secure`, so the service must sit
behind HTTPS (platform TLS or a reverse proxy). Behind a proxy, keep
`clear_untrusted_proxy_headers` in `run_prod.py`: the login rate limit keys on
the socket address, not on a client-supplied header.

### Volume ownership

`/data` is created and owned by `nobody` (uid 65534) in the image, which a named
Docker volume inherits on first use. A bind mount replaces `/data` with the
host directory's ownership; if the app then exits at startup, run
`chown 65534:65534 <host-dir>` (or use the named volume).

### Single-instance constraint

SQLite with WAL is a single-writer store on one filesystem. Run exactly one
instance and give it a persistent disk. Rate-limit counters also live in that
database, so the limits stay exact for one instance; scaling to several
instances means moving to a multi-writer database (a schema and data-access
change, not a hosting toggle).

## Backup and restore

```bash
python scripts/backup_db.py                                    # instance/bsr.db → backups/bsr-<utc stamp>.db
python scripts/backup_db.py instance/bsr.db backups/copy.db    # explicit destination
python scripts/backup_db.py instance/bsr.db backups/copy.db --force
```

The script uses SQLite's online backup API, so it is safe while the app is
serving. The copy is written to `*.partial`, verified with `PRAGMA
integrity_check`, and only then moved into place; a failed run leaves neither
the destination nor the partial file behind. An existing destination is refused
unless `--force` is passed, so a scheduled job cannot silently overwrite
yesterday's verified backup.

Restore by stopping the instance, replacing the database file (plus its
`-wal`/`-shm` siblings), and starting it again; migrations re-run idempotently
on boot.

## Release gate

```bash
python -m pytest -q                              # unit + integration (130 tests)
python -m pytest tests/e2e -m e2e                # browser journeys, needs a server
python -m compileall -q app run.py wsgi.py run_prod.py scripts
python scripts/release_smoke.py http://127.0.0.1:8000 <db path>   # live host, disposable DB
```

`scripts/release_smoke.py` changes one user's permission and writes audit rows,
so point it at a disposable database. `docs/qa/RELEASE.md` records the
case-by-case evidence from the hosted release run.

## Known limitations of this release

- Demo sign-in selects a role rather than authenticating a user; put a real
  identity provider in front before any non-synthetic data is loaded.
- SQLite backups are filesystem-based: schedule them, and keep the volume and
  the backup on separate storage.
- The service itself terminates no TLS: production expects HTTPS in front.
