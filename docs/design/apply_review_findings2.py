"""Fix the requirements-review findings on the prototype.

F1 (rank 3): every displayed market value must expose market and ingestion time.
            Add a compact provenance line to metric cards, a compact time label
            to tape cells and a real tooltip on both.
F2 (rank 3): the "session change" figure must state its base so it reconciles
            with the observation table's prior-observation delta.
F3 (rank 2): acting on a news item must not reset the topic/source filter.
F4 (rank 1): the collapsed rail must not render a lone separator.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

APP = 'docs/design/prototype/assets/app.js'
CSS = 'docs/design/prototype/assets/styles.css'

app = open(APP, encoding='utf-8', newline='').read()
css = open(CSS, encoding='utf-8', newline='').read()

session_title = 'title="Change against the previous session close, not against the prior stored observation"'

app_patches = [
    # F1a: metric card provenance line
    (
        """      <div class="metric-spark">${sparkline(i.spark, color)}</div>
      <div class="metric-meta"><span class="source">${esc(i.source)}</span>""",
        """      <div class="metric-spark">${sparkline(i.spark, color)}</div>
      <div class="metric-time"><span>Mkt <strong>${esc(i.marketTime)}</strong></span><span>In ${esc(i.ingestionTime)}</span></div>
      <div class="metric-meta"><span class="source">${esc(i.source)}</span>""",
    ),
    # F2a: card change label states its base
    (
        """<span class="${directionClass(i.pct)}">${fmtPct(i.pct)}</span><span class="muted">session change</span></div>""",
        """<span class="${directionClass(i.pct)}">${fmtPct(i.pct)}</span><span class="muted" """ + session_title + """>session change</span></div>""",
    ),
    # F1b: tape cell tooltip carries both timestamps and status
    (
        """              <button class="tape-item" data-action="open-metric" data-instrument="${id}">""",
        """              <button class="tape-item" data-action="open-metric" data-instrument="${id}" title="${esc(i.short)} · market ${esc(i.marketTime)} · ingested ${esc(i.ingestionTime)} · ${esc(i.dataStatus)}">""",
    ),
    # F1c: tape shows a compact market-time marker (not tooltip-only)
    (
        """                <span class="t-value">${fmtNum(i.value, i.decimals)} <span class="muted" style="font-size:9px;font-weight:400">${esc(i.unit)}</span></span>""",
        """                <span class="t-value">${fmtNum(i.value, i.decimals)} <span class="muted" style="font-size:9px;font-weight:400">${esc(i.unit)}</span><span class="t-time">${esc(i.marketTime.replace('14 Nov 2026 \\u00b7 ', ''))}</span></span>""",
    ),
    # F2b: market-data header change states its base (data header only)
    (
        """<div class="data-price small ${directionClass(selected.change)}" style="margin-top:2px">${fmtSigned(selected.change, selected.decimals)} \\u00b7 ${fmtPct(selected.pct)} <span class="muted">over session change</span></div>""",
        """<div class="data-price small ${directionClass(selected.change)}" style="margin-top:2px">${fmtSigned(selected.change, selected.decimals)} \\u00b7 ${fmtPct(selected.pct)} <span class="muted" """ + session_title + """>over session change</span></div>""",
    ),
    # F3a: keep the news filter after drawer actions
    (
        """  function closeDrawer() {
    $('#drawer').classList.remove('open');""",
        """  function closeDrawer() {
    if (state.route === 'news') syncNewsFilter();
    $('#drawer').classList.remove('open');""",
    ),
    # F3b: helper that reads the live filter controls back into state
    (
        """  function filterNews() {""",
        """  function syncNewsFilter() {
    const topic = $('#news-topic');
    const source = $('#news-source');
    const search = $('#news-search');
    if (topic) state.newsTopic = topic.value;
    if (source) state.newsSource = source.value;
    if (search) state.newsQuery = search.value;
  }

  function filterNews() {""",
    ),
    # F3c: feedback re-renders the page, so capture the filter first
    (
        """  function doFeedback(id, kind) {
    state.feedback[id] = state.feedback[id] || {};""",
        """  function doFeedback(id, kind) {
    syncNewsFilter();
    state.feedback[id] = state.feedback[id] || {};""",
    ),
]

failed = []
for old, new in app_patches:
    n = app.count(old)
    if n != 1:
        failed.append(f'app.js: {n} matches for {old[:70]!r}')
        continue
    app = app.replace(old, new, 1)

css_patches = [
    # F1 styles for the added provenance line and the tape time label
    (
        ".metric-meta { display: flex;",
        ".metric-time { display: flex; flex-wrap: wrap; gap: 2px 10px; font-family: var(--mono); font-size: 9px; color: var(--ink-600); margin: 2px 0 6px; }\n.metric-time strong { font-weight: 600; color: var(--ink-700); }\n.metric-meta { display: flex;",
    ),
    (
        ".tape-item .t-value {",
        ".tape-item .t-time { display: block; font-family: var(--sans); font-size: 8px; font-weight: 400; color: var(--ink-600); letter-spacing: 0; }\n.tape-item .t-value {",
    ),
    # F4: hide the collapsed-rail separator in both collapse paths
    (
        '.sidebar.collapsed .nav-label::after { content: "\\u00b7"; font-size: 12px; }',
        ".sidebar.collapsed .nav-label::after { content: none; }",
    ),
    (
        '  .sidebar .nav-label::after { content: "\\u00b7"; font-size: 12px; }',
        "  .sidebar .nav-label::after { content: none; }",
    ),
]
for old, new in css_patches:
    n = css.count(old)
    if n != 1:
        failed.append(f'styles.css: {n} matches for {old[:70]!r}')
        continue
    css = css.replace(old, new, 1)

if failed:
    print('FAILED')
    for f in failed:
        print(' -', f)
    sys.exit(1)

open(APP, 'w', encoding='utf-8', newline='').write(app)
open(CSS, 'w', encoding='utf-8', newline='').write(css)
print('applied', len(app_patches), 'JS and', len(css_patches), 'CSS fixes')
