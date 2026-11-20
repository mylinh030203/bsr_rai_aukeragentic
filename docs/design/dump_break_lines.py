import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = 'docs/design/prototype/assets/app.js'
lines = open(path, encoding='utf-8').read().split('\n')

for target in (40, 866, 1226, 1623):
    print('==== line', target - 1, '(0-based', target - 1, ') and neighbours')
    for k in range(max(0, target - 3), min(len(lines), target + 1)):
        print(k + 1, repr(lines[k][:300]))
    print()
