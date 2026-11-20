"""Contrast fix for table headers on the recessed surface.

--ink-400 (#5c6f74) on --surface-2 (#ede9df) measures 4.35:1; table headers use
that combination, so switch them to --ink-600 which clears AA.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = 'docs/design/prototype/assets/styles.css'
css = open(p, encoding='utf-8', newline='').read()

old = "  color: var(--ink-400); font-weight: 600; padding: 9px 12px; background: var(--surface-2);"
new = "  color: var(--ink-600); font-weight: 600; padding: 9px 12px; background: var(--surface-2);"

print('occurrences:', css.count(old))
if css.count(old) != 1:
    sys.exit(1)
open(p, 'w', encoding='utf-8', newline='').write(css.replace(old, new, 1))
print('applied table header contrast fix')
