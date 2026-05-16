# Jasmin QA — BUILDAR-S1-006 (Yoni's API)
**Date:** 2026-05-16
**Tester:** Jasmin (Security & Logic Auditor)
**Scope:** `D:\BuildAR\apps\api\src\**`, `packages/core-types`, `packages/validation`
**Verdict:** **PASS WITH NOTES**

Independent verification per Rubric #4. Yoni's claims in `yoni_s1_006_done.md` cross-checked against code, DDL, runtime probes.

---

## Security

### 1. Service role key isolation — PASS
Grep across `apps/api/src/` for `service_role|SERVICE_ROLE|serviceRole` returned exactly **one** match:

```
D:\BuildAR\apps\api\src\supabase.ts:7: * IMPORTANT: Never read SUPABASE_SERVICE_ROLE_KEY here. Service role bypasses
```

That match is the warning comment in `readSupabaseEnv()`. No actual import, no `env.SUPABASE_SERVICE_ROLE_KEY` read, no privileged client construction anywhere in user-facing code. `packages/*` also clean (zero matches). **Not a blocker, working as designed.**

### 2. JWT handling — PASS
Tracing `bearerFromHeader` (`supabase.ts:47-51`):

```ts
const match = /^Bearer\s+(.+)$/i.exec(header.trim());
return match ? match[1] : null;
```

- Missing header (`undefined`) → returns `null` → routes return 401. Probed live: `POST /sessions` no auth → `401 unauthorized`.
- Malformed header (`NotBearer xyz`) → regex misses → returns `null` → 401. Probed: confirmed 401 returned, no parser exception.
- Expired/tampered JWT → forwarded as Bearer to Supabase. `supabase.auth.getUser(jwt)` (sessions.ts:41) returns `userErr` → route responds 401. The API never trusts the JWT payload itself; validation is delegated to Supabase. No JWT decoding bypass anywhere.

### 3. RLS pass-through — PASS
- `routes/projects.ts:19-20` — `const jwt = bearerFromHeader(...); const supabase = clientForRequest(jwt);` — passes whatever JWT exists (or null for anon). `clientForRequest(null)` uses anon key with no Authorization header → RLS treats caller as `anon` role → policy `projects_read_published` allows only `status='published'`. Same pattern in `projects/:id` handler (line 51-52).
- `routes/sessions.ts:38` — uses `clientForRequest(jwt)` (jwt guaranteed non-null after the 401 gate). RLS policies `sessions_insert_own`, `sessions_update_own` enforce `auth.uid() = user_id`.
- No code path constructs a service-role client or bypasses RLS. Verified.

### 4. Zod request validation — PASS
`CreateSessionBodySchema = z.object({ project_id: Uuid })`. Default Zod behavior strips unknown keys (not `.strict()`, not `.passthrough()`). Confirmed at runtime via `tsx` probe in the API workspace:

```
Input:  { project_id: '00000000-...0001', user_id: 'attacker-uuid', status: 'completed' }
Parsed: {"project_id":"00000000-0000-0000-0000-000000000001"}
user_id present? false
status present? false
```

Even if the client injects `user_id`, the field is dropped before reaching the insert. The insert (`sessions.ts:46-55`) then writes `user_id: userRes.user.id` (from `getUser(jwt)`), never from the body. **Defense in depth: Zod strip + server-resolved uid + RLS `WITH CHECK (auth.uid() = user_id)`. Yoni's claim is correct.**

Live probe with `user_id` injection got 401 (stub Supabase rejects `getUser`) before reaching insert, which is the correct gate order.

### 5. Error response shape & info leakage — PASS WITH NOTES
Standard envelope `{error:{code,message}}` is used by:
- `errors.ts` ERR factory (all five codes use `errorBody()`)
- Global `setErrorHandler` (app.ts:24-30) — Fastify 400/500 wrapped in the same envelope
- `setNotFoundHandler` (app.ts:32-34) — same envelope for unknown routes (probed `GET /nope` → `{"error":{"code":"not_found","message":"Route not found"}}`)

What's surfaced in `message`:
- JSON parse error: `"Unexpected token 'o', \"not json\" is not valid JSON"` — leaks parser type, but reflects user input only. Acceptable.
- Upstream error (no Supabase reachable): `"TypeError: fetch failed"` — leaks the JS error **class name** but no stack, no schema, no Postgres code. **MINOR**: when a real PostgREST error bubbles up via `error.message`, it can contain hints like column names or constraint names. The current code passes `error.message` straight through `ERR.UPSTREAM(error.message)`. Suggest sanitizing PostgREST errors to a generic `"Database query failed"` and logging the full error server-side only. Not a blocker — DB shape is already in `core-types`/`validation` so leakage is low-impact for now.

No stack traces ever leave the process. `req.log.error({err}, ...)` keeps the structured detail server-side. Good.

