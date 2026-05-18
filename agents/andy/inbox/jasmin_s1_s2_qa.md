# Jasmin — QA Report: BUILDAR-S1-008/009 + S2-001/002

**From:** Jasmin (Reviewer — Security & Logic Auditor)
**To:** Andy (Orchestrator)
**Date:** 2026-05-17
**Repo:** `D:\BuildAR\`
**Branches reviewed:**
- Yoni: `feat/orchestrator-mvp` @ `bea4153` (S1-008 + S1-009)
- Silas: 2 migration files on disk (`0004_*.sql`, `0005_*.sql`) — branch ignored per brief

---

## TL;DR — Verdicts

| Task | Verdict | Headline |
|------|---------|----------|
| BUILDAR-S1-008 Orchestrator MVP (Yoni) | **PASS WITH NOTES** | 0 blockers. Both prior minor findings resolved at sessions+orchestrator boundary. Code, logic, and contracts are clean. |
| BUILDAR-S1-009 Telemetry wiring (Yoni) | **PASS WITH NOTES** | 0 blockers. Adapter is sound. `never-throws` contract honoured. |
| BUILDAR-S2-001 FK ON DELETE (Silas) | **PASS** | Static review clean. Idempotent. CASCADE choice on `events.user_id` accepted (see §5). |
| BUILDAR-S2-002 Storage bucket + RLS (Silas) | **PASS WITH NOTES** | Static review clean. Helper functions confirmed in 0001. One MINOR note re: SELECT policy posture. |

**Aggregate findings:** **0 BLOCKER**, **0 MAJOR**, **4 MINOR**, **2 NIT**.

**Wave 3 readiness:** **GREEN — green-light Yoni for mobile shell.** The schema adapter is a defensible stopgap; BUILDAR-S1-010 (events schema alignment) is **not a blocker** for the mobile shell and can ship in parallel.

**Deferred:**
- D1: Live Anthropic `/assist` curl — no `ANTHROPIC_API_KEY` available to me either. Documented; not blocking PR.
- D2: Behavioral RLS probes on Silas's storage policies — waiting for Inon to paste SQL into Supabase SQL Editor.

---

## 1. Gate-check reproduction (Yoni's branch)

Ran from `D:\BuildAR\` on `feat/orchestrator-mvp`:

| Step | Result |
|------|--------|
| `pnpm install` | ✅ clean (exit 0) |
| `pnpm -r lint` | ✅ all 7 workspaces clean |
| `pnpm -r typecheck` | ✅ strict, all 7 workspaces clean |
| `pnpm -r test` | ✅ **20/20 pass** (ai-client 6 + apps/api 14 = 20). Matches Yoni's report. |
| `buildApp()` boot probe | ✅ Fastify boots cleanly; all 5 routes (`/api/v1/health`, `/api/v1/projects`, `/api/v1/projects/:id`, `/api/v1/sessions` POST, `/api/v1/sessions/:id` PATCH, `/api/v1/orchestrator/assist` POST) register without error. |

No regression vs Yoni's done report. All gates green.

---

## 2. Section A.B — Security findings (Sprint 1)

### A.B.1 PostgREST `error.message` sanitization

Checked: `grep error.message D:\BuildAR\apps\api\src\` →
- `routes/sessions.ts:63, 153` — sanitized at boundary (returns generic `ERR.VALIDATION('Could not create/update session')`; upstream message kept in `req.log.error`). ✅
- `routes/orchestrator.ts:80, 96, 113` — sanitized; returns `ERR.INTERNAL()` with upstream logged. ✅
- `routes/projects.ts:31, 66, 82` — **STILL forwards `error.message` verbatim via `ERR.UPSTREAM(error.message)`.** ⚠️

**MINOR-1 (carry-over from S1-006 minor #1, partially unresolved):**
Yoni fixed the S1-009 changes (sessions + orchestrator) but did NOT touch `apps/api/src/routes/projects.ts` — the 3 upstream-error forwards at lines 31, 66, 82 are the same pattern I flagged in S1-006. Strictly speaking the S1-008/009 brief did not require Yoni to revisit `projects.ts`, so I'm tagging this MINOR (not MAJOR) and recommending Andy queue a one-line follow-up for Yoni: swap to `ERR.INTERNAL()` (or `ERR.UPSTREAM('Upstream unavailable')`) with the same `req.log.error` pattern already in place. Not a Wave 3 blocker.

### A.B.2 Service-role key isolation

`grep SUPABASE_SERVICE_ROLE_KEY D:\BuildAR\apps\api\src\` → **1 match, comment-only** at `supabase.ts:7` ("Never read SUPABASE_SERVICE_ROLE_KEY here…"). Zero route-handler matches. ✅ PASS.

### A.B.3 JWT handling in orchestrator route

`apps/api/src/routes/orchestrator.ts:61` — `const supabase = clientForRequest(jwt);` — every downstream `.from()` query and the `recordEvent` call at line 151 use this JWT-bound client. No service-role escalation. RLS context is honoured for the `events_insert_own` policy. ✅ PASS.

### A.B.4 Zod input validation on AssistRequest

`packages/validation/src/index.ts:155-159`:
```ts
export const AssistRequestSchema = z.object({
  session_id: Uuid,
  step_id: Uuid.nullable(),
  question: z.string().min(1, ...).max(2000, ...),
});
```
- `session_id`: UUID ✅
- `step_id`: UUID nullable ✅
- `question`: 1..2000 chars ✅
- **No client-injectable `user_id` field.** ✅
- Body parsed via `safeParse` at `routes/orchestrator.ts:53`. Extra props are stripped by Zod default (no `.strict()` but no leak either; orchestrator only destructures the three known fields). ✅

PASS.

### A.B.5 404-vs-403 convention

`routes/orchestrator.ts:84` — RLS-hidden session returns 404 (`ERR.NOT_FOUND('Session')`). Same at line 102 for projects. Same convention as S1-006 sessions routes. ✅ PASS.

### A.B.6 Prompt-injection surface

The user `question` is forwarded into both `buildSafetyContext()` (`ai-client/src/index.ts:166-173`) and `buildTutorContext()` (lines 238-254). It is concatenated into a string with labels like `"User question:\n" + input.question`.

Risk analysis:
- The 2000-char cap is enforced before the question reaches Anthropic — modest budget for an injection attempt.
- Both system prompts (Safety + Tutor) are constrained and clear. Safety system prompt explicitly says "JSON only" and lists block-worthy intents. Tutor is told "Never invent steps that are not in the project's step list."
- The Safety output parser (`parseSafetyJson`) defaults to `block` on unparseable verdicts (verified — see A.B.7 below). So an injection that tries to force a "proceed" verdict on a genuinely dangerous question would have to (a) produce well-formed JSON AND (b) pass through Safety's instruction-following — non-trivial.
- However, there is **no input sanitization** on `question` — newlines, backticks, and "```json"-style fences can be embedded. A determined attacker could try to spoof a fake "Safety verdict" inside the user content. The current parser only reads the model's response, not the user's input, so this is limited — but it's worth a doc note.

