# BUILDAR-S1-013 — PostgREST error sanitization — DONE

**Agent:** Yoni (Coding / Implementation)
**Date:** 2026-05-18
**Repo:** `D:\BuildAR\`
**Branch:** `feat/orchestrator-mvp`
**Commit:** `49bbed6` (not pushed, per brief)
**Status:** DONE — all 7 success criteria met, all 18 tests pass.

---

## What shipped

`feat(api): sanitize PostgREST errors before returning to client`

```
49bbed6 feat(api): sanitize PostgREST errors before returning to client
bea4153 feat(orchestrator+telemetry): S1-008 + S1-009
54c7863 chore(s1-006): baseline — apps/api routes + types + validation (prior PASS)
```

### Files touched (5)

| File | Change |
|---|---|
| `apps/api/src/lib/errors.ts` | **new** — `sanitizeError(err, requestId)` + status/code mapping |
| `apps/api/src/routes/projects.ts` | 3 DB error paths now use `sanitizeError()` |
| `apps/api/src/routes/sessions.ts` | 3 DB error paths now use `sanitizeError()` |
| `apps/api/src/routes/orchestrator.ts` | 3 DB error paths now use `sanitizeError()` |
| `apps/api/src/__tests__/error_sanitization.test.ts` | **new** — 4 test blocks (404 / 400 / 500 paths + unit mapping table) |

`events.ts` was listed in the brief but no such route file exists; the event-table writes live in `packages/utils/src/events.ts` and never echo PostgREST errors to clients (they `console.warn` server-side only). No change needed there — confirmed by inspection.

---

## Error shape contract (paste from `lib/errors.ts`)

```ts
export type SanitizedErrorCode =
  | 'NotFound'
  | 'BadRequest'
  | 'Conflict'
  | 'DatabaseError';

export interface SanitizedErrorBody {
  error: SanitizedErrorCode;
  message: string;     // safe, user-facing — NEVER a PostgREST detail
  requestId: string;   // = Fastify req.id, for server-log lookup
}

export interface SanitizedError {
  status: 400 | 404 | 409 | 500;
  body: SanitizedErrorBody;
}
```

Routes consume it as:

```ts
req.log.error({ err, requestId: req.id, ...ctx }, '<context>');
const sanitized = sanitizeError(err, req.id);
return reply.code(sanitized.status).send(sanitized.body);
```

Note: this is a **second envelope shape** alongside the existing `ApiError` `{error:{code,message}}` used by `ERR.UNAUTHORIZED / VALIDATION / NOT_FOUND / INTERNAL`. Sanitized DB errors deliberately have a flatter shape with `requestId` so operators get a correlation id. Both shapes coexist; sanitizeError is used **only** at the upstream-error boundary. See Findings → Design #1 for the trade-off.

---

## Status code mapping table

| PostgREST / Postgres code | HTTP status | `error` |
|---|---|---|
| `PGRST116` (`.single()` 0 rows) | 404 | `NotFound` |
| `23505` unique_violation | 409 | `Conflict` |
| `23503` foreign_key_violation | 409 | `Conflict` |
| `23514` check_violation | 400 | `BadRequest` |
| `23502` not_null_violation | 400 | `BadRequest` |
| `22P02` invalid_text_representation | 400 | `BadRequest` |
| `22001` string_data_right_truncation | 400 | `BadRequest` |
| HTTP `status=404` (no code) | 404 | `NotFound` |
| HTTP `status=409` (no code) | 409 | `Conflict` |
| HTTP `status` 4xx (no code) | 400 | `BadRequest` |
| anything else / unknown / empty | 500 | `DatabaseError` |

Every row is exercised by the `sanitizeError(): code → status/error mapping` unit test (12 cases).

---

## Test results

```
RUN  v1.6.1 D:/BuildAR/apps/api

 ✓ src/__tests__/smoke.test.ts                 (5 tests)  68ms
 ✓ src/__tests__/sessions_telemetry.test.ts    (3 tests)  84ms
 ✓ src/__tests__/orchestrator.test.ts          (6 tests)  99ms
 ✓ src/__tests__/error_sanitization.test.ts    (4 tests)  97ms

 Test Files  4 passed (4)
      Tests  18 passed (18)
```

- Baseline 14/14 (smoke 5 + telemetry 3 + orchestrator 6) still green.
- 4 new test blocks (the brief asked for 3; the 4th is a unit-level coverage of the mapping table so the contract is pinned even if no route happens to exercise a given code):
  1. `GET /api/v1/projects/:id` — `PGRST116` → 404 sanitized body, asserts no leakage of `JSON object requested`, `column "`, `projects_read_published`, etc.
  2. `POST /api/v1/sessions` — `22P02` on insert → 400 sanitized body, same leakage assertions.
  3. `GET /api/v1/projects/:id` — unknown PostgREST code → 500 sanitized body with `requestId`.
  4. Unit: `sanitizeError()` mapping table (12 inputs).
- `pnpm typecheck` and `pnpm lint` both exit 0.
- Workspace `pnpm -r test`: apps/api 18/18 + ai-client 6/6.

The leakage assertion (`bodyHasNoLeakage`) checks the **raw response body string** for substrings that would only appear if a PostgREST `message` / `details` / `hint` had been echoed back. None do.

---

## Decisions made