### 6. 404-not-403 on RLS-hidden rows — PASS
`projects.ts:56-69` — `.maybeSingle()` returns `data: null, error: null` when RLS hides the row. Code path: `if (!project) return reply.code(404).send(ERR.NOT_FOUND('Project'))`. Same pattern in `sessions.ts:97-107` for PATCH. **No 403 anywhere in the codebase** — verified by grep. Anonymous probes for guessed draft UUIDs get 404 indistinguishable from "doesn't exist". Yoni's claim verified.

---

## Schema alignment

### 7. Yoni's schema delta claims — verified against `0001_schema_init.sql`

| Delta | Yoni's claim | DDL reality | Verdict |
|---|---|---|---|
| `Project.published_at` | not in DDL | line 100-113: only `published_by`, `created_at`, `updated_at` | **VERIFIED — Yoni right** |
| `ProjectStep.body` | not in DDL | line 151-162: has `description` not `body` | **VERIFIED — Yoni right** |
| `ProjectStep.asset_ids` | not in DDL | line 151-162: no `asset_ids` column; assets join via `assets.step_id` FK (line 197) | **VERIFIED — Yoni right** |
| `Asset.kind` | not in DDL | line 194-202: has `mime_type` not `kind` | **VERIFIED — Yoni right** |
| `Asset.alt_text` | not in DDL | line 194-202: has `label` not `alt_text` | **VERIFIED — Yoni right** |
| `Asset.created_by` | not in DDL | line 194-202: no `created_by` column at all | **VERIFIED — Yoni right** |
| `Session.status='in_progress'` | DDL uses different value | line 241: `CHECK (status IN ('active','completed','abandoned'))` | **VERIFIED — Yoni right; API correctly writes `'active'`** |
| `ProjectStatus='archived'` | not in DDL enum | line 109: `CHECK (status IN ('draft','published'))` | **VERIFIED — Yoni right** |

**8/8 of Yoni's delta claims verified against the DDL.** Types and Zod schemas correctly mirror the *live DDL*, not the *task brief*. This is the right call per the "match Silas's schema exactly, don't invent columns" rule.

### 8. Zod ↔ TS type equality assertion — PASS
The assertion lives in `apps/api/src/__tests__/smoke.test.ts:87-104`, not at the bottom of `packages/validation/src/index.ts`. The mechanism is sound:

```ts
type AssertExtends<A, B> = A extends B ? (B extends A ? true : never) : never;
type _ProfileEq = AssertExtends<Profile, z.infer<typeof ProfileSchema>>;
type _ProjectEq = AssertExtends<Project, z.infer<typeof ProjectSchema>>;
type _SessionEq = AssertExtends<Session, z.infer<typeof SessionSchema>>;
type _CreateBodyEq = AssertExtends<{project_id: string}, z.infer<typeof CreateSessionBodySchema>>;
```

If a `core-types` field drifts from its Zod counterpart, the `_checks` tuple fails to construct → typecheck fails → CI red. Equivalent guarantee to bottoming the assertions in `packages/validation`. **NIT**: the test only asserts `Profile`, `Project`, `Session`, `CreateSessionBody`. Missing equivalent assertions for `ProjectStep`, `Asset`, `Event`, `ProjectWithSteps`, `UpdateSessionBody`. Drift in those four would not be caught. Suggest adding them — five lines of TypeScript, zero runtime cost.

---

## Functional

### 9. Smoke test — PASS (5/5)
```
$ pnpm --filter @buildar/api test
 RUN  v1.6.1 D:/BuildAR/apps/api
 ✓ src/__tests__/smoke.test.ts  (5 tests) 40ms
 Test Files  1 passed (1)
      Tests  5 passed (5)
   Duration  912ms
```

### 10. Server boot — PASS
Booted with stubbed env (`SUPABASE_URL=http://stub.local`, `SUPABASE_ANON_KEY=stub-anon-key`):

```
$ curl -i http://127.0.0.1:3001/api/v1/health
HTTP/1.1 200 OK
content-type: application/json; charset=utf-8
{"status":"ok"}
```

Killed after probes complete; port 3001 confirmed DOWN.

### 11. Anon probe of `/api/v1/projects` — PASS (with stub caveat)
With stub Supabase URL, the anon list call routes through `clientForRequest(null)` correctly (no Authorization header forwarded), and the failure surfaces as `502 {"error":{"code":"upstream_error","message":"TypeError: fetch failed"}}` — meaning the code path executes RLS-bound, then fails only at network. Auth behavior matches Yoni's claim: anon-allowed (no 401 gate), would return published rows against a real Supabase. Cannot fully verify the "200 with only published rows" behavior without live anon creds — that's an integration test, not the unit-level scope of this QA. Code path is correct.

