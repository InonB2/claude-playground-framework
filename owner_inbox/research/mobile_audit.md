# Mobile Responsiveness Audit — WEBSITE-001-PERF-01
**Auditor:** Vera (QA & Visual Inspector)  
**Date:** 2026-04-30  
**Site:** https://inonbaasov-website.base44.app  
**Codebase:** `sites/website-product-portfolio/pages/Home.jsx`  
**Viewports tested (via code inspection):** 375px · 768px · 1280px

---

## Executive Summary

The site is built entirely with inline React styles — no Tailwind, no external CSS framework. This means every responsive breakpoint must be handled manually through JavaScript or media queries. **Neither is present.** The page has zero CSS media queries and no responsive JavaScript logic. This results in a collection of critical layout failures on mobile (375px) that would render the site unusable on phones.

**Overall mobile rating: FAIL**  
**Blockers:** 5 | **High:** 5 | **Medium:** 4 | **Low:** 3

---

## Critical Issues (Blockers — must fix before launch)

### CRIT-01: No Viewport Meta Tag in Codebase
**File:** `pages/Home.jsx` — no `<head>` HTML present in the repo  
**Severity:** Blocker  
**Description:** The site is a Base44-deployed React app. No `index.html` or equivalent is present in this repo, so there is no way to verify that `<meta name="viewport" content="width=device-width, initial-scale=1">` is set. If the Base44 host does not inject this automatically, the page will render at desktop zoom on mobile, making all text microscopic and the page unusable.  
**Fix:** Confirm Base44 injects the viewport meta tag. If not, add it to the platform's HTML shell. This is the single most critical mobile fix possible.

---

### CRIT-02: Hero Two-Column Grid Breaks at 375px
**File:** `pages/Home.jsx` line 553  
**Code:** `gridTemplateColumns: "1fr auto"`  
**Severity:** Blocker  
**Description:** The hero section uses a two-column grid with text on the left and a 210px circular photo on the right. At 375px viewport, `1fr auto` will still try to place both columns side by side. With 5% padding on each side, the usable width is ~337px. The photo is fixed at 210px, leaving only ~127px for the name, tagline, status badge, and CTAs — causing severe text truncation, overflow, and probable horizontal scroll.  
**Fix:** Add a responsive breakpoint. Below 640px, switch to `gridTemplateColumns: "1fr"` and stack the photo above or below the text. Example: use a JS state check against `window.innerWidth` or a CSS media query injected via the `<style>` block.

---

### CRIT-03: Contact Form Two-Column Grid Collapses at 375px
**File:** `pages/Home.jsx` line 422  
**Code:** `gridTemplateColumns: "1fr 1fr"`  
**Severity:** Blocker  
**Description:** The Name and Email fields sit in a fixed two-column grid. At 375px, each column is approximately 150px wide. The input padding is 16px each side, leaving only ~118px of usable width per field. The placeholder text "your@email.com" will clip. Combined with the label text above, this creates a cramped, unusable form at mobile width.  
**Fix:** Below 480px, collapse to `gridTemplateColumns: "1fr"` so Name and Email stack vertically. This is a standard mobile form pattern.

---

### CRIT-04: Stats Bar Four-Column Grid Not Responsive
**File:** `pages/Home.jsx` lines 654–673  
**Code:** `gridTemplateColumns: "repeat(4,1fr)"`  
**Severity:** Blocker  
**Description:** The hero stats bar (`$2.5M / 38% / 99.99% / 10+ Years`) uses a rigid 4-column layout. At 375px, each column is approximately 84px wide. The `Counter` component renders values like "99.99%" at `clamp(20px,2.8vw,32px)` — which at 375px evaluates to ~20px. The values will fit but the label text at `fontSize: 9` with `letterSpacing: 2` risks clipping on narrow columns.  
**Fix:** At 375px, switch to `gridTemplateColumns: "repeat(2,1fr)"` (2x2 layout) or use `repeat(auto-fit,minmax(80px,1fr))`.

---

