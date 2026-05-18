# Yoni — BuildAR Pro S1-012-P1 polish (close Vera NIT 4 + Jasmin DESIGN-1/2/3)

**From:** Andy
**Dispatched:** 2026-05-18
**Task:** BUILDAR-S1-012-P1 (polish round on the S1-012 banner)
**Branch:** continue on `feat/mobile-shell` (extend with 1 commit)
**Tester:** Vera (re-verify NIT 4 closed) + Jasmin (re-verify DESIGN-1/2/3 closed)

---

## Why this matters

S1-012 shipped GREEN (Vera PASS WITH NOTES, Jasmin PASS WITH NOTES). Vera flagged 6 NITs, Jasmin flagged 3 DESIGN notes. Most are deferrable, but four are actionable now and cheap to close:

- **Vera NIT 4** — `accessibilityLabel` on Resume CTA omits step context. The brief explicitly said "Resume Project X at step N of M" — you shipped "Resume X". Brief miss.
- **Jasmin DESIGN-1 / Vera NIT 6** — no `HomeScreen.test.tsx` exists. Your tests live in `activeSessionCache.test.ts` + `ResumeBanner.test.tsx`. Add a HomeScreen wiring test (banner mounts/unmounts correctly + focus-effect re-reads cache + 404 prune path triggers).
- **Jasmin DESIGN-2** — no exact-boundary tests for the 7-day stale guard. Add 3 boundary tests: exactly 7d (passes), 7d + 1ms (stale), 6d 23h 59m 999ms (passes).
- **Jasmin DESIGN-3** — no N=1, N=total, or missing-total step-formatting tests. Add 3 tests: step 1 of 7, step 7 of 7, undefined totalSteps fallback.

Total: 1 label tweak + 7 new tests = ≤30 lines of code + ≤80 lines of tests.

---

## Success criteria

### Code
1. `apps/mobile/src/components/ResumeBanner.tsx` (or wherever the CTA lives): swap the `accessibilityLabel` to include project name AND step context. Format suggestion: `Resume ${projectName} at step ${currentStep} of ${totalSteps}` — or `Resume ${projectName}` if totalSteps is unknown. Confirm with the brief language Lena wrote.

### Tests (target: 53/53 passing, was 46/46)
2. Create `apps/mobile/src/__tests__/HomeScreen.test.tsx` with at minimum:
   - Banner mounts when cache has fresh entry
   - Banner unmounts when cache cleared
   - Focus effect re-reads cache (mock focus event)
   - 404 prune path: tap Resume on stale project → cache cleared
3. Add 3 boundary tests to `activeSessionCache.test.ts`:
   - `updatedAt` = exactly 7 days ago → fresh (passes guard)
   - `updatedAt` = 7 days + 1ms ago → stale (banner absent)
   - `updatedAt` = 6d 23h 59m 999ms ago → fresh
4. Add 3 step-formatting tests to `ResumeBanner.test.tsx` (or wherever the format helper lives):
   - `{ currentStep: 1, totalSteps: 7 }` → "Step 1 of 7"
   - `{ currentStep: 7, totalSteps: 7 }` → "Step 7 of 7"
   - `{ currentStep: 3, totalSteps: undefined }` → falls back to "Resume" (no step suffix) OR document the chosen fallback

### Quality bars
5. `pnpm --filter @buildar/mobile lint` passes
6. `pnpm --filter @buildar/mobile typecheck` passes
7. `pnpm --filter @buildar/mobile test` shows ≥53 tests passing (46 baseline + ≥7 new)

---

## What NOT to do

- Do NOT address Vera's other NITs (1 disabled-CTA, 2 width:32, 3 gap:2, 5 ratio quote tracking issue). Those are deferred.
- Do NOT change banner colors or layout.
- Do NOT widen the `ActiveSessionBackend` interface or swap to a real AsyncStorage implementation — that's a separate task.
- Do NOT push to GitHub or merge to main. Andy gates pushes.
- Do NOT touch any other branch (feat/orchestrator-mvp, feat/phase-b-prereqs, feat/events-schema-alignment).

---

## Infrastructure vs Design (per CLAUDE.md Rubric)

**Infrastructure:** None expected. Test-only + 1 label change.

**Design:** If the brief's exact wording for the accessibilityLabel differs from what I suggested ("Resume {project} at step {N} of {M}"), use the brief's wording. Note in your report which source you used.

---

## Commit strategy

1 commit on `feat/mobile-shell`:
```
fix(mobile): close Vera NIT 4 + Jasmin DESIGN-1/2/3 on resume banner
- accessibilityLabel now includes step context
- add HomeScreen.test.tsx (wiring + focus + 404 prune)
- add 7d stale-guard boundary tests
- add step-formatting edge cases
```

NOT pushed.

---

## Reporting

Write to `D:\Claude Playground\agents\andy\inbox\yoni_s1_012_p1_done.md`:
- Commit SHA + git log --oneline (since branch tip)
- Files touched
- Test count (target: ≥53, was 46)
- accessibilityLabel final string
- Status: DONE or BLOCKED

Telegram when done:
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-012-P1" "Polish round closed. <test counts>. Report at agents/andy/inbox/yoni_s1_012_p1_done.md."
```

---

## Constraints

- **Repo:** `D:\BuildAR\` on existing `feat/mobile-shell` branch
- **You are the ONLY agent in `D:\BuildAR\` right now.** Sequential.
- **Token discipline:** small surgical polish. Target ≤150 tool uses.

After you: Vera re-verifies NIT 4 closed, Jasmin re-verifies DESIGN-1/2/3 closed.

— Andy
