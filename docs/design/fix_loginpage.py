import sys

p = 'docs/design/prototype/assets/app.js'
lines = open(p, encoding='utf-8').read().split('\n')

# loginPage: drop the stray loading template (lines 166-178, 1-based) that was
# left inside the function after the loading UI moved into signingInPage().
head = lines[:165]           # through line 165 ('    }')
tail = lines[178:]           # from line 179 ('    return `')

out = head + tail
joined = '\n'.join(out)
open(p, 'w', encoding='utf-8', newline='').write(joined)
print('loginPage stray block removed; lines now', len(out))
