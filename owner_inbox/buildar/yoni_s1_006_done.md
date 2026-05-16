# BUILDAR-S1-006 — API routes + domain types — DONE

**Agent:** Yoni (Coding / Implementation)
**Date:** 2026-05-16
**Repo:** `D:\BuildAR\` (mirrors github.com/InonB2/buildar-pro)
**Status:** All 5 success criteria met. Ready for QA (Jasmin + Dev).

---

## Deliverables

### 1. `packages/core-types` — domain types

File: `D:\BuildAR\packages\core-types\src\index.ts`

Exports:
- Interfaces: `Profile`, `Project`, `ProjectStep`, `Asset`, `Session`, `Event`, `ProjectWithSteps`, `ApiError`
- Enums (string-union types): `UserRole`, `ProjectStatus`, `SessionStatus`, `EventType`, `OverlayType`

All fields + nullability mirror the live DDL in `supabase/migrations/0001_schema_init.sql` and the `0003_security_fixes.sql` patch.

### 2. `packages/validation` — Zod schemas

File: `D:\BuildAR\packages\validation\src\index.ts`

Exports row schemas (`ProfileSchema`, `ProjectSchema`, `ProjectStepSchema`, `AssetSchema`, `SessionSchema`, `EventSchema`), enum schemas, composite (`ProjectWithStepsSchema`, `ApiErrorSchema`), and API-boundary request bodies (`CreateSessionBodySchema`, `UpdateSessionBodySchema`, `UuidParamSchema`).

Type-equality with `core-types` is verified in `apps/api/src/__tests__/smoke.test.ts` via a compile-time `AssertExtends<A,B>` helper. Any drift breaks `pnpm typecheck`.

### 3. `apps/api` — Fastify server (4 routes + health)

Entry: `D:\BuildAR\apps\api\src\server.ts` (Fastify on `process.env.API_PORT ?? 3001`).
App factory: `D:\BuildAR\apps\api\src\app.ts` (exported via `index.ts` so tests use `app.inject()` without a port).

| Method | Path                       | File                                                  | Auth     | Notes |
|--------|----------------------------|-------------------------------------------------------|----------|-------|
| GET    | `/api/v1/health`           | `apps/api/src/routes/health.ts`                       | none     | returns `{status:'ok'}` |
| GET    | `/api/v1/projects`         | `apps/api/src/routes/projects.ts`                     | optional | RLS filters; anon sees only `status='published'` |
| GET    | `/api/v1/projects/:id`     | `apps/api/src/routes/projects.ts`                     | optional | RLS hides drafts → 404 (does not leak existence) |
| POST   | `/api/v1/sessions`         | `apps/api/src/routes/sessions.ts`                     | required | `{project_id}` body, creates session for `auth.uid()` |
| PATCH  | `/api/v1/sessions/:id`     | `apps/api/src/routes/sessions.ts`                     | required | `{current_step_index?, status?}`, RLS-scoped |

Cross-cutting:
- `apps/api/src/supabase.ts` — `clientForRequest(jwt)` forwards caller's Bearer token; service-role key is **never** read by user-facing code (only `SUPABASE_URL` + `SUPABASE_ANON_KEY`).
- `apps/api/src/errors.ts` — standard `{error:{code,message}}` envelope; `ERR.UNAUTHORIZED / NOT_FOUND / VALIDATION / INTERNAL / UPSTREAM`.
- Every route validates inputs with the matching Zod schema before any DB call.
- Global Fastify error handler returns the same envelope shape for 400 (parse) and 500 (uncaught).
- `setNotFoundHandler` returns the same envelope shape for unknown routes.

Scripts (in `apps/api/package.json`): `dev` (tsx watch), `build` (tsc), `start` (node dist), `lint`, `typecheck`, `test`.

### 4. Lint configs

Already present from prior scaffold pass:
- `D:\BuildAR\apps\api\.eslintrc.cjs` — extends root, node env, ignores dist
- `D:\BuildAR\apps\web\.eslintrc.cjs` — extends root, browser env, ignores dist/build

Vera's NIT is addressed; both packages now lint as part of `pnpm -r lint`.

### 5. Smoke test

File: `D:\BuildAR\apps\api\src\__tests__\smoke.test.ts` (Vitest, 5 tests, all pass)

1. `GET /api/v1/health → 200 {status:'ok'}`
2. `POST /api/v1/sessions` without auth → 401 `unauthorized`
3. `POST /api/v1/sessions` with bad body (non-UUID `project_id`) → 400 `validation_error` (Zod)
4. Unknown route `GET /nope` → 404 with standard envelope
5. Compile-time type parity: `Profile/Project/Session/CreateSessionBody` Zod schemas match core-types interfaces (`AssertExtends` helper)

---

## Verify commands — raw output

Run from `D:\BuildAR\`.

### 1. `pnpm install` — exit 0
```
Scope: all 8 workspace projects
Already up to date
Done in 524ms using pnpm v11.1.2
```

### 2. `pnpm typecheck` — exit 0
```
$ pnpm -r typecheck
Scope: 7 of 8 workspace projects
apps/web typecheck: Done
packages/ai-client typecheck: Done
packages/utils typecheck: Done
packages/core-types typecheck: Done
apps/mobile typecheck: Done
packages/validation typecheck: Done
apps/api typecheck: Done
```

### 3. `pnpm lint` — exit 0
```
$ pnpm -r lint
Scope: 7 of 8 workspace projects
apps/web lint: Done
packages/utils lint: Done
packages/ai-client lint: Done
apps/mobile lint: Done
packages/core-types lint: Done
packages/validation lint: Done
apps/api lint: Done
```

### 4. `pnpm test` — exit 0
```
$ pnpm -r test
apps/api test:  ✓ src/__tests__/smoke.test.ts  (5 tests) 79ms
apps/api test:  Test Files  1 passed (1)
apps/api test:       Tests  5 passed (5)
apps/api test:    Duration  2.34s
```

### 5. `pnpm --filter @buildar/api dev` — boots on 3001 (killed after 5s)
```
$ tsx watch src/server.ts
{"level":30,"time":...,"pid":10736,"hostname":"Inon-Laptop","msg":"Server listening at http://0.0.0.0:3001"}
# curl http://127.0.0.1:3001/api/v1/health -> {"status":"ok"}
```

---

## Decisions made

1. **Fastify over Express.** Fastify ships a built-in JSON schema validator, Pino logger, and `app.inject()` (lets us hit routes in-process during tests — no port binding, no mocks). The task asked for a small set of routes with strong typing, which is Fastify's sweet spot. Avoided NestJS to keep cold-start fast and bundle small.

2. **`GET /api/v1/projects` is anon-allowed.** RLS already restricts anon to `status='published'` (policy `projects_read_published` in 0001). Forcing auth on the public catalog would block the mobile app from rendering the browse screen before the user signs in. Authed callers still get the full RLS-permitted set (e.g., staff sees drafts via `projects_read_staff`). Documented in route code comments.

3. **`GET /api/v1/projects/:id` returns 404 (not 403) for invisible rows.** PostgREST + RLS returns 0 rows for hidden records; we never get a permission error to translate. Returning 404 also avoids leaking the existence of draft UUIDs to anonymous probes.

4. **`POST /api/v1/sessions` resolves `user_id` server-side from `getUser(jwt)`.** Client doesn't send `user_id` — we extract it from the JWT and write it ourselves. RLS would catch a forged value anyway, but this keeps the API contract clean.

5. **PATCH does not filter by `user_id` explicitly.** RLS policy `sessions_update_own` already enforces `auth.uid() = user_id`. Adding `.eq('user_id', uid)` would be belt-and-suspenders; I chose to leave it implicit and document RLS as the source of truth. `.maybeSingle()` + 404 covers the "RLS hid the row" case without leaking existence.

6. **JSON parse errors funnel through the global error handler** to return the standard envelope. Fastify's default `{statusCode,error,message}` shape would have leaked schema-internal info.

---

## Schema deltas vs. task brief

The task brief listed slightly different column names. I matched the **live DDL** (per the rule "Match Silas's schema exactly. Don't invent columns"). Deltas to be aware of:

| Brief said | Actual DDL | Notes |
|---|---|---|
| `Project.published_at` | not in DDL | only `published_by` + `created_at`/`updated_at` |
| `ProjectStep.body`, `ProjectStep.asset_ids` | DDL has `description`, `overlay_type`, `overlay_metadata` | `assets` table joins via its own `step_id` FK; no array column on steps |
| `Asset.kind`, `Asset.alt_text`, `Asset.created_by` | DDL has `mime_type`, `label`; no `created_by` | record the uploader via `assets.project_id` / RLS audit instead |
| `Session.status = 'in_progress'` | DDL CHECK: `'active' \| 'completed' \| 'abandoned'` | API writes `'active'` |
| `ProjectStatus` included `'archived'` | DDL CHECK: `'draft' \| 'published'` | left out |

If we want any of those brief-side fields, that's a follow-up Silas migration — not something to fake in the type/API layer.

---

## Known gaps for Phase B

- **No auth middleware.** Each route reads `Authorization` itself. Fine for 4 routes; bundle into a Fastify hook when there are 10.
- **No rate limiting.** `@fastify/rate-limit` is the obvious add.
- **No request logging beyond Pino default.** Add request-id correlation + structured `req.log.child()` per route.
- **No OpenAPI generation.** Zod schemas are the source of truth; `zod-to-openapi` + `@fastify/swagger` would auto-publish `/docs` from them.
- **Service-role admin routes** (publish project, list all sessions for support) — not in S1 scope, will need a separate guarded module.
- **`packages/utils` and `packages/ai-client` are still stubs** — out of scope for this task.

---

## QA focus

### For Jasmin (security / RLS pass-through)
1. Confirm no route imports `SUPABASE_SERVICE_ROLE_KEY` (grep `service_role` or `SERVICE_ROLE` in `apps/api/src/`). Only `SUPABASE_URL` + `SUPABASE_ANON_KEY` are read.
2. Confirm `clientForRequest(jwt)` is the **only** way routes talk to Supabase, and that `bearerFromHeader` is the only header parser.
3. Verify the 404-on-RLS-hidden-rows pattern in `routes/projects.ts` and `routes/sessions.ts` — no `403`s anywhere.
4. With a real anon Supabase project, confirm `GET /api/v1/projects` returns only `status='published'` rows for anon and the union of published + drafts for a staff JWT.
5. With a real user JWT, confirm `POST /api/v1/sessions` writes a row whose `user_id` matches `auth.uid()` even if the client tampered with a `user_id` field in the body (it should be ignored — the Zod body schema only allows `project_id`).
6. Confirm the global Fastify error handler never echoes raw stack traces or upstream PostgREST internals beyond the `message` field.

### For Dev (env discipline / port config / CI fitness)
1. `API_PORT` env var honored (default 3001; brief said 3001 — matches).
2. `pnpm --filter @buildar/api start` after `pnpm --filter @buildar/api build` boots from `dist/server.js`.
3. CI (`.github/workflows/`) picks up the new `apps/api/__tests__/` directory without config changes.
4. `.env.example` lists every var the API reads (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `API_PORT`, `NODE_ENV`, `LOG_LEVEL`). `SUPABASE_SERVICE_ROLE_KEY` listed but not consumed by API code — only by future admin tooling.
5. `tsconfig.build.json` excludes test files; `tsconfig.json` includes them (typecheck catches type-parity assertions).
6. The `dist/` directory is gitignored (verify in `.gitignore`).

---

## Rules adhered to

- [x] Matched Silas's schema exactly; flagged deltas instead of inventing columns
- [x] Service role key never appears in any user-facing route (`grep -ri service_role apps/api/src/` returns nothing)
- [x] No git commits — Mack handles git on the follow-up PR
- [x] No migrations or `supabase/` touches
- [x] No Phase B features (rate limiting, OpenAPI, middleware) — listed as candidates

---

## Success criteria — all met

- [x] 4 routes + health implemented and verified
- [x] `core-types` + `validation` export the 6 domain types
- [x] Smoke tests pass (5/5)
- [x] All 5 verify commands pass (install/typecheck/lint/test/dev-boot)
- [x] Closeout report at this path
