# Jasmin — BuildAR Pro Sprint 1 + Phase B QA

**From:** Andy
**Dispatched:** 2026-05-17
**Tasks to QA:**
- BUILDAR-S1-008 (Yoni — Orchestrator MVP)
- BUILDAR-S1-009 (Yoni — Telemetry wiring)
- BUILDAR-S2-001 (Silas — FK ON DELETE migration 0004) — **static SQL review only**, behavioral probes pending Inon paste
- BUILDAR-S2-002 (Silas — Storage bucket migration 0005) — **static SQL review only**, behavioral probes pending Inon paste

**Inputs:**
- Yoni's done-report: `D:\Claude Playground\agents\andy\inbox\yoni_s1_008_009_done.md`
- Yoni's schema request: `D:\Claude Playground\agents\yoni\scratchpad\schema_request.md`
- Silas's done-report: `D:\Claude Playground\agents\andy\inbox\silas_phase_b_done.md`
- Yoni's branch: `feat/orchestrator-mvp` in `D:\BuildAR\` (NOT pushed)
- Silas's branch: `feat/phase-b-prereqs` in `D:\BuildAR\` — **WARNING: polluted with Yoni's S1-006 baseline commit** (concurrent agent in same repo). The 2 migration files (`0004_*.sql`, `0005_*.sql`) are correct on disk; ignore the unrelated S1-006 chore commit when reviewing.

---

## Why you, and what changed from S1-006

You already QA'd Yoni's S1-006 (PASS WITH NOTES — 0 blockers, 0 majors, 2 minors, 1 nit). This wave addresses both your minor findings:
- Minor #1 (PostgREST error.message verbatim forward) — Yoni now sanitizes at the API boundary. Verify in `apps/api/src/routes/sessions.ts` + `apps/api/src/routes/orchestrator.ts`.
- Minor #2 (missing type-parity assertions) — Yoni added assertions in `apps/api/src/__tests__/smoke.test.ts` for AssistRequest + AssistResponse.

---

## Sprint 1 (Yoni) — QA scope

