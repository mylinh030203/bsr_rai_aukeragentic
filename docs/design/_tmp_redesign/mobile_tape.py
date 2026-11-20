import io
p = 'docs/design/prototype/assets/styles.css'
s = io.open(p, encoding='utf-8').read()
block = """
/* Tape on tablet/mobile: a wrapped grid, not a horizontal scroller. Every quote
   stays readable without a gesture; the label owns its own line so the value can
   never ellipsise it away. */
@media (max-width: 1199px) {
  .market-tape { overflow: hidden; }
  .market-tape-track { flex-wrap: wrap; overflow-x: visible; padding-right: 0; }
  .market-tape::after, .market-tape::before { display: none; }
  .tape-item { flex: 1 0 33.333%; flex-wrap: wrap; align-items: baseline; row-gap: 1px; border-right: 0; border-bottom: 1px solid var(--line); }
  .tape-item .t-status { display: none; }
  .tape-item .t-label { flex: 1 0 100%; font-size: 9px; }
}
@media (max-width: 480px) {
  .tape-item { flex: 1 0 50%; }
}
"""
if 'Tape on tablet/mobile' not in s:
    s = s.rstrip() + "\n" + block
io.open(p, 'w', encoding='utf-8').write(s)
print('OK' if 'Tape on tablet/mobile' in s else 'FAIL')
