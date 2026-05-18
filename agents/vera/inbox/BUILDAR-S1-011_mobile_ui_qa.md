# Vera — BuildAR Pro Mobile Shell UI/UX/a11y QA

**From:** Andy
**Dispatched:** 2026-05-17
**Task to QA:** BUILDAR-S1-011 (Yoni — mobile shell)

**Inputs:**
- Yoni's done-report: `D:\Claude Playground\agents\andy\inbox\yoni_s1_011_done.md`
- Lena's UX brief (source of truth): `D:\Claude Playground\owner_inbox\design\buildar_mobile_ux_brief.md`
- Mobile shell code: `D:\BuildAR\apps\mobile\` on branch `feat/mobile-shell` (commit `8b8f683`)

---

## Why you, and what you can/can't do

You normally QA web UIs against a live browser. This is a React Native mobile shell on Windows with NO Android SDK installed — Yoni already documented that boot is blocked on this host. **You will NOT be able to render the app visually.** Your QA is therefore a code-level + brief-conformance review, not a screenshot review.

What that means in practice:
- Read each screen file end-to-end and verify it matches Lena's brief component-by-component
- Verify accessibility primitives in code (touchable hit areas, accessibility labels, semantic roles)
- Verify color/typography/spacing tokens are correctly applied
- Verify RTL safety (logical CSS properties — no `left`/`right`, only `start`/`end`)
- Confirm the test files exercise the spec'd behaviors

---

## Mobile QA scope

### A. Per-screen conformance to Lena's brief

For EACH of the 5 screens, walk Lena's brief section by section and verify the code matches. Files:
- `src/screens/SignInScreen.tsx` — vs Lena §Screen 1
- `src/screens/HomeScreen.tsx` — vs Lena §Screen 2
- `src/screens/ProjectDetailScreen.tsx` — vs Lena §Screen 3
- `src/screens/SessionScreen.tsx` — vs Lena §Screen 4 (the big one, most complex)
- `src/screens/CompletionScreen.tsx` — vs Lena §Screen 5

For each screen, your verdict should call out:
- Primary action implemented correctly? (Y/N + line cite)
- Key components present? (checklist per Lena's bullets)
- Loading state implemented? (skeleton/spinner per spec)
- Empty state implemented? (Lena specifies different patterns per screen)
- Error state implemented?
- Navigation paths correct?

### B. Design system token discipline

Verify:
- `src/theme/colors.ts` — `#FF6B2B` (primary), `#1A1A1A` (text), `#F5F5F0` (background) match Lena's tokens exactly. No off-brand colors introduced.
- `src/theme/typography.ts` — scale matches Lena (13/15/17/20/24/32). System font stack only — no custom font loading.
- `src/theme/spacing.ts` — all values are multiples of 8 (8/16/24/32/48/64).
- Grep `apps/mobile/src/` for hardcoded hex colors NOT in the theme — those are token violations.
- Grep `apps/mobile/src/` for hardcoded font sizes not from the typography scale — token violations.

### C. Accessibility (a11y) — code-level review

This is your specialty. Verify:
- **Touch targets ≥44pt:** every `Pressable`, `TouchableOpacity`, `TextInput`, icon button must have minHeight + minWidth ≥ 44. Yoni claimed to use `touch.minTarget` — confirm where defined and verify usage at every interactive site.
- **Accessibility labels:** every interactive element has `accessibilityLabel` and (where appropriate) `accessibilityRole`. Especially icon-only buttons (show/hide password eye, sheet close X, exit button) — they MUST have labels.
- **Semantic roles:** form inputs use `accessibilityRole="textbox"` or implicit textbox; buttons use `accessibilityRole="button"`; toggles use `accessibilityRole="switch"`.
- **State announcements:** loading states should announce ("Loading…" with `accessibilityLiveRegion="polite"` or equivalent); errors should be announced.
- **Focus order:** in SignInScreen — email → password → submit; in step navigation — Previous → Next.
- **AI bottom sheet:** when opened, focus should move to the text input. When dismissed, focus returns to the FAB. (This is RN-specific — check if Yoni implemented focus management or noted it as deferred.)

### D. Color contrast (Lena specified WCAG AA)

