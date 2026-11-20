import io

p = 'docs/design/prototype/assets/styles.css'
s = io.open(p, encoding='utf-8').read()
subs = [
    ("min-width: 0; width: 100%; max-width: 100%;\n  flex-wrap: nowrap;",
     "min-width: 0; width: 100%; max-width: 100%;\n  flex-wrap: nowrap; padding-right: 8px;"),
    ("gap: 5px; padding: 5px 9px;", "gap: 5px; padding: 5px 8px;"),
    ("display: inline; margin-left: 2px; font-family: var(--mono); font-size: 8.5px;",
     "display: inline; margin-left: 2px; font-family: var(--mono); font-size: 8px;"),
    ("@media (max-width: 480px) {\n  .metric-grid { grid-template-columns: 1fr 1fr; }",
     "@media (max-width: 480px) {\n  .metric-grid { grid-template-columns: 1fr 1fr; }\n  .metric-top { align-items: flex-start; }\n  .metric-label { white-space: normal; overflow: visible; text-overflow: clip; line-height: 1.25; }"),
]
for old, new in subs:
    n = s.count(old)
    print('OK' if n == 1 else 'MISS(%d)' % n, old[:48].replace('\n', ' '))
    s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)

q = 'docs/design/_tmp_redesign/shoot.py'
t = io.open(q, encoding='utf-8').read()
old = '    pg.set_viewport_size({"width": 390, "height": 844})\n    pg.wait_for_timeout(400)'
new = '    pg.set_viewport_size({"width": 390, "height": 844})\n    pg.wait_for_timeout(400)\n    pg.evaluate("window.scrollTo(0,0)")\n    pg.wait_for_timeout(200)'
print('OK' if t.count(old) == 1 else 'MISS(%d)' % t.count(old), 'shoot.py scroll reset')
io.open(q, 'w', encoding='utf-8').write(t.replace(old, new, 1))
