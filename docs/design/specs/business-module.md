# Business module — BSR Market Intelligence

## Core entities

| Entity | What the user sees | Key states |
|---|---|---|
| Market Observation | Instrument value with unit, source, market time, ingestion time | Real-time / Delayed / EOD / Manual; Valid / Pending / Rejected / Corrected |
| Instrument | Brent, WTI, RON95, Diesel, Jet A-1, Fuel Oil, USD/VND, DXY, crack spreads | Futures / Physical / Index / Calculated |
| Crack Spread | Product minus crude benchmark, formula version and inputs | Valid / Rejected (mixed price types) |
| News Item | Headline, source, published time, topics, summary, original link | Processing / Processed / Duplicate candidate / Failed |
| Event | Market-moving occurrence linked to news and instruments | Confirmed / Developing |
| Forecast Version | Source projection for instrument and horizon | Current / Superseded |
| Forecast Evaluation | Error metrics against actuals | Complete / Missing actual |
| Analysis | Versioned interpretation with evidence and assumptions | Draft / Published |
| Recommendation | Decision-support option with confidence and uncertainty | Open / Reviewed |
| Report | Briefing with data cut-off, sources and version | Draft / Final |
| AI Execution | Auditable AI run | Succeeded / Fallback / Failed / Validation failed |
| Audit Log | Actor, action, object, time, result | Append-only |

## Decisions and information priority

1. **"What changed since I last looked?"** → market tape, 24h briefing, highlights, freshness.
2. **"Is this number trustworthy?"** → source, market vs ingestion time, data status, quality status, classification.
3. **"What is driving the move?"** → key drivers grouped by supply, demand, geopolitics, logistics; linked news.
4. **"What is the economics?"** → crack spread with formula version and inputs; time-series context.
5. **"Which source adds value?"** → coverage comparison, duplicate links, unique details, publication times.
6. **"How good are the forecasts?"** → versioned forecasts, actuals, MAE/MAPE/bias by source and horizon.
7. **"Can I share this?"** → report version, data cut-off, source ledger, export permission.
8. **"Can I trust the AI?"** → citations, tool trace, fact/calculation/interpretation labels, uncertainty.

## Meaningful metrics

- Absolute and percentage change over the selected period.
- Crack spread in USD/bbl with formula ID/version.
- Forecast error: absolute error, percentage error, MAE, MAPE, bias.
- Data freshness: age of market timestamp and ingestion timestamp.
- Coverage: number of sources and unique details per event (never a trust score).
- AI execution: latency, cost, validation status, retry count.

## Permission model

- Roles: Leadership, Market Intelligence, Internal.
- Classifications: Public, Internal, Confidential, Restricted.
- Restricted physical prices are visible only to explicitly entitled users; export is a separate permission.
- The UI hides unauthorized data, and the backend enforces the same rule for pages, APIs, AI retrieval and exports.