### CRIT-05: Modal Metrics Grid Not Responsive
**File:** `pages/Home.jsx` line 348  
**Code:** `gridTemplateColumns: "repeat(4,1fr)"`  
**Severity:** Blocker  
**Description:** The product case-study modal uses a 4-column metrics grid identical to the hero stats bar. At 375px the modal has `padding: "28px 20px"` leaving ~295px usable width. Each of four columns is ~74px. Metric values ("99.99%", "$2.5M") at `fontSize: 18` will overflow their columns.  
**Fix:** Collapse to `repeat(2,1fr)` on small screens, or `repeat(auto-fit,minmax(70px,1fr))`.

---

## High Severity Issues

### HIGH-01: Navigation Has No Mobile Hamburger Menu
**File:** `pages/Home.jsx` lines 505–521  
**Severity:** High  
**Description:** The nav bar renders 4 text links ("About", "Work", "Story", "Contact") plus a "Hire Me" CTA button in a horizontal row. At 375px with 5% padding (18px each side), the usable nav width is ~339px. The five items at their font sizes will overflow or wrap in unpredictable ways. There is no hamburger/drawer pattern implemented.  
**Fix:** Add a mobile nav that hides the text links and shows a hamburger toggle below ~640px. This is expected behavior on all professional portfolio sites.

---

### HIGH-02: About Section Two-Column Grid Not Responsive
**File:** `pages/Home.jsx` line 686  
**Code:** `gridTemplateColumns: "1fr 1fr"`  
**Severity:** High  
**Description:** The About section uses a fixed two-column grid (text + skill bars). At 375px, each column is ~168px. The paragraph text at `fontSize: 14.5` and `lineHeight: 1.9` will be readable but extremely narrow (168px), resulting in very long text columns with poor readability. The skill bar labels are already small at `fontSize: 12`.  
**Fix:** Below 768px, collapse to single column with the heading/text first, skill bars below.

---

### HIGH-03: Hero Floating Badges Overflow Viewport
**File:** `pages/Home.jsx` lines 627–647  
**Code:** `position: "absolute", left: -24` and `right: -28`  
**Severity:** High  
**Description:** The "$2.5M Raised" badge is positioned `left: -24px` relative to the photo container, and the "10+ yrs PM" badge is at `right: -28px`. At mobile viewports where the photo is already pushed against the edge of its column, these negatively-positioned badges will bleed outside the viewport boundary and trigger horizontal scroll — one of the most visible mobile UX failures.  
**Fix:** Either remove floating badges on mobile, or reposition them to stay within the viewport (e.g., `left: 0`, `bottom: -8px`).

---

### HIGH-04: Product Cards Grid Minimum Width Too Large for Some Phones
**File:** `pages/Home.jsx` line 746  
**Code:** `gridTemplateColumns: "repeat(auto-fill,minmax(272px,1fr))"`  
**Severity:** High  
**Description:** `minmax(272px,1fr)` means at any viewport narrower than 272px + padding, the grid forces a single column. At 375px with ~34px total padding, the usable width is ~341px, so cards should stack to one column. This is technically functional, but the cards have `padding: "24px 22px 20px"` and the internal 4-column metrics mini-grid (`repeat(4,1fr)`) is only ~297px wide — tight but workable. The card will single-column correctly. This is high priority only because the inner 4-column metric grid within each card (line 272) will be ~297px / 4 = ~74px per metric cell, which is very tight for the metric values.  
**Fix:** Inside the card's metrics grid, use `repeat(2,1fr)` below 400px width, or reduce font sizes further.

---

### HIGH-05: Timeline Chapter Tabs — Minimum Width Creates Scroll Before Content
**File:** `pages/Home.jsx` line 769  
**Code:** `overflowX: "auto"`, buttons with `minWidth: 72`  
**Severity:** High  
**Description:** Five chapter tabs with `minWidth: 72` requires at least 360px. At 375px this is technically feasible (5 × 72 = 360px + padding), but any additional tab content or padding pushes it into horizontal scroll territory. The tab buttons have no accessible touch target sizing (see also A11Y audit).  
**Fix:** Reduce `minWidth` to 60px at mobile, or let tabs scroll natively (already does with `overflowX: auto`). Confirm touch targets are at least 44px tall — currently `padding: "14px 10px"` makes them 48px+ tall which is acceptable.

