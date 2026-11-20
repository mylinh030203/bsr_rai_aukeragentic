# QA evidence — BSR Market Intelligence MVP

Date: 2026-11-15. Revision: working tree after the SPA and backend build.
Environment: Windows, Python 3.14, Flask 3.1, SQLite, Chromium 158 (Playwright 1.65), axe-core 4.12.1.

## Automated suites

| Command | Result |
|---|---|
| `python -m pytest -q` | 92 passed |
| `python -m pytest tests/e2e -m e2e -q` | 6 passed |
| `python -m compileall -q app run.py` | exit 0 |

E2E journeys (semantic locators only): morning triage, news review, forecast history, report generation + PDF download, permission boundary (restricted hidden, admin denied, AI refusal), quick input.

## Accessibility (axe-core 4.12.1, tags wcag2a/wcag2aa/wcag21aa/wcag22aa)

| Route | Violations | Incomplete |
|---|---|---|
| `#login` | 0 | 0 |
| `#overview` | 0 | 1 (SVG chart axis text: background not determinable) |
| `#market-data` | 0 | 1 (SVG axis text; instrument rail partially obscured by scroll container) |
| `#news` | 0 | 0 |
| `#forecast` | 0 | 0 |
| `#analysis` | 0 | 0 |
| `#assistant` | 0 | 0 |
| `#reports` | 0 | 0 |
| `#admin` | 0 | 0 |

Defects found and fixed during this pass:

- `.badge.warn` contrast 3.82:1 → text darkened to `#6f4a10` (passes 4.5:1).
- `.ai-label` contrast 4.3:1 → darkened to `#8f441f`.
- Market tape `div` carried `aria-label` without a role → `role="group"`.
- Admin permission toggles were icon-only with no accessible name → explicit `aria-label` per user/field/state.

Remaining incomplete items are axe limitations on SVG text and scroll-obscured nodes, not observed defects. Manual screen-reader and full keyboard journeys were not run; automated checks are not a conformance verdict.

## Responsive overflow matrix

`document.documentElement.scrollWidth` equals `window.innerWidth` for all 8 routes at 390×844, 768×1024, 1024×900 and 1440×900 (32/32 checks).

## Direct-API role matrix (fresh throwaway database)

19/19 checks passed:

- Internal role: overview excludes `brent_physical` and `bsr_margin`, response contains no `77.9`, `restricted_hidden` true; instruments 11; restricted instrument detail 404; news 5 with no `N-2405`; restricted news detail 404; forecasts 5 with no `F-104`; reports 2; confidential report 404; briefings exclude confidential; assistant refusal text present and no restricted record in the response.
- Leadership: `/api/admin/users` 403; report export 403 `export_denied`.
- MI: report export 200 with `%PDF-1.4` bytes.

## Performance sanity

`GET /api/overview` on the seeded database: median 25.9 ms, max 38.3 ms over 10 runs (target < 500 ms).

## Negative cases (pytest)

- Upload `.exe` → 422 `unsupported_type`, nothing stored.
- Upload 5.5 MB CSV → 413 `payload_too_large`, nothing stored.
- Export without permission → 403 `export_denied` plus an `export_attempt` audit row.
- Mixed price types on `CS-STRICT-1.0` → 422 `mixed_price_types`.
- Classification below the instrument's own → 422 `classification_below_instrument`.
- CSRF missing on a state-changing request → 403 `csrf_failed`.
- Login 11th attempt in the window → 429 `rate_limited`.

## Known limits

- The AI adapter is deterministic and local; no external model is called.
- PDF export is ASCII English only (no Vietnamese diacritics in the PDF body).
- Chart axis contrast is not machine-verifiable by axe; the token `--ink-400` was validated in the design review.
- Manual keyboard/screen-reader journeys and print-to-PDF rendering were not exercised in this pass.
