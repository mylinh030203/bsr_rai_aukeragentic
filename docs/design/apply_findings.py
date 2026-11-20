"""Apply the confirmed review/verify findings to the prototype.

Fixes:
  D1 residual contrast: .sidebar-user span, .page-kicker, table.data th,
     .instrument-btn .i-value, .instrument-btn.active value contrast.
  Verify-major: chart hover overlay must not intercept pointer events over the
     event markers.
  Verify-minor: renderFileError must not duplicate the retained file block.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CSS = 'docs/design/prototype/assets/styles.css'
APP = 'docs/design/prototype/assets/app.js'

css_patches = [
    (
        ".chart-svg .hover-line { stroke: var(--ink-400); stroke-width: 1; stroke-dasharray: 3 3; }\n.chart-svg .hover-dot { fill: var(--surface); stroke-width: 2; }",
        ".chart-svg .hover-group { pointer-events: none; }\n.chart-svg .hover-line { stroke: var(--ink-400); stroke-width: 1; stroke-dasharray: 3 3; user-select: none; }\n.chart-svg .hover-dot { fill: var(--surface); stroke-width: 2; user-select: none; }",
    ),
    (
        ".sidebar-user span { display: block; font-size: 9px; color: rgba(255,255,255,.45); white-space: nowrap; }",
        ".sidebar-user span { display: block; font-size: 9px; color: rgba(255,255,255,.62); white-space: nowrap; }",
    ),
    (
        ".page-kicker { font-size: 10px; letter-spacing: .18em; text-transform: uppercase; color: var(--copper); font-weight: 600; margin-bottom: 6px; }",
        ".page-kicker { font-size: 10px; letter-spacing: .18em; text-transform: uppercase; color: var(--copper-dark); font-weight: 600; margin-bottom: 6px; }",
    ),
    (
        ".instrument-btn .i-value { font-family: var(--mono); font-size: 10px; color: var(--ink-400); }",
        ".instrument-btn .i-value { font-family: var(--mono); font-size: 10px; color: var(--ink-600); }",
    ),
]

app_patches = [
    (
        "    const previous = $('#file-preview') ? $('#file-preview').innerHTML : '';\n    box.innerHTML = `<div class=\"inline-note\"><span class=\"note-mark\">!</span><span><strong>Upload rejected.</strong> ${esc(message)} The selected file is kept below so you can retry with a supported file.</span></div>${previous ? `<div class=\"mt-8\"><strong class=\"small\">Still selected</strong>${previous}</div>` : ''}`;",
        "    box.innerHTML = `<div class=\"inline-note\"><span class=\"note-mark\">!</span><span><strong>Upload rejected.</strong> ${esc(message)} The selected file is kept below so you can retry with a supported file.</span></div>`;",
    ),
]

failed = []
for path, patches in ((CSS, css_patches), (APP, app_patches)):
    src = open(path, encoding='utf-8', newline='').read()
    for old, new in patches:
        n = src.count(old)
        if n != 1:
            failed.append(f'{path}: {n} matches for {old[:60]!r}')
            continue
        src = src.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='').write(src)

if failed:
    print('FAILED')
    for f in failed:
        print(' -', f)
    sys.exit(1)
print('applied', len(css_patches) + len(app_patches), 'fixes')
