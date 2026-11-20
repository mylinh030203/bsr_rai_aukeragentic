import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

data = open('docs/design/prototype/assets/app.js', 'rb').read()
tail = data[data.find(b'function signingInPage') - 400:]
print('tail region bytes:', len(tail))
print(tail.decode('utf-8', 'replace'))
