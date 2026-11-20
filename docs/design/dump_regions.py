import sys

p = 'docs/design/prototype/assets/app.js'
s = open(p, encoding='utf-8', newline='').read()
lines = s.split('\n')
for idx, line in enumerate(lines, start=1):
    if 215 <= idx <= 225 or 1640 <= idx <= 1646:
        print(idx, repr(line[:180]))
print('total lines', len(lines))
print('signingIn refs', s.count('signingInPage'))