**Repository to QA:** `D:\BuildAR\` on branch `feat/orchestrator-mvp`.

### A. Reproduce gate checks

Run from `D:\BuildAR\`:
1. `pnpm install` — should be clean.
2. `pnpm -r lint` — should pass.
3. `pnpm -r typecheck` — should pass (strict, no `any`, no `@ts-ignore`).
4. `pnpm -r test` — should report 20/20 pass.
5. `pnpm --filter @buildar/api dev` (or whatever Yoni's boot script is — check apps/api/package.json) — should boot clean, log "Server listening at http://0.0.0.0:3010" (port may vary).

If ANY of these regress vs Yoni's report, that's a blocker — flag in your QA report.

### B. Security review (your specialty)

1. **PostgREST error sanitization** — grep for `error.message` in `apps/api/src/`. Confirm no upstream Supabase/PostgREST error strings are returned to the API caller. Errors should resolve to `ERR.INTERNAL()` or equivalent generic message, with the upstream message logged via `req.log.error`.
2. **Service-role key isolation** — grep for `SUPABASE_SERVICE_ROLE_KEY` in `apps/api/src/`. Should be ZERO matches in route handlers — only used in infra/seed scripts if at all.
3. **JWT handling in orchestrator route** — confirm `recordEvent` uses the per-request JWT-bound Supabase client (NOT a service-role client). The user's RLS context must be honored.
4. **Zod input validation** — verify schema in `packages/validation/src/index.ts` for AssistRequest: session_id is uuid, step_id is uuid|null, question is string max 2000. No client-injectable user_id field.
5. **404 vs 403 convention** — confirm the orchestrator route returns 404 (not 403) when session is owned by a different user — same convention as Yoni's S1-006 sessions routes.
6. **Prompt-injection surface** — the user-provided `question` field gets forwarded to Anthropic via Tutor agent. The Tutor system prompt should constrain behavior, but the brief did not require input sanitization on the `question` itself. Flag if you think a length cap (already at 2000) is insufficient or if escape sequences need stripping.
7. **Safety agent JSON parsing** — verify `packages/ai-client/src/agents/safety.ts` parses Safety output defensively. If Anthropic returns malformed JSON, the route should fail safely (probably default to `block` or surface a clear error, not crash).

### C. Logic + contract review

1. **Telemetry: events table writes** — verify the 5 `recordEvent` call sites in `apps/api/src/routes/sessions.ts` + `orchestrator.ts`. Each call should pass the correct `event_type` for the lifecycle transition.
2. **Schema adapter** — Yoni's `packages/utils/src/events.ts` adapts the brief's signature to the live DB schema (events table is missing `project_id`/`step_id`/`payload`/`session_resumed`). Read his adapter logic + verify it preserves the public API while writing into the existing `metadata` jsonb column without data loss.
3. **`recordEvent` never-throws contract** — verify telemetry failures do NOT break the parent request. The brief was explicit: telemetry must never break user flows.
4. **Type-parity assertions** — confirm new assertions in `apps/api/src/__tests__/smoke.test.ts` actually compile-time-fail if AssistRequest/AssistResponse drift between core-types and the route handler.
5. **Prompt caching** — verify `cache_control: { type: "ephemeral" }` is set on system + tutor + safety blocks in `packages/ai-client/src/index.ts`. This was a Perplexity-plan cost-control requirement.

### D. Deferred live test

Yoni could not run the live Anthropic curl (no `ANTHROPIC_API_KEY` in his environment). You ALSO will not have a key — that's an Inon-action item. Document this as `DEFERRED — pending Inon to drop ANTHROPIC_API_KEY in D:\BuildAR\.env` in your QA verdict; do not block the PR on it.

If you DO have a key in your env, run the curl Yoni described in his report § "Manual live test" and capture the transcript.

---

## Phase B (Silas) — Static SQL review

**Files:**
- `D:\BuildAR\supabase\migrations\0004_fk_ondelete_clauses.sql`
- `D:\BuildAR\supabase\migrations\0005_storage_bucket_project_assets.sql`

### Review checklist

1. **0004 is idempotent** — `DROP CONSTRAINT IF EXISTS` then `ADD CONSTRAINT`. Confirm BEGIN/COMMIT wraps the alter.
2. **0004 vs 0003 overlap** — Silas noted that 0003 (already applied 2026-05-16) already shipped these same FK changes. Confirm 0004 is a safe no-op if 0003 is live. (Acceptable redundancy for migration audit-trail.)
3. **events.user_id CASCADE choice** — Silas chose CASCADE; your original recommendation was SET NULL. Silas's argument: events.user_id is NOT NULL in 0001 schema (SET NULL would force dropping NOT NULL), and GDPR right-to-erasure favors CASCADE. Decide: do you accept his reasoning or do you re-raise SET NULL? If you re-raise, flag MAJOR and propose the resolution (e.g., move analytics to a separate table).
4. **0005 bucket is private** — `public: false` for the bucket. Yes/no.
5. **0005 RLS policies** — 4 policies, scoped to `bucket_id = 'project-assets'`:
   - INSERT: `is_creator_or_admin()` (helper function from prior migration)
   - SELECT: any authenticated
   - UPDATE: `is_admin()` only
   - DELETE: `is_admin()` only
   Are the policy expressions correct? Are the helper functions (`is_creator_or_admin`, `is_admin`) confirmed to exist in 0001 or 0003? (If not, 0005 will fail to apply.)
6. **Role source** — Silas reads role from `public.profiles` via helper functions, not from `auth.jwt() -> user_metadata`. His argument: `user_metadata` is user-mutable; `profiles.role` is single source of truth used by all other RLS. Validate.
7. **No collateral schema damage** — confirm 0004 and 0005 touch ONLY the constraints/bucket/policies they claim. No table drops, no policy edits outside `project_assets_*` scope.

### Behavioral QA (DEFERRED until Inon pastes SQL in Supabase Dashboard)

Once Inon confirms the SQL is applied:
- Delete a throwaway profile → confirm dependent project survives with `published_by = NULL`, dependent events rows are CASCADE-deleted.
- Insert into `storage.objects` for `project-assets` as a `user`-role JWT → denied.
- Same insert as a `creator` JWT → allowed.
- Delete as a non-admin → denied.

Do NOT run behavioral probes against the live DB right now — wait for Inon's paste confirmation. Andy will queue you again for this.

---

## Schema-delta context (informational, not in your QA scope)

Yoni flagged a separate request at `agents/yoni/scratchpad/schema_request.md` — proposed `0006_events_schema_alignment.sql` to add `project_id`/`step_id`/`payload` columns + `session_resumed` enum value. This is NOT something you QA in this round; Andy is queueing it as a fresh task (BUILDAR-S1-010 → Silas → you for QA later, sequentially).

---

## Branch hygiene flag (informational)

Silas's branch `feat/phase-b-prereqs` is polluted with Yoni's S1-006 baseline commit. This was a concurrent-agent incident in the same repo (memory: `feedback_parallel_agents_shared_repo`). The 2 migration files are correct on disk; PR strategy is cherry-pick into a clean branch off main. Don't let this confuse the SQL review — focus on the 2 migration files themselves.

---

## Definition of done (your QA)

1. All Sprint 1 gate checks reproduced (or deviations reported).
2. Security review notes per A.B.C.D above, with severity (BLOCKER / MAJOR / MINOR / NIT) per finding.
3. Static SQL review for both Silas migrations with PASS / PASS WITH NOTES / FAIL verdict per migration.
4. Independent verdict: do you accept the schema adapter as a stopgap, or is BUILDAR-S1-010 a blocker for Wave 3 (mobile shell)?
5. Independent verdict on Silas's CASCADE-vs-SET-NULL choice.
6. Report destination: `D:\Claude Playground\agents\andy\inbox\jasmin_s1_s2_qa.md`

When done, send Telegram:
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-008+009+S2-001+002 QA" "<one-line verdict + count of findings by severity>"
```

— Andy
