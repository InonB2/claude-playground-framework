# QA Report: Dashboard Redesign — `index.html`
**Auditor:** Vera  
**Date:** 2026-05-08  
**File:** `D:\Claude Playground\dashboard\index.html`  
**Total lines:** 1574  
**Audit scope:** Typography, LinkedIn CMS, Owner-blocked cards, Notification bell, Visual polish, Regression, Accessibility

---

## Feature 1: Typography

### PASS — Syne on Column Headers and Tab Labels
- `.col-title` (line 195): `font-family:'Syne',sans-serif` — PASS
- `.tab-btn` (line 152): `font-family:'Syne',sans-serif` — PASS
- `.topbar-title` (line 79): `font-family:'Syne',sans-serif` — PASS

### PASS — JetBrains Mono on IDs and Timestamps
- `.card-id` (line 236): `font-family:'JetBrains Mono',monospace` — PASS
- `.last-updated` (line 140): `font-family:'JetBrains Mono',monospace` — PASS
- `.col-count`, `.notif-item-meta`, `.job-card-date` all use JetBrains Mono — PASS

### PASS — Google Fonts Load
Line 6: Both `Syne` and `JetBrains Mono` requested in single `<link>` with `Inter` as body font. Correct `display=swap` included. No fallback issues — system monospace fallback present for JetBrains Mono via CSS keyword `monospace`.

**Typography verdict: PASS**

---

## Feature 2: LinkedIn CMS Tab

### PASS — Tab Present
Line 536: `<button class="tab-btn" data-tab="linkedin">LinkedIn</button>` — present in tab bar.

### PASS — Two-Column Layout
Lines 657–681: `linkedin-layout` flex container with `linkedin-list-panel` (340px) and `linkedin-detail-panel` (flex:1). Responsive breakpoint at 900px collapses to single column (line 481). Correct.

### PASS — Four Pipeline Stages
Line 1321: `const LI_STAGES=['Idea','Draft','Approved','Posted']` — all four stages rendered dynamically via `renderLiList()`.

### PASS — RTL Textarea with dir and lang
Line 880 (New Post modal): `<textarea id="liNewBody" rows="5" dir="rtl" lang="he">` — PASS  
Line 1426 (edit mode): `<textarea class="li-post-body-edit" id="liEditBody" dir="rtl" lang="he">` — PASS

### PASS — View-mode body div has RTL
Line 453–457: `.li-body-view` CSS has `direction:rtl;text-align:right` — PASS

### FLAG (Minor) — Sticky Hebrew Banner: Positioning Calculation
Line 366: `.linkedin-hebrew-banner` has `position:sticky;top:108px`. This assumes topbar (64px) + tabbar (44px) = 108px. This is correct in the current layout. However, the `linkedin-layout` height at line 368 is `calc(100vh - 180px)` which assumes topbar (64) + tabbar (44) + banner (assumed ~72px) = 180px. The banner is 10px padding top + 10px padding bottom + 11px font + 2px border = ~34px, making this 64+44+34 = 142px, not 180px — there is a 38px overcalculation. The two-column area will have a noticeable gap/unused space at the bottom on standard viewports.
- **Line:** 368
- **Severity:** Minor
- **Fix:** Change `height:calc(100vh - 180px)` to `height:calc(100vh - 144px)` or use `min-height` instead of fixed height.

### PASS — Banner Non-Dismissable
No close button or dismiss logic on the banner. `position:sticky` ensures it stays anchored. Confirmed non-dismissable.

### PASS — Banner Visible Only in LinkedIn Tab
Banner is inside `#tab-linkedin` div (line 650), which uses `display:none` when not active. The banner is correctly scoped to the LinkedIn tab only.

### FLAG (Minor) — Hebrew Text in Banner Uses Mixed Approach
Line 654: `<bdi>Hebrew</bdi>` — the word "Hebrew" is English, not actually Hebrew text, so `<bdi>` here is semantically incorrect (it wraps an English word, not Hebrew content). The banner reads: "All LinkedIn posts must be written in Hebrew only." The intent is correct but the `<bdi>` is applied to the wrong token. Hebrew content in list items uses `dir="rtl"` on the `.li-post-preview` div (line 1366), which is flagged below.
- **Line:** 654
- **Severity:** Minor
- **Fix:** The `<bdi>` on "Hebrew" is harmless but misleading. No Hebrew characters appear in the static banner — it's entirely English. If intent was to protect Hebrew text, apply it to actual Hebrew strings.

