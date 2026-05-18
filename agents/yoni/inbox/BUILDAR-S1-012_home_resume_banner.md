# Yoni — BuildAR Pro S1-012: HomeScreen resume-active-session banner

**From:** Andy
**Dispatched:** 2026-05-18
**Task:** BUILDAR-S1-012 (Phase 2 polish — deferred from S1-011)
**Branch:** continue on `feat/mobile-shell` (extend with 1–2 commits; branch already MERGE GREEN, this is additive)
**Tester:** Vera (UI/a11y) then Jasmin (logic)

---

## Why this matters

Lena's original brief called for a "Resume your last project" banner on HomeScreen when the user has an active (not completed) session. We scope-cut it from S1-011 because there's no `GET /sessions?status=active` route yet and we didn't want to widen API scope mid-sprint. Phase 2 unblocks it cleanly: **client-side cache only, no new API.**

---

## Success criteria (definition of done)

1. **Banner renders** at the top of HomeScreen ONLY when there is a non-completed session cached locally. If no active session, banner is absent (don't render an empty placeholder).
2. **Banner shows:** project name (from cache), step number ("Step 3 of 7" if step count known, else just "Resume"), and a `Resume` CTA button.
3. **Tap Resume** navigates directly to `SessionScreen` with the cached session id + project id. Same nav shape as the existing project → session flow.
4. **Cache source.** Read from whatever local store SessionScreen already writes on every step (likely AsyncStorage key like `@buildar/active_session` — confirm by reading SessionScreen first). If no such write exists yet, add it as part of this task: every `tickStep` or step-save action also persists `{ sessionId, projectId, projectName, currentStepIndex, totalSteps, updatedAt }` to a single AsyncStorage key.
5. **Cache invalidation.** On session completion (final step ticked) OR Exit → "Exit and discard," clear the cached key so the banner disappears.
6. **Stale guard.** If cached `updatedAt` is >7 days old, treat as stale and don't show the banner. (User probably abandoned that session.)
7. **WCAG AA.** Banner colors use existing tokens (`primary` `#C0461A` for any CTA fill, `primaryDark` `#B8431A` for orange text on light bg). No new hardcoded hex.
8. **Tests.** Add 3 tests minimum: (a) banner absent when no cache, (b) banner renders with project name when cache present + fresh, (c) banner absent when cache >7 days old. Existing 35/35 must still pass.

---

## What NOT to do

- Do NOT add a new API route. Pure client-side this iteration.
- Do NOT add a new dependency. Use the AsyncStorage already wired in.
- Do NOT touch the Yoni S1-008/009 orchestrator branch. Stay on `feat/mobile-shell`.
- Do NOT push to GitHub or merge to main. Andy gates pushes.
- Do NOT widen scope to fix other Vera NITs (1, 2, 3, 8, 9, 10) — those are deferred separately.

---

## Infrastructure vs design (per CLAUDE.md Rubric)

**Infrastructure:**
- Does the host have AsyncStorage's native module linked? (Bare RN — confirm.)
- Any storage-quota implication? (Negligible; just sanity-check the key isn't accidentally written every render.)

**Design:**
- Where does the persistence write live? (Should be the step-save action handler, NOT on render or on focus — that would re-write stale data.)
- What's the data shape contract? Document it inline at the top of the AsyncStorage helper file.
- Edge case: user has 3 in-flight sessions across 3 projects — current scope is "show the most recent one only." Spell this out in the helper's doc comment.

---

## Token discipline

This is small and surgical. Target ≤200 tool uses. No exploring beyond:
- `apps/mobile/src/screens/HomeScreen.tsx`
- `apps/mobile/src/screens/SessionScreen.tsx` (read to find the step-save handler + nav shape)
- `apps/mobile/src/theme/colors.ts` (read for token names)
- `apps/mobile/src/__tests__/` (read 1 existing test to mirror style)

---

## Commit strategy

1–2 commits on `feat/mobile-shell`:
```
1. feat(mobile): persist active session to AsyncStorage on step-save
2. feat(mobile): HomeScreen resume-active-session banner + tests
```
(Combine into 1 commit if your edits naturally interleave.)

NOT pushed.

---

## Reporting

Write to `D:\Claude Playground\agents\andy\inbox\yoni_s1_012_done.md`:
- Commit SHAs + git log --oneline (since branch tip)
- Files touched
- Test count (target: 38/38, was 35/35)
- AsyncStorage key name + shape
- Status: DONE or BLOCKED

Telegram when done:
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-012" "HomeScreen resume banner shipped. <test counts>. Report at agents/andy/inbox/yoni_s1_012_done.md."
```

---

## Constraints

- **Repo:** `D:\BuildAR\` on existing `feat/mobile-shell` branch.
- **You are the ONLY agent in `D:\BuildAR\` right now.** No parallel agent in this repo.
- After you: Vera runs UI/a11y QA, then Jasmin runs logic QA.

— Andy
