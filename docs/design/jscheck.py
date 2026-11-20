"""Judge whether a JS string is closed, tolerating regex literals.

The scanner reports the first string that never closes because it misreads
regex character classes such as /[&<>"']/ as strings. This checker tracks an
"expect value" flag so a '/' after an operator starts a regex literal instead
of a division, and skips regex bodies (including character classes).
"""
import sys

REGEX_PREV = set('(,=:[!&|?{};+-*%<>~^')


def check(path):
    s = open(path, encoding='utf-8').read()
    i = 0
    line = 1
    stack = []
    value_expected = True
    pairs = {'(': ')', '[': ']', '{': '}'}
    while i < len(s):
        c = s[i]
        if c == '\n':
            line += 1
            i += 1
            continue
        if c in ' \t\r':
            i += 1
            continue
        if c == '/' and i + 1 < len(s) and s[i + 1] == '/':
            j = s.find('\n', i)
            i = len(s) if j == -1 else j
            continue
        if c == '/' and i + 1 < len(s) and s[i + 1] == '*':
            j = s.find('*/', i + 2)
            i = len(s) if j == -1 else j + 2
            continue
        if c == '/' and value_expected:
            i += 1
            in_class = False
            while i < len(s):
                ch = s[i]
                if ch == '\\':
                    i += 2
                    continue
                if ch == '\n':
                    return [(line, 'unterminated regex literal')]
                if ch == '[':
                    in_class = True
                elif ch == ']':
                    in_class = False
                elif ch == '/' and not in_class:
                    i += 1
                    break
                i += 1
            value_expected = False
            continue
        if c in '\'"`':
            quote = c
            start = line
            i += 1
            while i < len(s):
                ch = s[i]
                if ch == '\\':
                    i += 2
                    continue
                if ch == '\n':
                    line += 1
                    if quote != '`':
                        return [(start, f'unterminated {quote} string')]
                if ch == quote:
                    i += 1
                    break
                i += 1
            else:
                return [(start, f'unterminated {quote} string at EOF')]
            value_expected = False
            continue
        if c in pairs:
            stack.append((c, line))
            value_expected = True
            i += 1
            continue
        if c in ')]}':
            if not stack:
                return [(line, f'unexpected {c}')]
            o, ol = stack.pop()
            if pairs[o] != c:
                return [(line, f'{c} closes {o} from line {ol}')]
            value_expected = False
            i += 1
            continue
        if c in REGEX_PREV:
            value_expected = True
        elif c.isalnum() or c in '_$':
            # identifier/keyword: keep scanning, but a following '(' is a call
            value_expected = False
        i += 1
    if stack:
        return [stack[-1][1:][::-1] + ('unclosed ' + stack[-1][0],)]
    return []


for path in sys.argv[1:]:
    issues = check(path)
    print(path, '->', 'clean' if not issues else issues[:5])