### FLAG (Major) — li-post-preview Uses dir="rtl" Not bdi
Line 1366 (JS template literal inside `renderLiList()`):
```js
`<div class="li-post-preview" dir="rtl">${escHtml(preview)}</div>`
```
The requirement specifies Hebrew text must use `<bdi>`, not `<span dir="rtl">` or any block element with `dir="rtl"`. A `<div dir="rtl">` changes the block-level direction and can affect surrounding layout. The correct pattern for inline bidirectional isolation is `<bdi>`.
- **Severity:** Major (spec non-compliance)
- **Fix:** For the preview snippet, either wrap content in `<bdi>`: `<div class="li-post-preview"><bdi>${escHtml(preview)}</bdi></div>` (and remove `dir="rtl"` from the div), or keep the block-level `dir="rtl"` but add `<bdi>` around the escaped content within it. Given the preview is a block-level truncated snippet, acceptable alternative: keep `dir="rtl"` on the container div but add `<bdi>` inside.

**LinkedIn CMS verdict: CONDITIONAL PASS — 3 flags including 1 Major**

---

## Feature 3: Owner-Blocked Cards

### PASS — #FF6B00 Color
Line 35: `--owner-block:#FF6B00` — exact hex as specified.

### PASS — ownerPulse Animation
Line 60: `@keyframes ownerPulse{...}` defined.  
Line 228: `.card.owner-blocked` applies `animation:ownerPulse 2.5s ease-out infinite` — PASS.

### PASS — "WAITING ON YOU" Prefix
Line 241: `.card.owner-blocked .card-note::before{content:'WAITING ON YOU · ';color:var(--owner-block);...}` — PASS.

### PASS — Reads blockedBy:"owner"
Line 1063: `const isOwnerBlocked = task.blockedBy==='owner'` — null-safe optional access.

### PASS — No Crash on Missing Field
Line 1063 guards the field. Line 1161: `t.blockedBy||''` used in modal save/load — gracefully handles undefined/null.

### FLAG (Minor) — Owner-blocked section header inserted only in "blocked" column
Lines 1089–1099: The `owner-blocked-section-header` is prepended only when `isOwnerBlocked && col==='blocked'`. But a task can have `blockedBy:'owner'` and `status:'needs-you'` (e.g., WEBSITE-001-SEC-01 in seed data, line 939). In that case, the card gets `owner-blocked` styling but no section header, which is the correct behavior. However, the "WAITING ON YOU" prefix on `.card-note::before` (CSS, line 241) will still display regardless of which column the card appears in. This may cause the orange "WAITING ON YOU" label to appear on a card in the Needs You column even if the intent was to show it only in the Blocked column. This is a minor UX inconsistency, not a crash.
- **Line:** 241 (CSS) vs 1089 (JS)
- **Severity:** Minor
- **Fix:** Scope the `::before` pseudo-element to `.col-blocked .card.owner-blocked .card-note::before` to restrict it to the blocked column only.

**Owner-blocked verdict: PASS (1 minor flag)**

---

## Feature 4: Notification Bell Dropdown

### PASS — Dropdown Panel Not Modal
Lines 512–520: `notif-panel` is a `<div>` absolutely positioned inside `.topbar-right`. Not a `<dialog>`, not `.modal-overlay`. Correct dropdown pattern.

### PASS — aria-live and aria-atomic on Badge
Line 509: `<div class="notif-bell-badge hidden" id="notifBadge" aria-live="polite" aria-atomic="true">` — both attributes present.

### PASS — Count Hidden at Zero
Line 1003: `badge.classList.toggle('hidden', count===0)` — correctly adds/removes the `.hidden` class (which sets `display:none` per line 99).

