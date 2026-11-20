"""Syntactic balance checker with template-expression recursion.

This is a linear scanner: template literals push an expression context for
${ ... }, and inside that context strings/templates are scanned the same way.
It reports the first construct that fails to close.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class Scanner:
    def __init__(self, s):
        self.s = s
        self.i = 0
        self.line = 1
        self.issues = []

    def peek(self, k=0):
        j = self.i + k
        return self.s[j] if j < len(self.s) else ''

    def adv(self):
        if self.s[self.i] == '\n':
            self.line += 1
        self.i += 1

    def skip_ws_and_comments(self):
        while self.i < len(self.s):
            c = self.s[self.i]
            if c in ' \t\r\n':
                self.adv()
            elif c == '/' and self.peek(1) == '/':
                while self.i < len(self.s) and self.s[self.i] != '\n':
                    self.adv()
            elif c == '/' and self.peek(1) == '*':
                start = self.line
                self.adv(); self.adv()
                while self.i < len(self.s) and not (self.s[self.i] == '*' and self.peek(1) == '/'):
                    self.adv()
                if self.i >= len(self.s):
                    self.issues.append((start, 'unterminated block comment'))
                    return
                self.adv(); self.adv()
            else:
                return

    def string(self):
        quote = self.s[self.i]
        start = self.line
        self.adv()
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == '\\':
                self.adv(); self.adv()
                continue
            if c == '\n':
                self.issues.append((start, f'unterminated {quote} string'))
                return
            if c == quote:
                self.adv()
                return
            self.adv()
        self.issues.append((start, f'unterminated {quote} string at EOF'))

    def template(self):
        start = self.line
        self.adv()  # opening backtick
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == '\\':
                self.adv(); self.adv(); continue
            if c == '`':
                self.adv(); return
            if c == '$' and self.peek(1) == '{':
                self.adv(); self.adv()
                if not self.expr(closing='}'):
                    self.issues.append((start, 'template expression never closed'))
                    return
                continue
            self.adv()
        self.issues.append((start, 'unterminated template literal at EOF'))

    def expr(self, closing):
        """Scan an expression until an unmatched `closing` bracket is consumed."""
        pairs = {'(': ')', '[': ']', '{': '}'}
        open_stack = []
        while self.i < len(self.s):
            self.skip_ws_and_comments()
            if self.i >= len(self.s):
                break
            c = self.s[self.i]
            if c in '\'"':
                self.string(); continue
            if c == '`':
                self.template(); continue
            if c == '/':
                # regex or divide: only treat as regex after an operator
                self.adv(); continue
            if c in pairs:
                open_stack.append(c)
                self.adv(); continue
            if c in ')]}':
                if open_stack:
                    o = open_stack.pop()
                    if pairs[o] != c:
                        self.issues.append((self.line, f'{c} closes {o}'))
                        return False
                elif closing and c == closing:
                    self.adv(); return True
                else:
                    self.issues.append((self.line, f'unexpected {c}'))
                    return False
                self.adv(); continue
            self.adv()
        self.issues.append((self.line, 'EOF inside expression'))
        return False


src = open('docs/design/prototype/assets/app.js', encoding='utf-8').read()
sc = Scanner(src)
ok = sc.expr(closing=None)
print('finished clean' if ok and not sc.issues else 'issues:')
for line, msg in sc.issues[:8]:
    print(' - line', line, msg)
print('last position line', sc.line)
