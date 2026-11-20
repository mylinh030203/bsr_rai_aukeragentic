"""Apply the remaining requirements-review fixes (idempotent anchors).

F1: market + ingestion time visible on metric cards and tape cells.
F2: the session-change figure states its base.
F3: news filters survive drawer-triggered re-renders.
Missing anchors are reported, not silently skipped.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

APP = 'docs/design/prototype/assets/app.js'
CSS = 'docs/design/prototype/assets/styles.css'

SESSION_TIP = 'title="Change against the previous session close, not against the prior stored observation"'

app = open(APP, encoding='utf-8', newline='').read()
css = open(CSS, encoding='utf-8', newline='').read()

app_patches = [
    (
        """      <div class="metric-spark">${sparkline(i.spark, color)}</div>
      <div class="metric-meta">""",
        """      <div class="metric-spark">${sparkline(i.spark, color)}</div>
      <div class="metric-time"><span>Mkt <strong>${esc(i.marketTime)}</strong></span><span>Ingested ${esc(i.ingestionTime)}</span></div>
      <div class="metric-meta">""",
    ),
    (
        """<span class="muted">session change</span>""",
        """<span class="muted" """ + SESSION_TIP + """>session change</span>""",
    ),
    (
        """<button class="tape-item" data-action="open-metric" data-instrument="${id}">""",
        """<button class="tape-item" data-action="open-metric" data-instrument="${id}" title="${esc(i.short)} · market ${esc(i.marketTime)} · ingested ${esc(i.ingestionTime)} · ${esc(i.dataStatus)}">""",
    ),
    (
        """<span class="t-value">${fmtNum(i.value, i.decimals)} <span class="muted" style="font-size:9px;font-weight:400">${esc(i.unit)}</span></span>""",
        """<span class="t-value">${fmtNum(i.value, i.decimals)} <span class="muted" style="font-size:9px;font-weight:400">${esc(i.unit)}</span></span><span class="t-time">${esc(i.marketTime.replace('14 Nov 2026 · ', ''))}</span>""",
    ),
    (
        """  function closeDrawer() {
    $('#drawer').classList.remove('open');""",
        """  function closeDrawer() {
    if (state.route === 'news') syncNewsFilter();
    $('#drawer').classList.remove('open');""",
    ),
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
    (
        """  function doFeedback(id, kind) {
    state.feedback[id] = state.feedback[id] || {};""",
        """  function doFeedback(id, kind) {
    syncNewsFilter();
    state.feedback[id] = state.feedback[id] || {};""",
    ),
]

css_patches = [
    (
        ".metric-meta { display: flex;",
        ".metric-time { display: flex; flex-wrap: wrap; gap: 2px 10px; font-family: var(--mono); font-size: 9px; color: var(--ink-600); margin: 2px 0 6px; }\n.metric-time strong { font-weight: 600; color: var(--ink-700); }\n.metric-meta { display: flex;",
    ),
    (
        ".tape-item .t-value {",
        ".tape-item .t-time { display: block; font-family: var(--sans); font-size: 8px; font-weight: 400; color: var(--ink-600); }\n.tape-item .t-value {",
    ),
]

problems = []
for path, src, patches, label in (
    (APP, app, app_patches, 'app.js'),
    (CSS, css, css_patches, 'styles.css'),
):
    for old, new in patches:
        n = src.count(old)
        if n != 1:
            problems.append(f'{label}: {n} matches for {old[:70]!r}')
            continue
        src = src.replace(old, new, 1)
    if label == 'app.js':
        app = src
    else:
        css = src

if problems:
    print('NOT APPLIED (nothing written)')
    for p in problems:
        print(' -', p)
    sys.exit(1)

open(APP, 'w', encoding='utf-8', newline='').write(app)
open(CSS, 'w', encoding='utf-8', newline='').write(css)
print('applied', len(app_patches), 'JS and', len(css_patches), 'CSS fixes')
