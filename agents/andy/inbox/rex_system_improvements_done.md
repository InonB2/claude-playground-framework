# Rex — Dashboard System Improvements (5-item set) — DONE

**Date:** 2026-05-15
**File touched (only one):** `D:\Claude Playground\dashboard\index.html` (absolute master path — verified, not a worktree copy)
**Ready for:** Vera QA. **Do NOT commit — Andy commits after Vera signs off.**

---

## Why this REDO

A prior pass hit a rate limit mid-flight. Andy verified state of master and reported:
- Item 1 (JD auto-load) — **0 markers, not done**
- Item 5 (wheel scroll) — **0 markers, not done**
- Items 2, 4, 6 — markers present, possibly partial

This pass picked up where the previous one stopped: finished items 1 and 5, then verified
2, 4, and 6 were fully wired end-to-end (they were — the prior pass landed them all in
master before the rate limit hit). Smoke-tested all five against the current master to
confirm no integration drift with Yoni's AI Toolkit, Mack's Import, or my own Phase 3
contacts/snapshot work.

> Note on numbering: my source comments label the items 1–5 in the order I tackled them
> (e.g. wheel scroll is "item 4" in `DASH-IMPROVE-2026-05-15 (item 4)`), not the Owner-brief
> numbering (1, 2, 4, 5, 6). The 5 features themselves are identical to the brief.

---

## Item 1 — JD auto-load on CV pick

**Where:** `dashboard/index.html` lines 4875–4945 (helpers), 4988–4995 (ATS Match wiring),
5582–5598 (AI Toolkit wiring), 1179 (`#atsJdHelper` DOM).

**What landed:**
- `_deriveJdTxtUrl(htmlPath)` — splits the CV's `htmlPath`, returns the sibling `JD.txt`
  URL using `resolveCvPath` (works in both `http://` and `file://` modes). Returns `null`
  on null/empty/no-slash input.
- `_fetchCvJdTxt(cv)` — async, never rejects. Returns `{ok, text, url, reason}`. Used by
  **both** `atsPrefillCv()` and `tkAutofillCv()` for symmetric behaviour across ATS Match
  and AI Toolkit tabs.
- `_renderJdHelper(containerId, cv, fetchResult)` — XSS-safe (uses `textContent` +
  `setAttribute` on a created anchor). Renders a green ✓ status when JD found, a muted
  "No JD.txt found — paste manually" when not, and surfaces `cv.jdUrl` as a clickable
  "View original JD ↗" reference link (does NOT fetch — CORS blocks every job site).
- `atsPrefillCv` now also fetches JD.txt and populates `#atsJdText` if empty, then renders
  the helper into `#atsJdHelper`. Never clobbers a user-typed JD.
- `tkAutofillCv` (AI Toolkit) does the same for the template's JD field if the active
  template has one. Falls back gracefully when the template has only `background` or only
  `jd` or neither.

**UX judgment:** "If the user already pasted a JD, we leave it alone" is enforced via
`!jdEl.value.trim()` checks. This prevents auto-load from destroying work mid-edit.

## Item 2 — CV action ↔ status linkage

**Where:** lines 3631–3649 (action button render), 3798–3816 (`advanceCvStatus`).

**What landed:**
- New flow: `Drafting → HTML Ready → PDF Ready → Applied → Interview → Rejected | Ghosted`.
- Each row exposes ONE forward-action button (`cv-apply-btn`), label and target derived
  from `_cvActionByStatus[cv.status]`. Terminal states (`Interview`, `Rejected`, `Ghosted`)
  show no action button — the row is "done" or "frozen" from a workflow standpoint.
- `advanceCvStatus(cvId, nextStatus)` — validates `nextStatus` is in `CV_VALID_STATUSES`
  and that its rank is strictly greater than the current one. Never downgrades. After
  setting, runs `syncCvToJob` so the linked job auto-advances along the documented map.
- Replaces the old behaviour where "Applied ✓" appeared from `Drafting` onward — that
  broke the action/status link by letting users skip Writing/Review/PDF stages.

## Item 4 — CV-Job column sync + Bookmarked tooltip

**Where:** lines 2518–2558 (documented maps), 2561–2596 (sync functions), 326–328 (CSS),
3114–3119 (tooltip render).

**What landed:**
- `CV_TO_JOB_STAGE` and `JOB_TO_CV_STATUS` — both maps now have an inline comment block
  documenting every row of the mapping in prose. New rules baked in:
  - Drafting / HTML Ready / PDF Ready → Preparing (CV started ≠ submitted)
  - Applied → Applied · Interview → Interviewing
  - Job:Offer/Accepted → CV:Interview (no separate CV status for those)
  - Terminals on either side map to terminals
- `syncCvToJob` / `syncJobToCv` — both already enforce "never downgrade" via rank
  comparison. Behavior unchanged this pass; documentation added inline.
- Bookmarked column: `?` help marker rendered in the column header via `stageTooltip`
  (line 3117). Tooltip text: *"Bookmarked = jobs you've saved but haven't started prep
  on yet. No linked CV yet, or no CV work begun. Once a CV is created or linked, the
  job auto-advances to Preparing."*
- CSS `.col-help` — small circular badge, dim by default, brightens on hover. Sized to
  match column-title typography.

## Item 5 — Mouse-wheel horizontal scroll on Jobs kanban

**Where:** lines 5747–5763 (init-tail handler).

