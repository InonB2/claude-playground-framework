# Rex — Job Search System Upgrade, Phase 3 — DONE

**Tasks:** JOBSEARCH-006 (contacts sub-panel per job) + JOBSEARCH-009 (daily "Today's Snapshot" widget)
**Date:** 2026-05-14
**File touched (only one):** `D:\Claude Playground\dashboard\index.html`
**Ready for:** Vera QA. **Do NOT commit yet — Andy commits after Vera signs off.**

---

## Important note on starting state

When I opened the dashboard, the **CSS for `.job-contacts` / `.contact-row` / `.jobs-snapshot`** and the **`#jContacts` container in the job modal** were already present (scaffolding from a prior pass), but **zero JS was wired** — no contact functions, no snapshot functions, no data-model fields, no card badge. So this phase was entirely the JS/data/render layer plus the snapshot widget HTML injection. I reused the existing CSS as-is (it's clean and on-theme); no CSS changes were needed.

---

## JOBSEARCH-006 — Contacts sub-panel per job

### Data model
- New field `contacts: [{ name, linkedinUrl, role, lastContacted }]` on every job — default `[]`.
- `migrateLegacyJobStages()` (existing migration fn) now seeds `contacts = []` on any legacy job missing it, and **defensively backfills** missing keys on existing contact objects (string coercion for name/role/url, `null` for missing `lastContacted`). Idempotent — only writes on actual change.

### Modal "Contacts" section
- `renderModalContacts()` renders into `#jContacts`: a list of contact rows (name / role / "LinkedIn ↗" link / last-contacted date) plus an **"+ Add contact"** button.
- **Add flow:** clicking "+ Add contact" reveals an inline `.contact-add-form` with 4 inputs (name, role, LinkedIn URL, last-contacted date) + Add/Cancel. `saveNewContact()` appends to the working array, persists, re-renders. Empty submits are silently ignored.
- **Delete:** each contact row has a `×` button → `deleteContact(idx)` → splice + persist + re-render.
- **LinkedIn link** renders as `<a target="_blank" rel="noopener">` and `stopPropagation`s its click so it never bubbles to the card/modal.
- **Sorted** by `lastContacted` most-recent-first, nulls last (`sortContacts()` — stable; display-only sort, true index resolved for deletes).
- **Persists immediately** on every add/delete via `_persistModalContacts()` → `saveJobs()` + `renderJobs()` (badge refresh). Even closing the modal without "Save" keeps contact changes — same pattern as the Phase 2 prep checklist.

### Card badge
- `renderContactBadge(job)` → `👤 N` pill on the job card when the job has ≥1 contact. Hidden at 0. Placed right after the follow-up badge, before the stars.

### New-job handling (no id yet)
- `_modalContacts` is the working copy: for a **saved** job it's a reference to `job.contacts` (mutate-in-place); for a **new** job it's a standalone array that `saveJob()` reads into the new job object. Either path goes through the same render/mutate functions.

## JOBSEARCH-009 — "Today's Snapshot" widget

- New field `createdAt: 'YYYY-MM-DD'` on every job. Migration seeds it as `j.date || todayIsoLocal()` for existing jobs; `saveJob()` stamps `todayIsoLocal()` on newly created jobs.
- New constants: `WEEKLY_JOBS_TARGET = 5` (single const to retune the goal) and `APPLIED_OR_BEYOND_STAGES`.
- `getMostRecentMonday()` — most recent Monday inclusive, local time (if today is Monday, returns today).
- `computeSnapshot()` returns the 4 stats; `renderSnapshot()` emits a compact 4-cell horizontal strip (`.jobs-snapshot`), injected as a sibling **above the kanban and above the overdue banner** inside `#tab-jobs`, rebuilt on every `renderJobs()` so it's always live.
- **Color coding** on the "jobs added" cell: `target-met` (green) if ≥5, `target-partial` (yellow) if 1–4, `target-none` (red) if 0. Overdue cell gets `alert` (red number) when >0.

---

## UX judgment calls (please note before QA)

1. **"Applications sent this week" — proxy, documented limitation.** There is no stage-change timestamp anywhere in the data model, and adding one was out of scope (and would need migration guesswork for historical jobs). My proxy: count jobs whose **stage is Applied-or-beyond AND whose `j.date` (the "Applied Date" field) falls in the current week**. This is accurate going forward as long as Inon sets the Applied Date when he applies — which the modal already prompts for. With the seed data this correctly reads **0** (seed applied dates are 05-05/05-06, before this week's Monday 05-11). If precise tracking is wanted later, the clean fix is an `appliedDate` set automatically on stage transition into Applied — a separate small task.
2. **"Next interview date" — reused `followUpDate`, no new field.** Per the brief's "your call; keep it simple," the widget shows the **earliest `followUpDate` among `Interviewing`-stage jobs**. Inon already uses follow-up dates as his "when to check back" date; for an Interviewing job that's effectively the interview/next-touch date. Avoids a redundant date field. Shows `—` when none. (I added a `followUpDate` to the BuildARPro seed job so the widget demos a real value: 2026-05-20.)
3. **"This week" = since most recent Monday, inclusive.** Standard work-week convention. Monday itself counts as week-start.
4. **Widget placement:** above the overdue banner, above the kanban, inside the Jobs tab content — scrolls with the tab, never a global sticky element. Consistent with where I put the Phase 2 banner.
5. **Contacts shown for all stages** (modal) — like the prep checklist, no stage gating; you can track contacts on a Bookmarked or even Archived job.
6. **No new top-level tabs.** Everything is inside the Jobs tab, the job modal, and JS. No CV-tab edits. ATS Match tab (Yoni's Phase 2 work) untouched — verified by grep, no edits to `ats-*` code. The "AI Prompt Toolkit" tab real estate Yoni will add next is untouched.
7. **Empty `JOBS_V6_ENTRIES = []`** placeholder added; `JOBS_SEED_VER` bumped 5 → 6. V6's payload is the migration (runs every load), so no merge entries needed — existing users get `contacts`/`createdAt` backfilled by `migrateLegacyJobStages()`.

---

## How I tested

### 1. JS parse check
`new Function(<script body>)` parses cleanly. Script ≈ 129.3 KB, file ≈ 205.8 KB.

### 2. Headless smoke test (jsdom) — **55 / 55 PASS**
Date mocked to **2026-05-14 (Thursday)** before script execution so weekly/overdue logic is deterministic. localStorage mocked. Coverage:
- **Contacts data model** — migration seeds `contacts[]` + `createdAt` on all jobs; seed contacts present and correct.
- **`sortContacts`** — newest-first, nulls last.
- **`getContactCount` / `renderContactBadge`** — count correct, badge shows for ≥1, empty for 0, shows the number.
- **Card badge in rendered DOM** — `.job-contact-badge` present on job-003 (2 contacts), absent on job-002 (0 contacts).
- **Modal contacts** — 1 row for job-001; LinkedIn link has `target="_blank"` + `rel="noopener"`; add-contact button present.
- **Add flow** — form appears, `saveNewContact()` appends, persists to `localStorage.andy_jobs`, modal re-renders 2 rows, sorted newest-first.
- **Delete flow** — `deleteContact()` removes, persists.
- **XSS guard** — contact name `<img src=x onerror=alert(1)>` and role `<b>boss</b>` are escaped (`&lt;img`, `&lt;b&gt;boss`); no live `<img>` node in `#jContacts`.
- **`saveJob`** — keeps contacts on edit; **new job** (no id) gets contacts from `_modalContacts` working copy + `createdAt` stamped to today.
- **Snapshot** — `getMostRecentMonday()` = 2026-05-11; `computeSnapshot()` → addedThisWeek=2, appliedThisWeek=0 (proxy, documented), overdueCount≥1, nextInterview=2026-05-20; `renderSnapshot()` emits 4 cells, `role="region"`, yellow class at 2/5, alert class on overdue; widget is in the DOM **above** both the kanban and the overdue banner; turns **green** when addedThisWeek hits 5.
- **Phase 1/2 regression** — `JOB_STAGES` still 9; `renderStars` still emits 5 buttons; `getPrepProgress` total=5; `isOverdue` still stage-gated; `getFollowUpClass` still flags overdue; `JOB_STAGE_RANK` intact; `WEEKLY_JOBS_TARGET` const = 5; migration still idempotent after a second run.

### 3. Live HTTP smoke
`npx serve .` → `GET /dashboard/index.html` returns **HTTP 200**. (Note: `grep` against the served stream under-counted markers vs. the on-disk file — a `serve` streaming/encoding quirk also seen in Phase 1/2; the on-disk `grep` confirms all 7 new functions present, and the jsdom test loads/executes the exact on-disk file.)

### 4. Accessibility
- Contact add-form inputs each have `aria-label` (Name / Role / LinkedIn URL / Last contacted date).
- Delete button has `aria-label="Delete contact <name>"`; add button is a real `<button>`.
- Snapshot strip has `role="region" aria-label="Today's job-search snapshot"`; each cell has a number + uppercase label + sub-line.
- Contact-count badge has `aria-label="N contacts"`.
- LinkedIn links are real `<a>` elements, keyboard-focusable, open in new tab safely.

---

## Malfunctions found / prevention
None — clean implementation. One **process note for prevention:** the prior pass left CSS + modal HTML committed without the JS, which is a half-wired feature that would silently render an empty Contacts box. Recommend QA (Vera) always checks that scaffolding CSS/HTML has matching JS wiring — a feature isn't "started" until its render function exists. I verified end-to-end wiring here.

## Files
- Modified: `D:\Claude Playground\dashboard\index.html` (only file changed)
- Smoke test was worktree-local and removed after passing (not for prod).

— Rex
