# Vera — BuildAR Pro S1-012 UI/a11y QA (HomeScreen resume banner)

**From:** Andy
**Dispatched:** 2026-05-18
**Worker:** Yoni
**Worker's report:** `D:\Claude Playground\agents\andy\inbox\yoni_s1_012_done.md`
**Branch:** `feat/mobile-shell` @ `cf682a7` (NOT pushed)
**Repo:** `D:\BuildAR\` — you are the ONLY agent in this repo right now; Yoni is done

---

## Context

Yoni added a "Resume your last project" banner on HomeScreen. Reads from a pluggable `ActiveSessionBackend` (in-memory default, AsyncStorage-ready). Banner shows project name + "Step N of M" + Resume CTA when there's a fresh (<7 days old) non-completed session cached.

You did the original S1-011 QA — you caught the WCAG fail and the math error. This is an additive extension on the same branch. Theme tokens you already validated: `primary` `#C0461A` (5.08:1 white-on), `primaryDark` `#B8431A` (6.75:1 on light bg), `warningBg` `#FFF4E5`, `errorBg` `#FBEAEA`.

---

## Success criteria — verify Yoni's 8

Split findings Infrastructure vs Design per CLAUDE.md Rubric.

### UI / visual
1. **Banner conditional render.** Confirm:
   - No cache → banner absent (no empty placeholder)
   - Fresh cache → banner visible with project name + "Step N of M" + Resume CTA
   - Cache >7 days old → banner absent
   - Cache cleared on completion → banner absent next render
2. **WCAG AA contrast.** Independently recompute any contrast pairs Yoni's banner introduces:
   - Banner background color
   - Banner text on banner background
   - Resume CTA fill + label
   - "Step N of M" text on banner bg
   Use the sRGB linearization + WCAG luminance formula (not the simplified "perceived brightness"). Target: ≥4.5:1 for normal text, ≥3:1 for large text. Show your work in the report.
3. **No new hardcoded hex.** `grep -nE "#[0-9A-Fa-f]{3,6}"` the new/modified files. Every color must reference `colors.*` from the theme. If you find any literal hex outside `theme/colors.ts`, that's a finding.
4. **8-pt spacing grid.** Spot-check banner padding/margins against the existing tokens. Note any new `spacing.xs / 2` divisions (Yoni's S1-011 had 3 acceptable cases).
5. **Touch target ≥44pt.** Resume CTA hit area meets iOS HIG minimum.
6. **No layout regression elsewhere on HomeScreen.** Project list, empty state, error state all still render correctly when banner is absent AND when present (banner pushes content down).

### Accessibility
7. **`accessibilityRole="button"`** on Resume CTA. `accessibilityLabel` describes the action ("Resume Project X at step N of M" or similar).
8. **`accessibilityLiveRegion="polite"`** on the banner so screen readers announce it when it appears after a refresh (consistent with S1-011 a11y pattern Yoni already shipped).
9. **Focus order.** Banner should appear FIRST in screen-reader traversal (before the project list heading) since it's a primary action. Not strict — note as NIT if reversed.
10. **Contrast in dark mode (if dark mode tokens exist).** If `theme/colors.ts` only has light tokens (per S1-011), skip — note as Phase 3 work.

---

## Verdict format

End with `PASS` / `PASS WITH NOTES` / `HOLD`.

Reporting destination: `D:\Claude Playground\agents\andy\inbox\vera_s1_012_qa.md`

---

## Hard rules

- Do NOT modify any code. You're a tester.
- Do NOT modify `tasks/active_tasks.json` — Andy handles that.
- Do NOT push to GitHub.
- After you: Jasmin runs logic/coverage QA. You're sequential — your report needs to land before she starts.

---

## Token discipline

Target ≤150 tool uses. Focus reads:
- `apps/mobile/src/screens/HomeScreen.tsx`
- The new banner component (find via Yoni's report — likely `apps/mobile/src/components/ResumeBanner.tsx` or inline in HomeScreen)
- `apps/mobile/src/theme/colors.ts`
- `apps/mobile/src/__tests__/HomeScreen.test.tsx`
- Yoni's report itself

— Andy
