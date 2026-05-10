# QA Report — Rex Dashboard: 3 New Features
**Auditor:** Vera  
**Date:** 2026-05-08  
**File audited:** `dashboard/index.html`  
**Scope:** LinkedIn Hebrew Rule Badge, Owner-Blocker Highlighting, Notification Bell + general regression check

---

## Feature 1: LinkedIn Hebrew Rule Badge (`.linkedin-rule-badge`)

**Status: FLAG**

### Findings

**1a. RTL direction applied at wrong level — FLAG (Minor)**
- Line 1642: `<span>LinkedIn: <span dir="rtl">עברית בלבד</span></span>`
- The `dir="rtl"` is applied to an inner `<span>` containing only the Hebrew text. Because Hebrew characters are inherently RTL (Unicode Bidirectional Algorithm handles them), the isolated `dir="rtl"` on that inner span has no practical effect — and it mixes bidi contexts in the middle of an LTR sentence, which is technically incorrect.
- The outer badge element itself has no `dir` attribute. For mixed-content correctness, the Hebrew portion should use a `<bdi>` element instead, or the badge should declare `dir="auto"` on the outer container.

**Recommended fix:**
```html
<div class="linkedin-rule-badge" title="Team rule: LinkedIn posts must be in Hebrew only">
  <span class="li-icon">in</span>
  <span>LinkedIn: <bdi>עברית בלבד</bdi></span>
</div>
```
Or apply `dir="auto"` to the outer `.linkedin-rule-badge` div.

**1b. Contrast — PASS**
- Badge color: `#818CF8` (indigo-400) on `rgba(99,102,241,0.12)` background which resolves to approximately `#161621` composite. Approximate contrast ratio: ~5.0:1 for 12px/600w text. Passes WCAG AA (4.5:1 for normal text).

**1c. Topbar layout — PASS**
- `.linkedin-rule-badge` has `flex-shrink: 0` and `white-space: nowrap` (line 169). It is placed between `.topbar-divider` and `.topbar-spacer` (lines 1639–1644), so the spacer absorbs available space and pushes right-side elements left. Layout will not break on desktop. On mobile (640px and below), the topbar uses `padding: 0 12px` but no `flex-wrap`, meaning all badges stay on one row — if many badges are present simultaneously (logo + LinkedIn badge + needs-you badge + bell + updated-timestamp), this could crowd at narrow widths. However at the current item count this is a cosmetic risk, not a blocker.

**1d. Tooltip — PASS**
- Line 1640: `title="Team rule: LinkedIn posts must be in Hebrew only"` — native browser tooltip is present and syntactically correct.

---

## Feature 2: Owner-Blocker Highlighting (`.card.owner-blocked`)

**Status: PASS with NOTE**

### Findings

**2a. `makeCard()` class and tag application — PASS**
- Lines 2073–2074:
  ```js
  const ownerClass = col === 'needs-you' ? ' owner-blocked' : '';
  const ownerTags  = ownerBlockerTagsHtml(task, col);
  ```
- Line 2076: `class="card${ownerClass}"` — class is conditionally applied correctly for `needs-you` column only.
- `ownerBlockerTagsHtml` (line 2049) also guards on `col !== 'needs-you'` and returns `''` for other columns. Double guard is redundant but harmless.

**2b. `ownerBlockedDays()` null/missing date handling — PASS**
- Lines 2040–2047:
  ```js
  const raw = task.updated_at || task.since || task.blocked_since || null;
  if (!raw) return null;
  const d = new Date(raw);
  if (isNaN(d)) return null;
  ```
- All null/undefined/missing date fields are handled. Invalid date strings produce `NaN` and are caught. No crash path exists.

**2c. Overdue logic (>3 days) — PASS**
- Line 2053: `const overdue = days !== null && days > 3;`
- Logic is correct: null-safe guard comes first, then threshold comparison. Strictly greater-than-3 (so day 4+ triggers overdue).

**2d. HTML entities in tags — NOTE (Cosmetic)**
- Line 2055: `&#x23F3; Waiting on you` — hourglass emoji via HTML entity. Renders correctly in modern browsers. 
- Line 2056: `&#x1F534; Overdue (${days}d)` — red circle emoji via HTML entity. Both are fine.

**2e. CSS — PASS**
- `.card.owner-blocked` rule (line 228–230) uses `!important` to override the priority border-left color with `var(--col-needs-you)` (orange). The `!important` is required here because the priority data-attribute rules (lines 468–472) are more specific. Usage is justified; no conflict introduced.

---

## Feature 3: Notification Bell (`.notif-bell`)

**Status: FLAG**

### Findings

**3a. Bell count reads from task data on render — PASS**
- Lines 2138–2142 (inside `render()`):
  ```js
  const notifCountEl = document.getElementById('notif-count');
  if (notifCountEl) {
    notifCountEl.textContent = nyCount;
    notifCountEl.className = 'notif-count ' + (nyCount > 0 ? 'has-items' : 'no-items');
  }
  ```
- `nyCount` is derived from `buckets['needs-you'].length` (line 2128). Count is set on every `render()` call, including `renderFromMemory()` re-renders. Correct.

