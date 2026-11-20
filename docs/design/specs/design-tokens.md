# Design tokens — BSR Market Intelligence

## Color

| Token | Value | Role |
|---|---|---|
| `--ink-950` | `#0A1D24` | Page text, sidebar background |
| `--ink-800` | `#16343D` | Sidebar hover, strong headings |
| `--ink-600` | `#3F5960` | Secondary text |
| `--ink-400` | `#4B5F65` | Muted labels, metadata (≥4.5:1 on paper, surface, surface-2) |
| `--paper` | `#F4F1E9` | App background |
| `--surface` | `#FCFBF7` | Cards, panels |
| `--surface-2` | `#EDE9DF` | Recessed areas, table headers |
| `--line` | `#D9D3C6` | Hairline borders |
| `--line-strong` | `#BEB5A4` | Emphasized dividers |
| `--copper` | `#B45B2D` | Primary accent, selection, AI provenance |
| `--copper-soft` | `#EAD2C1` | Accent wash |
| `--teal` | `#1D6A63` | Secondary data series, positive-neutral |
| `--positive` | `#2C7656` | Price up / success |
| `--negative` | `#AC423C` | Price down / error |
| `--warning` | `#9A6A18` | Delayed, pending, caution |
| `--restricted` | `#75405F` | Restricted classification |
| `--focus` | `#2C6E9C` | Focus ring |
| `--white` | `#FFFFFF` | Elevated surfaces |
| `--hero-glow` | `rgba(234,210,193,.55)` | Login brand-panel radial highlight (from `--copper-soft`) |
| `--hero-glow-strong` | `rgba(234,210,193,.22)` | Secondary hero highlight, lower corner |
| `--scroll-fade` | `var(--surface)` | Right-edge fade for horizontally scrollable strips (market tape, data tables) |
| `--topbar-bg` | `#F4F1E9` | Topbar surface; fully opaque so page content never shows through while scrolling (dark value: `#0B1A20`) |

Semantic red/green are reserved for direction and validation, never decoration. Classification uses a muted label + icon, not color alone.

## Dark palette

| Token group | Dark value / rule |
|---|---|
| Surfaces | `--paper: #0B1A20`, `--surface: #12242B`, `--surface-2: #0E1F26` |
| Text | `--ink-950: #E8EEF0`, `--ink-900: #CFDBE0`, `--ink-800: #B8C8CE`, `--ink-700: #A3B7BD`, `--ink-600: #8FA5AB`, `--ink-400: #9FB3B8` |
| Lines | `--line: #24343C`, `--line-strong: #35474F`, `--grid-line: #1C2E36` |
| Accents | `--copper: #D67A45`, `--copper-dark: #E08A55`, `--copper-soft: #3F2617`, `--teal: #5CB3A6` |
| Status | `--positive: #6DC594`, `--negative: #E07F77`, `--warning: #D9A94E`, `--restricted: #C993B6`, `--focus: #6DB3DD` |
| Chips | Every chip variant has dark `bg`, `border`, and `text` tokens; do not hard-code variant colors in component rules. |
| Overlays | Topbar, grid, fresh-dot, backdrop, sidebar and login overlays use semantic tokens; shadows use the dark `--shadow`. |
| Hero glow | `--hero-glow: rgba(214,122,69,.20)`, `--hero-glow-strong: rgba(214,122,69,.08)` — a low-alpha copper wash over the dark brand panel. The login hero never borrows the inverted ink scale for its gradient. |
| Scroll fade | `--scroll-fade: var(--surface)` — the fade must match the strip's own background in each theme. |

Theme dark/light là yêu cầu người dùng bổ sung — tài liệu yêu cầu PDF/DOCX không nêu.

Surfaces that stay dark in both themes (`--sidebar-bg`, `--panel-dark-bg`) must be used for any panel that is dark by design; the ink scale inverts between themes and cannot be used as a background there. The same rule applies to text on those panels: state the light ink explicitly rather than relying on `--white`, which is remapped to the dark surface in the dark theme.

## Type

- Display: `"Be Vietnam Pro", "Noto Serif", Georgia, "Times New Roman", serif` — page titles, briefing headlines, report titles. The lead family must carry Vietnamese stacked diacritics (ấ ầ ể ữ ộ); Be Vietnam Pro is loaded from Google Fonts with a dedicated `vietnamese` subset, and display tracking stays at or above −0.01em so accents are not clipped.
- Body/UI: `"Be Vietnam Pro", "Segoe UI", Aptos, system-ui, -apple-system, sans-serif` — navigation, labels, prose.
- Figures: `"Cascadia Mono", "SFMono-Regular", Consolas, monospace` — prices, percentages, timestamps, IDs.
- Scale: 11 / 12 / 13 / 14 / 16 / 20 / 28 / 38 px. Page title 38px desktop, 30px narrow. Table text 13px. Metadata 11–12px.
- Weights: 400 body, 500 emphasis, 600 labels, 700 figures. Display uses 400/500 only.

## Space, shape, elevation

- 4px base; common steps 4, 8, 12, 16, 20, 24, 32, 48.
- Radius: 2px controls, 4px cards, 999px pills. Avoid pill-heavy layouts.
- Border: 1px `--line`; selected state uses 2px copper inset or left rule.
- Shadow: `0 1px 2px rgba(10,29,36,.05), 0 8px 24px rgba(10,29,36,.06)` only for drawers/popovers.
- Density: compact but readable; 44px table rows, 56px nav items.

## Motion

- 120–180ms ease-out for drawers, hover, disclosure. Respect `prefers-reduced-motion`.
- No auto-rotating carousels or animated tickers.

## Charts

- Series: copper `#B45B2D`, teal `#1D6A63`, slate `#547078`, gold `#9A6A18`, plum `#75405F`.
- Grid: `#E2DDD1`; axis text `#4B5F65`; event marker: copper diamond with ink outline.
- Always label units; provide a table alternative; show missing data as gaps, not zero.
