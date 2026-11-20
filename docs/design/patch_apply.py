import sys

path = sys.argv[1]
old = sys.argv[2]
new = sys.argv[3]
src = open(path, encoding='utf-8', newline='').read()
count = src.count(old)
if count != 1:
    print(f'ABORT: expected 1 occurrence, found {count}')
    sys.exit(1)
open(path, 'w', encoding='utf-8', newline='').write(src.replace(old, new, 1))
print(f'OK: replaced 1 occurrence in {path}')
