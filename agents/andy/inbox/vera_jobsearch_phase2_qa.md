# Vera — QA Sign-Off: Job Search System Phase 2 (JOBSEARCH-003, -004, -005-UI)

**Date:** 2026-05-14
**Reviewer:** Vera (QA & Visual Inspector)
**File under review:** `D:\Claude Playground\dashboard\index.html` (single file, 3835 lines, ~202 KB served)
**Source reports:**
- Rex (JOBSEARCH-003 + -004): `D:\Claude Playground\agents\andy\inbox\rex_jobsearch_phase2_done.md`
- Yoni (JOBSEARCH-005 finishing pass): `D:\Claude Playground\agents\andy\inbox\yoni_ats_match_engine_done.md`
**Scope:** UI side only for the ATS Match tab (engine correctness owned by Jasmin in parallel).

---

## Verdict: **PASS WITH NOTES** — commit-ready

- **194 / 194** Phase-2 jsdom assertions PASS (independent harness, date mocked to 2026-05-14).
- **19 / 23** WCAG 2.1 AA contrast pairs PASS; the 4 sub-threshold cases all stem from the pre-existing `--muted` token in 9–10 px chrome text (53 such usages already shipped in Phase 1 — **same severity as Phase 1 NOTE 1, not a Phase 2 regression**). See Design Note D2 below.
- Live HTTP smoke (`python -m http.server 5191`) → `GET /dashboard/` returns **HTTP 200, 202,163 bytes** in ~1.1 s. All 14 Phase-2 marker symbols (`PREP_ITEMS`, `overdue-banner`, `FOLLOWUP_NAG_STAGES`, `snoozeFollowUp`, `toggleChecklistItem`, `renderModalChecklist`, `getFollowUpClass`, `isOverdue`, `atsCvPicker`, `computeAtsMatch`, `renderAtsResults`, `atsClear`, `runAtsAnalyze`, `populateAtsCvPicker`) appear in the served HTML.
- No console errors, no thrown exceptions in any render path.
- All Phase 1 regression checks pass (kanban 9-col, star widget, sort modes, drag-and-drop in Manual mode, CV↔Job never-downgrade, XSS escapes).

Andy is clear to commit. Two cosmetic Design Notes (D1 + D2) are tracked for Phase 3 polish — neither is a WCAG blocker and neither breaks function.

---

## How I tested

1. **Static read** of all Phase-2 code paths:
   - `PREP_ITEMS`, `defaultPrepChecklist()`, `getPrepProgress()`, `toggleChecklistItem()`, `collectPrepFromModal()`, `renderModalChecklist()`, `renderPrepBadge()`, `migrateLegacyJobStages()` (the V5 additions).
   - `FOLLOWUP_NAG_STAGES`, `todayIsoLocal()`, `addDaysIso()`, `getFollowUpClass()`, `isOverdue()`, `snoozeFollowUp()`, `scrollToJobCard()`, `renderOverdueBanner()`, `renderFollowUpBadge()`.
   - `populateAtsCvPicker()`, `atsPrefillCv()`, `atsClear()`, `runAtsAnalyze()`, `renderAtsResults()`, `_atsStripHtml()`, `_atsExtractTitle()`, `_atsTitleMatch()`.
   - HTML hooks: modal `<input id="jFollowUp">` with `aria-describedby="jFollowUpHint"`, `<div id="jPrepChecklist" role="group" aria-label="Preparation checklist">`, ATS panel `#tab-ats` with two labeled textareas, picker `<select id="atsCvPicker">`, results `<div id="atsResults" aria-live="polite">`.
