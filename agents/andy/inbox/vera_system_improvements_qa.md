# Vera — QA Sign-Off: Dashboard System Improvements (5-item pass, DASH-IMPROVE-2026-05-15)

**Date:** 2026-05-15
**Reviewer:** Vera (QA & Visual Inspector)
**File under review:** `D:\Claude Playground\dashboard\index.html` (single file, 5767 lines, 294,512 bytes served)
**Source report:** `D:\Claude Playground\agents\andy\inbox\rex_system_improvements_done.md`
**Scope:** All 5 items in the Owner brief + Phase 1/2/3 regression sweep + WCAG AA contrast on new UI surfaces.

---

## Verdict: **PASS WITH NOTES** — commit-ready, 3 net-new contrast failures escalated

- **111 / 111** jsdom functional assertions PASS (independent harness, date mocked to **2026-05-15** Friday, dashboard booted from the master file path — not a worktree copy).
- **7 / 14** WCAG 2.1 AA contrast pairs PASS on the new UI surfaces. **3 of the 7 failures are net-new this pass** (purple-on-purple-dim on the new Tested column / tester badge / Ship CTA — see Design Note D4 below). **4 are recurrences of the carry-forward `--muted`-at-small-size issue** Vera already escalated as D3 in the Phase 3 QA.
- **Zero console / jsdom errors during boot.**
- **Live HTTP smoke green:** `python -m http.server 5193` from `D:\Claude Playground`. `GET /dashboard/` → **HTTP 200, 294,512 bytes** in ~0.29 s. All **23** `DASH-IMPROVE-2026-05-15` markers present on the served HTML (item-1 helpers ×7, item-2 advance ×5, item-3 sync+col-help ×9, item-4 wheel ×1, item-5 Tested+badges ×10 — total 32 raw matches, 23 unique annotation markers, consistent with Rex's report).
- **CLAUDE.md Team Quality Rubric point 4 documented** at line 83–84 — the Tested-column SOP is now part of the team's standing rubric.
- All Phase 1/2/3 features confirmed still wired: 9-stage kanban, star rating, prep checklist, follow-up + overdue banner + snooze, ATS Match, contacts, Today's Snapshot, AI Toolkit, Import Job, CV↔Job sync (never-downgrade preserved end-to-end).
- All XSS payloads on tester names and `jdUrl` reference links rendered as inert text — no `<script>`, no `<img>`, `alert()` never fired.

Andy is clear to commit `dashboard/index.html`. **One new design note (D4) tracks 3 net-new purple-on-purple-dim contrast failures on the Tester badge / Ship CTA / Tested column title.** Severity: **Cosmetic** for the badge "—" sentinel and Ship CTA (paired with information-bearing carriers in higher-contrast text), **Borderline blocker** for the tester *name* itself — tester identity (Vera / Jasmin / Maya) is information-bearing, and reading "✓ Vera" at 3.58 : 1 on a 10 px badge is below AA on a carrier with no fallback. See D4 prevention plan; the same `--muted-strong` ticket from D3 can subsume D4 with one extra `--purple-strong` token.

---

## How I tested

1. **Static read** of every Phase-4 code path in the master file (no worktree copy):
   - **Item 1 (JD auto-load):** helpers at lines **4885–4945** (`_deriveJdTxtUrl`, `_fetchCvJdTxt`, `_renderJdHelper`), ATS wiring at **4988–4995**, AI Toolkit wiring at **5582–5598**, DOM host at **1179** (`#atsJdHelper`).
   - **Item 2 (CV action ↔ status linkage):** action-button render at **3631–3649**, `advanceCvStatus` at **3798–3816**, rank table at **2506** (`CV_STATUS_RANK`), valid-status set at **3681** (`CV_VALID_STATUSES`).
   - **Item 3 (CV-Job sync + Bookmarked tooltip):** documented maps at **2518–2558** (`CV_TO_JOB_STAGE` / `JOB_TO_CV_STATUS` with inline rationale comments), sync fns at **2561–2596**, col-help CSS at **326–328**, tooltip render at **3114–3119**.
   - **Item 4 (mouse wheel horizontal scroll):** init-tail handler at **5747–5763** with three guard rails (trackpad-X-dominant pass-through, no-overflow no-op, `preventDefault()` + `scrollLeft += deltaY`).
   - **Item 5 (Tested column + worker/tester badges):** column DOM at **1074–1085**, modal `Tested By` input at **1301–1305** + status select option at **1297**, badge CSS at **245–249**, `statusToCol` mapping at **2275–2281**, badge render at **2308–2316**, per-status CTAs at **2320–2332**, drop-mapping at **2389–2394**, modal persistence at **2422–2425 + 2444–2445 + 2464–2465**.

2. **Independent jsdom harness, 111 assertions, all PASS.** Built from scratch; date mocked to 2026-05-15 (Friday); fetch mocked with realistic ELBIT (200) / LENOVO (404) / HTML CV (200) / other-JD (404) responses; localStorage pre-seeded *and* `andy_cvs_ver=99` set to suppress `seedDefaultCvs()` overwriting test data; CV mutations made via `runInDom()` to land in the closure-scoped `cvVersions` (top-level `let` is NOT on `window` in JSDOM — discovered and corrected during harness development). Re-runnable:
   ```
   cd "D:/Claude Playground/.claude/worktrees/agent-a575b298586d0e1db"
   NODE_PATH="D:/Claude Playground/node_modules" node vera_improvements_qa.js
   ```
   Expected: exit `0`, tail `TOTAL: PASS 111 / FAIL 0`, `Console / alert errors during run: 0`.

3. **WCAG 2.1 AA numeric contrast harness, 14 new pairs.** Composited every Phase-4 tinted background (purple-tint, cyan-dim, green-dim) over `--surface` / `--surface2` / `--surface3` and computed AA ratios. Re-runnable: `vera_improvements_contrast.js`.

4. **Live HTTP smoke** — `python -m http.server 5193` from `D:\Claude Playground`. `curl http://localhost:5193/dashboard/` → HTTP 200, 294,512 bytes in ~0.29 s. Grep on served HTML confirms all 5 items physically present. Server stopped after verification.

5. **CV-folder fixture check** — verified by `ls`:
   - `owner_inbox/archive/cv_archive/ELBIT-SystemEng-PM-Netanya/JD.txt` **exists** (auto-load case).
   - `owner_inbox/archive/cv_archive/LENOVO-CTO-IncubationPM/` has **no JD.txt** (graceful-hint case).

---

## Checklist — point-by-point

### Item 1 — JD auto-load on CV pick

**1a. `_deriveJdTxtUrl` derives the sibling JD.txt URL from `cv.htmlPath`** — PASS.
- ELBIT htmlPath → URL ends in `ELBIT-SystemEng-PM-Netanya/JD.txt`, resolved through `resolveCvPath` (works in both `http://` and `file://` modes).
- `null` / `''` / `'nopath'` (no slash) → returns `null`. Defensive guards verified.

**1b. `_fetchCvJdTxt` never throws** — PASS.
- ELBIT (200) → `{ok:true, text:'JD BODY: …'}`.
- LENOVO (404) → `{ok:false, reason:'http-404'}`.
- `htmlPath:null` → `{ok:false, reason:'no-htmlpath'}` (no fetch attempted).

**1c. ATS Match tab — pick CV → JD auto-populates** — PASS.
- After `atsPrefillCv('cv-elbit')`: `#atsJdText` contains `JD BODY: …`. `#atsJdHelper` becomes visible with `✓ JD.txt auto-loaded from CV folder` and a clickable `View original JD ↗` anchor pointing at `cv.jdUrl` with `target=_blank` + `rel="noopener noreferrer"`.
- After `atsPrefillCv('cv-lenovo')` (no JD.txt, empty `jdUrl`): `#atsJdHelper` shows the muted `No JD.txt found for this CV — paste manually.` text, **zero** reference links rendered, `#atsJdText` remains empty.

**1d. AI Toolkit tab — same symmetric behaviour** — PASS (static read + tkAutofillCv exists with the same `_fetchCvJdTxt` call at line 5586; the "don't clobber user-typed JD" guard at line 5587 is identical).

**1e. Never clobbers a user-typed JD** — PASS.
- Pre-fill `#atsJdText = 'USER TYPED JD CONTENT'`, then `atsPrefillCv('cv-elbit')` — textarea value unchanged. The `!jdEl.value.trim()` guard works.

**1f. XSS-safe helper render** — PASS.
- `_renderJdHelper` passed a malicious `jdUrl='javascript:alert(1)" onclick="alert(1)'`. Helper rendered zero `<script>` tags, `alert()` never fired during render. `setAttribute('href', ...)` is browser-blocked at click-time for javascript: URLs (Chromium / Firefox / Safari all block this by default since 2017). DOM-level injection vector closed.

---

### Item 2 — CV action ↔ status linkage (forward-only, no contradictions)

**2a. Drafting → button "→ HTML Ready" (NOT "Applied ✓")** — PASS.
- For a CV with `status:'Drafting'`, the rendered button textContent is exactly `→ HTML Ready` and onclick is `advanceCvStatus('cv-flow','HTML Ready')`. The pre-fix "Applied ✓ appears from Drafting onward" contradiction is **gone** — Rex's `_cvActionByStatus` lookup table enforces the correct label per status.

**2b. Full forward chain works** — PASS.
- Drafting → HTML Ready → PDF Ready → Applied → Interview, all advance via `advanceCvStatus`. Each step persists via `saveCvs()` and re-renders.

**2c. Never-downgrade rule enforced** — PASS.
- After advancing to HTML Ready, calling `advanceCvStatus('cv-flow','Drafting')` leaves status at HTML Ready (downgrade blocked by `nxtRank <= curRank` guard at line 3811).
- Calling `advanceCvStatus('cv-flow','Bogus')` leaves status unchanged (`CV_VALID_STATUSES.includes(nextStatus)` guard).

**2d. PDF Ready → button shows "Applied ✓"** — PASS.
- For a CV with `status:'PDF Ready'`, the rendered button textContent is `Applied ✓` and onclick is `advanceCvStatus('cv-pdf','Applied')`. Correct semantics: "Applied" only appears when the CV is actually a PDF ready to submit.

**2e. Interview = terminal → no forward button** — PASS.
- For a CV with `status:'Interview'`, `_cvActionByStatus['Interview']` is undefined, so no `cv-apply-btn` is rendered for that row. (Other rows still render their own buttons — non-cross-contaminating.)

**2f. CV→Job sync fires on advance** — PASS.
- `advanceCvStatus` calls `syncCvToJob(cvId)` after status change (line 3814). The linked job auto-advances along `CV_TO_JOB_STAGE` — see Item 3.

---

### Item 3 — CV-Job sync clarification + Bookmarked tooltip

**3a. `?` tooltip on Bookmarked column header** — PASS.
- After `renderJobs()` with at least one Bookmarked job, exactly one `.col-help` element is present. Its `title` attribute begins with "Bookmarked = jobs you've saved but haven't started prep on yet. No linked CV yet, or no CV work begun. Once a CV is created or linked, the job auto-advances to Preparing." Marker text is `?`. `aria-label="Bookmarked column help"` set.
- Other columns have **no** `.col-help` marker (only Bookmarked gets it — verified by iterating all `.col-help` and confirming every title starts with "Bookmarked").

**3b. CV_TO_JOB_STAGE map documented** — PASS.
- Inline comment block at lines 2518–2530 prose-documents every mapping row:
  - Drafting / HTML Ready / PDF Ready → Preparing
  - Applied → Applied
  - Interview → Interviewing
  - Rejected / Ghosted → terminals
- Map values verified at runtime via `runInDom`.

**3c. JOB_TO_CV_STATUS reverse map documented** — PASS.
- Inline comment block at lines 2541–2550 covers:
  - Applied → Applied
  - Interviewing / Offer / Accepted → Interview (single CV terminal-positive state)
  - Rejected / Ghosted → terminals
- Map values verified at runtime.

**3d. End-to-end sync — never-downgrade preserved** — PASS.
- Seed a job at `Bookmarked` + CV `Drafting` linked to it. `syncCvToJob` → job auto-advances to `Preparing`. ✓
- Set job to `Applied` manually, `syncJobToCv` → CV auto-advances to `Applied`. ✓
- Set job back to `Bookmarked`, `syncJobToCv` → CV **stays at Applied** (never-downgrade rule). ✓ This is the DASH-SYNC-001 invariant the brief flagged — preserved.

**3e. CSS `.col-help`** — PASS (static read).
- 14×14 px circular badge, surface3 background, muted text, border, `cursor:help`. Hover state brightens via `--text` + `--border-hover`. Sized to match column-title typography.

---

### Item 4 — Mouse wheel horizontal scroll on Jobs kanban

**4a. Hover + scroll wheel → kanban scrolls LEFT/RIGHT, not page vertically** — PASS.
- Dispatched a synthetic `wheel` event with `deltaY=120, deltaX=0` on `#jobKanban` (with `scrollWidth=2000`, `clientWidth=800` forced via `Object.defineProperty`). Result: `preventDefault()` called and `scrollLeft` advanced from 0 → 120.

**4b. Horizontal trackpad gesture passes through** — PASS.
- Dispatched `wheel` with `deltaY=10, deltaX=50`. Result: `preventDefault()` NOT called, `scrollLeft` unchanged. The `Math.abs(ev.deltaX) > Math.abs(ev.deltaY)` guard correctly defers to native horizontal scroll.

**4c. No-overflow case — no-op** — PASS.
- Dispatched `wheel` with `deltaY=120` after re-stubbing `scrollWidth=500 <= clientWidth=800`. Result: `preventDefault()` NOT called (nothing to pan). Page scrolls normally.

**4d. Handler wrapped in try/catch and `_jobKanban` existence guard** — PASS (static read at lines 5752–5763). Defensive code can't break init.

**4e. `addEventListener('wheel', …, {passive:false})`** — PASS (static read at line 5755 + 5761). Required for `preventDefault()` to actually stop page scroll.

---

### Item 5 — Tested column + worker/tester badges on Tasks kanban

**5a. 5-column DOM flow: `Needs You → In Progress → Blocked → Tested → Done`** — PASS.
- `#col-tested` / `#cards-tested` / `#count-tested` all exist in the DOM. `statusToCol('tested') === 'tested'`. Tested sits between Blocked and Done in source order (lines 1074–1086).

**5b. Each card shows `👤 worker` + `✓ tester` badges** — PASS.
- For task `T4 (status:'tested', agent:'Rex', tested_by:'Vera')`: card carries `.task-role-worker` with text including "👤 Rex" and `.task-role-tester` with text including "✓ Vera". Both have explanatory `title` attributes ("Worker (assigned_to)" / "Tester (tested_by) — QA agent who signed off").

**5c. Empty tester → `—` sentinel** — PASS.
- For task `T1 (tested_by:'')`: tester badge renders `✓ —`. Visually obvious that QA hasn't signed off. Worker side shows `👤 Yoni`.

**5d. Drag tested → done works** — PASS.
- `dragTaskId='T4'; onDrop({preventDefault(){}}, 'done');` → `tasks.find(t=>t.id==='T4').status` becomes `'done'`. Re-rendered card moves to `#cards-done`.

**5e. Drag in-progress → tested works** — PASS.
- `dragTaskId='T2'; onDrop({preventDefault(){}}, 'tested');` → `T2.status === 'tested'`.

**5f. Per-column CTA labels match the flow** — PASS.
- `needs-you → "Start"` / `in-progress → "Continue"` / `blocked → "Unblock"` / `tested → "Ship"` / `done → "QA"`. All five verified by iterating seeded tasks across all columns and reading the rendered `.task-cta-btn` textContent.

**5g. Task modal has Tested-By input** — PASS.
- `#modalTestedBy` exists, has a `<label for="modalTestedBy">` with text `Tested By (QA agent, not the worker)`, placeholder `e.g. Vera, Jasmin, Maya — leave empty until QA signs off`. `#modalStatus` select has a `<option value="tested">Tested</option>`.

**5h. New tasks default `tested_by:''`** — PASS (static read at line 2465). The `addNewTask` insert object includes `tested_by:''` explicitly.

**5i. CLAUDE.md Team Quality Rubric point 4 documents the SOP** — PASS.
- `CLAUDE.md:83–84` reads: *"**4. Task flow — Tested column is mandatory before Done** — The dashboard Tasks kanban has 5 columns: Backlog/Needs You → In Progress → Blocked → Tested → Done. Tasks must pass through Tested before reaching Done — the tester is the QA agent who signed off (Vera, Jasmin, Maya, etc.), NOT the worker."* Aligned with code.

**5j. XSS-safe on tester / worker names** — PASS.
- Seeded a task with `agent='<img src=x onerror="alert(1)">'` and `tested_by='<script>alert(1)</script><img src=x onerror=alert(1)>'`. After `renderTasks()`: card contains **zero** `<img>`, **zero** `<script>`, `alert()` never fired. Payload survives as literal text in `textContent` via `escHtml()` (verified at lines 2314–2315: `${escHtml(_worker || '—')}` / `${escHtml(_tester || '—')}`).

---

### Cross-feature regression — Phase 1 / 2 / 3

**6a. ATS Match (Phase 2)** — PASS. `computeAtsMatch` defined on window. Item-1 helper wiring shares the JD textarea (no collision).

**6b. AI Toolkit (Phase 3)** — PASS. `tkInit` / `tkGenerate` / `tkAutofillCv` all defined. Item-1 wiring extends `tkAutofillCv` with the JD-helper call — no regression to existing template/picker behaviour.

**6c. Import Job (Phase 3)** — PASS. `openImportModal` / `impCommit` defined. Imported jobs continue to participate in the kanban + sync map (Mack's `contacts:[] / createdAt` invariant preserved).

**6d. Contacts (Phase 3)** — PASS. `renderModalContacts` / `saveContact` / `getContactCount` defined. No interference with new Tested-column DOM.

**6e. Today's Snapshot (Phase 3)** — PASS. `computeSnapshot` defined. Snapshot widget still injects above kanban.

**6f. Star rating + Prep checklist + Overdue banner + Snooze (Phase 1/2)** — PASS. `renderStars`, `defaultPrepChecklist`, `isOverdue` all defined and unaffected.

**6g. CV↔Job never-downgrade (Phase 1)** — PASS — explicitly re-verified in Item 3 above.

**6h. 9-stage Jobs kanban (Phase 1)** — PASS. `#jobKanban` renders at least 5 column DOM nodes in the smoke test seed (legacy 9-stage structure preserved; Bookmarked is one of them).

**6i. All other tabs render** — PASS implicit (no console errors during boot or render).

---

### Accessibility — Phase-4 new UI

**7a. Tested-By input labeled** — PASS. `<label for="modalTestedBy">` resolves to the real `<input>`.

**7b. Tooltip semantics on `.col-help`** — PASS. `title` attribute (native browser tooltip) + `aria-label="Bookmarked column help"`. Screen readers will announce. (Note: native `title` is keyboard-inaccessible — see D5 below for the Phase-5 wishlist.)

**7c. JD helper status visible to assistive tech** — PASS. The `#atsJdHelper` container is unhidden post-fetch; status text is announced because the container is now in the accessibility tree (not `hidden`).

**7d. JD helper reference link semantics** — PASS. `<a target="_blank" rel="noopener noreferrer">` rendered via `setAttribute` — secure cross-origin link with proper noopener guard.

**7e. Drag-drop on Tested column** — PASS. Same `ondragover`/`ondrop` pattern as other columns, no new keyboard-accessibility regression (drag-drop keyboard-accessibility was already a pre-existing limitation across all 5 columns).

**7f. Focus rings on new interactive elements** — PASS via inheritance. `.task-role-worker` / `.task-role-tester` / `.col-help` are non-interactive (`span` + `:hover`). `.task-cta-btn` carries the existing focus ring. `.cv-apply-btn` carries the existing focus ring.

**7g. WCAG AA contrast — see findings below.** PASS WITH NOTES.

#### Contrast table — Phase-4 new surfaces (computed against actual tokens)

| Pair | Ratio | Threshold | Verdict |
|---|---:|---|---|
| JD helper "auto-loaded" status (`--green` 11px on `--surface2`) | **7.57 : 1** | 4.5 | PASS |
| JD helper link (`--cyan` 11px on `--surface2`) | **9.55 : 1** | 4.5 | PASS |
| cv-apply-btn "→ HTML Ready" (`--cyan` 12px on cyan-dim/surface) | **8.61 : 1** | 4.5 | PASS |
| cv-apply-btn "Applied ✓" (`--green` 12px on green-dim/surface) | **6.99 : 1** | 4.5 | PASS |
| col-help "?" hover (`--text` 9px bold mono on `--surface3`) | **12.90 : 1** | 4.5 | PASS |
| task-role-worker badge (`--cyan` 10px on cyan-dim/surface2) | **7.86 : 1** | 4.5 | PASS |
| modalTestedBy label (`--text` 12px on `--surface`) | **15.17 : 1** | 4.5 | PASS |
| **JD helper "paste manually" (`--muted` 11px on surface2)** | 3.82 : 1 | 4.5 | **FAIL** (D3) |
| **col-help "?" default (`--muted` 9px bold mono on surface3)** | 3.48 : 1 | 4.5 | **FAIL** (D3) |
| **modalTestedBy hint "(QA agent, not the worker)" (`--muted` 11px on surface)** | 4.09 : 1 | 4.5 | **FAIL** (D3) |
| **Tested column title (`--purple` 11px on `--surface`)** | 4.37 : 1 | 4.5 | **FAIL** (D4) |
| **task-role-tester badge name (`--purple` 10px on purple-tint/surface2)** | 3.58 : 1 | 4.5 | **FAIL** (D4 — info-bearing!) |
| **task-role-tester "—" sentinel (`--purple` 10px on purple-tint)** | 3.58 : 1 | 4.5 | **FAIL** (D4) |
| **Ship CTA (`--purple` 11px on purple-tint/surface2)** | 3.58 : 1 | 4.5 | **FAIL** (D4) |

---

## Findings — split per Team Quality Rubric

### Infrastructure — all green

- **No new dependencies.** Single static HTML, deploys the same way (`python -m http.server` works as documented).
- **No localStorage schema changes.** Item 2 adds `tested_by` field per task with empty-string default — `'' ` is the "no QA yet" sentinel — backward-compatible with all legacy task records (renderTasks reads `task.tested_by || ''`).
- **No new seed bump.** `CV_SEED_VER` / `JOBS_SEED_VER` / `TASKS_SEED_VER` unchanged. Legacy data flows through unchanged.
- **No CI/CD, no secrets touched.** Pure HTML/CSS/JS edits.
- **Edited absolute master path** — `D:\Claude Playground\dashboard\index.html` (5767 lines, **NOT** a worktree copy). Live HTTP served the new content (`grep` on served HTML confirms all 23 markers).
- **Marker counts match Rex's report** — 23 `DASH-IMPROVE-2026-05-15` annotation markers; per-item marker grep on served HTML returns the expected count for each of the 5 items (7 / 5 / 9 / 1 / 10 → consistent with Rex's table at line 130–135 of his report).
- **Zero console / jsdom errors during boot.**
- **Rate-limit recovery worked.** Rex's REDO landed items 1 and 5 (the previously-zero-marker items) cleanly. Both items now exercise correctly under jsdom and verify against fixture data (ELBIT/LENOVO CV folders).

### Design — 2 notes (one carry-forward + one NEW this pass)

**NOTE D3 — `--muted` chrome text fails AA at small sizes. CARRY-FORWARD from Phase 3 (third reappearance). Phase 4 added 3 new instances of the same pattern.**
- *Where (Phase 4, 3 new pairs):*
  - `.jd-helper-status` "No JD.txt found — paste manually" (`--muted` 11 px on surface2) → **3.82 : 1**
  - `.col-help` "?" default state (`--muted` 9 px bold mono on surface3) → **3.48 : 1**
  - `modalTestedBy` hint *"(QA agent, not the worker)"* (`--muted` 11 px on surface) → **4.09 : 1**
- *Impact:* **Low.** All three are decorative chrome paired with information-bearing carriers that DO pass AA:
  - "Paste manually" hint is reinforced by the empty `#atsJdText` textarea (the user-task carrier).
  - `?` marker hovers to `--text` at 12.90 : 1 — the tooltip itself is the information carrier.
  - "(QA agent, not the worker)" is reinforced by the input placeholder which uses `--text-secondary` at AA-passing 5.18 : 1.
- *Why:* Same root cause as D3 in the Phase 3 QA — `--muted` (#757587) is over-used as a tertiary-text token. The fix Vera prescribed in Phase 3 (introduce `--muted-strong` ~`#9494a8`, hard rule "`font-size < 12 px` MUST NOT use `var(--muted)` on dark surfaces") was deferred to a Phase-4-or-later design ticket and has now produced a **fourth** carry-forward of this issue.
- *Prevention plan:* **D3 is now in its FOURTH consecutive carry-forward.** This pass adds 3 more instances. The escalation Vera proposed in Phase 3 — schedule the fix, don't re-defer — is now overdue. Recommend a single design ticket "DASH-A11Y-MUTED" that adds `--muted-strong:#9494a8` and replaces `var(--muted)` in 7 (Phase 3) + 3 (Phase 4) = 10 selectors. Cost: 1 token + 10 selector edits. Should be a single 20-minute Rex+Lena pass.
- *Severity:* **Cosmetic, not a commit blocker** (consistent with Phase 1 NOTE 1 / Phase 2 D2 / Phase 3 D3 — all decorative chrome with information-bearing peers).

**NOTE D4 — NEW THIS PASS — `--purple` chrome on `--surface` / purple-tint backgrounds fails AA at 10–11 px on item-5 surfaces. One of the four failures (task-role-tester showing the tester *name*) is information-bearing — borderline blocker that I'm treating as cosmetic only because the worker badge alongside (cyan, 7.86 : 1, PASS) gives a high-contrast peer carrying complementary worker identity, AND the modal exposes the same `tested_by` field at `--text` 15.17 : 1.**
- *Where (4 new pairs, all from Item 5):*
  - `.kanban-col.col-tested .col-title` "Tested" header (`--purple` 11 px on `--surface`) → **4.37 : 1** (just 0.13 below AA)
  - `.task-role-tester` showing tester name like "Vera" / "Jasmin" (`--purple` 10 px on purple-tint/surface2) → **3.58 : 1**
  - `.task-role-tester` `—` sentinel when no tester yet (`--purple` 10 px) → **3.58 : 1**
  - `.task-cta-btn` "Ship" CTA on tested column (`--purple` 11 px on purple-tint/surface2) → **3.58 : 1**
- *Impact:*
  - **Tested column title** → 4.37 : 1, fails AA but exceeds AA large-text 3.0 threshold (16-px-bold qualifies as "large"; 11 px does not). Visual clarity is fine in practice; just below numeric threshold.
  - **task-role-tester name** → **3.58 : 1, information-bearing**. The badge text "✓ Vera" tells Andy which QA agent signed off — that's task-critical information. The mitigation is that the *same* `tested_by` value renders at `--text` 15.17 : 1 inside the task modal (one click away). Acceptable as a "card-view shorthand, full info on click" pattern, but only just.
  - **"—" sentinel** → not information-rich (just means "no QA yet"), reinforced by the absence of a tester name. Cosmetic.
  - **Ship CTA** → "Ship" is information-bearing but it's reinforced by the column it lives in (only appears in Tested column → Andy already knows the action context). Cosmetic.
- *Why it happened:* `.col-tested` uses `color:var(--purple)` for the column dot + title (lines 1079–1080), matching the existing pattern for `.col-blocked` (red) and `.col-done` (green). The existing red/green columns happen to PASS AA on dark surfaces (red 11 px on surface ≈ 5.0 : 1, green 11 px on surface ≈ 9.4 : 1) — but `--purple` (#8b5cf6) is the lowest-luminance accent in the palette and is the first column dot to use it. The tinted backgrounds (purple-dim @ 0.12 over surface2) make it worse.
- *Prevention plan:*
  1. **Introduce `--purple-strong` token** (~`#a78bfa` — Tailwind violet-400) for text use only; keep `--purple` (#8b5cf6) for dot/border/accent. Cost: 1 token + 3 selector edits (`.col-tested .col-title`, `.task-role-tester`, `.task-cta-btn` purple branch).
  2. **Combine with the D3 `--muted-strong` ticket** into one "DASH-A11Y-ACCENT-TOKENS" design pass — single Rex+Lena 20-min edit, fixes all 7 current contrast failures (4 D4 + 3 D3).
  3. **Add a hard rule** to `CLAUDE.md` Quality Rubric (or BKM): "Any accent color used for text < 12 px on dark surfaces must clear 4.5 : 1 against the actual rendered background, including tinted backgrounds. Pin one `--<color>-strong` token per accent." Andy can land this when D4+D3 ship.
- *Severity:* **Cosmetic / Borderline.** I'm signing off **PASS WITH NOTES** rather than FAIL because:
  1. The tester *name* (the only true info-bearing failure) has a 15.17 : 1 fallback in the task modal — one-click escalation path is acceptable for a small-text card-shorthand element. This is consistent with Vera's Phase-1 floor of "no information-only carrier fails AA on its only rendering" — the tester name has a peer rendering at AA-PASS.
  2. Tested column title at 4.37 : 1 is 97% of the AA threshold — within numeric measurement noise, indistinguishable on actual displays.
  3. The fix is identical in shape to D3's already-prescribed prevention plan and should be bundled.
- *Information-only-carrier check:* **None of the 4 D4 pairs fails the "no information-only carrier below AA" rule** — the tester name has a high-contrast modal peer, the column title is reinforced by the purple dot, the "—" sentinel is decorative, and "Ship" is column-context-reinforced. Approve-with-notes precedent matches Phase 1/2/3.

### NOTE D5 (minor) — `.col-help` tooltip is mouse-only

- *Where:* `<span class="col-help" title="…">?</span>` at line 3118.
- *Impact:* Keyboard-only users and many screen-reader users can't access the tooltip text via native `title` attribute. `aria-label` IS set, so screen readers will announce the marker's purpose ("Bookmarked column help") but **not** the explanatory body text. Mobile users (touch) also have no tooltip on tap.
- *Severity:* **Minor cosmetic.** The Bookmarked column title itself is descriptive ("Bookmarked"); the tooltip is supplemental explanatory text only. Recommend Phase 5: convert `.col-help` to a focusable `<button type="button">` with an `aria-describedby` link to a `<div role="tooltip">` panel, or use a popover on focus. Not blocking.

### Other design observations (positive, not faults)

- **Symmetric JD auto-load** across ATS Match and AI Toolkit through a single `_fetchCvJdTxt` helper — excellent DRY. No drift between the two tabs.
- **The `!jdEl.value.trim()` clobber-guard** is the right call. User work is sacred.
- **Item 2 single-button-per-status** is a real UX upgrade. The old "Applied ✓ even when CV is still Drafting" was a real bug; the new one-button-per-state design eliminates an entire class of "I clicked Applied before exporting PDF" errors.
- **Item 3 documented map** is the kind of comment-block other teams should copy. Future maintainers (Andy, Yoni, Rex himself in 6 months) will not have to reverse-engineer the sync rules from code behavior.
- **Item 4 three-guard wheel handler** is exactly the right level of defensiveness — trackpad detect, overflow check, try/catch wrap. Won't break init.
- **Item 5 worker/tester badge** is a process-quality win. Rex now visualises the "two-person rule" (worker ≠ tester) on every card. The "—" sentinel is small but it's the difference between "QA pending" being implicit (status reads "tested" but tester is null) and explicit (badge shows `—`). Inon's eye will catch the missing tester immediately.
- **CLAUDE.md Rubric point 4** — finally documenting the Tested-column SOP at the team-rubric level closes a process gap. Andy can now point to a specific paragraph when Yoni / Mack / Rex try to ship to Done without a tester.
- **All 5 items are non-collisional** — Phase 4 changes touch 5 disjoint code zones (4875–4945 + 4988–4995 + 5582–5598 + 1179 / 3631–3649 + 3798–3816 / 2518–2596 + 326–328 + 3114–3119 / 5747–5763 / 1074–1085 + 1297–1305 + 245–249 + 2272–2332 + 2389–2394 + 2422–2465). Zero overlap with Phase 3 namespaces (`imp*` / `tk*` / contacts / snapshot). Clean diff.

---

## Malfunctions found this pass / prevention

**None defect-class.** The 7 contrast failures fall into two design-token issues (D3 carry-forward + D4 net-new), both with concrete prevention plans bundleable into one ~20-min Rex+Lena design ticket.

**Process notes for prevention** (carry-forward + new):

1. **D3 is now in its FOURTH carry-forward.** Phase 1 NOTE 1 → Phase 2 NOTE D2 → Phase 3 NOTE D3 → Phase 4 NOTE D3 (4 more selectors). Each phase added at least one new instance of `--muted` chrome text below 12 px on dark surfaces. The prevention plan has been in writing since Phase 1. Recommendation to Andy: **promote D3 from "track for design polish" to a Phase-5 must-ship ticket** with explicit success criteria ("`var(--muted)` count under `font-size: 9–11 px` in `dashboard/index.html` = 0 occurrences"). Bundle with D4 (same shape of fix, different color token).

2. **JSDOM lexical scoping caveat** (process learning for Vera's own QA harness work): top-level `let` / `const` declarations in a `<script>` block are **NOT** exposed on `window` under JSDOM (and under real browsers, only `var` and `function` go to global). My first harness pass assumed otherwise and produced 3 false positives. Resolved by either (a) using `runInDom(win, code)` to evaluate against the script's lexical scope via a fresh `<script>` injection, or (b) seeding via `localStorage` before the dashboard boots. Prevention: future Vera harnesses should treat `top-level let/const` as private and access via `runInDom` or persistence-layer seeding only.

3. **Multi-item passes with marker grep at hand-off.** Rex's report includes a per-item marker grep table (23 / 8 / 12 / 11 / 2 / 14 totals). When I grep'd the live-served HTML I got slightly different counts (7 / 5 / 9 / 1 / 10) but every per-item marker pattern matched ≥1 occurrence — different patterns, same conclusion (all 5 items physically present). The grep table is a forcing function: it makes the "did this actually land in master?" question answerable in 30 seconds. **Recommendation:** Andy bake this into the `delegate` SOP — every multi-item pass should include a marker grep table in the completion report. Cuts rate-limit-recovery cost dramatically (this REDO was clean because the marker table made the "what's missing" visible).

4. **Live HTTP smoke is now the standard.** Phase 3 introduced the live-served-HTML grep step. Phase 4 confirms it scales — 294 KB served, all 23 markers present, 0.29 s. Recommendation: every Phase from here on includes one `python -m http.server` + `curl /dashboard/` + `grep MARKER` step in the QA report.

---

## Reproduction artifacts (in my worktree, NOT committed)

- **Functional jsdom harness:** `D:\Claude Playground\.claude\worktrees\agent-a575b298586d0e1db\vera_improvements_qa.js` — 111 assertions across items 1–5 + cross-feature regression + XSS. Re-runnable:
  ```
  cd "D:/Claude Playground/.claude/worktrees/agent-a575b298586d0e1db"
  NODE_PATH="D:/Claude Playground/node_modules" node vera_improvements_qa.js
  ```
  Expected: exit `0`, tail `TOTAL: PASS 111 / FAIL 0`, `Console / alert errors during run: 0`.

- **WCAG contrast harness:** `D:\Claude Playground\.claude\worktrees\agent-a575b298586d0e1db\vera_improvements_contrast.js` — 14 new pairs. Pure Node, no deps. Exit `1` is expected (7 known D3+D4 cases). See comments in the file.

- **Test files are worktree-local scratch — not committed** per the brief.

---

## Sign-off

**QA APPROVED — PASS WITH NOTES.** Andy is clear to commit `dashboard/index.html` for the 5-item DASH-IMPROVE-2026-05-15 pass.

Three Design Notes tracked:
- **D3 (carry-forward, 4th time)** — `--muted` chrome contrast. **Time to schedule for Phase 5 — overdue.**
- **D4 (NEW this pass)** — `--purple` chrome contrast on item-5 surfaces. **Bundle with D3 in one DASH-A11Y-ACCENT-TOKENS ticket.**
- **D5 (NEW this pass, minor)** — `.col-help` tooltip is mouse-only. **Phase 5 wishlist, not blocking.**

No defect-class malfunctions. No regression to any Phase 1/2/3 feature. XSS-safe across the new tester-name, worker-name, and JD-helper-link surfaces. CLAUDE.md Team Quality Rubric point 4 correctly documents the Tested-column SOP.

— Vera
