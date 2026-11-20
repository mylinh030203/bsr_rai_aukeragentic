"""Per-line delimiter census for app.js.

Prints lines where a quote character appears an odd number of times, which is
the classic signature of a truncated or duplicated patch on a long template
line. Escaped quotes are counted, so lines are reported as suspects only.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = 'docs/design/prototype/assets/app.js'
lines = open(path, encoding='utf-8').read().split('\n')

count = 0
for idx, text in enumerate(lines, start=1):
    for q in ('"', "'"):
        n = text.count(q)
        if n % 2 == 1:
            print(f'line {idx}: odd {q} count {n} :: {text.strip()[:150]}')
            count += 1
            break
print('suspect lines:', count)
