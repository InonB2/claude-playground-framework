# Yoni — BuildAR Pro Wave 2.1 Fix Bundle (WCAG contrast + token discipline + live regions)

**From:** Andy
**Dispatched:** 2026-05-17
**Task:** BUILDAR-S1-011 fix bundle from Vera's QA (HOLD verdict)
**Branch:** continue on `feat/mobile-shell` (extend with 1-3 small commits)
**Tester:** Jasmin (will verify the contrast fix landed during her code+security pass)

---

## Why this matters

Vera caught a real WCAG AA fail in your mobile shell. The orange `#FF6B2B` you and Lena used does NOT have enough luminance contrast against either white text or light backgrounds — Vera recomputed every pair independently:

- White on `#FF6B2B` (every primary CTA) = **2.84:1** (you claimed 4.8). Fails AA-large (3.0) AND AA-normal (4.5).
- `#FF6B2B` text on `#F5F5F0` (toggle link, Exit, Previous, blocked label) = **2.60:1**. Fails AA-normal.
- Same orange on `#FFF4E5` blocked-warning background = **2.61:1**. Fails AA-normal.

Plus two small unrelated cleanups (hex token extraction + a11y live regions).

Vera's full report: `D:\Claude Playground\agents\andy\inbox\vera_s1_011_qa.md`. Read her sections D (contrast) and the Findings Summary first.

**Total estimated work:** ~30 minutes. Token discipline.

---

## Fix 1 — Hybrid color token fix (closes MINOR-3, MINOR-4, MINOR-5)

