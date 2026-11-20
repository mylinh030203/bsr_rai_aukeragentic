"""Repair literal backslash-n sequences inside data.js (outside string literals).

A patch inserted the two characters \ and n where a real newline belongs. This
script finds every such sequence that is NOT within a quoted string and turns it
into a newline, then reports the remaining count.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = 'docs/design/prototype/assets/data.js'
src = open(p, encoding='utf-8', newline='').read()

out = []
i = 0
n = len(src)
state = 'code'
fixed = 0
while i < n:
    c = src[i]
    if state == 'code':
        if c in '"\'':
            state = c
            out.append(c)
            i += 1
            continue
        if c == '\\' and i + 1 < n and src[i + 1] == 'n':
            out.append('\n')
            fixed += 1
            i += 2
            continue
        out.append(c)
        i += 1
        continue
    # inside a string
    if c == '\\':
        out.append(src[i:i + 2])
        i += 2
        continue
    if c == state or c == '\n':
        state = 'code'
    out.append(c)
    i += 1

result = ''.join(out)
print('literal escapes replaced:', fixed)
if fixed:
    open(p, 'w', encoding='utf-8', newline='').write(result)
    print('written')
else:
    print('nothing to change')
