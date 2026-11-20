# Design manifesto — BSR Market Intelligence

## Task and priorities

A permission-aware market-intelligence workspace for BSR. The primary job is to help a user answer, in one place: *what moved, why, what is the evidence, and what should I watch next?* Priorities: provenance and freshness first, analytical density second, AI assistance third. AI output must never look like source fact.

## Direction

**Research desk, not trading terminal.** A warm paper surface, deep petrol navigation and copper accents create the feel of an analyst's briefing book rather than a generic dark dashboard. Editorial serif headings give the product a research-grade voice; compact sans body and monospaced figures keep dense market data precise. Thin rules, restrained shadows and generous section rhythm replace card-grid noise.

## Reuse / adapt / explore

- **Reuse:** left navigation with collapse, metric cards with sparklines, time-series charts with event markers, source-attributed news feed, chat with citations, report version list. These are brief requirements and familiar financial-workspace patterns.
- **Adapt:** metric cards become "market tape" cells with explicit data status and timestamps; the AI briefing is a bordered research note with a version and source ledger, not a chat bubble; permission state is visible in the shell, not hidden in settings.
- **Explore:** a "provenance rail" on the right of analytical screens that keeps source, freshness and uncertainty visible while the user works. A single warm accent is used for attention and selection, while semantic green/red are reserved for market direction.

## Tradeoffs

- Dense information is intentional; whitespace is used to group, not to inflate.
- No photographic imagery: the product is an operational data workspace, and invented facility photography would imply unverified assets. Charts, typographic hierarchy and a subtle grid texture carry the visual identity.
- The prototype uses synthetic demo data, clearly labelled. It does not claim live market coverage or real BSR figures.
- Desktop-first; narrow layouts collapse the sidebar and stack panels, preserving the market tape and primary actions.

## Evidence

No external UI study was used. The brief's navigation, module and interaction requirements control. Rendered prototype and review evidence live under `docs/design/`.
