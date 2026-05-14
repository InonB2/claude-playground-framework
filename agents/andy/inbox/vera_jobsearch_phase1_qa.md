# Vera — QA Sign-Off: Job Search System Phase 1 (JOBSEARCH-001 + JOBSEARCH-002)

**Date:** 2026-05-13
**Reviewer:** Vera (QA & Visual Inspector)
**File under review:** `D:\Claude Playground\dashboard\index.html`
**Rex's report:** `D:\Claude Playground\agents\andy\inbox\rex_jobsearch_phase1_done.md`
**Plan source:** `D:\Claude Playground\owner_inbox\research\job_search_upgrade_plan.md` (JOBSEARCH-001, -002)

---

## Verdict: **PASS WITH NOTES** — commit-ready

- 59 independent QA assertions executed (all passed) — fully separate from Rex's 41-assertion suite.
- Live HTTP smoke (`npx serve . -l 5180`) returns HTTP 200; served HTML contains the new code paths (`JOB_STAGES`, `renderStars`, `#jobSort`, `role="radiogroup"`).
- No console errors, no exceptions in any render path (Tasks, Jobs, CVs, LinkedIn all render).
- The critical **CV↔Job sync regression (DASH-SYNC-001)** is intact — verified across all four directions (Job→CV advance, Job→CV no-downgrade, CV→Job advance, CV→Job no-downgrade).
- XSS guard verified: `<img src=x onerror=alert(1)>` and `<b>bold</b>` are escaped on render, no `<img>` / `<b>` nodes injected, no alert fires.
- WCAG 2.1 AA contrast: all relevant ratios computed numerically — every star and column color exceeds the required threshold.

There are **two minor notes** below (no blockers). Andy can commit; both notes are tracked as follow-up polish for Phase 2.

---

## How I tested

