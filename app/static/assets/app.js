/* BSR Market Intelligence SPA — vanilla ES module, no build step. */

import { api, apiBlob, setCsrf } from "./api.js";
import { getLang, onLangChange, roleLabel, setLang, t } from "./i18n.js";

const ROUTES = [
  "login",
  "overview",
  "market-data",
  "news",
  "forecast",
  "analysis",
  "assistant",
  "reports",
  "admin",
];

const ROUTE_TITLES = {
  overview: "overview",
  "market-data": "marketData",
  news: "news",
  forecast: "forecast",
  analysis: "analysis",
  assistant: "assistant",
  reports: "reports",
  admin: "admin",
};

const state = {
  user: null,
  route: "login",
  loading: false,
  error: null,
  data: null,
  tape: [],
  asOf: null,
  freshness: null,
  sidebarCollapsed: false,
  mobileNav: false,
  range: "1M",
  compare: "",
  instrument: "brent_futures",
  newsFilters: { topic: "", source: "", status: "", q: "" },
  forecastFilters: { instrument: "", horizon: "" },
  analysisQuestion: "What is driving the recent move in product cracks?",
  chat: [],
  chatBusy: false,
  adminTab: "users",
  lastFocus: null,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const esc = (value) =>
  String(value == null ? "" : value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));

const fmtNum = (value, decimals = 2) =>
  value == null
    ? "—"
    : Number(value).toLocaleString("en-US", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      });

const fmtSigned = (value, decimals = 2) =>
  value == null ? "—" : `${value > 0 ? "+" : ""}${fmtNum(value, decimals)}`;

const fmtPct = (value) =>
  value == null ? "—" : `${value > 0 ? "+" : ""}${fmtNum(value, 2)}%`;

const fmtTime = (iso) => {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return esc(iso);
  return date
    .toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Asia/Ho_Chi_Minh",
    })
    .replace(",", " ·");
};

const fmtDate = (iso) => {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return esc(iso);
  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Ho_Chi_Minh",
  });
};

const directionClass = (value) => (value > 0 ? "pos" : value < 0 ? "neg" : "muted");

const ICONS = {
  overview: '<path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z"/>',
  data: '<path d="M3 19h18M5 16V8M10 16V5M15 16v-6M20 16V9"/>',
  news: '<path d="M5 4h14v16H5zM8 8h8M8 12h8M8 16h5"/>',
  forecast: '<path d="M3 17l5-6 4 3 6-8M16 6h4v4"/>',
  analysis: '<circle cx="10" cy="10" r="7"/><path d="M15 15l6 6"/>',
  assistant: '<path d="M12 3l1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8zM19 16l.9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9z"/>',
  reports: '<path d="M6 3h9l4 4v14H6zM15 3v5h4M9 13h7M9 17h7"/>',
  admin: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4v-.2a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6v-.2h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1z"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/>',
  bell: '<path d="M18 8a6 6 0 1 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  close: '<path d="M5 5l14 14M19 5L5 19"/>',
  chevron: '<path d="M9 18l6-6-6-6"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  download: '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
  upload: '<path d="M12 16V4M7 9l5-5 5 5M5 21h14"/>',
  lock: '<rect x="5" y="10" width="14" height="10" rx="1"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  check: '<path d="M4 12l5 5L20 6"/>',
  sparkle: '<path d="M12 3l1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8z"/>',
  print: '<path d="M6 9V3h12v6M6 18H4v-7h16v7h-2M7 14h10v7H7z"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  alert: '<path d="M12 3l10 18H2zM12 9v5M12 17h.01"/>',
  arrowRight: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  filter: '<path d="M4 5h16M7 12h10M10 19h4"/>',
};

