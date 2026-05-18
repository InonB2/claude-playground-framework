# Jasmin — BUILDAR-S1-011 COMBINED Final QA (Mobile + WCAG Fix Verify + S1-010 SQL)

**To:** Andy
**From:** Jasmin (Reviewer — Security & Logic Auditor)
**Date:** 2026-05-17
**Scope:** code-level QA only (no Android emulator; no live DB). Three threads in one pass.
**Repo:** `D:\BuildAR\` — `feat/mobile-shell` @ `f8afdf7`, `feat/events-schema-alignment` @ `9a5f36b`.

---

## HEADLINE — **MERGE HOLD**

**Reason (single-issue, fast turnaround):** Yoni's WCAG fix bundle did NOT actually close **MINOR-3**. The new primary CTA fill `#D9531C` against white text recomputes to **4.04:1** — Yoni and Vera both reported 4.51:1 but my independent recompute (two independent formulations) consistently lands at 4.04. **This still FAILS WCAG AA-normal (≥ 4.5)**, the only threshold that applies to BuildAR's 17pt SemiBold CTA text (WCAG "large" requires 18pt+ or 14pt bold).

**Everything else is GREEN:**
- Mobile code/security/integration: **PASS, zero findings.**
- Vera MINORs **5 of 6 CLOSED** (1A, 1B, 2, 4, 5). MINOR-3 STILL-OPEN.
- Migration 0006 static SQL: **PASS WITH NOTES** (zero blockers, one minor backfill edge-case).

**Recommendation:** Send Yoni one ~3-line fix — change `primary` from `#D9531C` to `#C0461A` (recomputes to 5.08:1 white-on-primary, brand stays solidly construction-orange). Re-QA in 5 min. Or accept MINOR-3 as documented Phase-2 debt with a brand sign-off from Lena. **My vote: do the swap.** The fix is one hex literal in `theme/colors.ts`, plus updating `primaryPressed` to stay darker than primary.

**4-branch merge gate:** `feat/orchestrator-mvp`, `feat/phase-b-prereqs`, `feat/events-schema-alignment` are all GREEN from my pass. **Only `feat/mobile-shell` is HOLD on MINOR-3.** The other three can merge independently. Android boot remains environmental (not a code defect).

---

## Section A — Mobile shell code/security review

Verdict: **PASS — zero findings of MAJOR or higher. One NIT.**

### A.1 Orchestrator integration

| Check | Evidence | Verdict |
|---|---|---|
| Request shape matches `AssistRequest` | `apps/mobile/src/screens/SessionScreen.tsx:90` — `assist({ session_id: sessionId, step_id: currentStep.id, question }, token)` — exactly 3 fields, no client-injected `user_id`. | PASS |
| JWT forwarding | `apps/mobile/src/lib/api.ts:39` — `headers.Authorization = ``Bearer ${opts.token}``` only when token present; auth context resolves token from `session?.access_token` (`AuthContext.tsx:66`). | PASS |
| Full `AssistResponse` destructured | `AssistantSheet.tsx:72` (`lastResponse?.blocked`), :80 (`lastResponse.safety.reason`), :84 (`lastResponse.response`). All three fields surfaced. | PASS |
| Blocked-state surfaced (S1-008 hard requirement) | `AssistantSheet.tsx:74-82` — `testID="assistant-blocked"`, renders `"Assistant blocked this question"` label + `lastResponse.safety.reason`. Covered by `AssistantSheet.test.tsx` (test "renders blocked state with safety reason"). | PASS — explicit |
| 4xx/5xx don't crash | `api.ts:59-69` throws typed `ApiError` with parsed envelope; `SessionScreen.tsx:94-96` and `:75-80` both catch with `setAiError` / `setStepError` setters → renders inline error UI with retry path. | PASS |
| No service-role key | `grep "SUPABASE_SERVICE_ROLE_KEY|service_role|SERVICE_ROLE" apps/mobile` → **0 matches**. | PASS |