---

## Medium Severity Issues

### MED-01: No prefers-reduced-motion Support for Animations
**File:** `pages/Home.jsx` lines 164–171 (Reveal), lines 863–865 (`@keyframes float` and `@keyframes pulse`)  
**Severity:** Medium  
**Description:** The `Reveal` component applies CSS transitions via inline styles (opacity + transform, .7s duration). The `float` and `pulse` keyframe animations run indefinitely. None of these check `prefers-reduced-motion`. For users with vestibular disorders, persistent motion and scroll-triggered animations can cause discomfort. This is also a WCAG 2.1 AA requirement (SC 2.3.3, AAA) but is best practice at AA level.  
**Fix:** Add `@media (prefers-reduced-motion: reduce)` to the `<style>` block setting `animation: none !important` and `transition: none !important`. Alternatively, check `window.matchMedia('(prefers-reduced-motion: reduce)')` in the Reveal hook and skip transforms when true.

---

### MED-02: Hardcoded Photo Size Does Not Scale Below 375px
**File:** `pages/Home.jsx` lines 617–624  
**Code:** `width: 210, height: 210` (pixels, unitless — treated as px in inline styles)  
**Severity:** Medium  
**Description:** The profile photo circle is hardcoded at 210px. On very small screens (320px — old iPhones, Galaxy A series) or when the hero grid correctly collapses, the 210px image may still be too large for the available single-column width. Using `vw`-relative sizing would be safer.  
**Fix:** Replace fixed `210` with a responsive value such as `Math.min(210, windowWidth * 0.55)` driven by a resize listener, or use CSS like `width: min(210px, 55vw)` via a class.

---

### MED-03: Footer Three-Item Flex Layout Wraps Poorly
**File:** `pages/Home.jsx` lines 847–859  
**Code:** `display: "flex", justifyContent: "space-between", flexWrap: "wrap"`  
**Severity:** Medium  
**Description:** The footer has three flex children (logo, copyright, links). `flexWrap: "wrap"` allows wrapping but `justifyContent: "space-between"` will create awkward spacing when items wrap to two lines. At 375px, "INON BAASOV" + the copyright line + the two product links will likely produce a 2-row layout with the copyright line alone on the second row, left-aligned. Visually inconsistent.  
**Fix:** On mobile, set `flexDirection: "column"` and `alignItems: "center"` with appropriate margin between items.

---

### MED-04: Font Sizes Below 10px — Unreadable on Mobile
**File:** `pages/Home.jsx` multiple locations  
**Severity:** Medium  
**Description:** Several text elements use extremely small font sizes:
- Counter label: `fontSize: 9` (line 198)
- Tag component: `fontSize: 9` (line 229)
- Metric sublabels in cards: `fontSize: 8.5` (line 279)
- Tech stack tags: `fontSize: 9.5` (line 286)
- Modal metric sublabels: `fontSize: 9` (line 355)
- Various letter-spaced labels: `fontSize: 10` across multiple locations

Sub-10px text is unreadable on mobile without zoom. WCAG SC 1.4.4 requires text to be resizable up to 200% without loss of content — but starting at 8.5px means even with browser zoom, legibility is poor.  
**Fix:** Set a minimum font-size floor of 11px for any visible text. Replace fixed tiny sizes with `clamp()` or responsive rem values.

---

## Low Severity Issues

### LOW-01: Touch Target Arrow Button in Cards Is 30px (Below 44px Minimum)
**File:** `pages/Home.jsx` lines 298–306  
**Code:** `width: 30, height: 30, borderRadius: "50%"`  
**Severity:** Low (combined with A11Y-HIGH-03)  
**Description:** The circular arrow icon in each card footer is 30×30px, below Apple's 44pt and Google's 48dp minimum touch target guidelines.  
**Fix:** Increase to at least 44×44px, or ensure the entire card itself is the click target (which it is via `onClick={() => onOpen(p)}` on the card div), making this less critical. Still, the visual button should match the tap zone.