function icon(name, size = 16) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ICONS.overview}</svg>`;
}

function toast(message, kind = "info") {
  const stack = $("#toast-stack");
  if (!stack) return;
  const node = document.createElement("div");
  node.className = `toast ${kind === "error" ? "error" : ""}`;
  node.setAttribute("role", kind === "error" ? "alert" : "status");
  node.innerHTML = `<span>${esc(message)}</span><button type="button" aria-label="${esc(t("close"))}">×</button>`;
  node.querySelector("button").addEventListener("click", () => node.remove());
  stack.appendChild(node);
  window.setTimeout(() => node.remove(), 5000);
}

function statusChip(status) {
  const map = {
    "real-time": "",
    delayed: "warn",
    eod: "warn",
    manual: "manual",
  };
  return `<span class="chip ${map[status] || ""}"><span class="dot"></span>${esc(status)}</span>`;
}

function classificationTag(classification) {
  const letter = { public: "P", internal: "I", confidential: "C", restricted: "R" }[classification] || "?";
  return `<span class="cls ${classification === "restricted" ? "restricted" : ""}">${letter} · ${esc(classification)}</span>`;
}

function badge(text, kind = "") {
  return `<span class="badge ${kind}">${esc(text)}</span>`;
}

/* ---------- Overlays ---------- */

function trapFocus(event, container) {
  if (event.key !== "Tab") return;
  const focusable = $$(
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    container,
  ).filter((node) => node.offsetParent !== null);
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function openDrawer(title, body, foot = "") {
  const drawer = $("#drawer");
  state.lastFocus = document.activeElement;
  drawer.innerHTML = `
    <div class="drawer-head">
      <h2 id="drawer-title">${esc(title)}</h2>
      <button class="icon-btn" type="button" data-action="close-overlays" aria-label="${esc(t("closeDrawer"))}" style="margin-left:auto">${icon("close")}</button>
    </div>
    <div class="drawer-body">${body}</div>
    ${foot ? `<div class="drawer-foot">${foot}</div>` : ""}`;
  drawer.hidden = false;
  drawer.setAttribute("aria-hidden", "false");
  const focusTarget = drawer.querySelector("button, a, input, select, textarea");
  if (focusTarget) focusTarget.focus();
}

function openModal(title, body, foot = "") {
  const modal = $("#modal");
  state.lastFocus = document.activeElement;
  modal.innerHTML = `
    <div class="modal-head">
      <h2 id="modal-title">${esc(title)}</h2>
      <button class="icon-btn" type="button" data-action="close-overlays" aria-label="${esc(t("close"))}" style="margin-left:auto">${icon("close")}</button>
    </div>
    <div class="modal-body">${body}</div>
    ${foot ? `<div class="modal-foot">${foot}</div>` : ""}`;
  modal.hidden = false;
  modal.setAttribute("aria-hidden", "false");
  const focusTarget = modal.querySelector("input, select, textarea, button");
  if (focusTarget) focusTarget.focus();
}

function closeOverlays() {
  ["#drawer", "#modal"].forEach((selector) => {
    const node = $(selector);
    if (!node) return;
    node.hidden = true;
    node.setAttribute("aria-hidden", "true");
    node.innerHTML = "";
  });
  if (state.lastFocus && typeof state.lastFocus.focus === "function") {
    state.lastFocus.focus();
  }
  state.lastFocus = null;
}

/* ---------- Shell ---------- */

function navItem(route, labelKey, iconName) {
  const active = state.route === route ? "active" : "";
  return `<a class="nav-item ${active}" href="#${route}" ${active ? 'aria-current="page"' : ""}>
    ${icon(iconName)}<span>${esc(t(labelKey))}</span></a>`;
}

function renderShell(content) {
  const user = state.user;
  const adminNav = user && user.is_admin ? navItem("admin", "admin", "admin") : "";
  const tape = state.tape.length
    ? `<div class="tape" role="group" aria-label="${esc(t("marketTape"))}">${state.tape
        .map(
          (item) => `<div class="tape-item">
            <span class="name">${esc(item.short_name)}</span>
            <span class="value">${fmtNum(item.value, 2)}</span>
            <span class="unit">${esc(item.unit)}</span>
            <span class="${directionClass(item.change)}">${fmtSigned(item.change)}</span>
          </div>`,
        )
        .join("")}</div>`
    : "";

  return `<div class="shell ${state.sidebarCollapsed ? "collapsed" : ""}">
    <aside class="sidebar ${state.mobileNav ? "open" : ""}" aria-label="Navigation">
      <div class="wordmark">
        <span class="mark" aria-hidden="true">B</span>
        <div><strong>BSR Market Intel</strong><span>${esc(t("tagline"))}</span></div>
      </div>
      <nav>
        <div class="nav-group">
          <div class="nav-label">${esc(t("overview"))}</div>
          ${navItem("overview", "overview", "overview")}
          ${navItem("market-data", "marketData", "data")}
          ${navItem("news", "news", "news")}
        </div>
        <div class="nav-group">
          <div class="nav-label">${esc(t("analysis"))}</div>
          ${navItem("forecast", "forecast", "forecast")}
          ${navItem("analysis", "analysis", "analysis")}
          ${navItem("assistant", "assistant", "assistant")}
          ${navItem("reports", "reports", "reports")}
        </div>
        ${adminNav ? `<div class="nav-group"><div class="nav-label">${esc(t("admin"))}</div>${adminNav}</div>` : ""}
      </nav>
      <div class="sidebar-footer">
        <p class="user">${esc(user ? user.name : "")}</p>
        <p>${esc(user ? roleLabel(user.role) : "")} · ${esc(user ? user.department : "")}</p>
        <p>${esc(t("synthetic"))}</p>
        <button class="btn ghost" type="button" data-action="sign-out" style="color:#cfe0e3;margin-top:8px">${icon("arrowRight")} ${esc(t("signOut"))}</button>
      </div>
    </aside>
    ${state.mobileNav ? '<div class="backdrop" data-action="toggle-mobile-nav"></div>' : ""}
    <div class="main">
      <header class="topbar">
        <button class="icon-btn" type="button" data-action="toggle-mobile-nav" aria-label="${esc(t("menu"))}">${icon("menu")}</button>
        <button class="icon-btn" type="button" data-action="toggle-sidebar" aria-label="${esc(t("collapse"))}" aria-expanded="${!state.sidebarCollapsed}">${icon("chevron")}</button>
        <div class="breadcrumb">BSR / <strong>${esc(t(ROUTE_TITLES[state.route] || "overview"))}</strong></div>
        <div class="asof"><span class="freshness-dot"></span>${esc(t("asOf"))} ${fmtTime(state.asOf)} · ${esc(state.freshness === "mixed" ? t("mixed") : state.freshness || "")}</div>
        <div class="topbar-actions">
          <button class="icon-btn" type="button" data-action="open-search" aria-label="${esc(t("search"))}">${icon("search")}</button>
          <button class="icon-btn" type="button" data-action="open-notifications" aria-label="${esc(t("notifications"))}">${icon("bell")}</button>
          <button class="btn ghost" type="button" data-action="toggle-language" aria-label="${esc(t("language"))}">${getLang().toUpperCase()}</button>
          <select class="role-select" data-action="switch-role" aria-label="${esc(t("role"))}">
            ${["leadership", "mi", "internal"]
              .map(
                (role) =>
                  `<option value="${role}" ${user && user.role === role ? "selected" : ""}>${esc(roleLabel(role))}</option>`,
              )
              .join("")}
          </select>
        </div>
      </header>
      ${tape}
      <main id="main-content" class="page">${content}</main>
    </div>
  </div>`;
}

/* ---------- Login ---------- */

function renderLogin() {
  const roles = [
    { role: "leadership", dept: "Executive Office", perms: ["Restricted data", "No export", "No admin"] },
    { role: "mi", dept: "Market Intelligence", perms: ["Restricted data", "Export", "Admin"] },
    { role: "internal", dept: "Commercial", perms: ["Internal data only", "No export", "No admin"] },
  ];
  return `<div class="login-wrap">
    <div class="login-card">
      <div class="brand"><span class="mark" aria-hidden="true">B</span><strong>BSR Market Intelligence</strong></div>
      <h1>${esc(t("chooseRole"))}</h1>
      <p class="lede">${esc(t("tagline"))}. ${esc(t("synthetic"))}</p>
      <div class="role-grid">
        ${roles
          .map(
            (entry) => `<button class="role-card" type="button" data-action="login" data-role="${entry.role}">
              <strong>${esc(roleLabel(entry.role))}</strong>
              <span class="dept">${esc(entry.dept)}</span>
              <ul>${entry.perms.map((perm) => `<li>${esc(perm)}</li>`).join("")}</ul>
            </button>`,
          )
          .join("")}
      </div>
      <p class="login-foot">${esc(t("synthetic"))}</p>
    </div>
  </div>`;
}

/* ---------- Charts ---------- */

function lineChart(series, events = []) {
  const values = series.flatMap((entry) => entry.points.map((point) => point.v)).filter((value) => value != null);
  if (!values.length) return `<div class="chart-empty">${esc(t("empty"))}</div>`;
  const width = 760;
  const height = 260;
  const pad = { left: 48, right: 16, top: 18, bottom: 30 };
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const innerW = width - pad.left - pad.right;
  const innerH = height - pad.top - pad.bottom;
  const xAt = (index, count) => pad.left + (count <= 1 ? 0 : (index / (count - 1)) * innerW);
  const yAt = (value) => pad.top + innerH - ((value - min) / span) * innerH;

  const grid = [0, 0.25, 0.5, 0.75, 1]
    .map((ratio) => {
      const y = pad.top + innerH * ratio;
      const value = max - span * ratio;
      return `<line class="grid-line" x1="${pad.left}" y1="${y}" x2="${width - pad.right}" y2="${y}"/>
        <text class="axis-text" x="${pad.left - 6}" y="${y + 3}" text-anchor="end">${fmtNum(value, 2)}</text>`;
    })
    .join("");

  const paths = series
    .map((entry, seriesIndex) => {
      let path = "";
      let started = false;
      entry.points.forEach((point, index) => {
        if (point.v == null) {
          started = false;
          return;
        }
        const command = started ? "L" : "M";
        path += `${command}${xAt(index, entry.points.length).toFixed(1)},${yAt(point.v).toFixed(1)} `;
        started = true;
      });
      return `<path class="series ${seriesIndex === 0 ? "primary" : "secondary"}" d="${path.trim()}"/>`;
    })
    .join("");

  const primary = series[0];
  const firstTime = new Date(primary.points[0].t).getTime();
  const lastTime = new Date(primary.points[primary.points.length - 1].t).getTime();
  const markers = events
    .map((event) => {
      const time = new Date(event.occurred_at).getTime();
      if (Number.isNaN(time) || time < firstTime || time > lastTime) return "";
      const ratio = (time - firstTime) / (lastTime - firstTime || 1);
      const cx = pad.left + ratio * innerW;
      return `<g role="button" tabindex="0" data-action="event-detail" data-id="${esc(event.id)}" aria-label="${esc(event.title)}">
        <title>${esc(event.title)} · ${fmtDate(event.occurred_at)}</title>
        <rect x="${cx - 7}" y="${pad.top}" width="14" height="${innerH}" fill="transparent"/>
        <polygon class="event-marker" points="${cx},${pad.top + 4} ${cx + 5},${pad.top + 9} ${cx},${pad.top + 14} ${cx - 5},${pad.top + 9}"/>
      </g>`;
    })
    .join("");

  const axis = `<text class="axis-text" x="${pad.left}" y="${height - 8}">${fmtDate(primary.points[0].t)}</text>
    <text class="axis-text" x="${width - pad.right}" y="${height - 8}" text-anchor="end">${fmtDate(primary.points[primary.points.length - 1].t)}</text>`;

  return `<svg class="chart" viewBox="0 0 ${width} ${height}" role="group" aria-label="${esc(
    series.map((entry) => entry.instrument.short_name).join(" vs "),
  )}">${grid}${paths}${markers}${axis}</svg>`;
}

function chartTable(series) {
  const primary = series[0];
  if (!primary) return "";
  return `<details class="table-toggle"><summary>${esc(t("table"))}</summary>
    <div class="table-wrap" style="margin-top:8px"><table>
      <thead><tr><th>${esc(t("time"))}</th>${series
        .map((entry) => `<th class="num">${esc(entry.instrument.short_name)} (${esc(entry.unit)})</th>`)
        .join("")}</tr></thead>
      <tbody>${primary.points
        .map(
          (point, index) => `<tr><td class="mono">${esc(point.t)}</td>${series
            .map((entry) => `<td class="num">${entry.points[index] && entry.points[index].v != null ? fmtNum(entry.points[index].v, 2) : "—"}</td>`)
            .join("")}</tr>`,
        )
        .join("")}</tbody>
    </table></div></details>`;
}

/* ---------- Overview ---------- */