1. **Static read** of all modified sections — `JOB_STAGES`, `JOB_COL_COLORS`, `JOB_STAGE_RANK`, `LEGACY_STAGE_MAP`, `CV_TO_JOB_STAGE`, `JOB_TO_CV_STATUS`, `migrateLegacyJobStages()`, `renderStars()`, `setJobRating()`, `renderJobs()`, `setJobSortMode()`, `openJobModal()` / `saveJob()`, modal HTML, CSS for `.job-stars` / `.star-btn`, seed data (`seedDefaultJobs`, `JOBS_V2_ENTRIES`, `JOBS_SEED_VER=4`).
2. **Independent jsdom harness** — `D:\Claude Playground\.claude\worktrees\agent-aad6043f24fc5f180\vera_qa.js`. 59 assertions, all PASS. (I built this from scratch rather than rerunning Rex's `smoke.js` — different selectors, different scenarios, eval-bridge for `const` access.)
3. **Live HTTP** — started `npx serve . -l 5180`, verified `/dashboard/` returns 200 and the served HTML contains the new code paths. Server stopped after verification.
4. **Numeric WCAG contrast** — computed luminance ratios for every star/column color pairing against the actual surface tokens (`--surface`, `--surface2`, `--bg`).
5. **CV↔Job sync regression** — five-scenario controlled test (see Q7a–Q7e below). This is the most important section in the report; it is intact.

---

## Per-checklist results (12 sections)

### 1. Dashboard loads — PASS
- `npx serve . -l 5180` → `GET /dashboard/` → **HTTP 200** in 35 ms.
- jsdom parses & executes inline `<script>` cleanly. No `console.error`, no syntax error, no thrown exception.
- All four `render*()` functions (Tasks, Jobs, CVs, LinkedIn) execute without throw.

### 2. Kanban columns — PASS
- `JOB_STAGES.length === 9`: `['Bookmarked','Preparing','Applied','Interviewing','Offer','Accepted','Rejected','Ghosted','Archived']`
- 9 `.job-col` elements rendered in `#jobKanban`.
- 6 distinct color tokens across 9 columns — see **NOTE 1** below.

### 3. Drag-and-drop — PASS (in Manual mode, as Rex documented)
- Default `jobSortMode === 'manual'`; first card `.draggable === true`; `ondragstart="jobDragStart(event,'job-lenovo-inc-001')"` attached.
- Stage change persists to `localStorage.andy_jobs` (verified by re-read after `saveJobs()`).

### 4. Sort modes — PASS
- `setJobSortMode('rating-desc')` reorders Preparing column: injected ratings `[1,5,3]` plus seed rating `5` → rendered order `[5,5,3,1]` — descending confirmed.
- `setJobSortMode('date-desc')` activates; cards `.draggable === false`, no `ondragstart` attribute → drag intentionally disabled (matches Rex's design note).
- Switching back to `'manual'` re-enables drag (`draggable === true`, attribute restored).

### 5. Star rating — PASS
- `setJobRating(evt, jobId, 4)` → `job.rating === 4`. Second call with same value → `job.rating === null` (toggle-off works).
- Persistence: `localStorage.andy_jobs` reflects the new rating after `saveJobs()`.
- Star button `onclick="setJobRating(event,...)"` — `event` is passed; `stopPropagation`/`preventDefault` inside `setJobRating`.
- Simulated `MouseEvent('click', {bubbles:true})` dispatched on `.star-btn`: modal `#jobModal` does NOT acquire the `.open` class. Card-level handler correctly bails when `ev.target.closest('.star-btn')` matches.

### 6. Job modal — Excitement select — PASS
- `#jRating` `<select>` exists, options `["","1","2","3","4","5"]`, first option labeled `— unrated —`.
- Save round-trip: set stage = Preparing + rating = 4, click Save → `localStorage.andy_jobs[job].stage === 'Preparing' && .rating === 4`.
- Empty rating saves as `null` (not `0`, not `""`) — confirmed via `Math.max(1, Math.min(5, …)) || null` clamp.

### 7. CV↔Job sync regression (CRITICAL) — PASS
All five scenarios in the JOBSEARCH-001 spec verified end-to-end:
- **Q7a** Job → Interviewing: `JOB_TO_CV_STATUS['Interviewing'] === 'Interview'` → CV "Drafting" advances to "Interview". PASS.
- **Q7b** CV "HTML Ready" (target stage `Preparing`, rank 1) while job at `Applied` (rank 2): never-downgrade rule fires → job stays at `Applied`. PASS.
- **Q7c** CV "Interview" (target stage `Interviewing`, rank 3) while job at `Applied` (rank 2): job advances to `Interviewing`. PASS.
- **Q7d** Job → Offer with CV already at `Interview`: `JOB_TO_CV_STATUS['Offer'] === 'Interview'`, same rank → CV stays `Interview` (no spurious mutation). PASS.
- **Q7e** Job → Rejected: CV advances `Interview` (rank 4) → `Rejected` (rank 5). PASS.
- **Q7f** CV chip (`IB-v1-PM-SyncCo`) renders inside the linked job's `.job-card` innerHTML. PASS.
- **Q7g** Job Stage badge column appears in CV table for linked CVs. PASS.

### 8. XSS guard — PASS
- Injected `company = '<img src=x onerror=alert(1)>'`, `role = '<b>bold</b>'`.
- Resulting `.job-card`: `querySelectorAll('img').length === 0`, `querySelectorAll('b').length === 0`, `window.alert` intercepted and **never fired**.
- `textContent` of the card contains the literal escaped strings (`<img src=x onerror=alert(1)>` and `<b>bold</b>`).

### 9. Legacy migration — PASS
- `Saved → Bookmarked` ✓
- `CV Ready → Preparing` ✓
- `Screen → Interviewing` ✓
- `Interview → Interviewing` ✓
- `Negotiating → Offer` ✓
- `Withdrawn → Archived` ✓
- `BogusStage` (unknown) → `Bookmarked` (safe fallback) ✓
- All migrated jobs gain `rating: null` ✓
- Idempotent: second `migrateLegacyJobStages()` produces zero mutations (`JSON.stringify(jobs)` identical before/after). ✓

### 10. Accessibility — PASS
- `.job-stars` has `role="radiogroup"` and `aria-label="Excitement rating"`.
- Each `.star-btn` has `role="radio"`, `aria-label="N star(s)"`, and `aria-checked="true"/"false"` matching filled state.
- CSS includes `.star-btn:focus-visible { outline: 2px solid var(--cyan); outline-offset: 1px }` — focus ring present.
- **WCAG 2.1 contrast (numeric, computed against actual tokens):**

| Pair | Ratio | Threshold | Verdict |
|---|---|---|---|
| Filled star (`#FACC15`) on card surface (`#1C1C21`) | **11.08 : 1** | 4.5 : 1 (text) / 3 : 1 (UI) | PASS |
| Unfilled star stroke (`#757587`) on card surface | **3.76 : 1** | 3 : 1 (non-text graphical, SC 1.4.11) | PASS |
| Cyan focus ring (`#22D3EE`) on card surface | **9.39 : 1** | 3 : 1 (UI component) | PASS |
| Body text (`#E4E4EF`) on `--surface` | 14.70 : 1 | 4.5 : 1 | PASS |
| Orange column accent on `--surface2` | 6.05 : 1 | 3 : 1 | PASS |
| Purple column accent on `--surface2` | 6.24 : 1 | 3 : 1 | PASS |
| Green column accent on `--surface2` | 8.83 : 1 | 3 : 1 | PASS |
| Red column accent on `--surface2` | 6.14 : 1 | 3 : 1 | PASS |
| Muted column accent on `--surface2` (used by Bookmarked/Ghosted/Archived) | 3.76 : 1 | 3 : 1 | PASS (see **NOTE 1**) |

Per my hard rule (no WCAG AA contrast failure → no approval), this build clears the bar in every category.

### 11. Visual regression on other tabs — PASS
- `renderTasks()` runs without throw; 4 task-card containers (`[id^="cards-"]`) intact.
- `renderCvs()` runs without throw; CV table renders, 5 Open/Preview buttons + 5 Apply buttons rendered.
- `renderLiList()` runs without throw.
- Notifications path not touched (no related selectors regressed).
- Nothing outside the `JOB APPLICATIONS` / job-modal / jobs-tab HTML / job-CSS block was modified (verified via Grep — no edits to `cv-preview-btn`, `cv-apply-btn`, `markCvApplied` handlers).

### 12. CV table Print/Apply buttons — PASS
- 5 `.cv-preview-btn` elements rendered (Open).
- 5 `.cv-apply-btn` elements rendered (Applied ✓).
- `markCvApplied('cv-001')` advances `PDF Ready → Applied` correctly; downstream `syncCvToJob` then runs (already covered by Q7c).

---

## Findings — split per team quality rubric

### Infrastructure (none — all green)
- No new dependencies introduced.
- No external resource added; star widget uses inline SVG (no font-glyph dependency).
- Server (`npx serve`) works as documented; no CSP, port, or routing surprises.
- `localStorage` schema bumped cleanly (`JOBS_SEED_VER 3 → 4`) with idempotent runtime migration — no destructive write path.

### Design — 2 minor notes (non-blocking)

**NOTE 1 — Three columns share `--muted` color (Bookmarked, Ghosted, Archived).**
- *Where:* `JOB_COL_COLORS` map (line 1771).
- *Impact:* Low. Column titles are clearly labeled and the columns are physically separated in the kanban grid, so this does not violate WCAG 1.4.1 ("color not the only means of conveying information"). However, a fast-scanning user could conflate the entry funnel ("Bookmarked") with the two terminal states ("Ghosted", "Archived"), since they look visually identical.
- *Why it happened:* The 9-column expansion outgrew the existing 6-color palette without a tier-tier color extension. No design brief delta was issued for the new terminal states.
- *Prevention:* Add a "soft-red" or "dim-amber" token to the palette in Phase 2 so terminal states (Ghosted, Archived) can be muted-but-distinct from the funnel entry. Pair this with a Lena design-brief update so future stage additions auto-pull from the palette.
- *Severity:* Cosmetic. Not a commit blocker.

**NOTE 2 — Modal exposes both star widget (on card) and `<select>` (in modal), but they don't visually share styling.**
- *Where:* `#jRating` `<select>` in job modal (line 919–928) vs `.job-stars` SVG widget on cards.
- *Impact:* Low UX inconsistency. The modal uses a native dropdown (`1 ★`, `2 ★★`, …) while the card uses the bespoke star widget. Two different input affordances for the same data field.
- *Why it happened:* Modal needed a native control for keyboard form workflow; the card needed inline clickability without opening the modal. Both legitimate, but the visual asymmetry is jarring.
- *Prevention:* In Phase 2 / Tier 2, replace the modal `<select>` with the same star widget reused (just toggled into a different container). One affordance, two contexts. Cole/Lena follow-up item.
- *Severity:* Cosmetic. Not a commit blocker.

---

## Reproduction artifact

- Independent QA harness (re-runnable, not for prod): `D:\Claude Playground\.claude\worktrees\agent-aad6043f24fc5f180\vera_qa.js`
- Run with: `cd "D:\Claude Playground\.claude\worktrees\agent-ac7647d00a4c372c4" ; NODE_PATH="D:/Claude Playground/.claude/worktrees/agent-ac7647d00a4c372c4/node_modules" node "D:/Claude Playground/.claude/worktrees/agent-aad6043f24fc5f180/vera_qa.js"` (borrows Rex's `jsdom` install — this worktree has no `node_modules`).
- Expected exit code: `0`. Expected output: `PASS: 59 / FAIL: 0`.

---

## Sign-off

**QA APPROVED.** Andy is clear to commit `dashboard/index.html`. The two design notes are good Phase 2 polish items, not blockers — neither violates WCAG AA, neither breaks function, and both are clearly traceable to design-brief gaps rather than implementation defects.

— Vera
