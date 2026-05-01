# Accessibility Audit — WEBSITE-001-A11Y-01
**Standard:** WCAG 2.1 AA  
**Auditor:** Vera (QA & Visual Inspector)  
**Date:** 2026-04-30  
**Site:** https://inonbaasov-website.base44.app  
**Codebase:** `sites/website-product-portfolio/pages/Home.jsx`

---

## Executive Summary

The site is a dark-background, design-forward React portfolio built entirely with inline styles. While it achieves strong visual polish, it has significant accessibility gaps across multiple WCAG 2.1 AA success criteria. The most severe issues are: interactive elements implemented as non-semantic `<div>` or `<button>` elements without ARIA roles, a modal that lacks proper focus trap and ARIA attributes, form inputs that have visible labels but broken `for`/`id` associations, and pervasive color contrast failures due to low-opacity white text on a near-black background.

**Overall A11Y rating: FAIL (WCAG 2.1 AA)**  
**Critical:** 4 | **High:** 5 | **Medium:** 5 | **Low:** 4

---

## Critical Issues (WCAG AA failures — must fix)

### A11Y-CRIT-01: Modal Lacks ARIA Role, Focus Trap, and aria-modal
**File:** `pages/Home.jsx` lines 313–396  
**WCAG:** 4.1.2 Name, Role, Value (A); 2.1.2 No Keyboard Trap (A)  
**Severity:** Critical  
**Description:** The product case-study modal is a `<div>` with `position: fixed`. It has:
- No `role="dialog"` or `role="alertdialog"`
- No `aria-modal="true"`
- No `aria-labelledby` pointing to the modal title
- No focus trap — when the modal opens, keyboard focus stays behind it on the underlying page
- The only keyboard support is an Escape key listener (line 316) — but this only works if focus is somewhere reachable

Screen reader users will not know a modal has opened, cannot navigate its content, and cannot close it reliably. Keyboard users cannot Tab through the modal content without cycling back into the page behind it.  
**Fix:**
```jsx
<div role="dialog" aria-modal="true" aria-labelledby="modal-title" ...>
  // On mount, focus the first focusable element inside (Close button)
  // Implement focus trap: Tab/Shift+Tab cycle only within modal children
```
Add `id="modal-title"` to the product title heading inside the modal.

---

### A11Y-CRIT-02: Form Inputs Have Visible Labels But No Programmatic Association
**File:** `pages/Home.jsx` lines 424–451  
**WCAG:** 1.3.1 Info and Relationships (A); 4.1.2 Name, Role, Value (A)  
**Severity:** Critical  
**Description:** The contact form has three `<label>` elements ("NAME", "EMAIL", "MESSAGE") but none have `htmlFor` attributes. The corresponding inputs have no `id` attributes. This means screen readers cannot associate labels with inputs — AT users will hear "text field, required" with no indication of what the field is for.  
**Fix:**
```jsx
<label htmlFor="contact-name" ...>NAME</label>
<input id="contact-name" type="text" ... />

<label htmlFor="contact-email" ...>EMAIL</label>
<input id="contact-email" type="email" ... />

<label htmlFor="contact-message" ...>MESSAGE</label>
<textarea id="contact-message" ... />
```

---

### A11Y-CRIT-03: Navigation Buttons Have No Accessible Name for Screen Readers
**File:** `pages/Home.jsx` lines 506–521  
**WCAG:** 4.1.2 Name, Role, Value (A)  
**Severity:** Critical  
**Description:** The nav buttons ("About", "Work", "Story", "Contact", "Hire Me") use `<button>` elements — correct semantically — and their text content provides accessible names. However, the logo button (line 499) renders:
```jsx
<button ...><span style={{ color: "#0ea5e9" }}>I</span>B</button>
```
The accessible name of this button is "IB" — which is meaningless to a screen reader user. Similarly, the nav is not wrapped in a `<nav>` element, so it is not identified as a navigation landmark.  
**Fix:**
```jsx
<nav aria-label="Main navigation">
  <button aria-label="Go to top of page" ...>
    <span aria-hidden="true"><span>I</span>B</span>
  </button>
  ...
</nav>
```

---

