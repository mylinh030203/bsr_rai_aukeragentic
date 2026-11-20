# BSR Market Intelligence Platform — PRD

Version: 1.0 (MVP build)
Source: BSR Market Intelligence Platform specification v2.0
Status: Implementation-ready

## 0. Project type

A permission-aware enterprise web application (desktop-first, responsive) backed by a Python HTTP API and relational database. It includes a server-rendered/static JavaScript frontend, deterministic analytical services, a normalized AI adapter, and an auditable demo AI execution path. This is a UI build.

## 1. Problem statement

BSR's Market Intelligence team gathers crude and refined-product prices, news, research, forecasts and internal documents from many providers, spreadsheets and reports. The work is manual and fragmented, so leadership waits too long for context, source comparison is inconsistent, forecast accuracy is not tracked historically, and sensitive physical prices risk being over-shared. The MVP creates one market-centric workspace that unifies observations, news, forecasts, deterministic analytics and cited AI assistance under backend-enforced permissions.

## 2. Target users

**Lãnh đạo & quản lý (Leadership, ~40)** — consumes market summaries, asks questions and requests reports. Needs speed, cited evidence and clear uncertainty; does not perform data entry.

**Đội Market Intelligence (~10)** — ingests prices, news and documents, validates extracted data, manages forecasts and publishes briefings. Needs efficient workflows, quality state and source provenance.

**Người dùng nội bộ (~1,500)** — reads approved market information and reports. Must never see Restricted physical data by default. Medium product literacy.

## 3. User stories

### P0 — Market overview and data

**US-01 — Market overview snapshot (P0)**
As a leadership user I want a single overview of Brent, WTI, gasoline, USD/VND and crack spreads so that I can judge the market before a meeting.
Acceptance criteria:
- Given seeded observations, when I open Overview, then I see instrument, latest value, unit, absolute and percentage change, market timestamp, ingestion timestamp, source and data status.
- Given a stale or manual observation, when it is displayed, then it is labelled as such rather than as real-time.
- Given I lack Restricted access, then no restricted physical value appears in cards, charts, API responses or AI context.

**US-02 — Market data series (P0)**
As a Market Intelligence user I want to explore historical observations by instrument and date range so that I can understand trend and context.
Acceptance criteria:
- Given an instrument, when I open Market Data, then I see a time-series chart, selectable range, latest value and source metadata.
- Given multiple obtained series, when I select a second series, then both are normalized or unit-labelled and comparison is readable.
- Given a calculated crack spread, when I inspect it, then I can see formula version, inputs and calculation time.

**US-03 — Deterministic crack spread (P0)**
As an analyst I want crack spreads computed reproducibly from versioned formulas so that I can defend the number.
Acceptance criteria:
- Given a formula and two permitted input observations, when a spread is calculated, then the result and formula ID/version are stored and visible.
- Given a physical/futures mismatch, when the formula is configured to disallow mixing, then calculation is rejected.
- Given the same inputs and formula version, when recalculated, then the result is identical.

### P0 — News intelligence

**US-04 — Ingest and process news (P0)**
As Market Intelligence staff I want to add news text or upload a supported document so that it enters a consistent processing pipeline.
Acceptance criteria:
- Given valid title, body/source/publication time and classification, when I submit, then a news item is created with processing states and source metadata.
- Given an unsupported or oversized upload, then I receive a controlled error and no item is stored.
- Given a news item, then I can see original content, AI summary and AI insight as distinct attributions.

**US-05 — News feed with filters (P0)**
As an internal user I want to filter news by topic, source and time so that I can find relevant developments quickly.
Acceptance criteria:
- Given news items, when I filter, then only matching permitted items return, with source, published time, topics and processing status.
- Given a duplicate candidate, then the feed links it to the original instead of deleting source content.
- Given a Restricted news item, then unauthorized users receive no title, snippet or count leak.

**US-06 — Condensed intelligence (P0)**
As a leadership user I want an AI-generated market briefing from permitted sources so that I can absorb the day's developments quickly.
Acceptance criteria:
- Given observations and news, when a briefing is generated, then it includes timestamp, 24-hour moves, drivers, new items and traceable source references.
- Given AI-generated content, then it is labelled separately from source facts.
- Given a briefing is regenerated, then a new version is stored; the previous version is unchanged.

### P0 — AI assistant and reports

**US-07 — Permission-scoped AI chat (P0)**
As an authorized user I want to ask natural-language questions about permitted data and news so that I get an evidence-linked answer without manual research.
Acceptance criteria:
- Given a question about a permitted instrument, when the AI responds, then the answer cites retrieved observations/news and identifies itself as AI interpretation.
- Given a user without Restricted access, when they ask about physical prices, then the AI system receives no Restricted records and replies that data is unavailable.
- Given a deterministic calculation is requested, then the answer uses the analytical service output, not an LLM-computed number.
- Given every AI call, an execution record stores trace ID, task type, model, latency, cost, validation status and permission scope.