---

### LOW-02: Scroll-Linked Parallax May Cause Jank on Low-End Devices
**File:** `pages/Home.jsx` lines 530–549  
**Code:** Background blobs with `transform: translateY(${scrollY * 0.05}px)` and grid opacity driven by `scrollY`  
**Severity:** Low  
**Description:** The `useScrollY` hook fires on every scroll event without throttling or `requestAnimationFrame`. On low-end Android phones this can cause scroll jank. The blob parallax and grid opacity changes are computed on every scroll tick.  
**Fix:** Wrap the scroll handler in `requestAnimationFrame` or use `throttle`. Alternatively, use CSS `transform` with GPU-composited layers via `will-change: transform` on the parallax elements.

---

### LOW-03: No Explicit overflow-x: hidden on Body/Root
**File:** `pages/Home.jsx` line 484  
**Code:** `overflowX: "hidden"` is set on the root div  
**Severity:** Low  
**Description:** `overflowX: "hidden"` is set on the main div, not on `body` or `html`. The floating badges (CRIT-05) and any other elements absolutely positioned outside this div could still cause `document.body` to scroll horizontally. On some mobile browsers, the overflow is not fully contained.  
**Fix:** Also set `overflow-x: hidden` on `body` and `html` via the `<style>` block already present in the component.

---

## Summary Table

| ID | Issue | Severity | File:Line |
|----|-------|----------|-----------|
| CRIT-01 | No confirmed viewport meta tag | Blocker | Platform-level |
| CRIT-02 | Hero 2-col grid breaks at 375px | Blocker | Home.jsx:553 |
| CRIT-03 | Contact form 2-col grid breaks at 375px | Blocker | Home.jsx:422 |
| CRIT-04 | Stats bar 4-col grid not responsive | Blocker | Home.jsx:654 |
| CRIT-05 | Modal metrics 4-col grid not responsive | Blocker | Home.jsx:348 |
| HIGH-01 | No mobile hamburger nav | High | Home.jsx:505 |
| HIGH-02 | About section 2-col grid not responsive | High | Home.jsx:686 |
| HIGH-03 | Hero floating badges overflow viewport | High | Home.jsx:627 |
| HIGH-04 | Product card inner metrics grid too tight | High | Home.jsx:272 |
| HIGH-05 | Timeline tabs tight at 375px | High | Home.jsx:769 |
| MED-01 | No prefers-reduced-motion support | Medium | Home.jsx:164, 863 |
| MED-02 | Photo hardcoded at 210px | Medium | Home.jsx:617 |
| MED-03 | Footer flex wraps awkwardly | Medium | Home.jsx:847 |
| MED-04 | Sub-10px font sizes on mobile | Medium | Multiple |
| LOW-01 | Card arrow button 30px (below 44px) | Low | Home.jsx:298 |
| LOW-02 | Scroll parallax no RAF throttle | Low | Home.jsx:154 |
| LOW-03 | overflow-x not set on body/html | Low | Home.jsx:484 |

---

## Recommended Fix Priority

1. CRIT-01 — Confirm viewport meta tag with Base44 platform team
2. CRIT-02, CRIT-03, CRIT-04, CRIT-05 — All grid layout fixes (can batch in one pass)
3. HIGH-01 — Mobile nav hamburger menu
4. HIGH-02, HIGH-03 — About grid + floating badge overflow
5. MED-01 — prefers-reduced-motion (quick win, high impact)
6. MED-04 — Font size floor (quick win)
7. Remaining HIGH/MED/LOW items in order

**Verdict: DO NOT APPROVE for mobile production. Fix all Blocker and High items before launch.**

---
*Vera — QA & Visual Inspector | Task WEBSITE-001-PERF-01*