function renderOverview() {
  const data = state.data || {};
  const cards = data.cards || [];
  const series = data.series || [];
  const briefing = data.briefing;
  return `
    <div class="page-head">
      <div><h1>${esc(t("overview"))}</h1><p>${esc(t("tagline"))}</p></div>
      <div class="head-actions">
        <button class="btn" type="button" data-action="quick-query">${icon("sparkle")} ${esc(t("quickQuery"))}</button>
        ${state.user.role === "mi" ? `<button class="btn primary" type="button" data-action="quick-input">${icon("plus")} ${esc(t("observations"))}</button>` : ""}
      </div>
    </div>
    ${data.restricted_hidden ? `<div class="notice" style="margin-bottom:16px">${icon("lock")} ${esc(t("restrictedHidden"))}</div>` : ""}
    <section class="section">
      <div class="grid cols-4">
        ${cards
          .slice(0, 8)
          .map(
            (card) => `<button class="card metric-card" type="button" data-action="open-instrument" data-id="${esc(card.instrument.id)}">
              <span class="label">${esc(card.instrument.short_name)} ${classificationTag(card.classification)}</span>
              <span class="metric-value">${fmtNum(card.value, card.instrument.decimals)} <span class="unit">${esc(card.instrument.unit)}</span></span>
              <span class="delta ${directionClass(card.change)}">${fmtSigned(card.change, card.instrument.decimals)} · ${fmtPct(card.change_pct)}</span>
              <span class="meta">${esc(card.source.name)} · market <span class="mono">${fmtTime(card.market_time)}</span></span>
              <span class="meta">ingested <span class="mono">${fmtTime(card.ingested_at)}</span></span>
              <span class="meta">${statusChip(card.data_status)} ${badge(card.quality_status, card.quality_status === "valid" ? "ok" : "warn")}</span>
            </button>`,
          )
          .join("")}
      </div>
    </section>
    <section class="section grid main-rail">
      <div class="card">
        <div class="section-head"><h2>Brent vs WTI</h2><span class="hint">${esc(t("range"))} ${esc(state.range)}</span></div>
        ${lineChart(series, data.events || [])}
        ${chartTable(series)}
      </div>
      <div class="card">
        <h3>${esc(t("keyDrivers"))}</h3>
        ${(data.drivers || [])
          .map(
            (driver) => `<div class="driver"><span class="strength">${driver.strength}</span><div><strong>${esc(driver.label)}</strong><div class="meta">${esc(driver.detail)}</div></div></div>`,
          )
          .join("")}
      </div>
    </section>
    <section class="section grid main-rail">
      <div class="card">
        <h3>${esc(t("highlights"))}</h3>
        ${(data.highlights || [])
          .map(
            (item) => `<div class="news-item"><h3>${esc(item.title)}</h3>
              <div class="row"><span class="meta">${esc(item.source.name)} · ${fmtTime(item.published_at)}</span>${badge(item.attribution, "ai")}</div></div>`,
          )
          .join("") || `<div class="empty">${esc(t("empty"))}</div>`}
      </div>
      <div class="card">
        <h3>${esc(t("briefing"))}</h3>
        ${
          briefing
            ? `<div class="ai-block"><span class="ai-label">${esc(t("aiInterpretation"))} · v${briefing.version}</span>
                <p style="margin-top:6px">${esc(briefing.headline)}</p>
                <div class="meta">${fmtTime(briefing.generated_at)} · ${esc(t("asOf"))} ${fmtTime(briefing.data_cutoff)}</div>
                <ul class="evidence" style="margin-top:8px">${(briefing.moves || [])
                  .map((move) => `<li><span class="kind">move</span>${esc(move.instrument)} ${fmtNum(move.value, 2)} ${esc(move.unit || "")}${move.change != null ? ` · <span class="${directionClass(move.change)}">${fmtSigned(move.change)} / ${fmtPct(move.pct)}</span>` : ""}</li>`)
                  .join("")}</ul>
              </div>`
            : `<div class="empty">${esc(t("empty"))}</div>`
        }
      </div>
    </section>`;
}

/* ---------- Market data ---------- */

function renderMarketData() {
  const data = state.data || {};
  const instruments = data.instruments || [];
  const series = data.series || [];
  const observations = data.observations || [];
  const formulas = data.formulas || [];
  const selected = instruments.find((item) => item.id === state.instrument) || instruments[0];
  const formula = selected && selected.formula_id ? formulas.find((item) => item.id === selected.formula_id) : null;

  return `
    <div class="page-head">
      <div><h1>${esc(t("marketData"))}</h1><p>${esc(t("tagline"))}</p></div>
      <div class="head-actions">
        <div class="range-tabs" role="group" aria-label="${esc(t("range"))}">
          ${["7D", "1M", "3M", "1Y"]
            .map(
              (range) =>
                `<button type="button" data-action="set-range" data-range="${range}" aria-pressed="${state.range === range}">${range}</button>`,
            )
            .join("")}
        </div>
        <select class="role-select" data-action="set-compare" aria-label="${esc(t("compare"))}">
          <option value="">${esc(t("compare"))}…</option>
          ${instruments
            .filter((item) => item.id !== state.instrument)
            .map(
              (item) =>
                `<option value="${esc(item.id)}" ${state.compare === item.id ? "selected" : ""}>${esc(item.short_name)}</option>`,
            )
            .join("")}
        </select>
      </div>
    </div>
    <div class="grid main-rail">
      <div>
        <div class="card section">
          <div class="section-head"><h2>${esc(selected ? selected.name : "")}</h2><span class="hint">${esc(selected ? selected.unit : "")}</span></div>
          ${lineChart(series, data.events || [])}
          ${chartTable(series)}
        </div>
        <div class="card section">
          <div class="section-head"><h2>${esc(t("observations"))}</h2><span class="hint">Δ vs prior observation</span></div>
          <div class="table-wrap"><table>
            <thead><tr><th>${esc(t("time"))}</th><th>Ingested</th><th class="num">${esc(t("value"))}</th><th class="num">Δ vs prior obs.</th><th>${esc(t("source"))}</th><th>${esc(t("status"))}</th></tr></thead>
            <tbody>${observations
              .map((row, index) => {
                const prior = observations[index + 1];
                const delta = prior ? row.value - prior.value : null;
                return `<tr><td class="mono">${fmtTime(row.market_time)}</td>
                  <td class="mono">${fmtTime(row.ingested_at)}</td>
                  <td class="num">${fmtNum(row.value, 2)} ${esc(row.unit)}</td>
                  <td class="num ${directionClass(delta)}">${fmtSigned(delta)}</td>
                  <td>${esc(row.source.name)}</td>
                  <td>${statusChip(row.data_status)} ${badge(row.quality_status, row.quality_status === "valid" ? "ok" : "warn")}</td></tr>`;
              })
              .join("")}</tbody>
          </table></div>
        </div>
      </div>
      <div>
        <div class="card section">
          <h3>${esc(t("allInstruments"))}</h3>
          <div class="instrument-rail">
            ${instruments
              .map(
                (item) => `<button class="instrument-btn ${item.id === state.instrument ? "active" : ""}" type="button" data-action="select-instrument" data-id="${esc(item.id)}">
                  <span>${esc(item.short_name)}<br><span class="meta">${esc(item.group)}</span></span>
                  <span class="val">${item.latest ? fmtNum(item.latest.value, item.decimals) : "—"}</span>
                </button>`,
              )
              .join("")}
          </div>
        </div>
        ${
          formula
            ? `<div class="card section"><h3>${esc(t("formula"))}</h3>
                <dl class="kv"><dt>ID</dt><dd class="mono">${esc(formula.id)}</dd>
                <dt>${esc(t("version"))}</dt><dd>${esc(formula.version)}</dd>
                <dt>Rule</dt><dd>${esc(formula.expression)}</dd>
                <dt>Inputs</dt><dd>${formula.inputs.map((input) => esc(input)).join(", ")}</dd>
                <dt>Mixed types</dt><dd>${formula.allow_mixed_price_types ? "allowed" : "rejected"}</dd></dl></div>`
            : ""
        }
        ${state.user.role === "mi" ? `<button class="btn primary" type="button" data-action="quick-input">${icon("plus")} ${esc(t("observations"))}</button>` : ""}
      </div>
    </div>`;
}

/* ---------- News ---------- */

function renderNews() {
  const items = (state.data && state.data.news) || [];
  const topics = [...new Set(items.flatMap((item) => item.topics))].sort();
  const sources = [...new Map(items.map((item) => [item.source.id, item.source.name])).entries()];
  return `
    <div class="page-head">
      <div><h1>${esc(t("news"))}</h1><p>${esc(t("tagline"))}</p></div>
      <div class="head-actions">
        ${state.user.role === "mi" ? `<button class="btn" type="button" data-action="news-intake">${icon("plus")} ${esc(t("intake"))}</button>
        <button class="btn" type="button" data-action="news-upload">${icon("upload")} ${esc(t("upload"))}</button>` : ""}
      </div>
    </div>
    <div class="card section">
      <div class="form-row">
        <div class="field"><label for="news-topic">${esc(t("allTopics"))}</label>
          <select id="news-topic" data-filter="topic"><option value="">${esc(t("allTopics"))}</option>${topics
            .map((topic) => `<option value="${esc(topic)}" ${state.newsFilters.topic === topic ? "selected" : ""}>${esc(topic)}</option>`)
            .join("")}</select></div>
        <div class="field"><label for="news-source">${esc(t("allSources"))}</label>
          <select id="news-source" data-filter="source"><option value="">${esc(t("allSources"))}</option>${sources
            .map(([id, name]) => `<option value="${esc(id)}" ${state.newsFilters.source === id ? "selected" : ""}>${esc(name)}</option>`)
            .join("")}</select></div>
        <div class="field"><label for="news-status">${esc(t("allStatuses"))}</label>
          <select id="news-status" data-filter="status"><option value="">${esc(t("allStatuses"))}</option>${["processed", "duplicate_candidate", "processing", "failed"]
            .map((status) => `<option value="${status}" ${state.newsFilters.status === status ? "selected" : ""}>${esc(status)}</option>`)
            .join("")}</select></div>
        <div class="field"><label for="news-query">${esc(t("search"))}</label>
          <input id="news-query" type="search" data-filter="q" value="${esc(state.newsFilters.q)}" placeholder="${esc(t("search"))}"></div>
      </div>
    </div>
    <div class="card">
      ${items
        .map(
          (item) => `<article class="news-item">
            <h3><button class="btn ghost" type="button" data-action="news-detail" data-id="${esc(item.id)}" style="padding:0;min-height:0;text-align:left">${esc(item.title)}</button></h3>
            <div class="row">
              <span class="meta">${esc(item.source.name)} · ${fmtTime(item.published_at)}</span>
              ${badge(item.processing_status, item.processing_status === "processed" ? "ok" : "warn")}
              ${classificationTag(item.classification)}
              ${item.duplicate_of ? `<span class="meta">↳ ${esc(item.duplicate_of)}</span>` : ""}
            </div>
            <div class="row" style="margin-top:6px">${item.topics.map((topic) => `<span class="chip">${esc(topic)}</span>`).join("")}</div>
          </article>`,
        )
        .join("") || `<div class="empty">${esc(t("empty"))}</div>`}
    </div>`;
}

