# Rex — Job Search System Upgrade, Phase 1 — DONE

**Tasks:** JOBSEARCH-001 (5-stage funnel kanban) + JOBSEARCH-002 (excitement rating)
**Date:** 2026-05-13
**File touched (only one):** `D:\Claude Playground\dashboard\index.html`
**Ready for:** Vera QA. **Do NOT commit yet — Andy will do that after Vera signs off.**

---

## Decision: 5 funnel stages + 4 terminal stages (= 9 columns)

**Stage list:** `Bookmarked → Preparing → Applied → Interviewing → Offer` (the 5 Teal funnel concepts), then `Accepted, Rejected, Ghosted, Archived` as terminal states.

**Rationale (2 lines as requested):**
The original 12 stages mixed funnel positions with outcomes; collapsing to a pure 5 would have erased the terminal-state tracking the dashboard already used (Rejected/Ghosted/Withdrawn/Archived) and that Cole/Inon rely on for cv_archive. Keeping 5 funnel + 4 terminal preserves every concept while making the active pipeline visually clean — the funnel cards sit in the first 5 columns; "dead" applications drop into terminal columns and stop competing for attention.

**Legacy stage migration (idempotent, runs once on every load):**
- `Saved` → `Bookmarked`
- `CV Ready` → `Preparing`
- `Screen` / `Interview` → `Interviewing`
- `Negotiating` → `Offer`
- `Withdrawn` → `Archived`
- Any unknown legacy stage falls back to `Bookmarked` (safest — never silently terminates anything)
- All migrated jobs gain `rating: null` so the field always exists once loaded

CV↔Job sync maps (`CV_TO_JOB_STAGE`, `JOB_TO_CV_STATUS`) updated to point at the new stage names; never-downgrade rule (DASH-SYNC-001) is preserved end-to-end.

---

## What changed (file: `dashboard/index.html`)

### JS — `JOB APPLICATIONS` block (≈ line 1750–1900)
- New constants: `JOB_STAGES` (9 entries), `JOB_COL_COLORS`, `JOB_STAGE_RANK` (legacy aliases retained so partial-migration states don't crash), `LEGACY_STAGE_MAP`.
- New function: `migrateLegacyJobStages()` — wired into `init()` after job-load.
- New function: `renderStars(jobId, rating)` — inline SVG star widget (5 buttons, ARIA `radiogroup`, no external font).
- New function: `setJobRating(e, jobId, value)` — toggle behaviour (click same star → clear). `stopPropagation` so it does not open the modal.
- `renderJobs()` rewritten: applies the within-column sort (`manual` / `rating-desc` / `date-desc`); native HTML5 drag is auto-disabled while a non-manual sort is active (manual reorder makes no sense when rows re-sort on every render — switch back to "Manual" to drag).
- New: `setJobSortMode(mode)` and global `jobSortMode`.
- Job modal: stage `<select>` updated to the 9 new stages; new `Excitement (1-5)` `<select>` with "— unrated —" + 1–5 ★ options. `openJobModal()` reads `j.rating`, `saveJob()` writes a clamped 1–5 integer or `null`.
- Seed jobs in `seedDefaultJobs()` migrated to new stage names and pre-populated with ratings. `JOBS_V2_ENTRIES` updated too. `JOBS_SEED_VER` bumped 3 → 4.

### HTML — Jobs tab toolbar (≈ line 700)
- Added Sort dropdown: `Manual / Rating (high → low) / Date (newest first)`.

### CSS — Job Excitement Stars (≈ line 340)
- `.job-stars`, `.star-btn`, `.star-btn:hover`, `.star-btn:focus-visible`, `.star-btn.filled` — keyboard-accessible, hover scale, focus ring, gold glow on filled stars.

**Lines outside `JOB APPLICATIONS` / job modal / job tab HTML / job CSS were not touched.** No regressions to CV table, LinkedIn CMS, Tasks kanban, or notifications.

---

## How I tested

1. **JS syntax check** — Node `new Function(<script body>)` parses cleanly (89.6 KB).
2. **Headless smoke test (jsdom)** — 41 assertions, all green. Test file: `D:\Claude Playground\.claude\worktrees\agent-ac7647d00a4c372c4\smoke.js`. Coverage:
   - JOB_STAGES contains all 5 funnel concepts + 9 total length.
   - Legacy migration: `Saved/CV Ready/Screen/Negotiating/Withdrawn/Interview` → correct new stages; `rating` initialised to `null`.
   - `setJobRating`: set, toggle-off, re-set.
   - `renderJobs`: emits 5 `.star-btn` per card; filled state matches rating.
   - Sort: `rating-desc` orders `[5,3,2,null]` correctly; native `draggable` disabled while sort active; restored under `manual`.
   - **CV↔Job never-downgrade preserved**: CV "HTML Ready" (→Preparing rank 1) does NOT downgrade a job at Applied (rank 2); CV "Interview" advances job to Interviewing; job→Offer does NOT downgrade CV; job→Rejected advances CV to Rejected.
   - **XSS guard**: company `<img src=x onerror=alert(1)>` and role `<b>bold</b>` are escaped — no live `<img>` or `<b>` nodes appear in the card (Vera's prior XSS fix on stage rendering is preserved; I also escaped the stage title and column-cards `id` in the kanban header).
   - Modal round-trip: stage `Preparing` + rating `3` saved via `saveJob()` lands in `localStorage.andy_jobs`.
3. **Live HTTP smoke** — `npx serve .` on port 5179 served `dashboard/index.html` 200 OK; HTML contained `JOB_STAGES=['Bookmarked','Preparing','Applied','Interviewing','Offer'`, `renderStars`, and the `#jobSort` dropdown. Server stopped after verification.

Print/Apply buttons untouched (those are CV-table actions, not job actions) — confirmed by grep: no edits to `cv-preview-btn`, `cv-apply-btn`, or related handlers.

---

## Known gotchas Vera should validate

- **Drag is intentionally disabled when a non-manual sort is active.** Cards have `draggable=false` and no `ondragstart` handler in that mode. To drag, switch Sort back to "Manual." (Acceptance criterion in brief: "Drag-and-drop still works" — works in manual mode; this is the cleanest UX trade-off.)
- **Existing `andy_jobs` localStorage with legacy stages** will be migrated on first load after this deploy. Migration writes once if anything changes (idempotent). To test, open dashboard with old data → check that `Saved`/`Screen` cards now appear in `Bookmarked`/`Interviewing`.
- **`JOBS_V4_ENTRIES = []`** is a placeholder for future seed merges; no V4 entries needed because the V3 migration handled state transition.

---

## Files
- Modified: `D:\Claude Playground\dashboard\index.html`
- Test script (worktree-local, not for prod): `D:\Claude Playground\.claude\worktrees\agent-ac7647d00a4c372c4\smoke.js`

— Rex