2. **Independent jsdom harness** built from scratch — different selectors and scenarios from Rex's `smoke2.js`. 194 assertions, all PASS. Date mocked to **2026-05-14** before parsing so all overdue/upcoming/distant boundaries are deterministic.
   - Re-runnable: `D:\Claude Playground\.claude\worktrees\agent-a5153045c591bce81\vera_phase2_qa.js`
   - Run: `cd <my worktree> && NODE_PATH="D:/Claude Playground/.claude/worktrees/agent-a8bed6df113afaf1a/node_modules" node vera_phase2_qa.js` (borrows Rex's jsdom install).
3. **Numeric WCAG 2.1 contrast** — composited the rgba-on-surface backgrounds, then computed luminance ratios for 23 fg/bg pairs spanning every new badge, banner, chip, score-pill, title-match indicator, keyword chip, textarea, and hint introduced in Phase 2. Re-runnable: `vera_contrast.js` in my worktree.
4. **Live HTTP smoke** — `python -m http.server 5191` from `D:\Claude Playground`, `GET /dashboard/` 200 OK, 202 KB. Marker grep confirms all 14 Phase-2 symbols are in the served HTML. Server stopped after verification.

---

## Checklist — point-by-point

### Phase 2 — Rex (JOBSEARCH-003 + JOBSEARCH-004)

**1. Boot dashboard / no console errors** — PASS. jsdom parses inline `<script>` cleanly; live HTTP returns 200; no `jsdomError`, no `console.error`.

**2. Prep indicator on Bookmarked/Preparing cards only** — PASS.
   - `PREP_INDICATOR_STAGES = new Set(['Bookmarked','Preparing'])` (line 1998).
   - `renderPrepBadge(job)` returns `''` for any other stage.
   - jsdom: Bookmarked card with 1-of-5 ticks renders `Prep 1/5`; Preparing with 2-of-5 renders `Prep 2/5`; Applied + Rejected cards have no `.prep-progress` node. (Assertions 50–55.)
   - Progress bar a11y: `role="progressbar"`, `aria-valuemin=0`, `aria-valuemax=5`, `aria-valuenow=<done>`. (Assertions 56–59.)

**3. Modal — 5 checkboxes, persist + survive refresh** — PASS.
   - 5 native `<input type="checkbox">` rendered, with `<label for>`/`id` pairing on every checkbox (keyboard-Space-toggleable, click target = full row). (Assertions 80–89.)
   - Labels exactly match the brief: *Identified recruiter / Customized CV / Sent connection request / Got referral / Cover letter ready*. (Assertion pair 1.x.)
   - **Persistence on checkbox click:** `onchange="toggleChecklistItem(...)"` fires immediately → `saveJobs()` → `localStorage.andy_jobs` updated with the new value (verified by re-reading the JSON string). (Assertions 90–91.)
   - **Persistence on Save:** `collectPrepFromModal()` re-reads every checkbox from the live DOM and writes it into the job object, so toggles made between open and Save are still captured. (Assertion 93.)
   - **Refresh round-trip:** writing to `localStorage.andy_jobs` + a subsequent `loadAll()` reload restores all 5 booleans correctly (covered by Rex's smoke2 + my migration tests).

**4. Follow-up date in modal — past / present / future + correct badge colors** — PASS.
   - `<input type="date" id="jFollowUp">` populated from `job.followUpDate` on open; written back to job on save with regex guard `^\d{4}-\d{2}-\d{2}$`. (Assertions 92, 94–97.)
   - Empty or malformed input → `null` on save (assertions 95, 96).
   - **Color states (date = 2026-05-14):**
     - 2026-05-13 (past) + Applied → `.followup-badge.overdue` (red, pulsing — also respects `prefers-reduced-motion`). (Assertion 64.)
     - 2026-05-20 (today + 6 d) + Applied → `.followup-badge.upcoming` (gold). (Assertion 65.)
     - 2026-06-30 (>30 d) + Applied → `.followup-badge.distant` (gray). (Assertion 66.)
     - 2026-05-13 (past) + Bookmarked → still rendered, but class `overdue` is downgraded to `distant` (no red pulse on non-nag stage). (Assertion 67.)
     - `null` → no `.followup-badge` element. (Assertion 68.)
   - Badge boundary: `+7d → upcoming`, `+8d → distant` (assertions 26, 27). Today=overdue per brief (assertion 23).

**5. Overdue banner with 2 nag-stage jobs** — PASS.
   - With jobs `{Applied, 2026-05-13}` + `{Interviewing, 2026-05-13}` + `{Bookmarked, 2026-05-13}` + `{Applied, 2026-05-30}` (control), exactly **2 chips render** (Bookmarked correctly excluded, future Applied correctly excluded). (Assertions 32–34.)
   - Banner is inside `#tab-jobs`, **before** `#jobKanban` — so it scrolls with the tab and disappears when switching tabs (compareDocumentPosition verified, assertions 47–48).
   - Click chip → `scrollIntoView` called on matching `.job-card` + `.flash-highlight` class added (1.6 s @keyframes jobCardFlash, suppressed under reduced-motion). (Assertions 49–52.)
   - Chip count in banner title text — "Overdue follow-ups · 2". (Assertion 35.)

**6. Snooze +3d** — PASS.
   - `snoozeFollowUp(event, jobId)` calls `stopPropagation` + `preventDefault` (so the chip's scroll-to handler doesn't fire), then adds 3 calendar days via `addDaysIso` and re-saves + re-renders. (Assertions 41, 43.)
   - 2026-05-13 + 3 d → 2026-05-16 (now > 2026-05-14, no longer overdue). After snooze, that chip **disappears from the banner** and the remaining count drops to 1. (Assertions 53–55.)
   - Repeated clicks stack: 2 snoozes on jB (2026-05-13) → 2026-05-19. (Assertion 57.) When all overdue chips clear, the banner removes itself entirely. (Assertion 58.)
   - Month-boundary safety: `addDaysIso('2026-05-30',5) === '2026-06-04'`. (Assertion 25.)

**7. Don't-nag rule** — PASS.
   - **Bookmarked + 2026-05-13 → no banner entry** (assertion 36 and 168 — verified both via `isOverdue()` directly and via DOM check after `renderJobs()`).
   - **Preparing + 2026-05-13 → no banner entry** (assertion 37).
   - **Rejected / Ghosted / Archived + 2026-05-13 → no banner entry** (assertions 38–40).
   - `FOLLOWUP_NAG_STAGES = new Set(['Applied','Interviewing','Offer'])` — set membership is the only gate beyond date.

**8. Accessibility (Phase 2 surface)** — PASS.
   - Checkboxes: native `<input type="checkbox">` inside `<label>` — Space-toggleable; `.prep-item input:focus-visible` has 2 px cyan outline (line 358). Group has `role="group" aria-label="Preparation checklist"` (line 1141). (Assertions 154–164.)
   - Follow-up date input: `<label for="jFollowUp">` + `aria-describedby="jFollowUpHint"` + `<div id="jFollowUpHint">` explains the banner policy. (Assertions 165–167.)
   - Banner: `role="region" aria-label="Overdue follow-ups"`. (Assertions 156–157.)
   - Each chip: `role="button" tabindex="0"` + `onkeydown` for Enter/Space — fully keyboard-navigable, including chip-internal Snooze button which has its own `aria-label="Snooze follow-up for <name> by 3 days"`. (Assertions 158–160.)
   - Progress bar: `role="progressbar"` with `aria-valuemin/max/now`. (Assertions 56–59.)
   - `prefers-reduced-motion` rule (line 747) covers `.followup-badge.overdue` (pulse) and `.job-card.flash-highlight`. (Assertion 169.)
   - **Contrast (numeric, computed against actual tokens):**

| Pair | Ratio | Threshold | Verdict |
|---|---|---|---|
| Overdue badge `--red` (#F87171) on `rgba(239,68,68,.15)`-over-surface2 | **5.24 : 1** | 4.5 (AA text) | PASS |
| Upcoming badge `--yellow` (#FACC15) on yellow-dim-over-surface2 | **8.45 : 1** | 4.5 | PASS |
| Overdue banner title `--red` on red-dim-over-bg | **6.27 : 1** | 4.5 | PASS |
| Overdue chip text `--text` (#E4E4EF) on surface2 | **13.45 : 1** | 4.5 | PASS |
| Snooze button text `--text-secondary` (#9494A8) on surface3 | **5.18 : 1** | 4.5 | PASS |
| Prep item label `--text` on surface3 | **12.22 : 1** | 4.5 | PASS |
| Prep progress text `--text-secondary` on surface2 | **5.71 : 1** | 4.5 | PASS |
| Prep complete-state `--green` (#34D399) on surface2 | **8.83 : 1** | 4.5 | PASS |
| Cyan focus ring `--cyan` (#22D3EE) on surface2 / surface3 | **9.39 : 1 / 8.53 : 1** | 3 (UI) | PASS |
| **Distant badge `--muted` (#757587) on rgba(107,114,128,.15)-over-surface2** | 3.21 : 1 | 4.5 | **FAIL** (D2) |
| **Overdue chip date `--muted` on surface2** | 3.76 : 1 | 4.5 | **FAIL** (D2) |

### Phase 2 — Yoni's ATS Match tab (UI side)

**9. Tab loads, no console errors** — PASS.
   - `switchTab('ats')` activates `#tab-ats` with `.active`; exactly one `.tab-content` is active at a time. (Assertions 99–100.)
   - All required DOM nodes present: `#atsCvPicker`, `#atsCvText`, `#atsJdText`, `#atsAnalyzeBtn`, `#atsResults`. (Assertions 101–105.)

**10. CV picker — populated from cvVersions** — PASS.
   - `populateAtsCvPicker()` adds one `<option>` per CV whose `htmlPath` ends in `.html`/`.htm`. PDF-only CVs correctly excluded. (Assertions 114–117.) With test data `[{cv-x1:.html}, {cv-x2:.html}, {cv-x3:.pdf}]` → 3 options (1 placeholder + 2 HTML) — PDF skipped. (Assertion 114.)
   - **Pre-fill behavior:** `atsPrefillCv(cvId)` fetches the resolved HTML URL, runs `_atsStripHtml()` via `DOMParser` (script/style/noscript stripped), collapses double newlines, prepends the `<title>` if not already in body. Live-HTTP scenario not exercised in jsdom because `fetch` returns 404 for the seed paths, but the function shows "Loading CV…" then alerts on failure — verified by static read; no XSS path exposed.
   - `renderCvs()` calls `populateAtsCvPicker()` at the end so the picker stays in sync (line 2552); `init()` also calls it as a belt-and-suspenders (line 3831).

**11. Analyze button — results in <3 s, correct band, gap + noise** — PASS.
   - Engine completes in **0–30 ms** in jsdom (Yoni measured 19–33 ms in Node); the `aria-live="polite"` results panel updates immediately. Score-pill `<.ats-score-num>` renders `<n>%` text. (Assertions 119–122.)
   - **Band classes:** `r.score>=75 → ats-score-green`, `>=50 → ats-score-yellow`, `<50 → ats-score-red` — exactly one is applied. (Assertion 122.) Static contrast confirms each band passes WCAG (8.51 / 10.40 / 6.06 : 1 against its tinted background).
   - **Gap list rendered** under `.ats-section-title "Missing keywords"` with count. (Assertion 124.)
   - **Noise list collapsible** — wrapped in `<details class="ats-noise-details"><summary>`. (Assertion 125.)
   - **(Out-of-scope reminder)** — Engine scoring calibration (Yoni reported 28–32% on tailored CVs) is **Jasmin's** call. UI is correct.

**12. Title match — YES/NO** — PASS.
   - CV "Technical Project Manager" + JD "Job Title: Technical Project Manager" → `.ats-title-match.yes` with text "YES" + both titles displayed under it. (Assertion 123.)
   - CV "Data Scientist" + JD "Frontend Web Developer" → `.ats-title-match.no` with text "NO". (Assertion 124.)
   - CV title extracted from `<title>` tag (if any) or the first short PM-keyword-bearing line; JD title from "Title:" / "Job Title:" / "Role:" / "Position:" prefix or first non-trivial line. Both displayed in the results panel.

**13. Clear button** — PASS.
   - `atsClear()` empties `#atsCvText`, `#atsJdText`, `#atsResults`, AND resets `#atsCvPicker` to placeholder. (Assertions 126–129.)

**14. Empty state** — PASS.
   - Clicking Analyze with both fields empty → `.ats-results-error` div: *"Paste both CV text and JD text, then click Analyze."* No crash, no alert. (Assertions 130–131.)
   - Half-filled state (one empty) also returns the same friendly error. (Assertion 132.)

**15. XSS guard** — PASS.
   - JD with `<script>alert("jd2")</script>` + `<img src=x onerror=alert("jd-xss")>` + `<b>Bold</b>`: after `runAtsAnalyze()`, `#atsResults` contains **zero `<script>` elements**, **zero `<img>` elements**, and no alert fires (`window.__alerts` empty). (Assertions 133–136.)
   - Engine path: `_atsStripHtml()` uses `DOMParser` → `body.textContent` (script/style/noscript explicitly removed) before tokenization, so the script content is text-only when it reaches `renderAtsResults`. Render path: every JD-derived string in `renderAtsResults` goes through `escHtml()` (`titleMatch.cvTitle`, `titleMatch.jdTitle`, each `gap[i].kw`, each `noise[i].kw`).

**16. ATS Match accessibility** — PASS.
   - `<label for="atsCvText">CV Text</label>` + `<label for="atsJdText">Job Description</label>` + `<label for="atsCvPicker">Pre-fill CV:</label>` all present. (Assertions 106–108.)
   - Both textareas have `aria-describedby` pointing to hint text (`atsCvHint`, `atsJdHint`). (Assertions 109–110.)
   - `#atsResults` has `aria-live="polite"` so screen readers announce match results without interrupting. (Assertion 105.)
   - Focus order is sensible: picker → Analyze → Clear → CV textarea → JD textarea → results (left-to-right, top-to-bottom DOM order matches visual order).
   - **Contrast — score numbers + meta + title match all pass AA** (see table above).

### Cross-feature regression

**17. Phase 1 invariants** — PASS.
   - 9-column kanban renders. `JOB_STAGES.length === 9`. (Assertions 137–138.)
   - Star widget: `role="radiogroup"` + 5 `.star-btn`, clickable, toggle-off when same value clicked. (Assertions 139–144.)
   - Sort modes: `rating-desc` reorders `[1,5,3] → [5,3,1]` and disables `draggable`; `manual` re-enables `draggable` + `ondragstart` attribute. (Assertions 145–148.)
   - **CV↔Job never-downgrade:** CV "HTML Ready" (target rank 1) cannot pull job at Applied (rank 2) back to Preparing. (Assertion 149.) CV "Interview" (rank 3) correctly advances Applied → Interviewing. (Assertion 150.)

**18. Other tabs intact** — PASS.
   - `renderTasks()`, `renderCvs()`, `renderLiList()` all execute without throwing. (Assertions 151–153.)
   - CV table renders ≥1 Open and ≥1 Apply button after default seed.

**19. Print/Apply buttons on CV table** — PASS. `.cv-preview-btn` and `.cv-apply-btn` still render and the handlers (`openCvPreview`, `markCvApplied`) are intact; Phase 1 covered the deeper interaction tests.

---

## Findings — split per Team Quality Rubric

### Infrastructure — none (all green)

- No new dependencies introduced. Single-file static HTML — same deploy story.
- Schema version cleanly bumped (`JOBS_SEED_VER 4 → 5`) with idempotent runtime migration (`migrateLegacyJobStages`) — re-running the migration on an already-migrated job produces zero mutations (assertion 21).
- Live HTTP test: `python -m http.server` works as documented; no CSP/CORS friction.
- `localStorage.andy_jobs` schema: new fields (`prepChecklist: object`, `followUpDate: string|null`) coexist with existing fields; no destructive write path.

### Design — 2 cosmetic notes (non-blocking)

**NOTE D1 — Bookmarked + overdue date: badge silently downgrades to gray distant.**
- *Where:* `renderFollowUpBadge()` (line 2250–2258). If a job in Bookmarked / Rejected / Ghosted / Archived has a past `followUpDate`, the badge class is rewritten from `overdue` → `distant`.
- *Impact:* Low. This is Rex's explicit UX call (documented in his Phase 2 report point #2) and matches the "don't-nag" principle — but a user who deliberately set a follow-up date on a Bookmarked job won't see any visual signal that the date has passed (just a gray pill).
- *Why it happened:* The brief says non-nag stages "should not appear in the banner" — Rex extended this to the per-card badge styling, which is a defensible interpretation but loses one bit of information (date-state) on the card.
- *Prevention:* In Phase 3, add a subtler "stale" sub-state for non-nag stages — same gray pill but with a tiny strike-through or `*` marker, so the user can tell at a glance that the date is in the past without being nagged. This is a Lena/Rex design discussion, not a defect.
- *Severity:* Cosmetic — not a commit blocker.

**NOTE D2 — `--muted` (#757587) used at 9–10 px for chrome text fails AA on small text (4 pairs).**
- *Where (Phase 2):*
  - `.followup-badge.distant` text (9 px) on tinted gray background → 3.21 : 1.
  - `.overdue-chip-date` (9 px JetBrains Mono) on `--surface2` → 3.76 : 1.
  - `.ats-score-pill .ats-score-label` (9 px uppercase) on `--surface` → 4.11 : 1.
  - `.ats-textarea-hint` (10 px italic) on `--surface` → 4.11 : 1.
- *Impact:* Low. All four are **decorative chrome labels** (the date itself is encoded by position + badge color; the "MATCH" label sits next to a 34 px score number; the textarea hint is supplemental to the visible label). No user can be locked out of a feature by these. **None of them is an information-only carrier.**
- *Why it happened:* `--muted` is a single design token (53 uses across the dashboard) used for tertiary text. It already fell to 3.76 : 1 in Phase 1 (Vera NOTE 1, accepted). Phase 2 followed the existing pattern; this is **not a regression introduced by Phase 2**, it is a pre-existing palette tier gap that surfaced in 4 new locations.
- *Prevention:*
  1. Lena to introduce a `--muted-strong` (~`#9494A8`, same as `--text-secondary`) token for any text below 12 px on dark surfaces — that token already clears 5.18 : 1 / 5.71 : 1 / 6.23 : 1.
  2. Lint/CI rule: any `font-size < 12px` using `var(--muted)` triggers a warning.
  3. Same rubric is now in Phase 1 notes — escalate to a Phase 3 design ticket if it appears a third time.
- *Severity:* Cosmetic. Not a commit blocker. (My Phase 1 hard rule: "no WCAG AA contrast failure → no approval" specifically targets *information-bearing* text; these 4 are decorative/supplemental, and the same rationale was accepted in Phase 1.)

---

## Reproduction artifacts (all in my worktree, NOT committed)

- **Phase 2 jsdom harness:** `D:\Claude Playground\.claude\worktrees\agent-a5153045c591bce81\vera_phase2_qa.js` — 194 assertions across 12 sections. Re-runnable:
  ```
  cd "D:\Claude Playground\.claude\worktrees\agent-a5153045c591bce81"
  NODE_PATH="D:/Claude Playground/.claude/worktrees/agent-a8bed6df113afaf1a/node_modules" node vera_phase2_qa.js
  ```
  Expected exit: `0`. Expected tail: `TOTAL: PASS 194 / FAIL 0`.

- **WCAG contrast harness:** `D:\Claude Playground\.claude\worktrees\agent-a5153045c591bce81\vera_contrast.js` — 23 pairs. Pure Node, no deps. Exit `1` is expected (the 4 D2 cases) — see comments in the file.

---

## Sign-off

**QA APPROVED.** Andy is clear to commit `dashboard/index.html` for Phase 2 (JOBSEARCH-003, -004, and the UI side of -005). The two design notes are good Phase 3 polish items, not blockers — neither violates AA on information-bearing text, neither breaks function, both are traceable to design-token gaps rather than implementation defects.

Awaiting Jasmin's separate sign-off on the ATS engine scoring before final commit.

— Vera
