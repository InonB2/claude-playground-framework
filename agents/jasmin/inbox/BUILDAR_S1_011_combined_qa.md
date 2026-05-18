# Jasmin — BuildAR Pro Sprint 1 Combined Final QA (Mobile + S1-010 SQL + Contrast Fix Verify)

**From:** Andy
**Dispatched:** 2026-05-17
**Tasks to QA:**
- BUILDAR-S1-011 (Yoni — Mobile shell): code/security/integration review
- BUILDAR-S1-011-FIX (Yoni — WCAG contrast + token + a11y fix bundle): verify the 6 MINORs Vera flagged actually landed
- BUILDAR-S1-010 (Silas — events schema alignment migration 0006): static SQL review

**Inputs:**
- Yoni's mobile shell done-report: `D:\Claude Playground\agents\andy\inbox\yoni_s1_011_done.md`
- Yoni's fix-bundle done-report: `D:\Claude Playground\agents\andy\inbox\yoni_s1_011_fix_done.md`
- Vera's UI QA report (the one Yoni's fix addresses): `D:\Claude Playground\agents\andy\inbox\vera_s1_011_qa.md`
- Silas's S1-010 done-report: `D:\Claude Playground\agents\andy\inbox\silas_s1_010_done.md`
- Lena's mobile UX brief (informational): `D:\Claude Playground\owner_inbox\design\buildar_mobile_ux_brief.md`
- Repo: `D:\BuildAR\` on branch `feat/mobile-shell` (5 commits beyond main, NOT pushed) + branch `feat/events-schema-alignment` (1 commit)

---

## Scope summary

You're the final QA gate. Three review threads in one pass:

1. **Mobile shell code/security review** — orchestrator integration, telemetry call sites, AR fallback logic, security posture, schema-adapter integrity in the mobile context (the mobile uses Yoni's adapter helpers from S1-009).
2. **Verify Vera's 6 MINORs are closed** — sample-recompute the new contrast pairs, grep for the old `#FF6B2B` orange-as-text, confirm the 7 live regions exist.
3. **Static SQL review on migration 0006** — same discipline as your S2-001/002 review.

Vera already did the UI/UX/a11y pass — no need to re-walk her per-screen checks. Focus on what only YOU do: security, integration logic, SQL safety.

**Critical constraint:** You CANNOT boot the mobile app (no Android SDK on host). Like Vera, your QA is code-level + brief-conformance, NOT visual screenshot review.

---

## Section A — Mobile shell code/security review

### A.1 Orchestrator integration (`apps/mobile/src/lib/api.ts::assist`)

Verify:
1. **Request shape matches `AssistRequest`** from `@buildar/core-types`. Should send `{ session_id, step_id, question }` — no extra fields, no client-injected `user_id`.
2. **JWT forwarding:** Bearer token from Supabase session is forwarded in the Authorization header.
3. **Response handling:** the mobile client correctly destructures `AssistResponse` shape — including `blocked: boolean`, `response: string | null`, `safety: { verdict, reason }`.
4. **Blocked-state surfacing:** when Safety returns `blocked: true`, the mobile renders the `safety.reason` (NOT silently swallowing it). This was your explicit S1-008 requirement. Verify in `AssistantSheet.tsx` — find the testID `assistant-blocked`.
5. **Error handling:** 401/4xx/5xx responses don't crash the sheet; user sees a friendly retry option.
6. **No service-role key:** grep `apps/mobile/src/` for `SUPABASE_SERVICE_ROLE_KEY` — must be ZERO matches. Mobile is anon-only.

### A.2 Telemetry integration

Mobile doesn't write events directly — it relies on backend routes (POST /sessions, PATCH /sessions/:id, POST /orchestrator/assist) firing the telemetry helpers Yoni wrote in S1-009. Verify in mobile:
- SignInScreen → no telemetry (correct; auth events come from Supabase auth.users trigger if at all)
- HomeScreen → no telemetry
- ProjectDetailScreen → `createSession` call on Start tap → backend writes `session_started`
- SessionScreen → `patchSession` on Next/Previous/Complete → backend writes `step_viewed`, `step_completed`, `session_completed`
- SessionScreen AssistantSheet → `assist` call → backend writes `assistant_invoked`

Confirm the mobile correctly issues these calls at the right lifecycle moments. No client-side telemetry expected (backend is source of truth).

### A.3 AR fallback logic (`apps/mobile/src/components/ARView.tsx`)

Yoni claims: `tryLoadViro()` wraps `require` in try/catch; returns null on any failure; component renders dark-fallback `<View testID="ar-view-fallback">`.