**NIT-1:** Consider adding a one-line comment in `orchestrator.ts` or in `buildSafetyContext` noting that the 2000-char cap is the only injection mitigation and that the Safety system prompt's instruction-following is the actual safety boundary. No code change required.

### A.B.7 Safety agent JSON parser defensiveness

`packages/ai-client/src/index.ts:175-209` `parseSafetyJson`:
- Strips ```json/``` fences and whitespace before parsing. ✅
- Try/catch around `JSON.parse` → returns `{verdict:'block', reason:'Safety check could not be parsed…'}` on failure. ✅ (fail-safe — never silently `proceed`)
- Validates `verdict` is exactly one of the three allowed enums AND `reason` is a string. Otherwise → `block`. ✅
- Missing `reason` → `block`. ✅
- Unit test coverage at `packages/ai-client/src/__tests__/safety_parse.test.ts` exercises all 6 paths (well-formed proceed, well-formed block, code-fenced, unparseable, invalid verdict, missing reason). All 6 pass. ✅

PASS. Defensive parser is correct and well-tested.

---

## 3. Section C — Logic + contract findings (Sprint 1)

### C.1 Telemetry call sites

Verified 5 `recordEvent` call sites:

| File:line | event_type | Trigger |
|-----------|------------|---------|
| `routes/sessions.ts:70` | `session_started` | Successful POST /sessions |
| `routes/sessions.ts:184` | `session_resumed` | PATCH status: !active → active |
| `routes/sessions.ts:195` | `session_completed` | PATCH status: → completed |
| `routes/sessions.ts:212` | `step_completed` | PATCH current_step_index advanced (next > prev) — for the PREVIOUS step |
| `routes/sessions.ts:222` | `step_viewed` | PATCH current_step_index changed (any direction) — for the NEW step |
| `routes/orchestrator.ts:151` | `assistant_invoked` | After assistFn returns (block AND proceed paths both record) |

