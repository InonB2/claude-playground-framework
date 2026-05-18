# Vera — BUILDAR-S1-012-P1 UI/a11y Re-verify

**From:** Vera
**To:** Andy
**Date:** 2026-05-18
**Task:** BUILDAR-S1-012-P1 — polish round re-verify
**Branch:** `feat/mobile-shell` @ `a208284`
**Worker:** Yoni
**Scope:** Re-verify NIT 4 (a11y label step context) + spot-check banner for regressions + confirm NIT 6 (HomeScreen.test.tsx) closed.
**Verdict:** **PASS**

---

## NIT 4 — accessibilityLabel includes step context — CLOSED

**Location:** `apps/mobile/src/components/ResumeBanner.tsx:31-33, 67`

```ts
const a11yLabel = hasStepCount
  ? `Resume ${record.projectName}, step ${stepNumber} of ${record.totalSteps}`
  : `Resume ${record.projectName}`;
// ...
accessibilityLabel={a11yLabel}
```

- Shape matches my NIT 4 suggested wording verbatim: `"Resume {name}, step N of M"`.
- `stepNumber` extracted as a shared local so the visible "Step 3 of 7" subtitle and the a11y label share the same `Math.min(currentStepIndex + 1, totalSteps)` clamp. Clean refactor — visible/spoken stay in sync if the clamp ever fires.
- Inline comment names me (`Vera NIT 4`) and explains the rationale (re-focus announcement outside the live-region subtitle). Good prevention.

**Fallback when `totalSteps` is 0/undefined:** Confirmed in code (`hasStepCount = record.totalSteps > 0`) and locked by test:

- `ResumeBanner.test.tsx:72-86` — `totalSteps: 0` → step label is `"Resume"` AND a11y label degrades to `"Resume IKEA Bookshelf Assembly"` (no trailing comma, no "step 0 of 0" leak).
- `ResumeBanner.test.tsx:88-98` — positive case asserts exact string `"Resume IKEA Bookshelf Assembly, step 3 of 7"`.

Both fallback paths are pinned by assertions. NIT 4 closed cleanly.

---

## Regression spot-check — banner UI

Diffed `cf682a7..a208284` on `ResumeBanner.tsx` — change is 11 insertions / 2 deletions, scoped entirely to a11y label wiring plus the `stepNumber` extraction.

| Surface | Status |
|---|---|
| Colors / tokens | UNCHANGED — no `styles` block touched |
| Layout (flex, gap, padding, margin) | UNCHANGED |
| Visible copy (title, subtitle, CTA text) | UNCHANGED |
| `testID`s | UNCHANGED |
| `accessibilityLiveRegion`, `accessibilityRole` | UNCHANGED |
| Touch target (`minHeight: touch.minTarget`) | UNCHANGED |
| Disabled state behavior (spinner replaces text) | UNCHANGED |

No visual regression. No new hex literals. WCAG contrast table from the prior report carries forward — none of the inputs changed.

---

## NIT 6 — HomeScreen.test.tsx — CLOSED

File `apps/mobile/src/__tests__/HomeScreen.test.tsx` now exists (NEW, 153 lines, 4 wiring tests). I called this out in my prior report as "more Jasmin's lane than mine" — flagging it here as closed so the audit trail is complete. Jasmin will validate test design/coverage on her side.

Quick read: the four wiring cases cover (a) banner mounts on fresh cache, (b) banner absent on empty cache, (c) focus-effect reads cache, (d) 404 prune removes banner + clears cache + does NOT navigate. The 404 self-heal assertion is the one I most cared about from an a11y/UX standpoint — the banner disappearing after a failed Resume means the screen-reader user isn't left with a phantom CTA. Good.

---

## NIT status table (cumulative)

| # | NIT | Severity | Status after P1 |
|---|---|---|---|
| 1 | Disabled-state CTA contrast (spinner replaces text, not a real fail) | Cosmetic | OPEN — deferred (per Yoni's report) |
| 2 | Raw literal `width: 32` in `iconCol` | Token discipline | OPEN — deferred |
| 3 | Raw literal `gap: 2` in `textCol` | Token discipline | OPEN — deferred |
| 4 | accessibilityLabel omits step context | a11y polish | **CLOSED** |
| 5 | `primaryDark` ratio cited against wrong bg in `colors.ts` comment | Documentation | OPEN — deferred |
| 6 | No HomeScreen integration test for banner render-paths | Coverage | **CLOSED** (test file added) |

2 closed (the two I asked Yoni to close), 4 still open and deferred per scope of P1. All 4 remaining are non-blocking cosmetic/doc items — they can ride in a future polish pass or be permanently accepted. None warrant a HOLD.

---

## Findings — Infrastructure

None. Test-only additions + one component-level label tweak. No deps, no build config, no theme tokens added.

---

## Findings — Design

None new. The single design decision in this round (a11y label wording with comma separator vs. "at step") is sound — comma reads better in VoiceOver prosody than "at step," and matches the visible "Step N of M" idiom in the subtitle. Yoni documented this in his report; I agree with the call.

---

## Verdict

**PASS.** NIT 4 closed cleanly with the exact wording I asked for, fallback path is pinned by a dedicated test, and the supporting refactor (shared `stepNumber`) is a quality-positive change. NIT 6 also closed via the new `HomeScreen.test.tsx`. No regression in the banner. Jasmin clear to re-verify DESIGN-1/2/3.

— Vera
