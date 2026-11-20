"""Mobile layout fix: at <=1024px the instrument rail becomes a horizontal
scroller, which clipped group labels at 390px. Restore a vertical column for
the data layout while keeping the generic rail behaviour elsewhere.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = 'docs/design/prototype/assets/styles.css'
css = open(p, encoding='utf-8', newline='').read()

old = "  .admin-grid { grid-template-columns: 1fr; }\n  .login { grid-template-columns: 1fr; }"
new = ("  .admin-grid { grid-template-columns: 1fr; }\n"
       "  .data-layout .instrument-rail { flex-direction: column; overflow-x: visible; }\n"
       "  .data-layout .instrument-group { min-width: 0; }\n"
       "  .login { grid-template-columns: 1fr; }")

print('occurrences:', css.count(old))
if css.count(old) != 1:
    sys.exit(1)
open(p, 'w', encoding='utf-8', newline='').write(css.replace(old, new, 1))
print('patched')