Yoni's report claims:
- Body text `#1A1A1A` on `#F5F5F0` = 16.4:1 (AAA ✓)
- Muted text `#6B6B6B` on `#F5F5F0` = 4.9:1 (AA for normal ✓)
- Orange button `#FF6B2B` with white text = 4.8:1 (AA-large only ✓)

Verify Yoni's claimed ratios by recomputing them yourself (you do this in every web QA — same math here). Flag any text/background combination that fails AA for its size class.

Special attention to:
- "AR unavailable" label on the dark AR-fallback rectangle (Screen 4) — if the fallback uses a near-black background, what's the label color contrast?
- Error message text in error states — usually red on light background; verify the red is dark enough for AA.
- "Delete?" / "Yes, delete" inline confirmation buttons — must be discoverable.

### E. RTL safety

Lena's brief: use logical CSS properties (inline-start/inline-end), not left/right, so RTL (Hebrew) requires only a stylesheet swap.

Grep `apps/mobile/src/` for:
- `left:` or `right:` in style objects — should be `start:` or `end:`
- `marginLeft` / `marginRight` / `paddingLeft` / `paddingRight` — should be `marginStart` / `marginEnd` / `paddingStart` / `paddingEnd`
- `textAlign: 'left'` / `'right'` — should be `'start'` / `'end'` (or omitted for default behavior)
- `flexDirection: 'row-reverse'` — usually a red flag; `'row'` auto-flips for RTL in RN

Yoni's report claims compliance; verify with grep.

### F. Component tests review

Read each `src/__tests__/*.tsx` file and verify the tests exercise spec'd behavior, not implementation details:
- `AssistantSheet.test.tsx` — must test: typing input, submit fires, blocked state renders `safety.reason`, loading shows typing indicator, error shows retry. Yoni claims 6 tests; verify each maps to a Lena/brief behavior.
- `ARView.test.tsx` — must test: fallback renders when ViroReact unavailable AND when `forceFallback` is set. Yoni claims 3 tests; verify both scenarios covered.
- `ProjectCard.test.tsx` — must test: title/category/difficulty/time render; tap fires navigation; not a generic "renders without crashing" smoke.
- `DifficultyIndicator.test.tsx`, `StepProgressIndicator.test.tsx` — verify the difficulty `1-5` value is rendered correctly (not as stars per brief).

### G. Cross-checks

- **No analytics SDK** (Lena's brief implies no Mixpanel/Amplitude in Phase 0–1) — grep for `analytics`, `mixpanel`, `amplitude`, `posthog`.
- **No social/OAuth login buttons** — grep `SignInScreen.tsx` for `signInWith` patterns other than `signInWithPassword`.
- **No "Sign up" hidden in SignInScreen** — Lena's brief allows a toggle to sign-up mode. Verify it's present OR documented as deferred. (Yoni's brief said email/password only — clarify whether sign-up toggle was implemented.)
- **No marketing copy** — grep for marketing/landing-page patterns.

---

## Constraints

- **Repo:** `D:\BuildAR\` on branch `feat/mobile-shell`. NOT pushed.
- **You are the ONLY agent in `D:\BuildAR\` right now.** Silas just finished. Don't spawn helpers.
- You CANNOT boot the app (no Android SDK). All QA is code-level. Document this scope in your report.
- **Token discipline:** keep tool uses ≤300. This is a thorough code review, not exploration.

---

## Definition of done

1. Per-screen verdict table (5 rows) with PASS / PASS WITH NOTES / FAIL + line cites for issues.
2. Token discipline grep summary.
3. Accessibility findings with severity (BLOCKER / MAJOR / MINOR / NIT).
4. Color contrast verification (independent recompute or accept Yoni's claims with sample re-checks).
5. RTL grep summary — must report ZERO bare `left:` / `right:` / `marginLeft` / `marginRight` if Lena's spec is being honored, OR a flagged list with severity.
6. Component test review (per-test-file commentary).
7. Headline: **Wave 2 GREEN for merge** or **HOLD — needs <minor list>** — with specifics.

**Report destination:** `D:\Claude Playground\agents\andy\inbox\vera_s1_011_qa.md`

**When done, Telegram:**
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-011 UI QA" "<verdict + counts: e.g. 'PASS WITH NOTES: 0 blocker, 0 major, X minor, Y nit; merge GREEN'>"
```

The user (Inon) is away today. You report to Andy. Jasmin will do the security/integration QA after you — sequential.

— Andy
