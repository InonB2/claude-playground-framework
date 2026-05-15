# Rex — Job Search Phase 3 REDO — DONE

**Tasks:** JOBSEARCH-006 (contacts sub-panel) + JOBSEARCH-009 (Today's Snapshot widget)
**Date:** 2026-05-14
**File touched (only one):** `D:\Claude Playground\dashboard\index.html` (absolute master path — not a worktree copy)
**Ready for:** Vera QA. **Do NOT commit — Andy commits after Vera signs off.**

---

## Why this REDO happened

Phase 3's JS + HTML was lost to a worktree glitch — only the CSS landed in master.
This pass re-applied the JS + data-model + HTML wiring against the **current** master,
which now also contains Yoni's AI Toolkit tab + Mack's Import Job feature (both added
after my original work). Verified end-to-end that I broke neither.

---

## Starting state (verified by reading current master)

- Contacts CSS (`.job-contacts` / `.contact-row` / `.contact-add-form` / `.job-contact-badge`) — present at lines ~427–481. **Reused as-is, no duplication.**
- Snapshot CSS (`.jobs-snapshot` / `.snapshot-cell` / `.target-*`) — present at lines ~521–546. **Reused as-is, no duplication.**
- `#jContacts` container — already in the job modal HTML (line ~1394). **Reused.**
- Contacts JS / snapshot JS / data-model fields / card badge — all **MISSING**. Re-created this pass.

---

## JOBSEARCH-006 — Contacts sub-panel

### Data model
- New field `contacts: [{name, role, linkedinUrl, lastContacted}]` on every job, default `[]`.
- `migrateLegacyJobStages()` now seeds `contacts = []` on legacy jobs **and** defensively backfills missing keys on existing contact objects (string-coerces name/role/linkedinUrl, `null` for missing lastContacted). Idempotent — only writes on actual change.

### Modal Contacts section (`renderModalContacts()` → `#jContacts`)
- List of contact rows: name / role / "LinkedIn ↗" link / last-contacted date (or "Never contacted").
- LinkedIn link is a real `<a target="_blank" rel="noopener">` and `stopPropagation`s its click.
- "+ Add contact" button reveals an inline `.contact-add-form` (name / role / LinkedIn URL / date inputs + Add/Cancel). `saveContact()` appends + persists + re-renders. Submits with no name are ignored; fully-empty submits silently close the form.
- Per-contact `×` delete button → `deleteContact(idx)` (true index, resolved from the sorted view).
- Contacts sorted by `lastContacted` **descending, nulls last** (`sortContacts()`).
- Persists immediately on every add/delete (`_persistModalContacts()` → `saveJobs()` + `renderJobs()`), so changes survive closing the modal without "Save" — same pattern as the Phase 2 prep checklist.

### Working-copy model
- `_modalContacts`: for a **saved** job it's a reference to `job.contacts` (mutate-in-place); for a **new** job it's a standalone array that `saveJob()` reads into the new job object.

### Card badge
- `renderContactBadge(job)` → `👤 N` pill when ≥1 contact, hidden at 0. Placed after the follow-up badge, before the stars.

## JOBSEARCH-009 — Today's Snapshot widget

- New field `createdAt: 'YYYY-MM-DD'` on every job. Migration seeds `j.date || todayIsoLocal()`; `saveJob()` stamps `todayIsoLocal()` on new jobs and preserves `createdAt` across edits.
- New consts: `WEEKLY_JOBS_TARGET = 5`, `APPLIED_OR_BEYOND_STAGES`.
- `getMostRecentMonday()` — most recent Monday inclusive, local time.
- `computeSnapshot()` → 4 stats; `renderSnapshot()` emits a 4-cell `.jobs-snapshot` strip, injected as a sibling **above the kanban and above the overdue banner** inside `#tab-jobs`, rebuilt on every `renderJobs()`.
- "Jobs added" cell color: `target-met` (green ≥5), `target-partial` (yellow 1–4), `target-none` (red 0). Overdue cell gets `alert` when >0.

## UX judgment calls (carried over from original spec, still apply)

1. **"Applications sent this week" — documented proxy.** No stage-change timestamps exist. Proxy = jobs whose stage is Applied-or-beyond AND whose `j.date` falls in the current week. Accurate going forward as Inon sets the Applied Date.
2. **"Next interview date" — earliest `followUpDate` among `Interviewing`-stage jobs.** Reuses the existing follow-up field; no redundant date field. Shows `—` when none.
3. **"This week" = since most recent Monday, inclusive.**
4. **Widget placement:** above overdue banner, above kanban, inside the Jobs tab content.
5. **Contacts shown for all stages** — no stage gating.

## Reconciliation with Mack's Import Job code

Mack's `impCommit()` forward-seeds `contacts: []` and `createdAt` on imported jobs using the
**exact field names** my migration/model uses (`contacts`, `createdAt`, `linkedinUrl`).
Verified aligned — no field-name mismatch. Migration stays idempotent on imported jobs
(it only writes when a field is missing).

## Seed data

Seed jobs updated with `contacts` + `createdAt` for a live demo (job-001: 1 contact;
job-003: 2 contacts incl. one null-date to demo nulls-last sort; job-003 followUpDate
set to 2026-05-20 so the snapshot's "Next interview" shows a real value).
`JOBS_SEED_VER` bumped 5 → 6; `JOBS_V6_ENTRIES = []` added (V6's payload is the migration,
which runs every load — existing users get `contacts`/`createdAt` backfilled, no data loss).

---

## MANDATORY verification — results

### 1. Grep marker check (proves JS landed on disk)
```
grep -c "renderContacts\|saveContact\|addContactRow"  →  4
grep -c "renderModalContacts"                          →  7
grep -c "computeSnapshot\|renderSnapshot\|getMostRecentMonday"  →  6
```
Full marker sweep (12 new function/var names): **35 occurrences** in the master file.
All 12 function/var definitions confirmed physically present (lines 2776–2940):
`_modalContacts`, `getContactCount`, `sortContacts`, `renderContactBadge`,
`renderModalContacts`, `addContactRow`, `cancelContactRow`, `saveContact`,
`deleteContact`, `getMostRecentMonday`, `computeSnapshot`, `renderSnapshot`.

### 2. JS parse check
`new Function(<script body>)` parses cleanly — script body 174,087 bytes.

### 3. jsdom smoke test — **50 / 50 PASS**
Date mocked to 2026-05-14 (Thursday); localStorage mocked. Coverage:
- Migration seeds `contacts[]` + `createdAt` on all 4 jobs; seed contacts present and correct.
- `sortContacts` — newest-first, nulls last.
- `getContactCount` / `renderContactBadge` — count correct, badge for ≥1, empty at 0.
- Card badge in rendered DOM — present on job-003 (2 contacts), absent on job-002 (0).
- Modal — 1 row for job-001; LinkedIn link `target=_blank` + `rel=noopener`; add button present.
- Add flow — form appears, `saveContact()` appends + persists to `localStorage.andy_jobs`, re-renders 2 rows sorted newest-first.
- XSS guard — name `<img src=x onerror=alert(1)>` and role `<b>boss</b>` escaped; no live `<img>` node.
- Delete flow — `deleteContact()` removes + persists.
- `saveJob` — keeps contacts + `createdAt` on edit; new job gets contacts from `_modalContacts` + `createdAt` stamped today.
- Snapshot — `getMostRecentMonday()` = 2026-05-11; `computeSnapshot()` addedThisWeek≥2, appliedThisWeek numeric, overdueCount≥1, nextInterview=2026-05-20; widget has 4 cells, `role="region"`, sits above kanban and above overdue banner.
- Phase 1/2 regression — 9 kanban columns, `renderStars` 5 buttons, `getPrepProgress` total=5, `isOverdue` intact, `WEEKLY_JOBS_TARGET` reflected as "Target: 5/week", migration idempotent on re-run.
- Yoni's toolkit (`tkInit`, `tkGenerate`) + Mack's import (`impCommit`, `openImportModal`) + ATS (`runAtsAnalyze`) all still present and parse.

### 4. Edited the absolute master path
`D:\Claude Playground\dashboard\index.html` — confirmed, not a worktree copy.

---

## Malfunctions found / prevention

None this pass. **Prevention note** (carried forward): the original loss was a half-wired
feature — CSS + modal HTML committed without JS. Recommend QA always confirms scaffolding
CSS/HTML has matching JS wiring; a feature isn't "started" until its render function exists.
This pass verified end-to-end wiring via the 50-test jsdom run before reporting.

## Files
- Modified: `D:\Claude Playground\dashboard\index.html` (only file changed)
- Smoke test was worktree-local and removed after passing (not for prod).

— Rex
