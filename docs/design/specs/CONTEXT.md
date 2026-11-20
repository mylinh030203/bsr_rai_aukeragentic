# BSR Market Intelligence — Context

The shared language for the BSR Market Intelligence Platform. Terms describe the market-intelligence domain, not implementation details.

## Market data

**Market Observation**:
A timestamped value for one instrument from one source, with market time and ingestion time stored separately.
_Avoid_: Price row, tick

**Instrument**:
A tracked market series such as Brent futures, WTI physical, RON95 or USD/VND.
_Avoid_: Ticker, symbol

**Price Type**:
The nature of a value: Futures, Physical, Index or Calculated.
_Avoid_: Source type

**Crack Spread**:
A product value minus a crude benchmark, produced by a versioned and reproducible formula.
_Avoid_: Margin (unless BSR's official formula is confirmed)

**Data Status**:
The freshness of an observation: Real-time, Delayed, End-of-day or Manual.
_Avoid_: Live flag

**Quality Status**:
The validation state of an observation: Valid, Pending, Rejected or Corrected.
_Avoid_: Health

**Classification**:
The access level of data: Public, Internal, Confidential or Restricted.
_Avoid_: Sensitivity tag

## Intelligence

**News Item**:
An ingested article or document with source, publication time, topics, entities and processing state.
_Avoid_: Article record

**Event**:
A market-moving occurrence linked to news items and affected instruments.
_Avoid_: Alert

**Forecast**:
A source's projection for an instrument over a period and horizon.
_Avoid_: Prediction

**Forecast Version**:
An immutable revision of a forecast. Updates create a new version; old versions are never overwritten.
_Avoid_: Forecast edit

**Forecast Evaluation**:
A deterministic comparison of a forecast version with actual observations.
_Avoid_: AI accuracy score

**Analysis**:
A versioned, source-grounded interpretation combining observations, news, forecasts and analytical calculations.
_Avoid_: AI answer

**Recommendation**:
A decision-support option with context, evidence, assumptions, uncertainty and confidence. It never executes a business decision.
_Avoid_: Action, order

**Report**:
A generated briefing with a data cut-off, source references and immutable content.
_Avoid_: Export

**Report Version**:
An immutable revision of a report.
_Avoid_: Report copy

## AI and governance

**AI Task**:
A normalized request to the AI layer with task type, allowed tools, output schema, permission scope and trace ID.
_Avoid_: Prompt

**AI Execution**:
One auditable run of an AI task with model, latency, cost, retries and validation status.
_Avoid_: Log line

**Auker**:
The AI allocation and orchestration layer that chooses model, reasoning depth, tools and fallback. It never owns authorization or business data.
_Avoid_: AI provider

**Analytical Service**:
A deterministic calculation service for spreads, time series, volatility, correlation and forecast evaluation.
_Avoid_: AI calculator

**Audit Log**:
An append-only record of security-relevant actions with actor, action, object, time and result.
_Avoid_: Activity feed