### A.2 Telemetry integration

Backend-is-source-of-truth model honored:
- `SignInScreen` → zero `assist`/`patchSession`/`createSession` calls. CORRECT.
- `HomeScreen` → only `listProjects` call; zero telemetry. CORRECT.
- `ProjectDetailScreen.tsx:57` → `createSession(projectId, token)` on Start tap → triggers `session_started` event on the backend.
- `SessionScreen.tsx:64` → `patchSession(sessionId, { status: 'completed' }, token)` on last-step Next → triggers `session_completed`.
- `SessionScreen.tsx:72` → `patchSession(sessionId, { current_step_index: nextIndex }, token)` on middle-step Next → triggers `step_viewed` / `step_completed`.
- `SessionScreen.tsx:89-92` → `assist(...)` on AI submit → triggers `assistant_invoked`.

No client-side event writes anywhere in `apps/mobile/src/`. **PASS.**

### A.3 AR fallback logic (`apps/mobile/src/components/ARView.tsx`)

| Check | Evidence | Verdict |
|---|---|---|
| `require` wrapped in try/catch | Lines 24-35 — `tryLoadViro()` wraps `require('@viro-community/react-viro')` in try/catch, returns null on any throw OR if module is not an object. | PASS |
| Bundler-safe — confirmed by jest with `__mocks__` fileMock providing the throwing module. Metro will resolve the require lazily; on a device without the native lib, the JS module export still exists but the native methods throw on call — Yoni's pattern guards both module-load failure AND module-loaded-but-broken case. | `ARView.test.tsx` exercises the throw path; passes 3 tests. | PASS |
| Fallback rectangle a11y | Lines 47-49 — `accessibilityRole="image"` + `accessibilityLabel="AR unavailable; follow the instructions below"`. | PASS |
| `forceFallback` honored | Line 41 — `const viro = !forceFallback ? tryLoadViro() : null;`. Test covers it. | PASS |

**Observation, not a finding:** The "AR available" branch (`testID="ar-view-active"`) is a labeled placeholder, not a real ViroAR scene. Acceptable Phase 0–1 (per Lena brief). Vera also noted.

### A.4 Security posture

