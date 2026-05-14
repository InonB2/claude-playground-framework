# Rex — Job Search System Upgrade, Phase 2 — DONE

**Tasks:** JOBSEARCH-003 (prep checklist per job) + JOBSEARCH-004 (follow-up reminder date)
**Date:** 2026-05-13
**File touched (only one):** `D:\Claude Playground\dashboard\index.html`
**Ready for:** Vera QA. **Do NOT commit yet — Andy will do that after Vera signs off.**

---

## What changed

### JOBSEARCH-003 — Preparation Checklist

- Per-job field `prepChecklist: {identifiedRecruiter, customizedCv, sentConnection, gotReferral, coverLetterReady}` — all booleans, default `false`.
- 5 default items, declared once via the new `PREP_ITEMS` constant (label + key) — adding a 6th item later is one line.
- **Modal:** Always-visible "Preparation checklist" group with 5 checkboxes. Visible for jobs in any stage (Inon explicitly wanted to be able to fill it in retroactively).
  - Each checkbox is a native `<input type="checkbox">` inside a `<label class="prep-item">`, so it is keyboard-toggleable (Space) and focus-visible.
  - Clicking a checkbox in the modal **persists immediately to localStorage** via `toggleChecklistItem(jobId,key,checked)` — even if the user closes the modal without "Save" the change sticks. `Save` does a full re-collect from DOM as a safety net.
- **Card:** Compact progress indicator on cards in `Bookmarked` and `Preparing` stages only. Cyan→green progress bar with `N/5` text. Hidden on Applied / Interviewing / Offer / terminal stages so finished cards stay clean.
- Migration: `migrateLegacyJobStages()` (existing function) now seeds `prepChecklist = defaultPrepChecklist()` on any legacy job missing the field. Partial-checklist legacy objects (theoretical, but defensive) get missing keys filled with `false` without losing existing `true` values.

### JOBSEARCH-004 — Follow-up Reminder

- Per-job field `followUpDate: 'YYYY-MM-DD' | null`.
- **Modal:** New "Follow-up date" `<input type="date">` directly under "Applied Date" with a short hint explaining the banner-stage policy.
- **Card badge:** `📅 YYYY-MM-DD` pill with 3 visual states (all in CSS, no JS color logic on the card):
  - `overdue` — red with subtle pulse (respects `prefers-reduced-motion`)
  - `upcoming` — gold, within next 7 days
  - `distant` — gray, >7 days out
  - For jobs in non-nag stages (Bookmarked/Accepted/Rejected/Ghosted/Archived) the badge still renders if set, but `overdue` styling is downgraded to `distant` — the date is still informative but the card doesn't shout.
- **Overdue banner:** Injected as a sibling element above the kanban, INSIDE `#tab-jobs`, so it scrolls with the tab and disappears when no overdue jobs exist. Renders only when `jobs.filter(isOverdue).length > 0`.
  - "Overdue" rule (exact, per the brief): `followUpDate <= today` AND `stage ∈ {Applied, Interviewing, Offer}`.
  - Each chip is a `role="button" tabindex="0"` element — clickable AND Enter/Space-activatable. Clicking scrolls the matching `.job-card` into center view and triggers a 1.6s cyan flash (`@keyframes jobCardFlash`).
  - Snooze button on each chip — `+3d` — adds 3 calendar days to the follow-up date via `addDaysIso()`. `stopPropagation` prevents accidental scroll-to. Repeated clicks keep adding 3d (idempotent in effect, not state).
- Today is computed with `todayIsoLocal()` using local time, matching the `<input type="date">` value format — so DST/UTC drift can't false-flag a job.

