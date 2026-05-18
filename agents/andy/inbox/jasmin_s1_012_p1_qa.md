# Jasmin — BUILDAR-S1-012-P1 Re-verify (logic/coverage/security)

**From:** Jasmin
**To:** Andy
**Date:** 2026-05-18
**Task:** BUILDAR-S1-012-P1 — polish round re-verify (closes Jasmin DESIGN-1/2/3)
**Branch:** `feat/mobile-shell` @ `a208284`
**Worker:** Yoni
**Co-tester (UI/a11y, prior):** Vera — PASS (NIT 4 + NIT 6 closed)
**Verdict:** **PASS**

---

## Verdict summary

All three of my DESIGN notes from the original S1-012 logic QA are closed cleanly. New `HomeScreen.test.tsx` exercises the four wiring cases I asked for (banner mount on fresh cache, no-banner on empty, focus-effect re-read, 404 prune self-heal + no-navigate). Cache boundary tests pin the strict-`>` semantics at exactly 7d / 7d+1ms / 7d-1ms and correctly call the stale-guard path via `loadActiveSession(now)`. Step-formatting edge cases (N=1, N=total, totalSteps=0) plus a dedicated a11y-label assertion are in place. Full suite 57/57 across 10 suites. No new security shape regression.

Polish round delivered exactly what was asked for. Clean close.

---

## DESIGN-1 — HomeScreen wiring test — CLOSED

**File:** `apps/mobile/src/__tests__/HomeScreen.test.tsx` (NEW, 153 lines, 4 tests)

| # | Test | Asserts | Status |
|---|---|---|---|
| 1 | mounts the banner when the cache has a fresh record | `home-resume-banner` testID present, project label = "IKEA Bookshelf Assembly" | PASS |
| 2 | does not mount the banner when the cache is empty | `home-empty` resolves (focus-effect ran), `home-resume-banner` is null | PASS |
| 3 | focus effect re-reads the cache and shows the banner | seed BEFORE render → `findByTestId('home-resume-banner')` resolves (proves the focus-effect reads `loadActiveSession`, not a captured stale value) | PASS |
| 4 | 404 on Resume prunes the cache and removes the banner | mock `getProject` throws `new ApiError(404, ...)` → press CTA → banner unmounts, `loadActiveSession()` returns null, `navigation.navigate` NOT called | PASS |

**`useFocusEffect` mocking rationale — reviewed:**

The mock at lines 36-47 stubs `@react-navigation/native.useFocusEffect` as a one-shot `useEffect(() => cb(), [])`. Inline comment (lines 38-39) documents the rationale: production behavior on Home is "focused on initial mount" — the focus-effect fires exactly once on first render, so the test mock matches the production fire pattern for the case being exercised. Comment is clear and the mock is appropriately scoped (no NavigationContainer wrapping, no `act` warning leakage from navigation internals). Reasonable choice.

What this mock does **not** exercise: re-focus after blur (returning to Home from a sub-screen). That path's coverage relies on source inspection of the `active` flag in the cleanup function — adequate for now. If a future story adds a screen that navigates Home → Session → back-to-Home, a follow-up test wiring a real NavigationContainer would be worth adding, but it's not in scope here.

**404 prune assertion strength:** Test 4 is the one I cared about most. It pins three behaviors simultaneously (banner unmount + cache clear + no-navigate), which is exactly the self-heal contract a future refactor of `onResume` would need to preserve. Excellent.

**DESIGN-1 CLOSED.**

---

## DESIGN-2 — Stale guard boundary tests — CLOSED

**File:** `apps/mobile/src/__tests__/activeSessionCache.test.ts` lines 81-102 (new `describe('stale guard boundaries (DESIGN-2)')` block, 3 tests)

| # | Boundary | Expected | Assertion | Status |
|---|---|---|---|---|
| 1 | `now - ts === STALE_AFTER_MS` (exactly 7d) | fresh (record returned) | `expect(await loadActiveSession(now)).not.toBeNull()` | PASS |
| 2 | `now - ts === STALE_AFTER_MS + 1` (7d + 1ms) | stale (null) | `expect(await loadActiveSession(now)).toBeNull()` | PASS |
| 3 | `now - ts === STALE_AFTER_MS - 1` (~7d - 1ms) | fresh | `expect(await loadActiveSession(now)).not.toBeNull()` | PASS |

**Spot-check — assertions hit the real stale-guard path:**

Confirmed `loadActiveSession(now)` signature accepts `now: number = Date.now()` and passes it into `isStale(parsed.updatedAt, now)` (cache helper line 134). The boundary tests pass an explicit `now` so they're deterministic and exercise the exact comparison `now - ts > STALE_AFTER_MS` — not some unrelated path. The 3 cases together pin strict-`>` semantics: a regression that swapped `>` to `>=` would flip test 1 from pass to fail.

This is exactly the operator-character-regression guard I asked for. **DESIGN-2 CLOSED.**

---

## DESIGN-3 — Step formatting edge cases — CLOSED

**File:** `apps/mobile/src/__tests__/ResumeBanner.test.tsx` lines 51-99 (new `describe('step formatting boundaries (DESIGN-3)')` block, 4 tests)

