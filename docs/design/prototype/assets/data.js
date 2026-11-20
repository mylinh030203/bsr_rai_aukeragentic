/* Synthetic demo data for the BSR Market Intelligence design prototype. */
(function () {
  const DAY = 86400000;
  const end = new Date('2026-11-14T09:42:00+07:00');

  function series(base, drift, vol, seed, n) {
    const out = [];
    let value = base;
    for (let i = n - 1; i >= 0; i--) {
      const t = (n - i) / n;
      const noise = Math.sin((i + seed) * 1.31) * vol + Math.cos((i + seed * 2.1) * 0.43) * vol * 0.55;
      value = base * (1 - drift * t) + noise + Math.sin(i * 0.11 + seed) * base * 0.012;
      out.push({ date: new Date(end.getTime() - i * DAY), value: Math.round(value * 100) / 100 });
    }
    out[out.length - 1].value = base;
    return out;
  }

  const instruments = [
    {
      id: 'brent_futures', name: 'Brent Crude Futures', short: 'Brent', group: 'Crude oil', ticker: 'BRN',
      value: 78.42, unit: 'USD/bbl', priceType: 'Futures', source: 'ICE (demo)', sourceId: 'SRC-ICE',
      marketTime: '14 Nov 2026 · 08:30 ICT', ingestionTime: '14 Nov 2026 · 08:30 ICT',
      dataStatus: 'Real-time', quality: 'Valid', classification: 'Internal', decimals: 2,
      change: 2.06, pct: 2.7, spark: series(78.42, 0.02, 1.6, 3, 40), series: series(78.42, 0.02, 1.8, 3, 365),
      description: 'Front-month Brent futures, ICE. Demo series illustrative of market shape.'
    },
    {
      id: 'wti_futures', name: 'WTI Crude Futures', short: 'WTI', group: 'Crude oil', ticker: 'CL',
      value: 74.18, unit: 'USD/bbl', priceType: 'Futures', source: 'CME (demo)', sourceId: 'SRC-CME',
      marketTime: '14 Nov 2026 · 08:28 ICT', ingestionTime: '14 Nov 2026 · 08:28 ICT',
      dataStatus: 'Real-time', quality: 'Valid', classification: 'Internal', decimals: 2,
      change: 0.52, pct: 0.71, spark: series(74.18, 0.015, 1.3, 7, 40), series: series(74.18, 0.015, 1.4, 7, 365),
      description: 'Front-month WTI futures, CME. Demo series illustrative of market shape.'
    },
    {
      id: 'brent_physical', name: 'Brent Physical Dated', short: 'Brent Dated', group: 'Crude oil', ticker: 'BRD',
      value: 77.9, unit: 'USD/bbl', priceType: 'Physical', source: 'Platts (demo)', sourceId: 'SRC-PLATTS',
      marketTime: '13 Nov 2026 · 18:30 ICT', ingestionTime: '14 Nov 2026 · 07:05 ICT',
      dataStatus: 'End-of-day', quality: 'Valid', classification: 'Restricted', decimals: 2,
      change: 0.8, pct: 1.04, spark: series(77.9, 0.018, 1.5, 11, 40), series: series(77.9, 0.018, 1.6, 11, 365),
      description: 'Dated Brent physical assessment. Restricted commercial data.'
    },
    {
      id: 'ron95', name: 'Gasoline RON95 (FOB Singapore)', short: 'RON95', group: 'Refined products', ticker: 'RON95',
      value: 92.1, unit: 'USD/bbl', priceType: 'Physical', source: 'Platts (demo)', sourceId: 'SRC-PLATTS',
      marketTime: '13 Nov 2026 · 18:30 ICT', ingestionTime: '14 Nov 2026 · 07:05 ICT',
      dataStatus: 'End-of-day', quality: 'Valid', classification: 'Internal', decimals: 2,
      change: -0.45, pct: -0.49, spark: series(92.1, -0.01, 1.9, 15, 40), series: series(92.1, -0.01, 2.0, 15, 365),
      description: 'Gasoline RON95 FOB Singapore assessment used for crack reference.'
    },
    {
      id: 'diesel', name: 'Diesel 10ppm (FOB Singapore)', short: 'Diesel', group: 'Refined products', ticker: 'DIESEL',
      value: 96.4, unit: 'USD/bbl', priceType: 'Physical', source: 'Platts (demo)', sourceId: 'SRC-PLATTS',
      marketTime: '13 Nov 2026 · 18:30 ICT', ingestionTime: '14 Nov 2026 · 07:05 ICT',
      dataStatus: 'End-of-day', quality: 'Valid', classification: 'Internal', decimals: 2,
      change: 0.3, pct: 0.31, spark: series(96.4, 0.01, 1.7, 19, 40), series: series(96.4, 0.01, 1.8, 19, 365),
      description: 'Diesel 10ppm FOB Singapore assessment.'
    },
    {
      id: 'jet', name: 'Jet Fuel A-1 (FOB Singapore)', short: 'Jet A-1', group: 'Refined products', ticker: 'JET',
      value: 99.2, unit: 'USD/bbl', priceType: 'Physical', source: 'Platts (demo)', sourceId: 'SRC-PLATTS',
      marketTime: '13 Nov 2026 · 18:30 ICT', ingestionTime: '14 Nov 2026 · 07:05 ICT',
      dataStatus: 'End-of-day', quality: 'Valid', classification: 'Internal', decimals: 2,
      change: 0.55, pct: 0.56, spark: series(99.2, 0.012, 1.9, 23, 40), series: series(99.2, 0.012, 2.0, 23, 365),
      description: 'Jet Fuel A-1 FOB Singapore assessment.'
    },
    {
      id: 'fuel_oil', name: 'Fuel Oil 180 CST (FOB Singapore)', short: 'Fuel oil', group: 'Refined products', ticker: 'FO180',
      value: 68.3, unit: 'USD/bbl', priceType: 'Physical', source: 'Platts (demo)', sourceId: 'SRC-PLATTS',
      marketTime: '13 Nov 2026 · 18:30 ICT', ingestionTime: '14 Nov 2026 · 07:05 ICT',
      dataStatus: 'End-of-day', quality: 'Pending', classification: 'Internal', decimals: 2,
      change: -0.2, pct: -0.29, spark: series(68.3, -0.005, 1.1, 27, 40), series: series(68.3, -0.005, 1.2, 27, 365),
      description: 'Fuel oil 180 CST FOB Singapore. Quality check pending.'
    },
    {
      id: 'usd_vnd', name: 'USD/VND', short: 'USD/VND', group: 'FX & macro', ticker: 'USDVND',
      value: 25480, unit: 'VND', priceType: 'Exchange rate', source: 'SBV (demo)', sourceId: 'SRC-SBV',
      marketTime: '14 Nov 2026 · 09:00 ICT', ingestionTime: '14 Nov 2026 · 09:00 ICT',
      dataStatus: 'Delayed', quality: 'Valid', classification: 'Internal', decimals: 0,
      change: 35, pct: 0.14, spark: series(25480, 0.004, 90, 31, 40).map(p => ({ ...p, value: Math.round(p.value) })), series: series(25480, 0.004, 90, 31, 365).map(p => ({ ...p, value: Math.round(p.value) })),
      description: 'State Bank of Vietnam reference rate. Delayed demo feed.'
    },
    {
      id: 'dxy', name: 'US Dollar Index', short: 'DXY', group: 'FX & macro', ticker: 'DXY',
      value: 104.12, unit: 'index', priceType: 'Index', source: 'ICE (demo)', sourceId: 'SRC-ICE',
      marketTime: '14 Nov 2026 · 08:20 ICT', ingestionTime: '14 Nov 2026 · 08:22 ICT',
      dataStatus: 'Delayed', quality: 'Valid', classification: 'Internal', decimals: 2,
      change: -0.18, pct: -0.17, spark: series(104.12, -0.002, 0.5, 35, 40), series: series(104.12, -0.002, 0.55, 35, 365),
      description: 'US Dollar Index, delayed demo feed.'
    },
    {
      id: 'crack_gasoline', name: 'Gasoline Crack Spread', short: 'Gasoline crack', group: 'Crack spreads', ticker: 'CS-GAS',
      value: 18.35, unit: 'USD/bbl', priceType: 'Calculated', source: 'BSR Analytical', sourceId: 'SRC-BSR-AN',
      marketTime: '13 Nov 2026 · 18:30 ICT', ingestionTime: '14 Nov 2026 · 07:06 ICT',
      dataStatus: 'End-of-day', quality: 'Valid', classification: 'Internal', decimals: 2,
      change: 0.65, pct: 3.67, spark: series(18.35, 0.03, 0.9, 39, 40), series: series(18.35, 0.03, 1.0, 39, 365),
      description: 'Gasoline crack versus Brent futures. Formula CS-GAS-2.1, no price-type mixing.',
      formula: { id: 'CS-GAS-2.1', inputs: ['RON95 (FOB Singapore)', 'Brent Crude Futures'], rule: 'RON95 physical − Brent futures. Converted to USD/bbl.' }
    },
    {
      id: 'crack_diesel', name: 'Diesel Crack Spread', short: 'Diesel crack', group: 'Crack spreads', ticker: 'CS-DSL',
      value: 21.1, unit: 'USD/bbl', priceType: 'Calculated', source: 'BSR Analytical', sourceId: 'SRC-BSR-AN',
      marketTime: '13 Nov 2026 · 18:30 ICT', ingestionTime: '14 Nov 2026 · 07:06 ICT',
      dataStatus: 'End-of-day', quality: 'Valid', classification: 'Internal', decimals: 2,
      change: -0.24, pct: -1.12, spark: series(21.1, 0.015, 0.8, 43, 40), series: series(21.1, 0.015, 0.9, 43, 365),
      description: 'Diesel crack versus Brent futures. Formula CS-DSL-2.0.',
      formula: { id: 'CS-DSL-2.0', inputs: ['Diesel 10ppm (FOB Singapore)', 'Brent Crude Futures'], rule: 'Diesel physical − Brent futures. Converted to USD/bbl.' }
    },
    {
      id: 'crack_321', name: '3-2-1 Composite Crack', short: '3-2-1 crack', group: 'Crack spreads', ticker: 'CS-321',
      value: 19.4, unit: 'USD/bbl', priceType: 'Calculated', source: 'BSR Analytical', sourceId: 'SRC-BSR-AN',
      marketTime: '13 Nov 2026 · 18:30 ICT', ingestionTime: '14 Nov 2026 · 07:06 ICT',
      dataStatus: 'End-of-day', quality: 'Valid', classification: 'Internal', decimals: 2,
      change: 0.41, pct: 2.16, spark: series(19.4, 0.02, 0.8, 47, 40), series: series(19.4, 0.02, 0.9, 47, 365),
      description: 'Illustrative 3-2-1 composite using two gasoline barrels and one diesel barrel against three crude barrels.',
      formula: { id: 'CS-321-1.3', inputs: ['RON95', 'Diesel', 'Brent futures'], rule: '(2 × gasoline + 1 × diesel − 3 × Brent) / 3. Demo formula.' }
    },
    {
      id: 'bsr_margin', name: 'BSR Indicative Refining Margin', short: 'BSR margin', group: 'Refinery operations', ticker: 'BSR-M',
      value: 8.24, unit: 'USD/bbl', priceType: 'Calculated', source: 'BSR Internal', sourceId: 'SRC-BSR-IN',
      marketTime: '13 Nov 2026 · 17:00 ICT', ingestionTime: '13 Nov 2026 · 17:04 ICT',
      dataStatus: 'Manual', quality: 'Valid', classification: 'Confidential', decimals: 2,
      change: 0.34, pct: 4.3, spark: series(8.24, 0.02, 0.5, 51, 40), series: series(8.24, 0.02, 0.55, 51, 365),
      description: 'Indicative internal refining margin. Confidential; illustrative only.'
    }
  ];

  const events = [
    { date: '2026-10-06', title: 'OPEC+ agrees November output path', type: 'Policy', instruments: ['brent_futures', 'wti_futures'], source: 'Reuters (demo)' },
    { date: '2026-10-19', title: 'Red Sea freight disruption widens', type: 'Logistics', instruments: ['brent_futures', 'diesel'], source: 'Platts (demo)' },
    { date: '2026-11-03', title: 'Dung Quat unit maintenance begins', type: 'Refining', instruments: ['crack_gasoline', 'bsr_margin'], source: 'BSR Internal' },
    { date: '2026-11-11', title: 'US crude inventories fall more than expected', type: 'Inventory', instruments: ['wti_futures', 'brent_futures'], source: 'EIA (demo)' }
  ];

  const drivers = [
    { group: 'Supply', label: 'OPEC+ discipline', detail: 'Voluntary cuts extended through Q4; compliance signal firming.', direction: 'tightening', strength: 82 },
    { group: 'Supply', label: 'Middle East risk', detail: 'Shipping insurance costs elevated along the Gulf routes.', direction: 'tightening', strength: 68 },
    { group: 'Demand', label: 'Asia gasoline demand', detail: 'Regional cracks supported by resilient mobility demand.', direction: 'firming', strength: 61 },
    { group: 'Demand', label: 'Industrial diesel demand', detail: 'Soft manufacturing prints cap upside in middle distillates.', direction: 'softening', strength: 47 },
    { group: 'Logistics', label: 'Freight & insurance', detail: 'Red Sea diversions keep product arb windows uneven.', direction: 'tightening', strength: 57 },
    { group: 'Macro', label: 'USD / VND', detail: 'Stable reference rate reduces imported-cost volatility.', direction: 'neutral', strength: 36 }
  ];

  const highlights = [
    { title: 'Brent holds above $78 as supply risk offsets demand caution', meta: 'Reuters · 14 Nov 2026, 08:10 ICT', topics: ['Crude supply', 'Geopolitics'], source: 'Reuters (demo)', type: 'Source fact' },
    { title: 'Gasoline crack widens on stronger Asian blending demand', meta: 'Platts · 13 Nov 2026, 19:05 ICT', topics: ['Refined products', 'Asia demand'], source: 'Platts (demo)', type: 'Source fact' },
    { title: 'AI read: product cracks are doing more work than crude direction', meta: 'AI interpretation · 14 Nov 2026, 09:15 ICT', topics: ['Cross-market'], source: 'Deterministic inputs + cited news', type: 'AI interpretation' }
  ];

  const news = [
    {
      id: 'N-2411', title: 'OPEC+ signals patience on output as Brent tests $78', source: 'Reuters (demo)', published: '14 Nov 2026 · 07:50 ICT', ingested: '14 Nov 2026 · 08:02 ICT',
      topics: ['OPEC+', 'Crude supply'], entities: ['OPEC+', 'Brent'], classification: 'Internal', status: 'Processed', relevance: 94,
      summary: 'Delegates indicated the group is unlikely to accelerate unwinding voluntary cuts before the next ministerial meeting, keeping near-term supply expectations tight.',
      original: 'Sourced reporting placeholder for the prototype. The original article remains accessible from the licensed provider in production.',
      insight: 'AI interpretation: the signal supports the front of the Brent curve, but the market reaction is modest because the decision was partly expected.',
      linked: ['brent_futures', 'wti_futures'], duplicateOf: null, coverage: '3 sources · 2 unique details',
      /* Six timestamp types (requirements v2.0). Synthetic demo values. */
      timestamps: {
        marketTime: '14 Nov 2026 · 07:48 ICT',
        eventTime: '13 Nov 2026 · 18:00 ICT',
        publicationTime: '14 Nov 2026 · 07:50 ICT',
        ingestionTime: '14 Nov 2026 · 08:02 ICT',
        processingTime: '14 Nov 2026 · 08:04 ICT',
        creationTime: '14 Nov 2026 · 08:05 ICT'
      },
      lineage: [
        { step: 'Source', value: 'Reuters (demo) · wire article' },
        { step: 'Processing path', value: 'Intake → validation → extraction → normalisation → deduplication → classification → entity/event → summary → market link → store/index' },
        { step: 'Inputs used', value: 'Article text, publication time, entity list (OPEC+, Brent), linked series brent_futures and wti_futures' },
        { step: 'Formula / method', value: 'Relevance scoring v1.2 (demo) · no market calculation applied' },
        { step: 'AI execution', value: 'AI-8F19 · news_summarization · demo-orchestrator/small' },
        { step: 'Version', value: 'News item v1 · not revised' }
      ]
    },
    {
      id: 'N-2410', title: 'Red Sea diversions add a week to Gulf–Asia product voyages', source: 'Platts (demo)', published: '14 Nov 2026 · 06:40 ICT', ingested: '14 Nov 2026 · 06:58 ICT',
      topics: ['Shipping & freight', 'Refined products'], entities: ['Red Sea', 'Singapore'], classification: 'Internal', status: 'Processed', relevance: 88,
      summary: 'Freight assessments for Gulf–Asia routes rose again as operators extended diversions, tightening effective product availability in the east.',
      original: 'Sourced reporting placeholder for the prototype.',
      insight: 'AI interpretation: the freight move is more material for product arb economics than for absolute crude direction.',
      linked: ['diesel', 'jet'], duplicateOf: null, coverage: '4 sources · 3 unique details',
      timestamps: {
        marketTime: '14 Nov 2026 · 06:30 ICT',
        eventTime: '13 Nov 2026 · 12:00 ICT',
        publicationTime: '14 Nov 2026 · 06:40 ICT',
        ingestionTime: '14 Nov 2026 · 06:58 ICT',
        processingTime: '14 Nov 2026 · 07:01 ICT',
        creationTime: '14 Nov 2026 · 07:02 ICT'
      },
      lineage: [
        { step: 'Source', value: 'Platts (demo) · freight assessment note' },
        { step: 'Processing path', value: 'Intake → validation → extraction → normalisation → deduplication → classification → entity/event → summary → market link → store/index' },
        { step: 'Inputs used', value: 'Assessment text, route list (Gulf–Asia), linked series diesel and jet' },
        { step: 'Formula / method', value: 'Relevance scoring v1.2 (demo) · no market calculation applied' },
        { step: 'AI execution', value: 'AI-8F19 · news_summarization · demo-orchestrator/small' },
        { step: 'Version', value: 'News item v1 · not revised' }
      ]
    },
    {
      id: 'N-2409', title: 'US crude inventories fall more than expected: EIA', source: 'EIA (demo)', published: '13 Nov 2026 · 22:30 ICT', ingested: '13 Nov 2026 · 22:41 ICT',
      topics: ['Inventory', 'Crude demand'], entities: ['United States', 'WTI'], classification: 'Public', status: 'Processed', relevance: 76,
      summary: 'Commercial crude stocks declined while gasoline inventories built modestly, a mixed signal for the crude–product complex.',
      original: 'Sourced reporting placeholder for the prototype.',
      insight: 'AI interpretation: crude draws support flat price, but the product build limits the read-through to cracks.',
      linked: ['wti_futures', 'crack_gasoline'], duplicateOf: null, coverage: '2 sources · 1 unique detail'
    },
    {
      id: 'N-2408', title: 'Dung Quat begins planned maintenance on CDU', source: 'BSR Internal', published: '13 Nov 2026 · 16:20 ICT', ingested: '13 Nov 2026 · 16:25 ICT',
      topics: ['Refining operations'], entities: ['Dung Quat', 'BSR'], classification: 'Confidential', status: 'Processed', relevance: 91,
      summary: 'A planned crude distillation unit maintenance window begins, with product output and crude intake adjusted according to the internal plan.',
      original: 'Internal operations note (demo placeholder).',
      insight: 'AI interpretation: the maintenance window is already reflected in the internal plan; monitor product cracks for unintended tightening.',
      linked: ['bsr_margin', 'crack_gasoline'], duplicateOf: null, coverage: '1 source · 2 unique details'
    },
    {
      id: 'N-2407', title: 'OPEC+ keeps output path steady, delegates say', source: 'Bloomberg (demo)', published: '14 Nov 2026 · 07:58 ICT', ingested: '14 Nov 2026 · 08:06 ICT',
      topics: ['OPEC+', 'Crude supply'], entities: ['OPEC+', 'Brent'], classification: 'Internal', status: 'Duplicate candidate', relevance: 93,
      summary: 'A near-identical account of the OPEC+ signal, adding one detail on the next ministerial date.',
      original: 'Sourced reporting placeholder for the prototype.',
      insight: 'AI interpretation: duplicate candidate linked to N-2411. Adds the ministerial date, so the source is retained and linked, not removed.',
      linked: ['brent_futures'], duplicateOf: 'N-2411', coverage: 'Linked to N-2411 · 1 additive detail'
    },
    {
      id: 'N-2406', title: 'Asian refiners trim spot crude purchases for December', source: 'Reuters (demo)', published: '13 Nov 2026 · 14:10 ICT', ingested: '13 Nov 2026 · 14:23 ICT',
      topics: ['Crude demand', 'Asia demand'], entities: ['Asia', 'Brent'], classification: 'Internal', status: 'Processed', relevance: 72,
      summary: 'Several regional refiners reduced December spot requirements, pointing to softer near-term crude demand in Asia.',
      original: 'Sourced reporting placeholder for the prototype.',
      insight: 'AI interpretation: a demand-side offset to the supply narrative; keep it in the watch list rather than the base case.',
      linked: ['brent_futures', 'diesel'], duplicateOf: null, coverage: '2 sources · 1 unique detail'
    },
    {
      id: 'N-2405', title: 'Platts physical Brent assessment: dated cargoes firm', source: 'Platts (demo)', published: '13 Nov 2026 · 18:30 ICT', ingested: '14 Nov 2026 · 07:05 ICT',
      topics: ['Crude supply', 'Refining operations'], entities: ['Brent', 'North Sea'], classification: 'Restricted', status: 'Processed', relevance: 85,
      summary: 'Restricted physical assessment detail. Visible only to roles with Restricted access.',
      original: 'Licensed physical assessment placeholder.',
      insight: 'AI interpretation is withheld from unauthorized roles at retrieval time.',
      linked: ['brent_physical'], duplicateOf: null, coverage: 'Restricted source'
    }
  ];

  const forecasts = [
    { id: 'F-101', source: 'EIA (demo)', instrument: 'brent_futures', instrumentLabel: 'Brent Crude Futures', value: 79.5, period: 'Q1 2027', horizon: '3-month', published: '12 Nov 2026', ingested: '12 Nov 2026', version: 3, methodology: 'STEO baseline', classification: 'Internal', actual: 77.35, previous: 80.2 },
    { id: 'F-102', source: 'IEA (demo)', instrument: 'brent_futures', instrumentLabel: 'Brent Crude Futures', value: 77.8, period: 'Q1 2027', horizon: '3-month', published: '10 Nov 2026', ingested: '10 Nov 2026', version: 2, methodology: 'Balances + inventory model', classification: 'Internal', actual: null, previous: 78.4 },
    { id: 'F-103', source: 'Platts (demo)', instrument: 'ron95', instrumentLabel: 'Gasoline RON95', value: 93.4, period: 'Dec 2026', horizon: '1-month', published: '13 Nov 2026', ingested: '13 Nov 2026', version: 4, methodology: 'Analytics spot outlook', classification: 'Internal', actual: 91.7, previous: 92.9 },
    { id: 'F-104', source: 'BSR Internal', instrument: 'crack_gasoline', instrumentLabel: 'Gasoline Crack Spread', value: 17.9, period: 'Dec 2026', horizon: '1-month', published: '11 Nov 2026', ingested: '11 Nov 2026', version: 1, methodology: 'Demo internal scenario', classification: 'Confidential', actual: 18.35, previous: null },
    { id: 'F-105', source: 'IEA (demo)', instrument: 'wti_futures', instrumentLabel: 'WTI Crude Futures', value: 72.6, period: 'Q1 2027', horizon: '3-month', published: '10 Nov 2026', ingested: '10 Nov 2026', version: 2, methodology: 'Balances + inventory model', classification: 'Internal', actual: 73.66, previous: 73.9 },
    { id: 'F-106', source: 'EIA (demo)', instrument: 'wti_futures', instrumentLabel: 'WTI Crude Futures', value: 74.1, period: 'Q1 2027', horizon: '3-month', published: '12 Nov 2026', ingested: '12 Nov 2026', version: 3, methodology: 'STEO baseline', classification: 'Internal', actual: null, previous: 75.0 }
  ];

  const reports = [
    { id: 'R-2026-041', type: 'Morning Briefing', title: 'Morning briefing — supply risk meets product strength', range: '13–14 Nov 2026', created: '14 Nov 2026 · 09:20 ICT', cutOff: '14 Nov 2026 · 09:15 ICT', version: 2, requester: 'Lê Minh Anh', status: 'Final', classification: 'Internal', sources: ['SRC-ICE', 'SRC-PLATTS', 'SRC-NEWS-2411', 'SRC-NEWS-2410'] },
    { id: 'R-2026-040', type: 'Weekly Market Report', title: 'Week 46 — cracks carry the narrative', range: '9–15 Nov 2026', created: '13 Nov 2026 · 17:40 ICT', cutOff: '13 Nov 2026 · 17:30 ICT', version: 1, requester: 'Lê Minh Anh', status: 'Final', classification: 'Internal', sources: ['SRC-ICE', 'SRC-CME', 'SRC-PLATTS'] },
    { id: 'R-2026-039', type: 'Event-driven Analysis', title: 'Hormuz disruption — exposure and watch list', range: '1–12 Nov 2026', created: '12 Nov 2026 · 15:10 ICT', cutOff: '12 Nov 2026 · 15:00 ICT', version: 1, requester: 'Nguyễn Thu Hà', status: 'Final', classification: 'Confidential', sources: ['SRC-ICE', 'SRC-NEWS-2410', 'SRC-BSR-AN'] }
  ];

  const audit = [
    { time: '14 Nov 2026 · 09:42 ICT', actor: 'Lê Minh Anh', role: 'Leadership', action: 'AI request', object: 'AI-8F2A · market_briefing', result: 'Succeeded', classification: 'Internal' },
    { time: '14 Nov 2026 · 09:20 ICT', actor: 'Lê Minh Anh', role: 'Leadership', action: 'Report generated', object: 'R-2026-041 v2', result: 'Succeeded', classification: 'Internal' },
    { time: '14 Nov 2026 · 09:05 ICT', actor: 'Nguyễn Thu Hà', role: 'Market Intelligence', action: 'Restricted data viewed', object: 'brent_physical', result: 'Allowed', classification: 'Restricted' },
    { time: '14 Nov 2026 · 08:58 ICT', actor: 'Nguyễn Thu Hà', role: 'Market Intelligence', action: 'News uploaded', object: 'N-2411', result: 'Succeeded', classification: 'Internal' },
    { time: '14 Nov 2026 · 08:31 ICT', actor: 'Trần Quốc Bảo', role: 'Internal', action: 'Restricted data requested', object: 'brent_physical', result: 'Denied', classification: 'Restricted' },
    { time: '14 Nov 2026 · 08:02 ICT', actor: 'system', role: 'Pipeline', action: 'News processed', object: 'N-2411', result: 'Succeeded', classification: 'Internal' }
  ];

  const aiExecutions = [
    { task: 'AI-8F2A', type: 'market_briefing', model: 'demo-orchestrator/large', reasoning: 'deep', tools: 4, latency: '2.8s', cost: '$0.041', status: 'Succeeded', validation: 'Passed' },
    { task: 'AI-8F19', type: 'news_summarization', model: 'demo-orchestrator/small', reasoning: 'standard', tools: 2, latency: '1.4s', cost: '$0.008', status: 'Succeeded', validation: 'Passed' },
    { task: 'AI-8F11', type: 'chat_query', model: 'demo-orchestrator/standard', reasoning: 'standard', tools: 3, latency: '2.1s', cost: '$0.018', status: 'Fallback', validation: 'Passed' },
    { task: 'AI-8EF0', type: 'chat_query', model: 'demo-orchestrator/small', reasoning: 'simple', tools: 2, latency: '0.9s', cost: '$0.004', status: 'Succeeded', validation: 'Passed' }
  ];

  const coverage = [
    { topic: 'OPEC+ output signal', sources: ['Reuters', 'Bloomberg'], shared: 'Extension of voluntary cuts; next ministerial date', unique: 'Bloomberg adds the ministerial date; Reuters adds delegate count', articles: 2 },
    { topic: 'Red Sea freight', sources: ['Platts', 'Reuters'], shared: 'Diversions and rising insurance costs', unique: 'Platts adds Gulf–Asia freight route assessments', articles: 2 },
    { topic: 'US inventories', sources: ['EIA'], shared: 'Crude draw, gasoline build', unique: 'Weekly inventory levels and product breakdown', articles: 1 }
  ];

  const analysis = {
    question: 'What is driving the recent move in product cracks, and what should BSR watch next?',
    asOf: '14 Nov 2026 · 09:30 ICT',
    facts: [
      'Gasoline crack (CS-GAS-2.1) is $18.35/bbl, +3.67% from 12 Nov (17.70), the last two stored sessions.',
      'Brent futures are $78.42/bbl, +2.70% from 12 Nov (76.36); WTI is $74.18/bbl, +0.71%.',
      'Red Sea freight assessments have risen for a second week.'
    ],
    calculations: [
      { label: '5-day return, Brent', value: '+2.1%', method: 'close-to-close, 5 sessions' },
      { label: '20-day realised volatility, Brent', value: '24.6%', method: 'annualised stdev of daily log returns' },
      { label: 'Brent–WTI spread', value: '$4.24/bbl', method: 'Brent futures − WTI futures' },
      { label: 'Gasoline crack change', value: '+$0.62/bbl', method: 'CS-GAS-2.1, session change' }
    ],
    assumptions: [
      'Demo series are illustrative and are not official BSR or Platts assessments.',
      'The freight signal is treated as a product-arbitrage input, not proof of crude supply loss.',
      'No restricted physical assessment is included for unauthorized roles.'
    ],
    recommendation: {
      title: 'Keep product cracks as the primary watch item; do not extrapolate a crude-supply shock from the freight move alone.',
      confidence: 'Medium',
      rationale: 'The crack move is supported by product-specific freight and Asian blending demand, while crude flat price remains range-bound. The evidence supports a watch stance, not a trading instruction.',
      watch: ['Gasoline crack vs 20-day average', 'Red Sea freight assessments', 'OPEC+ ministerial commentary', 'Dung Quat maintenance progress'],
      /* Seven-field recommendation contract (requirements v2.0). Synthetic demo content. */
      context: 'Gasoline crack CS-GAS-2.1 has firmed for two sessions while Brent stays range-bound between $77 and $79; the question is whether the product move is a durable signal or a freight-driven spike.',
      dataSources: 'ICE Brent futures (demo), CME WTI futures (demo), Platts RON95 and diesel assessments (demo), Reuters OPEC+ reporting (demo), Platts Red Sea freight assessments (demo), formula CS-GAS-2.1.',
      reasoning: 'Product cracks rose while crude flat price held. Freight assessments for Gulf–Asia routes rose for a second week and Asian blending demand is described as resilient, so the product-specific evidence carries the signal rather than a crude-supply thesis.',
      assumptions: ['Freight disruption persists through the next assessment window.', 'No unplanned crude supply loss is assumed.', 'Demo series are illustrative and not official BSR or Platts assessments.'],
      uncertainties: 'The duration of the freight disruption and its read-through to crude supply are not established. A single two-session move is a thin sample for a trend claim.',
      confidenceDetail: 'Medium confidence: source-confirmed freight and crack observations, but a short sample and no independent confirmation of duration.',
      timing: 'Created 14 Nov 2026 · 09:30 ICT · data cut-off 14 Nov 2026 · 09:15 ICT',
      version: 'Analysis v1 · formula CS-GAS-2.1 · AI execution AI-8F2A'
    },
    /* Seven standard Market Impact Analysis questions (requirements v2.0). One demo line per question. */
    marketImpact: [
      { q: 'Which products or valuations are affected?', a: 'Gasoline crack (CS-GAS-2.1) and diesel crack first; Brent and WTI flat price only indirectly.' },
      { q: 'How large is the impact, quantified?', a: 'Gasoline crack +3.67% and Brent +2.70% between the last two stored sessions (12 Nov → 14 Nov); Brent–WTI spread $4.24/bbl.' },
      { q: 'What price zone or range applies?', a: 'Brent $77–$79 range; gasoline crack watch band $17.20–$18.60/bbl around the 20-day average.' },
      { q: 'Is this an event or a fundamental parameter?', a: 'A freight event layered on a product-fundamental trend; the crude fundamental balance is unchanged in this demo.' },
      { q: 'Which data release dates must be watched?', a: 'EIA weekly inventories (next release 19 Nov 2026), next OPEC+ ministerial date, weekly Platts freight assessments.' },
      { q: 'What are the limits of this conclusion?', a: 'Two-session sample, synthetic data, no licensed physical assessment for unauthorized roles, correlation is not causation.' },
      { q: 'What would be needed to validate it?', a: 'A third week of freight assessments, an independent source on route duration, and a recorded actual to score the forecast version.' }
    ],
    /* Geopolitical intelligence scope (requirements v2.0). Synthetic demo items. */
    geopolitical: [
      { area: 'OPEC+ decisions', detail: 'Delegates signal patience on unwinding voluntary cuts; next ministerial date is the trigger to watch.', linked: 'Brent, WTI', risk: 'Medium' },
      { area: 'Sanction risk', detail: 'Demo scenario: tighter secondary-sanction scrutiny on a crude exporter would raise freight and insurance costs.', linked: 'Brent Dated, freight', risk: 'Medium' },
      { area: 'Chokepoint and shipping', detail: 'Red Sea diversions add about a week to Gulf–Asia product voyages; Hormuz remains open in this demo.', linked: 'Diesel, jet', risk: 'High' },
      { area: 'Energy policy shift', detail: 'Demo scenario: a refining-capacity policy change in Asia would shift product arb economics rather than crude direction.', linked: 'RON95, fuel oil', risk: 'Low' }
    ]
  };

  /* AI Evaluation rubric — the ten groups named by requirements v2.0. Scores are synthetic demo values. */
  const aiRubric = [
    { id: 'factual-accuracy', label: 'Factual Accuracy', score: 4.4, max: 5, note: 'Stated observations match the stored series; no invented prices.' },
    { id: 'source-grounding', label: 'Source Grounding', score: 4.6, max: 5, note: 'Every factual claim carries a permitted source reference.' },
    { id: 'extraction-accuracy', label: 'Extraction Accuracy', score: 4.1, max: 5, note: 'Entity and topic extraction checked against a demo sample of news items.' },
    { id: 'summarization-quality', label: 'Summarization Quality', score: 4.2, max: 5, note: 'Summaries keep the source attribution and do not present generated text as the article.' },
    { id: 'financial-reasoning', label: 'Financial Reasoning', score: 3.8, max: 5, note: 'Interpretation is separated from deterministic calculation; weaker on multi-step inference.' },
    { id: 'tool-selection', label: 'Tool Selection', score: 4.3, max: 5, note: 'Registered tools chosen for the task; one fallback run recorded.' },
    { id: 'task-completion', label: 'Task Completion', score: 4.5, max: 5, note: 'Answer delivered with sources and tool trace in the demo executions.' },
    { id: 'permission-compliance', label: 'Permission Compliance', score: 5.0, max: 5, note: 'Restricted data excluded before the task; refusal path verified for the Internal role.' },
    { id: 'latency', label: 'Latency', score: 3.9, max: 5, note: 'Demo executions ranged 0.9s–2.8s; no production benchmark.' },
    { id: 'cost', label: 'Cost', score: 4.0, max: 5, note: 'Demo cost per execution $0.004–$0.041; not a production allocation.' }
  ];

  /* Source manager: the eight fields named by requirements v2.0 for every configured source.
   * All values are synthetic demo values; no licensed feed is connected. */
  const sources = [
    {
      id: 'SRC-ICE', name: 'ICE (demo)', sourceType: 'Exchange feed', dataType: 'Futures', updateFrequency: 'Real-time (demo)',
      connectionStatus: 'Connected', validationRule: 'Price > 0, timestamp within 5 min of market time',
      usageRights: 'Internal', ingestionError: null
    },
    {
      id: 'SRC-CME', name: 'CME (demo)', sourceType: 'Exchange feed', dataType: 'Futures', updateFrequency: 'Real-time (demo)',
      connectionStatus: 'Connected', validationRule: 'Price > 0, timestamp within 5 min of market time',
      usageRights: 'Internal', ingestionError: null
    },
    {
      id: 'SRC-PLATTS', name: 'Platts (demo)', sourceType: 'Licensed assessment', dataType: 'Physical assessments', updateFrequency: 'End-of-day',
      connectionStatus: 'Connected', validationRule: 'Assessment present for every business day; no mixed price types',
      usageRights: 'Restricted', ingestionError: null
    },
    {
      id: 'SRC-SBV', name: 'SBV (demo)', sourceType: 'Central bank reference', dataType: 'FX reference rate', updateFrequency: 'Delayed (daily)',
      connectionStatus: 'Connected', validationRule: 'Rate within ±2% of the prior reference',
      usageRights: 'Internal', ingestionError: null
    },
    {
      id: 'SRC-NEWS', name: 'Reuters / Bloomberg (demo)', sourceType: 'News wire', dataType: 'News articles', updateFrequency: 'Manual / licensed integration pending',
      connectionStatus: 'Manual', validationRule: 'Headline, source and publication time required before indexing',
      usageRights: 'Internal', ingestionError: 'Last run 13 Nov 2026 · 2 items rejected: missing publication time'
    }
  ];

  window.DEMO = { meta: { asOf: '14 Nov 2026 · 09:42 ICT', freshness: 'Mixed freshness', disclaimer: 'Synthetic demo data for review. Not live BSR or licensed market data.' },
    uploadLimits: { maxBytes: 5 * 1024 * 1024, extensions: ['.csv', '.xls', '.xlsx', '.pdf', '.doc', '.docx'], label: 'CSV, XLS/XLSX, PDF, DOC/DOCX' },
    roles: {
    leadership: { label: 'Leadership', label_vi: 'Ban lãnh đạo', name: 'Lê Minh Anh', initials: 'LA', maxClassification: 'Restricted', viewRestricted: true, export: false, admin: false, department: 'Executive Office', department_vi: 'Văn phòng điều hành' },
    mi: { label: 'Market Intelligence', label_vi: 'Phân tích thị trường', name: 'Nguyễn Thu Hà', initials: 'TH', maxClassification: 'Restricted', viewRestricted: true, export: true, admin: true, department: 'Market Intelligence', department_vi: 'Phân tích thị trường' },
    internal: { label: 'Internal user', label_vi: 'Người dùng nội bộ', name: 'Trần Quốc Bảo', initials: 'QB', maxClassification: 'Internal', viewRestricted: false, export: false, admin: false, department: 'Commercial', department_vi: 'Kinh doanh' }
  }, sources, instruments, events, drivers, highlights, news, forecasts, reports, audit, aiExecutions, coverage, analysis, aiRubric };
})();
