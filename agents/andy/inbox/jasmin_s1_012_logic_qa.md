# Jasmin — BUILDAR-S1-012 Logic / Coverage / Security-Shape QA Report

**From:** Jasmin
**To:** Andy
**Date:** 2026-05-18
**Task:** BUILDAR-S1-012 — HomeScreen resume-active-session banner
**Branch:** `feat/mobile-shell` @ `cf682a7`
**Worker:** Yoni
**Co-tester (UI/a11y, prior):** Vera — PASS WITH NOTES (6 NITs)
**Verdict:** **PASS WITH NOTES**

---

## Verdict summary

Logic is sound. Cache write timing is correct, stale guard math is UTC-stable and uses a strict-greater comparison (the intuitive boundary semantics), invalidation paths are both wired, the 404 prune triggers correctly off `ApiError.status`, and the pluggable-backend pattern is clean with a dedicated `__resetActiveSessionCacheForTests` seam. Full suite passes 46/46. No injection surface in RN-rendered `<Text>`. Storage upper bound is a single ~150-byte JSON record — no DoS shape.

Three minor coverage / belt-and-suspenders notes below, none blocking. No HOLD warranted.

---

## Test suite result

```
$ pnpm --filter @buildar/mobile test
Test Suites: 9 passed, 9 total
Tests:       46 passed, 46 total
```

Confirmed: 46/46, matches Yoni's claim. The lone `act()` warning in `AssistantSheet.test.tsx` is pre-existing (S1-010 territory), unrelated to this change.

---

## Logic correctness (5 items)

### 1. Cache write only on step-save — PASS

Traced every `saveActiveSession` call site:

