import json, pathlib, re
from playwright.sync_api import sync_playwright

URL = "file:///D:/ReasonaryAI/BSR_Market_Intel%20-%20auker/docs/design/prototype/index.html"
OUT = pathlib.Path("docs/design/_tmp_redesign/shots")
OUT.mkdir(parents=True, exist_ok=True)
res = {}

def tape_metrics(pg):
    return pg.evaluate("""() => {
      const t = document.querySelector('.market-tape-track');
      if (!t) return { error: 'no tape', hash: location.hash, body: document.body.innerText.slice(0, 300) };
      const items = [...document.querySelectorAll('.tape-item')];
      return {
        scrollW: t.scrollWidth, clientW: t.clientWidth,
        docScrollW: document.documentElement.scrollWidth, innerW: window.innerWidth,
        items: items.map(i => { const r = i.getBoundingClientRect(); return { text: i.innerText.replace(/\\s+/g,' ').trim(), w: Math.round(r.width), right: Math.round(r.right) }; })
      };
    }""")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(URL)
    pg.get_by_role("button", name=re.compile("Ban lãnh đạo")).first.click()
    pg.wait_for_selector(".market-tape-track", timeout=20000)
    pg.wait_for_timeout(1200)
    res["hash_after_login"] = pg.evaluate("location.hash")
    res["tape_1440"] = tape_metrics(pg)
    pg.screenshot(path=str(OUT / "tape-1440-light.png"))

    pg.set_viewport_size({"width": 1280, "height": 800})
    pg.wait_for_timeout(300)
    res["tape_1280"] = tape_metrics(pg)
    pg.screenshot(path=str(OUT / "tape-1280-light.png"))

    pg.set_viewport_size({"width": 1440, "height": 900})
    pg.wait_for_timeout(300)
    pg.locator(".metric-card").first.click()
    pg.wait_for_timeout(500)
    res["hash_after_metric_click"] = pg.evaluate("location.hash")
    res["panel"] = pg.evaluate("""() => {
      const p = document.getElementById('overview-inline-panel');
      if (!p) return null;
      return { tabs: [...p.querySelectorAll('.range-tab')].map(t => t.textContent.trim()),
               link: (p.querySelector('a[href=\"#market-data\"]') || {}).textContent,
               closeLabel: (p.querySelector('[data-action=\"close-inline-metric\"]') || {}).getAttribute('aria-label'),
               title: (p.querySelector('.inline-chart-title') || {}).textContent };
    }""")
    pg.screenshot(path=str(OUT / "inline-open-1440.png"))
    pg.locator('[data-action="close-inline-metric"]').click()
    pg.wait_for_timeout(400)
    res["panel_after_close"] = pg.evaluate("!!document.getElementById('overview-inline-panel')")

    pg.locator('[data-theme-value="dark"]').click()
    pg.wait_for_timeout(400)
    res["theme_after_click"] = pg.evaluate("document.documentElement.getAttribute('data-theme')")
    pg.screenshot(path=str(OUT / "tape-1440-dark.png"))
    pg.reload()
    pg.wait_for_timeout(600)
    res["theme_after_reload"] = pg.evaluate("document.documentElement.getAttribute('data-theme')")
    res["hash_after_reload"] = pg.evaluate("location.hash")
    pg.screenshot(path=str(OUT / "tape-1440-dark-reload.png"))

    pg.set_viewport_size({"width": 390, "height": 844})
    pg.wait_for_timeout(400)
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(200)
    res["tape_390_dark"] = tape_metrics(pg)
    pg.screenshot(path=str(OUT / "tape-390-dark.png"))
    pg.locator('[data-theme-value="light"]').click()
    pg.wait_for_timeout(400)
    res["tape_390_light"] = tape_metrics(pg)
    pg.screenshot(path=str(OUT / "tape-390-light.png"))
    b.close()

print(json.dumps(res, ensure_ascii=False, indent=1))
