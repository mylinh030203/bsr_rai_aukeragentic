"""One-shot Playwright verification harness for the static BSR prototype.

Run from the project root:
    python docs/design/_tmp_verify/verify_all.py

Writes screenshots to docs/design/_tmp_verify/shots/ and prints a JSON summary
to stdout (delimited by ===JSON-BEGIN=== / ===JSON-END===).
"""

from __future__ import annotations

import json
import os
import sys
import traceback

BASE = "http://127.0.0.1:8123"
OUT_DIR = os.path.join("docs", "design", "_tmp_verify")
SHOTS = os.path.join(OUT_DIR, "shots")
os.makedirs(SHOTS, exist_ok=True)

ROUTES = [
    ("login", ""),
    ("overview", "#/overview"),
    ("market-data", "#/market-data"),
    ("news", "#/news"),
    ("forecast", "#/forecast"),
    ("analysis", "#/analysis"),
    ("assistant", "#/assistant"),
    ("reports", "#/reports"),
    ("admin", "#/admin"),
]

SHOT_ROUTES = ["overview", "market-data", "news", "assistant", "reports", "admin"]

VIEWPORTS = [1440, 1024, 768, 390]

CONTRAST_SELECTORS = [
    ".muted",
    ".chip",
    ".card-sub",
    ".tape-item",
    ".perm-badge",
    "th",
    ".small.muted",
    "table.data td",
    ".pipeline-step",
    ".timeline-row dt",
    ".dedup-row",
    ".impact-q",
]

CONTRAST_ROUTES = ["market-data", "news"]

VIEWPORT_SIZES = [(1440, 900), (1024, 900), (768, 1024), (390, 844)]

# JS helper injected into the page: resolves effective fg/bg colors and ratio.
CONTRAST_JS = r"""
(selectors) => {
  function parse(c) {
    if (!c) return null;
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\s\/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  }
  function over(top, bottom) {
    if (!top) return bottom;
    const a = top.a;
    return {
      r: top.r * a + bottom.r * (1 - a),
      g: top.g * a + bottom.g * (1 - a),
      b: top.b * a + bottom.b * (1 - a),
      a: 1,
    };
  }
  function effBg(el) {
    const stack = [];
    let node = el;
    while (node && node.nodeType === 1) {
      const cs = getComputedStyle(node);
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) {
        stack.push(c);
        if (c.a >= 1) break;
      }
      node = node.parentElement;
    }
    let base = { r: 255, g: 255, b: 255, a: 1 };
    for (let i = stack.length - 1; i >= 0; i--) base = over(stack[i], base);
    return base;
  }
  function lum(c) {
    const f = (v) => {
      v = v / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  }
  function visible(el) {
    if (!el || !el.getBoundingClientRect) return false;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) return false;
    return true;
  }
  const out = [];
  for (const sel of selectors) {
    const els = Array.from(document.querySelectorAll(sel)).filter(visible);
    if (!els.length) { out.push({ selector: sel, count: 0 }); continue; }
    const el = els[0];
    const cs = getComputedStyle(el);
    const bg = effBg(el);
    const fgRaw = parse(cs.color) || { r: 0, g: 0, b: 0, a: 1 };
    const fg = over(fgRaw, bg);
    const l1 = lum(fg), l2 = lum(bg);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const size = parseFloat(cs.fontSize);
    const weight = parseInt(cs.fontWeight, 10) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    out.push({
      selector: sel,
      count: els.length,
      text: (el.textContent || "").trim().slice(0, 60),
      fg: `rgb(${Math.round(fg.r)},${Math.round(fg.g)},${Math.round(fg.b)})`,
      bg: `rgb(${Math.round(bg.r)},${Math.round(bg.g)},${Math.round(bg.b)})`,
      fontSize: size,
      fontWeight: weight,
      large,
      ratio: Math.round(ratio * 100) / 100,
      threshold: large ? 3.0 : 4.5,
      pass: ratio >= (large ? 3.0 : 4.5),
    });
  }
  return out;
}
"""