/* ---------- Forecast ---------- */

function renderForecast() {
  const data = state.data || {};
  const forecasts = data.forecasts || [];
  const evaluation = data.evaluation || { items: [], aggregates: [] };
  const instruments = [...new Map(forecasts.map((item) => [item.instrument.id, item.instrument.name])).entries()];
  const horizons = [...new Set(forecasts.map((item) => item.horizon))];
  return `
    <div class="page-head"><div><h1>${esc(t("forecast"))}</h1><p>${esc(t("tagline"))}</p></div></div>
    <div class="card section">
      <div class="form-row">
        <div class="field"><label for="forecast-instrument">${esc(t("allInstruments"))}</label>
          <select id="forecast-instrument" data-filter="forecast-instrument"><option value="">${esc(t("allInstruments"))}</option>${instruments
            .map(([id, name]) => `<option value="${esc(id)}" ${state.forecastFilters.instrument === id ? "selected" : ""}>${esc(name)}</option>`)
            .join("")}</select></div>
        <div class="field"><label for="forecast-horizon">${esc(t("allHorizons"))}</label>
          <select id="forecast-horizon" data-filter="forecast-horizon"><option value="">${esc(t("allHorizons"))}</option>${horizons
            .map((horizon) => `<option value="${esc(horizon)}" ${state.forecastFilters.horizon === horizon ? "selected" : ""}>${esc(horizon)}</option>`)
            .join("")}</select></div>
      </div>
    </div>
    <div class="card section">
      <div class="table-wrap"><table>
        <thead><tr><th>${esc(t("source"))}</th><th>Instrument</th><th>${esc(t("version"))}</th><th class="num">${esc(t("value"))}</th><th class="num">Actual</th><th class="num">Abs. error</th><th>${esc(t("status"))}</th><th></th></tr></thead>
        <tbody>${forecasts
          .map(
            (item) => `<tr><td>${esc(item.source.name)}</td><td>${esc(item.instrument.name)}<br><span class="meta">${esc(item.horizon)} · ${esc(item.period)}</span></td>
              <td class="mono">v${item.version}</td><td class="num">${fmtNum(item.value, 2)}</td>
              <td class="num">${item.actual == null ? `<span class="meta">${esc(t("missingActual"))}</span>` : fmtNum(item.actual, 2)}</td>
              <td class="num">${item.absolute_error == null ? "—" : fmtNum(item.absolute_error, 2)}</td>
              <td>${item.note ? badge(item.note, "warn") : badge("evaluated", "ok")}</td>
              <td><button class="btn ghost" type="button" data-action="forecast-versions" data-id="${esc(item.id)}">${esc(t("history"))}</button></td></tr>`,
          )
          .join("")}</tbody>
      </table></div>
    </div>
    <div class="card">
      <h3>${esc(t("accuracy"))}</h3>
      <div class="table-wrap"><table>
        <thead><tr><th>${esc(t("source"))}</th><th>Horizon</th><th class="num">n</th><th class="num">MAE</th><th class="num">MAPE</th><th class="num">Bias</th><th class="num">${esc(t("missingActual"))}</th></tr></thead>
        <tbody>${evaluation.aggregates
          .map(
            (row) => `<tr><td>${esc(row.source)}</td><td>${esc(row.horizon)}</td><td class="num">${row.count}</td>
              <td class="num">${row.mae == null ? "—" : fmtNum(row.mae, 2)}</td><td class="num">${row.mape == null ? "—" : fmtNum(row.mape, 2)}</td>
              <td class="num">${row.bias == null ? "—" : fmtSigned(row.bias, 2)}</td><td class="num">${row.missing}</td></tr>`,
          )
          .join("")}</tbody>
      </table></div>
    </div>`;
}

/* ---------- Analysis ---------- */

function renderAnalysis() {
  const data = state.data || {};
  return `
    <div class="page-head"><div><h1>${esc(t("analysis"))}</h1><p>${esc(t("tagline"))}</p></div></div>
    <form class="card section" data-form="analysis">
      <div class="field"><label for="analysis-question">${esc(t("ask"))}</label>
        <input id="analysis-question" name="question" value="${esc(state.analysisQuestion)}" required></div>
      <button class="btn primary" type="submit">${icon("analysis")} ${esc(t("submit"))}</button>
    </form>
    ${
      data.facts
        ? `<div class="grid main-rail">
            <div>
              <div class="card section"><h3>${esc(t("facts"))}</h3><ul class="evidence">${data.facts
                .map((fact) => `<li><span class="kind">fact</span>${esc(fact)}</li>`)
                .join("")}</ul></div>
              <div class="card section"><h3>${esc(t("calculations"))}</h3><ul class="evidence">${data.calculations
                .map(
                  (item) => `<li><span class="kind">${esc(t("deterministic"))}</span>${esc(item.label)}: <strong class="mono">${fmtNum(item.value, 2)} ${esc(item.unit)}</strong><div class="meta">${esc(item.method)}</div></li>`,
                )
                .join("")}</ul></div>
              <div class="card section"><h3>${esc(t("assumptions"))}</h3><ul class="evidence">${data.assumptions
                .map((item) => `<li><span class="kind">assumption</span>${esc(item)}</li>`)
                .join("")}</ul></div>
            </div>
            <div>
              <div class="card section ai-block"><span class="ai-label">${esc(t("recommendation"))}</span>
                <p style="margin-top:6px">${esc(data.recommendation.title)}</p>
                <div class="meta">Confidence: ${esc(data.recommendation.confidence)}</div>
                <p class="meta" style="margin-top:6px">${esc(data.recommendation.rationale)}</p></div>
              <div class="card section"><h3>${esc(t("evidence"))}</h3><ul class="evidence">${(data.evidence || [])
                .map((item) => `<li><span class="kind">${esc(item.kind)}</span>${esc(item.label)} <span class="meta mono">#${esc(item.id)}</span></li>`)
                .join("")}</ul></div>
              <div class="card"><h3>${esc(t("executions"))}</h3><dl class="kv"><dt>Task</dt><dd class="mono">${esc(data.execution.task_id)}</dd><dt>${esc(t("status"))}</dt><dd>${esc(data.execution.status)}</dd><dt>Model</dt><dd>${esc(data.execution.model)}</dd></dl></div>
            </div>
          </div>`
        : `<div class="empty">${esc(t("empty"))}</div>`
    }`;
}

/* ---------- Assistant ---------- */

function renderAssistant() {
  const suggestions = [
    "What is the gasoline crack spread?",
    "What is driving Brent today?",
    "What is the 5-session return on Brent?",
    "What is the dated Brent physical price?",
  ];
  return `
    <div class="page-head"><div><h1>${esc(t("assistant"))}</h1><p>${esc(t("tagline"))}</p></div></div>
    <div class="grid main-rail">
      <div class="card">
        <div class="chat" id="chat-log">
          ${
            state.chat.length
              ? state.chat
                  .map(
                    (message) => `<div class="bubble ${message.role} ${message.role === "assistant" ? "ai" : ""}">
                      <div>${esc(message.text)}</div>
                      ${
                        message.citations && message.citations.length
                          ? `<ul class="citation-list">${message.citations
                              .map((citation) => `<li>${esc(citation.kind)} · ${esc(citation.label || citation.id)}</li>`)
                              .join("")}</ul>`
                          : ""
                      }
                      ${
                        message.calculations && message.calculations.length
                          ? `<ul class="evidence">${message.calculations
                              .map(
                                (item) => `<li><span class="kind">${esc(t("deterministic"))}</span>${esc(item.label)}: <strong class="mono">${fmtNum(item.value, 2)} ${esc(item.unit)}</strong></li>`,
                              )
                              .join("")}</ul>`
                          : ""
                      }
                      ${
                        message.toolTrace && message.toolTrace.length
                          ? `<details class="table-toggle"><summary>${esc(t("toolTrace"))}</summary><ul class="evidence">${message.toolTrace
                              .map((tool) => `<li>${esc(tool.tool)} · ${esc(tool.status)}</li>`)
                              .join("")}</ul></details>`
                          : ""
                      }
                      ${message.execution ? `<div class="meta mono">${esc(message.execution.task_id)} · ${esc(message.execution.status)} · ${message.execution.latency_ms} ms</div>` : ""}
                    </div>`,
                  )
                  .join("")
              : `<div class="empty">${esc(t("suggestions"))}</div>`
          }
          ${state.chatBusy ? `<div class="bubble assistant">${esc(t("loading"))}</div>` : ""}
        </div>
        <form class="composer" data-form="assistant">
          <textarea name="question" aria-label="${esc(t("ask"))}" placeholder="${esc(t("ask"))}" required></textarea>
          <button class="btn primary" type="submit" ${state.chatBusy ? "disabled" : ""}>${icon("sparkle")} ${esc(t("send"))}</button>
        </form>
      </div>
      <div class="card">
        <h3>${esc(t("suggestions"))}</h3>
        ${suggestions
          .map(
            (question) => `<button class="btn ghost" type="button" data-action="suggestion" data-question="${esc(question)}" style="display:block;text-align:left;width:100%;margin-bottom:6px">${esc(question)}</button>`,
          )
          .join("")}
      </div>
    </div>`;
}

