p = 'app.js'
src = open(p, encoding='utf-8', newline='').read()
old = "$$('.event-marker', svg)"
new = "$$('.event-marker-group', svg)"
n = src.count(old)
print('count', n, 'before_new', src.count(new))
if n == 1 and src.count(new) == 0:
    out = src.replace(old, new, 1)
    open(p, 'w', encoding='utf-8', newline='').write(out)
    print('written')
else:
    print('skipped')
