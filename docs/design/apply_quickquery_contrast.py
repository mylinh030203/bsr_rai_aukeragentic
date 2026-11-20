"""Final contrast polish flagged by the delta review (R1).

`.quick-query .card-sub` renders at 4.44:1 on the petrol card; lift the alpha so
the 11 px helper text clears AA.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = 'docs/design/prototype/assets/styles.css'
css = open(p, encoding='utf-8', newline='').read()

old = ".quick-query .card-sub { color: rgba(255,255,255,.45); }"
new = ".quick-query .card-sub { color: rgba(255,255,255,.52); }"

print('occurrences:', css.count(old))
if css.count(old) != 1:
    sys.exit(1)
open(p, 'w', encoding='utf-8', newline='').write(css.replace(old, new, 1))
print('applied quick-query contrast lift')