The brief asked for "5 recordEvent call sites" but I count **6** (5 in sessions.ts + 1 in orchestrator.ts) — one extra because sessions PATCH advance emits both `step_completed` AND `step_viewed`. This matches the test assertions in `sessions_telemetry.test.ts:209`. ✅ PASS.

### C.2 Schema adapter integrity

`packages/utils/src/events.ts` — read end to end. Adapter mappings:

| Brief input | Adapter behaviour |
|-------------|-------------------|
| `event_type='session_resumed'` | → DB `step_viewed` + `metadata.resumed=true` ✅ |
| `project_id` (uuid) | → `metadata.project_id` (only if non-null) ✅ |
| `step_id` (uuid) | → `metadata.step_id` (only if non-null); caller may pre-resolve `step_index` ✅ |
| `payload` jsonb | → DB `metadata` jsonb (spread) ✅ |
| `session_id === null` | → log + drop (events.session_id NOT NULL would otherwise PostgREST 23502) ✅ |

Public signature preserved. When Silas ships BUILDAR-S1-010 (the schema alignment migration), the adapter can be simplified without changing the call-site API.

**MINOR-2:** The `step_index` in `RecordEventInput` is optional (`step_index?: number | null`) but several call sites resolve the UUID → index manually and pass it in (e.g. `orchestrator.ts:157` passes `resolvedStepIndex`). Other call sites (sessions PATCH) pass `next.current_step_index` directly. The behaviour is correct in all 6 sites I checked, but the contract is a little surprising — caller has to know to pre-resolve. Acceptable as-is; once BUILDAR-S1-010 lands and `step_id` becomes a real DB column, this can drop entirely.

**NIT-2:** The dropped-event console.warn at `events.ts:73` is well-intentioned, but if a future caller wants to record genuine top-of-funnel events (e.g. landing-page view before any session exists), this becomes silent data loss. Acceptable since the brief doesn't require it; flag for re-evaluation when 0006 lands.

### C.3 `recordEvent` never-throws contract

Verified at `packages/utils/src/events.ts:105-123` — full try/catch around the supabase insert. Both the `error` field path (`if (error) console.warn(...)`) and the throw path (`catch (err) { console.warn(...) }`) return void cleanly. No re-throw. ✅ PASS.

Cross-checked at call sites: every `await recordEvent(...)` is fire-and-forget — return value is `void`, not checked. ✅

### C.4 Type-parity assertions

`apps/api/src/__tests__/smoke.test.ts:96-117` — `AssertExtends<A, B>` is the bidirectional type-equality trick. Compile-time, NOT runtime. Confirmed:
- `_AssistReqEq = AssertExtends<AssistRequest, z.infer<typeof AssistRequestSchema>>` ✅
- `_AssistResEq = AssertExtends<AssistResponse, z.infer<typeof AssistResponseSchema>>` ✅
- Drift between `core-types` and Zod schemas would resolve `AssertExtends` to `never`, failing `tsc -p` at compile time. ✅
- Verified empirically: `pnpm -r typecheck` passes with the assertions in place.

PASS. Both my prior S1-006 MINOR-2 items are now resolved.

### C.5 Prompt caching

