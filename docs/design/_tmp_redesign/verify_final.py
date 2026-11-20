import json, pathlib, re
from playwright.sync_api import sync_playwright
URL = "file:///D:/ReasonaryAI/BSR_Market_Intel%20-%20auker/docs/design/prototype/index.html"
OUT = pathlib.Path("docs/design/_tmp_redesign/shots"); OUT.mkdir(parents=True, exist_ok=True)
msgs, res = [], {}
def tape(pg):
    return pg.evaluate("""() => {
      const tr = document.querySelector('.market-tape-track');
      const items = [...document.querySelectorAll('.tape-item')];
      return { scrollW: tr.scrollWidth, clientW: tr.clientWidth, count: items.length,
               docScrollW: document.documentElement.scrollWidth, innerW: window.innerWidth,
               afterDisplay: getComputedStyle(document.querySelector('.market-tape'), '::after').display,
               items: items.map(i => { const r = i.getBoundingClientRect(); return { text: i.innerText.replace(/\s+/g,' ').trim(), left: Math.round(r.left), right: Math.round(r.right), clipped: i.scrollWidth > i.clientWidth + 1 }; }) };
    }""")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.on("console", lambda m: msgs.append(m.type + ": " + m.text))
    pg.on("pageerror", lambda e: msgs.append("pageerror: " + str(e)))
    pg.goto(URL); pg.wait_for_timeout(700)
    pg.screenshot(path=str(OUT / "vf-login-light-1440.png"))
    pg.get_by_role("button", name=re.compile("Ban lãnh đạo")).first.click()
    pg.wait_for_selector(".market-tape-track", timeout=20000); pg.wait_for_timeout(1400)
    res["tape_1440"] = tape(pg)
    res["hash_before"] = pg.evaluate("location.hash")
    pg.screenshot(path=str(OUT / "vf-overview-light-1440.png"))
    pg.set_viewport_size({"width": 1280, "height": 800}); pg.wait_for_timeout(700)
    res["tape_1280"] = tape(pg)
    pg.screenshot(path=str(OUT / "vf-overview-light-1280.png"))
    pg.set_viewport_size({"width": 1440, "height": 900}); pg.wait_for_timeout(600)
    res["styles_light"] = pg.evaluate("""() => {
      const pick = (sel) => { const e = document.querySelector(sel); if (!e) return null; const cs = getComputedStyle(e); return { color: cs.color, bg: cs.backgroundColor, size: cs.fontSize }; };
      return { title: pick('.page-title'), metricValue: pick('.metric-card .metric-value'), tapeValue: pick('.tape-item .t-value'), tapeUnit: pick('.tape-item .t-unit'), appBg: getComputedStyle(document.body).backgroundColor, topbarBg: pick('.topbar') };
    }""")
    pg.locator(".metric-card").first.click(); pg.wait_for_timeout(800)
    res["hash_after_metric"] = pg.evaluate("location.hash")
    res["panel_probe"] = pg.evaluate("""() => { const p = document.getElementById('overview-inline-panel'); if (!p) return null;
      return { tabs: [...p.querySelectorAll('.range-tab')].map(t => t.textContent.trim()),
               cta: (p.querySelector('a[href="#market-data"]') || {}).textContent,
               close: (p.querySelector('[data-action="close-inline-metric"]') || {}).getAttribute('aria-label'),
               chartH: Math.round((p.querySelector('.inline-chart-body') || {clientHeight:0}).clientHeight) }; }""")
    pg.screenshot(path=str(OUT / "vf-inline-light-1440.png"))
    pg.locator('[data-action="set-inline-range"][data-range="90"]').click(); pg.wait_for_timeout(500)
    res["panel_after_90"] = pg.evaluate("!!document.getElementById('overview-inline-panel')")
    pg.screenshot(path=str(OUT / "vf-inline-90-light-1440.png"))
    pg.locator('[data-action="close-inline-metric"]').click(); pg.wait_for_timeout(500)
    res["panel_after_close"] = pg.evaluate("!!document.getElementById('overview-inline-panel')")
    res["hash_after_close"] = pg.evaluate("location.hash")
    pg.locator('[data-theme-value="dark"]').click(); pg.wait_for_timeout(700)
    res["theme_dark"] = pg.evaluate("[document.documentElement.getAttribute('data-theme'), localStorage.getItem('bsr-theme')]")
    pg.screenshot(path=str(OUT / "vf-overview-dark-1440.png"))
    res["styles_dark"] = pg.evaluate("""() => {
      const pick = (sel) => { const e = document.querySelector(sel); if (!e) return null; const cs = getComputedStyle(e); return { color: cs.color, bg: cs.backgroundColor, size: cs.fontSize }; };
      return { title: pick('.page-title'), metricValue: pick('.metric-card .metric-value'), tapeValue: pick('.tape-item .t-value'), tapeUnit: pick('.tape-item .t-unit'), appBg: getComputedStyle(document.body).backgroundColor, topbarBg: pick('.topbar') };
    }""")
    pg.reload(); pg.wait_for_timeout(1600)
    res["theme_after_reload"] = pg.evaluate("[document.documentElement.getAttribute('data-theme'), localStorage.getItem('bsr-theme')]")
    pg.screenshot(path=str(OUT / "vf-overview-dark-reload-1440.png"))
    pg.locator('[data-theme-value="light"]').click(); pg.wait_for_timeout(600)
    res["theme_back_light"] = pg.evaluate("document.documentElement.getAttribute('data-theme')")
    pg.set_viewport_size({"width": 390, "height": 844}); pg.wait_for_timeout(800)
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)
    res["mobile"] = pg.evaluate("""() => { const lb = [...document.querySelectorAll('.metric-card .metric-label')].map(e => ({ t: e.innerText.trim(), clipped: e.scrollWidth > e.clientWidth + 1 }));
      const ti = document.querySelector('.market-tape-track');
      return { docScrollW: document.documentElement.scrollWidth, innerW: window.innerWidth, tapeScrollW: ti ? ti.scrollWidth : null, tapeClientW: ti ? ti.clientWidth : null, labels: lb }; }""")
    pg.screenshot(path=str(OUT / "vf-overview-light-390.png"))
    pg.locator('[data-theme-value="dark"]').click(); pg.wait_for_timeout(700)
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT / "vf-overview-dark-390.png"))
    pg.set_viewport_size({"width": 1440, "height": 900}); pg.wait_for_timeout(700)
    try:
        pg.locator('[data-action="set-lang"][data-lang="en"]').first.click(); pg.wait_for_timeout(600)
        res["en_head"] = pg.evaluate("document.body.innerText.slice(0,160)")
        pg.locator('[data-action="set-lang"][data-lang="vi"]').first.click(); pg.wait_for_timeout(600)
        res["vi_head"] = pg.evaluate("document.body.innerText.slice(0,160)")
    except Exception as e:
        res["lang_err"] = str(e)
    res["console"] = msgs
    b.close()
print(json.dumps(res, ensure_ascii=False, indent=1))