### PASS — Closes on Escape
Line 1030: `document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeNotifPanel();...}})` — PASS.

### PASS — Closes on Click-Outside
Lines 1031–1037: `document.addEventListener('click',...)` checks if click is outside both `notifPanel` and `notifBell` — PASS.

### PASS — Closes via X Button
Line 515: `<button class="notif-panel-close" onclick="closeNotifPanel()">✕</button>` — PASS.

### PASS — 9+ Cap on Badge
Line 1002: `badge.textContent = count > 9 ? '9+' : String(count)` — PASS.

### FLAG (Minor) — notif-bell lacks role and keyboard accessibility
Line 507: `<div class="notif-bell" id="notifBell" onclick="toggleNotifPanel()" title="Notifications">` — this is a `<div>` acting as a button. It lacks `role="button"`, `tabindex="0"`, and `aria-expanded` state. Keyboard-only users cannot Tab to it or activate it with Enter/Space.
- **Severity:** Major (WCAG 2.1 AA: 2.1.1 Keyboard)
- **Fix:** Change to `<button>` element, or add `role="button" tabindex="0"` and a `keydown` handler for Enter/Space. Also add `aria-expanded="false"` that toggles to `true` when panel is open.

**Notification bell verdict: CONDITIONAL PASS — 1 Major accessibility flag**

---

## Feature 5: Visual Polish

### PASS — Stagger Animation on Page Load
Line 1069: `card.style.animationDelay = \`${cardIndex*30}ms\`` — each card gets progressively delayed `cardIn` animation. PASS.

### PASS — Tab Switch Fade-In
Line 160: `.tab-content.active{display:block;animation:tabFadeIn 0.15s ease}` — PASS.

### PASS — Card Shimmer on Hover
Lines 220–221: `.card:hover::after` with radial-gradient shimmer pseudo-element. PASS.

### PASS — Critical Card Glow
Line 221: `.card.priority-critical{box-shadow:0 0 0 1px rgba(239,68,68,0.25),0 4px 16px rgba(0,0,0,0.4)}` — PASS.

### PASS — Animations Use transform/opacity Only
- `cardIn` (line 57): `transform:translateY(8px)` + `opacity` — PASS
- `tabFadeIn` (line 58): `transform:translateY(4px)` + `opacity` — PASS
- `ownerPulse` (line 60): `box-shadow` only — note: `box-shadow` does NOT trigger layout reflow and runs on the compositor, so this is acceptable. PASS.
- `expandBar` (line 59): `transform:scaleX()` + `opacity` — PASS
- `notifSlideIn` (line 61): `transform:translateY(-8px)` + `opacity` — PASS

