import sys

path = sys.argv[1]
old = sys.argv[2]
new = sys.argv[3]
src = open(path, encoding='utf-8', newline='').read()
count = src.count(old)
print(f'match_count={count} old_len={len(old)} new_len={len(new)}')
if count != 1:
    print('ABORT')
    sys.exit(1)
open(path, 'w', encoding='utf-8', newline='').write(src.replace(old, new, 1))
print('OK')
