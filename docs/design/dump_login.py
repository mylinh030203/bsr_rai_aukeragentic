import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

s = open('docs/design/prototype/assets/app.js', encoding='utf-8').read()
lines = s.split('\n')
for n in range(196, 224):
    print(n + 1, repr(lines[n][:220]))
