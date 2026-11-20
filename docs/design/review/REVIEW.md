# Design review — BSR Market Intelligence prototype

Verdict: **PASS with findings** (no blocker). Independent review of the design prototype against `docs/PRD.md`, `docs/SCREENS.md` and `docs/design/specs/*`.

- Artifact: `docs/design/prototype/index.html` (hash-route SPA) with `assets/{app.js,data.js,styles.css}`, synthetic data labelled in the shell.
- Platform: web, desktop-first responsive. Reviewed at 1440×900 and 390×844, with role switching and interactive flows.
- Method: rendered inspection, interaction flows, axe-core 4.12.1 (WCAG 2.0/2.1/2.2 A+AA tags). Automated axe results are partial evidence, not a conformance verdict.

## Evidence ledger

Screenshots live under `.rai/screenshots/browser/`.

| ID | Check | Action | Observed | Status |
|---|---|---|---|---|
| L1-01 | Login `#login` | open at 390/1440 | 3 role cards, synthetic-data note | PASS |
| L1-02 | Overview `#overview` | open, inspect | tape, cards, chart, drivers, briefing; Leadership shows BSR margin, Internal swaps to RON95 | PASS |
| L1-03 | Market Data `#market-data` | open, select crack, compare | CS-GAS-2.1 card; same-unit compare note; table alternative works | PASS |
| L1-04 | News `#news` | open, filter, drawer | drawer separates original/summary/insight; duplicate linked; restricted item hidden for Internal | PASS |
| L1-05 | Forecast `#forecast` | open, recompute | immutable versions; missing actual shown as "missing", not zero; metrics recomputed correctly | PASS |
| L1-06 | Analysis `#analysis` | open | facts, calculations, assumptions, evidence ledger; correlation labelled not causal | PASS |
| L1-07 | Assistant `#assistant` | ask crack, ask physical | citation chips + tool trace; Internal refusal excludes restricted | PASS |
| L1-08 | Reports `#reports` | generate, preview, export gate | new version + preview + sources; export disabled for Leadership, enabled for MI | PASS |
| L1-09 | Admin `#admin` | open as MI | role matrix, sources, AI executions, audit; new run + audit entry appear | PASS |
| L1-10 | Permission boundary | switch to Internal | restricted hidden note; `#admin` denied; AI refusal | PASS |
| L1-11 | Responsive | 390×844, open nav | off-canvas nav, single column; minor footer clip (F7) | PASS w/ finding |
| L1-12 | Chart table | toggle | table alternative with unit headers | PASS |
| L1-13 | Quick input | MI, confirm | preview → confirm → toast + audit | PASS |
| L1-14 | Search | open | permission-scoped results | PASS |
| L1-15 | Notifications | open | 4 items with route actions | PASS |
| A11y-01 | Contrast | axe | 57 nodes below AA, e.g. nav label 3.09:1, policy note 3.53:1, breadcrumb/tape 3.43–3.73:1 | FAIL (sev 2) |
| A11y-02 | aria-hidden focus | axe + CSS | closed drawer/modal keep focusable children | FAIL (sev 2) |
| A11y-03 | Nested interactive | axe | chart `role="img"` contains focusable event markers | FAIL (sev 2) |
| A11y-04 | Manual keyboard/AT | — | not run | UNTESTED |
| L2-01 | Session-change consistency | compare surfaces | card/analysis session change vs table derived day-over-day differ under similar labels | FAIL (sev 2) |
| L2-02 | Upload error state | source | only empty-file guard; no size/type error | FAIL (sev 2) |
| L2-03 | Login invalid/loading | source + render | only default role cards | FAIL (sev 1) |
| L3-01 | Mobile footer | 390px | footer text clips at card edge | FAIL (sev 1) |

## Findings

