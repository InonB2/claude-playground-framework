# Jasmin QA — BUILDAR-S1-013 (PostgREST error sanitization)
**Date:** 2026-05-18
**Tester:** Jasmin (Security & Logic Auditor)
**Scope:** `D:\BuildAR\apps\api\src\lib\errors.ts`, `apps/api/src/routes/{projects,sessions,orchestrator}.ts`, `apps/api/src/__tests__/error_sanitization.test.ts`, `packages/utils/src/events.ts`
**Branch / Commit:** `feat/orchestrator-mvp` @ `49bbed6` (unpushed, per brief)
**Verdict:** **PASS WITH NOTES** — MINOR #1 from S1-006 is closed; one new minor info-leak surface found (`req.id` is sequential), one infra follow-up confirmed.

---

## Security correctness

### 1. No schema-leak path remains — PASS
Grep for `error.message|error.details|error.hint|error.code` across `apps/api/src/routes/`:
- Only match: `orchestrator.ts:46` — a doc comment ("Never forwards upstream PostgREST error.message to the caller…"). Zero functional matches.
- Targeted grep for the actual reply-bound variables (`err.message`, `projectErr.message`, `sessionErr.message`, `stepsErr.message`, `prevErr.message`, `userErr.message`) → **0 hits.**
- Every `if (error|*Err)` block in the three route files routes through `sanitizeError(err, req.id)` and sends `sanitized.body`. None construct an `ERR.UPSTREAM(error.message)` reply anymore.

`ERR.UPSTREAM` itself is no longer imported by any route file — verified by grep. The S1-006 MINOR #1 leak surface (column/constraint/hint echo) is **closed.**

### 2. Status mapping correctness — PASS (one note)
Independently checked against PostgREST + Postgres SQLSTATE semantics:

| Code | Yoni's mapping | Semantics | Verdict |
|---|---|---|---|
| `PGRST116` | 404 NotFound | `.single()` got 0/multi rows | Correct |
| `23505` unique_violation | 409 Conflict | Idempotent retry candidate | Correct |
| `23503` foreign_key_violation | 409 Conflict | Defensible — see note | Acceptable |
| `23514` check_violation | 400 BadRequest | Client-supplied value invalid | Correct |
| `23502` not_null_violation | 400 BadRequest | Client omitted required field | Correct |
| `22P02` invalid_text_representation | 400 BadRequest | E.g. bad UUID | Correct |
| `22001` string_data_right_truncation | 400 BadRequest | Oversize string | Correct |
| HTTP 404 | 404 NotFound | PostgREST passthrough | Correct |
| HTTP 409 | 409 Conflict | PostgREST passthrough | Correct |
| HTTP 4xx | 400 BadRequest | Conservative collapse | Correct |
| HTTP 5xx / unknown | 500 DatabaseError | Safe default | Correct |
| `42501` (insufficient_privilege) | **NOT mapped** | Falls to 500 | Acceptable for now — see note |

**Note (Design, not a finding):** `23503` (FK violation) is dual-natured. It fires both when a child references a non-existent parent (client error → 400/404) AND when a DELETE on a parent is blocked by an existing child (server-state conflict → 409). Yoni picked 409 uniformly. Defensible since BuildAR has no public DELETE endpoints in S1; revisit when delete routes ship. Not a blocker.

**Note (Design, not a finding):** `42501` (RLS / privilege denied) falls through to 500 DatabaseError. In normal operation, RLS rejections come back to PostgREST as 0 rows on `.maybeSingle()` (correctly returning 404 in our code paths), so 42501 should be rare. If a privileged operation ever surfaces this code, 500 hides the privilege check from the client — which is conservatively safe (no info leak), but the operator sees the wrong category in metrics. Add `42501 → 403` only if a real route starts emitting it.

### 3. `requestId` exposure assessment — **MINOR finding**
Yoni claims `req.id` is "ULID-like by default" (his report, line 134). **This is incorrect.** Fastify's default `genReqId` is a **sequential per-process counter** prefixed with `req-`. Probed live in this very codebase:

```js
// 5 sequential requests against a fresh Fastify instance:
["req-1","req-2","req-3","req-4","req-5"]
```

`buildApp()` in `apps/api/src/app.ts` does NOT override `genReqId` — grep for `genReqId|requestIdHeader` returns 0 matches. So every sanitized error body sent to a client now includes a monotonic counter:

```json
{"error":"DatabaseError","message":"Could not complete the request.","requestId":"req-42"}
```

