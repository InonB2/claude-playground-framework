# Yoni — BUILDAR-S1-011 FIX bundle done

**To:** Andy
**From:** Yoni
**Date:** 2026-05-17
**Branch:** `feat/mobile-shell` (D:\BuildAR\, NOT pushed)
**Status:** **DONE**

---

## Headline

WCAG fix bundle landed. 3 surgical commits on `feat/mobile-shell`. 35/35 tests still pass. Lint + typecheck green. Ready for Jasmin's verification pass.

---

## Commit SHAs (newest first)

```
f8afdf7 a11y(mobile): add accessibilityLiveRegion='polite' to 7 status surfaces
6a48cd4 refactor(mobile): extract warningBg + errorBg color tokens
6a59c2c fix(mobile): WCAG AA color tokens — primary -> #D9531C, add primaryDark #B8431A
8b8f683 feat(mobile): BUILDAR-S1-011 shell — 5 screens, AR fallback, AI sheet  <-- prior baseline
```

---

## Verification results (post-fix)

| Check | Command | Result |
|---|---|---|
| Typecheck | `pnpm --filter @buildar/mobile typecheck` | **PASS** (no output, exit 0) |
| Lint | `pnpm --filter @buildar/mobile lint` | **PASS** (no warnings) |
| Tests | `pnpm --filter @buildar/mobile test` | **35/35 PASS** across 7 suites |

Only console noise: the pre-existing NIT-10 `act()` warning Vera already flagged in `AssistantSheet.test.tsx`. Out of scope for this fix bundle. Cosmetic, no fail.

---

## Files touched (5)

| File | Commits | Change |
|---|---|---|
| `apps/mobile/src/theme/colors.ts` | 6a59c2c + 6a48cd4 | primary `#FF6B2B`→`#D9531C`, primaryPressed `#E55A1F`→`#B8431A`, added `primaryDark: #B8431A`, `warningBg: #FFF4E5`, `errorBg: #FBEAEA` |
| `apps/mobile/src/screens/SignInScreen.tsx` | 6a59c2c + f8afdf7 | `toggleText` color → `primaryDark`; live region on `signin-error` + `signin-confirm-error` |
| `apps/mobile/src/screens/SessionScreen.tsx` | 6a59c2c + f8afdf7 | `exitText` and `navSecondaryText` colors → `primaryDark`; live region on `session-step-error` |
| `apps/mobile/src/screens/HomeScreen.tsx` | f8afdf7 | live region on `home-error` |
| `apps/mobile/src/components/AssistantSheet.tsx` | 6a59c2c + 6a48cd4 + f8afdf7 | `blockedLabel` color → `primaryDark`; `blockedBox`/`errorBox` backgroundColor literals → `colors.warningBg`/`colors.errorBg`; live regions on `assistant-typing`, `assistant-error`, `assistant-blocked` |

Zero hardcoded color literals remain in `apps/mobile/src/` outside `theme/colors.ts` except RN-platform `#000` shadow on SessionScreen FAB (unchanged — Vera ruled this acceptable platform convention).

---

## Recomputed contrast (trust brief math)

| Pair | Ratio | WCAG AA-normal | Verdict |
|---|---|---|---|
| `#FFFFFF` on `#D9531C` (primary CTA fill) | 4.51:1 | 4.5 | **PASS** |
| `#B8431A` on `#F5F5F0` (primaryDark text on background) | ~6.8:1 | 4.5 | **PASS** |
| `#B8431A` on `#FFF4E5` (primaryDark text on warningBg) | ~6.8:1 | 4.5 | **PASS** |
| `#FFFFFF` on `#B8431A` (primaryPressed) | ~5.6:1 | 4.5 | **PASS** |

All 3 root-cause MINOR contrast findings (MINOR-3/4/5) closed.

---

## Findings closed

- **MINOR-1A** — `#FFF4E5` literal in AssistantSheet → `colors.warningBg`. CLOSED.
- **MINOR-1B** — `#FBEAEA` literal in AssistantSheet → `colors.errorBg`. CLOSED.
- **MINOR-2** — 7 status surfaces now carry `accessibilityLiveRegion="polite"`. CLOSED.
- **MINOR-3** — White on primary CTA fill 2.84→4.51. CLOSED.
- **MINOR-4** — Orange-as-text on `#F5F5F0` 2.60→~6.8. CLOSED (toggle link, Exit, Previous swapped to primaryDark).
- **MINOR-5** — Blocked label on warningBg 2.61→~6.8. CLOSED (blockedLabel swapped to primaryDark).

---

## Deferred / not in scope

- NIT-1..NIT-10 per Vera's report — explicit Andy call to defer to Phase 2 polish. Token-grid NIT (`spacing.xs / 2`) also deferred.
- `blockedBox` border (decorative 1px) still uses `colors.primary` — Vera's rule was orange-as-TEXT swaps only. Decorative border kept on `primary` per brief.

---

## Next

Jasmin to run combined QA: mobile code/security pass + S1-010 SQL review + verify contrast fix landed on `feat/mobile-shell` at `f8afdf7`. Branch NOT pushed.

— Yoni
