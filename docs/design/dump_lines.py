s = open('docs/design/prototype/assets/app.js', encoding='utf-8').read()
lines = s.split('\n')
for n in (852, 1213):
    for k in (n - 1, n, n + 1):
        print(k + 1, repr(lines[k][:200]))
    print('---')
print(len(lines))