**Risk (LOW but real):**
- **Request enumeration / volume disclosure.** A hostile caller hitting `/api/v1/projects/<bad>` twice can subtract the two `requestId` values and infer total request volume in the window. Useful for sizing the service, timing attacks, or knowing whether the API just restarted (counter resets to 1 on process boot).
- **Cross-tenant correlation.** Two unrelated users who each get a 500 within ms can see they hit consecutive request ids — minor side-channel.

**Fix (one line in `app.ts`):**
```ts
import { randomUUID } from 'node:crypto';
const app = Fastify({
  logger: ...,
  genReqId: () => randomUUID(),
});
```

Or `nanoid` if a shorter id is desired. No new dependency needed — `node:crypto` is built-in. Recommend opening a follow-up task (S1-014 or similar) — small, safe, isolated.

### 4. Server-side log still has the full error — PASS
For every one of the 9 `sanitizeError()` call sites, there is a **paired** `req.log.error(...)` call **immediately above it**, on the same code path, carrying:
- the full raw error object (`err: error` / `err: projectErr` / `err: prevErr` / etc.)
- the same `requestId: req.id` echoed back to the client
- contextual route-specific identifiers (`id`, `project_id`, `session_id`)

Verified by grep: 9 `sanitizeError(` call sites and 9 `req.log.error` lines across the three route files, 1:1.

This means support / on-call CAN look up the raw PostgREST error from the client's `requestId` — provided the log lines survive (see Infra #1 below).

### 5. `events.ts` skip justified? — PASS
Read `packages/utils/src/events.ts` line-by-line. Confirmed:
- The file is a helper, not a route. It has no `reply` parameter and no Fastify dependency.
- On insert failure (line 107-115) it calls `console.warn('[telemetry] recordEvent insert failed', { event_type, code, message })`. This goes to **stdout only** — there is no return path to a client. The function returns `void` either way.
- On thrown exception (line 117-123) same pattern — server-side `console.warn` only.
- Line 112-113 even has a defensive comment: *"DO NOT log error.message verbatim if this ever escapes the API boundary; here it's server-side log only and safe."*

Yoni's claim is correct: `events.ts` writes never reach a client. No HOLD.

---

## Logic correctness

### 6. All DB error paths covered — PASS (count = 9, matches claim)
Independent count by greppping `sanitizeError(` in `apps/api/src/routes/`:

| File | Sanitizer calls | Lines |
|---|---|---|
| `routes/projects.ts` | 3 | 33, 69, 86 |
| `routes/sessions.ts` | 3 | 65, 141, 161 |
| `routes/orchestrator.ts` | 3 | 85, 105, 126 |
| **Total** | **9** | — |

Matches Yoni's "9 DB error paths" claim. Each call is on the `if (error)` / `if (*Err)` branch of a Supabase query result. No DB-error branch in these three route files bypasses the sanitizer.

`health.ts` has no DB calls and needs no sanitizer. The S1-006 `ERR.UPSTREAM(error.message)` pattern is gone from all three route files (zero grep hits for `ERR.UPSTREAM` in routes).

### 7. No regression on happy paths — PASS
Ran `pnpm --filter @buildar/api test` fresh:

```
 ✓ src/__tests__/smoke.test.ts                 (5 tests)  59ms
 ✓ src/__tests__/error_sanitization.test.ts    (4 tests)  69ms
 ✓ src/__tests__/sessions_telemetry.test.ts    (3 tests)  80ms
 ✓ src/__tests__/orchestrator.test.ts          (6 tests)  101ms

 Test Files  4 passed (4)
      Tests  18 passed (18)
   Duration  1.65s
```

14 baseline (smoke 5 + telemetry 3 + orchestrator 6) + 4 new = 18/18 green. Matches Yoni's claim exactly.

The new test file's `bodyHasNoLeakage()` helper checks the raw response body for 10 forbidden substrings (`JSON object requested`, `column "`, `invalid input syntax`, `enable_seqscan`, `projects_read_published`, `pgbouncer`, `public.projects`, `expects uuid`, `multiple (or no) rows`, `pg buffer`) covering the leaky `message` / `details` / `hint` fields. Each route-level test injects a deliberately leaky error and asserts none of those substrings appear in the reply. Strong assertion shape.

