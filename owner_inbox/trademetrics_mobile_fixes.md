# TradeMetrics Mobile & Accessibility Fixes
**Audit task:** MOBILE-AUDIT-002  
**Agent:** Rex (Web Developer)  
**Date:** 2026-05-02  
**Commit:** `8e266c5`  
**Repo:** https://github.com/InonB2/trademetrics

---

## Files Changed

| File | Change |
|---|---|
| `index.html` | Title updated: "TradeJournal" → "TradeMetrics" |
| `src/components/dashboard/TradesTable.jsx` | P&L display updated in both mobile card view (line 57) and desktop table view (line 155) |

---

## Fix Status by Issue

### TP-MOB-02 — Responsive chart containers
**Status: Already fixed (no changes needed)**

All chart components in the codebase already use `<ResponsiveContainer width="100%">` from Recharts. Confirmed in:
- `EquityCurve.jsx`, `MonthlyPnlChart.jsx`, `WinRateChart.jsx`
- `RMultipleChart.jsx`, `SetupBreakdownWidget.jsx`
- `Analytics.jsx`, `Backtest.jsx`, `Benchmarking.jsx`, `Replay.jsx`, `RiskDashboard.jsx`, `SetupPerformance.jsx`, `RuleEngine.jsx`

No hardcoded pixel widths on any chart component. Fixed heights (e.g. `height={300}`) are intentional and correct — ResponsiveContainer handles responsive width automatically.

### TP-MOB-03 — Trade log mobile responsive table
**Status: Already fixed (no changes needed)**

`TradesTable.jsx` already implements a dual-layout approach:
- Mobile (`sm:hidden`): Card-per-trade layout showing instrument, direction, entry/exit price, date, and P&L
- Desktop (`hidden sm:block`): Full multi-column table with progressive disclosure (secondary columns hidden via `hidden md:table-cell`, `hidden lg:table-cell`, `hidden xl:table-cell`)

### TP-A11Y-05 — P&L color-blind accessibility (triangle symbols)
**Status: FIXED**

Changed P&L display in `TradesTable.jsx` to use triangle symbols instead of `+`/`-` signs:
- Profit: `▲ $250.00` (green) — was `+$250.00`
- Loss: `▼ $127.50` (red) — was `-$127.50`
- Breakeven: `$0.00` (muted) — unchanged

Applied to both the mobile card layout and the desktop table's Net P&L column. Used `Math.abs()` on the value so loss amounts don't show redundant double-negation (e.g. `▼ $127.50` not `▼ $-127.50`).

Note: The MetricCard component (used on the Dashboard for Today's P&L, Total P&L, Expectancy) and the MonthlyPnlChart tooltip also show color-coded P&L but were not in scope for this ticket. Those are lower-frequency display paths and can be addressed in a follow-up audit item if needed.

### TP-MOB-05 — PWA icon size (718KB)
**Status: Cannot fix from source code**

The repository has no `public/` directory and no icon PNG files. The app is hosted on the Base44 platform, which serves the manifest.json and all PWA icon assets from its own CDN. There is no source icon to resize in this repo.

**Inon must handle manually:** Log into the Base44 dashboard for this app → find PWA/manifest settings → upload new icon files at 192×192px (~10KB target) and 512×512px (~25KB target). These can be generated from any image editor or tool like squoosh.app.

### TP-MOB-08 — Brand name inconsistency
**Status: FIXED (partial — see note)**

Updated `index.html`:
```
<title>TradeMetrics</title>
```
(was `<title>TradeJournal</title>`)

The `manifest.json` is not in the repo — it's served by Base44 at `/manifest.json` from their platform infrastructure.

**Inon must handle manually:** Log into the Base44 dashboard → find app settings or manifest configuration → set `name: "TradeMetrics"` and `short_name: "TradeMetrics"` to match the code name and URL.

---

## Items Requiring Manual Action (Base44 Dashboard)

1. **TP-MOB-05** — Upload optimized PWA icons (192px ≈ 10KB, 512px ≈ 25KB) in Base44 app settings
2. **TP-MOB-08 (partial)** — Set `manifest.json` `name` and `short_name` to "TradeMetrics" in Base44 dashboard
3. **TP-MOB-01** (from original Vera audit, not in this ticket scope) — If viewport meta tag is missing or wrong, it must be set in the Base44 dashboard's HTML shell editor, not in this repo's `index.html` (which appears to already have the correct viewport meta, but Base44 may override it)

---

## Prevention Notes

- All new chart components added to this app should continue the established pattern of `<ResponsiveContainer width="100%">` with a pixel height.
- New P&L display locations (tooltips, summary cards, export PDFs) should use the `▲`/`▼` convention established in TradesTable going forward.
- Platform-managed assets (manifest, icons, meta tags) cannot be version-controlled — document in README that these must be managed via Base44 dashboard.
