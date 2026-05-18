# Yoni — BUILDAR-S1-011 FINAL FIX — DONE

**Task:** Close MINOR-3 (white-on-primary contrast fail) per Jasmin re-verify, plus bundle NIT-A1.
**Branch:** `feat/mobile-shell`
**Status:** DONE — branch is MERGE GREEN.

## Commits

- `5076063` — fix(mobile): WCAG AA-normal — primary #D9531C → #C0461A
- `337ba11` — feat(mobile): NIT-A1 — TextInput maxLength=2000 matches Zod backend

## Recomputed contrast ratios (independent Python verify, WCAG 2.x sRGB)

| Pair | Ratio | Requirement | Verdict |
|---|---|---|---|
| `#FFFFFF` on new `primary` `#C0461A` | **5.08:1** | ≥ 4.5 AA-normal | PASS |
| `#FFFFFF` on new `primaryPressed` `#A03A14` | **6.75:1** | ≥ 3.0 AA-large (4.5 ideal) | PASS — exceeds AA-normal |
| `#B8431A` text on `#F5F5F0` bg (`primaryDark`, unchanged) | **4.98:1** | ≥ 4.5 AA-normal | PASS (unchanged) |
| OLD `#FFFFFF` on `#D9531C` (for reference) | 4.04:1 | ≥ 4.5 AA-normal | FAIL — confirms Jasmin's recompute |

`primaryDark` `#B8431A` is UNCHANGED as instructed (text token, ~4.98:1 on `#F5F5F0`).

## Token tape

- `primary`: `#D9531C` → `#C0461A`
- `primaryPressed`: `#B8431A` → `#A03A14` (was lighter than new primary; swapped to a true darker pressed state)
- `primaryDark`: `#B8431A` (unchanged)
- Comments in `colors.ts` updated to reflect new ratios and history.

## NIT-A1

`AssistantSheet.tsx` line ~128: added `maxLength={2000}` to the `<TextInput>`. Matches existing Zod backend cap. No behavior change for inputs ≤ 2000 chars.

## CI

- `pnpm --filter @buildar/mobile lint` — clean
- `pnpm --filter @buildar/mobile typecheck` — clean
- `pnpm --filter @buildar/mobile test` — **35/35 passed** (7 suites)
- Pre-existing act() console warning in `AssistantSheet.test.tsx` unrelated and unchanged.

## Ready for

Inon to authorize merge of `feat/mobile-shell` → `main`.
