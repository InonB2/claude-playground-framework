# Vera — BUILDAR-S1-012 UI/a11y QA Report

**From:** Vera
**To:** Andy
**Date:** 2026-05-18
**Task:** BUILDAR-S1-012 — HomeScreen resume-active-session banner
**Branch:** `feat/mobile-shell` @ `cf682a7`
**Worker:** Yoni
**Verdict:** **PASS WITH NOTES**

---

## Verdict summary

The banner ships clean. All hard WCAG AA gates pass on user-facing text. No new hardcoded hex literals introduced. Touch target meets iOS HIG. Live-region + button role + label all wired. Six NITs noted below — none are blockers; none warrant a HOLD.

Recommend Andy proceeds to Jasmin for logic/coverage QA.

---

## Independent WCAG contrast recompute

Computed with sRGB linearization + WCAG luminance formula (not the simplified "perceived brightness"):

```
L_channel = c/12.92                 if c <= 0.03928
L_channel = ((c+0.055)/1.055)^2.4   otherwise
L = 0.2126*Lr + 0.7152*Lg + 0.0722*Lb
ratio = (L_lighter + 0.05) / (L_darker + 0.05)
```

| Pair                                  | fg       | bg       | Ratio     | Target          | Result |
|---------------------------------------|----------|----------|-----------|-----------------|--------|
| CTA "Resume" white on `primary`       | `#FFFFFF`| `#C0461A`| **5.08:1**| 4.5:1 normal    | PASS   |
| CTA white on `primaryPressed`         | `#FFFFFF`| `#A03A14`| **6.75:1**| 4.5:1 normal    | PASS   |
| Title `text` on `surface`             | `#1A1A1A`| `#FFFFFF`| **17.40:1**| 4.5:1 normal   | PASS   |
| Subtitle `primaryDark` on `surface`   | `#B8431A`| `#FFFFFF`| **5.45:1**| 4.5:1 normal    | PASS   |
| Inline `error` on `surface`           | `#C62828`| `#FFFFFF`| **5.62:1**| 4.5:1 normal    | PASS   |
| Icon `primaryDark` on `surface`       | `#B8431A`| `#FFFFFF`| **5.45:1**| 3:1 graphical   | PASS   |
| CTA white on `disabled` (loading state)| `#FFFFFF`| `#B5B5B0`| **2.06:1**| 4.5:1 normal   | See NIT 1 |

**Discrepancy with Yoni's report:** Yoni cited `primaryDark` (`#B8431A`) as "6.8:1" — that figure is correct on `colors.background` (`#F5F5F0`) but the banner sits on `colors.surface` (`#FFFFFF`), where the actual ratio is **5.45:1**. Still PASS AA-normal. No remediation needed but the report's number is misattributed; flagging for accuracy.

---

## Success criteria — verification

### UI / visual (6 items)

