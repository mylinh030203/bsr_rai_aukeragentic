"""Add live validation to the quick-input modal (F5 wiring).

The manual tab currently only validates when Preview is pressed. This patch
wires input listeners so the preview/error updates as the user types, and keeps
the existing button-based path working.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = 'docs/design/prototype/assets/app.js'
src = open(p, encoding='utf-8', newline='').read()

old = "    if (e.target.id === 'quick-query-input') { /* transient */ }"
new = ("    if (e.target.id === 'quick-query-input') { /* transient */ }\n"
       "    if (['input-value', 'input-source', 'input-instrument', 'input-quality'].includes(e.target.id)) previewInput();")
print('anchor count', src.count(old))
if src.count(old) != 1:
    sys.exit(1)

src = src.replace(old, new, 1)
open(p, 'w', encoding='utf-8', newline='').write(src)
print('patched onInput live validation')