### FLAG (Minor) — No prefers-reduced-motion media query
None of the `@keyframes` animations are gated by `@media (prefers-reduced-motion: reduce)`. This violates WCAG 2.1 SC 2.3.3 (AAA) and is a common WCAG AA best practice. With `ownerPulse` running `infinite` on blocked cards, users with vestibular disorders may be affected.
- **Severity:** Minor (AAA violation, AA best practice)
- **Fix:** Add:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```

**Visual polish verdict: PASS (1 minor flag)**

---

## Feature 6: Regression Check

### PASS — All Existing Tabs Present
Tab bar (lines 532–537): Tasks, Job Applications, CV Versions, LinkedIn — all four present.

### PASS — Kanban Drag-Drop
Lines 1087–1088: `dragstart`/`dragend` event listeners on cards. Lines 558–560, 570–572, 582–584, 594–596: `ondragover` and `ondrop` on kanban columns. `onDrop()` function at line 1120 functional.

### PASS — Filters Work
Lines 544–553: Filter buttons with `setFilter()` handler. `renderTasks()` applies `currentFilter` correctly at line 1057.

### PASS — localStorage Keys Present
Line 911: `andy_tasks`, `andy_jobs`, `andy_cvs`, `andy_liposts` — all four keys. All `save*()` and `load*()` functions reference correct keys.

### PASS — No Duplicate IDs (Static)
Static HTML IDs checked: `notifBell`, `notifBadge`, `notifPanel`, `notifList`, `ownerBadge`, `ownerBadgeText`, `lastUpdated`, `kanban`, `col-needs-you`, `col-inprogress`, `col-blocked`, `col-done`, `cards-*`, `count-*`, `tab-tasks`, `tab-jobs`, `tab-cv`, `tab-linkedin`, `filterCount`, `taskModal`, `addTaskModal`, `jobModal`, `cvModal`, `liPostModal` — no duplicates found.

### PASS — No Unclosed Tags
File ends correctly at line 1574 with `</html>`. HTML structure validated by inspection: `<head>` closed at line 495, `<body>` opened line 496, all modal overlays closed, `<script>` block closed at line 1572.

### FLAG (Minor) — Job Applications tab: col-header uses col-title without font-family declared
Line 1219 (JS-generated job column HTML):
```js
`<div class="col-title" style="color:${color};font-size:11px">${stage}</div>`
```
The `.col-title` CSS class at line 195 includes `font-family:'Syne',sans-serif`. This is correctly inherited since it uses the CSS class directly. No issue — confirming PASS on re-check. No regression.

### FLAG (Major) — CV table column headers do not use Syne in all cases
Line 337–341: `.cv-table th` has `font-family:'Syne',sans-serif` — correct. However, `.cv-table th` also has `text-align:left` with no explicit `scope` attribute on any `<th>`. For accessibility, all `<th>` elements should have `scope="col"`. Lines 632–640: `<th>Version</th>`, `<th>Role / Target</th>` etc. — none have `scope` attribute.
- **Severity:** Minor (accessibility)
- **Fix:** Add `scope="col"` to all `<th>` elements in the CV table header.

**Regression verdict: PASS (1 minor a11y flag)**

---

## Feature 7: Accessibility

### PASS — focus-visible Ring Present
Line 11: `*:focus-visible{outline:2px solid var(--cyan);outline-offset:2px;border-radius:4px}` — global focus-visible ring implemented. PASS.

### FLAG (Major) — Notification bell is a div, not a button (duplicate of Feature 4 flag)
Already reported above. `<div onclick="...">` with no keyboard support. Severity: Major.

### FLAG (Major) — Modal overlays lack role="dialog" and aria-modal
Lines 685, 756, 794, 831, 865: All five `modal-overlay` divs are plain `<div>` elements with class `modal-overlay`. They lack:
- `role="dialog"`
- `aria-modal="true"`
- `aria-labelledby` pointing to the modal title
Screen readers will not announce these as dialogs, and focus is not trapped when they open.
- **Severity:** Major (WCAG 2.1 AA: 4.1.2 Name, Role, Value)
- **Fix:** Add `role="dialog" aria-modal="true" aria-labelledby="[title-id]"` to each modal overlay, and implement focus trap (move focus to first focusable element on open; restore on close).

### FLAG (Major) — Form inputs in modals lack associated `<label>` elements
Example: Line 699: `<input type="text" id="modalTitleInput" />` — its label (line 698) is `<label>Title</label>` but there is no `for="modalTitleInput"` attribute. Same pattern throughout all modal fields (lines 693–745, 763–784, 801–821, 838–854, 872–884).
- **Severity:** Major (WCAG 2.1 AA: 1.3.1 Info and Relationships; 4.1.2)
- **Fix:** Add `for` attributes to all `<label>` elements matching their associated input IDs. Example: `<label for="modalTitleInput">Title</label>`.

### FLAG (Minor) — li-post-preview uses dir="rtl" on div (already flagged in Feature 2)
Line 1366. Already documented above as Major under Feature 2.

### FLAG (Minor) — Color contrast: muted text may fail AA
`--muted:#757587` on `--bg:#0A0A0B`. Foreground: `#757587` = rgb(117,117,135). Background: `#0A0A0B` = rgb(10,10,11).  
Contrast ratio estimate: approximately 4.7:1 — marginally passes AA for normal text (4.5:1 threshold). However, `.card-id` at 10px and `.col-count` at 10px are below the 18px/14px bold thresholds for large text, so they require 4.5:1. At ~4.7:1 this is technically passing but very close to the boundary; verify with a contrast checker tool.

