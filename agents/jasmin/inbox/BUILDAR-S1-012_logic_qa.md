# Jasmin — BuildAR Pro S1-012 logic/coverage QA

**From:** Andy
**Dispatched:** 2026-05-18
**Worker:** Yoni
**Worker's report:** `D:\Claude Playground\agents\andy\inbox\yoni_s1_012_done.md`
**UI tester (already done):** Vera — report `D:\Claude Playground\agents\andy\inbox\vera_s1_012_qa.md` (PASS WITH NOTES, 6 NITs)
**Branch:** `feat/mobile-shell` @ `cf682a7` (NOT pushed)
**Repo:** `D:\BuildAR\` — you are the ONLY agent in this repo right now

---

## Context

Yoni shipped a HomeScreen resume-active-session banner backed by a pluggable `ActiveSessionBackend` (in-memory default, AsyncStorage-ready). 46/46 tests passing (+11 from baseline). Vera already verified UI/contrast/a11y at PASS WITH NOTES.

Your scope is logic + coverage + the security shape of the new code (no XSS surface in RN, but watch for storage-quota leaks, race conditions, missing test coverage Vera flagged).

---

## Success criteria

Split findings Infrastructure vs Design per CLAUDE.md Rubric.

### Logic correctness
1. **Cache write only on step-save.** Confirm the cache-persistence call lives in the step-save handler (per Yoni's design decision), NOT on render, focus, or any effect that fires more than once per step. Trace from `SessionScreen.tsx` → step-save handler → cache helper. If it fires on focus or render, it would clobber `updatedAt` and break the 7-day stale guard.
2. **Stale guard math.** The 7-day window: how is "now" computed? `Date.now()` vs `new Date()` — either is fine; just confirm it's UTC-stable and not affected by device-time tampering edge cases. Boundary tests: exactly 7 days, 7 days + 1ms, 6 days 23h 59m.
3. **Cache invalidation paths.** Yoni cleared cache on (a) session completion and (b) 404 stale-prune. Confirm both code paths exist. Spell out in your report each location where the cache is written or cleared.
4. **404 prune.** When the user taps Resume but the project no longer exists (deleted from another device), Yoni claims the cache is pruned. Confirm error handling path.
5. **Pluggable backend pattern.** The `ActiveSessionBackend` interface — confirm:
   - In-memory implementation correctly resets to empty on each test (otherwise test isolation breaks)
   - One-line swap pattern Yoni claims (`setActiveSessionCacheBackend(AsyncStorage)`) actually wires through cleanly without changing call-sites
   - No leaky abstraction (e.g., serialization assumed at one layer but performed at another)

### Test coverage
6. **11 new tests claim — count + assert.** Yoni added 11 tests (target was 3+). List them. Confirm they cover:
   - Banner absent when no cache
   - Banner renders with project name when cache fresh
   - Banner absent when cache >7 days
   - Cache cleared on completion
   - 404 prune behavior
   - Resume navigation target
   - Step "N of M" formatting (especially N=1, N=total, missing total)
7. **`HomeScreen.test.tsx` existence.** Vera's NIT 6 noted no `HomeScreen.test.tsx` exists. Confirm or refute. If Yoni's tests live somewhere else (component test for `ResumeBanner.tsx`?), that's fine — note where they live.
8. **No existing test broken.** `pnpm --filter @buildar/mobile test` should pass 46/46. Run it.

### Security shape
9. **No injection surface.** Cache stores `projectName` from API response; it's rendered as RN `<Text>` (safe, no innerHTML). Confirm nothing concatenates `projectName` into a URL or shell command.
10. **Storage-quota DoS.** What's the upper bound on cache size? Single key, single object — bounded. Confirm no append-on-write pattern that could grow unboundedly.

---

## Verdict format

End with `PASS` / `PASS WITH NOTES` / `HOLD`. Worker = Yoni, testers = Vera (UI) + Jasmin (logic) — both names go on the task card.

Report destination: `D:\Claude Playground\agents\andy\inbox\jasmin_s1_012_logic_qa.md`

---

## Hard rules

- Do NOT modify any code. You're a tester.
- Do NOT modify `tasks/active_tasks.json` or `.env`.
- Do NOT push to GitHub.
- Do NOT re-litigate Vera's UI/contrast findings — your scope is logic + coverage. If you spot a contrast issue Vera missed, note it as cross-lane and stop.

---

## Token discipline

Target ≤200 tool uses. Focus reads listed in Yoni's report. Run the one `pnpm test` invocation to confirm 46/46.

— Andy