/* ---------- Reports ---------- */

function renderReports() {
  const reports = (state.data && state.data.reports) || [];
  return `
    <div class="page-head"><div><h1>${esc(t("reports"))}</h1><p>${esc(t("tagline"))}</p></div></div>
    <div class="grid main-rail">
      <div class="card">
        <h3>${esc(t("reports"))}</h3>
        <div class="table-wrap"><table>
          <thead><tr><th>${esc(t("type"))}</th><th>${esc(t("version"))}</th><th>${esc(t("classification"))}</th><th>${esc(t("time"))}</th><th></th></tr></thead>
          <tbody>${reports
            .map(
              (report) => `<tr><td>${esc(report.title)}<br><span class="meta">${esc(report.range_start)} → ${esc(report.range_end)}</span></td>
                <td class="mono">v${report.version}</td><td>${classificationTag(report.classification)}</td><td class="mono">${fmtTime(report.created_at)}</td>
                <td><button class="btn ghost" type="button" data-action="report-preview" data-id="${esc(report.id)}">${esc(t("preview"))}</button></td></tr>`,
            )
            .join("")}</tbody>
        </table></div>
      </div>
      <div class="card">
        <h3>${esc(t("generate"))}</h3>
        <form data-form="report">
          <div class="field"><label for="report-type">${esc(t("type"))}</label>
            <select id="report-type" name="type">
              <option>On-demand Market Analysis</option>
              <option>Morning Briefing</option>
              <option>Weekly Market Report</option>
            </select></div>
          <div class="form-row">
            <div class="field"><label for="report-start">From</label><input id="report-start" name="range_start" type="date" value="2026-11-01" required></div>
            <div class="field"><label for="report-end">To</label><input id="report-end" name="range_end" type="date" value="2026-11-14" required></div>
          </div>
          <button class="btn primary" type="submit">${icon("reports")} ${esc(t("generate"))}</button>
        </form>
        <p class="meta" style="margin-top:10px">${state.user.can_export ? "PDF export is available for your role." : "PDF export is not available for your role; the attempt is audited."}</p>
      </div>
    </div>`;
}

/* ---------- Admin ---------- */

function renderAdmin() {
  if (!state.user.is_admin) {
    return `<div class="page-head"><div><h1>${esc(t("admin"))}</h1></div></div>
      <div class="empty">${icon("lock")} ${esc(t("denied"))}</div>`;
  }
  const data = state.data || {};
  const tabs = ["users", "sources", "executions", "audit"];
  let body = "";
  if (state.adminTab === "users") {
    const fieldLabels = {
      can_view_restricted: t("viewRestricted"),
      can_export: t("export"),
      is_admin: t("adminRights"),
    };
    body = `<div class="table-wrap"><table>
      <thead><tr><th>${esc(t("users"))}</th><th>${esc(t("role"))}</th><th>${esc(t("classification"))}</th><th>${esc(t("viewRestricted"))}</th><th>${esc(t("export"))}</th><th>${esc(t("adminRights"))}</th></tr></thead>
      <tbody>${(data.users || [])
        .map(
          (user) => `<tr><td>${esc(user.name)}<br><span class="meta">${esc(user.department)}</span></td><td>${esc(roleLabel(user.role))}</td>
            <td>${classificationTag(user.max_classification)}</td>
            ${["can_view_restricted", "can_export", "is_admin"]
              .map(
                (field) => `<td><button class="btn ghost" type="button" data-action="toggle-permission" data-user="${esc(user.id)}" data-field="${field}" aria-pressed="${user[field]}" aria-label="${esc(`${fieldLabels[field]} — ${user.name}: ${user[field] ? "granted" : "denied"}`)}">${user[field] ? icon("check") : "—"}</button></td>`,
              )
              .join("")}</tr>`,
        )
        .join("")}</tbody>
    </table></div>`;
  } else if (state.adminTab === "sources") {
    body = `<div class="table-wrap"><table>
      <thead><tr><th>ID</th><th>${esc(t("source"))}</th><th>Kind</th><th>${esc(t("classification"))}</th><th>Licence</th></tr></thead>
      <tbody>${(data.sources || [])
        .map(
          (source) => `<tr><td class="mono">${esc(source.id)}</td><td>${esc(source.name)}</td><td>${esc(source.kind)}</td><td>${classificationTag(source.classification)}</td><td class="meta">${esc(source.licence_note || "")}</td></tr>`,
        )
        .join("")}</tbody>
    </table></div>`;
  } else if (state.adminTab === "executions") {
    body = `<div class="table-wrap"><table>
      <thead><tr><th>Task</th><th>${esc(t("type"))}</th><th>Model</th><th class="num">Latency</th><th class="num">Cost</th><th>${esc(t("status"))}</th><th>Validation</th></tr></thead>
      <tbody>${(data.executions || [])
        .map(
          (row) => `<tr><td class="mono">${esc(row.task_id)}</td><td>${esc(row.task_type)}</td><td>${esc(row.model)}</td>
            <td class="num">${row.latency_ms} ms</td><td class="num">$${fmtNum(row.cost_usd, 3)}</td>
            <td>${badge(row.status, row.status === "succeeded" ? "ok" : "warn")}</td><td>${esc(row.validation)}</td></tr>`,
        )
        .join("")}</tbody>
    </table></div>`;
  } else {
    body = `<div class="table-wrap"><table>
      <thead><tr><th>${esc(t("time"))}</th><th>Actor</th><th>Action</th><th>Object</th><th>Result</th><th>${esc(t("classification"))}</th></tr></thead>
      <tbody>${(data.audit || [])
        .map(
          (row) => `<tr><td class="mono">${fmtTime(row.created_at)}</td><td>${esc(row.actor_id || "system")}<br><span class="meta">${esc(row.actor_role || "")}</span></td>
            <td>${esc(row.action)}</td><td class="mono">${esc(row.object_id || "")}</td><td>${esc(row.result)}</td><td>${row.classification ? classificationTag(row.classification) : "—"}</td></tr>`,
        )
        .join("")}</tbody>
    </table></div>`;
  }
  return `
    <div class="page-head"><div><h1>${esc(t("admin"))}</h1><p>${esc(t("tagline"))}</p></div></div>
    <div class="tabs" role="tablist">
      ${tabs
        .map(
          (tab) => `<button type="button" role="tab" data-action="admin-tab" data-tab="${tab}" aria-selected="${state.adminTab === tab}">${esc(t(tab === "executions" ? "executions" : tab))}</button>`,
        )
        .join("")}
    </div>
    <div class="card">${body}</div>`;
}

/* ---------- Route rendering ---------- */

function renderContent() {
  if (state.loading) return `<div class="empty">${esc(t("loading"))}</div>`;
  if (state.error) {
    return `<div class="error-box">${esc(t("error"))}: ${esc(state.error.message)} <button class="btn ghost" type="button" data-action="retry">${esc(t("retry"))}</button></div>`;
  }
  switch (state.route) {
    case "overview":
      return renderOverview();
    case "market-data":
      return renderMarketData();
    case "news":
      return renderNews();
    case "forecast":
      return renderForecast();
    case "analysis":
      return renderAnalysis();
    case "assistant":
      return renderAssistant();
    case "reports":
      return renderReports();
    case "admin":
      return renderAdmin();
    default:
      return `<div class="empty">${esc(t("empty"))}</div>`;
  }
}

function render() {
  const app = $("#app");
  if (!app) return;
  if (state.route === "login" || !state.user) {
    app.innerHTML = renderLogin();
    return;
  }
  app.innerHTML = renderShell(renderContent());
}

/* ---------- Data loading ---------- */

