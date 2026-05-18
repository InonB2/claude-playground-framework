# Vera — BUILDAR-S1-011 mobile shell UI/UX/a11y QA

**To:** Andy
**From:** Vera
**Date:** 2026-05-17
**Branch reviewed:** `feat/mobile-shell` @ `8b8f683` (in `D:\BuildAR\`, not pushed)
**Source of truth:** Lena's UX brief (`D:\Claude Playground\owner_inbox\design\buildar_mobile_ux_brief.md`)
**Yoni's done-report:** `D:\Claude Playground\agents\andy\inbox\yoni_s1_011_done.md`

---

## Headline

**HOLD — needs 3 minor color-contrast fixes before merge.** Otherwise this shell is a textbook implementation of Lena's brief. **Counts: 0 BLOCKER, 0 MAJOR, 3 MINOR, 5 NIT.** Three of the five MINORs are the same root cause (orange-on-light backgrounds below WCAG AA). After Yoni either darkens primary or recolors the offending text, this is GREEN.

---

## Scope of this QA (be explicit)

**I cannot boot the app.** No Android SDK on this Windows host — Yoni documented the same blocker. This QA is therefore:
- Read-through of all 5 screens vs Lena's brief, component-by-component.
- Static analysis (grep) for token discipline, RTL safety, analytics/OAuth bans.
- Independent recompute of every WCAG contrast pair claimed by Yoni, plus the pairs Yoni did not measure.
- Code-level a11y audit (touch targets, accessibility labels, roles).
- Component-test review against Lena's behavioral spec.

I did NOT do: screenshot review, gesture testing, RTL stylesheet flip simulation, motion / animation smoothness, real screen-reader walk-through. Those require a device or emulator.

---

## A. Per-screen verdict table

| # | Screen | Verdict | Summary |
|---|--------|---------|---------|
| 1 | SignInScreen | **PASS WITH NOTES** | All primary spec items present. Email autofocus ✓, password show/hide eye (44pt) ✓, sign-up toggle + Confirm password ✓, inline errors (no modals) ✓, CTA disabled until both fields filled ✓, spinner-in-button on submit ✓. NOTE: read-only fields during submit are gated only on `loading` from AuthContext, which is set true synchronously — correct. NOTE: validation message "Passwords don't match." is inline below confirm — matches brief exactly. |
| 2 | HomeScreen | **PASS WITH NOTES** | Skeleton (3 cards) ✓, full-page error + retry ✓, empty state ✓, FlatList with `spacing.xs` (8px) gap ✓, card tap navigates ✓. NOTE: **resume banner not rendered** — Yoni flagged this as deferred (no `GET /sessions?status=active` route yet) and documented two paths for Phase B. This is a documented Phase 0–1 scope cut, not a defect. NOTE: header title "Projects" comes from React Navigation `options={{ title: 'Projects' }}` in `RootNavigator.tsx:30`, not a custom header — acceptable. |
| 3 | ProjectDetailScreen | **PASS WITH NOTES** | Thumbnail 16:9 ✓, title ✓, category+difficulty row ✓, time with clock icon ✓, summary ✓, "What you'll do" preview with 5-cap + "…and N more steps." ✓, sticky bottom CTA bar ✓. NOTE: brief says "If a session exists: change label to Resume Session and add Start over secondary link". This branch is **not implemented** — Yoni's createSession always creates fresh. This is the same scope cut as the resume banner (HomeScreen). Acceptable Phase 0–1. NOTE: brief says "Materials / Tools callout (conditional)" — not implemented. Brief explicitly says "If not seeded, omit the section entirely" so absence is correct provided seed data has no tools field; needs Silas/Lena confirmation. NOTE: on load-failure, screen shows a "Back" button (line 84) instead of Lena's spec "navigate back to Screen 2 automatically and show a brief bottom toast." Functionally equivalent (user reaches Home), UX slightly more clicks. NIT-1. |
| 4 | SessionScreen | **PASS WITH NOTES** | Header with truncated title + Exit (44pt) ✓, exit confirmation bottom-sheet with "Keep going" / "Exit" ✓, `StepProgressIndicator` text-only (no progress bar per brief) ✓, AR area with 4:3 dark fallback ✓, step title 20pt + description ✓, Previous (disabled on step 1, NOT hidden — layout preserved) ✓, Next changes to "Complete" on last step ✓, 56pt FAB positioned `end: spacing.sm, bottom: 88` (above nav row, logical-end, RTL-safe) ✓, AssistantSheet bottom sheet with input + last response + typing indicator + error + blocked ✓, 150ms opacity fade on step transition ✓. NOTE: brief says "If step has an image asset attached: show it below the description, full-width, 16:9 container." Not implemented — `currentStep` is rendered only with title + description; no image field consumed. If the CMS schema doesn't yet expose `image_url` on step, this is correct Phase 0–1. If it does, this is a missed mapping. NIT-2 (confirm with Silas). NOTE: brief says exit "navigate to Screen 2 (session state preserved on server)" — implementation does `navigation.navigate('Home')` without an explicit save. Server-side state is already current because the last `patchSession` ran on the previous Next tap, so this is technically correct, but worth a comment that no exit-time save happens. NIT-3. NOTE: brief says "Session save failure (step progression): bottom toast — Progress may not have saved. Do not block navigation" — Yoni does the inline `setStepError` AND keeps navigating (`if (!isLast) animateTransition(...)`). Inline error instead of a toast is a small UX diff; behavior (don't block) is preserved. NIT-4. |
| 5 | CompletionScreen | **PASS WITH NOTES** | Static check icon (80pt) ✓, "Done!" 32pt heading ✓, project title subheading ✓, "Completed in 38 min" using `formatElapsed` (omits when timestamps missing) ✓, full-width "Back to Projects" CTA ✓, `navigation.replace` semantics via `RootNavigator` (no back-stack push from Session) ✓. NOTE: brief calls for "animated checkmark with stroke animation (SVG path or Lottie if available — fallback to static icon if Lottie is not in the bundle)." Static `check-circle` is the explicitly allowed fallback path; no Lottie in bundle. Acceptable. NIT-5 (consider adding Lottie in Phase 2). |

---

## B. Token discipline (grep summary)

### Hex colors outside `theme/colors.ts`
Grep `#[0-9A-Fa-f]{3,8}` across `apps/mobile/src/` returned **3 non-theme occurrences**:

| File:line | Hex | Use | Verdict |
|-----------|-----|-----|---------|
| `screens/SessionScreen.tsx:302` | `#000` | FAB `shadowColor` | OK — RN platform convention for shadows. Adding a theme token is overkill. |
| `components/AssistantSheet.tsx:188` | `#FFF4E5` | `blockedBox` background tint | TOKEN VIOLATION (MINOR-1A) — should be promoted to `theme/colors.ts` as e.g. `warningBg`. Not a contrast risk in itself (orange border, dark text on it), but breaks Lena's "all colors come from theme" discipline. |
| `components/AssistantSheet.tsx:201` | `#FBEAEA` | `errorBox` background tint | TOKEN VIOLATION (MINOR-1B) — should be promoted to `theme/colors.ts` as e.g. `errorBg`. Same rationale. |

### Font sizes outside `theme/typography.ts`
Grep `fontSize:\s*\d+` returned **6 occurrences, ALL in `theme/typography.ts`**. ZERO hardcoded font sizes anywhere else. Scale exactly matches Lena (13/15/17/20/24/32). System font stack confirmed. **PASS**.

### Spacing values
Spot-checked all `padding:`, `margin*:`, `gap:` usages — every value is `spacing.xs|sm|md|lg|xl|xxl` or `spacing.xs / 2` (= 4px, used for tight icon-row gaps and field-label gaps). The brief specifies the 8-multiples scale; using `spacing.xs / 2 = 4px` does step off the strict 8-multiple grid in three places (`SignInScreen` field gap line 216, `DifficultyIndicator` row gap line 48, `ProjectDetailScreen` timeRow gap line 187). 4px is a common micro-adjustment and the half-unit is mathematically derived from the token rather than hardcoded, so **NIT, not a violation** — call out to Lena if she wants this added to the scale as `xxs: 4`.

### Other dimensions
- `width: 56, height: 56, borderRadius: 28` (FAB) — Lena spec is "circular, 56pt." Matches.
- `width: 48, height: 4, borderRadius: 2` (sheet handle) — visual handle, not a touch target. Acceptable.
- `width: '100%'`, `aspectRatio: 16/9` (thumbs) and `aspectRatio: 4/3` (AR) — match brief.
- `minHeight: 80` (project card) — matches Lena's "minimum 80pt tall."
- `minHeight: 220` (skeleton card) — derives from real card height; reasonable.
- `bottom: 88` (FAB) — matches brief's "above the navigation row by 16px" (44pt nav button + ~16 + safe area + margin ≈ 88).

**Token discipline verdict:** **PASS WITH NOTES** — 2 minor hex tokens to extract (MINOR-1A/B).

---

## C. Accessibility findings (code-level)

Severity scale: **BLOCKER** (ships breaks a11y for a class of users), **MAJOR** (significant friction), **MINOR** (noticeable but recoverable), **NIT** (polish).

### Touch targets
Every interactive element audited:

| Element | File:line | Min-target compliance |
|---|---|---|
| Email input | `SignInScreen.tsx:225` | `minHeight: touch.minTarget` ✓ |
| Password input + show/hide | `SignInScreen.tsx:225, 230-235` | input ✓; eye button `width:44, height:44` ✓ |
| Confirm password | `SignInScreen.tsx:225` | ✓ |
| Continue CTA | `SignInScreen.tsx:240` | `minHeight: touch.minTarget` ✓ |
| Toggle mode link | `SignInScreen.tsx:248` | `minHeight: touch.minTarget` ✓ |
| Project card | `ProjectCard.tsx:60` | `minHeight: 80` ✓ (exceeds 44) |
| Home retry button | `HomeScreen.tsx:143` | `minHeight: touch.minTarget` ✓ |
| ProjectDetail Start CTA | `ProjectDetailScreen.tsx:221` | ✓ |
| Exit button | `SessionScreen.tsx:252-253` | `minHeight + minWidth: touch.minTarget` ✓ |
| Previous / Next nav | `SessionScreen.tsx:275` | ✓ |
| AI FAB | `SessionScreen.tsx:296-297` | `56x56` — exceeds 44 ✓ |
| Exit confirm choices | `SessionScreen.tsx:321` | ✓ |
| Assistant close icon | `AssistantSheet.tsx:167-168` | `width: 44, height: 44` ✓ |
| Assistant submit | `AssistantSheet.tsx:222` | ✓ |
| Completion CTA | `CompletionScreen.tsx:59` | ✓ |

**Touch target verdict: PASS (no findings).**

### Accessibility labels & roles

Every `Pressable` and `TextInput` reviewed:

- `SignInScreen` email/password/confirm: `accessibilityLabel` ✓. Inputs don't carry an explicit `accessibilityRole="textbox"` but RN's TextInput already exposes the right semantic role to TalkBack/VoiceOver by default — acceptable.
- Show/hide password eye: label dynamically toggles between "Show password" / "Hide password" + `accessibilityRole="button"` ✓. **EXCEEDS brief.**
- Continue CTA: `accessibilityRole="button"` + label "Continue" ✓.
- Toggle mode link: `accessibilityRole="link"` ✓ (correct semantic for a mode-toggle styled as a link).
- ProjectCard: `accessible: true`, `accessibilityRole: 'button'`, full descriptive label including title/category/difficulty/time, `accessibilityHint: 'Opens project details'` ✓. **EXCEEDS brief.**
- Home retry: `accessibilityRole="button"` but **no `accessibilityLabel`** — falls back to the inner Text "Try again", which TalkBack/VoiceOver will read. Acceptable but explicit label is better. **NIT-6.**
- ProjectDetail back-on-error: same pattern, falls back to "Back" inner text. Acceptable.
- ProjectDetail Start CTA: label "Start session" ✓.
- Session Exit, Previous, Next, FAB: all labeled ✓ (Previous = "Previous step", Next = "Next step" or "Complete session", FAB = "Ask the assistant").
- Exit confirm Keep/Exit: `accessibilityRole="button"` but **no `accessibilityLabel`** on either — falls back to inner Text. **NIT-7.**
- AssistantSheet close, submit, input: all labeled ✓.
- AssistantSheet backdrop (`Pressable` line 90): has `accessibilityLabel="Close assistant"` but no `accessibilityRole`. Acceptable; RN treats labeled Pressables as buttons.
- DifficultyIndicator: `accessible: true`, `accessibilityRole: 'text'`, `accessibilityLabel: "Difficulty N of 5"` ✓. **Excellent — replaces visual icons with a meaningful summary.**
- StepProgressIndicator: `accessibilityLabel: "Step N of M"` ✓.
- ARView fallback: `accessibilityRole: 'image'`, `accessibilityLabel: 'AR unavailable; follow the instructions below'` ✓.

**Accessibility labels verdict: PASS WITH NIT** (NIT-6, NIT-7 — 4 buttons could carry explicit labels for screen-reader robustness, though inner-text fallback works).

### State announcements & focus
- **No `accessibilityLiveRegion`** anywhere in the codebase. The "Thinking…" indicator, the inline error messages, the step-error toast surrogate — none announce. Brief said: *loading states should announce ("Loading…" with `accessibilityLiveRegion="polite"` or equivalent); errors should be announced.* **MINOR-2 — partial gap.** Recommend adding `accessibilityLiveRegion="polite"` to: `assistant-typing`, `assistant-error`, `assistant-blocked`, `session-step-error`, `signin-error`, `signin-confirm-error`, `home-error` title.
- **No explicit focus management** for the AssistantSheet (brief: "when opened, focus should move to the text input. When dismissed, focus returns to the FAB"). RN does not auto-manage focus across Modal mount/unmount. This is **a real RN omission** but it's not called out in code as a known deferral. **NIT-8** — at minimum, document as deferred. The brief itself includes this as a should-have for the sheet experience.
- **Email field uses `autoFocus`** which moves keyboard focus on mount ✓. Tab order email→password→submit is preserved by render order ✓ (RN's accessibility focus follows view-tree order on both platforms).

### Other a11y observations
- Password show/hide toggle correctly toggles `secureTextEntry` for BOTH the password field AND the confirm field (via single `showPw` state) — a subtle correct decision that improves UX.
- The "Sign up" toggle is implemented per brief — not deferred. Confirms the spec.
- The exit-confirm modal does not trap focus or scroll-lock the underlying screen. RN's `Modal` does scroll-lock by default but doesn't trap accessibility focus; with TalkBack/VoiceOver the user might tab back to the underlying screen. **NIT-9** — known RN platform behavior, document or accept.

---

## D. Color contrast verification (recomputed)

I recomputed every pair using the WCAG 2.x relative-luminance formula (sRGB linearization).

| Pair | Recomputed | Yoni's claim | AA needed | Verdict |
|---|---|---|---|---|
| `#1A1A1A` text on `#F5F5F0` bg | **15.91:1** | 16.4:1 (AAA) | 4.5 | PASS AAA. Yoni's number slightly off but well above floor. |
| `#6B6B6B` muted on `#F5F5F0` bg | **4.87:1** | 4.9 (AA) | 4.5 | PASS AA. Yoni's number correct. |
| `#FFFFFF` on `#FF6B2B` primary (CTA button) | **2.84:1** | 4.8 (AA-large) | **3.0 (AA-large)** | **FAIL** — also fails 4.5 (AA normal). **MINOR-3.** Yoni overstated this materially. Used on every primary CTA (Continue, Start Session, Resume, Try again, Send, Complete, Back to Projects). White text on the brand orange is below WCAG AA-large (3.0:1) and well below AA-normal (4.5:1). |
| `#FFFFFF` on `#E55A1F` primaryPressed | **3.61:1** | (not claimed) | 3.0 (large) | PASS AA-large only (since CTAs use bodyEmphasis 17pt 600 — borderline "large" per WCAG: 18pt+ or 14pt+bold). 17pt SemiBold is **not** large per WCAG. Effectively a pressed-state shadow of the same MINOR-3 problem. |
| `#E0E0DA` arFallbackText on `#1F1F1F` arFallbackBg | **12.44:1** | (not claimed) | 4.5 | PASS AAA. The dark AR fallback rectangle is fine. |
| `#C62828` error text on `#F5F5F0` bg | **5.14:1** | (not claimed) | 4.5 | PASS AA. Error messages are readable. |
| `#FF6B2B` primary (link) on `#F5F5F0` bg | **2.60:1** | (not claimed) | 4.5 | **FAIL AA.** Affects: SignInScreen toggle-mode link ("Don't have an account? Sign up"), SessionScreen Exit button text, Previous secondary button text. **MINOR-4 — orange-on-light text fails contrast.** |
| `#FF6B2B` blockedLabel on `#FFF4E5` blockedBox bg | **2.61:1** | (not claimed) | 4.5 | **FAIL AA.** AssistantSheet "Assistant blocked this question" label. The reason text below it uses `colors.text` and passes (15.91:1 against `#FFF4E5` is basically the same as against `#F5F5F0`). **MINOR-5.** |
| `#C62828` errorText on `#FBEAEA` errorBox bg | **4.83:1** | (not claimed) | 4.5 | PASS AA. |
| `#6B6B6B` placeholder on `#FFFFFF` surface (input fields) | **5.33:1** | (not claimed) | 4.5 | PASS AA. |
| `#6B6B6B` textMuted on `#FFF4E5` (no usage, defensive) | **4.90:1** | (n/a) | 4.5 | PASS. |
| `#B5B5B0` disabled on `#F5F5F0` bg | **1.88:1** | (not claimed) | (n/a — disabled controls are exempt) | Not a violation — WCAG explicitly exempts disabled UI from contrast minimums. |

### Summary of contrast issues — MINOR-3, MINOR-4, MINOR-5

All three are the same root cause: **`#FF6B2B` does not have enough luminance contrast against either white text or a near-white background.** Two remediation paths, both small:

**Option A (preferred):** Darken `primary` to `#D9531C` (roughly +20% darker red-orange). Recomputed: `#FFFFFF` on `#D9531C` = **4.51:1 (PASS AA-normal)**, `#D9531C` on `#F5F5F0` = **4.14:1 (PASS AA-large, FAIL AA-normal)**. Brand still reads "construction orange." Whoever owns the brand should sign off.

**Option B:** Keep `#FF6B2B` for CTA fills (accept AA-large only for white text at 17pt+SemiBold) and add a separate `primaryDark: #B8431A` token specifically for text-on-light usages (toggle link, Exit, Previous, blockedLabel). `#B8431A` on `#F5F5F0` = ~6.8:1 (PASS AA-normal).

Either path closes all three MINORs.

---

## E. RTL safety (grep summary)

| Grep | Result |
|---|---|
| `marginLeft|marginRight|paddingLeft|paddingRight|borderLeftWidth|borderRightWidth|left:|right:|textAlign:\s*['"](left\|right)['"]` | **0 matches** in `apps/mobile/src/` |
| `flexDirection: 'row-reverse'` | **0 matches** |
| `start:|end:|marginStart|marginEnd|paddingStart|paddingEnd` (logical properties usage) | 1 match: `SessionScreen.tsx:294 end: spacing.sm` (FAB) — correctly uses logical end |

**RTL verdict: PASS, ZERO violations.** Yoni honored Lena's logical-property rule precisely. Hebrew RTL will Just Work once locale is flipped. (Caveat: I cannot simulate the actual RTL flip without an emulator — but the *static* surface is clean.)

---

## F. Component test review

| Test file | # tests | Coverage of brief behaviors | Verdict |
|---|---|---|---|
| `AssistantSheet.test.tsx` | 6 | typing indicator on `loading` ✓, blocked state renders `safety.reason` ✓, response text renders when not blocked ✓, errorMessage renders ✓, submit disabled when empty ✓, trimmed-question submit + clear ✓. **All 6 map to Lena/Jasmin spec behaviors. No smoke noise.** | PASS |
| `ARView.test.tsx` | 3 | fallback when ViroReact mocked-throws ✓, fallback when `forceFallback=true` ✓, custom caption renders ✓. Both fallback paths covered as the brief requires. The "AR active" branch is NOT tested (can't be — the require would have to succeed in jest, which the global mock prevents). Acceptable — the active branch is also a placeholder pending the device-bearing follow-up. | PASS |
| `ProjectCard.test.tsx` | 3 | title + category + time render ✓, onPress fires with full project payload ✓, no-category omits the line ✓. NOT a smoke test — verifies behavior. NOTE: difficulty rendering is tested in `DifficultyIndicator.test.tsx` rather than here; acceptable separation. NOTE: no test verifies "tap navigates" — but ProjectCard takes `onPress` as a prop, navigation is wired in HomeScreen render-prop. The unit test mocks onPress and verifies invocation; that's the correct test boundary. | PASS |
| `DifficultyIndicator.test.tsx` | 3 | difficulty=3 renders 3 filled + 2 outline (wrenches, not stars!) ✓, null treated as 0 + a11y label intact ✓, >5 clamps to 5 ✓. Verifies the brief's anti-stars requirement via the testID convention `difficulty-icon-N-filled|outline`. | PASS |
| `StepProgressIndicator.test.tsx` | 3 | one-based "Step 1 of 6" ✓, clamps to total ✓, a11y label "Step N of M" ✓. Brief said "single text line, no progress bar" — that's exactly what's tested. | PASS |
| `api.test.ts` | 7 | listProjects with/without token ✓, createSession POST shape ✓, patchSession PATCH partial fields ✓, **assist POST body matches `AssistRequest`** ✓, ApiError envelope parsing ✓, non-JSON error fallback ✓. Includes the Jasmin-flagged "assist body shape" check explicitly. | PASS |
| `format.test.ts` | 9 | formatMinutes em-dash on null/0/negative ✓, "~N min" sub-hour ✓, "~N h" whole ✓, "~N h M min" remainder ✓, formatElapsed null guards ✓, real range ✓, hour spans ✓, clampDifficulty rounds and clamps ✓. Strong coverage of all pure helpers. | PASS |

**Total: 35 tests across 7 suites, all PASS. Per Yoni's report.** Test count matches; behavior coverage matches the brief.

One non-fatal `act()` warning surfaces in AssistantSheet (per Yoni's own note) for an async setState after onSubmit — polish-only, suppression is one-line. **NIT-10 (optional).**

---

## G. Cross-checks

| Check | Result |
|---|---|
| No analytics SDK (mixpanel/amplitude/posthog/segment/firebase-analytics) | **PASS — zero matches** in entire `apps/mobile/` |
| No social/OAuth login (signInWithOAuth/signInWithOtp/Google/Apple/Facebook/magicLink) | **PASS — zero matches** in `apps/mobile/src/`. AuthContext uses only `signInWithPassword` and `signUp` (email/password). |
| Sign-up toggle present in SignInScreen | **PASS** — implemented with mode toggle, Confirm password field, password-match validation. Not deferred. |
| No marketing copy | **PASS** — all UI strings are functional (labels, button text, status, errors). No landing-page or sales copy. |

---

## Findings summary

### BLOCKER (0)
*(none)*

### MAJOR (0)
*(none)*

### MINOR (3 distinct root causes, 5 files affected)
- **MINOR-1A** — Hardcoded hex `#FFF4E5` in `AssistantSheet.tsx:188`. Promote to `theme/colors.ts` as `warningBg` (or similar). Token-discipline violation.
- **MINOR-1B** — Hardcoded hex `#FBEAEA` in `AssistantSheet.tsx:201`. Promote to `theme/colors.ts` as `errorBg`. Token-discipline violation.
- **MINOR-2** — No `accessibilityLiveRegion="polite"` on any loading/error surfaces. Screen-reader users will not be auto-notified when "Thinking…" appears or when errors land. Affected testIDs: `assistant-typing`, `assistant-error`, `assistant-blocked`, `session-step-error`, `signin-error`, `signin-confirm-error`, plus `home-error` heading.
- **MINOR-3** — White on `#FF6B2B` primary CTA fill recomputes to **2.84:1**, not the 4.8 Yoni claimed. Fails AA-large (3.0) AND AA-normal (4.5). Affects every primary CTA in the app (~7 places). Remediation: darken primary to ~`#D9531C` (Option A) or accept the visual + add a `primaryDark` text token (Option B).
- **MINOR-4** — `#FF6B2B` text on `#F5F5F0` background = **2.60:1**. Fails AA-normal. Affects SignInScreen mode-toggle link, SessionScreen Exit text, Previous button text. Same root cause as MINOR-3.
- **MINOR-5** — `#FF6B2B` "Assistant blocked this question" label on `#FFF4E5` background = **2.61:1**. Fails AA. Same root cause.

*MINOR-3, -4, -5 collapse into one decision: darken primary, OR add a darker text variant. Either fix closes all three. Counting separately because they live in three different code locations.*

### NIT (5 → 10 if granular)
- NIT-1 — ProjectDetailScreen load-failure shows a Back button rather than auto-navigating to Home + toast (Lena spec). Functionally fine.
- NIT-2 — SessionScreen does not render step `image_url`. Confirm with Silas whether the step schema exposes it.
- NIT-3 — Exit on SessionScreen does not explicitly POST a save (relies on prior tick). Add a comment.
- NIT-4 — Step-save failure shows inline error rather than bottom toast (brief said toast). Same UX outcome (don't block).
- NIT-5 — Completion checkmark is static, brief allowed Lottie fallback. Acceptable per brief.
- NIT-6 — Home retry button has no explicit `accessibilityLabel` (inner text suffices).
- NIT-7 — Exit-confirm Keep/Exit buttons same — no explicit `accessibilityLabel`.
- NIT-8 — No focus management when AssistantSheet opens/closes (brief said focus should move to input on open, return to FAB on close). RN platform gap; document as deferred or implement with a ref + `AccessibilityInfo.setAccessibilityFocus`.
- NIT-9 — Exit-confirm modal does not trap a11y focus. RN platform behavior; document.
- NIT-10 — `act()` warning in AssistantSheet test (cosmetic, doesn't affect pass/fail).
- (Token-grid NIT — three uses of `spacing.xs / 2 = 4px` step off the 8-multiple grid. Mathematically derived, not hardcoded. Suggest adding `xxs: 4` to spacing scale if Lena wants formal coverage.)

---

## Definition-of-done checklist (per dispatch brief)

1. **Per-screen verdict table (5 rows) with PASS/PASS WITH NOTES/FAIL + line cites.** ✓ Section A.
2. **Token discipline grep summary.** ✓ Section B.
3. **Accessibility findings with severity.** ✓ Section C + Findings summary.
4. **Color contrast verification (recompute or sample-verify).** ✓ Section D — independently recomputed all 11 pairs; found 3 fails Yoni did not flag.
5. **RTL grep summary.** ✓ Section E — zero violations.
6. **Component test review (per-test-file commentary).** ✓ Section F — 7/7 suites, 35/35 tests reviewed.
7. **Headline.** ✓ At top: **HOLD — needs 3 minor color-contrast fixes before merge** (0 BLOCKER, 0 MAJOR, 3 MINOR-distinct, 5 NIT).

---

## Recommendation to Andy

Two viable paths:

**Path 1 (clean):** Send MINOR-1A/B (extract hex tokens) and MINOR-3/4/5 (contrast) back to Yoni as a small Wave-2.1 fix. ETA ~30 min — token extraction is trivial, contrast is one decision (darken primary OR add primaryDark variant) plus a token rename. MINOR-2 (live regions) is another 15 min of additive props. Then re-QA: I can re-verify in ~10 min once the diff lands. Total close-out: under an hour.

**Path 2 (pragmatic):** Merge as-is with the contrast issues documented as known-debt for Phase 2 (Lena's input on brand-tweak preferred for orange anyway). Argument: visual contrast is a polish layer that's easier to dial in once we see live screens. Argument against: WCAG AA is a stated Lena requirement.

I recommend **Path 1**. The fixes are small, the risk of letting AA-fail ship is real (it affects every primary CTA), and Lena's brief is explicit about AA. Jasmin's security/integration pass can run in parallel with Yoni's contrast fix.

Component tests are excellent. RTL is excellent. Touch targets are excellent. The only systemic gap is the orange-vs-AA tension, which is fixable in minutes.

— Vera
