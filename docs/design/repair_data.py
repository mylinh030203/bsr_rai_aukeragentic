"""Repair the literal two-character sequence backslash-n that a patch inserted
into data.js, and report any other literal escapes outside strings.
"""
p = 'docs/design/prototype/assets/data.js'
src = open(p, encoding='utf-8', newline='').read()

old = "licensed market data.' },\\n    uploadLimits"
new = "licensed market data.' },\n    uploadLimits"
print('occurrences:', src.count(old))
if src.count(old) == 1:
    open(p, 'w', encoding='utf-8', newline='').write(src.replace(old, new, 1))
    print('repaired')
else:
    print('left untouched')
