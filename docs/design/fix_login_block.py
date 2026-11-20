import sys

p = 'docs/design/prototype/assets/app.js'
s = open(p, encoding='utf-8', newline='').read()

broken_start = "    if (state.signingIn) {\n      return '' +\n      '<div class=\"login\">'"
start = s.find(broken_start)
if start == -1:
    print('ABORT: login block not found')
    sys.exit(1)
end_marker = "</div>`;\n    }\n    return `"
end = s.find(end_marker, start)
if end == -1:
    print('ABORT: login block end not found')
    sys.exit(1)
block_end = end + len(end_marker)

replacement = """    if (state.signingIn) {
      const label = esc(pendingRoleLabel());
      return `
      <div class="login">
        <section class="login-brand" aria-label="BSR Market Intelligence">
          <div class="brand-lockup"><div class="brand-mark">BSR</div><div><div class="brand-name">Market Intelligence</div><div class="brand-sub">Reasonary AI \\u00b7 Auker intelligence layer</div></div></div>
        </section>
        <section class="login-panel" aria-labelledby="signin-loading-title" aria-busy="true">
          <h2 id="signin-loading-title">Preparing your workspace\\u2026</h2>
          <p role="status">Applying the ${label} permission scope. Restricted data and actions are resolved before the workspace renders.</p>
          <ul class="signin-steps"><li class="done">Demo identity verified</li><li class="active">Loading permitted scope</li><li>Opening overview</li></ul>
          <div class="login-note">If the scope cannot be resolved, the workspace denies the route instead of showing unfiltered data.</div>
        </section>
      </div>`;
    }
    return `"""

s = s[:start] + replacement + s[block_end:]
open(p, 'w', encoding='utf-8', newline='').write(s)
print('replaced login block')
