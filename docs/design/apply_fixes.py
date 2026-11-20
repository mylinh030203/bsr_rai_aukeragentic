import sys

ROOT = 'docs/design/prototype/assets/'
APP = ROOT + 'app.js'
CSS = ROOT + 'styles.css'

patches = [
    # F5a: file input wiring - validation on change, retained preview on error
    (
        APP,
        "        <div class=\"field\"><label for=\"input-file-name\">Data file</label><input id=\"input-file-name\" type=\"file\" accept=\".csv,.xlsx,.pdf,.doc,.docx\"></div>\n        <div class=\"inline-note mt-12\"><span class=\"note-mark\">i</span><span>Supported demo formats: CSV, XLSX, PDF, DOC/DOCX. The upload is validated, stored, classified and queued for extraction. It is not applied directly to market observations until reviewed.</span></div>",
        "        <div class=\"field\"><label for=\"input-file-name\">Data file</label><input id=\"input-file-name\" type=\"file\" accept=\"${D.uploadLimits.extensions.join(',')}\" aria-describedby=\"input-file-note input-file-error\"></div>\n        <div class=\"inline-note mt-12\" id=\"input-file-note\"><span class=\"note-mark\">i</span><span>Supported demo formats: ${esc(D.uploadLimits.label)}, up to ${Math.round(D.uploadLimits.maxBytes / (1024 * 1024))} MB. The upload is validated, stored, classified and queued for extraction. It is not applied directly to market observations until reviewed.</span></div>\n        <div id=\"input-file-error\" class=\"mt-12\" role=\"alert\"></div>",
    ),
    # F5b: validation helper before confirmFileInput
    (
        APP,
        "  function confirmFileInput() {\n    const file = $('#input-file-name') && $('#input-file-name').files && $('#input-file-name').files[0];\n    if (!file) { showToast('Choose a file before confirming. Nothing was uploaded.'); return; }",
        "  function validateUpload(file) {\n    if (!file) return 'Choose a file before confirming. Nothing was uploaded.';\n    const ext = (file.name.match(/\\.[^.]+$/) || [''])[0].toLowerCase();\n    if (!D.uploadLimits.extensions.includes(ext)) return `Unsupported format (${ext || 'no extension'}). Allowed: ${D.uploadLimits.label}. Nothing was stored.`;\n    if (file.size > D.uploadLimits.maxBytes) return `File is ${(file.size / (1024 * 1024)).toFixed(1)} MB, above the ${Math.round(D.uploadLimits.maxBytes / (1024 * 1024))} MB limit. Nothing was stored.`;\n    return null;\n  }\n\n  function renderFileError(message) {\n    const box = $('#input-file-error');\n    if (!box) return;\n    if (!message) { box.innerHTML = ''; return; }\n    const previous = $('#file-preview') ? $('#file-preview').innerHTML : '';\n    box.innerHTML = `<div class=\"inline-note\"><span class=\"note-mark\">!</span><span><strong>Upload rejected.</strong> ${esc(message)} The selected file is kept below so you can retry with a supported file.</span></div>${previous ? `<div class=\"mt-8\"><strong class=\"small\">Still selected</strong>${previous}</div>` : ''}`;\n  }\n\n  function confirmFileInput() {\n    const file = $('#input-file-name') && $('#input-file-name').files && $('#input-file-name').files[0];\n    const problem = validateUpload(file);\n    if (problem) { renderFileError(problem); showToast('Upload rejected. ' + problem); return; }\n    renderFileError('');",
    ),
    # F5c: change handler sets error or clears it
    (
        APP,
        "    if (e.target.id === 'input-file-name') { const f = e.target.files && e.target.files[0]; const box = $('#file-preview'); if (f && box) box.innerHTML = `<div class=\"formula-box\"><div class=\"formula-id\">Selected file</div><p>${esc(f.name)} · ${Math.ceil(f.size / 1024)} KB · queued for validation and extraction on confirm.</p></div>`; }",
        "    if (e.target.id === 'input-file-name') {\n      const f = e.target.files && e.target.files[0];\n      const box = $('#file-preview');\n      if (!f) return;\n      const problem = validateUpload(f);\n      if (box) box.innerHTML = `<div class=\"formula-box\"><div class=\"formula-id\">Selected file</div><p>${esc(f.name)} · ${Math.ceil(f.size / 1024)} KB · ${problem ? 'rejected, see the error above' : 'queued for validation and extraction on confirm'}.</p></div>`;\n      renderFileError(problem);\n    }",
    ),
    # F6: login loading state before routing
    (
        APP,
        "  function loginPage() {\n    return `",
        "  function loginPage() {\n    if (state.signingIn) {\n      return `\n      <div class=\"login\">\n        <section class=\"login-brand\" aria-label=\"BSR Market Intelligence\"><div class=\"brand-lockup\"><div class=\"brand-mark\">BSR</div><div><div class=\"brand-name\">Market Intelligence</div><div class=\"brand-sub\">Reasonary AI · Auker intelligence layer</div></div></div></section>\n        <section class=\"login-panel\" aria-labelledby=\"signin-loading-title\" aria-busy=\"true\">\n          <h2 id=\"signin-loading-title\">Preparing your workspace…</h2>\n          <p role=\"status\">Applying the ${esc(pendingRoleLabel())} permission scope. Restricted data and actions are resolved before the workspace renders.</p>\n          <ul class=\"signin-steps\"><li class=\"done\">Demo identity verified</li><li class=\"active\">Loading permitted scope</li><li>Opening overview</li></ul>\n          <div class=\"login-note\">If the scope cannot be resolved, the workspace denies the route instead of showing unfiltered data.</div>\n        </section>\n      </div>`;\n    }\n    return `",
    ),
    # F6b: helper for pending role label, placed before loginPage
    (
        APP,
        "  function loginPage() {",
        "  function pendingRoleLabel() {\n    const r = D.roles[state.pendingRole] || D.roles[state.role];\n    return r ? r.label : 'demo';\n  }\n\n  function loginPage() {",
    ),
    # F6c: login action enters loading state then routes
    (
        APP,
        "      case 'login':\n        state.role = el.dataset.role; state.route = 'overview'; history.pushState(null, '', '#overview'); render(); break;",
        "      case 'login': {\n        const next = el.dataset.role;\n        state.pendingRole = next;\n        state.signingIn = true;\n        render();\n        setTimeout(() => { state.signingIn = false; state.role = next; state.route = 'overview'; history.pushState(null, '', '#overview'); render(); }, 600);\n        break;\n      }",
    ),
    # F7: footer allows wrapping
    (
        CSS,
        ".card-foot { padding: 10px 18px; border-top: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 11px; color: var(--ink-400); }",
        ".card-foot { padding: 10px 18px; border-top: 1px solid var(--line); display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px 12px; font-size: 11px; color: var(--ink-400); }\n.card-foot > span { min-width: 0; overflow-wrap: anywhere; }",
    ),
    # F6d: signin step styles
    (
        CSS,
        ".login-note { margin-top: 22px;",
        ".signin-steps { list-style: none; padding: 0; margin: 8px 0 0; display: grid; gap: 6px; font-size: 12px; color: var(--ink-600); }\n.signin-steps li { display: flex; align-items: center; gap: 8px; }\n.signin-steps li::before { content: \"\"; width: 6px; height: 6px; border-radius: 50%; background: var(--line-strong); flex: none; }\n.signin-steps li.done::before { background: var(--positive); }\n.signin-steps li.active::before { background: var(--copper); }\n.login-note { margin-top: 22px;",
    ),
]

errors = []
for path, old, new in patches:
    src = open(path, encoding='utf-8', newline='').read()
    n = src.count(old)
    if n != 1:
        errors.append(f'{path}: expected 1 match, found {n}')
        continue
    open(path, 'w', encoding='utf-8', newline='').write(src.replace(old, new, 1))

if errors:
    print('FAILED')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print(f'APPLIED {len(patches)} patches')