**US-08 — Generate and export a report (P0)**
As a leadership user I want an on-demand market report with sources and exportable PDF so that I can share a defensible snapshot.
Acceptance criteria:
- Given a report type and date range, when generated, then it stores report type, data cut-off, content, source references, requester and version.
- Given later source changes, then the stored report content does not silently change.
- Given export permission, then PDF download works; without export permission, the endpoint is denied and audited.

### P0 — Access control and audit

**US-09 — Role and classification enforcement (P0)**
As a security owner I want backend-enforced RBAC and data classification so that permissions do not depend on prompts or UI hiding.
Acceptance criteria:
- Given leadership, Market Intelligence and internal roles, then each sees only permitted data and actions.
- Given a direct API request for a Restricted object by an unauthorized user, then the backend returns 403/404 without leaking content.
- Given a sensitive action (view restricted, export, upload, AI request, permission change), then an audit entry records actor, action, object, timestamp and result.

### P1 — Forecast and source comparison

**US-10 — Versioned forecasts (P1)**
As a Market Intelligence user I want each forecast update stored as a new version so that history is preserved.
Acceptance criteria: updates never overwrite; versions show source, publication date, value, horizon and methodology; revisions are comparable.

**US-11 — Forecast evaluation (P1)**
As an analyst I want deterministic error metrics against actuals so that I can compare source accuracy by instrument and horizon.
Acceptance criteria: absolute/percentage error, MAE, MAPE, bias computed from stored values; missing actuals are stated, not treated as zero.

**US-12 — News coverage comparison (P1)**
As an analyst I want to compare how sources cover the same event so that I can see what is additive.
Acceptance criteria: linked articles show source, publish time, shared topics and unique details; counts do not imply trustworthiness.

**US-13 — Event-linked series (P1)**
As an analyst I want event markers on time series so that I can relate price moves to occurrences.
Acceptance criteria: permitted events appear as markers; selecting one shows title, time, sources and linked instruments.

## 4. Scope

### In scope (P0 plus selected P1)
- Local authentication with demo accounts, session cookies, three roles and data-classification filtering.
- Market Overview with metric cards, sparklines, market highlights, key drivers and AI briefing versions.
- Market Data with instrument catalog, time series, range controls, comparison, crack-spread display and event markers.
- News intake (text + PDF/text upload), processing simulation, topic classification, duplicate candidates, feed filters, feedback/comments.
- Forecast register with immutable versions and basic evaluation against actual observations.
- Analysis workspace with deterministic returns, volatility, moving average, correlation, spread analytics and evidence separation.
- AI Assistant with permission-scoped retrieval, cited answers, deterministic tool use, structured AI task/execution records and graceful fallback.
- Reports: on-demand generation, versions, source references, PDF export.
- Audit log, global freshness indicator, demo data seeding.
- Responsive, accessible market-centric UI with collapsible left navigation.

### Out of scope
- Full enterprise risk-management platform, risk heatmap as the central UI, automatic trade execution.
- Live Reuters/Platts/Bloomberg integrations or licensed feeds.
- A real external LLM call; the AI adapter is deterministic and local by default, designed for provider swapping. (No provider credentials are assumed.)
- ERP/Finance/Procurement/Production integrations, SSO/IdP, email delivery, video briefing, mobile native app.
- Fine-grained per-user ACL editor beyond the demonstrated role + classification + department model.

## 5. Success metrics

- A first-time user can reach a sourced market answer in under 3 clicks from Overview; demo login is one click per role.
- Every displayed market value exposes source, data status and market/ingestion timestamps.
- Unauthorized restricted data leaks: 0 in automated role-matrix tests, including AI retrieval and PDF export.
- Every generated report and briefing has at least one stored source reference and an immutable version.
- Every AI interaction is traceable by task/trace ID with latency and cost metadata.
- All P0 acceptance criteria have an automated test; app starts with one documented command.

## 6. Open questions (non-blocking for demo)

- Official BSR crack-spread formula and physical-price validation workflow are not supplied; demo uses configurable illustrative formulas and flags them as demo configuration.
- Commercial source licensing/API availability is unconfirmed; ingestion is via manual text/file and seeded data.
- Deployment target, retention, SSO and quantitative latency targets are unspecified; local SQLite/file storage is used for the MVP.
- Report approval workflow and official instrument taxonomy need BSR confirmation.
