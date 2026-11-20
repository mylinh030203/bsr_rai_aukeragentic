import json, pathlib, re
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(r"D:/ReasonaryAI/BSR_Market_Intel - auker")
URL = (ROOT / "docs/design/prototype/index.html").as_uri()
OUT = ROOT / "docs/design/_tmp_redesign/shots"
OUT.mkdir(parents=True, exist_ok=True)

PACK = r"""
() => {
  const q = (s, r=document) => r.querySelector(s);
  const pack = (el) => el ? {text:(el.innerText||'').replace(/\s+/g,' ').trim(), cw:el.clientWidth, sw:el.scrollWidth, ch:el.clientHeight, sh:el.scrollHeight, clipped: el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1} : null;
  const cards = [...document.querySelectorAll('.metric-card')].map(c => {
    const ch = q('.metric-change', c);
    const cs = ch ? getComputedStyle(ch) : null;
    return {label: pack(q('.metric-label', c)), muted: pack(q('.metric-change .muted', c)),
            change: ch ? {cw: ch.clientWidth, sw: ch.scrollWidth, clipped: ch.scrollWidth > ch.clientWidth + 1, ws: cs.whiteSpace, ov: cs.overflow} : null};
  });
  const track = q('.market-tape-track');
  return {cards, docW: document.documentElement.scrollWidth, innerW: window.innerWidth,
          tapeItems: document.querySelectorAll('.tape-item').length,
          tapeSW: track ? track.scrollWidth : null, tapeCW: track ? track.clientWidth : null};
}
"""

PANEL = r"""
() => {
  const p = document.getElementById('overview-inline-panel');
  if (!p) return {exists: false, hash: location.hash};
  const r = p.getBoundingClientRect();
  return {exists: true, hash: location.hash,
          rect: {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), right: Math.round(r.right)},
          innerW: window.innerWidth, docW: document.documentElement.scrollWidth,
          tabs: [...p.querySelectorAll('.range-tab')].map(t => t.textContent.trim()),
          cta: (p.querySelector('a[href="#market-data"]') || {}).textContent,
          close: (p.querySelector('[data-action="close-inline-metric"]') || {}).getAttribute('aria-label')};
}
"""

res, errs = {}, []

def enter(pg, w):
    pg.goto(URL); pg.wait_for_timeout(900)
    try:
        pg.get_by_role("button", name=re.compile("Ban lãnh đạo")).first.click(timeout=5000)
    except Exception as e:
        errs.append(f"{w}:roleclick:{e}")
        try:
            pg.get_by_text("Ban lãnh đạo").first.click(timeout=3000)
        except Exception as e2:
            errs.append(f"{w}:textclick:{e2}")
    try:
        pg.wait_for_selector(".market-tape-track", timeout=20000)
    except Exception as e:
        errs.append(f"{w}:tapewait:{e}")
    pg.wait_for_timeout(800)
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(600, 900), (700, 900)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.on("console", lambda m, w=w: errs.append(f"{w}:{m.type}:{m.text}") if m.type == "error" else None)
        pg.on("pageerror", lambda e, w=w: errs.append(f"{w}:pageerror:{e}"))
        enter(pg, w)
        res[f"band_{w}"] = pg.evaluate(PACK)
        pg.screenshot(path=str(OUT / f"band-{w}.png"))
        pg.close()
    for w, h in [(1024, 1000), (390, 900)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.on("console", lambda m, w=w: errs.append(f"{w}:{m.type}:{m.text}") if m.type == "error" else None)
        pg.on("pageerror", lambda e, w=w: errs.append(f"{w}:pageerror:{e}"))
        enter(pg, w)
        res[f"panel_{w}_hash_before"] = pg.evaluate("location.hash")
        pg.locator(".metric-card").first.click(); pg.wait_for_timeout(700)
        res[f"panel_{w}"] = pg.evaluate(PANEL)
        pg.screenshot(path=str(OUT / f"panel-{w}.png"))
        try:
            pg.locator('[data-action="close-inline-metric"]').click(); pg.wait_for_timeout(400)
            res[f"panel_{w}_after_close"] = pg.evaluate("!!document.getElementById('overview-inline-panel')")
        except Exception as e:
            errs.append(f"{w}:close:{e}")
        pg.close()
    b.close()

res["console"] = errs
print(json.dumps(res, ensure_ascii=True, indent=1))