| Location | Line | Trigger |
|---|---|---|
| `SessionScreen.tsx` `persistCache` | 49 | called from 3 places below |
| `SessionScreen.tsx` `useEffect` mount-seed | 63-65 | fires once on mount; deps = `[persistCache]`, memoized over stable inputs (`project.id`, `project.title`, `sessionId`, `totalSteps`) — re-fires only on session change, NOT on render |
| `SessionScreen.tsx` `goNext` happy path | 100 | after successful `patchSession({current_step_index})` |
| `SessionScreen.tsx` `goNext` catch path | 110 | optimistic advance when API errors but UI advances (per Lena's "don't block on save failure") |

Critically, `persistCache` is **NOT** called inside `animateTransition`, on focus, or in any handler that fires more than once per actual step change. The 150ms fade transition will not re-write the cache. The stale guard's `updatedAt` field can therefore only advance on real session lifecycle events — exactly what the brief required.

Minor note: the mount-seed write (line 64) is a once-per-mount call, not a true "step save" — but it's at step 0, immediately on session start, and matches Yoni's documented design rationale ("banner appears even if the user backgrounds the app before reaching the second step"). Not a defect.

### 2. Stale guard math — PASS

`activeSessionCache.ts:75-79`:
```ts
function isStale(updatedAt: string, now: number): boolean {
  const ts = Date.parse(updatedAt);
  if (Number.isNaN(ts)) return true; // malformed timestamp = treat as stale
  return now - ts > STALE_AFTER_MS;
}
```

- "Now" is `Date.now()` (default arg in `loadActiveSession`, line 113) → epoch milliseconds, timezone-independent. UTC-stable. PASS.
- `Date.parse(ISO-8601)` → epoch ms. Symmetric with `Date.now()`. PASS.
- Boundary semantics: `>` (strict greater), not `>=`. A record at **exactly** 7d (`now - ts === STALE_AFTER_MS`) is **NOT stale** — first millisecond past 7d is stale. This is the intuitive interpretation and matches the helper's contract comment.
- Malformed timestamp → treated as stale → record auto-pruned on next read (line 131). Good defensive choice; prevents a poison record from sticking.
- Device-time tampering: out of scope — there is no signed server-side timestamp here, and the worst case (user moves clock forward) is "banner disappears prematurely" which is a UX papercut, not a security concern.

### 3. Cache invalidation paths — PASS

Spell-out of every `clearActiveSession` call site:

| # | Location | Line | Trigger |
|---|---|---|---|
| 1 | `SessionScreen.tsx` `goNext` | 91 | after `patchSession({status:'completed'})` succeeds, before `navigation.replace('Completion', …)` |
| 2 | `HomeScreen.tsx` `onResume` catch | 87 | when `getProject(resumeRecord.projectId)` throws with `status === 404` |
| 3 | `activeSessionCache.ts` `loadActiveSession` | 127 | JSON.parse failure (corrupt payload self-heal) |
| 4 | `activeSessionCache.ts` `loadActiveSession` | 131 | schema validation failure (`isValidRecord` returns false) |
| 5 | `activeSessionCache.ts` `loadActiveSession` | 135 | stale record (>7d) on read |

Yoni claimed the two primary paths (completion + 404 prune). Confirmed, plus three self-healing paths inside the helper. All five are correct.

### 4. 404 prune — PASS

`HomeScreen.tsx:80-89`:
```ts
} catch (e) {
  const msg = e instanceof Error ? e.message : "Couldn't resume session.";
  setResumeError(msg);
  const status = (e as { status?: number } | null)?.status;
  if (status === 404) {
    await clearActiveSession();
    setResumeRecord(null);
  }
}
```

Cross-checked `api.ts:22-28`: `ApiError` is a real class with a public readonly `status: number`, thrown from `request()` on every non-2xx. The narrow cast `(e as { status?: number } | null)?.status` works for `ApiError` instances and is defensive against unrelated errors (transient network → `status` is undefined → falls through to "show inline error" without clearing the cache). Good shape.

Note: a stricter `e instanceof ApiError && e.status === 404` would be more type-safe, but the duck-typed read is functionally equivalent here and the difference is purely stylistic. Not flagging as a NIT.

### 5. Pluggable backend pattern — PASS

- **In-memory backend reset between tests:** `__resetActiveSessionCacheForTests` (line 71) creates a fresh `Map` and reassigns the module-level `backend` reference. The test file calls it in `beforeEach` (line 19-21). I verified test isolation manually: each test starts with an empty store. PASS.
- **One-line swap:** `setActiveSessionCacheBackend(next)` (line 66) reassigns the `backend` variable. All public helpers (`saveActiveSession`, `loadActiveSession`, `clearActiveSession`) read through `backend.*`, so a single call at app init wires AsyncStorage in with zero call-site churn. PASS.
- **No leaky abstraction:** Serialization (`JSON.stringify` / `JSON.parse`) lives entirely in `activeSessionCache.ts` (lines 106, 124). The `ActiveSessionBackend` interface trades only `string` values — matches AsyncStorage's actual contract (`string | null`). When the AsyncStorage dep lands, the swap is a literal `setActiveSessionCacheBackend(AsyncStorage)`. PASS.
- **Try/catch swallows in `saveActiveSession` / `clearActiveSession`:** intentional, documented ("cache failure must not break the session flow"). Good — cache is best-effort by design.

---

## Test coverage (3 items)

### 6. 11 new tests — counted + asserted

`activeSessionCache.test.ts` — **7 tests:**
1. `returns null when nothing has been saved`
2. `round-trips a saved record with a fresh timestamp`
3. `treats records older than 7 days as stale and returns null` (8 days ago)
4. `keeps records inside the stale window` (6 days ago)
5. `clears the record on demand`
6. `drops corrupt JSON payloads on read`
7. `STALE_AFTER_MS is exactly 7 days`

`ResumeBanner.test.tsx` — **4 tests:**
8. `renders the project name and 1-based step label` (proves N+1 conversion: index 2 → "Step 3 of 7")
9. `falls back to "Resume" when totalSteps is 0` (covers missing-total path)
10. `invokes onResume when the CTA is pressed` (navigation handler wiring)
11. `renders an error line when errorMessage is set`

**Total: 7 + 4 = 11.** Matches Yoni's claim exactly.

**Brief checklist coverage:**
- Banner absent when no cache → covered indirectly (cache returns null, HomeScreen renders `null`); not asserted at the HomeScreen layer — see item 7.
- Banner renders with project name when fresh → **#8 PASS**
- Banner absent when cache >7d → **#3 PASS** at cache layer; banner-layer assertion not separate (relies on the cache returning null) — see item 7.
- Cache cleared on completion → **#5 PASS** at cache layer (clear-on-demand); the SessionScreen happy-path is not directly asserted (no SessionScreen test exists; not in Yoni's scope) — see DESIGN-1.
- 404 prune behavior → covered by reading `HomeScreen.tsx:86-89`; not directly asserted by a test (no HomeScreen test) — see item 7 and DESIGN-1.
- Resume navigation target → **#10 PASS** (CTA invokes handler; the `navigation.navigate('Session', …)` call itself is verified by source read, not by test).
- Step "N of M" formatting — N=1 case: NOT asserted (index 0 → "Step 1 of N" would be valuable). N=total: NOT asserted. Missing total: **#9 PASS**.

Two formatting edge-case tests (N=1 and N=total) would round this out, but the underlying code (`Math.min(record.currentStepIndex + 1, record.totalSteps)`) is trivially correct on inspection and the bound is explicit — clamps any over-count to `totalSteps`. Filing as DESIGN-2 below, not a HOLD.

### 7. `HomeScreen.test.tsx` existence — CONFIRMED ABSENT (matches Vera NIT 6)

Verified `apps/mobile/src/__tests__/` directory listing — files present are:
```
activeSessionCache.test.ts
api.test.ts
ARView.test.tsx
AssistantSheet.test.tsx
DifficultyIndicator.test.tsx
format.test.ts
ProjectCard.test.tsx
ResumeBanner.test.tsx
StepProgressIndicator.test.tsx
```

No `HomeScreen.test.tsx`. Vera's NIT 6 stands. Yoni's tests target the cache (in isolation) and the banner component (in isolation) — the wiring (banner-present + list, banner-present + empty, banner-absent + list, banner-absent + error, focus-refresh triggering reload) is unit-tested only by source read on my side. Filing as DESIGN-1 below.

### 8. Full suite still 46/46 — PASS

See "Test suite result" section above. `pnpm --filter @buildar/mobile test` → 9 suites, 46 tests, all green.

---

## Security shape (2 items)

### 9. No injection surface — PASS

`projectName` from API response is rendered in two places only:
- `ResumeBanner.tsx:39` — `<Text>{record.projectName}</Text>` (RN `<Text>`, no `innerHTML` equivalent, no shell interpretation)
- `ResumeBanner.tsx:60` — `accessibilityLabel={`Resume ${record.projectName}`}` (string interpolation into a screen-reader label; not eval'd, not parsed)

Cache write/read paths:
- `JSON.stringify` on save, `JSON.parse` on load — no `eval`, no `new Function`, no template injection.
- Storage key is a hardcoded constant (`@buildar/active_session`), not user-derived — no key-confusion attack.
- `projectName` is never concatenated into a URL, shell command, SQL string, or React Native bridge call. Greps confirmed.

No injection surface. PASS.

### 10. Storage-quota DoS — PASS

- **Single key:** `ACTIVE_SESSION_KEY` is a constant string. No per-user, per-session, per-day key proliferation.
- **Single record:** every `saveActiveSession` calls `setItem(KEY, JSON.stringify(toStore))` — overwrites, never appends.
- **Bounded payload size:** `ActiveSessionRecord` is 4 strings (UUIDs ~36 chars each + `projectName` + ISO timestamp ~24 chars) and 2 small integers. Realistic ceiling ~500 bytes including a pathological `projectName`. Even at 10 KB the impact on AsyncStorage's 6 MB iOS default quota is negligible.
- **No write loops:** all `persistCache` calls are guarded by user action (step advance) or once-per-mount lifecycle. No timer, no polling, no animation-loop write.

No DoS shape. PASS.

---

## Findings — Infrastructure

None. No build, dependency, or environment issues introduced by this change. The pluggable backend correctly avoids adding a native dep prematurely. AsyncStorage swap path is documented and one-line.

---

## Findings — Design

### DESIGN-1 — No HomeScreen integration test for banner wiring (echoes Vera NIT 6)

- **What:** `HomeScreen.test.tsx` does not exist. The 4 state combinations (banner+list, banner+empty, no-banner+list, no-banner+error) and the `useFocusEffect` reload-on-focus behavior are verified only by source inspection.
- **Why it matters for logic QA:** The 404 prune path (`HomeScreen.tsx:86-89`) and the focus-refresh path (`HomeScreen.tsx:57-68` with the `active` flag against setState-on-unmounted) are exactly the kind of code that benefits from a regression test. Source inspection caught nothing wrong, but a future refactor of the focus effect could silently break self-healing on 404.
- **Severity:** Notes-level, not blocking. Yoni's brief targeted "3+ tests"; he delivered 11. Adding HomeScreen-layer tests is incremental hardening, not a defect.
- **Fix:** Add `HomeScreen.test.tsx` covering: (a) banner renders when `loadActiveSession` returns a record, (b) banner absent when it returns null, (c) `onResume` 404 path triggers `clearActiveSession` and removes banner, (d) `useFocusEffect` re-reads the cache when Home regains focus.
- **Prevention:** Codify a "screen-level tests required for screens with side-effecting `useFocusEffect`" rule in the mobile testing SOP.

### DESIGN-2 — Stale guard boundary tests not exhaustive

- **What:** Yoni's tests cover the "comfortably stale" (8d ago) and "comfortably fresh" (6d ago) cases. The brief asked for the tight boundaries: exactly 7d, 7d + 1ms, 6d 23h 59m.
- **Why it matters:** The code uses strict `>` (line 78), so the boundary semantics are: `now - ts > 7d` is stale, `===` is fresh. That's the right call, but a regression where someone "fixes" `>` to `>=` would not be caught by the current tests.
- **Severity:** Notes-level. The bug surface is one operator character.
- **Fix:** Add three tests — `now - ts === STALE_AFTER_MS` (expect fresh), `now - ts === STALE_AFTER_MS + 1` (expect stale), `now - ts === STALE_AFTER_MS - 1` (expect fresh).
- **Prevention:** Add boundary-condition checklist to the test review template for any helper with a time- or threshold-based predicate.

### DESIGN-3 — Step formatting edge-case tests missing (N=1, N=total)

- **What:** Only the mid-range case (index 2, total 7 → "Step 3 of 7") and the missing-total case (totalSteps=0 → "Resume") are asserted.
- **Why it matters:** The clamp `Math.min(record.currentStepIndex + 1, record.totalSteps)` is the kind of off-by-one logic where an N=1 (index 0) or N=total (index = totalSteps - 1) test pins behavior cheaply. Currently if someone removed the `+1` or the `Math.min`, only manual QA would catch it.
- **Severity:** Notes-level.
- **Fix:** Add two assertions to `ResumeBanner.test.tsx` — `currentStepIndex: 0, totalSteps: 5` → "Step 1 of 5"; `currentStepIndex: 4, totalSteps: 5` → "Step 5 of 5".
- **Prevention:** Same template note as DESIGN-2 (boundary checklist).

---

## What I checked but found no issue with

- `useFocusEffect` cleanup with `active` flag — correctly guards against setState-on-unmounted in fast-navigate scenarios.
- `useEffect` mount-seed dependency array — `[persistCache]` with stable memoized deps means no re-fire storm.
- `JSON.parse` failure path self-heals (clears the corrupt record) — test #6 proves it.
- Schema validator `isValidRecord` is strict on every field type — no partial-record acceptance.
- Try/catch wrappers in `saveActiveSession` / `clearActiveSession` swallow errors silently — correct for best-effort cache.
- No `JSON.parse(raw)` is fed to any code path that trusts shape — every read goes through `isValidRecord` first.
- Cache helper module-level `backend` variable is reassignable, but the public API doesn't expose it — no test/production confusion possible without using `setActiveSessionCacheBackend` deliberately.

---

## Cross-lane note (none)

I spotted no UI/contrast issues Vera missed.

---

## Verdict

**PASS WITH NOTES.** Ship it. 3 DESIGN-level coverage hardening notes (DESIGN-1, DESIGN-2, DESIGN-3) — none blocking, all suitable as follow-up tickets. Logic is correct, security shape is clean, full suite green at 46/46.

Worker = Yoni. Testers = Vera (UI/a11y) + Jasmin (logic/coverage/security). Both names go on the task card before Andy moves it to Done.

— Jasmin