### Modifications inside `renderJobs()`
- Step 0: remove any existing `.overdue-banner`, recompute `jobs.filter(isOverdue)`, inject fresh banner above the kanban when non-empty. Idempotent on every render — toggling a stage or snoozing immediately reflects in the banner.
- Each card now interleaves: company → role → aging → **follow-up badge** → stars → **prep progress** → linked-CV chips. Order chosen so the follow-up date is the first thing the eye hits when scanning a column (it's actionable), with prep progress just under stars.

### Seed data
- `JOBS_SEED_VER` bumped 4 → 5.
- `seedDefaultJobs()` updated — every seed job now has `followUpDate` and a partially-filled `prepChecklist`. With today fixed at 2026-05-13, the Elbit Smart Sensing job (Applied, followUp 2026-05-13) **demos the overdue banner on first load**.
- Added empty `JOBS_V5_ENTRIES = []` placeholder — V5's payload is the migration (which runs on every load), no new entries needed.

### Backward compatibility
- All Phase 1 invariants preserved: 9 stages, star rating, manual drag in Manual sort, CV↔Job never-downgrade, XSS escapes, legacy stage migration.
- New fields default cleanly: `undefined → false / null` migration is idempotent (only writes on actual change).

---

## How I tested

### 1. JS parse check
`new Function(<script body>)` parses cleanly. Script size ≈ 100.7 KB.

### 2. Headless smoke test (jsdom) — **84 / 84 PASS**
Test file: `D:\Claude Playground\.claude\worktrees\agent-a8bed6df113afaf1a\smoke2.js`
Date is **mocked to 2026-05-13** before script execution so overdue logic is deterministic.

Coverage groups:
- **JOBSEARCH-003 prep checklist** — `PREP_ITEMS` shape, `defaultPrepChecklist()`, migration seeds, `getPrepProgress()` counts (`done/total/pct`), partial-checklist legacy backfill.
- **JOBSEARCH-004 follow-up** — `todayIsoLocal()`, `addDaysIso()` (incl. month boundary), `getFollowUpClass()` (today=overdue, +6d=upcoming, +12d=distant, null=null), `isOverdue()` stage gating (Bookmarked/Rejected/Archived never overdue regardless of date).
- **Snooze** — `snoozeFollowUp()` adds +3d, can stack.
- **toggleChecklistItem** — flips state, persists to `localStorage.andy_jobs`.
- **Overdue banner integration** — banner appears with N chips when N overdue jobs exist; disappears when all overdue jobs leave nag stages; correctly excludes Bookmarked. Chip snooze button is present.
- **Prep progress on cards** — only renders on Bookmarked + Preparing; hidden on Applied/Rejected; text shows `N/5`.
- **Follow-up badge classes on cards** — `overdue` / `upcoming` / `distant` mapped correctly; no badge when null; Bookmarked downgrade from overdue → distant.
- **Modal round-trip** — `openJobModal()` loads followUpDate into input + checkboxes from job data; `saveJob()` persists toggled checkboxes + new followUpDate; works for both edit and "new job" flows.
- **XSS guard preserved** — company name `<script>alert(1)</script>` and role `<img onerror=...>` survive as escaped text in both the overdue chip and the underlying job card. No live `<script>` or `<img>` nodes.
- **Phase 1 regression** — `JOB_STAGES` still 9 items; never-downgrade still blocks CV "HTML Ready" from overwriting a job at Applied; `rating-desc` sort still ranks 5 → 2 → null.

### 3. Live HTTP smoke
`npx serve .` from `D:\Claude Playground` → `GET /dashboard/` returns HTTP 200, 178 KB.
`grep -c` for the new feature markers (`prep-checklist|overdue-banner|PREP_ITEMS|followUpDate|FOLLOWUP_NAG_STAGES|renderOverdueBanner|snoozeFollowUp|toggleChecklistItem`) → **49 hits** in the served HTML. Server stopped after verification.

### 4. Accessibility spot-checks
- Checkbox: native `<input type="checkbox">` inside a `<label>` → keyboard toggle (Space) and focus-visible ring inherited from the global `*:focus-visible` rule.
- Follow-up date: `<input type="date">` has a real `<label for="jFollowUp">` plus `aria-describedby="jFollowUpHint"` pointing at the policy hint.
- Overdue chip: `role="button"` + `tabindex="0"` + `onkeydown` handler for Enter/Space → fully keyboard-navigable, including `aria-label` on the snooze button.
- Banner has `role="region" aria-label="Overdue follow-ups"`.
- Progress bar has `role="progressbar"` with `aria-valuemin/max/now` on the `.prep-progress-bar`.

---

## UX judgment calls (please note before QA)

1. **Checklist visible for all stages** — the brief said "modal for jobs in any stage" so I show it even for Bookmarked/Rejected. The compact card indicator is only on Bookmarked/Preparing (where it adds signal) — terminal stages stay clean.
2. **Follow-up badge shown even for non-nag stages, but `overdue` styling is suppressed** — if Inon sets a follow-up date on an Archived job, the date still shows (as `distant` gray) but doesn't pulse red. The banner ignores it. Reasoning: he might want to remember a date for an Archived job without it becoming noise.
3. **Today=overdue** — strictly per the brief: `followUpDate <= today` counts as overdue. If he wants "due tomorrow" as a warning state instead, that's a one-line tweak in `getFollowUpClass`.
4. **Snooze duration = 3 days** — exact value the brief mentioned. Quick action; no per-click prompt. Multiple clicks stack.
5. **Banner location** — directly above the kanban container, inside the Jobs tab content, NOT in the top sticky bar. So it scrolls with the tab and never blocks other tabs. Per-tab clutter > global noise.
6. **No new top-level tabs introduced.** I stayed inside Jobs tab + job modal + CSS, exactly as Andy specified. No CV tab edits. ATS Match panel real estate (Yoni's next work) is untouched.
7. **Existing card-click → open-modal preserved.** Clicking anywhere on a card opens the modal as before; star clicks still `stopPropagation`. The new follow-up badge and prep progress on the card are visual-only — clicking them also opens the modal (no special handling needed since `card.addEventListener('click', …)` was untouched and the new elements bubble normally).

---

## Files

- Modified: `D:\Claude Playground\dashboard\index.html` (only file changed)
- Test script (worktree-local, not for prod): `D:\Claude Playground\.claude\worktrees\agent-a8bed6df113afaf1a\smoke2.js`

— Rex