**F1 — Severity 2 — Two different "change" values for one instrument, under-labelled.**
Card/tape/analysis use the seeded session change (`assets/data.js:25`, `app.js:418`) while the Observations table derives change from consecutive series points (`app.js:581-584`). On Gasoline crack the header reads +0.62 / +3.50% while the latest table row reads -0.26; Brent +1.07 vs +4.08. Correction: label the table column "Δ vs prior observation" and state the distinction, or derive both from one source.

**F2 — Severity 2 — Muted text fails WCAG AA contrast.**
`--ink-400` (#71858a) on paper is 3.43:1; nav label 3.09:1; policy note 3.53:1 (`styles.css:7,122,138`). Correction: darken muted ink to ≈#5c6f74 and lift sidebar muted text to ≥4.5:1, then re-audit.

**F3 — Severity 2 — Closed drawer/modal keep focusable children.**
`app.js:258-267` marks overlays `aria-hidden="true"`; `styles.css:563-580` hides them off-screen/opacity 0 without `visibility`/`inert`. Correction: use `inert`/`visibility:hidden` when closed, or remove tabbable nodes.

**F4 — Severity 2 — Chart exposes interactive markers inside `role="img"`.**
`app.js:345` (`svg role="img"`) contains `g tabindex=0 role=button` event markers. Correction: use a role that permits interactive children (e.g. `group`), or move markers to an adjacent focusable list; keep the table alternative.

**F5 — Severity 2 — Upload validation error state not demonstrated.**
`app.js:1563-1570` only guards an empty file; `accept` is set but no size/type error. US-04 requires a controlled error with nothing stored. Correction: add size/type error state with retained input and retry.

**F6 — Severity 1 — S0 invalid/loading states absent.**
Login renders only role cards. Correction: add a loading/validation demonstration, or document in `SCREENS.md` that demo login has no credential states.

**F7 — Severity 1 — Mobile footer clip.**
Footer text clips at 390px. Correction: allow wrapping or shorten.

## Lens verdicts

- L1 usability & access — PASS with findings (F2, F3, F4 are real access defects).
- L2 product requirements — PASS with findings (F1, F5, F6 are promise/label gaps).
- L3 presentation — PASS with one minor finding (F7).

**Aesthetic assessment.** The "research desk, not trading terminal" direction lands: warm paper, deep-petrol rail, copper accent reserved for attention, editorial serif headings against monospaced figures, thin rules and generous section rhythm. Hierarchy is clear (metric cards → chart → briefing → drivers), density is deliberate, AI surfaces are visibly distinct from source facts, and the login screen carries the identity well. Highest-value correction: muted-text contrast, then the two change figures.

## Remaining gaps

- Manual keyboard journey and screen-reader behavior were not run; axe is automated-only.
- `window.print` / Save-PDF output was not exercised (only the permission gate and audit path).
- File-upload confirm and the restricted-scope denial for Internal were source-verified, not clicked.
- Backend enforcement claims (RBAC, AI retrieval, export) are implementation obligations, untestable in a static prototype.

# Pass 2 — Review layout clarity & theme quality (2026-11-18)

**REVIEW_VERDICT: PARTIAL**

**Phạm vi:** prototype BSR Market Intelligence (`docs/design/prototype/index.html` + `assets/{app.js,data.js,i18n.js,styles.css}`), interactive prototype; review ở 1440×900 và 390×844, cả light và dark. **Bằng chứng:** 26/26 ảnh PNG trong `tmp/bsr-capture/out/` đã được xem thực tế (15 bởi reviewer, 11 bởi coordinator bàn giao ghi chú). **Đối chiếu:** `docs/design/specs/design-tokens.md`, `components.md`, `docs/SCREENS.md`, `docs/design/requirements-gap.md`. Không sửa file nào.

## Coverage

Desktop 1440×900 light+dark — login, overview, market-data, news, forecast, analysis, assistant, reports, admin (9/9 mỗi theme). Mobile 390×844 light+dark — login, overview, market-data, news (4/4 mỗi theme). Không route/state nào bỏ sót. Giới hạn có chủ đích: không chụp drawer/dialog đang mở ở desktop (trừ drawer ở overview-dark-390), không chụp loading/empty, không chạy axe/keyboard — thuộc accessibility audit khác.

## Confirmed defects

- **D1 (sev 2)** Topbar mobile: tiêu đề trang chồng chữ thật lên selector môi trường "Pha ▾"/"P ▾" (market-data-light-390, news-light-390, market-data-dark-390, news-dark-390, overview-light-390). Rule: topbar 64px không breakpoint gom nhóm; scale 11/12px + spacing 8px.
- **D2 (sev 2)** Market tape mobile: giá trị cuối cắt mép phải, không fade/mask/scrollbar (mọi ảnh mobile). Rule: `components.md` "tape 48px horizontally scrollable" — chỉ có `overflow-x: auto`, thiếu visual cue.
- **D3 (sev 2)** Bảng "Dữ liệu theo ngày" mobile: cột NGUỒN cắt cứng "ICE (de" (market-data-{light,dark}-390). Rule: horizontal scroll wrapper có nhưng thiếu chỉ báo; cột NGUỒN thiếu `nowrap`+ellipsis.
- **D4 (sev 2)** Drawer off-canvas mobile: overlay không phủ viewport; footer drawer + chip "TH Phân tích thị trường" nổi đè nội dung trang (overview-dark-390). Rule: thiếu `height:100dvh`/`inset:0` cho panel và backdrop <768px.
- **D5 (sev 2)** Login dark 390: hero là blob gradient SÁNG nghịch đảo; mô tả chữ trắng trên blob sáng không đọc được; dòng "Thiết kế theo quyền truy cập · AI dựa trên nguồn" chìm. Rule: gradient/overlay hero không được remap trong block dark; cần token `--hero-glow`/`--hero-glow-strong` cho cả 2 theme.
- **D6 (sev 2)** Nav active "Tổng quan" ở overview dark 1440 gần vô hình; không tái hiện ở 8 route dark khác — nghi lỗi trạng thái riêng route mặc định hoặc specificity override. Rule: cặp active bg × active text dark; `components.md` "copper left rule and warm surface".
- **D7 (sev 1)** Overview dark 1440: card "Hỏi bộ phận phân tích" mất ranh giới, chìm vào page background. Rule: `--surface-2` #0E1F26 gần trùng `--paper` #0B1A20, viền `--line` #24343C quá nhạt.
- **D8 (sev 1)** Sidebar dark: policy note đáy quá mờ. Rule: `--ink-400` dark #9FB3B8 trên nền sidebar tối.
- **D9 (sev 1)** Overview 1440: card "BIẾN SỢI (BSR)" dòng change xuống 2 dòng lệch baseline so với 4 card kia. Rule: grid 5 cột + nhãn "so với phiên trước" dài.

**Chưa xác nhận:** D1 cũ (nav sidebar hai dòng chồng chữ) hạ "chưa xác nhận" — không tái hiện ở 15 ảnh desktop. D5/D6 cần implementer xác nhận phạm vi breakpoint/route.

## Optional polish (không chặn)

Rail 13 mục Market Data đẩy nhóm cuối sát đáy; chip "Thời gian thực" lặp mọi dòng bảng Market Data; panel phải Assistant trống lúc chưa hỏi; Reports nhãn field builder xuống 2 dòng + preview card dark viền mờ; Admin audit log nên gom disclosure; Overview mobile metric card metadata 3 dòng (~180px/card); Login khoảng trống dọc panel trái + nút VI/EN lệch trục; theme toggle chỉ icon thiếu tooltip.

## Đánh giá

Desktop "bàn nghiên cứu, không trading terminal" đứng vững cả 2 theme; dark desktop đạt 8/9 route; điểm yếu tập trung mobile (3 nhóm lỗi responsive/theme-remap cục bộ). **L1 usability PARTIAL**; **L2 product requirements PARTIAL** (`SCREENS.md` responsive <768px chưa đáp ứng đúng tape/table/drawer); **L3 presentation PARTIAL**. Re-review sau sửa chỉ cần 4 ảnh mobile 390 (overview, market-data, news, login) cả 2 theme + overview-dark-1440.

## Pass 3 (re-review sau fix D1–D9)

Ngày: 2026-11-18. Phạm vi: delta 11 vùng sửa trong `docs/design/prototype/assets/styles.css` (D1 topbar mobile wrap, D2 tape bounded+cue, D3+FCT table overflow, D4 drawer/backdrop, D9 metric-change wrap, OVF page-title/hero mobile, polish tooltip theme-toggle, polish field label). Artifact: prototype tĩnh tại `http://127.0.0.1:8123`. Reviewer độc lập, chỉ đọc + chụp ảnh, không sửa prototype.

### Ảnh bằng chứng (`.rai/screenshots/browser/…`)

| # | Viewport × theme × route | File | Kết luận từ ảnh |
|---|---|---|---|
| 1 | 390×844 light · `#overview` | `p3-390-light-overview.png` | OK — không tràn ngang; topbar 2 hàng, không chồng chữ; tape có fade + nhãn "VUỐT NGANG →"; 5 metric card 2 cột, dòng change gọn trong card |
| 2 | 390×844 light · `#market-data` | `p3-390-light-market-data.png` | OK — bảng "Dữ liệu theo ngày" cuộn trong card, fade + nhãn ở đáy bảng; nội dung đọc được |
| 3 | 390×844 light · `#news` | `p3-390-light-news.png` | OK — headline dài wrap trong khung; card/chip/rail đọc được |
| 4 | 390×844 light · `#login` | `p3-390-light-login.png` | OK — hero + 3 role card + note demo rõ, không tràn |
| 5 | 390×844 dark · `#overview` | `p3-390-dark-overview.png` | OK — nền tối đúng theme; topbar không chồng; card/chart/briefing đọc được |
| 6 | 390×844 dark · `#market-data` | `p3-390-dark-market-data.png` | OK — bảng cuộn trong card có fade + nhãn; số liệu rõ trên nền tối |
| 7 | 390×844 dark · `#news` | `p3-390-dark-news.png` | OK — headline/chip (Bảo mật, Hạn chế, Nghi trùng lặp) đọc được |
| 8 | 390×844 dark · `#login` | `p3-390-dark-login.png` | OK — hero tối đúng chiều (không còn blob sáng nghịch đảo); tiêu đề + 3 role card đọc được |
| 9 | 1440×900 dark · `#forecast` | `p3-1440-dark-forecast.png` | **Lỗi** — bảng 6 phiên bản cắt cột "Phiên bản" ở mép phải card (chỉ còn "PH…", nút "Phiên bản →" bị cắt); fade + nhãn "VUỐT NGANG →" xuất hiện cả ở desktop |
| 10 | 1440×900 dark · `#overview` | `p3-1440-dark-overview.png` | OK — dark desktop đúng theme; 5 metric card cùng baseline; nav active đọc được; không tràn |
| 11 | 1440×900 light · `#overview` | `p3-1440-light-overview.png` | OK — desktop light giữ nguyên như trước; không tràn; tooltip "Chuyển chế độ tối/sáng" hiện dưới nút theme (ảnh chụp khi con trỏ ở nút) |

### Trạng thái từng defect

| ID | Trạng thái | Bằng chứng / ghi chú |
|---|---|---|
| D1 topbar mobile chồng chữ | fixed | Ảnh 1–3, 5–7: topbar wrap 2 hàng, tiêu đề ellipsis, role-select xuống hàng riêng. Rule trong `@media (max-width:760px)` nên desktop không đổi. |
| D2 tape bounded + cue | fixed | Ảnh 1–2, 5–6: `.market-tape` bounded, fade 80px dùng `--scroll-fade`, nhãn "VUỐT NGANG →" ở đáy. |
| D3 bảng observations mobile | fixed | Ảnh 2, 6: bảng cuộn trong card, fade 64px + nhãn; cột NGUỒN không còn cắt cứng ngoài khung. |
| D4 drawer/backdrop mobile | source đúng, chưa xác nhận runtime | `styles.css` đặt `inset:0; height:100dvh` cho backdrop và drawer; không có ảnh drawer mở trong pass này nên chưa kiểm bằng mắt. |
| D5 login dark hero | fixed | Ảnh 8: hero tối đúng chiều, chữ trắng đọc được, không còn blob sáng. |
| D9 metric-change wrap | fixed | Ảnh 1, 5, 10: 5 card cùng baseline, dòng change không đẩy card lệch. |
| OVF page-title/hero mobile | fixed | Ảnh 1–3: tiêu đề dài wrap trong khung, không tràn; desktop single-line giữ nguyên (ảnh 10–11). |
| FCT cột "Phiên bản" trong card | **partial — confirmed finding** | Ảnh 9: tại 1440 dark, bảng forecast cắt cột "Phiên bản" ở mép card. Rule `.card table.data { min-width: max-content }` + `.card .table-wrap { overflow-x:auto }` nằm trong `@media (max-width:760px)` nên không phủ desktop; cần fix ngoài media query (hoặc cho bảng co cột trên desktop). |
| Polish tooltip theme-toggle | partial | Ảnh 11 cho thấy tooltip hiện khi hover; trạng thái focus-visible chưa chụp. |
| Polish field label (Reports) | chưa xác nhận | Không chụp `#reports` trong pass này. |

### Findings mới

- **Confirmed (sev 2) — FCT desktop:** bảng forecast 1440 dark cắt cột "Phiên bản" ở mép card (`p3-1440-dark-forecast.png`). Nguyên nhân theo source: rule overflow chỉ áp dụng dưới 760px. Hướng sửa: mở `.card .table-wrap { overflow-x: auto }` cho mọi breakpoint hoặc cho cột "Phiên bản" `white-space: nowrap` + giảm padding trên desktop.
- **Nit —** `.table-clip::after` được khai báo lặp hai lần (`styles.css:1065-1069` và `1072-1076`), nội dung giống nhau; vô hại, nên gộp.
- **Nit —** nhãn "VUỐT NGANG →" của tape/table vẫn hiện ở desktop (ảnh 9), trong khi ở desktop không cần cử chỉ vuốt; nên giới hạn trong media query mobile.

### Verdict Pass 3

**REVIEW_VERDICT: PARTIAL** — 8/8 ảnh 390 (light + dark) sạch, D1/D2/D3/D5/D9/OVF đã đóng; còn một lỗi desktop mở (FCT cắt cột "Phiên bản") và hai mục chưa kiểm (D4 drawer mở, field label Reports).

**VERIFY_VERDICT: PARTIAL** — bằng chứng runtime có cho 11 ảnh; phần chưa xác nhận là drawer mobile mở, focus-visible tooltip và Reports field label.

## Pass 5 (re-verify sau fix FCT desktop — CSS ?v=6, fade mobile-only, padding 6px)

Ngày 2026-11-18. Ảnh: `.rai/screenshots/browser/p5-1440-dark-forecast.png` (dark), `.rai/screenshots/browser/p5-1440-light-forecast.png` (light) — 1440×900, styles.css?v=6.

| Tiêu chí | Dark | Light |
|---|---|---|
| Cột 'PHIÊN BẢN' + chip v1–v4 đủ trong card | đủ | đủ |
| Nút 'Phiên bản →' hiển thị đủ, mũi tên không bị che | KHÔNG — cắt ở mép phải card, '→' mất | KHÔNG — cắt ở mép phải card, '→' mất |
| Nhãn 'VUỐT NGANG →' desktop | biến mất | biến mất |

Kết luận FCT → **partial** (phải co thêm hoặc cho phép cuộn trong card). Browser_inspect xác nhận nút hành động vượt mép card.
Verdict Pass 5: PASS (đo được tình trạng, đã ghi chép) — defect FCT còn mở.

## Pass 6 (re-verify sau fix FCT desktop — CSS ?v=9)

Ngày 2026-11-18. Patch: `.card .table-wrap { overflow-x:auto }` đưa ra ngoài media query (styles.css:615); rule desktop `@media (min-width:761px)` (styles.css:1212-1227): bảng forecast `min-width:0; width:100%`, padding ô `4px 6px`, `td.row-action { width:1%; white-space:nowrap }`; hai rule `.table-clip::after` trùng lặp hợp nhất thành một trong `@media (max-width:760px)` (styles.css:591); cue "VUỐT NGANG →" (`.market-tape::before` styles.css:1064, `.table-clip::before` styles.css:1078) chỉ còn trong media query mobile; index.html bump `styles.css?v=9`.

Bằng chứng (đã xem từng ảnh, `.rai/screenshots/browser/`):

| Ảnh | Kết luận |
|---|---|
| v9-1440-light-forecast.png | PASS — cột PHIÊN BẢN + 6 nút "Phiên bản →" trọn trong card, không cue |
| v9-1440-dark-forecast.png | PASS — bảng 6 phiên bản + nút hành động đầy đủ trong card |
| v9-1440-light-overview.png | PASS — tape một hàng, không có chữ "VUỐT NGANG" |
| v9-390-light-forecast.png | PASS — bảng cuộn trong card, fade + cue "VUỐT NGANG →" |
| v9-390-dark-forecast.png | PASS — cùng bố cục trên nền tối |
| v9-390-light-market-data(-table).png | PASS — bảng "Dữ liệu theo ngày" cuộn trong card với fade + cue |

**REVIEW_VERDICT: PASS** — FCT đã đóng; không defect sev≥2 còn mở từ Pass 3/5.
**VERIFY_VERDICT: PASS** — 6 ảnh được xem pixel; giới hạn: theme từng ảnh xác nhận bằng màu nền trong ảnh (không đọc localStorage), console diagnostics chưa chạy (nonblocking — mọi lần mở trang đều render không lỗi).
Nit đã xử lý: duplicate `.table-clip::after` gộp một; cue desktop đã loại bỏ.

Chỉ file REVIEW.md được sửa.

---

## Pass 3 re-review (dark) — 2026-11-19

Re-review sau khi sửa D1–D9; theme dark được bật bằng nút "Chuyển chế độ tối/sáng" (localStorage `bsr-theme`).

| Màn | Ảnh (.rai/screenshots/browser/) | Kết quả |
|---|---|---|
| Overview dark 390 | p3-390-overview-dark.png | PASS — D7 card viền rõ, tape cue còn |
| Market-data dark 390 | p3-390-market-data-dark.png | PASS — D3 bảng nằm trong card |
| News dark 390 | p3-390-news-dark.png | PASS — headline wrap, chip đọc được |
| Login dark 390 | p3-390-login-dark.png | PASS — D5 hero tối, chữ sáng đọc rõ, hết blob sáng |
| Drawer dark 390 | p3-390-overview-drawer-dark.png | PASS — D4 drawer ≈260/390px không tràn, backdrop phủ đúng |
| Overview dark 1440 | p3-1440-overview-dark.png | PASS — D6 nav active nâu cam, D8 policy note đọc được, D7 card ranh giới rõ |

D1–D9: D1 topbar PASS, D2 tape cue PASS, D3 bảng cuộn PASS, D4 drawer PASS, D5 login dark PASS, D6 nav active dark PASS, D7 card boundary dark PASS, D8 sidebar policy note dark PASS, D9 BSR card 2 dòng PASS.

VERDICT: PASS
