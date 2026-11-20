import sys

p = 'docs/design/prototype/assets/app.js'
s = open(p, encoding='utf-8', newline='').read()

start_marker = "    if (state.signingIn) {\n"
start = s.find(start_marker)
if start == -1:
    print('ABORT: marker not found')
    sys.exit(1)
rest = s.find("    return `", start)
if rest == -1:
    print('ABORT: fallthrough return not found')
    sys.exit(1)

replacement = """    if (state.signingIn) {
      return signingInPage();
    }
"""
s = s[:start] + replacement + s[rest:]

helper = """
  function signingInPage() {
    const label = esc(pendingRoleLabel());
    const steps = ['Demo identity verified', 'Loading permitted scope', 'Opening overview']
      .map((text, idx) => '<li class="' + (idx === 0 ? 'done' : idx === 1 ? 'active' : '') + '">' + text + '</li>')
      .join('');
    const head = '<section class="login-brand" aria-label="BSR Market Intelligence"><div class="brand-lockup"><div class="brand-mark">BSR</div>'
      + '<div><div class="brand-name">Market Intelligence</div><div class="brand-sub">Reasonary AI \\u00b7 Auker intelligence layer</div></div></div></section>';
    const panel = '<section class="login-panel" aria-labelledby="signin-loading-title" aria-busy="true">'
      + '<h2 id="signin-loading-title">Preparing your workspace\\u2026</h2>'
      + '<p role="status">Applying the ' + label + ' permission scope. Restricted data and actions are resolved before the workspace renders.</p>'
      + '<ul class="signin-steps">' + steps + '</ul>'
      + '<div class="login-note">If the scope cannot be resolved, the workspace denies the route instead of showing unfiltered data.</div>'
      + '</section>';
    return '<div class="login">' + head + panel + '</div>';
  }

  function loginPage() {"""

s = s.replace('\n  function loginPage() {', helper, 1)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('rewritten')
