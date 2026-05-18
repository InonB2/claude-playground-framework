# Yoni — BUILDAR-S1-012 DONE

**From:** Yoni
**To:** Andy
**Date:** 2026-05-18
**Task:** BUILDAR-S1-012 — HomeScreen resume-active-session banner
**Branch:** `feat/mobile-shell` @ `cf682a7` (NOT pushed)
**Status:** DONE

---

## Commits added

```
cf682a7 feat(mobile): HomeScreen resume-active-session banner + AsyncStorage-style cache
```

(Combined into 1 commit per brief allowance — edits naturally interleaved.)

## Files touched / created

Created:
- `apps/mobile/src/lib/activeSessionCache.ts` — typed cache abstraction with pluggable backend
- `apps/mobile/src/components/ResumeBanner.tsx` — banner UI
- `apps/mobile/src/__tests__/activeSessionCache.test.ts` — 7 tests
- `apps/mobile/src/__tests__/ResumeBanner.test.tsx` — 4 tests

Modified:
- `apps/mobile/src/screens/HomeScreen.tsx` — cache read on focus, banner render, Resume handler
- `apps/mobile/src/screens/SessionScreen.tsx` — cache write on mount + step advance, clear on completion

## Test count

- Before: 35/35 passing
- After: **46/46 passing** (added 11, target was 3+)
- Lint: clean. Typecheck: clean.

## Cache contract

- **Key:** `@buildar/active_session` (constant `ACTIVE_SESSION_KEY`)
- **Stale window:** 7 days (constant `STALE_AFTER_MS = 7 * 24 * 60 * 60 * 1000`)
- **Shape:**
  ```ts
  {
    sessionId: string,
    projectId: string,
    projectName: string,
    currentStepIndex: number,   // 0-based
    totalSteps: number,
    updatedAt: string,          // ISO-8601
  }
  ```

## Success criteria coverage (all 8)

1. Banner renders only when cache is present and fresh — yes (HomeScreen `resumeRecord != null` gate).
2. Shows project name + "Step N of M" + Resume CTA — yes (`Step ${i+1} of ${total}`, falls back to "Resume" when `totalSteps === 0`).
3. Tap Resume navigates to SessionScreen with sessionId + project — yes (`getProject` then `navigation.navigate('Session', {...})`).
4. Cache write lives in step-save handler — yes (`persistCache` called on mount, after successful `patchSession`, and on optimistic advance after a save failure).
5. Cache invalidation on completion — yes (`clearActiveSession()` after the `status: 'completed'` patch). Also clears on `getProject` 404 from Resume.
6. Stale guard — yes (`loadActiveSession()` enforces 7-day cutoff and clears the stale record on read).
7. WCAG AA — yes (banner uses `colors.primary` `#C0461A` for CTA fill with white text = 5.08:1 PASS, `colors.primaryDark` `#B8431A` for orange subtitle text on `colors.surface` white background). Zero new hex literals.
8. 3+ new tests, existing 35/35 still pass — yes (+11 added, 46/46 total).

## Findings — Infrastructure

- **AsyncStorage native module is NOT linked** in this Bare RN project. `@react-native-async-storage/async-storage` is not in `apps/mobile/package.json` and not present under `node_modules`. The brief said "do not add a new dependency" and "use the AsyncStorage already wired in."
- **Solution + prevention** (per CLAUDE.md Rubric point 1):
  - **Fix:** I shipped a pluggable cache backend — `ActiveSessionBackend` interface with an in-memory default. The API surface (`saveActiveSession`, `loadActiveSession`, `clearActiveSession`) is identical to what an AsyncStorage-backed cache would expose. When the dep lands, one call to `setActiveSessionCacheBackend(AsyncStorage)` at app init makes the cache persistent across reloads. No call-site changes needed.
  - **Prevention:** Documented this at the top of `activeSessionCache.ts` so the next agent doesn't assume persistence works across cold-start without the swap. Also: the brief incorrectly stated AsyncStorage was wired — flagging here so Andy can correct the assumption in the next sprint brief.
- **Storage quota:** Negligible. Single JSON record (~150 bytes), single key, written only on mount + each `Next` press (handful per session).

## Findings — Design

- **Cache write location:** placed in the step-save handler (`goNext`) and once on `useEffect` mount — NOT on every render or on focus. Render-side writes would clobber `updatedAt` during fade animations and re-renders, defeating the stale guard.
- **Most-recent-wins scope:** single record, last save overwrites. Documented in the helper's doc comment. If the user has 3 in-flight sessions across 3 projects, only the most recently touched one surfaces in the banner — matches Lena's "your last project" framing.
- **Exit semantics:** the existing SessionScreen Exit modal copy is "Your progress is saved. Exit?" — there is no "Exit and discard" affordance to wire into. Per scope rule, I did NOT add one. Cache is preserved on Exit, cleared only on completion (or on a 404 from the Resume fetch, which auto-prunes a deleted project). If "Exit and discard" lands as a future NIT, add `clearActiveSession()` in that branch.
- **Resume 404 handling:** if the cached project has been deleted server-side, the `getProject` call throws an `ApiError` with `status: 404`. The Home `onResume` catches this, calls `clearActiveSession()`, and removes the banner. Inline error line shows for non-404 errors (transient network).
- **Race on focus:** `useFocusEffect` cleanup uses an `active` flag so a fast back-and-forth doesn't set state on an unmounted screen.

## What I did NOT touch (per brief)

- No new API route, no new dependency.
- Did not push, did not merge.
- Did not touch orchestrator / phase-b-prereqs / events-schema-alignment branches.
- Did not address other Vera NITs (1, 2, 3, 8, 9, 10).
- Did not modify `tasks/active_tasks.json`.

## Next steps for QA

- **Vera (UI/a11y):** verify banner contrast on the warm-white background (`#F5F5F0`); confirm 44pt touch target on the Resume CTA; confirm `accessibilityLiveRegion` announcement on first appearance; confirm banner does not push the FlatList into a layout shift on slow loads.
- **Jasmin (logic):** verify cache write timing (mount + after successful step PATCH only); verify 7-day stale guard edge cases; verify completion path clears cache before navigation.replace; verify the in-memory backend swap path documented in the helper comment.

— Yoni