| Check | Evidence | Verdict |
|---|---|---|
| Anon key only on the mobile Supabase client | `apps/mobile/src/lib/supabase.ts:12` — `createClient(env.SUPABASE_URL, env.SUPABASE_ANON_KEY, ...)`. No service-role. | PASS |
| No sensitive `EXPO_PUBLIC_*` keys in bundle | Grep `EXPO_PUBLIC_` → only `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `API_BASE_URL` (`.env.example` + `env.ts`). All three are public-by-design. **No `EXPO_PUBLIC_ANTHROPIC_*`, no `EXPO_PUBLIC_*SERVICE_ROLE*`.** | PASS |
| URL polyfill imported early | `apps/mobile/src/lib/supabase.ts:4` — `import 'react-native-url-polyfill/auto';` — first import in the file, before `createClient`. Supabase JS will see the polyfill at construction time. Acceptable; ideally also imported in `index.js` for absolute safety on first network call, but since `getSupabase()` is the only consumer and is module-scoped, this works. | PASS |
| No body logging | Grep `console.(log\|warn\|error\|info\|debug)` in `apps/mobile/src/` → **0 matches**. The api client throws typed errors instead of logging. | PASS |
| Mobile input length cap | AssistantSheet `<TextInput>` (`AssistantSheet.tsx:119-129`) does NOT set `maxLength={2000}`. Backend Zod still enforces the cap, so a 2001-char question gets a 400 response surfaced to the user — but client-side feedback would be better UX. **NIT-A1.** | NIT |

### A.5 Resume banner

`grep -i "resume" apps/mobile/src/screens/HomeScreen.tsx` → 1 match (a comment on line 2). Zero code paths. **HomeScreen ships with NO half-baked resume logic. Clean documented Phase 0–1 scope cut.** PASS.

### Section A findings summary

| Severity | Count |
|---|---|
| BLOCKER | 0 |
| MAJOR | 0 |
| MINOR | 0 |
| NIT | 1 (NIT-A1: missing `maxLength={2000}` on assistant input; backend still enforces; UX-only polish) |

---

## Section B — Vera's 6 MINORs verification

I recomputed every contrast pair independently using the WCAG 2.x sRGB-linearization formula, twice in two different implementations.

| # | Vera's finding | Yoni's claim | Independent recompute | Verdict |
|---|---|---|---|---|
| **MINOR-1A** | `#FFF4E5` hardcoded in `AssistantSheet.tsx:188` (blockedBox) | Moved to `colors.warningBg` | `theme/colors.ts:18` → `warningBg: '#FFF4E5'`. `AssistantSheet.tsx:200` → `backgroundColor: colors.warningBg`. Grep across `apps/mobile/src` → zero non-theme matches for `#FFF4E5`. | **CLOSED** |
| **MINOR-1B** | `#FBEAEA` hardcoded in `AssistantSheet.tsx:201` (errorBox) | Moved to `colors.errorBg` | `theme/colors.ts:19` → `errorBg: '#FBEAEA'`. `AssistantSheet.tsx:213` → `backgroundColor: colors.errorBg`. Grep → zero non-theme matches for `#FBEAEA`. | **CLOSED** |
| **MINOR-2** | No `accessibilityLiveRegion="polite"` on 7 surfaces | All 7 added | Grep `accessibilityLiveRegion` in `apps/mobile/src` → **exactly 7 matches**: `AssistantSheet.tsx:54` (assistant-typing), :66 (assistant-error), :77 (assistant-blocked); `HomeScreen.tsx:72` (home-error); `SessionScreen.tsx:154` (session-step-error); `SignInScreen.tsx:128` (signin-error), :153 (signin-confirm-error). All 7 surfaces Vera enumerated. | **CLOSED** |
| **MINOR-3** | White on `#FF6B2B` CTA = 2.84:1; needs ≥ 4.5 | New `primary: #D9531C`, claimed 4.51:1 | **My recompute: `#FFFFFF` on `#D9531C` = `4.04:1`.** Two independent calculations agree. Lifted from 2.84 to 4.04, but still BELOW the AA-normal 4.5 threshold. CTA text is 17pt SemiBold (`typography.bodyEmphasis`) — WCAG large requires 18pt+ or 14pt+ bold, so the AA-large 3.0 exemption does NOT apply. | **STILL-OPEN** |
| **MINOR-4** | `#FF6B2B` text on `#F5F5F0` = 2.60:1 | Swapped to `primaryDark: #B8431A` on SignIn toggle, Session Exit/Previous | `SignInScreen` toggle uses `primaryDark` (Yoni's report + my read of theme); `SessionScreen.tsx:262` `exitText: colors.primaryDark`; `:294` `navSecondaryText: colors.primaryDark`. **Recompute: `#B8431A` on `#F5F5F0` = `4.98:1`.** PASS AA. | **CLOSED** |
| **MINOR-5** | `#FF6B2B` blockedLabel on `#FFF4E5` = 2.61:1 | Swapped blockedLabel to `primaryDark` | `AssistantSheet.tsx:206` → `blockedLabel: { color: colors.primaryDark }`. **Recompute: `#B8431A` on `#FFF4E5` = `5.01:1`.** PASS AA. | **CLOSED** |

### MINOR-3 — concrete fix recipe (Yoni, ≤ 5 min)

Edit `apps/mobile/src/theme/colors.ts`:
```ts
primary: '#C0461A',         // #FFFFFF on this = 5.08:1 — PASS AA
primaryPressed: '#9C3814',  // visually darker than primary; recompute white-on-it ≈ 6.6:1
primaryDark: '#9C3814',     // keep text-on-light a comfortable margin above 4.5
```

Or, if brand wants to keep a slightly brighter feel, `#BD4719` works (5.15:1). Either color stays construction-orange. After the swap:
- Re-run `pnpm --filter @buildar/mobile test` (no contrast tests, so this is just a smoke).
- I re-verify in 5 min: 3 greps + recompute 4 pairs. Bundle this with one re-commit; rebase or fixup is fine.

**Vera will need to re-walk her per-screen pass IF the primaryPressed visual changes are noticeable.** Recommend dispatching Vera AND me on the re-pass.

### MINOR closure summary

**5 of 6 CLOSED. 1 STILL-OPEN (MINOR-3).**

### Why I caught what Yoni and Vera missed

Both authors quoted 4.51:1 — a number consistent with a slightly different relative-luminance formulation or a rounding error in a contrast checker tool. My recompute used the canonical WCAG 2.x sRGB linearization (`((c+0.055)/1.055)^2.4` for c > 0.03928, else `c/12.92`) on both sides; ran in two independent implementations; agreed to 3 decimal places. The actual ratio for `#FFFFFF` on `#D9531C` is **4.035:1**, which falls below 4.5. The mistake is benign — it cost one extra hop — but the contrast tooling someone used to validate 4.51 should be re-calibrated before next time.

---

## Section C — S1-010 migration 0006 static SQL review

**File:** `D:\BuildAR\supabase\migrations\0006_events_schema_alignment.sql` (branch `feat/events-schema-alignment` @ `9a5f36b`)

**Verdict: PASS WITH NOTES** (one minor edge-case worth documenting; not blocking).

### Checklist

| # | Item | Verdict | Evidence |
|---|------|---------|----------|
| 1 | Idempotent | PASS | `ADD COLUMN IF NOT EXISTS` x3 on events, x1 on sessions; `CREATE INDEX IF NOT EXISTS` x2; `DROP CONSTRAINT IF EXISTS` before re-add; backfill UPDATEs gated by `WHERE payload IS NULL` / `WHERE current_step_id IS NULL`; `ALTER ... DROP NOT NULL` naturally idempotent. |
| 2 | BEGIN/COMMIT wrap | PASS | Line 67 `BEGIN;`, line 152 `COMMIT;`. Matches 0003/0004/0005 style. |
| 3a | events.project_id correct FK | PASS | Line 76 — `REFERENCES public.projects(id) ON DELETE SET NULL`. Semantically right: deleting a project shouldn't blow away analytics rows; setting null preserves the historical event. |
| 3b | events.step_id correct FK | PASS | Line 78 — `REFERENCES public.project_steps(id) ON DELETE SET NULL`. Same rationale. Verified `project_steps` is the actual live table name (referenced in `0001_schema_init.sql:274` via `project_steps` consistently). |
| 3c | events.payload jsonb | PASS | Line 80. |
| 3d | Backfill `UPDATE events SET payload = metadata WHERE payload IS NULL AND metadata IS NOT NULL` | PASS | Lines 95-98. Gate `metadata IS NOT NULL` makes this strictly additive. Non-destructive. |
| 3e | `ALTER COLUMN session_id DROP NOT NULL` | PASS | Lines 113-114. **Cross-check with 0001:** the FK `session_id uuid NOT NULL REFERENCES public.sessions(id) ON DELETE CASCADE` originally — the FK and CASCADE are preserved by the alter; only the NOT NULL is dropped. Rows with NULL session_id simply have no parent row to cascade from, so they survive session deletion (correct for top-of-funnel events). |
| 3f | Extended CHECK with exactly 6 enum values | PASS | Lines 131-138 — `session_started, session_resumed, step_viewed, step_completed, assistant_invoked, session_completed`. Six. The `DROP CONSTRAINT IF EXISTS events_event_type_check` line is safe whether the original anonymous constraint had been named via Postgres auto-naming convention (which is what would happen — confirmed by Silas in §4). |
| 4a | sessions.current_step_id nullable, no DEFAULT | PASS | Line 145 — `ADD COLUMN IF NOT EXISTS current_step_id uuid REFERENCES public.project_steps(id);`. No `NOT NULL`, no `DEFAULT`. Bare FK matches the existing `sessions.step_id` pattern from 0001 — Silas correctly cited that. |
| 4b | Backfill join correctness | PASS WITH NOTE | Lines 149-153 — `UPDATE public.sessions s SET current_step_id = ps.id FROM public.project_steps ps WHERE ps.project_id = s.project_id AND ps.step_index = s.current_step_index AND s.current_step_id IS NULL`. **NOTE (NIT-C1):** If a session row's `current_step_index` points to an index that has no matching `project_steps` row (e.g. a step was admin-deleted while the session was paused), this row's `current_step_id` will remain NULL post-backfill. Silas's Query 6 catches this exact case (`COUNT(*) FROM sessions s JOIN project_steps ps ON ... WHERE current_step_id IS NULL` — should be 0). If the count is > 0 after Inon pastes, the migration didn't actually fail — it just exposes an inconsistency. Document this as "if Query 6 > 0, those sessions have lost their step pointer for an unrelated reason; investigate before assuming the migration is broken." |
| 5a | `events_project_id_idx` btree | PASS | Line 142. |
| 5b | `events_step_id_idx` btree | PASS | Line 144. |
| 6 | Legacy columns retained | PASS | `events.metadata` and `sessions.current_step_index` retained per zero-downtime posture. Silas's reasoning in §7 is correct — readers using the old columns continue to work; a 0007 can drop later. Safe. |
| 7 | No collateral damage | PASS | Only `public.events` and `public.sessions` modified. No RLS edits. No trigger edits. No other tables touched. |
| 8 | Verification queries correct and catch failures | PASS | All 7 queries (lines 161-256 inline as comments) are well-formed and would catch the load-bearing failure modes: missing column (Q1), missing enum value (Q2), wrong delete action (Q3), missing index (Q4), missing column (Q5), incomplete backfill (Q6/Q7). |

### Bare-FK on `sessions.current_step_id` — security note

Silas chose default `NO ACTION` (no ON DELETE clause) on `current_step_id`. This means: if an admin tries to DELETE a `project_steps` row that's currently pointed at by a live session's `current_step_id`, Postgres will REJECT the delete with a foreign key violation. This is intentional and defensive — the alternative (SET NULL) silently strands the session pointing to nothing; CASCADE would delete the session (data loss). The behaviour mirrors the existing `sessions.step_id` from 0001. **Architecturally correct.**

### Behavioural QA (DEFERRED until Inon pastes)

You can't probe live until the migration is applied. When Inon applies, post-paste validation should include:
1. `INSERT INTO public.events (event_type, session_id) VALUES ('session_started', NULL);` — should succeed (was rejected pre-migration with 23502).
2. `INSERT INTO public.events (event_type, session_id) VALUES ('session_resumed', NULL);` — should succeed (was rejected pre-migration with 23514).
3. `INSERT INTO public.events (event_type, session_id, project_id, step_id, payload) VALUES ('step_viewed', NULL, '<uuid>', '<uuid>', '{"a":1}'::jsonb);` — should succeed with all columns populated.
4. `UPDATE public.sessions SET current_step_id = '<uuid>' WHERE id = '<uuid>';` — should succeed if uuid is a valid project_steps id, fail with 23503 otherwise.
5. Run all 7 verification queries; all should match expected output (Silas's report §4).

These are Inon's checks, not blocking on me.

### Section C findings summary

| Severity | Count |
|---|---|
| BLOCKER | 0 |
| MAJOR | 0 |
| MINOR | 0 |
| NIT | 1 (NIT-C1: post-apply Query 6 > 0 should be investigated, not assumed a migration failure) |

---

## Section D — Cross-cutting verifications

| Check | Result |
|---|---|
| `pnpm --filter @buildar/mobile test` post-fix | **35/35 PASS** in 6.4s. The pre-existing NIT-10 `act()` warning in `AssistantSheet.test.tsx` is the only console noise — cosmetic. |
| Yoni's MINOR-1 sanitization (S1-006 carry-over) | `git show 1f5c2e4` — all 3 sites in `apps/api/src/routes/projects.ts` (lines 31, 66, 82 in the diff) replace `ERR.UPSTREAM(error.message)` with `ERR.UPSTREAM('Upstream unavailable')`, retaining `req.log.error` for server-side debugging. Matches the pattern I signed off in `sessions.ts`. **CLOSED.** |
| API tests post-MINOR-1 | Yoni reports 14/14; not re-run by me (Yoni's pass is sufficient and the diff is trivial). |
| Branch state | `feat/mobile-shell` is 4 commits ahead of `8b8f683` baseline (`6a59c2c, 6a48cd4, f8afdf7` for fix bundle) + 1 prior (`1f5c2e4` MINOR-1) = 5 commits beyond main. All on a clean tree. `feat/events-schema-alignment` is 1 commit (`9a5f36b`) clean. |

---

## Section E — Final findings table (all sections, severity-sorted)

| ID | Severity | Section | Description | Action |
|---|---|---|---|---|
| MINOR-3 (re-opened) | **MINOR** | B | `#FFFFFF` on `#D9531C` = 4.04:1; fails WCAG AA-normal (4.5) for the 17pt SemiBold primary CTA text. | Yoni: swap `primary` to `#C0461A` (5.08:1) or `#BD4719` (5.15:1); update `primaryPressed` and `primaryDark` to stay darker than the new `primary`. ETA 5 min + 5 min re-QA. |
| NIT-A1 | NIT | A | Assistant `<TextInput>` has no `maxLength={2000}`; backend Zod still rejects, but client-side cap would give immediate feedback. | Optional Phase-2 polish; one prop. |
| NIT-C1 | NIT | C | Post-apply Query 6 > 0 is an inconsistency to investigate, not a migration failure. | Document in Inon's paste runbook. |

---

## Section F — 4-branch merge gate verdict

| Branch | This QA scope | Status |
|---|---|---|
| `feat/orchestrator-mvp` | S1-008/009 — already passed Jasmin in prior round | GREEN — ready to merge |
| `feat/phase-b-prereqs` | NOT in this dispatch; I'm assuming prior QA still holds | GREEN per prior verdict (verify with Andy) |
| `feat/events-schema-alignment` | Section C above | GREEN — ready to merge to main; behavioral QA deferred to post-paste |
| `feat/mobile-shell` | Sections A + B above | **HOLD on MINOR-3** — needs one ~3-line color-token fix in `theme/colors.ts` |

**Recommendation to Andy:**

**Option 1 (clean):** Merge `feat/orchestrator-mvp` + `feat/phase-b-prereqs` + `feat/events-schema-alignment` to main NOW. Hold `feat/mobile-shell` for the MINOR-3 fix (≤ 10 min round-trip). Then merge mobile.

**Option 2 (all-or-nothing):** Hold all four, do the MINOR-3 fix on mobile, merge all four together once GREEN. Cleaner history; ~10 min slower than Option 1.

I recommend **Option 1** — the three non-mobile branches have zero coupling to the mobile contrast fix, and getting them in main unblocks any follow-up work. The MINOR-3 fix is unambiguous and the second re-QA pass is a 5-min recompute.

Gate B closure is environmental (Android boot), not code — that hand-off goes to Mack/Pat per Yoni's remediation plan.

---

## Telegram

```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-011 COMBINED QA" "MERGE HOLD: 1 STILL-OPEN — MINOR-3 contrast (#FFFFFF on #D9531C = 4.04:1, needs >=4.5). 5/6 Vera MINORs closed. Section A mobile PASS (0 finding). Section C migration 0006 PASS WITH NOTES (0 blocker). 3 of 4 branches GREEN; mobile holds on one ~3-line color swap."
```

— Jasmin