**3b. Red/grey toggle logic — PASS**
- `has-items` → `background: var(--red-bright)` (line 218), `no-items` → `background: var(--grey)` (line 222). Logic correctly switches between the two states. Initial state on HTML is `no-items` (line 1652) — correct default before data loads.

**3c. Bell click handler — PASS for scroll, FLAG for early-execution risk**
- Lines 2418–2433: The click handler is attached via `document.getElementById('notif-bell').addEventListener(...)` at script parse time (not inside `DOMContentLoaded` or after `loadTasks()`).
- The element exists in static HTML (line 1650) so `getElementById` will not return null at parse time. PASS on null-reference risk.
- However: the handler references `document.querySelector('#cards-needs-you .card:not(.hidden)')`. If the bell is clicked before `loadTasks()` resolves (i.e., during loading), this selector returns `null` and the handler silently does nothing. This is acceptable graceful degradation, but there is no visual feedback (e.g., no toast or tooltip saying "No tasks loaded yet"). FLAG as Minor UX gap.

**3d. Tab switch before scroll — PASS**
- Lines 2419–2423 correctly check whether the Tasks tab is active and call `.click()` to switch if not. This is safe because tab switching is synchronous DOM manipulation.

**3e. Missing `aria-live` on badge count — FLAG (Accessibility / Minor)**
- The `.notif-count` badge updates dynamically (line 2140) but has no `aria-live` attribute. Screen reader users will not be notified when the count changes.
- **Recommended fix:** Add `aria-live="polite"` and `aria-atomic="true"` to the `#notif-count` span on line 1652:
  ```html
  <span class="notif-count no-items" id="notif-count" aria-live="polite" aria-atomic="true">0</span>
  ```

---

## Regression Check — Existing Functionality

### Tabs — PASS
- Tab switching logic (lines 2531–2538) uses `querySelectorAll` and `data-tab` attributes. No new code touches tab state. The new features do not use any `tab-btn` or `tab-content` class names. Safe.

### Filters — PASS
- Filter logic reads `.card` elements and `data-project` attributes (lines 2177–2195). `makeCard()` still emits `data-project` correctly (line 2076). No regression.

### Kanban drag/drop (Jobs board) — PASS
- Job drag/drop uses `.job-card` and `.job-cards` selectors exclusively (lines 2633–2655). The new features use `.card` and `.card-owner-tags` — no namespace collision.

### localStorage — PASS
- New features do not touch `cc_job_applications` or `cc_cv_versions` keys. The `render()` function does not write to localStorage. Safe.

### CSS conflicts — PASS with NOTE
- No class name collisions detected between new styles (`.linkedin-rule-badge`, `.notif-bell`, `.notif-count`, `.card.owner-blocked`, `.card-owner-tags`, `.owner-tag`) and pre-existing selectors.
- Note: `.last-updated` style (lines 263–267) was added alongside the new features and is referenced in the topbar HTML (line 1654). It was not in the pre-existing code base — this appears to be part of Rex's additions. It is a cosmetic element and does not conflict.

### HTML validity — PASS with NOTE
- No unclosed tags detected in the new additions.
- No duplicate IDs introduced. `notif-bell`, `notif-count` are unique. `needs-you-counter` and `needs-you-count` pre-existed and are untouched.
- One structural note: `<span dir="rtl">` inside a `<span>` inside a `<div>` — valid HTML but semantically suboptimal (flagged under Feature 1 above).

---

## Summary Table

| Feature | Status | Severity |
|---|---|---|
| LinkedIn Hebrew Rule Badge — layout | PASS | — |
| LinkedIn Hebrew Rule Badge — `dir="rtl"` scope | FLAG | Minor |
| LinkedIn Hebrew Rule Badge — contrast | PASS | — |
| LinkedIn Hebrew Rule Badge — tooltip | PASS | — |
| Owner-Blocker class + tags in `makeCard()` | PASS | — |
| `ownerBlockedDays()` null safety | PASS | — |
| Overdue >3 days logic | PASS | — |
| Bell count from task data | PASS | — |
| Bell red/grey toggle | PASS | — |
| Bell click scroll + tab switch | PASS | — |
| Bell count `aria-live` missing | FLAG | Minor (Accessibility) |
| Bell click before data loads (silent no-op) | FLAG | Minor (UX) |
| Tabs regression | PASS | — |
| Filters regression | PASS | — |
| Drag/drop regression | PASS | — |
| localStorage regression | PASS | — |
| CSS conflicts | PASS | — |
| HTML validity | PASS | — |

---

## Required Fixes Before Sign-off

1. **LINE 1642** — Replace `<span dir="rtl">עברית בלבד</span>` with `<bdi>עברית בלבד</bdi>` to correctly isolate bidi context.
2. **LINE 1652** — Add `aria-live="polite" aria-atomic="true"` to `#notif-count` span for screen reader support.

Both are Minor changes. No Blocker or Major issues found. Existing functionality is unaffected.

**QA verdict: CONDITIONAL PASS — resolve 2 minor flags, then approved for production.**
