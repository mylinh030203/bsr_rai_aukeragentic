"""Find the first line where a template literal / string never closes.

Each line is classified independently (JS statements are line-scoped for our
purposes): for every line we count whether it opens an unterminated template
or string. Multiline template literals are the norm in this file, so the
tracker follows backticks explicitly and flags mismatches.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = 'docs/design/prototype/assets/app.js'
s = open(path, encoding='utf-8').read()

i = 0
line = 1
state = None  # None | 'template' | 'expr'
depth = 0
report = []


def scan_until(i, line, quote, terminator_check):
    return i


# Simpler approach: use a proper tokenizer limited to strings/templates.
i = 0
line = 1
mode = 'code'
quote = None
stack = []
while i < len(s):
    c = s[i]
    if mode == 'code':
        if c == '\n':
            line += 1
            i += 1
            continue
        if c == '/' and i + 1 < len(s) and s[i + 1] == '/':
            j = s.find('\n', i)
            i = len(s) if j == -1 else j
            continue
        if c == '/' and i + 1 < len(s) and s[i + 1] == '*':
            j = s.find('*/', i + 2)
            line += s.count('\n', i, j)
            i = len(s) if j == -1 else j + 2
            continue
        if c in '\'"':
            mode = 'string'
            quote = c
            start = line
            i += 1
            continue
        if c == '`':
            mode = 'template'
            start = line
            i += 1
            continue
        if c in '([{':
            stack.append((c, line))
        elif c in ')]}':
            if stack:
                stack.pop()
        i += 1
        continue
    if mode == 'string':
        if c == '\\':
            i += 2
            continue
        if c == '\n':
            report.append(f'line {start}: string {quote} not closed before newline')
            mode = 'code'
            line += 1
            i += 1
            continue
        if c == quote:
            mode = 'code'
        i += 1
        continue
    if mode == 'template':
        if c == '\\':
            i += 2
            continue
        if c == '\n':
            line += 1
            i += 1
            continue
        if c == '`':
            mode = 'code'
            i += 1
            continue
        if c == '$' and i + 1 < len(s) and s[i + 1] == '{':
            # parse embedded expression until matching }
            j = i + 2
            d = 1
            inner_line = line
            while j < len(s) and d > 0:
                ch = s[j]
                if ch == '\n':
                    line += 1
                elif ch == '{':
                    d += 1
                elif ch == '}':
                    d -= 1
                elif ch in '\'"':
                    q = ch
                    j += 1
                    while j < len(s) and s[j] != q:
                        if s[j] == '\\':
                            j += 1
                        if s[j] == '\n':
                            report.append(f'line {line}: inner string unclosed')
                        j += 1
                    j += 1
                    continue
                j += 1
            if d != 0:
                report.append(f'line {inner_line}: template expression never closed')
                break
            i = j + 1
            continue
        i += 1
        continue

if mode != 'code':
    report.append(f'EOF reached in mode={mode} started line {start}')

print('bracket stack depth', len(stack))
print('reports:', len(report))
for r in report[:20]:
    print(' -', r)