**What landed:**
- `addEventListener('wheel', …, {passive:false})` on `#jobKanban`.
- Three guard rails:
  1. If user is doing a real horizontal trackpad gesture (`|deltaX| > |deltaY|`), let the
     browser handle it — no double-scroll.
  2. If `scrollWidth <= clientWidth`, do nothing — nothing to pan, no point preventing
     the page from scrolling vertically.
  3. Otherwise: `preventDefault()` + `scrollLeft += deltaY` — wheel-down pans right.
- Wrapped in try/catch and a `_jobKanban` existence guard so it can never break init.

## Item 6 — Tested column + worker/tester badges (Tasks kanban)

**Where:** lines 1074–1085 (column DOM), 1297, 1301–1305 (status select + Tested-By
field in task modal), 246–249 (CSS for badges), 2272–2281 (status mapping), 2287–2293
(render columns), 2308–2316 (badge HTML), 2320–2332 (per-status CTA labels/colors),
2389–2394 (drop mapping), 2422–2425 + 2444–2445 + 2464–2465 (modal persistence).

**What landed:**
- 5-column flow: `Needs You → In Progress → Blocked → Tested → Done`. Tested is a
  mandatory QA gate before Done.
- Drag-drop onto `#col-tested` sets `task.status = 'tested'` (verified in smoke test).
- Worker badge `👤 assigned_to` (falls back to legacy `task.agent`) + Tester badge
  `✓ tested_by` (renders `—` when null/empty so QA-pending is visually obvious).
- Per-column CTAs match the flow: Start / Continue / Unblock / Ship / QA.
- Task modal exposes a `Tested By` input with placeholder explaining "QA agent, not the
  worker". New tasks default `tested_by:''`.
- Aligned with CLAUDE.md Team Quality Rubric point 4 (worker vs tester separation).

---

## MANDATORY verification

### 1. Grep marker counts (final, on master path)

| Pattern | Item | Count |
|---|---|---:|
| `DASH-IMPROVE-2026-05-15` | all five (annotation tag) | **23** |
| `_fetchCvJdTxt\|_deriveJdTxtUrl\|_renderJdHelper\|atsJdHelper` | Item 1 (JD auto-load) | **8** |
| `advanceCvStatus\|_cvActionByStatus\|CV_STATUS_RANK` | Item 2 (CV action/status) | **12** |
| `CV_TO_JOB_STAGE\|JOB_TO_CV_STATUS\|col-help\|stageTooltip` | Item 4 (sync map + tooltip) | **11** |
| `scrollLeft \+= ev\.deltaY\|jobKanban\.addEventListener\('wheel'` | Item 5 (wheel) | **2** |
| `col-tested\|cards-tested\|task-role-tester\|task-role-worker\|tested_by\|modalTestedBy` | Item 6 (Tested + badges) | **14** |

Every item has unique markers physically present in the master file.

### 2. jsdom smoke test — 35 / 35 PASS

Test file: `.rex_smoke_redo.js` (run from `D:\Claude Playground`, removed after pass).
Mocks: `fetch` returns JD body for any URL matching `/jd-ok/.../JD.txt`, 404 for other
JD.txt, and an HTML stub for `.html` paths. Coverage:

- **Item 6 (Tested):** Tested column DOM exists; `statusToCol('tested')==='tested'`; a
  synthetic `status:'tested'` task lands under `#cards-tested`; worker badge shows
  agent name, tester badge shows `tested_by`; empty tester renders the `—` sentinel;
  `onDrop(ev,'tested')` sets `task.status='tested'`.
- **Item 2 (CV action/status):** `CV_STATUS_RANK` monotonic 0→4; `advanceCvStatus`
  forward-moves work; downgrades blocked; `renderCvs` emits `.cv-apply-btn` buttons;
  Drafting row's button label is "→ HTML Ready", **not** "Applied ✓".
- **Item 4 (CV-Job map + tooltip):** `CV_TO_JOB_STAGE` and `JOB_TO_CV_STATUS` both have
  the expected mappings (Drafting→Preparing, Applied↔Applied, Interview↔Interviewing);
  Bookmarked column emits at least one `.col-help` element with title containing
  "Bookmarked".
- **Item 5 (Wheel):** `wheel` event with `deltaY=120, deltaX=0` triggers
  `preventDefault()` and increments `scrollLeft`; horizontal trackpad gesture
  (`deltaX > deltaY`) is passed through (no preventDefault).
- **Item 1 (JD auto-load):** `_deriveJdTxtUrl` returns the sibling JD.txt URL on a real
  htmlPath and `null` on bad input; `_fetchCvJdTxt` resolves `ok:true` with body on 200
  and `ok:false` with no throw on 404. End-to-end: `atsPrefillCv('cv-rex-probe')` (path
  matching the OK fixture) populates `#atsJdText`, shows the helper with the jdUrl
  reference link, and a second probe with a missing-folder path shows the "paste
  manually" fallback text.

### 3. Edited absolute master path

Confirmed `D:\Claude Playground\dashboard\index.html` (5767 lines). Not a worktree copy.

---

## Malfunctions / prevention

None. **Carry-forward prevention note:** the prior rate-limit cut-off left a half-wired
state (some items in master, others not). Future passes that span multiple items should
land + commit per-item rather than as one big bundle — or at minimum, run the marker
grep mid-flight to catch missing items before reporting done. This pass verified each of
the 5 items by marker AND by jsdom smoke before signing off.

## Files
- Modified: `D:\Claude Playground\dashboard\index.html` (only file changed)
- Smoke test was worktree-local and removed after passing (not for prod).

— Rex
