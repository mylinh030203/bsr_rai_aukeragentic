import subprocess, sys, time, os
from playwright.sync_api import sync_playwright

ROOT = r"D:\ReasonaryAI\BSR_Market_Intel - auker\docs\design\prototype"
OUT = r"D:\ReasonaryAI\BSR_Market_Intel - auker\docs\design\_tmp_verify\shots"
BASE = "http://127.0.0.1:8899"

def main():
    server = subprocess.Popen([sys.executable, "-m", "http.server", "8899", "--bind", "127.0.0.1"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(2.0)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            def themed_page(theme, vp):
                ctx = browser.new_context(viewport=vp)
                pg = ctx.new_page()
                pg.add_init_script("window.localStorage.setItem('bsr-theme','" + theme + "')")
                return pg
            def cap(page, name):
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(700)
                page.screenshot(path=os.path.join(OUT, name))
                print("SAVED", name)
            vp390 = {"width": 390, "height": 844}
            for theme in ("light", "dark"):
                page = themed_page(theme, vp390)
                page.goto(BASE + "/", wait_until="load"); page.wait_for_timeout(500)
                cap(page, "re-login-" + theme + "-390.png")
                for rname, rhash in (("overview", "#/overview"), ("market-data", "#/market-data"), ("news", "#/news")):
                    page.goto(BASE + "/" + rhash, wait_until="load"); page.wait_for_timeout(500)
                    cap(page, "re-" + rname + "-" + theme + "-390.png")
                    if rname == "market-data":
                        page.locator("table.data").first.scroll_into_view_if_needed()
                        cap(page, "re-market-data-table-" + theme + "-390.png")
                    if rname == "overview":
                        page.locator(".metric-card").nth(4).scroll_into_view_if_needed()
                        cap(page, "re-overview-b-" + theme + "-390.png")
                if theme == "dark":
                    page.goto(BASE + "/#/news", wait_until="load"); page.wait_for_timeout(600)
                    page.click('[data-action="open-news"]')
                    page.wait_for_timeout(600)
                    cap(page, "re-news-drawer-dark-390.png")
            page2 = themed_page("dark", {"width": 1440, "height": 900})
            page2.goto(BASE + "/#/overview", wait_until="load"); page2.wait_for_timeout(700)
            cap(page2, "re-overview-dark-1440.png")
            browser.close()
    finally:
        server.terminate()

main()