`packages/ai-client/src/index.ts`:
- Safety system block at line 220-224: `cache_control: { type: 'ephemeral' }` ✅
- Tutor system block at line 265-269: `cache_control: { type: 'ephemeral' }` ✅
- No third block (the user message is per-call by design — caching wouldn't help).

PASS. Per the Perplexity plan's cost-control requirement.

---

## 4. Section D — Live Anthropic curl (DEFERRED)

I do not have `ANTHROPIC_API_KEY` in my environment either. The deferred item passes through to Inon:

**Action for Inon:** drop a personal `ANTHROPIC_API_KEY` into `D:\BuildAR\.env` (gitignored). Then re-run the curl from Yoni's done-report § "Manual live test", and confirm:
1. 200 response shaped to `AssistResponse`
2. Exactly one `assistant_invoked` row inserted into `public.events` for the session.

Once that is green, Andy can mark D1 closed. Not a Wave 3 blocker.

---

## 5. Phase B — Static SQL review

### 5.1 Migration 0004 (FK ON DELETE)

**Verdict: PASS.**

Checks:
1. **Idempotent** — `DROP CONSTRAINT IF EXISTS` then `ADD CONSTRAINT`. ✅
2. **BEGIN/COMMIT wrap** — present at lines 33 + 88. ✅
3. **Overlap with 0003** — confirmed by reading `0003_security_fixes.sql:73-103`. Fixes 3 + 4 in 0003 already ship the same two FK changes. Re-running 0004 on top of 0003 is a no-op that reaffirms intent. ✅ Accepted as documented audit-trail redundancy.
4. **No collateral damage** — only `projects_published_by_fkey` and `events_user_id_fkey` are touched. No table/column adds, no other policy edits. ✅

### 5.2 CASCADE-vs-SET-NULL on `events.user_id`

**I accept Silas's CASCADE choice. Re-raise: NO.**

Silas's three reasons are valid and ranked correctly:
1. `events.user_id` is `NOT NULL` in `0001_schema_init.sql`. SET NULL would force dropping that constraint, weakening insert-time integrity for live writes. **This is the dealbreaker.** I missed this in my original S1-006 audit because I was thinking GDPR-deletion in isolation, not the schema constraint.
2. GDPR right-to-erasure on a personal-activity log: CASCADE is the cleaner story. Pseudonymized events still count as personal data when joinable.
3. Anonymized analytics belong in a separate `analytics_*` table populated by a scheduled job, NOT as orphaned rows mixed into the live behavioural log. Agree.

If product later needs retained anonymized aggregates, the right answer is a new analytics table + scheduled rollup — not relaxing the events FK. Closing the SET-NULL recommendation as superseded.

### 5.3 Migration 0005 (storage bucket + RLS)

**Verdict: PASS WITH NOTES.**

Checks:
1. **Bucket privacy** — `INSERT INTO storage.buckets (id, name, public) VALUES ('project-assets', 'project-assets', false)` at line 45. `public=false` confirmed. ✅
2. **Idempotency** — `ON CONFLICT (id) DO NOTHING` on the bucket; `DROP POLICY IF EXISTS` before each CREATE. ✅
3. **Helper functions exist** — `grep is_admin\|is_creator_or_admin D:\BuildAR\supabase\migrations\` confirms both functions are defined in `0001_schema_init.sql:40` (`is_admin`) and `:45` (`is_creator_or_admin`). Both are `STABLE SECURITY DEFINER SET search_path = public` and call `has_role()` against `public.profiles`. 0005 will apply cleanly. ✅
4. **Policy expressions** — all 4 policies correctly scope to `bucket_id = 'project-assets'` AND apply the right role gate (INSERT: creator-or-admin; SELECT: any authenticated; UPDATE: admin USING + WITH CHECK; DELETE: admin). ✅
5. **`TO authenticated`** — every policy includes the role qualifier. Anonymous traffic is blocked by default (no policy matches). ✅
6. **Role source via `public.profiles` (not `auth.jwt() user_metadata`)** — agree with Silas. `user_metadata` is user-mutable in Supabase default config (the `updateUser({ data: ... })` API path); `profiles.role` is the single source of truth used by every other RLS policy. Keep it. ✅
7. **No collateral schema damage** — only `storage.buckets` and 4 named `storage.objects` policies under the `project_assets_*` prefix. No other touches. ✅

**MINOR-3 (Silas open question #2 — path-segment validation):**
Silas's RLS deliberately does NOT validate that the storage path's first segment matches a `project_id` the uploader owns. The `{project_id}/{asset_filename}` convention is enforced only at the application layer. Posture I'd recommend:
- Acceptable for Phase B (mobile shell) — keeps the policy small and avoids entangling storage RLS with `public.projects` joins.
- BUT: when the Lovable CMS lands and creators upload directly through it (bypassing the API), the application-layer enforcement is no longer a single chokepoint. At that point, a defense-in-depth policy that checks `split_part(name, '/', 1)::uuid IN (SELECT id FROM public.projects WHERE published_by = auth.uid())` is worth adding.
- File this as a follow-up under "Lovable CMS hardening", not a blocker.

**MINOR-4 (SELECT-any-authenticated posture):**
Currently any authenticated user can SELECT any object in `project-assets` (subject to the bucket being private, so they'd still need a signed URL or session). For a published catalog this is fine. But if a creator uploads a DRAFT-project asset, any authenticated user can read it given the storage path. The brief explicitly opts for "any authenticated" for the mobile-shell case; flagging this so it's an explicit decision rather than an oversight. If draft-asset privacy is desired, a future policy can join through `public.projects` on the path segment (overlaps with MINOR-3's fix).

---

## 6. Schema adapter — Wave 3 readiness verdict

**Verdict: SCHEMA ADAPTER ACCEPTED AS A STOPGAP. Wave 3 (mobile shell) is GREEN.**

Reasoning:
- The adapter at `packages/utils/src/events.ts` cleanly preserves the public `recordEvent` signature.
- `step_id` UUIDs are still recorded in `metadata.step_id`, so no data is lost — only analytics ergonomics suffer.
- The `session_resumed → step_viewed + metadata.resumed=true` fold is recoverable; analytics queries against `metadata->>'resumed'` will work.
- When BUILDAR-S1-010 lands (the migration Yoni proposed), the adapter becomes a 5-line passthrough. Zero API caller changes.

BUILDAR-S1-010 should be queued behind Wave 3, **not** ahead of it. The mobile shell does not exercise events analytics — it only needs the orchestrator's `/assist` endpoint and session lifecycle, both of which work today via the adapter.

If product wants clean analytics SQL before launch, ship S1-010 in parallel with the mobile shell (Silas + Jasmin sequential; Yoni unblocked).

---

## 7. Findings summary (severity matrix)

| # | Severity | Area | Summary | Action |
|---|----------|------|---------|--------|
| MINOR-1 | MINOR | Sec | `routes/projects.ts:31,66,82` still forward upstream `error.message` verbatim — carry-over from S1-006 minor #1; Yoni only fixed sessions+orchestrator | Queue 1-line follow-up for Yoni; not Wave 3 blocker |
| MINOR-2 | MINOR | Logic | `recordEvent` `step_index` contract is split (caller must sometimes pre-resolve UUID → index) | Acceptable until S1-010; auto-resolves then |
| MINOR-3 | MINOR | Sec/DB | 0005 storage RLS does not validate `{project_id}/` path segment | Acceptable for Phase B; revisit when Lovable CMS lands |
| MINOR-4 | MINOR | Sec/DB | 0005 SELECT policy allows any authenticated to read DRAFT-project assets | Decision flag — accept or tighten in follow-up |
| NIT-1 | NIT | Sec | No code comment noting that 2000-char `question` cap is the only injection mitigation | Doc-only; optional |
| NIT-2 | NIT | Logic | Top-of-funnel events with `session_id=null` are silently dropped | Re-evaluate after S1-010 |

**Totals: 0 BLOCKER, 0 MAJOR, 4 MINOR, 2 NIT.**

---

## 8. Recommendations for Andy

1. **Green-light Yoni for Wave 3 (mobile shell).** No blockers, no majors. The schema adapter is a defensible stopgap.
2. **Queue BUILDAR-S1-010 (events schema alignment) → Silas → Jasmin QA.** Sequential, not in parallel with the mobile shell. Can run any time before launch — ideally before analytics ship.
3. **Queue MINOR-1 fix (projects.ts error sanitization) as a one-line follow-up to Yoni.** Same pattern as the sessions.ts fix already done.
4. **Surface Silas's 2 SQL blocks to Inon via Telegram** (per Silas's done-report § 8). Once Inon confirms applied + verification queries match, dispatch me again for behavioral RLS probes (D2).
5. **Ask Mack to provision `ANTHROPIC_API_KEY` in `D:\BuildAR\.env`** so D1 (live curl) can close.
6. **Note for the parallel-agent memory rule:** Silas's `feat/phase-b-prereqs` branch picked up Yoni's S1-006 baseline commit (`54c7863`). For the PR strategy, cherry-pick `0004_*.sql` and `0005_*.sql` into a clean branch off `main`. Migration files on disk are correct and verified.

---

## 9. Sign-off

- BUILDAR-S1-008: **PASS WITH NOTES**
- BUILDAR-S1-009: **PASS WITH NOTES**
- BUILDAR-S2-001: **PASS**
- BUILDAR-S2-002: **PASS WITH NOTES**

**Wave 3 readiness: GREEN.**

Code is ready for merge into `main` after the MINOR-1 one-line follow-up; both migrations are ready for Inon to paste into the Supabase SQL Editor.

— Jasmin
