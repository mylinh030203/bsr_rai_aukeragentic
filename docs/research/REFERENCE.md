# Domain research notes — BSR Market Intelligence Platform

Source: BSR Market Intelligence Platform specification v2.0 (user-supplied brief). No external market or competitor research was commissioned; sections not covered by the brief are marked as not researched.

## Domain vocabulary (entities, KPIs, statuses) → seeds docs/design/specs/CONTEXT.md

- **Market Observation** — a timestamped value for one instrument from one source. Carries market time and ingestion time separately.
- **Instrument** — a tracked market series (Brent futures, WTI physical, RON95, USD/VND, a crack spread).
- **Price Type** — Futures, Physical, Index or Calculated. Futures and physical must never be mixed in one calculation unless the formula explicitly allows it.
- **Crack Spread** — product value minus crude benchmark, computed by a versioned, reproducible formula.
- **Data Status** — Real-time, Delayed, End-of-day, Manual.
- **Quality Status** — Valid, Pending, Rejected, Corrected.
- **Classification** — Public, Internal, Confidential, Restricted. Restricted covers physical prices and commercial secrets.
- **News Item** — an ingested article or document with source, publication time, topics, entities and processing state.
- **Event** — a market-moving occurrence linked to news and instruments.
- **Forecast / Forecast Version** — a source's projection for an instrument and horizon; every update creates a new version.
- **Forecast Evaluation** — deterministic comparison of a forecast version with actual observations (absolute error, percentage error, MAE, MAPE, bias).
- **Analysis** — a versioned, source-grounded interpretation combining observations, news, forecasts and analytical calculations.
- **Recommendation** — a decision-support option with context, evidence, assumptions, uncertainty and confidence. Never an automatic business decision.
- **Report / Report Version** — a generated briefing with a data cut-off, source references and immutable content.
- **AI Task** — a normalized request to the AI layer with task type, allowed tools, output schema, permission scope and trace ID.
- **AI Execution** — one auditable run of an AI task with model, latency, cost, retries and validation status.
- **Auker** — the AI allocation and orchestration layer. Chooses model, reasoning depth, tools and fallback; never owns authorization or business data.
- **Analytical Service** — deterministic calculation service (spread, time series, volatility, correlation, forecast evaluation). LLMs interpret results but do not perform these calculations.

## User decisions

1. **Leadership:** "Is the market moving in a way that changes our commercial position today?" → needs snapshot, highlights, briefing, exposure-relevant indicators.
2. **Leadership:** "What is driving this move, and how confident should we be?" → needs evidence-linked analysis, source attribution, uncertainty.
3. **Market Intelligence:** "Which incoming item is new, duplicated or materially additive?" → needs deduplication, source comparison, provenance.
4. **Market Intelligence:** "Is this observation trustworthy enough to publish?" → needs quality status, source, timestamps, validation workflow.
5. **Market Intelligence:** "Which forecast source is actually accurate for this instrument and horizon?" → needs versioned forecasts and deterministic error metrics.
6. **Commercial / analysis user:** "What is the current crack economics and what changed?" → needs reproducible spread calculations and time-series context.
7. **Any authorized user:** "Can I get a grounded answer or report without manually gathering sources?" → needs permission-scoped AI chat and report generation with citations.
8. **Security owner:** "Did anyone access or export restricted physical data?" → needs audit log and independent view/export permissions.

## Conventions users expect (text principles, table stakes)

- Dense, scannable financial dashboards with explicit units, timestamps and source labels.
- Clear separation of futures, physical and calculated values.
- Stale/delayed data visibly marked, never presented as real-time.
- Every AI statement distinguishable from source fact and deterministic calculation.
- Left navigation with collapsible sections; persistent global context (as-of time, data freshness).
- Tables for precision, charts for trend; drill-down without losing the current workspace.
- Restricted data hidden entirely, not merely blurred, for unauthorized users.

## UI references and formats

Not externally researched. The brief itself specifies: left sidebar with collapse/expand, six modules, market-centric overview, metric cards with sparklines, interactive drill-down via drawer/panel, event markers on time series, source-attributed news cards, AI chat with citations, report builder. These are treated as brief requirements, not as validated market patterns.

## User sentiment

Not researched. The brief documents internal pain points (BP-01…BP-06) but supplies no user interviews or usage data.

## Failed attempts

Not researched.

## Opportunity gaps

Derived from the brief only: a single permission-aware workspace that connects market observations, news, forecasts, deterministic analytics and AI output with provenance. No claim is made about competitor absence.