def set_theme(page, theme: str) -> None:
    """Set theme by clicking the toggle until html[data-theme] matches."""
    for _ in range(3):
        cur = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
        if cur == theme:
            return
        btn = page.query_selector('[data-action="toggle-theme"]')
        if not btn:
            page.evaluate(
                "(t) => { localStorage.setItem('bsr-theme', t);"
                " document.documentElement.setAttribute('data-theme', t); }",
                theme,
            )
            return
        btn.click()
        page.wait_for_timeout(250)
    cur = page.evaluate("() => document.documentElement.getAttribute('data-theme')")
    if cur != theme:
        page.evaluate(
            "(t) => { localStorage.setItem('bsr-theme', t);"
            " document.documentElement.setAttribute('data-theme', t); }",
            theme,
        )


def safe(fn, default=None):
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 - harness must survive one failure
        return default if default is not None else {"error": f"{type(exc).__name__}: {exc}"}


def count_text(page, text: str) -> int:
    try:
        return page.get_by_text(text, exact=False).count()
    except Exception:
        return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from playwright.sync_api import sync_playwright

    summary = {
        "base": BASE,
        "routes": {},
        "contrast_dark": [],
        "gaps": [],
        "screenshots": [],
        "notes": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        # ---------------------------------------------------------------- A/B
        for route_name, hash_part in ROUTES:
            url = f"{BASE}/index.html{hash_part}"
            for theme in ("light", "dark"):
                key = f"{route_name}|{theme}"
                entry = {
                    "themePersist": None,
                    "themeAfterReload": None,
                    "localStorage": None,
                    "overflowPx": None,
                    "viewport": None,
                    "consoleErrors": [],
                }
                errors: list[str] = []
                page.on("console", lambda m, e=errors: e.append(m.text) if m.type == "error" else None)
                page.on("pageerror", lambda exc, e=errors: e.append(f"pageerror: {exc}"))
                try:
                    page.goto(url, wait_until="load")
                    page.wait_for_timeout(400)
                    set_theme(page, theme)
                    page.reload(wait_until="load")
                    page.wait_for_timeout(500)
                    entry["themeAfterReload"] = page.evaluate(
                        "() => document.documentElement.getAttribute('data-theme')"
                    )
                    entry["localStorage"] = page.evaluate(
                        "() => localStorage.getItem('bsr-theme')"
                    )
                    entry["themePersist"] = (
                        entry["themeAfterReload"] == theme
                        and entry["localStorage"] == theme
                    )
                    entry["viewport"] = page.evaluate("() => window.innerWidth")
                    entry["overflowPx"] = page.evaluate(
                        "() => document.documentElement.scrollWidth - window.innerWidth"
                    )
                except Exception as exc:  # noqa: BLE001
                    entry["error"] = f"{type(exc).__name__}: {exc}"
                entry["consoleErrors"] = errors
                summary["routes"][key] = entry
                page.remove_listener("console", lambda *_: None) if False else None

        # -------------------------------------------------- overflow viewports
        overflow = {}
        for vw, vh in VIEWPORT_SIZES:
            page.set_viewport_size({"width": vw, "height": vh})
            for route_name, hash_part in ROUTES:
                for theme in ("light", "dark"):
                    key = f"{route_name}|{theme}|{vw}x{vh}"
                    try:
                        page.goto(f"{BASE}/index.html{hash_part}", wait_until="load")
                        page.wait_for_timeout(300)
                        set_theme(page, theme)
                        page.wait_for_timeout(200)
                        overflow[key] = {
                            "viewport": f"{vw}x{vh}",
                            "innerWidth": page.evaluate("() => window.innerWidth"),
                            "scrollWidth": page.evaluate("() => document.documentElement.scrollWidth"),
                            "overflowPx": page.evaluate(
                                "() => document.documentElement.scrollWidth - window.innerWidth"
                            ),
                        }
                    except Exception as exc:  # noqa: BLE001
                        overflow[key] = {"viewport": f"{vw}x{vh}", "error": f"{type(exc).__name__}: {exc}"}
        summary["overflow_matrix"] = overflow
        page.set_viewport_size({"width": 1440, "height": 900})

        # ------------------------------------------------------- screenshots
        for theme in ("light", "dark"):
            for route_name in SHOT_ROUTES:
                hash_part = dict(ROUTES)[route_name]
                try:
                    page.goto(f"{BASE}/index.html{hash_part}", wait_until="load")
                    page.wait_for_timeout(500)
                    set_theme(page, theme)
                    page.wait_for_timeout(300)
                    path = os.path.join(SHOTS, f"{route_name}-{theme}.png")
                    page.screenshot(path=path, full_page=True)
                    summary["screenshots"].append(path)
                except Exception as exc:  # noqa: BLE001
                    summary["notes"].append(f"screenshot {route_name}/{theme}: {exc}")
            # news drawer
            try:
                page.goto(f"{BASE}/index.html#/news", wait_until="load")
                page.wait_for_timeout(500)
                set_theme(page, theme)
                opener = page.query_selector('[data-action="open-news"]')
                if opener:
                    opener.click()
                    page.wait_for_timeout(600)
                    path = os.path.join(SHOTS, f"news-drawer-{theme}.png")
                    page.screenshot(path=path, full_page=True)
                    summary["screenshots"].append(path)
                else:
                    summary["notes"].append(f"news drawer {theme}: no open-news trigger")
            except Exception as exc:  # noqa: BLE001
                summary["notes"].append(f"news drawer {theme}: {exc}")

        # ------------------------------------------------------ contrast dark
        contrast = {}
        for croute in CONTRAST_ROUTES:
            try:
                page.goto(f"{BASE}/index.html{dict(ROUTES)[croute]}", wait_until="load")
                page.wait_for_timeout(500)
                set_theme(page, "dark")
                page.wait_for_timeout(300)
                contrast[croute] = page.evaluate(CONTRAST_JS, CONTRAST_SELECTORS)
            except Exception as exc:  # noqa: BLE001
                contrast[croute] = {"error": f"{type(exc).__name__}: {exc}"}
                summary["notes"].append(f"contrast {croute}: {exc}")
        summary["contrast_dark"] = contrast
        flat = []
        for croute, rows in contrast.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if row.get("count") and not row.get("pass", True):
                    flat.append({"route": croute, **row})
        summary["contrast_failures"] = flat

        # ---------------------------------------------------------- gap items
        def open_news_drawer():
            page.goto(f"{BASE}/index.html#/news", wait_until="load")
            page.wait_for_timeout(600)
            opener = page.query_selector('[data-action="open-news"]')
            if opener:
                opener.click()
                page.wait_for_timeout(700)
                return True
            return False

        def close_overlays():
            try:
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
            except Exception:  # noqa: BLE001
                pass

        def gap(item, route, fn, prep=None):
            hash_part = dict(ROUTES)[route]
            try:
                page.goto(f"{BASE}/index.html{hash_part}", wait_until="load")
                page.wait_for_timeout(500)
            except Exception as exc:  # noqa: BLE001
                summary["notes"].append(f"gap {item} navigation: {exc}")
            prepped = None
            if prep is not None:
                try:
                    prepped = prep()
                except Exception as exc:  # noqa: BLE001
                    summary["notes"].append(f"gap {item} prep: {exc}")
            try:
                res = fn()
            except Exception as exc:  # noqa: BLE001
                res = {"found": False, "count": 0, "sample": f"error: {exc}"}
            if prepped is not None:
                res["prep"] = prepped
            res["item"] = item
            res["route"] = route
            res["status"] = "FOUND" if res.get("found") else "NOT-FOUND"
            summary["gaps"].append(res)
            close_overlays()

        NAV_LABELS = [
            "Tổng quan",
            "Dữ liệu thị trường",
            "Tin thị trường",
            "Dự báo",
            "Phân tích",
            "Trợ lý AI",
            "Báo cáo",
        ]

        def gap_nav():
            hits = [t for t in NAV_LABELS if count_text(page, t) > 0]
            nav_links = page.query_selector_all('nav a, [data-action="navigate"]')
            return {
                "found": len(hits) >= 6,
                "count": len(hits),
                "sample": " / ".join(hits) + f" | nav_locators={len(nav_links)}",
            }

        gap("1. Six-module navigation", "overview", gap_nav)

        def gap_admin():
            labels = [
                (l.text_content() or "").strip()
                for l in page.query_selector_all('[data-action="navigate"]')
            ]
            admin_nav = [l for l in labels if "Quản trị" in l or "Admin" in l]
            heading = count_text(page, "Người dùng và phạm vi quyền")
            return {
                "found": bool(admin_nav) or heading > 0,
                "count": len(admin_nav),
                "sample": f"nav={admin_nav[:2]} admin_area_text={heading}",
            }

        gap("2. Administration area", "admin", gap_admin)

        def gap_ai_table():
            page.fill('[data-action="prompt"]' if False else "#chat-input", "Brent spread outlook") if page.query_selector(
                "#chat-input"
            ) else None
            btn = page.query_selector('[data-action="send-chat"]')
            if btn:
                btn.click()
                page.wait_for_timeout(1200)
            tables = page.query_selector_all("#chat-body table")
            charts = page.query_selector_all("#chat-body svg, #chat-body canvas, #chat-body .chart")
            return {
                "found": (len(tables) + len(charts)) > 0,
                "count": len(tables) + len(charts),
                "sample": f"tables={len(tables)} charts={len(charts)}",
            }

        gap("3. AI answer table/chart", "assistant", gap_ai_table)

        def prep_report_builder():
            opener = page.query_selector('[data-action="open-report-builder"]')
            if opener:
                opener.click()
                page.wait_for_timeout(700)
                return "open-report-builder clicked"
            for label in ("Tạo bản tin", "Tạo báo cáo"):
                btn = page.get_by_text(label, exact=False).first
                if btn.count():
                    btn.click()
                    page.wait_for_timeout(700)
                    return f"text button {label}"
            return "no opener"

        def gap_report_types():
            opts = page.query_selector_all("#report-type option")
            labels = [(o.text_content() or "").strip() for o in opts]
            wanted = [
                "Bản tin sáng",
                "Báo cáo cuối ngày",
                "Báo cáo thị trường ngày",
                "Báo cáo thị trường tuần",
                "Báo cáo thị trường tháng",
                "Phân tích thị trường theo yêu cầu",
                "Báo cáo thị trường theo sự kiện",
            ]
            hit = [w for w in wanted if any(w.lower() in l.lower() for l in labels)]
            return {
                "found": len(labels) == 7 and len(hit) == 7,
                "count": len(labels),
                "sample": "; ".join(labels) if labels else "no #report-type options",
            }

        gap("4. Seven report types", "reports", gap_report_types, prep=prep_report_builder)

        def gap_chart_modes():
            btns = page.query_selector_all('[data-action="set-chart-mode"]')
            labels = [(b.text_content() or "").strip() for b in btns]
            return {"found": len(btns) >= 4, "count": len(btns), "sample": "; ".join(labels)}

        gap("5. Chart modes", "market-data", gap_chart_modes)

        def prep_news_intake():
            opener = page.query_selector('[data-action="open-news-input"]')
            if opener:
                opener.click()
                page.wait_for_timeout(700)
                return "open-news-input clicked"
            btn = page.get_by_text("Nhập", exact=False).first
            if btn.count():
                btn.click()
                page.wait_for_timeout(700)
                return "text button Nhập"
            return "no opener"

        def gap_news_intake():
            url_input = page.query_selector("#news-url-input")
            file_input = page.query_selector("#news-file-input")
            accept = (file_input.get_attribute("accept") or "") if file_input else ""
            office = any(k in accept.lower() for k in ("docx", "xlsx", "doc", "xls"))
            return {
                "found": bool(url_input) and bool(file_input) and office,
                "count": int(bool(url_input)) + int(bool(file_input)),
                "sample": f"url_input={bool(url_input)} file_input={bool(file_input)} accept={accept}",
            }

        gap("6. News intake URL + Office upload", "news", gap_news_intake, prep=prep_news_intake)

        def gap_pipeline():
            steps = page.query_selector_all(".pipeline-step")
            retry = page.query_selector_all('[data-action="pipeline-retry"]')
            manual = page.query_selector_all('[data-action="pipeline-manual"]')
            labels = [(s.text_content() or "").strip()[:30] for s in steps]
            return {
                "found": len(steps) == 11 and (len(retry) + len(manual)) > 0,
                "count": len(steps),
                "sample": f"steps={len(steps)} retry={len(retry)} manual={len(manual)} | {'; '.join(labels[:11])}",
            }

        gap("7. Eleven-step pipeline", "news", gap_pipeline, prep=open_news_drawer)

        def gap_topics():
            opts = page.query_selector_all("#news-topic option")
            labels = [(o.text_content() or "").strip() for o in opts]
            return {"found": len(labels) >= 12, "count": len(labels), "sample": "; ".join(labels[:12])}

        gap("8. Twelve news topics", "news", gap_topics)

        def gap_monitoring():
            mon = count_text(page, "Theo dõi liên tục")
            alert = count_text(page, "cảnh báo") + count_text(page, "Cảnh báo")
            return {
                "found": mon > 0 and alert > 0,
                "count": mon + alert,
                "sample": f"monitoring={mon} alert={alert}",
            }

        gap("9. Continuous monitoring + alerts", "news", gap_monitoring, prep=open_news_drawer)

        def gap_dedup():
            rows = page.query_selector_all(".dedup-row")
            return {
                "found": len(rows) == 4,
                "count": len(rows),
                "sample": (rows[0].text_content() or "").strip()[:80] if rows else "",
            }

        gap("10. Dedup relations", "news", gap_dedup, prep=open_news_drawer)

        def gap_sources():
            table = page.query_selector_all("table.source-manager-table")
            heads = page.query_selector_all("table.source-manager-table thead th")
            label = count_text(page, "Quản lý nguồn")
            return {
                "found": len(table) > 0 or label > 0,
                "count": len(table) + label,
                "sample": f"source-manager-table={len(table)} columns={len(heads)} label={label}",
            }

        gap("11. Source manager", "admin", gap_sources)

        def gap_perms():
            badges = page.query_selector_all(".perm-badge")
            label = count_text(page, "Người dùng và phạm vi quyền")
            heads = [
                (h.text_content() or "").strip().lower()
                for h in page.query_selector_all("table.data thead th")
            ]
            dept = any("phòng ban" in h or "department" in h for h in heads)
            doc = any("tài liệu" in h or "document" in h for h in heads)
            return {
                "found": label > 0 and (dept or doc or len(badges) > 0),
                "count": len(badges) + label,
                "sample": f"label={label} perm_badges={len(badges)} dept_col={dept} doc_col={doc}",
            }

        gap("12. Department + document permissions", "admin", gap_perms)

        def gap_timestamps():
            rows = page.query_selector_all(".timeline-row")
            labels = [(r.text_content() or "").strip()[:40] for r in rows]
            return {"found": len(rows) >= 6, "count": len(rows), "sample": "; ".join(labels[:6])}

        gap("13. Six timestamp types", "news", gap_timestamps, prep=open_news_drawer)

        def gap_lineage():
            n = count_text(page, "Truy xuất nguồn gốc dữ liệu")
            return {
                "found": n > 0,
                "count": n,
                "sample": "Truy xuất nguồn gốc dữ liệu" if n else "not found",
            }

        gap("14. Data lineage", "news", gap_lineage, prep=open_news_drawer)

        def gap_rubric():
            rows = page.query_selector_all(".rubric-table tbody tr")
            label = count_text(page, "Bộ tiêu chí đánh giá AI")
            return {
                "found": label > 0 and len(rows) >= 10,
                "count": len(rows),
                "sample": f"label={label} rubric rows={len(rows)}",
            }

        gap("15. AI Evaluation rubric (10 groups)", "admin", gap_rubric)

        def gap_recommendation():
            n = count_text(page, "Khuyến nghị") + count_text(page, "Recommendation")
            return {"found": n > 0, "count": n, "sample": f"recommendation text={n}"}

        gap("16. Recommendation record", "analysis", gap_recommendation)

        def gap_geo():
            n = count_text(page, "Tình báo địa chính trị") + count_text(
                page, "Geopolitical Intelligence"
            )
            return {
                "found": n > 0,
                "count": n,
                "sample": "Tình báo địa chính trị" if n else "not found",
            }

        gap("17. Geopolitical Intelligence", "analysis", gap_geo)

        def gap_impact():
            items = page.query_selector_all(".impact-list li")
            label = count_text(page, "Phân tích tác động thị trường")
            return {
                "found": len(items) >= 7,
                "count": len(items),
                "sample": f"impact items={len(items)} label={label}",
            }

        gap("18. Market Impact Analysis (7 questions)", "analysis", gap_impact)

        browser.close()

    print("===JSON-BEGIN===")
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    print("===JSON-END===")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        sys.exit(1)