| # | Criterion                                | Result | Note |
|---|------------------------------------------|--------|------|
| 1 | Banner conditional render                | PASS   | `HomeScreen.tsx:143-151`: `banner = resumeRecord != null ? <ResumeBanner …/> : null`. Renders nothing when null (no empty placeholder). 7-day stale guard in `activeSessionCache.ts:75-79` clears + returns null. Completion path clears (per Yoni); 404 prune wired in `HomeScreen.tsx:86-89`. |
| 2 | WCAG AA contrast                         | PASS   | All user-facing text pairs ≥4.5:1. See table above. |
| 3 | No new hardcoded hex                     | PASS   | `grep -nE "#[0-9A-Fa-f]{3,6}"` against all three new/modified files: zero matches. Every color routes through `colors.*`. |
| 4 | 8-pt spacing grid                        | PASS WITH NOTES | All paddings/margins/gaps use `spacing.sm` (16). See NITs 2 & 3 for two raw-literal exceptions. |
| 5 | Touch target ≥44pt                       | PASS   | CTA `minHeight: touch.minTarget` (44). Horizontal padding `spacing.md` (24×2 = 48 + 6-char "Resume" label at 17pt ≈ ~60pt total width). Comfortably above iOS HIG. |
| 6 | No layout regression on HomeScreen       | PASS   | Banner wired three ways: (a) skeleton/loading — banner deliberately absent (correct, no resume state to read yet); (b) empty state — banner renders above empty container via `{banner}` (HomeScreen.tsx:156); (c) list — passed as `ListHeaderComponent` (HomeScreen.tsx:174), pushes list down cleanly. Error state shows full-page error and intentionally suppresses banner (correct — don't offer resume when project list is broken). |

### Accessibility (4 items)

| # | Criterion                                | Result | Note |
|---|------------------------------------------|--------|------|
| 7 | `accessibilityRole="button"` + label     | PASS WITH NOTES | Role present (`ResumeBanner.tsx:59`). Label = `Resume ${projectName}`. Brief suggested "Resume Project X at step N of M" — step is omitted. See NIT 4. |
| 8 | `accessibilityLiveRegion="polite"`       | PASS   | Set on banner root view (`ResumeBanner.tsx:32`). Will announce on appearance after focus regain. Matches S1-011 pattern. |
| 9 | Focus order                              | PASS   | Banner is `ListHeaderComponent` — appears first in screen-reader traversal. Correct primary-action ordering. |
| 10| Dark mode contrast                       | N/A    | `theme/colors.ts` only ships light tokens. Per brief, skip — Phase 3 work. |

---

## Findings — Infrastructure

None. No build, lint, or dependency issues introduced by this change. Cache abstraction is sound and AsyncStorage-swap path is clean.

---

## Findings — Design

### NIT 1 — Disabled-state CTA contrast (cosmetic, not a WCAG fail)
- **What:** White text on `colors.disabled` (`#B5B5B0`) computes to **2.06:1**, well below the 4.5:1 normal-text bar.
- **Why it's not a blocker:** When `resuming=true`, the CTA replaces the "Resume" text with an `ActivityIndicator` spinner (`ResumeBanner.tsx:62-66`). No text is shown during the disabled state, so there is no user-facing text-contrast failure. WCAG 2.1 1.4.3 also exempts "inactive UI components" from the contrast requirement.
- **Recommendation:** Keep as-is. If a future state ever shows the "Resume" label simultaneously with `disabled=true` (e.g. a different disabled reason), this becomes a real fail — flag for future regression.
- **Prevention:** Add a comment near `ctaDisabled` in `ResumeBanner.tsx` noting the spinner replaces the label so contrast guard isn't needed; will prevent future devs from re-introducing the label in the disabled state.

### NIT 2 — Raw literal `width: 32` in `iconCol`
- **Location:** `ResumeBanner.tsx:86` — `iconCol: { width: 32, ... }`.
- **Why it matters:** 32 is on the 8-pt grid (and equals `spacing.lg`), so visually fine — but the project's token discipline says "every dimension references a token." This is a raw number.
- **Fix:** Replace with `spacing.lg`. One-line change. Not blocking.

### NIT 3 — Raw literal `gap: 2` in `textCol`
- **Location:** `ResumeBanner.tsx:92` — `textCol: { flex: 1, gap: 2 }`.
- **Why it matters:** 2pt is finer than the existing `spacing.xs / 2` precedent (4pt, used in 3 places in S1-011). It's a deliberate tight line-pair gap for the project-name / step-label stack, but it's the first sub-4pt token-free value in the codebase.
- **Fix:** Either (a) accept and document as the new tightest tier, or (b) bump to `spacing.xs / 2` (4pt). Visually acceptable either way. Not blocking.
- **Prevention:** Consider adding a `spacing.hairline = 2` token if more sub-4pt gaps emerge; otherwise the 8-pt grid contract starts to drift.

### NIT 4 — `accessibilityLabel` omits step context
- **Location:** `ResumeBanner.tsx:60` — `accessibilityLabel={`Resume ${record.projectName}`}`.
- **Brief asked for:** "Resume Project X at step N of M" or similar.
- **Why it matters:** Screen-reader users hear "Resume IKEA Bookshelf Assembly" but lose the "Step 3 of 7" context that sighted users see in the subtitle. The subtitle text is in the live region, so it WILL be announced when the banner appears — but the button's own label won't re-announce step on re-focus.
- **Fix:** `accessibilityLabel={hasStepCount ? `Resume ${record.projectName}, step ${record.currentStepIndex + 1} of ${record.totalSteps}` : `Resume ${record.projectName}`}`. Two-line change.
- **Prevention:** Cross-reference brief a11y phrasing in PR template.

### NIT 5 — Yoni's contrast number for `primaryDark` cites wrong background
- **What:** Yoni's report says `primaryDark` subtitle = "6.8:1 on light bg," but the banner background is `colors.surface` (`#FFFFFF`), not `colors.background` (`#F5F5F0`). Actual ratio on white = **5.45:1**.
- **Why it matters:** Still PASS AA — no remediation. But the team's contrast bookkeeping should be background-specific to avoid a future "looked fine on background, fails on surface" miss.
- **Fix:** Update `colors.ts` comment to reflect surface-specific ratio:
  ```
  // primaryDark: 5.45:1 on #FFFFFF (surface); 6.8:1 on #F5F5F0 (background). Both PASS AA-normal.
  ```
- **Prevention:** Future contrast comments in `colors.ts` should always name the specific background hex.

### NIT 6 — No HomeScreen integration test for banner render-paths
- **What:** `__tests__/HomeScreen.test.tsx` does not exist. The 11 new tests cover `ResumeBanner` in isolation and `activeSessionCache` directly, but no test exercises the wiring (banner-present + list, banner-present + empty, banner-absent + list, banner-absent + error).
- **Why it matters:** Layout regression test would catch the case where banner accidentally renders inside the error state, or fails to push the FlatList correctly. Currently I verified by reading the code; an integration test would lock it in.
- **Severity:** This is more Jasmin's lane than mine — flagging it here so she sees it on intake.
- **Prevention:** Add a smoke `HomeScreen` test covering the 4 banner+state combinations.

---

## What I checked but found no issue with

- All three new/modified files: zero hex literals.
- `theme/colors.ts` token set: unchanged from S1-011 — no new tokens added (good — Yoni reused existing).
- Touch target: 44pt minHeight + 24pt horizontal padding × 2 = comfortable.
- Live-region pattern: matches S1-011 error banner pattern Yoni already shipped.
- Focus order: banner first via `ListHeaderComponent` — correct primary-action priority.
- `useFocusEffect` cleanup with `active` flag — prevents setState-on-unmounted regression (good defensive pattern).
- 404 cache-prune on Resume failure: solid UX — banner self-heals when project is deleted server-side.

---

## Verdict

**PASS WITH NOTES.** Ship it. 6 NITs — none blocking. Jasmin clear to proceed with logic/coverage QA.

— Vera