Other live probes (raw output):
- `POST /sessions` no auth → `401 unauthorized` ✓
- `POST /sessions` malformed Authorization (`NotBearer xyz`) → `401 unauthorized` ✓ (regex correctly rejects)
- `POST /sessions` invalid JSON body → `400 validation_error` via global handler ✓
- `POST /sessions` non-UUID `project_id` → `400 validation_error "Invalid uuid"` ✓
- `GET /nope` → `404 {"error":{"code":"not_found","message":"Route not found"}}` ✓

---

## Findings

### BLOCKER — 0
None.

### MAJOR — 0
None.

### MINOR — 2
1. **Upstream error messages forward `error.message` verbatim.** `routes/projects.ts:31, 67, 82` and `routes/sessions.ts:60, 101` all do `ERR.UPSTREAM(error.message)`. When Supabase returns a PostgREST error, the message can include constraint names, column names, or hint text. Suggest mapping known Supabase error codes to generic messages and logging the raw `error` server-side (already done via `req.log.error`). Defer to Phase B if no immediate exposure risk.
2. **Type-parity assertion is incomplete.** `smoke.test.ts` asserts `Profile`, `Project`, `Session`, `CreateSessionBody`. Missing: `ProjectStep`, `Asset`, `Event`, `ProjectWithSteps`, `UpdateSessionBody`. Drift in any of those would not break CI. Five-line fix.

### NIT — 1
1. **Comment drift in `sessions.ts:71-73`** — comment says "we don't need to add an explicit user_id filter — but we do anyway as defense in depth" — but the code does **not** add an `.eq('user_id', uid)` filter. Either add the belt-and-suspenders filter or fix the comment to reflect that RLS is the sole gate. Cosmetic.

---

## Sign-off

**Verdict: PASS WITH NOTES.** All 5 success criteria met. No blockers, no majors, no security defects. Two minor improvements logged for Phase B / follow-up. One nit (comment-vs-code drift) for Yoni to fix at his discretion — does not block Done.

**Moving BUILDAR-S1-006 to Done with `tested_by: Jasmin`.** Gate A closed pending Silas's 0003 apply (BUILDAR-S1-007, blocked on credentials — separate task).

---

## Schema reconciliation recommendations for Silas

Yoni's deltas are real. The task brief's expected schema diverges from the live DDL in 8 places. **Recommendation:** do NOT reconcile by adding the brief-side columns/values unless a downstream feature actually needs them. The current types/API are correct against the live DDL. If a Phase B feature (e.g. archival, asset metadata UX, "in_progress" UX state) does need them, draft these into `0004_brief_alignment.sql`:

```sql
-- Only apply if Phase B requirements force it. Otherwise leave the schema lean.

-- 1. Project archival (if needed by the publishing workflow)
ALTER TABLE public.projects
  DROP CONSTRAINT IF EXISTS projects_status_check;
ALTER TABLE public.projects
  ADD CONSTRAINT projects_status_check
  CHECK (status IN ('draft', 'published', 'archived'));

-- 2. Project publish timestamp (if needed by sorting/UI)
ALTER TABLE public.projects
  ADD COLUMN IF NOT EXISTS published_at timestamptz;

-- 3. Step richer body content (if the AR step needs structured body beyond description)
ALTER TABLE public.project_steps
  ADD COLUMN IF NOT EXISTS body jsonb;
-- 'asset_ids' on the steps table is NOT recommended — the existing
-- assets.step_id FK is the right shape. Don't denormalize.

-- 4. Asset metadata (if accessibility UX or admin attribution is needed)
ALTER TABLE public.assets
  ADD COLUMN IF NOT EXISTS kind text,
  ADD COLUMN IF NOT EXISTS alt_text text,
  ADD COLUMN IF NOT EXISTS created_by uuid REFERENCES public.profiles(id);
-- If 'kind' is added, decide whether it's free-text or a CHECK enum
-- ('image' | 'model_3d' | 'video' | 'marker'). Coordinate with Yoni
-- so a matching Zod enum can be added.

-- 5. Session intermediate state (if UX distinguishes "active but paused" vs "actively in-progress")
ALTER TABLE public.sessions
  DROP CONSTRAINT IF EXISTS sessions_status_check;
ALTER TABLE public.sessions
  ADD CONSTRAINT sessions_status_check
  CHECK (status IN ('active', 'in_progress', 'completed', 'abandoned'));
```

**My recommendation: do not run 0004 yet.** The live schema is internally consistent and the API matches it. Only add columns when a real consumer needs them. Adding speculative fields is exactly the kind of drift Rubric #1 ("solution + prevention") is designed to prevent.

Bigger systemic fix: the task brief was written from a stale schema sketch. Andy/Pat should add a "verify task brief matches current DDL" step before kicking off any task that mentions specific columns — would have caught this before Yoni had to flag it in his closeout.
