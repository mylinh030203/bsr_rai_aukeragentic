p = 'docs/design/prototype/assets/app.js'
d = open(p, 'rb').read()
print('bytes', len(d))
print('utf8 ok', end=' ')
try:
    s = d.decode('utf-8')
    print(True, 'chars', len(s))
except UnicodeDecodeError as e:
    print(False, e)
print('surrogates', d.count(b'\xed\xa0'), d.count(b'\xed\xb0'))
print('bom', d[:3])
for i, line in enumerate(d.split(b'\n')):
    try:
        line.decode('utf-8')
    except UnicodeDecodeError as e:
        print('bad line', i + 1, e, line[:120])