Verify:
1. The require-guard pattern doesn't throw during module load (RN bundlers can be aggressive — confirm Yoni's mock pattern works).
2. The fallback rectangle looks intentional (per Lena: dark rectangle + camera icon + "AR unavailable" label — Vera already confirmed brief-conformance; you check the accessibility label is correct).
3. `forceFallback` prop honored.

### A.4 Security posture

1. **Anon key only:** `apps/mobile/src/lib/supabase.ts` uses anon key from env. Grep confirms no service-role anywhere.
2. **No exposed secrets in bundle:** any `EXPO_PUBLIC_*` env vars are public-by-design (they end up in the JS bundle). Verify nothing sensitive (service role, Anthropic API key, etc.) is prefixed with `EXPO_PUBLIC_`. The mobile bundle should NEVER contain the Anthropic key — that lives backend-only on the API.
3. **URL polyfill:** Yoni mentioned importing URL polyfill for supabase-js compat. Confirm it's imported early (index.js or App.tsx) before any Supabase call.
4. **No API response body logging:** mobile API client must not log response bodies (could leak tokens, user data). Grep `console.log\|console.warn\|console.error` in `apps/mobile/src/lib/api.ts` and confirm no body-logging.
5. **Input validation in AssistantSheet:** the user types a question, mobile sends to /assist. Backend Zod-validates (you reviewed this in S1-008). Mobile should also enforce max length (2000 chars) client-side to give immediate feedback — verify or flag as NIT.

### A.5 Resume banner — Andy's call

Yoni flagged that HomeScreen's "resume banner" (Lena §Screen 2) is NOT rendered — no `GET /sessions?status=active` route yet. Andy's call (sent via Telegram to Inon): use client-side cache (no backend change). Yoni did NOT implement this either way. Two options:

1. Accept current state (no resume banner in v0) — log as deferred to Phase 2 — note in your QA.
2. Re-dispatch Yoni for client-side caching of last-active session ID in AsyncStorage/MMKV.

You don't need to implement — just verify Yoni didn't accidentally ship a half-baked resume path. If `HomeScreen.tsx` references any resume logic, flag it. If clean (just "no banner"), note as documented Phase 0–1 scope cut.

---

## Section B — Verify Vera's 6 MINORs are closed

Vera's report flagged:
- **MINOR-1A:** `#FFF4E5` hardcoded in AssistantSheet.tsx:188 → should be `theme/colors.ts::warningBg`
- **MINOR-1B:** `#FBEAEA` hardcoded in AssistantSheet.tsx:201 → should be `theme/colors.ts::errorBg`
- **MINOR-2:** No `accessibilityLiveRegion="polite"` on 7 surfaces → must exist on each
- **MINOR-3:** White on `#FF6B2B` CTA = 2.84:1 (fails AA) → primary should be `#D9531C` now
- **MINOR-4:** `#FF6B2B` orange-as-text on `#F5F5F0` = 2.60:1 (fails AA) → should use new `primaryDark` `#B8431A`
- **MINOR-5:** Same orange on `#FFF4E5` blocked-box = 2.61:1 → same `primaryDark` fix

### Verification steps