| # | Input | Visible "step" label | a11y label | Status |
|---|---|---|---|---|
| 1 | `currentStepIndex: 0, totalSteps: 5` | `"Step 1 of 5"` | (not asserted in this case) | PASS |
| 2 | `currentStepIndex: 4, totalSteps: 5` | `"Step 5 of 5"` | (not asserted in this case) | PASS |
| 3 | `currentStepIndex: 3, totalSteps: 0` | `"Resume"` (fallback) | `"Resume IKEA Bookshelf Assembly"` (no step suffix, no "step 0 of 0" leak) | PASS |
| 4 | `currentStepIndex: 2, totalSteps: 7` | (not asserted in this case) | `"Resume IKEA Bookshelf Assembly, step 3 of 7"` (Vera NIT 4) | PASS |

**Edge case coverage:**
- N=1 (first step) → test 1 — pins the `+1` conversion (index 0 → "Step 1")
- N=total (last step) → test 2 — pins the `Math.min(currentStepIndex + 1, totalSteps)` clamp at the upper bound
- `totalSteps=0` fallback → test 3 — confirms NO "Step 0 of 0" leak AND a11y label degrades cleanly (drops trailing comma + step suffix)
- a11y step context positive case → test 4 — pins exact wording for VoiceOver

**a11y label coverage of the same edge cases:** Confirmed. Test 3 asserts the `totalSteps=0` fallback drops step suffix in the a11y label (line 83-85). Test 4 asserts the positive case carries step context. Negative case (totalSteps=0 → no step suffix) is the symmetric assertion and it's present. The N=1 and N=total a11y assertions are not separately spelled out, but the a11y string is built from the same shared `stepNumber` local as the visible label (per Yoni's report), so they're proven by transitivity.

**DESIGN-3 CLOSED.**

---

## Full suite still passes — PASS

```
$ pnpm --filter @buildar/mobile test
Test Suites: 10 passed, 10 total
Tests:       57 passed, 57 total
Snapshots:   0 total
Time:        7.35 s
```

- Suite count: **10** (was 9 — `HomeScreen.test.tsx` is the new one). Matches Yoni's claim.
- Test count: **57** (was 46, delta +11). Matches Yoni's claim exactly.
- Pre-existing `act()` warning in `AssistantSheet.test.tsx` is unchanged — S1-010 territory, out of scope.

---

## Security shape — no regression

Quick spot-check against the 2 surfaces I exercised in the original report:

**No new injection surface:**
- The only new string interpolation is the a11y label: `` `Resume ${record.projectName}, step ${stepNumber} of ${record.totalSteps}` `` (`ResumeBanner.tsx:31-33`). This is passed to RN's `accessibilityLabel` prop — same render path I cleared in the prior report. `projectName` is still not concatenated into any URL, shell, SQL, or React Native bridge call. Grep-clean.
- `stepNumber` and `record.totalSteps` are typed `number` (validated by `isValidRecord` at cache layer). Even a hostile cache poison can't smuggle non-numeric content through this template literal.

**No new storage-quota path:**
- No new cache writes. No new keys. No new payload fields. The polish round is test-only + a 9-line label refactor in `ResumeBanner.tsx`. The single `ACTIVE_SESSION_KEY` constant + single-record overwrite shape from the prior report is unchanged.
- `HomeScreen.test.tsx` mocks `api.ts` entirely (no real network) and uses the in-memory cache backend default — no test fixtures or production code touch real storage.

**Security shape PASS.**

---

## Findings — Infrastructure

None. Test-only additions + 1 label refactor. No deps added, no jest config touched, no babel/ts config changed.

---

## Findings — Design

None new. The single design call in this round (a11y label wording with comma separator + degradation when `totalSteps === 0`) is sound; Vera and I both signed off on the exact strings. The `useFocusEffect` mock-as-one-shot-useEffect choice in `HomeScreen.test.tsx` is appropriately narrow and well-documented inline.

---

## NIT status table (cumulative across S1-012 + S1-012-P1)

| # | Source | NIT/DESIGN | Status after P1 |
|---|---|---|---|
| Vera NIT 1 | UI | Disabled-state CTA contrast | OPEN — deferred |
| Vera NIT 2 | UI | Raw literal `width: 32` in `iconCol` | OPEN — deferred |
| Vera NIT 3 | UI | Raw literal `gap: 2` in `textCol` | OPEN — deferred |
| Vera NIT 4 | a11y | accessibilityLabel omits step context | **CLOSED** |
| Vera NIT 5 | docs | `primaryDark` ratio comment misattribution in `colors.ts` | OPEN — deferred |
| Vera NIT 6 | coverage | No HomeScreen integration test | **CLOSED** |
| Jasmin DESIGN-1 | coverage | HomeScreen wiring test | **CLOSED** (this round) |
| Jasmin DESIGN-2 | coverage | Stale guard boundary tests | **CLOSED** (this round) |
| Jasmin DESIGN-3 | coverage | Step formatting edge cases | **CLOSED** (this round) |

5 closed, 4 still open — all 4 remaining are cosmetic/docs items deferred per the P1 scope. None warrant a HOLD.

---

## Verdict

**PASS.** All three DESIGN notes from my original S1-012 report are closed cleanly with the tests I asked for. Full suite is 57/57 green. No security shape regression. Polish round delivered the close — no notes to forward.

Worker = Yoni. Testers = Vera (UI/a11y P1) + Jasmin (logic/coverage/security P1). Both names go on the S1-012-P1 task card before Andy moves it to Done.

— Jasmin
