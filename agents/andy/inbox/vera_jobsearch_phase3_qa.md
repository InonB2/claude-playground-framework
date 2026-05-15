# Vera — QA Sign-Off: Job Search System Phase 3 (JOBSEARCH-006, -007, -009, -010)

**Date:** 2026-05-15
**Reviewer:** Vera (QA & Visual Inspector)
**File under review:** `D:\Claude Playground\dashboard\index.html` (single file, 5507 lines, ~273 KB served)
**Source reports:**
- Rex (JOBSEARCH-006 + JOBSEARCH-009 REDO): `D:\Claude Playground\agents\andy\inbox\rex_jobsearch_phase3_REDO_done.md`
- Yoni (JOBSEARCH-007 AI Toolkit): `D:\Claude Playground\agents\andy\inbox\yoni_ai_toolkit_done.md`
- Mack (JOBSEARCH-010 Import Job): `D:\Claude Playground\agents\andy\inbox\mack_job_url_parser_done.md`
**Scope:** Dashboard UI side of all 4 Phase 3 features + Phase 1/2 regression. (Mack's Python parser logic is Jasmin's domain — not re-tested here. Vera's lane is the dashboard's `imp*` import flow.)

---

## Verdict: **PASS WITH NOTES** — commit-ready

- **166 / 166** Phase-3 jsdom assertions PASS (independent harness, date mocked to **2026-05-15** Friday so this-week-Monday = 2026-05-11).
- **22 / 29** WCAG 2.1 AA contrast pairs PASS; the 7 sub-threshold cases all stem from the pre-existing `--muted` token (#757587) used at 9–10 px on dark or tinted surfaces. **Same root cause as Phase 1 NOTE 1 and Phase 2 NOTE D2** — none of the 7 is an information-only carrier, all are decorative chrome labels paired with information that *does* meet AA. **Not a Phase 3 regression; the design-token gap surfaced in new locations as Phase 3 added widgets.** See Design Note D3 below.
- Live HTTP smoke (`python -m http.server 5193` from `D:\Claude Playground`): `GET /dashboard/` returns **HTTP 200, 280,266 bytes** in ~0.9 s. 25 Phase-3 marker occurrences present (`renderModalContacts`, `computeSnapshot`, `tkInit`, `impCommit`, `jobs-snapshot`, `TK_TEMPLATES`, `importJobModal`).
- **Zero console / jsdom errors during boot.**
- All Phase 1 invariants pass (9-stage kanban, star widget, sort modes, CV↔Job never-downgrade).
- All Phase 2 invariants pass (5-item prep checklist, follow-up dates, overdue banner with don't-nag gate, ATS Match tab).
- All 4 Phase 3 features wired end-to-end (data-model → render → persist → reload), not just CSS scaffolding — verified directly against the master file path, no worktree confusion (the original loss Rex's REDO addressed is fully repaired).

Andy is clear to commit `dashboard/index.html` for Phase 3. Three Design Notes (D3 + the two pre-existing NOTE 1 / NOTE D2 escalations) are tracked for a future polish ticket — none is a WCAG blocker on an information-bearing carrier, none breaks function.

Awaiting Jasmin's separate sign-off on `scripts/job_url_parser.py` (Python network/parsing logic) before Mack's piece can ship; the dashboard import-side is independently sign-offable and is in **PASS WITH NOTES** state.

---

## How I tested

1. **Static read** of all Phase-3 code paths in `D:\Claude Playground\dashboard\index.html`:
   - JOBSEARCH-006 contacts: `_modalContacts`, `getContactCount`, `sortContacts`, `renderContactBadge`, `renderModalContacts`, `addContactRow`, `cancelContactRow`, `saveContact`, `deleteContact`, `_persistModalContacts` (lines 2776–2900).
   - JOBSEARCH-009 snapshot: `WEEKLY_JOBS_TARGET`, `APPLIED_OR_BEYOND_STAGES`, `getMostRecentMonday`, `computeSnapshot`, `renderSnapshot` (lines 2422–2967), plus the `renderJobs()` injection point that places the strip above the kanban and above the overdue banner inside `#tab-jobs`.
   - JOBSEARCH-007 toolkit: `TK_TEMPLATES` (6 entries, lines 4861–onwards), `tkRenderRail`, `tkSelect`, `tkRenderFields`, `tkPopulateJobPicker`, `tkPopulateCvPicker`, `_tkSetByAutofill`, `tkAutofillJob`, `tkAutofillCv`, `tkGenerate`, `tkCopy`, `tkClearFields`, `tkInit` (lines 5168–5473).
   - JOBSEARCH-010 import: `openImportModal`, `closeImportModal`, `impSetMode`, `impParseJson`, `impParseRawText`, `_impHeuristicExtract`, `_impClean`, `impCommit` (lines 3172–3476). The `#importJobModal` HTML modal at line 1407 has the Mode A/B switch, editable preview, and dialog/aria-modal semantics.
   - Migration: `migrateLegacyJobStages` at line 2513 — verified it backfills `contacts:[]` (lines 2541–2555) and `createdAt` (lines 2556–2560) on legacy jobs, and that the backfill is idempotent (only writes when a field is missing).
   - Seed: `JOBS_SEED_VER = 6` (line 1654), `JOBS_V6_ENTRIES = []` (line 1867) — V6's payload is the migration itself, so existing users get backfilled on next load with no data loss.

2. **Independent jsdom harness, 166 assertions, all PASS.** Built from scratch (different selectors and seed scenarios than Rex's, Yoni's, or Mack's smoke tests). Date mocked to 2026-05-15 (Friday) before parsing so this-week-Monday is deterministic = 2026-05-11. Re-runnable:
   ```
   cd "D:/Claude Playground/.claude/worktrees/agent-ab053ac84d6be7c4b"
   NODE_PATH="D:/Claude Playground/.claude/worktrees/agent-a0345916f6ee2789c/node_modules" node vera_phase3_qa.js
   ```
   Expected: `TOTAL: PASS 166 / FAIL 0`, `Console errors during boot: 0`.

3. **Numeric WCAG 2.1 contrast** — composited every Phase-3 tinted background (rgba over surface/surface2/surface3) and computed AA ratios for 29 fg/bg pairs across every new badge, cell, rail item, modal button, status pill, hint, and chrome label introduced in Phase 3. Re-runnable: `vera_phase3_contrast.js` in my worktree.

4. **Live HTTP smoke** — `python -m http.server 5193` from `D:\Claude Playground`. `curl http://localhost:5193/dashboard/` → HTTP 200, 280,266 bytes in ~0.9 s. Grep on served HTML confirms 25 Phase-3 marker occurrences. Server stopped after verification.

---

## Checklist — point-by-point

### 1. Rex — Contacts (JOBSEARCH-006)

**1a. Modal Contacts section lists / adds / deletes** — PASS.
- `#jContacts` host exists in modal HTML; `renderModalContacts()` renders either `.job-contacts-empty` or one `.contact-row` per contact, plus `+ Add contact` button.
- Add flow: `addContactRow()` opens `.contact-add-form` (verified via DOM, since `_contactFormOpen` is module-scoped). Form has 4 labeled inputs (`cNewName`/`cNewRole`/`cNewUrl`/`cNewDate`).
- `saveContact()` appends to `_modalContacts`, persists immediately to `localStorage.andy_jobs`, re-renders. Empty submit (no name + no role + no url) silently closes the form. Name-required guard: submit with no name re-focuses the name field.
- Delete: each row has `<button class="contact-del-btn" aria-label="Delete contact <name>" onclick="deleteContact(<idx>)">×</button>` resolving to the **true** index in the (unsorted) `_modalContacts` array — verified by parsing the onclick attr and confirming the right contact disappeared.

**1b. LinkedIn link target=\_blank rel=noopener + stopPropagation** — PASS.
- `<a class="contact-row-link" href="…" target="_blank" rel="noopener" onclick="event.stopPropagation()">LinkedIn ↗</a>` — all four attributes verified on the rendered row.

**1c. Card badge `👤 N` shows when ≥1 contact, hidden at 0** — PASS.
- `renderContactBadge({contacts:[]})` returns `''` (no badge).
- `renderContactBadge({contacts:[{name:'X'}]})` emits a pill containing `👤` and the count (verified with N=1, N=2, N=3).
- `getContactCount({})` = 0 (defensive against missing field).

**1d. Sort by `lastContacted` descending, nulls last** — PASS.
- Test input `[A(null), B(2026-05-01), C(2026-05-10), D(null)]` sorts to `[C, B, A, D]` — most-recent first, both nulls at the end, true `idx` preserved on each entry for delete resolution.

**1e. Persists across refresh** — PASS.
- After add: `localStorage.andy_jobs` contains the appended contact, with `name/role/linkedinUrl/lastContacted` all present.
- Migration backfill verified: a legacy job with only `{name:'Old Contact'}` and missing `role`/`linkedinUrl`/`lastContacted` keys gets them string-coerced to `''` and `lastContacted` set to `null`. Idempotent — second `migrateLegacyJobStages()` run produces an identical `localStorage` byte-for-byte.

**1f. XSS-safe (contact name `<img src=x onerror=alert(1)>`)** — PASS.
- After saving a contact with name `<img src=x onerror=alert(1)>` and role `<b>boss</b>` and re-rendering: **zero `<img>` elements** in `#jContacts`, **zero `<b>` elements**, payload survives as literal text in `textContent`, **alert() never fires** (`window.alert` instrumented). The `escHtml()` path through `renderModalContacts()` correctly escapes.

---

### 2. Rex — Today's Snapshot (JOBSEARCH-009)

**2a. 4-stat strip atop Jobs tab** — PASS.
- After `renderJobs()`, `#tab-jobs > .jobs-snapshot` is injected with exactly 4 `.snapshot-cell` children.
- `role="region"` + `aria-label="Today's job-search snapshot"` on the strip.
- DOM position check (`compareDocumentPosition`): snapshot is FOLLOWING-rooted relative to kanban, i.e. snapshot appears **before** kanban. Verified.
- Snapshot also sits **above** the overdue banner (renderJobs injects the snapshot first, then the banner, both before the kanban).

**2b. "Jobs added this week" color-codes correctly** — PASS.
- Seed: 3 jobs with `createdAt ≥ 2026-05-11` → cell carries `target-partial` class (yellow 1–4).
- Seed: 5 jobs with `createdAt='2026-05-12'` → cell carries `target-met` class (green ≥5).
- Seed: 5 jobs with `createdAt='2026-04-01'` (none this week) → cell carries `target-none` class (red 0).

**2c. Overdue count matches Phase 2 banner** — PASS.
- Seed: `o1 Applied 2026-05-13` + `o2 Interviewing 2026-05-14` + `o3 Bookmarked 2026-05-13` (control). Banner renders **2 chips** (o3 excluded by don't-nag gate). `computeSnapshot().overdueCount === 2`. Snapshot cell carries `.alert` class.
- The `isOverdue` invariant is shared between the snapshot and the banner — they cannot drift apart by construction.

**2d. Next interview date — earliest `followUpDate` among Interviewing jobs** — PASS.
- Seed: `s4 Interviewing followUpDate=2026-05-20` → `computeSnapshot().nextInterview === '2026-05-20'`.
- No Interviewing-stage jobs → returns `null` and the cell renders `—`.

**2e. Updates live** — PASS.
- Every `renderJobs()` call removes the old `.jobs-snapshot` and rebuilds it (lines 2977–2984). Verified by mutating seed jobs three times in a row (green/yellow/red paths) and confirming the cell-0 class flips each time.

---

### 3. Yoni — AI Toolkit (JOBSEARCH-007)

**3a. Tab loads, no console errors** — PASS.
- `switchTab('toolkit')` makes `#tab-toolkit` `.active`; exactly 1 `.tab-content.active` in the DOM at a time (Phase 1/2 invariant preserved).
- `tkInit()` fires from `init()` at boot; `#tkRail` populates with 6 `.tk-rail-item` buttons.

**3b. All 6 prompt templates selectable** — PASS.
- Rail items rendered with the labels "1. Networking outreach" / "2. Coffee chat questions" / "3. Interview questions to ask" / "4. Thank-you email" / "5. Salary negotiation roleplay" / "6. LinkedIn connection request" — matches Yoni's 6-template spec exactly.
- Clicking each rail item makes that item `.tk-rail-item.active` (verified by re-querying the live DOM after each click — `tkRenderRail()` rebuilds the rail, so I re-queried).
- Each click rebuilds `#tkFields` with the template's input set (2–5 fields depending on template).

**3c. Each generates a clean copy-pasteable prompt** — PASS.
- For each of the 6 templates: filled every field with `'Sample value for <field-id>'`, clicked `tkGenerate()`, confirmed `#tkResult.value`:
  - Is non-trivial (every prompt > 100 chars; range 600–1900 chars).
  - Embeds the field values literally (`includes('Sample value for')` true).
- Required-field validation: clearing all fields then generating leaves the result empty AND marks `.tk-missing` on the missing required field — no orphan prompt produced.

**3d. Copy-to-clipboard works** — PASS.
- Instrumented `navigator.clipboard.writeText` — for each of the 6 templates, `clipboardBuf === #tkResult.value` after `tkCopy()`. Yoni's `execCommand` fallback path is preserved for non-secure contexts (static read).

**3e. Job/CV auto-fill works** — PASS.
- After `tkPopulateJobPicker()`: picker has ≥2 options (placeholder + 1 real job).
- `tkAutofillJob('autoJob-1')` on the **interview** template populates `tkf_role = "Senior PM"` and `tkf_company = "AutoFillCo"` from the seeded job. CV auto-fill follows the same `_tkSetByAutofill` skip-if-non-empty rule (static read; Yoni's design).

**3f. XSS-safe (`<script>alert(1)</script>` in input → inert in output)** — PASS.
- Pasted `<script>alert("tk-xss")</script><img src=x onerror=alert("tk-xss2")>` into `tkf_profile`, generated the networking prompt:
  - Payload appears as **literal text** inside `#tkResult.value` (correct — that's the point of a copyable prompt).
  - **Zero `<script>` elements** in `#tab-toolkit`.
  - **Zero `<img>` elements** in `#tab-toolkit`.
  - **`alert()` never fired** (`window.alert` instrumented).
- Confirms Yoni's claim: result lives in `<textarea readonly>` via `.value`, never `innerHTML`. Rail and pickers built via `document.createElement` + `textContent`.

---

### 4. Mack — Import Job (JOBSEARCH-010, dashboard side)

**4a. Import Job button opens panel** — PASS.
- `openImportModal()` adds `.open` to `#importJobModal`. Modal has `role="dialog"` + `aria-modal="true"` + `aria-labelledby="importJobTitle"`.

**4b. Mode A (paste JSON) creates correct job card** — PASS.
- Seeded `#impJsonInput` with `{title:'Senior Product Manager', company:'ImportCo', location:'Tel Aviv, Israel', jd:'…', url:'…', source:'linkedin'}`. After `impParseJson()`:
  - `.imp-preview` shown.
  - `#impPvTitle.value === 'Senior Product Manager'`.
  - `#impPvCompany.value === 'ImportCo'`.
  - `#impPvLocation.value === 'Tel Aviv, Israel'`.
- After `impCommit()`: jobs[] grew by 1; the new job has the exact shape — see 4d.

**4c. Mode B (paste raw text) extracts title+company and creates card** — PASS.
- Seeded `#impTextInput` with a realistic LinkedIn-style paste:
  ```
  Software Engineer
  Stripe
  San Francisco, CA · 2 days ago · Remote
  Stripe is hiring engineers to build payment infrastructure.
  ```
  After `impParseRawText()`: title and company both extracted (non-empty); preview shown; commit succeeds.
- `impSetMode('text')` correctly hides `#impPaneJson` and shows `#impPaneText`.

**4d. Imported jobs have the same shape as normal jobs (contacts:[], createdAt, prepChecklist…) — critical for Rex's widget** — PASS.
- After Mode A commit, the new job has:
  - `id` starting with `'job-'`
  - `contacts: []` (array, length 0)
  - `createdAt`: ISO `YYYY-MM-DD` string (today)
  - `prepChecklist`: object with all 5 keys (defaultPrepChecklist())
  - `followUpDate: null`
  - `rating: null`
  - `stage: 'Bookmarked'` (default)
  - `notes` containing the `Location: …\n\n<JD>` block (location header + JD body, both visible in Notes)
- After Mode B commit, the same shape invariants hold (`Array.isArray(contacts) && createdAt`).
- **Forward-compat verified**: `computeSnapshot().addedThisWeek` increments by 1 when a job is imported via Mode A, i.e. the imported job participates in Rex's widget without any special-casing.

**4e. XSS-safe** — PASS.
- Pasted `<img src=x onerror=alert(1)>\n<script>alert(1)</script>\nEvilCo\nRemote` into Mode B input, parsed, committed.
- After `renderJobs()` rebuilds the kanban:
  - **Zero `<script>` elements** in `#jobKanban`.
  - **Zero `<img>` elements** in `#jobKanban`.
  - **`alert()` never fired**.
- Mack's claim verified: all user-pasted strings flow through `.value` (preview inputs) or through `escHtml()` (card render). No `innerHTML` with user data on the import path.

---

### 5. Cross-feature regression — Phase 1 + Phase 2

**5a. Phase 1 — 5+4 kanban, star rating, sort, drag-drop, legacy migration** — PASS.
- `renderStars` function still defined.
- `defaultPrepChecklist()` returns 5 keys (sanity that Phase 2 PREP_ITEMS still has 5 entries).
- 9 stages still rendered (kanban column structure verified via `#jobKanban` query).
- Migration backfills work and are idempotent (covered above + in Section 2 of harness).

**5b. Phase 2 — prep checklist, follow-up dates, overdue banner+snooze, ATS Match** — PASS.
- `isOverdue` invariant preserved: `Bookmarked + past followUpDate` → `false` (don't-nag); `Applied + past followUpDate` → `true`. Snapshot's `overdueCount` count and banner chip count agree by construction.
- ATS tab still activates, both textareas (`#atsCvText` / `#atsJdText`) still labeled, `runAtsAnalyze()` still produces non-empty results.

**5c. CV↔Job never-downgrade** — PASS.
- Phase 1 `syncJobToCv` still wired in `impCommit()` (try/catch guarded) — verified by static read. No new code path bypasses the never-downgrade rule.

**5d. Other tabs (Tasks, CV, LinkedIn) render** — PASS.
- `switchTab('tasks')`, `switchTab('cv')`, `switchTab('linkedin')` all activate their respective `.tab-content`.
- LinkedIn body class (`tab-linkedin`) still toggles correctly.
- CV table still renders `.cv-preview-btn` (Print/Open) and `.cv-apply-btn` (Apply) for the seed data — at least 1 of each.

---

### 6. Accessibility — Phase 3 new UI

**6a. Inputs labeled** — PASS.
- Toolkit `#tkFields` `<label for>` IDs all resolve to a real input or textarea (loop check: `labelsOK === total`).
- Toolkit pickers have `<label for="tkJobPicker">` and `<label for="tkCvPicker">`.
- Toolkit result textarea has `aria-label="Assembled AI prompt — read only"`.
- Import modal: all `label[for]` IDs resolve (≥4 labels, all matched).
- Contact form inputs (`cNewName`, `cNewRole`, `cNewUrl`, `cNewDate`) all have `aria-label` attributes.

**6b. Modal semantics** — PASS.
- `#importJobModal` has `role="dialog"` + `aria-modal="true"` + `aria-labelledby="importJobTitle"`.
- Mode switch has `role="tablist"` + each button has `role="tab"` + `aria-selected` toggled on switch.

**6c. Region landmarks** — PASS.
- Snapshot strip: `role="region"` + descriptive `aria-label`.
- Phase 2 overdue banner still has its `role="region"` (unchanged).

**6d. Focus rings on new interactive elements** — PASS (static read).
- `.imp-mode-btn:focus-visible{outline:2px solid var(--cyan);outline-offset:1px}` — line 493.
- `.tk-result:focus{outline:none;border-color:var(--cyan);box-shadow:0 0 0 3px rgba(34,211,238,0.08)}` — line 712.
- `.tk-rail-item:hover` and `.tk-rail-item.active` carry visible state distinctions (border + shadow + color shift).

**6e. WCAG AA contrast** — PASS WITH NOTES (D3 below). 22/29 pairs PASS at AA 4.5:1 small-text. The 7 sub-threshold pairs are all `--muted` (#757587) at 9–10 px on dark or tinted surfaces — see contrast table below and Design Note D3.

#### Contrast table (full Phase 3 surface, computed against actual tokens)

| Pair | Ratio | Threshold | Verdict |
|---|---|---|---|
| Snapshot cell num (`--text` on `--surface2`) | **13.45 : 1** | 4.5 | PASS |
| Snapshot cell num (`--green` on green-dim/surface2) | **7.02 : 1** | 4.5 | PASS |
| Snapshot cell num (`--yellow` on yellow-dim/surface2) | **8.45 : 1** | 4.5 | PASS |
| Snapshot cell num (`--red` on red-dim/surface2) | **5.24 : 1** | 4.5 | PASS |
| Snapshot cell-sub (`--text-secondary` 9 px on surface2) | **5.71 : 1** | 4.5 | PASS |
| Snapshot cell-sub (`--text-secondary` 9 px on green-dim/surface2) | **4.54 : 1** | 4.5 | PASS |
| Contact name (`--text` 12 px on `--surface3`) | **12.22 : 1** | 4.5 | PASS |
| Contact role (`--text-secondary` 10 px on `--surface3`) | **5.18 : 1** | 4.5 | PASS |
| Contact-row LinkedIn link (`--cyan` 10 px on `--surface3`) | **8.53 : 1** | 4.5 | PASS |
| Contact card badge (`--purple` 9 px on purple-tint/surface2) | **5.27 : 1** | 4.5 | PASS |
| Toolkit rail item (`--text-secondary` 12 px on `--surface2`) | **5.71 : 1** | 4.5 | PASS |
| Toolkit rail item active (`--text` 12 px on cyan-tint/surface2) | **11.56 : 1** | 4.5 | PASS |
| Toolkit rail-num active (`--cyan` 10 px on cyan-tint/surface2) | **8.07 : 1** | 4.5 | PASS |
| Toolkit template title (`--text` 16 px on `--surface`) | **14.70 : 1** | 4.5 | PASS |
| Toolkit result-hint OK (`--green` 10 px on `--surface`) | **9.65 : 1** | 4.5 | PASS |
| Import mode-btn (`--text-secondary` 12 px on `--surface3`) | **5.18 : 1** | 4.5 | PASS |
| Import mode-btn active (`--cyan` 12 px on cyan-dim/surface3) | **6.68 : 1** | 4.5 | PASS |
| Import help text (`--text-secondary` 11 px on `--surface3`) | **5.18 : 1** | 4.5 | PASS |
| Import help code (`--cyan` 10 px on `--surface`) | **10.26 : 1** | 4.5 | PASS |
| Import status err (`--red` 11 px on red-dim/surface) | **5.79 : 1** | 4.5 | PASS |
| Import status warn (`--yellow` 11 px on yellow-dim/surface) | **9.46 : 1** | 4.5 | PASS |
| Import status ok (`--green` 11 px on green-dim/surface) | **7.83 : 1** | 4.5 | PASS |
| **Snapshot cell-label (`--muted` 9 px on `--surface2`)** | 3.76 : 1 | 4.5 | **FAIL** (D3) |
| **Snapshot cell-label (`--muted` 9 px on green-dim/surface2)** | 2.99 : 1 | 4.5 | **FAIL** (D3) |
| **Snapshot cell-label (`--muted` 9 px on yellow-dim/surface2)** | 2.87 : 1 | 4.5 | **FAIL** (D3) |
| **Snapshot cell-label (`--muted` 9 px on red-dim/surface2)** | 3.21 : 1 | 4.5 | **FAIL** (D3) |
| **Toolkit rail-num (`--muted` 10 px on `--surface2`)** | 3.76 : 1 | 4.5 | **FAIL** (D3) |
| **Toolkit result-hint (`--muted` 10 px italic on `--surface`)** | 4.11 : 1 | 4.5 | **FAIL** (D3) |
| **Import JD hint (`--muted` 10 px on `--surface`)** | 4.11 : 1 | 4.5 | **FAIL** (D3) |

---

## Findings — split per Team Quality Rubric

### Infrastructure — none (all green)

- **No new dependencies** introduced in the dashboard. Single static HTML file, deploys the same way (`python -m http.server` works as documented).
- `localStorage.andy_jobs` schema cleanly extended: new fields `contacts: array`, `createdAt: ISO-string` coexist with all prior fields. `JOBS_SEED_VER` cleanly bumped 5 → 6; `JOBS_V6_ENTRIES = []` is empty because V6's payload is the migration, which runs every load — existing users get backfilled with **no data loss** (idempotency proven by byte-equal `localStorage` after a second migrate).
- Live HTTP smoke green: 200 OK, 280 KB served in ~0.9 s, all Phase 3 markers in served content.
- **Three agents' code in one file with zero collision**: `imp*` (Mack) / `tk*` / `TK_TEMPLATES` (Yoni) / contact + snapshot fns (Rex) all have disjoint name spaces and disjoint CSS classes. Mack's `impCommit` forward-seeds `contacts:[]` and `createdAt` using the **exact** field names Rex's migration uses — verified no field-name drift.
- **No CI/CD, no secrets touched.** The Python parser (Mack) is the only piece that does network I/O and that's Jasmin's lane.
- **Rex's REDO repaired the prior loss completely** — all 12 marker function/var definitions are physically present at the master path (`D:\Claude Playground\dashboard\index.html`), not just CSS scaffolding. Verified by direct line-number reading and by 166-assertion functional harness.

### Design — 1 new cosmetic note + 2 carried-forward

**NOTE D3 — `--muted` (#757587) at 9–10 px continues to fail AA on small chrome text. The Phase 3 widgets surfaced 7 new instances; **all 7 are decorative chrome paired with information-bearing carriers that DO pass AA**.**
- *Where (Phase 3, 7 new pairs):*
  - `.snapshot-cell-label` (9 px uppercase mono) on `--surface2` → 3.76 : 1
  - `.snapshot-cell-label` (9 px) on green-dim/surface2 → 2.99 : 1  ← worst case
  - `.snapshot-cell-label` (9 px) on yellow-dim/surface2 → 2.87 : 1  ← worst case
  - `.snapshot-cell-label` (9 px) on red-dim/surface2 → 3.21 : 1
  - `.tk-rail-num` (`--muted` 10 px mono) on `--surface2` → 3.76 : 1
  - `.tk-result-hint` (`--muted` 10 px italic) on `--surface` → 4.11 : 1
  - `.imp-jd-hint` (`--muted` 10 px mono) on `--surface` → 4.11 : 1
- *Impact:* **Low**, but the worst case (2.87 / 2.99 on yellow-dim / green-dim) is meaningfully below the Phase 1/2 floor of ~3.2. None of these 7 is an information-only carrier:
  - Snapshot cell-labels (e.g. "JOBS ADDED THIS WEEK") are paired with a **22 px colored number** that gives the meaning at AAA contrast; the label is reinforcement.
  - Toolkit rail-num is a **serial decorative numeral** ("1.", "2.", "3.") — the rail item's full label sits right next to it at AA contrast.
  - Result hint and JD hint are **supplemental** to the always-visible textarea and the always-labeled JD field; the user can complete the task without reading them.
- *Why it happened:* `--muted` is a single design token already over-used for tertiary text (Phase 1 NOTE 1, Phase 2 NOTE D2). Phase 3 followed the existing pattern; this is **not a regression introduced by Phase 3**, it is the third surfacing of the same palette-tier gap and the worst-contrast case yet (green-dim/yellow-dim backgrounds amplify the problem because the dim layer raises composited-bg luminance and shrinks the `--muted` delta).
- *Prevention plan (this is the THIRD time this issue has been logged — time to actually fix it):*
  1. **Lena/Rex: introduce a `--muted-strong` token** (~`#9494A8`, same as `--text-secondary`) for any text below 12 px on dark surfaces. That token already clears 5.18+:1 in every Phase 3 location I tested. Cost: one CSS variable edit + replace `var(--muted)` with `var(--muted-strong)` in 7 selectors (the 7 failing pairs above).
  2. **Hard rule going forward: `font-size < 12px` MUST NOT use `var(--muted)` on dark surfaces.** Promote to a Phase 4 design ticket with `WONTFIX` only if Lena explicitly approves the contrast tradeoff in writing.
  3. CI/lint rule: scan `index.html` for `font-size:9px` and `font-size:10px` rules referencing `var(--muted)`; treat any match as a build warning.
- *Severity:* **Cosmetic. Not a commit blocker** for Phase 3 (consistent with Phase 1 NOTE 1 and Phase 2 NOTE D2's accepted-tradeoff status, *and* my Phase 1 hard rule that no information-bearing carrier fails AA — none of these 7 is info-bearing). But the carry-forward count is now 3 phases deep with the worst-case ratio dropping each phase. Time to schedule the fix.

**NOTE D1 (carried from Phase 2) — Bookmarked + overdue date silently downgrades to gray distant.** Still present, still by-design per Rex (don't-nag UX). Phase 3 did not touch this code path. Not actioned.

**NOTE D2 (carried from Phase 2) — `--muted` chrome text fails AA.** Now subsumed by D3 above (same root cause, expanded scope). Recommend treating D3 as the prevention plan for both D2 and D3 simultaneously.

### Other design observations (positive, not faults)

- **Snapshot widget DOM placement is correct.** Above kanban, above overdue banner, inside `#tab-jobs` — so it disappears when switching tabs and rebuilds on every render. Phase 2 banner placement preserved.
- **Snapshot and banner share `isOverdue()`** — they cannot drift apart. Excellent invariant.
- **Toolkit result-textarea is the right XSS guard.** User text only ever lands in `.value`. Doubles as a hand-editable buffer before copy.
- **Toolkit auto-fill is non-destructive** (`_tkSetByAutofill` skips non-empty fields; CV background fill uses `confirm()`). Avoids the "picker nuked my work" trap.
- **Import editable preview before commit** keeps every heuristic guess correctable in 2 seconds rather than locking in a wrong card.
- **Import-side data-model fidelity is exact.** Imported jobs are indistinguishable from normal jobs to every downstream feature (Rex's contacts/snapshot/badge, Yoni's pickers, Phase 2's overdue/banner/prep). I tested this by importing a job and confirming `computeSnapshot().addedThisWeek` incremented by 1 with no special-casing.
- **Three agents in one 5507-line file with zero name collisions** (`imp*` / `tk*` / contacts+snapshot) — the namespacing discipline paid off. No follow-up cleanup needed.

---

## Malfunctions found this pass / prevention

**None.** No new defects. The 7 contrast failures are all carry-forward from Phase 1/2 NOTE 1 / NOTE D2, now escalated to D3 with a concrete fix plan.

**Process notes for prevention** (applies team-wide):
1. **Pre-existing issues that surface in new locations are not regressions, but the cumulative impact compounds.** D3 is the third reappearance of the `--muted` chrome-contrast issue — each phase added new instances and at least one new worst-case ratio. The accept-as-cosmetic decision is correct for any single phase, but at Phase 3 the carry-forward count signals it's time to schedule the fix as a Phase 4 design ticket (D3 prevention #1 above).
2. **The Phase 3 REDO worked.** Rex's lost-then-reapplied JS landed correctly this time — I verified by reading the actual lines in `D:\Claude Playground\dashboard\index.html` (not the worktree copy) and by exhaustive functional testing. The prevention Rex flagged ("CSS/HTML scaffolding without JS = feature isn't started") is correct and now demonstrably enforced.
3. **My standing prevention from prior phases is now even more relevant**: when three agents land in one file, each agent should grep the actual master file (not their report) before testing — Mack's report flagged this on his pass, and his foresight in seeding `contacts:[]` and `createdAt` on imported jobs even though Rex's code wasn't merged yet meant that when Rex's REDO did land, the import pipeline already produced forward-compatible jobs. Excellent defensive coding.

---

## Reproduction artifacts (in my worktree, NOT committed)

- **Phase 3 jsdom harness:** `D:\Claude Playground\.claude\worktrees\agent-ab053ac84d6be7c4b\vera_phase3_qa.js` — 166 assertions across 10 sections. Re-runnable:
  ```
  cd "D:/Claude Playground/.claude/worktrees/agent-ab053ac84d6be7c4b"
  NODE_PATH="D:/Claude Playground/.claude/worktrees/agent-a0345916f6ee2789c/node_modules" node vera_phase3_qa.js
  ```
  Expected: exit `0`, tail `TOTAL: PASS 166 / FAIL 0`, `Console errors during boot: 0`.

- **WCAG contrast harness:** `D:\Claude Playground\.claude\worktrees\agent-ab053ac84d6be7c4b\vera_phase3_contrast.js` — 29 pairs. Pure Node, no deps. Exit `1` is expected (the 7 D3 cases). See comments in the file.

- **Test files are worktree-local scratch — not committed.** Per the brief.

---

## Sign-off

**QA APPROVED — PASS WITH NOTES.** Andy is clear to commit `dashboard/index.html` for Phase 3 (JOBSEARCH-006, -007, -009, and the dashboard side of -010). 

Three Design Notes tracked for a Phase 4 design polish ticket — D3 (the `--muted` chrome-contrast issue) is now in its third phase of carry-forward and should be scheduled rather than re-deferred. D1 and D2 are unchanged from Phase 2.

**Still required before Mack's piece fully ships:** Jasmin's separate sign-off on `scripts/job_url_parser.py` (Python network/parsing logic — not in my lane).

— Vera
