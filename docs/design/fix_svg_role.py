import sys

p = 'docs/design/prototype/assets/app.js'
s = open(p, encoding='utf-8', newline='').read()

old = """    const svg = `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" ${eventsInRange.length ? 'role="group"' : 'role="img"'} aria-label="${esc((opts.ariaLabel || 'Time series chart') + (eventsInRange.length ? ` with ${eventsInRange.length} event marker${eventsInRange.length === 1 ? '' : 's'}` : ''))}">"""
new = """    const markerNote = eventsInRange.length ? ' with ' + eventsInRange.length + ' event marker' + (eventsInRange.length === 1 ? '' : 's') : '';
    const svgRole = eventsInRange.length ? 'group' : 'img';
    const svg = `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" role="${svgRole}" aria-label="${esc((opts.ariaLabel || 'Time series chart') + markerNote)}">"""

print('svg anchor count', s.count(old))
if s.count(old) != 1:
    sys.exit(1)

# login loading block: rewrite the nested template to plain concatenation
old2 = """    if (state.signingIn) {
      return `
      <div class="login">"""
new2 = """    if (state.signingIn) {
      return '' +
      '<div class="login">'"""

print('login anchor count', s.count(old2))
if s.count(old2) == 1:
    s = s.replace(old2, new2, 1)

s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('done')