async function fetchRoute(route) {
  if (route === "overview") {
    const [overview, series] = await Promise.all([
      api("/api/overview"),
      api(`/api/instruments/brent_futures/series?range=${state.range}&compare=wti_futures`),
    ]);
    state.tape = overview.tape || [];
    state.asOf = overview.as_of;
    state.freshness = overview.freshness;
    return { ...overview, series: series.series, events: series.events };
  }
  if (route === "market-data") {
    const instrumentsResponse = await api("/api/instruments");
    const instruments = instrumentsResponse.instruments;
    if (!instruments.some((item) => item.id === state.instrument)) {
      state.instrument = instruments.length ? instruments[0].id : "";
    }
    if (state.compare && !instruments.some((item) => item.id === state.compare)) {
      state.compare = "";
    }
    const compare = state.compare ? `&compare=${encodeURIComponent(state.compare)}` : "";
    const [series, observations, formulas] = await Promise.all([
      api(`/api/instruments/${encodeURIComponent(state.instrument)}/series?range=${state.range}${compare}`),
      api(`/api/observations?instrument=${encodeURIComponent(state.instrument)}&limit=30`),
      api("/api/formulas"),
    ]);
    return {
      instruments,
      series: series.series,
      events: series.events,
      observations: observations.observations,
      formulas: formulas.formulas,
    };
  }
  if (route === "news") {
    const params = new URLSearchParams();
    Object.entries(state.newsFilters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    return api(`/api/news?${params.toString()}`);
  }
  if (route === "forecast") {
    const params = new URLSearchParams();
    if (state.forecastFilters.instrument) params.set("instrument", state.forecastFilters.instrument);
    if (state.forecastFilters.horizon) params.set("horizon", state.forecastFilters.horizon);
    const [forecasts, evaluation] = await Promise.all([
      api(`/api/forecasts?${params.toString()}`),
      api(`/api/forecasts/evaluation?${params.toString()}`),
    ]);
    return { forecasts: forecasts.forecasts, evaluation };
  }
  if (route === "analysis") {
    return api(`/api/analysis?question=${encodeURIComponent(state.analysisQuestion)}`);
  }
  if (route === "reports") {
    return api("/api/reports");
  }
  if (route === "admin") {
    if (!state.user.is_admin) return {};
    const [users, sources, audit, executions] = await Promise.all([
      api("/api/admin/users"),
      api("/api/admin/sources"),
      api("/api/admin/audit?limit=50"),
      api("/api/admin/ai-executions"),
    ]);
    return {
      users: users.users,
      sources: sources.sources,
      audit: audit.audit,
      executions: executions.executions,
    };
  }
  return {};
}

async function loadRoute() {
  if (state.route === "login") {
    render();
    return;
  }
  if (!state.user) {
    try {
      const me = await api("/api/me");
      state.user = me.user;
      setCsrf(me.csrf_token);
    } catch (error) {
      state.route = "login";
      location.hash = "#login";
      render();
      return;
    }
  }
  state.loading = true;
  state.error = null;
  render();
  try {
    state.data = await fetchRoute(state.route);
  } catch (error) {
    if (error.status === 401) {
      state.user = null;
      state.route = "login";
      location.hash = "#login";
      render();
      return;
    }
    state.error = error;
  } finally {
    state.loading = false;
    render();
  }
}

/* ---------- Actions ---------- */

async function signIn(role) {
  try {
    const session = await api("/api/auth/session", { method: "POST", body: { role } });
    state.user = session.user;
    setCsrf(session.csrf_token);
    state.chat = [];
    state.data = null;
    state.tape = [];
    state.asOf = null;
    state.freshness = null;
    state.instrument = "brent_futures";
    state.compare = "";
    state.newsFilters = { topic: "", source: "", status: "", q: "" };
    state.forecastFilters = { instrument: "", horizon: "" };
    state.adminTab = "users";
    if (location.hash === "#overview") {
      state.route = "overview";
      await loadRoute();
    } else {
      location.hash = "#overview";
    }
  } catch (error) {
    toast(error.message, "error");
  }
}

async function signOut() {
  try {
    await api("/api/auth/session", { method: "DELETE" });
  } catch (error) {
    // A failed sign-out still clears the local view.
  }
  state.user = null;
  state.data = null;
  state.tape = [];
  setCsrf(null);
  location.hash = "#login";
}

async function switchRole(role) {
  await signIn(role);
}

function openQuickInput() {
  const instruments =
    (state.data && state.data.instruments) ||
    ((state.data && state.data.cards) || []).map((card) => card.instrument);
  const options = instruments
    .map((item) => `<option value="${esc(item.id)}" ${item.id === state.instrument ? "selected" : ""}>${esc(item.name)} (${esc(item.unit)})</option>`)
    .join("");
  openModal(
    t("observations"),
    `<form data-form="quick-input">
      <div class="field"><label for="qi-instrument">Instrument</label><select id="qi-instrument" name="instrument_id">${options}</select></div>
      <div class="form-row">
        <div class="field"><label for="qi-value">${esc(t("value"))}</label><input id="qi-value" name="value" type="number" step="0.01" required></div>
        <div class="field"><label for="qi-time">${esc(t("time"))}</label><input id="qi-time" name="market_time" type="datetime-local" value="2026-11-14T08:00" required></div>
      </div>
      <div class="form-row">
        <div class="field"><label for="qi-source">${esc(t("source"))}</label>
          <select id="qi-source" name="source_id"><option value="SRC-ICE">ICE (demo)</option><option value="SRC-CME">CME (demo)</option><option value="SRC-PLATTS">Platts (demo)</option><option value="SRC-SBV">SBV (demo)</option></select></div>
        <div class="field"><label for="qi-status">${esc(t("status"))}</label>
          <select id="qi-status" name="data_status"><option value="real-time">real-time</option><option value="delayed">delayed</option><option value="eod">eod</option><option value="manual">manual</option></select></div>
      </div>
      <div class="field"><label for="qi-classification">${esc(t("classification"))}</label>
        <select id="qi-classification" name="classification"><option value="internal">internal</option><option value="public">public</option><option value="confidential">confidential</option><option value="restricted">restricted</option></select></div>
      <p class="meta">${esc(t("synthetic"))}</p>
    </form>`,
    `<button class="btn" type="button" data-action="close-overlays">${esc(t("close"))}</button>
     <button class="btn primary" type="submit" form="quick-input-form">${esc(t("submit"))}</button>`,
  );
  const form = $("#modal form");
  if (form) form.id = "quick-input-form";
}

async function submitQuickInput(form) {
  const data = new FormData(form);
  const instrument = ((state.data && state.data.instruments) || []).find((item) => item.id === data.get("instrument_id"));
  const marketTime = data.get("market_time");
  const payload = {
    instrument_id: data.get("instrument_id"),
    value: Number(data.get("value")),
    unit: instrument ? instrument.unit : undefined,
    market_time: marketTime ? `${marketTime}:00+07:00` : undefined,
    source_id: data.get("source_id"),
    data_status: data.get("data_status"),
    quality_status: "valid",
    classification: data.get("classification"),
  };
  try {
    await api("/api/observations", { method: "POST", body: payload });
    closeOverlays();
    toast(t("saved"));
    await loadRoute();
  } catch (error) {
    toast(error.message, "error");
  }
}

function openQuickQuery() {
  openModal(
    t("quickQuery"),
    `<form data-form="quick-query">
      <div class="field"><label for="qq-question">${esc(t("ask"))}</label>
        <input id="qq-question" name="question" value="What is the gasoline crack spread?" required></div>
    </form>`,
    `<button class="btn" type="button" data-action="close-overlays">${esc(t("close"))}</button>
     <button class="btn primary" type="submit" form="quick-query-form">${esc(t("send"))}</button>`,
  );
  const form = $("#modal form");
  if (form) form.id = "quick-query-form";
}

async function askAssistant(question) {
  state.chat.push({ role: "user", text: question });
  state.chatBusy = true;
  render();
  try {
    const response = await api("/api/assistant/query", { method: "POST", body: { question } });
    state.chat.push({
      role: "assistant",
      text: response.answer,
      citations: response.citations,
      calculations: response.calculations,
      toolTrace: response.tool_trace,
      execution: response.execution,
    });
  } catch (error) {
    state.chat.push({ role: "assistant", text: `${t("error")}: ${error.message}` });
  } finally {
    state.chatBusy = false;
    render();
  }
}

async function openNewsDetail(id) {
  try {
    const item = await api(`/api/news/${encodeURIComponent(id)}`);
    openDrawer(
      item.title,
      `<div class="row" style="margin-bottom:10px">${badge(item.processing_status, item.processing_status === "processed" ? "ok" : "warn")} ${classificationTag(item.classification)}</div>
       <dl class="kv"><dt>${esc(t("source"))}</dt><dd>${esc(item.source.name)}</dd>
       <dt>Published</dt><dd class="mono">${fmtTime(item.published_at)}</dd>
       <dt>Ingested</dt><dd class="mono">${fmtTime(item.ingested_at)}</dd>
       <dt>Topics</dt><dd>${item.topics.map((topic) => esc(topic)).join(", ")}</dd>
       ${item.duplicate_of ? `<dt>Duplicate of</dt><dd class="mono">${esc(item.duplicate_of)}</dd>` : ""}</dl>
       <h3 style="margin-top:16px">Original</h3><p>${esc(item.body)}</p>
       <h3 style="margin-top:12px">AI summary</h3><div class="ai-block"><span class="ai-label">${esc(t("aiInterpretation"))}</span><p>${esc(item.summary || "")}</p></div>
       <h3 style="margin-top:12px">AI insight</h3><div class="ai-block"><span class="ai-label">${esc(t("aiInterpretation"))}</span><p>${esc(item.insight || "")}</p></div>
       <h3 style="margin-top:12px">Feedback</h3><ul class="evidence">${(item.feedback || [])
         .map((entry) => `<li><span class="kind">${esc(entry.kind)}</span>${esc(entry.body || "")}</li>`)
         .join("") || `<li class="meta">${esc(t("empty"))}</li>`}</ul>`,
      `<button class="btn" type="button" data-action="feedback-important" data-id="${esc(item.id)}">${esc(t("important"))}</button>
       <button class="btn" type="button" data-action="feedback-comment" data-id="${esc(item.id)}">${esc(t("addComment"))}</button>`,
    );
  } catch (error) {
    toast(error.message, "error");
  }
}

function openNewsIntake() {
  openModal(
    t("intake"),
    `<form data-form="news-intake">
      <div class="field"><label for="ni-title">Title</label><input id="ni-title" name="title" required></div>
      <div class="field"><label for="ni-body">Body</label><textarea id="ni-body" name="body" required></textarea></div>
      <div class="form-row">
        <div class="field"><label for="ni-source">${esc(t("source"))}</label>
          <select id="ni-source" name="source_id"><option value="SRC-REUTERS">Reuters (demo)</option><option value="SRC-PLATTS">Platts (demo)</option><option value="SRC-EIA">EIA (demo)</option><option value="SRC-BLOOMBERG">Bloomberg (demo)</option></select></div>
        <div class="field"><label for="ni-published">Published</label><input id="ni-published" name="published_at" type="datetime-local" value="2026-11-14T09:00" required></div>
      </div>
      <div class="field"><label for="ni-classification">${esc(t("classification"))}</label>
        <select id="ni-classification" name="classification"><option value="internal">internal</option><option value="public">public</option><option value="confidential">confidential</option></select></div>
    </form>`,
    `<button class="btn" type="button" data-action="close-overlays">${esc(t("close"))}</button>
     <button class="btn primary" type="submit" form="news-intake-form">${esc(t("submit"))}</button>`,
  );
  const form = $("#modal form");
  if (form) form.id = "news-intake-form";
}

function openNewsUpload() {
  openModal(
    t("upload"),
    `<form data-form="news-upload">
      <div class="field"><label for="nu-file">File (CSV, XLSX, PDF, DOC, DOCX · max 5 MB)</label><input id="nu-file" name="file" type="file" accept=".csv,.xlsx,.pdf,.doc,.docx" required></div>
      <div class="field"><label for="nu-title">Title (optional)</label><input id="nu-title" name="title"></div>
      <div class="form-row">
        <div class="field"><label for="nu-source">${esc(t("source"))}</label>
          <select id="nu-source" name="source_id"><option value="SRC-REUTERS">Reuters (demo)</option><option value="SRC-PLATTS">Platts (demo)</option><option value="SRC-EIA">EIA (demo)</option></select></div>
        <div class="field"><label for="nu-published">Published</label><input id="nu-published" name="published_at" type="datetime-local" value="2026-11-14T09:00" required></div>
      </div>
      <div class="field"><label for="nu-classification">${esc(t("classification"))}</label>
        <select id="nu-classification" name="classification"><option value="internal">internal</option><option value="public">public</option><option value="confidential">confidential</option></select></div>
      <p class="meta">Unsupported or oversized files are rejected before anything is stored.</p>
    </form>`,
    `<button class="btn" type="button" data-action="close-overlays">${esc(t("close"))}</button>
     <button class="btn primary" type="submit" form="news-upload-form">${esc(t("upload"))}</button>`,
  );
  const form = $("#modal form");
  if (form) form.id = "news-upload-form";
}

async function openForecastVersions(id) {
  try {
    const data = await api(`/api/forecasts/${encodeURIComponent(id)}/versions`);
    openDrawer(
      `${t("history")} · ${id}`,
      `<div class="table-wrap"><table>
        <thead><tr><th>${esc(t("version"))}</th><th class="num">${esc(t("value"))}</th><th class="num">Actual</th><th class="num">Abs. error</th><th>Method</th></tr></thead>
        <tbody>${data.versions
          .map(
            (row) => `<tr><td class="mono">v${row.version}</td><td class="num">${fmtNum(row.value, 2)}</td>
              <td class="num">${row.actual == null ? `<span class="meta">${esc(t("missingActual"))}</span>` : fmtNum(row.actual, 2)}</td>
              <td class="num">${row.absolute_error == null ? "—" : fmtNum(row.absolute_error, 2)}</td><td>${esc(row.methodology)}</td></tr>`,
          )
          .join("")}</tbody>
      </table></div>`,
    );
  } catch (error) {
    toast(error.message, "error");
  }
}

async function openReportPreview(id) {
  try {
    const report = await api(`/api/reports/${encodeURIComponent(id)}`);
    const latest = report.versions[0];
    openDrawer(
      report.title,
      `<div class="row" style="margin-bottom:10px">${classificationTag(report.classification)} ${badge(`v${latest.version}`, "ok")}</div>
       <dl class="kv"><dt>${esc(t("type"))}</dt><dd>${esc(report.type)}</dd>
       <dt>Range</dt><dd>${esc(report.range_start)} → ${esc(report.range_end)}</dd>
       <dt>Data cut-off</dt><dd class="mono">${fmtTime(latest.data_cutoff)}</dd></dl>
       <h3 style="margin-top:14px">${esc(latest.content.summary || "")}</h3>
       ${(latest.content.sections || [])
         .map(
           (section) => `<h3 style="margin-top:12px">${esc(section.heading)}</h3><p>${esc(section.body)}</p>
             <ul class="evidence">${(section.items || [])
               .map((item) => `<li>${esc(item.title || `${item.instrument_id}: ${item.value} ${item.unit}`)}</li>`)
               .join("")}</ul>`,
         )
         .join("")}
       <h3 style="margin-top:12px">${esc(t("sources"))}</h3>
       <ul class="evidence">${(latest.sources || [])
         .map((source) => `<li><span class="kind">${esc(source.kind)}</span>${esc(source.label)}</li>`)
         .join("")}</ul>`,
      `<button class="btn" type="button" data-action="close-overlays">${esc(t("close"))}</button>
       <button class="btn primary" type="button" data-action="report-export" data-id="${esc(report.id)}" ${state.user.can_export ? "" : "disabled title=\"Export permission required\""}>${icon("download")} ${esc(t("exportPdf"))}</button>`,
    );
  } catch (error) {
    toast(error.message, "error");
  }
}

async function exportReport(id) {
  try {
    const blob = await apiBlob(`/api/reports/${encodeURIComponent(id)}/export.pdf`);
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${id}.pdf`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
    toast(t("saved"));
  } catch (error) {
    toast(error.message, "error");
  }
}

async function openSearch() {
  openModal(
    t("search"),
    `<form data-form="search">
      <div class="field"><label for="search-input">${esc(t("search"))}</label><input id="search-input" name="q" type="search" required></div>
    </form>
    <div id="search-results"></div>`,
  );
  const form = $("#modal form");
  if (form) form.id = "search-form";
}

async function runSearch(form) {
  const query = new FormData(form).get("q");
  const results = $("#search-results");
  if (!results) return;
  try {
    const data = await api(`/api/search?q=${encodeURIComponent(query)}`);
    results.innerHTML = `
      <h3>Instruments</h3><ul class="evidence">${data.instruments.map((item) => `<li>${esc(item.name)}</li>`).join("") || `<li class="meta">${esc(t("empty"))}</li>`}</ul>
      <h3>News</h3><ul class="evidence">${data.news.map((item) => `<li>${esc(item.title)}</li>`).join("") || `<li class="meta">${esc(t("empty"))}</li>`}</ul>
      <h3>Reports</h3><ul class="evidence">${data.reports.map((item) => `<li>${esc(item.title)}</li>`).join("") || `<li class="meta">${esc(t("empty"))}</li>`}</ul>`;
  } catch (error) {
    results.innerHTML = `<div class="error-box">${esc(error.message)}</div>`;
  }
}

async function openNotifications() {
  try {
    const data = await api("/api/notifications");
    openDrawer(
      t("notifications"),
      `<ul class="evidence">${data.notifications
        .map(
          (item) => `<li><strong>${esc(item.title)}</strong><div class="meta">${esc(item.body)}</div>
            <div class="row" style="margin-top:4px"><span class="meta mono">${fmtTime(item.created_at)}</span>
            ${item.read_at ? badge("read", "ok") : `<button class="btn ghost" type="button" data-action="mark-notification" data-id="${item.id}">${esc(t("saved"))}</button>`}</div></li>`,
        )
        .join("") || `<li class="meta">${esc(t("empty"))}</li>`}</ul>`,
    );
  } catch (error) {
    toast(error.message, "error");
  }
}

async function markNotification(id) {
  try {
    await api(`/api/notifications/${id}/read`, { method: "POST" });
    await openNotifications();
  } catch (error) {
    toast(error.message, "error");
  }
}

async function togglePermission(userId, field) {
  const user = ((state.data && state.data.users) || []).find((entry) => entry.id === userId);
  if (!user) return;
  try {
    await api(`/api/admin/users/${encodeURIComponent(userId)}`, {
      method: "PATCH",
      body: { [field]: !user[field] },
    });
    toast(t("saved"));
    await loadRoute();
  } catch (error) {
    toast(error.message, "error");
  }
}

/* ---------- Event wiring ---------- */

document.addEventListener("click", async (event) => {
  const target = event.target.closest("[data-action]");
  if (!target) return;
  const action = target.dataset.action;
  if (action === "login") {
    await signIn(target.dataset.role);
  } else if (action === "sign-out") {
    await signOut();
  } else if (action === "toggle-sidebar") {
    state.sidebarCollapsed = !state.sidebarCollapsed;
    render();
  } else if (action === "toggle-mobile-nav") {
    state.mobileNav = !state.mobileNav;
    render();
  } else if (action === "toggle-language") {
    setLang(getLang() === "vi" ? "en" : "vi");
  } else if (action === "close-overlays") {
    closeOverlays();
  } else if (action === "retry") {
    await loadRoute();
  } else if (action === "open-instrument") {
    state.instrument = target.dataset.id;
    state.compare = "";
    location.hash = "#market-data";
  } else if (action === "select-instrument") {
    state.instrument = target.dataset.id;
    state.compare = "";
    await loadRoute();
  } else if (action === "set-range") {
    state.range = target.dataset.range;
    await loadRoute();
  } else if (action === "quick-input") {
    openQuickInput();
  } else if (action === "quick-query") {
    openQuickQuery();
  } else if (action === "news-detail") {
    await openNewsDetail(target.dataset.id);
  } else if (action === "news-intake") {
    openNewsIntake();
  } else if (action === "news-upload") {
    openNewsUpload();
  } else if (action === "feedback-important") {
    try {
      await api(`/api/news/${encodeURIComponent(target.dataset.id)}/feedback`, {
        method: "POST",
        body: { kind: "important" },
      });
      toast(t("saved"));
    } catch (error) {
      toast(error.message, "error");
    }
  } else if (action === "feedback-comment") {
    openModal(
      t("addComment"),
      `<form data-form="feedback-comment"><div class="field"><label for="fc-body">Comment</label><textarea id="fc-body" name="body" required></textarea></div></form>`,
      `<button class="btn" type="button" data-action="close-overlays">${esc(t("close"))}</button>
       <button class="btn primary" type="submit" form="feedback-comment-form">${esc(t("submit"))}</button>`,
    );
    const form = $("#modal form");
    if (form) {
      form.id = "feedback-comment-form";
      form.dataset.newsId = target.dataset.id;
    }
  } else if (action === "forecast-versions") {
    await openForecastVersions(target.dataset.id);
  } else if (action === "suggestion") {
    await askAssistant(target.dataset.question);
  } else if (action === "report-preview") {
    await openReportPreview(target.dataset.id);
  } else if (action === "report-export") {
    await exportReport(target.dataset.id);
  } else if (action === "admin-tab") {
    state.adminTab = target.dataset.tab;
    render();
  } else if (action === "toggle-permission") {
    await togglePermission(target.dataset.user, target.dataset.field);
  } else if (action === "open-search") {
    await openSearch();
  } else if (action === "open-notifications") {
    await openNotifications();
  } else if (action === "mark-notification") {
    await markNotification(target.dataset.id);
  } else if (action === "event-detail") {
    const event = ((state.data && state.data.events) || []).find((item) => item.id === target.dataset.id);
    if (event) {
      openDrawer(
        event.title,
        `<dl class="kv"><dt>Type</dt><dd>${esc(event.type)}</dd><dt>Occurred</dt><dd class="mono">${fmtTime(event.occurred_at)}</dd>
         <dt>${esc(t("source"))}</dt><dd>${esc((event.source && event.source.name) || "—")}</dd>
         <dt>Instruments</dt><dd>${(event.instruments || []).map((item) => esc(item)).join(", ") || "—"}</dd>
         <dt>${esc(t("status"))}</dt><dd>${esc(event.status)}</dd><dt>${esc(t("classification"))}</dt><dd>${classificationTag(event.classification)}</dd></dl>`,
      );
    }
  }
});

document.addEventListener("change", async (event) => {
  const target = event.target;
  if (target.matches('[data-action="switch-role"]')) {
    await switchRole(target.value);
  } else if (target.matches('[data-action="set-compare"]')) {
    state.compare = target.value;
    await loadRoute();
  } else if (target.matches('[data-filter="topic"]')) {
    state.newsFilters.topic = target.value;
    await loadRoute();
  } else if (target.matches('[data-filter="source"]')) {
    state.newsFilters.source = target.value;
    await loadRoute();
  } else if (target.matches('[data-filter="status"]')) {
    state.newsFilters.status = target.value;
    await loadRoute();
  } else if (target.matches('[data-filter="forecast-instrument"]')) {
    state.forecastFilters.instrument = target.value;
    await loadRoute();
  } else if (target.matches('[data-filter="forecast-horizon"]')) {
    state.forecastFilters.horizon = target.value;
    await loadRoute();
  }
});

let searchTimer = null;
document.addEventListener("input", (event) => {
  const target = event.target;
  if (target.matches('[data-filter="q"]')) {
    state.newsFilters.q = target.value;
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => loadRoute(), 300);
  }
});

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("form[data-form]");
  if (!form) return;
  event.preventDefault();
  const kind = form.dataset.form;
  if (kind === "quick-input") {
    await submitQuickInput(form);
  } else if (kind === "quick-query") {
    const question = new FormData(form).get("question");
    closeOverlays();
    location.hash = "#assistant";
    await askAssistant(question);
  } else if (kind === "assistant") {
    const question = new FormData(form).get("question");
    if (question) await askAssistant(question);
  } else if (kind === "analysis") {
    state.analysisQuestion = new FormData(form).get("question");
    await loadRoute();
  } else if (kind === "news-intake") {
    const data = new FormData(form);
    const published = data.get("published_at");
    try {
      await api("/api/news", {
        method: "POST",
        body: {
          title: data.get("title"),
          body: data.get("body"),
          source_id: data.get("source_id"),
          published_at: published ? `${published}:00+07:00` : undefined,
          classification: data.get("classification"),
        },
      });
      closeOverlays();
      toast(t("saved"));
      await loadRoute();
    } catch (error) {
      toast(error.message, "error");
    }
  } else if (kind === "news-upload") {
    const data = new FormData(form);
    const published = data.get("published_at");
    if (published) data.set("published_at", `${published}:00+07:00`);
    try {
      await api("/api/news/upload", { method: "POST", form: data });
      closeOverlays();
      toast(t("saved"));
      await loadRoute();
    } catch (error) {
      toast(error.message, "error");
    }
  } else if (kind === "feedback-comment") {
    const body = new FormData(form).get("body");
    try {
      await api(`/api/news/${encodeURIComponent(form.dataset.newsId)}/feedback`, {
        method: "POST",
        body: { kind: "comment", body },
      });
      closeOverlays();
      toast(t("saved"));
    } catch (error) {
      toast(error.message, "error");
    }
  } else if (kind === "report") {
    const data = new FormData(form);
    try {
      const report = await api("/api/reports", {
        method: "POST",
        body: {
          type: data.get("type"),
          range_start: `${data.get("range_start")}T00:00:00+07:00`,
          range_end: `${data.get("range_end")}T23:59:00+07:00`,
        },
      });
      toast(t("saved"));
      await loadRoute();
      await openReportPreview(report.id);
    } catch (error) {
      toast(error.message, "error");
    }
  } else if (kind === "search") {
    await runSearch(form);
  }
});

document.addEventListener("keydown", (event) => {
  const actionable = event.target.closest('[data-action][role="button"]');
  if (actionable && (event.key === "Enter" || event.key === " ")) {
    event.preventDefault();
    // SVG elements do not implement click(); dispatch the same bubbling event
    // the delegated click handler listens for.
    actionable.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
    return;
  }
  const drawer = $("#drawer");
  const modal = $("#modal");
  if (event.key === "Escape") {
    if ((drawer && !drawer.hidden) || (modal && !modal.hidden)) {
      event.preventDefault();
      closeOverlays();
    }
    return;
  }
  if (drawer && !drawer.hidden) trapFocus(event, drawer);
  if (modal && !modal.hidden) trapFocus(event, modal);
});

/* ---------- Boot ---------- */

function routeFromHash() {
  const route = location.hash.replace("#", "") || "login";
  return ROUTES.includes(route) ? route : "overview";
}

window.addEventListener("hashchange", () => {
  state.route = routeFromHash();
  state.mobileNav = false;
  closeOverlays();
  loadRoute();
});

onLangChange(() => render());

state.route = routeFromHash();
loadRoute();
