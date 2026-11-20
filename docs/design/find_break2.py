"""Locate the first structural break in app.js.

Strategy: strip comments and string/template contents while preserving newlines
and code characters that matter for balance ((), [], {}). Template ${...}
expressions are kept as code so their brackets count. Then walk the leftover
code characters and report the first bracket mismatch with its line.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = 'docs/design/prototype/assets/app.js'
src = open(path, encoding='utf-8').read()

out = []  # list of (char, line) for code characters only
i = 0
line = 1


def emit(ch):
    out.append((ch, line))


while i < len(src):
    c = src[i]
    if c == '\n':
        line += 1
        i += 1
        continue
    if c == '/' and i + 1 < len(src) and src[i + 1] == '/':
        j = src.find('\n', i)
        i = len(src) if j == -1 else j
        continue
    if c == '/' and i + 1 < len(src) and src[i + 1] == '*':
        j = src.find('*/', i + 2)
        seg = src[i:j]
        line += seg.count('\n')
        i = len(src) if j == -1 else j + 2
        continue
    if c in '\'"':
        q = c
        i += 1
        while i < len(src):
            ch = src[i]
            if ch == '\\':
                i += 2
                continue
            if ch == '\n':
                line += 1
            if ch == q:
                i += 1
                break
            i += 1
        continue
    if c == '`':
        i += 1
        while i < len(src):
            ch = src[i]
            if ch == '\\':
                i += 2
                continue
            if ch == '\n':
                line += 1
                i += 1
                continue
            if ch == '`':
                i += 1
                break
            if ch == '$' and i + 1 < len(src) and src[i + 1] == '{':
                emit('{')
                i += 2
                depth = 1
                while i < len(src) and depth > 0:
                    ch2 = src[i]
                    if ch2 == '\\':
                        i += 2
                        continue
                    if ch2 == '\n':
                        line += 1
                        i += 1
                        continue
                    if ch2 in '\'"':
                        q2 = ch2
                        i += 1
                        while i < len(src):
                            c3 = src[i]
                            if c3 == '\\':
                                i += 2
                                continue
                            if c3 == '\n':
                                line += 1
                            if c3 == q2:
                                i += 1
                                break
                            i += 1
                        continue
                    if ch2 == '`':
                        i += 1
                        while i < len(src):
                            c4 = src[i]
                            if c4 == '\\':
                                i += 2
                                continue
                            if c4 == '\n':
                                line += 1
                            if c4 == '`':
                                i += 1
                                break
                            i += 1
                        continue
                    if ch2 == '{':
                        depth += 1
                    elif ch2 == '}':
                        depth -= 1
                    emit(ch2)
                    i += 1
                continue
            i += 1
        continue
    emit(c)
    i += 1

pairs = {'(': ')', '[': ']', '{': '}'}
stack = []
for ch, ln in out:
    if ch in pairs:
        stack.append((ch, ln))
    elif ch in ')]}':
        if not stack:
            print('first problem: unexpected', ch, 'at line', ln)
            break
        o, ol = stack.pop()
        if pairs[o] != ch:
            print(f'first problem: {ch} at line {ln} closes {o} opened at line {ol}')
            break
else:
    if stack:
        print('unclosed at EOF:', stack[-6:])
    else:
        print('all brackets balanced')
