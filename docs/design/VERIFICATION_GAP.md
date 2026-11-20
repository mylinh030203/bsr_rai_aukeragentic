# Verification status — BSR Market Intelligence prototype

Status: **resolved** (prototype only). Architecture, scaffold, backend and the
implementation build have **not** started.

Scope of this note: `docs/design/prototype/index.html` and
`assets/{app.js,data.js,styles.css}`. Static hash-route SPA, synthetic demo data,
no build step.

## What was broken and what is true now

The previous note recorded a JavaScript syntax error that rendered the page
blank (`Invalid or unexpected token` in `loginPage` and `confirmFileInput`).
That no longer reproduces:

- A delimiter scan over the whole file (template literals, nested `${}`
  substitutions, strings, comments) reports 0 problems. The scan was proven to
  detect a dropped `}` and a dropped `)`, so 0 problems is meaningful.
- The page renders on every route; `assets/{app.js,data.js,styles.css}` all
  return 200/304 and the only console entry is the server's missing
  `favicon.ico`, not a project asset.

Do not re-open the "blank page" report without a fresh reproduction: the
current artifact does not exhibit it.

## Review findings F1–F7 (report: `docs/design/review/REVIEW.md`)

| ID | Fix | Live evidence |
|---|---|---|
| F1 | Card/header say "session change"; Observations column reads "Δ vs prior obs." with an explanatory sub-line | Market Data at 1440: header `+1.07 · +1.38% over session change`, column `Δ VS PRIOR OBS.`, sub-line "Δ is versus the prior stored observation; the header change is session-over-session" |
| F2 | Muted ink darkened | `--ink-400` is `#4b5f65`: 5.96 / 6.49 / 5.54 / 4.64 on paper / surface / surface-2 / copper-soft. The earlier `#5c6f74` failed AA at 4.35 on the Forecast `.accuracy-cell` tiles |
| F3 | Closed overlays hidden and unfocusable | closed `#drawer` / `#modal` compute `visibility: hidden`, are absent from the a11y tree, refuse programmatic focus, and Tab never enters them |
| F4 | Chart role permits its markers | chart SVG is `role="group"` when events exist; markers are `g[role=button][tabindex=0]` and receive focus; 0 role="img" charts contain markers |
| F5 | Upload validation | `.exe` → alert "Unsupported format (.exe) … Nothing was stored."; 6 MB CSV → "File is 6.0 MB, above the 5 MB limit. Nothing was stored."; small CSV → toast + news item + one audit row. Selection is retained for retry |
| F6 | Login loading state | choosing a role shows "Preparing your workspace…" with the pending role label for ~600 ms before routing |
| F7 | Mobile footer wrap | at 390×844 the Market Data card footer stays inside the card (span right edge 352.4 vs 357 content edge) |

## Defects found and fixed during this pass

- **Muted contrast on tinted tiles.** `#5c6f74` was exactly 4.35:1 on
  `--surface-2`, failing WCAG AA on the Forecast accuracy cells (6 nodes).
  Fixed by the token change above; axe reports 0 violations there now.
- **Horizontal page overflow on the topbar.** The page was wider than the
  viewport wherever the topbar could not shrink: 397 px at 390 wide, 903 px at
  768 wide (`#admin`). Fixed with `min-width: 0` / `flex-shrink` constraints on
  the 760 px band plus a 761–1024 px band. Re-measured: 390 / 768 / 1024 / 1440
  all equal the viewport across every route.
- **D10 (severity 2) — modal dialogs did not contain keyboard focus.** Only the
  drawer had a Tab loop; with `aria-modal="true"` on `#modal`, Shift+Tab left
  the dialog and reached the page behind it. Fixed by generalising the loop into
  one module-scope `trapFocus(e, sel)` (`app.js:1564-1578`) called for `#modal`
  and `#drawer`. Verified live: Tab and Shift+Tab wrap at both ends inside two
  different modals and the drawer, focus never reaches a background control,
  `scrollY` stays 0, and Escape restores focus to the opener.
- **N1 (severity 1) — S0 promised an invalid sign-in state that does not exist.**
  `docs/SCREENS.md:7` now reads `Default, loading (demo sign-in has no credential
  input, so no invalid state)`, matching the built screen (role cards + loading,
  zero `<input>` elements).

## Verification evidence (current revision)

- axe-core 4.12.1, tags `wcag2a,wcag2aa,wcag21aa,wcag22aa`: **0 violations**
  on all 9 routes. Incomplete results are non-text glyphs (SVG tick text, `✓`)
  and login text whose backdrop is covered by a pseudo-element — axe limits,
  not defects.
- Overflow matrix: 9 route states × 4 viewports (1440×900, 1024×900, 768×1024,
  390×844) → `document.documentElement.scrollWidth` equals the viewport
  everywhere.
- Independent delta reviews (design profile, then code profile): **PASS** with
  no open severity 2 or above finding. The code-profile pass loaded
  `code-quality.md`, `security.md`, `testing.md` and `conformance.md`; security
  and testing were N/A with reasons (no trust boundary in the delta; no test
  runner exists in the repo).
- Runtime verification of the final revision: **PASS** on the focus-trap delta
  (modal and drawer wrapping, Escape restore) with the earlier full-run evidence
  (overflow matrix, axe, upload suite) reused unchanged.

## Known cosmetic residue (accepted, not defects)

- `.asof` uses `overflow: hidden` on a flex container, so at 761–768 px the
  timestamp is hard-cut ("Mixed fres") instead of ellipsised. The same value is
  repeated in card meta rows and the `title` tooltip, so nothing informational
  is lost.
- `.role-select { max-width: 110px }` truncates its own selected label
  ("Market Intellig…") at 768 and 390. The DOM value, accessible name and the
  login-card permission description all still identify the role.
- Native Chromium `datetime-local` sub-field keys (e.g. `End`) can scroll the
  document while that input has focus, because an open overlay does not lock
  background scroll. Ordinary Tab traversal never scrolls the page.

## Not started

Architecture (`STACK.md`, `DATA_MODEL.md`, `API.md`, `RAI.md`), scaffold, smoke
test, implementation plan and build. Backend enforcement claims (RBAC, AI
retrieval filtering, export gating) remain implementation obligations that the
prototype only demonstrates.

## Files to clean up (generated during QA)

Removal through the shell is blocked for project paths; delete these by hand:

- `tmp/bsr_upload/` — `feed.exe`, `big.csv` (6 MB), `ok.csv` upload fixtures.
- `tmp/bsr-harness/` — a prototype copy made for the overflow matrix harness.
- `tmp/bsr_rotate/` — earlier probe output (`probe_ok`); not produced by this
  pass, listed so the scratch tree ends empty.
- `docs/design/*.py` helper scripts and `docs/design/probe*.txt` left from the
  earlier repair attempts (listed in the previous version of this note).
- `.rai/jobs/*.out` — background job logs.