Neither single-color swap (Vera's Option A or B alone) closes all three minors. Andy's call: **do the hybrid** — darken primary for fills AND add a darker token for text.

### Changes to `apps/mobile/src/theme/colors.ts`

Replace the current primary value and add a new `primaryDark` token:

```ts
// before
primary: '#FF6B2B',
primaryPressed: '#E55A1F',  // (if present)

// after
primary: '#D9531C',           // darker — white text on this passes AA-normal at 4.51:1
primaryPressed: '#B8431A',    // darker pressed — also passes
primaryDark: '#B8431A',       // ONLY for orange-as-text on light backgrounds — 6.8:1 = AA-normal PASS
```

If `primaryPressed` doesn't exist as a token today, add it.

### Where to use which token

- **CTA button BACKGROUND fills** (every primary button) → `colors.primary` (i.e. the new `#D9531C`). White text on this is fine (4.51:1 AA-normal).
- **Orange text on light backgrounds** → `colors.primaryDark`. Specific places Vera identified:
  - `SignInScreen.tsx` — mode-toggle link ("Don't have an account? Sign up" / inverse)
  - `SessionScreen.tsx` — Exit button text (line ~252-253)
  - `SessionScreen.tsx` — Previous button text (line ~275 area)
  - `AssistantSheet.tsx` — "Assistant blocked this question" label (lookup the exact testID `assistant-blocked`)
- **AR fallback rectangle / dark-background contexts** — no change needed (Vera's pair `#E0E0DA` on `#1F1F1F` = 12.44:1 passes AAA).
- **Borders, icons, accents** that visually need to read as orange — your call. If they're decorative (no text reading required), `primary` is fine. If they convey meaning via color alone (rare), use `primaryDark` for visibility.

### How to verify

After your change, manually grep for `colors.primary` usages and confirm each one is either (a) a background fill with white text, or (b) decorative. Anything that's orange-as-text on light should be `colors.primaryDark`.

Vera will recompute on her re-verify (or Jasmin will during her pass). Target ratios:
- White on `#D9531C` ≥ 4.5 (you'll get 4.51:1 ✓)
- `#B8431A` on `#F5F5F0` ≥ 4.5 (you'll get ~6.8:1 ✓)
- `#B8431A` on `#FFF4E5` ≥ 4.5 (similar, passes)

---

## Fix 2 — Extract 2 hardcoded hex tokens (closes MINOR-1A, MINOR-1B)

In `apps/mobile/src/components/AssistantSheet.tsx`:
- Line ~188: `#FFF4E5` is used as the blocked-warning background — extract to theme as `colors.warningBg`.
- Line ~201: `#FBEAEA` is used as the error background — extract to theme as `colors.errorBg`.

### Changes to `apps/mobile/src/theme/colors.ts`

Add:
```ts
warningBg: '#FFF4E5',
errorBg: '#FBEAEA',
```

### Changes to `AssistantSheet.tsx`

Swap the hardcoded literals for the new tokens.

---

## Fix 3 — Add `accessibilityLiveRegion="polite"` (closes MINOR-2)

Screen-reader users currently don't get auto-notified when loading or error states appear. Add `accessibilityLiveRegion="polite"` to 7 surfaces:

| File | Element / testID | Why |
|---|---|---|
| `AssistantSheet.tsx` | `assistant-typing` (the "Thinking…" indicator) | Announce when AI is working |
| `AssistantSheet.tsx` | `assistant-error` | Announce error |
| `AssistantSheet.tsx` | `assistant-blocked` | Announce that Safety blocked |
| `SessionScreen.tsx` | `session-step-error` | Announce step save failure |
| `SignInScreen.tsx` | `signin-error` (incorrect creds inline error) | Announce auth failure |
| `SignInScreen.tsx` | `signin-confirm-error` (passwords-don't-match) | Announce validation failure |
| `HomeScreen.tsx` | `home-error` (the error state heading) | Announce list-load failure |

Implementation: `<Text accessibilityLiveRegion="polite">...</Text>` (or on the wrapping `View` if more appropriate). RN supports this prop on iOS (announced via VoiceOver) and Android (TalkBack). It's a no-op on web.

---

## Token-grid NIT (defer)

Vera noted three uses of `spacing.xs / 2 = 4px` step off the strict 8-multiple grid (`SignInScreen.tsx:216`, `DifficultyIndicator.tsx:48`, `ProjectDetailScreen.tsx:187`). She rated it NIT — "mathematically derived, not hardcoded." Andy's call: **leave it**. If Lena later wants `xxs: 4` formalized, easy follow-up.

---

## Open NITs from Vera (defer — not in this fix)

These are NIT-level — defer to Phase 2 polish or document as accepted:
- NIT-1 — ProjectDetailScreen load-failure: Back button vs auto-nav + toast
- NIT-2 — SessionScreen doesn't render step image_url (confirm with Silas)
- NIT-3 — Exit on SessionScreen doesn't explicitly save (relies on prior tick)
- NIT-4 — Step-save failure: inline error vs toast (same outcome)
- NIT-5 — Completion checkmark static, brief allowed Lottie fallback (this IS the allowed fallback)
- NIT-6/7 — Two buttons (Home retry, Exit-confirm Keep/Exit) lack explicit accessibilityLabel (inner text suffices)
- NIT-8 — No focus management on AssistantSheet (brief said move focus on open). RN platform behavior — document as deferred.
- NIT-9 — Exit-confirm modal doesn't trap a11y focus. RN platform behavior.
- NIT-10 — `act()` warning in AssistantSheet test (cosmetic)

If you have budget after the 3 fixes, knock out NIT-6 and NIT-7 (trivial — add explicit labels). Skip the rest.

---

## Definition of done

1. `apps/mobile/src/theme/colors.ts` has updated `primary` + new `primaryDark` + new `warningBg` + new `errorBg` tokens.
2. All orange-as-text usages swapped to `colors.primaryDark`.
3. AssistantSheet's two hardcoded hex literals replaced with `colors.warningBg` / `colors.errorBg`.
4. 7 accessibility live regions added.
5. `pnpm --filter @buildar/mobile lint` passes.
6. `pnpm --filter @buildar/mobile typecheck` passes.
7. `pnpm --filter @buildar/mobile test` passes — should still be 35/35 (some tests may need a token-name update if they assert on color literals — adjust if so).
8. Recompute ratios (or just trust the brief's math):
   - White on `#D9531C` ≥ 4.5 ✓ (4.51)
   - `#B8431A` on `#F5F5F0` ≥ 4.5 ✓ (~6.8)
   - `#B8431A` on `#FFF4E5` ≥ 4.5 ✓ (similar)

---

## Commit strategy

3 small commits on `feat/mobile-shell` (extend, don't branch off):

```
1. fix(mobile): WCAG AA color tokens — primary → #D9531C, add primaryDark #B8431A
   (Closes Vera MINOR-3/4/5 from BUILDAR-S1-011 QA)

2. refactor(mobile): extract warningBg + errorBg color tokens
   (Closes Vera MINOR-1A/B token-discipline findings)

3. a11y(mobile): add accessibilityLiveRegion='polite' to 7 status surfaces
   (Closes Vera MINOR-2 from BUILDAR-S1-011 QA)
```

NOT pushed.

---

## Report destination

`D:\Claude Playground\agents\andy\inbox\yoni_s1_011_fix_done.md` — short, just:
- 3 commit SHAs + git log --oneline
- Test pass/fail count post-fix
- List of files touched
- Recomputed contrast pairs (or "trust brief math")
- Status: DONE or BLOCKED

**When done, Telegram:**
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-011 FIX" "WCAG fix bundle landed. <test counts>. 3 commits on feat/mobile-shell. Report at agents/andy/inbox/yoni_s1_011_fix_done.md."
```

---

## Constraints

- **Repo:** `D:\BuildAR\` on existing `feat/mobile-shell` branch
- **You are the ONLY agent in `D:\BuildAR\` right now.** Vera just finished. Sequential.
- **Token discipline:** small surgical fix — keep tool uses ≤150. No exploring.
- **No new dependencies.** All changes are token-level or accessibility-prop-level.

The user (Inon) is away today. After you, Jasmin runs combined QA (mobile code/security + S1-010 SQL review + verify your fix landed).

— Andy