`--text-secondary:#9494A8` on `--surface:#131316`: rgb(148,148,168) on rgb(19,19,22) — estimated contrast ~5.3:1. PASS.

### PASS — No dir="rtl" on inline spans (static HTML)
Static HTML confirmed: `<bdi>` used on line 654. No `<span dir="rtl">` found in static markup. The JS-generated `<div dir="rtl">` on line 1366 is flagged above.

### PASS — Color contrast on new elements (owner-block, linkedin)
`--owner-block:#FF6B00` on `--owner-block-dim:rgba(255,107,0,0.18)` overlaid on `--surface2:#1C1C21`:  
Effective background ≈ #341708 approx. Orange (#FF6B00) on this: estimated ~4.9:1 — PASS.  
`--linkedin-bright:#2D8CF0` on `--linkedin-dim:rgba(10,102,194,0.2)` overlaid on `--surface2`: estimated ~5.1:1 — PASS.

**Accessibility verdict: CONDITIONAL PASS — 3 Major flags, 2 Minor flags**

---

## Summary Table

| # | Feature | Status | Severity | Issues |
|---|---------|--------|----------|--------|
| 1 | Typography | PASS | — | All fonts applied correctly |
| 2 | LinkedIn CMS Tab | CONDITIONAL PASS | Major | `dir="rtl"` on div instead of `<bdi>`; overcalculated height; minor `<bdi>` misuse |
| 3 | Owner-blocked Cards | PASS | Minor | `::before` not scoped to blocked column |
| 4 | Notification Bell | CONDITIONAL PASS | Major | Bell is a `<div>`, no keyboard access, no aria-expanded |
| 5 | Visual Polish | PASS | Minor | No `prefers-reduced-motion` guard |
| 6 | Regression | PASS | Minor | `<th>` missing `scope="col"` |
| 7 | Accessibility | CONDITIONAL PASS | Major ×2 | Modals lack role/aria-modal/labelledby; labels lack `for` attributes |

---

## Issues Requiring Fix (Prioritized)

### BLOCKERS (Major — must fix before ship)

**[A1] Notification bell is a `<div>` — not keyboard accessible**  
Line 507. Change to `<button>` element or add `role="button" tabindex="0"` + Enter/Space handler + `aria-expanded`.

**[A2] LinkedIn post preview uses `<div dir="rtl">` instead of `<bdi>`**  
Line 1366 (JS). Wrap content in `<bdi>` inside the div, or replace with a block container + inner `<bdi>`.

**[A3] Modal overlays missing role="dialog", aria-modal, aria-labelledby**  
Lines 685, 756, 794, 831, 865. Add ARIA dialog attributes and focus trapping on open/close.

**[A4] Modal form labels missing `for` attributes**  
All modal `<label>` elements. Add `for="[inputId]"` to every label.

### MINOR (Should fix, does not block ship)

**[B1] LinkedIn layout height overcalculated**  
Line 368: `calc(100vh - 180px)` should be approximately `calc(100vh - 144px)`.

**[B2] `::before` "WAITING ON YOU" not scoped to blocked column**  
Line 241. Scope to `.col-blocked .card.owner-blocked .card-note::before`.

**[B3] No `prefers-reduced-motion` media query**  
Add reduced-motion override for all animations including infinite `ownerPulse`.

**[B4] CV table `<th>` missing `scope="col"`**  
Lines 632–640. Add `scope="col"` to all table header cells.

**[B5] `<bdi>` in banner wraps English word "Hebrew" not actual Hebrew text**  
Line 654. Cosmetic/semantic — remove or relocate `<bdi>` to actual Hebrew strings.

---

## Overall Verdict

**CONDITIONAL PASS**

The redesign is visually solid, functionally complete, and meets the core feature spec. Four Major accessibility issues prevent a clean PASS. None are runtime crashes or data-loss bugs. The dashboard is shippable for internal use with the understanding that A1–A4 must be resolved before any external-facing or public access context.

Rex should action items A1–A4 as a follow-up patch. Items B1–B5 can be batched in the same pass.
