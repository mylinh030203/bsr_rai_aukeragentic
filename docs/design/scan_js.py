"""Report the first unterminated string / bracket imbalance in a JS file.

Known-good files (data.js) are used to sanity-check the scanner itself, so a
false positive in the scanner cannot be mistaken for a file defect.
"""
import sys


def scan(path):
    s = open(path, encoding='utf-8').read()
    opens = {'(': ')', '[': ']', '{': '}'}
    stack = []
    issues = []
    i = 0
    line = 1
    while i < len(s):
        c = s[i]
        if c == '\n':
            line += 1
            i += 1
            continue
        if c in '\'"`':
            quote = c
            start_line = line
            i += 1
            closed = False
            while i < len(s):
                ch = s[i]
                if ch == '\\':
                    i += 2
                    continue
                if ch == '\n':
                    line += 1
                    if quote != '`':
                        issues.append(f'line {start_line}: unterminated {quote} string')
                        closed = True
                        break
                if ch == quote:
                    closed = True
                    i += 1
                    break
                i += 1
            if not closed:
                issues.append(f'line {start_line}: unterminated {quote} string at EOF')
            continue
        if c in opens:
            stack.append((c, line))
        elif c in ')]}':
            if not stack:
                issues.append(f'line {line}: unexpected {c}')
            else:
                o, ol = stack.pop()
                if opens[o] != c:
                    issues.append(f'line {line}: {c} closes {o} opened line {ol}')
        i += 1
    if stack:
        issues.append(f'unclosed: {stack[-5:]}')
    return issues


for path in sys.argv[1:]:
    print(path)
    found = scan(path)
    if not found:
        print('  clean')
    for x in found[:12]:
        print('  -', x)