### A11Y-CRIT-04: Product Cards Are Non-Semantic Click Targets
**File:** `pages/Home.jsx` lines 238–310  
**WCAG:** 4.1.2 Name, Role, Value (A); 2.1.1 Keyboard (A)  
**Severity:** Critical  
**Description:** Each product card is implemented as a `<div onClick={() => onOpen(p)}>`. While it has an `onClick` handler, it:
- Has no `role="button"` — screen readers will not announce it as interactive
- Has no `tabIndex={0}` — keyboard users cannot Tab to it
- Has no `onKeyDown` handler for Enter/Space — keyboard users cannot activate it even if they somehow focus it
- Has no `aria-label` describing what it opens

This means the primary interactive element of the portfolio is completely inaccessible to keyboard and screen reader users.  
**Fix:**
```jsx
<div
  role="button"
  tabIndex={0}
  aria-label={`Open case study: ${p.title}`}
  onClick={() => onOpen(p)}
  onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && onOpen(p)}
  ...
>
```
Alternatively, convert to a semantic `<button>` element.

---

## High Severity Issues

### A11Y-HIGH-01: Color Contrast Failures — Body Text on Dark Background
**File:** `pages/Home.jsx` multiple locations  
**WCAG:** 1.4.3 Contrast (Minimum) — AA requires 4.5:1 for normal text, 3:1 for large text  
**Severity:** High  
**Description:** The site uses `background: "#050c1a"` (approximately #050C1A, near-black). Many text colors are low-opacity white, which results in contrast ratios well below the 4.5:1 AA requirement:

| Text style | Approx hex on #050C1A | Contrast ratio | AA Pass? |
|---|---|---|---|
| `rgba(255,255,255,0.45)` | ~#8A8E95 | ~4.1:1 | FAIL (just under) |
| `rgba(255,255,255,0.42)` | ~#878B92 | ~3.9:1 | FAIL |
| `rgba(255,255,255,0.35)` | ~#797D84 | ~3.4:1 | FAIL |
| `rgba(255,255,255,0.28)` | ~#6A6E74 | ~2.8:1 | FAIL |
| `rgba(255,255,255,0.22)` | ~#5F6268 | ~2.4:1 | FAIL |
| `rgba(255,255,255,0.18)` | ~#575A60 | ~2.1:1 | FAIL |
| `rgba(255,255,255,0.14)` | ~#4E5157 | ~1.8:1 | FAIL |

The paragraph text in the hero (`rgba(255,255,255,0.42)`), About section (`rgba(255,255,255,0.45)`), and especially secondary text labels throughout the page fail contrast. Only `#fff` (1.0 opacity) on `#050c1a` passes comfortably at ~20:1.

Specific failing instances:
- Hero paragraph, Home.jsx:588 — `rgba(255,255,255,0.42)`
- Hero sub-paragraph, Home.jsx:592 — `rgba(255,255,255,0.22)`
- About body text, Home.jsx:691 — `rgba(255,255,255,0.45)` (borderline fail)
- About secondary text, Home.jsx:694 — `rgba(255,255,255,0.28)` (fail)
- Card tagline, Home.jsx:271 — `rgba(255,255,255,0.45)` (borderline)
- Card metric sublabels, Home.jsx:279 — `rgba(255,255,255,0.22)` (fail, also tiny font)
- Timeline desc, Home.jsx:799 — `rgba(255,255,255,0.58)` (~5.2:1 — PASS, barely)
- Footer copyright, Home.jsx:852 — `rgba(255,255,255,0.18)` (severe fail)

**Fix:** Increase opacity of body text to minimum `rgba(255,255,255,0.65)` (~5.8:1). For secondary/decorative text, use at least `rgba(255,255,255,0.45)` and prefer `0.60+`. Remove or de-emphasize decorative text that serves no informational purpose.

---

### A11Y-HIGH-02: Heading Hierarchy Incorrect — Multiple h2s, No h1 Sections
**File:** `pages/Home.jsx` lines 576, 688, 739, 764, 818  
**WCAG:** 1.3.1 Info and Relationships (A)  
**Severity:** High  
**Description:** The page has one `<h1>` (hero name, line 576). All subsequent section headings use `<h2>`. This is correct structurally. However, the section labels ("ABOUT ME", "MY WORK", "MY STORY", "GET IN TOUCH") are rendered as plain `<span>` elements (lines 683, 737, 762, 817) rather than headings. This means:
- Screen readers navigating by heading will find the `<h1>` and then immediately jump to the first `<h2>` within each section, missing the section label entirely
- The section labels are visually present but semantically invisible

Additionally, `DesignOptions.jsx` line 77 uses an `<h1>` but the rest of the design option labels are plain `<div>` elements.  
**Fix:** Either promote section labels to `<h2>` and demote the current `<h2>` section headings to `<h3>`, or wrap section labels with `<p>` and `aria-hidden="true"` if they are purely decorative.

---

### A11Y-HIGH-03: Interactive Elements Below 44px Touch Target
**File:** `pages/Home.jsx` lines 298–306, 499–503  
**WCAG:** 2.5.5 Target Size (AA in WCAG 2.2)  
**Severity:** High  
**Description:**
- Card arrow button: 30×30px (Home.jsx:298–306)
- Logo button: height constrained by `fontSize: 15` with no explicit padding — approximately 20px tall
- Chapter tab chapter-code labels (`fontSize: 9.5`) above tab buttons are information-bearing but not separately interactive

While WCAG 2.5.5 is technically WCAG 2.2 (and this audit is against 2.1 AA), touch target size of 44×44px minimum is Apple HIG and Google Material standard, and the spirit of 2.1 SC 2.5.5 (AAA).  
**Fix:** Minimum `min-height: 44px; min-width: 44px` for all interactive elements. The logo button needs explicit `padding: "12px 8px"` or similar.

---

### A11Y-HIGH-04: No Skip Navigation Link
**File:** `pages/Home.jsx` — not present  
**WCAG:** 2.4.1 Bypass Blocks (A)  
**Severity:** High  
**Description:** The page has a fixed navigation bar that appears before all content. There is no "Skip to main content" link. Keyboard users must Tab through all 5 nav items before reaching the page content on every page load. This is a WCAG Level A failure.  
**Fix:** Add a visually hidden skip link as the first focusable element:
```jsx
<a href="#hero" style={{
  position: 'absolute', top: '-40px', left: 0,
  background: '#0ea5e9', color: '#fff', padding: '8px',
  zIndex: 9999,
  ':focus': { top: 0 }  // must use onFocus/onBlur to toggle in React
}}>Skip to main content</a>
```

---

### A11Y-HIGH-05: External Links Missing rel="noreferrer" and No New-Tab Warning
**File:** `pages/Home.jsx` lines 698, 703, 826, 831, 854, 855; also Modal line 385  
**WCAG:** 3.2.2 On Input (A) — though primarily a security/UX concern  
**Severity:** High  
**Description:** Multiple `<a>` elements use `target="_blank"` (LinkedIn, live app links, CV download) with only `rel="noopener"` — missing `rel="noreferrer"`. More critically, none warn users that they will open a new tab. Screen reader users and cognitive-disability users may be confused when a new browser tab opens without warning.  
Additionally, the modal link (line 385) has `rel="noopener"` but missing `noreferrer`.  
**Fix:**
```jsx
rel="noopener noreferrer"
aria-label="View TradePulse live app (opens in new tab)"
```
Add `(opens in new tab)` to link text or aria-label for all `target="_blank"` links.

---

## Medium Severity Issues

### A11Y-MED-01: Images Missing Descriptive Alt Text (DesignOptions.jsx)
**File:** `pages/DesignOptions.jsx` lines 287, 431, 549  
**WCAG:** 1.1.1 Non-text Content (A)  
**Severity:** Medium  
**Description:** Multiple profile photo `<img>` elements in design preview components use `alt="Inon"` (line 287, 549) or `alt="Inon"` (line 431). While the main `Home.jsx` correctly uses `alt="Inon Baasov"` (line 622), the DesignOptions preview images use abbreviated alt text. If the DesignOptions page is accessible to users, these images lack meaningful descriptions.  
**Fix:** Use `alt="Inon Baasov, Product Leader and Co-Founder"` or similar descriptive text across all profile images, including preview components.

---

### A11Y-MED-02: Scroll Reveal Animations — No Reduced Motion Support
**File:** `pages/Home.jsx` lines 162–171  
**WCAG:** 2.3.3 Animation from Interactions (AAA, but best practice at AA)  
**Severity:** Medium  
**Description:** The `Reveal` component uses `IntersectionObserver` to trigger opacity/transform transitions. These cannot be disabled without JavaScript. The `@keyframes float` and `@keyframes pulse` CSS animations in the `<style>` block have no `@media (prefers-reduced-motion)` override.  
**Fix:**
```css
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
```
In the `Reveal` component:
```jsx
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
// If true, set opacity:1 and transform:none immediately without transition
```

---

### A11Y-MED-03: SkillBar Progress Bars Missing ARIA Role
**File:** `pages/Home.jsx` lines 203–220  
**WCAG:** 4.1.2 Name, Role, Value (A)  
**Severity:** Medium  
**Description:** The `SkillBar` component renders skill levels as visual progress bars using `<div>` elements. Screen readers will announce these as generic containers with no indication of their value. A user listening to the About section will hear nothing about the skill levels.  
**Fix:**
```jsx
<div role="progressbar" aria-valuenow={level} aria-valuemin={0} aria-valuemax={100} aria-label={`${label}: ${level}%`} ...>
```

---

### A11Y-MED-04: Emoji Used as Content Without Text Alternatives
**File:** `pages/Home.jsx` — multiple locations throughout  
**WCAG:** 1.1.1 Non-text Content (A)  
**Severity:** Medium  
**Description:** Emojis are used as meaningful content throughout the page (product icons "🎬", "📈", "👨‍👩‍👧", "🤖"; career chapter emojis "🔬", "⚗️", "📊", "🚀", "🎯"). Screen readers will read emoji descriptions verbatim ("Movie Camera emoji", "Chart Increasing emoji") which may be confusing or off-brand. Some emojis are in interactive elements (timeline tabs, step icons in modal).  
**Fix:** Wrap emoji in `<span aria-hidden="true">` when they are decorative or when adjacent text provides the same meaning. Where emoji carry unique meaning, add `aria-label` to the containing element.

---

### A11Y-MED-05: Focus Indicators Absent on Custom Button Styles
**File:** `pages/Home.jsx` lines 499–521 (nav buttons), 598–607 (hero CTAs), 454–465 (form submit)  
**WCAG:** 2.4.7 Focus Visible (AA)  
**Severity:** Medium  
**Description:** All `<button>` elements are styled with custom CSS via inline styles. None define a `:focus` or `:focus-visible` style. The browser default focus ring may be suppressed by the `background: none; border: none` base styles (which some browsers interpret as resetting focus styling). Keyboard users tabbing through the page will have no clear visual indicator of which element is focused.  
**Fix:** Add focus styles to the `<style>` block:
```css
button:focus-visible, a:focus-visible {
  outline: 2px solid #0ea5e9;
  outline-offset: 3px;
  border-radius: 4px;
}
```

---

## Low Severity Issues

### A11Y-LOW-01: Section Elements Missing Explicit aria-label
**File:** `pages/Home.jsx` lines 525, 678, 726, 757, 807  
**WCAG:** 2.4.6 Headings and Labels (AA)  
**Severity:** Low  
**Description:** The five `<section>` elements have `id` attributes ("hero", "about", "products", "timeline", "contact") but no `aria-label` or `aria-labelledby`. Screen readers that support landmark navigation will announce them as generic "region" landmarks without names.  
**Fix:**
```jsx
<section id="about" aria-label="About Inon Baasov" ...>
<section id="products" aria-label="Products and case studies" ...>
```

---

### A11Y-LOW-02: Language Attribute Not Set in Codebase
**File:** Platform-level concern (no `index.html` in repo)  
**WCAG:** 3.1.1 Language of Page (A)  
**Severity:** Low  
**Description:** WCAG SC 3.1.1 requires the primary language of the page to be set in the `<html lang="...">` attribute. No HTML file is present in this repo to verify this. On the Base44 platform, the default `lang` may or may not be set to "en".  
**Fix:** Confirm Base44 injects `<html lang="en">` into the page shell. If not, request the platform team add it.

---

### A11Y-LOW-03: Contact Form Submit Redirects to Mail Client — No Warning
**File:** `pages/Home.jsx` lines 403–409  
**WCAG:** 3.2.2 On Input (A)  
**Severity:** Low  
**Description:** Submitting the contact form triggers `window.location.href = "mailto:..."`, which opens the user's email client. There is no advance warning to users (especially screen reader users) that form submission will launch an external application. The only feedback is the button text changing to "Opening your mail client..." after submission.  
**Fix:** Add helper text below the form: `<p>Submitting this form will open your email client to send a message.</p>`. Alternatively, use a backend form handler (Formspree, EmailJS) that submits without leaving the page.

---

### A11Y-LOW-04: Counter Animation Announces Updates to Screen Readers
**File:** `pages/Home.jsx` lines 174–201  
**WCAG:** 4.1.3 Status Messages (AA)  
**Severity:** Low  
**Description:** The `Counter` component rapidly updates a displayed number from 0 to the target value over ~1.1 seconds with 38 steps. Each state update causes a DOM re-render. Screen readers with live region detection may announce each intermediate value ("$0.07M", "$0.13M"... "$2.5M"), creating an extremely disruptive experience for AT users.  
**Fix:** Wrap the counter display in `<span aria-live="off">` during animation and switch to `aria-live="polite"` only after the animation completes, announcing only the final value. Or use `aria-label` set once to the final value, with the animated display being `aria-hidden="true"`.

---

## Summary Table

| ID | Issue | WCAG SC | Severity | File:Line |
|----|-------|---------|----------|-----------|
| A11Y-CRIT-01 | Modal lacks role/focus trap/aria | 4.1.2, 2.1.2 | Critical | Home.jsx:313 |
| A11Y-CRIT-02 | Form labels not associated with inputs | 1.3.1, 4.1.2 | Critical | Home.jsx:424 |
| A11Y-CRIT-03 | Nav landmark + logo button unnamed | 4.1.2 | Critical | Home.jsx:499 |
| A11Y-CRIT-04 | Product cards non-semantic, not keyboard accessible | 4.1.2, 2.1.1 | Critical | Home.jsx:238 |
| A11Y-HIGH-01 | Color contrast failures — multiple text elements | 1.4.3 | High | Home.jsx:multiple |
| A11Y-HIGH-02 | Heading hierarchy — section labels not headings | 1.3.1 | High | Home.jsx:683+ |
| A11Y-HIGH-03 | Touch targets below 44px | 2.5.5 | High | Home.jsx:298 |
| A11Y-HIGH-04 | No skip navigation link | 2.4.1 | High | Not present |
| A11Y-HIGH-05 | External links no new-tab warning, missing noreferrer | 3.2.2 | High | Home.jsx:698+ |
| A11Y-MED-01 | Design preview images abbreviated alt text | 1.1.1 | Medium | DesignOptions.jsx:287 |
| A11Y-MED-02 | No prefers-reduced-motion support | 2.3.3 | Medium | Home.jsx:162 |
| A11Y-MED-03 | Skill bars missing progressbar ARIA role | 4.1.2 | Medium | Home.jsx:203 |
| A11Y-MED-04 | Emojis not wrapped in aria-hidden | 1.1.1 | Medium | Home.jsx:multiple |
| A11Y-MED-05 | Focus indicators absent on custom buttons | 2.4.7 | Medium | Home.jsx:499+ |
| A11Y-LOW-01 | Sections missing aria-label | 2.4.6 | Low | Home.jsx:525+ |
| A11Y-LOW-02 | lang attribute not confirmed in platform shell | 3.1.1 | Low | Platform-level |
| A11Y-LOW-03 | Form submit launches mail client without warning | 3.2.2 | Low | Home.jsx:403 |
| A11Y-LOW-04 | Counter animation disruptive to screen readers | 4.1.3 | Low | Home.jsx:174 |

---

## Recommended Fix Priority

1. A11Y-CRIT-02 — Form label associations (5-minute fix, high impact)
2. A11Y-CRIT-04 — Card keyboard accessibility (role, tabIndex, onKeyDown)
3. A11Y-CRIT-03 — Nav landmark + logo aria-label
4. A11Y-CRIT-01 — Modal focus trap and ARIA role (most complex, requires engineering)
5. A11Y-MED-05 — Focus indicators via CSS (quick win, high visibility)
6. A11Y-HIGH-04 — Skip navigation link (simple, Level A requirement)
7. A11Y-HIGH-01 — Color contrast (requires design review — may affect visual design)
8. A11Y-HIGH-05 — External link warnings (quick win)
9. A11Y-MED-03 — SkillBar progressbar role (quick win)
10. A11Y-MED-04 — Emoji aria-hidden (quick win)
11. Remaining HIGH/MED/LOW items

**Verdict: DO NOT APPROVE for WCAG 2.1 AA compliance. Four Critical items are Level A failures — the minimum required conformance level. The site currently fails WCAG 2.1 Level A.**

---
*Vera — QA & Visual Inspector | Task WEBSITE-001-A11Y-01*