### 8. Sanitizer is pure / deterministic — PASS
Read `lib/errors.ts` end-to-end:
- No imports of `pino`, `fastify`, `console`, `fs`, `process`, or any I/O module.
- `classify()` is a pure switch over `err.code` and `err.status`.
- `sanitizeError()` only constructs and returns an object literal.
- Same input → same output, every time. The unit test (12 cases) confirms.
- The `SAFE_MESSAGES` table is a frozen const — no per-request mutation.

Logging is correctly the **caller's** responsibility, paired with the sanitizer call. This is the right separation of concerns — testable as a pure unit, and the route can decide log level / context per call site. Matches Yoni's Design note #2.

---

## Infrastructure vs Design (per Rubric)

### Infrastructure

1. **Log shipping is console-only — CONFIRMED, MEDIUM severity.** Yoni flagged this in his Infra #1. I concur — and want to upgrade it to **Medium** because the sanitizer's value proposition ("look up the full PostgREST error by requestId") is entirely contingent on the log line surviving long enough for an operator to query. With `pnpm start` writing pino JSON to stdout and no log collector:
   - A process restart loses everything in flight.
   - There is no central place to grep `requestId: "req-42"` across replicas.
   - The client gets a `requestId` that **looks** actionable but, in production today, has nowhere to resolve.
   - **Fix:** add a pino transport (`pino/file` with rotation, or a hosted sink). One-line config change in `app.ts` plus an env var.
   - **Prevention:** add "logs go somewhere that outlives the process" to the deploy-readiness checklist before BuildAR goes to a real environment. Track as a follow-up infra task — does not block S1-013 sign-off, but should not ship to prod without it.

2. **Sequential `req.id`** — see Security #3 above. Filed there because the security implication (request enumeration) drives the priority, but the **fix** is an infra/app config one-liner.

3. **Log level discipline.** Every sanitized error currently logs at `error` level — including 404 sanitizations (which are typically benign RLS misses, not outages). In high volume this will swamp signal. Consider downgrading 404 paths to `warn`. Carry-forward, not a finding.

### Design

1. **Mapping table is conservative.** Several PostgREST-specific codes (`PGRST300/301/302/…`) collapse to 500. Safer than guessing — agreed with Yoni's Design #3. Add specific mappings as we learn which ones actually fire in production.

2. **Two error envelope shapes coexist** (`{error:{code,message}}` from `ERR` factory vs `{error,message,requestId}` from sanitizer). Asymmetry is documented in `lib/errors.ts` header. Clients must handle both. Acceptable for S1; unify in a Phase B versioned API bump. Matches Yoni's Design #1.

3. **404 path bifurcation** (RLS-hidden via `ERR.NOT_FOUND` vs PostgREST `PGRST116` via sanitizer). Both correctly 404, both safe. Client-side inconvenience. Same Phase B unification candidate. Matches Yoni's Design #4.

---

## Findings summary

### BLOCKER — 0
None.

### MAJOR — 0
None.

### MINOR — 2
1. **Sequential `req.id` exposed in every sanitized error body.** Fastify default `genReqId` is a per-process counter. Probed live: `req-1, req-2, …`. Enables request volume enumeration and process-restart inference. Fix: set `genReqId: () => randomUUID()` in `buildApp()` (one line, no new dep). Recommend a follow-up task.
2. **Log persistence gap (carried forward from Yoni's Infra #1).** `requestId` correlation is only useful if the server log survives. No transport configured. Pre-prod blocker, not an S1-013 blocker.

### NIT — 1
1. **Yoni's report says `req.id` is "ULID-like by default"** (line 134 of his closeout). It is not — it is a sequential counter. Cosmetic correction for accuracy of future references.

---

## Sign-off

**Verdict: PASS WITH NOTES.** S1-013 closes Jasmin S1-006 MINOR #1 (PostgREST schema leak). All 7 of Yoni's success criteria verified independently. 18/18 tests pass on a fresh run. No new security defect introduced — the only new minor (sequential `req.id`) is inherited from Fastify defaults and predates this task, but is now visible to clients because S1-013 echoes it. Recommend the `randomUUID()` follow-up be scheduled before any production deploy.

**Recommendation to Andy:** move BUILDAR-S1-013 to Done with `tested_by: Jasmin`. File a small follow-up task ("S1-014: switch `req.id` to UUID + add pino transport") to address the two MINORs and the infra log-persistence gap as a single hardening pass.

Out of scope per brief (not addressed here): S1-006 MINOR #2 (type-parity assertions for `ProjectStep / Asset / Event / ProjectWithSteps / UpdateSessionBody`).

— Jasmin
