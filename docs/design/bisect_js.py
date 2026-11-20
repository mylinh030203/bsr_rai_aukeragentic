"""Bisect app.js: report which top-level functions contain an unbalanced
template/string/bracket region, so the broken patch site can be isolated
without guessing.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = 'docs/design/prototype/assets/app.js'
src = open(path, encoding='utf-8').read()


def balance(text, base_line=1):
    i = 0
    line = base_line
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}
    while i < len(text):
        c = text[i]
        if c == '\n':
            line += 1
            i += 1
            continue
        if c == '/' and i + 1 < len(text) and text[i + 1] == '/':
            j = text.find('\n', i)
            i = len(text) if j == -1 else j
            continue
        if c == '/' and i + 1 < len(text) and text[i + 1] == '*':
            j = text.find('*/', i + 2)
            i = len(text) if j == -1 else j + 2
            continue
        if c in '\'"`':
            q = c
            start = line
            i += 1
            closed = False
            while i < len(text):
                ch = text[i]
                if ch == '\\':
                    i += 2
                    continue
                if ch == '\n':
                    line += 1
                    if q != '`':
                        return (f'unterminated {q} string', start, len(stack))
                if ch == q:
                    i += 1
                    closed = True
                    break
                i += 1
            if not closed:
                return (f'unterminated {q} at EOF', start, len(stack))
            continue
        if c in pairs:
            stack.append((c, line))
        elif c in ')]}':
            if not stack:
                return (f'unexpected {c}', line, 0)
            o, ol = stack.pop()
            if pairs[o] != c:
                return (f'{c} closes {o} from line {ol}', line, len(stack))
        i += 1
    if stack:
        return (f'unclosed {stack[-1]}', stack[-1][1], len(stack))
    return None


# Split on function declarations to localize the fault
import re
starts = [m.start() for m in re.finditer(r'\n  function ', src)]
starts.append(len(src))
prev_bad = None
for k in range(len(starts) - 1):
    chunk = src[starts[k]:starts[k + 1]]
    name = chunk.split('(')[0].strip()
    base_line = src[:starts[k]].count('\n') + 1
    issue = balance(chunk, base_line)
    if issue:
        print(f'BROKEN {name} (line {base_line}): {issue}')
