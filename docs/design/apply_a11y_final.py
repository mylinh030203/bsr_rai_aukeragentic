"""Close the remaining axe items on the prototype.

1. `.market-tape` is a div with `aria-label` but no role (axe
   `aria-prohibited-attr`). Give it `role="group"` so the label is permitted.
2. `.note-mark` uses `--copper` on `--surface-2` (3.87:1); switch it to
   `--copper-dark`, which clears 4.5:1 at the same weight.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

APP = 'docs/design/prototype/assets/app.js'
CSS = 'docs/design/prototype/assets/styles.css'

app = open(APP, encoding='utf-8', newline='').read()
old_html = '<div class="market-tape" aria-label="Market tape">'
new_html = '<div class="market-tape" role="group" aria-label="Market tape">'
print('tape occurrences:', app.count(old_html))

css = open(CSS, encoding='utf-8', newline='').read()
old_css = '.inline-note .note-mark { color: var(--copper); font-weight: 700; }'
new_css = '.inline-note .note-mark { color: var(--copper-dark); font-weight: 700; }'
print('note-mark occurrences:', css.count(old_css))

if app.count(old_html) != 1 or css.count(old_css) != 1:
    sys.exit(1)

open(APP, 'w', encoding='utf-8', newline='').write(app.replace(old_html, new_html, 1))
open(CSS, 'w', encoding='utf-8', newline='').write(css.replace(old_css, new_css, 1))
print('applied')
