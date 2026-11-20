import itertools

p = 'docs/design/prototype/assets/app.js'
s = open(p, encoding='utf-8').read()

opens = {'(': ')', '[': ']', '{': '}'}
stack = []
i = 0
line = 1
issues = []
while i < len(s):
    c = s[i]
    if c == '\n':
        line += 1
    elif c in "'\"`":
        quote = c
        start_line = line
        i += 1
        while i < len(s):
            ch = s[i]
            if ch == '\\':
                i += 2
                continue
            if ch == '\n':
                line += 1
                if quote != '`':
                    issues.append(f'unterminated {quote} string starting line {start_line}')
                    break
            if ch == quote:
                break
            i += 1
        # template literal ${ } nesting is balanced overall, bracket stack still sees ${ handled below
    elif c == '$' and i + 1 < len(s) and s[i + 1] == '{' and False:
        pass
    elif c in opens:
        stack.append((c, line))
    elif c in ')]}':
        if not stack:
            issues.append(f'unexpected {c} at line {line}')
        else:
            o, ol = stack.pop()
            if opens[o] != c:
                issues.append(f'mismatch {o} line {ol} closed by {c} line {line}')
    i += 1
if stack:
    issues.append(f'unclosed {stack[-3:]}')

print('issues', len(issues))
for x in issues[:10]:
    print(' -', x)
