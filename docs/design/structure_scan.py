"""Per-function delimiter deltas using brace-aware splitting.

The previous census split on `function name(` regardless of whether the
occurrence sat inside a template literal, which produced false positives. This
version strips string/template bodies (keeping only code characters plus a
placeholder) and then splits on real top-level function declarations.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = 'docs/design/prototype/assets/app.js'
src = open(path, encoding='utf-8').read()

code = []          # code characters only, line-preserving
line_map = []      # code index -> source line
i = 0
line = 1
n = len(src)
while i < n:
    c = src[i]
    if c == '\n':
        line += 1
        code.append('\n')
        line_map.append(line - 1)
        i += 1
        continue
    if c == '/' and i + 1 < n and src[i + 1] == '/':
        j = src.find('\n', i)
        i = n if j == -1 else j
        continue
    if c == '/' and i + 1 < n and src[i + 1] == '*':
        j = src.find('*/', i + 2)
        if j == -1:
            break
        line += src.count('\n', i, j)
        i = j + 2
        continue
    if c in '"\'':
        q = c
        start_line = line
        i += 1
        while i < n:
            ch = src[i]
            if ch == '\\':
                i += 2
                continue
            if ch == '\n':
                print(f'!! unterminated {q} string starting line {start_line}')
                break
            if ch == q:
                i += 1
                break
            i += 1
        code.append('S')
        line_map.append(start_line)
        continue
    if c == '`':
        start_line = line
        i += 1
        while i < n:
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
            if ch == '$' and i + 1 < n and src[i + 1] == '{':
                i += 2
                depth = 1
                while i < n and depth > 0:
                    ch2 = src[i]
                    if ch2 == '\\':
                        i += 2
                        continue
                    if ch2 == '\n':
                        line += 1
                        code.append('\n')
                        line_map.append(line)
                        i += 1
                        continue
                    if ch2 == '{':
                        depth += 1
                    elif ch2 == '}':
                        depth -= 1
                        if depth == 0:
                            i += 1
                            break
                        code.append('}')
                        line_map.append(line)
                        i += 1
                        continue
                    if ch2 == '(':
                        code.append('(')
                    elif ch2 == ')':
                        code.append(')')
                    elif ch2 == '[':
                        code.append('[')
                    elif ch2 == ']':
                        code.append(']')
                    elif ch2 == '{':
                        code.append('{')
                    line_map.append(line)
                    i += 1
                if depth != 0:
                    print(f'!! template expression never closed, started line {start_line}')
                continue
            i += 1
        code.append('T')
        line_map.append(start_line)
        continue
    code.append(c)
    line_map.append(line)
    i += 1

text = ''.join(code)
print('code stream length', len(text))

# walk to find top-level `function name(` occurrences (brace depth 0 at `function`)
depth = 0
starts = []
idx = 0
L = len(text)
while idx < L:
    ch = text[idx]
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth < 0:
            print('!! negative brace depth at source line', line_map[idx])
            depth = 0
    if depth == 0 and text.startswith('function ', idx):
        # capture name
        j = idx + 9
        k = j
        while k < L and (text[k].isalnum() or text[k] in '_$'):
            k += 1
        starts.append((idx, text[j:k], line_map[idx]))
    idx += 1

starts.append((L, 'EOF', line_map[-1]))
print('top-level functions found', len(starts) - 1)
prev_depth_ok = None
for s in range(len(starts) - 1):
    a, name, ln = starts[s]
    b = starts[s + 1][0]
    body = text[a:b]
    d = body.count('{') - body.count('}')
    p = body.count('(') - body.count(')')
    br = body.count('[') - body.count(']')
    if d or p or br:
        print(f'DELTA line {ln:5} {name:24} braces={d:+d} parens={p:+d} brackets={br:+d}')
print('total depth at EOF', depth)