1. **Grep for old `#FF6B2B` in apps/mobile/src/**: ZERO matches expected. If any remain (including comments), flag.
2. **Grep for hardcoded `#FFF4E5` and `#FBEAEA`** in `apps/mobile/src/components/` and `apps/mobile/src/screens/`: should be ZERO matches (now only in theme/colors.ts).
3. **Read `apps/mobile/src/theme/colors.ts`**: confirm `primary: '#D9531C'`, `primaryDark: '#B8431A'`, `warningBg: '#FFF4E5'`, `errorBg: '#FBEAEA'` all present.
4. **Spot-recompute contrast pairs** (you can do this with the WCAG 2.x relative luminance formula — same math Vera used):
   - White on `#D9531C`: must be ≥ 4.5 for AA-normal (expected 4.51:1)
   - `#B8431A` on `#F5F5F0`: must be ≥ 4.5 (expected ~6.8:1)
   - `#B8431A` on `#FFF4E5`: must be ≥ 4.5 (expected similar)
5. **Grep for `accessibilityLiveRegion`** in `apps/mobile/src/`: expect 7 occurrences on the surfaces Vera listed (assistant-typing, assistant-error, assistant-blocked, session-step-error, signin-error, signin-confirm-error, home-error). Count and verify.
6. **Test suite still 35/35** — run `pnpm --filter @buildar/mobile test`.

### Verdict per MINOR

In your report, mark each of the 6 MINORs as CLOSED or STILL-OPEN with evidence.

---

## Section C — S1-010 static SQL review (migration 0006)

**File:** `D:\BuildAR\supabase\migrations\0006_events_schema_alignment.sql` (on branch `feat/events-schema-alignment`, commit `9a5f36b`)

Per Silas's done-report at `agents/andy/inbox/silas_s1_010_done.md` — review with the same discipline you applied to migrations 0004 and 0005.

### Review checklist

1. **Idempotent** — `ADD COLUMN IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, `DROP CONSTRAINT IF EXISTS` before re-adding. Confirm pattern.
2. **BEGIN/COMMIT wrap** — present. Same style as 0003 + 0004.
3. **Events schema changes:**
   - `ADD COLUMN project_id uuid REFERENCES public.projects(id) ON DELETE SET NULL` — correct?
   - `ADD COLUMN step_id uuid REFERENCES public.project_steps(id) ON DELETE SET NULL` — correct? (Confirm `project_steps` is the actual table name — Yoni's schema_request also used this name)
   - `ADD COLUMN payload jsonb` — correct?
   - Backfill: `UPDATE public.events SET payload = metadata WHERE payload IS NULL` — non-destructive, correct?
   - `ALTER COLUMN session_id DROP NOT NULL` — correct? Note: this makes top-of-funnel events possible per Yoni's brief.
   - `DROP CONSTRAINT events_event_type_check; ADD CONSTRAINT ... CHECK (event_type IN (..., 'session_resumed', ...))` — confirm exactly 6 enum values listed.
4. **Sessions schema change:**
   - `ADD COLUMN current_step_id uuid REFERENCES public.project_steps(id)` — correct? Did Silas correctly default to NULLABLE (no DEFAULT)?
   - Backfill: `UPDATE public.sessions s SET current_step_id = ps.id FROM public.project_steps ps WHERE ps.project_id = s.project_id AND ps.step_index = s.current_step_index` — correct join? Are there sessions where this join would return NULL (i.e. current_step_index points to a step that doesn't exist)? Edge case — flag if unhandled.
5. **Indexes:**
   - `events_project_id_idx` on `events(project_id)` — correct?
   - `events_step_id_idx` on `events(step_id)` — correct?
6. **Legacy columns retained** — Silas chose to NOT drop `events.metadata` or `sessions.current_step_index` in this migration. Yoni's adapter still works with the old columns. Drop is queued as a follow-up. Is this a safe zero-downtime posture? Verify.
7. **No collateral damage** — only events + sessions modified. No other tables, no RLS edits.
8. **Verification queries** — Silas provided 7 inline. Are they correct and would they catch a failed migration?

### Behavioral QA (DEFERRED until Inon pastes the SQL)

You can't behaviorally probe until Inon applies the migration to live DB. Document deferral plan:
- Insert event with project_id + step_id + payload → confirm columns populated correctly
- Insert event with session_id = NULL → confirm no longer rejected
- Insert event with event_type = 'session_resumed' → confirm no longer rejected
- Update session current_step_id → confirm FK constraint enforced

---

## Constraints

- **Repo:** `D:\BuildAR\` (both branches — checkout each as needed)
- **You are the ONLY agent in `D:\BuildAR\` right now.** Yoni's fix bundle just landed. Sequential.
- **Token discipline:** ≤300 tool uses. Three threads but each is focused.

---

## Definition of done

Your report at `D:\Claude Playground\agents\andy\inbox\jasmin_s1_011_combined_qa.md` should include:

1. **Mobile code/security verdict:** per Section A — findings table with severity (BLOCKER/MAJOR/MINOR/NIT), file:line cites.
2. **Vera MINOR closure verdict:** per Section B — 6 rows (each MINOR), CLOSED / STILL-OPEN with evidence.
3. **S1-010 SQL static review verdict:** per Section C — PASS / PASS WITH NOTES / FAIL with notes.
4. **Final headline:**
   - **MERGE GREEN** — all 4 branches (feat/orchestrator-mvp, feat/phase-b-prereqs, feat/events-schema-alignment, feat/mobile-shell) ready for main merge.
   - **MERGE HOLD** — what's missing.

**When done, Telegram:**
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-011 COMBINED QA" "<MERGE GREEN|HOLD>: <findings summary>. Vera MINORs <N/6 closed>."
```

The user (Inon) is away today. After your verdict, if MERGE GREEN, Andy will hand off to Inon (or schedule a Mack-led cherry-pick + push + PR open in a follow-up dispatch).

— Andy