1. **`requestId` = `req.id`.** Fastify generates a unique request id per request out of the box (`reqId` in pino logs). Reused that instead of generating a fresh id per error — keeps the log line, the error response, and any downstream tracing tied to the same key. No new dependency.
2. **Flat sanitized shape (`{error,message,requestId}`) instead of nested `{error:{code,message}}`.** The brief explicitly specified the flat shape. Kept the existing nested `ApiError` for `UNAUTHORIZED / VALIDATION / NOT_FOUND` because changing those would have broken the smoke/orchestrator tests and was out of scope. The contract is documented at the top of `lib/errors.ts` so the asymmetry isn't surprising.
3. **`.maybeSingle()` returning `data:null, error:null` (RLS hides the row) is NOT a sanitizer concern.** That path already correctly returns a manual `ERR.NOT_FOUND('Project')` / `ERR.NOT_FOUND('Session')` and never carried a PostgREST error to begin with. Left unchanged.
4. **404 sanitized body has its own shape, but the existing `ERR.NOT_FOUND` path (RLS-hidden rows) still returns the nested envelope.** Acceptable — both indicate 404 and neither leaks schema info. A future cleanup could unify, but that would be a route-signature change which the brief forbids.
5. **No new dependency.** `lib/errors.ts` is pure TS; the requestId comes from Fastify's built-in `req.id`.

---

## Findings — Infrastructure vs Design (per Rubric)

### Infrastructure

1. **Log shipping is currently console-only.** Fastify's default pino logger writes JSON lines to stdout. There is no log-file rotation, no structured-log shipping to a remote sink (Loki / Datadog / Cloudwatch), and no retention policy committed in the repo. **The sanitizer's contract — "look up the raw PostgREST error by requestId" — depends on those logs surviving long enough to be queried.** If the API is run under `pnpm start` in production without a log collector wrapping it, an incident more than a process-restart ago is unrecoverable.
   - **Fix:** point pino at a transport (`pino-pretty` for dev, a transport package for prod). Track as Phase B infra.
   - **Prevention:** add a deploy-readiness checklist line "logs go somewhere that outlives the process" before BuildAR ships to a real environment.
2. **No log-level discipline around sanitized errors.** Every DB error now logs at `error` level — which is correct, but in a high-volume production environment this could swamp signal. Consider downgrading 404 sanitizations to `warn` (it's usually a benign RLS miss, not an outage).
3. **Fastify request id is opaque + ULID-like by default.** Good for correlation, not human-readable. Acceptable. If a friendlier id is wanted, configure `genReqId` in `buildApp()` — one-line change, deferred.

### Design

1. **Two error envelope shapes now coexist.** Existing routes use `{error:{code,message}}` (`ApiError`) for auth / validation / not-found; the new sanitizer uses `{error,message,requestId}`. Clients that parse error responses need to handle both. The asymmetry is documented in `lib/errors.ts` and was deliberate (the brief specified the flat shape and forbade route-signature changes), but a Phase B unification would simplify the client.
2. **`sanitizeError()` is purposely a pure function — it does not call `req.log.error()` itself.** Caller is responsible for logging. This avoids coupling the lib to Fastify and keeps it testable as a unit, but it means every route's `if (error) {...}` block has the same 3-line pattern. If we wanted to DRY, a `reply.sanitized(err, ctx)` decorator would be the next step. Did not add it now — would be a route-shape change.
3. **The mapping table is conservative.** Several PostgREST-specific codes (`PGRST300`, `PGRST301`, etc.) are NOT mapped explicitly and fall to 500. That's safer than guessing — collapse to 500 + log the full code server-side. Easy to add specific mappings as we learn which ones occur in practice.
4. **Sanitized 404 vs `ERR.NOT_FOUND` 404.** Two routes can now respond 404 with two different body shapes depending on which path triggered (RLS-hidden vs. PostgREST `PGRST116`). Documented in Decisions #4. Not a bug, but a client-side inconvenience.

---

## Out of scope (carry-forward)

- Jasmin S1-006 MINOR #2 (type-parity assertions for `ProjectStep / Asset / Event / ProjectWithSteps / UpdateSessionBody`). Explicitly excluded per brief.
- Unifying the two error envelope shapes (see Design #1). Would change response contracts; needs a versioned API bump.
- Log shipping infrastructure (Infra #1). Deploy-time concern.

---

## Success criteria — all 7 met

- [x] **1.** Identified every `error.message` forwarding path (`projects.ts:31,67,82`, `sessions.ts:60,101`, plus `orchestrator.ts:80,96,113` and the `ERR.INTERNAL()` returns).
- [x] **2.** Replaced verbatim forwarding with sanitized `{error, message, requestId}`.
- [x] **3.** Full PostgREST error logged server-side via `req.log.error({ err, requestId: req.id, ...ctx }, ...)`.
- [x] **4.** HTTP status preserved per mapping table (404 / 400 / 409 / 500).
- [x] **5.** No new dependency.
- [x] **6.** 3 new tests added (4 actually — 3 route-level + 1 unit table); each asserts sanitized shape and explicitly checks for no leakage of `details`/`hint`/column names.
- [x] **7.** 14/14 baseline tests still pass; 18/18 total.

---

## Reminders for Jasmin (re-QA scope)

1. Branch `feat/orchestrator-mvp`, commit `49bbed6` (not pushed).
2. Boot the API with stub env and curl one of the broken paths to see the sanitized shape live. The mock-only tests assert no leakage, but eyeballing a real `{"error":"DatabaseError","message":"...","requestId":"req-1"}` against a stubbed PostgREST is the gut-check.
3. Confirm `req.log.error(...)` is the **only** place the raw error appears — grep `error.message` should now return zero matches in the reply-path of route files.
4. The orchestrator's `assist` route also now sanitizes. Verify against the existing `orchestrator.test.ts` flows.

— Yoni
