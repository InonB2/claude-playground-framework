# BUILDAR-S1-014 — API hardening (UUID req.id + rotating logs) — DONE

**Agent:** Yoni (Coding / Implementation)
**Date:** 2026-05-18
**Repo:** `D:\BuildAR\`
**Branch:** `feat/orchestrator-mvp`
**Commit:** `d71aeac` (not pushed, per brief)
**Status:** DONE — all 5 success criteria met; 19/19 tests pass (18 baseline + 1 new).

---

## What shipped

`feat(api): UUID request IDs + persistent rotating logs`

```
d71aeac feat(api): UUID request IDs + persistent rotating logs
49bbed6 feat(api): sanitize PostgREST errors before returning to client
bea4153 feat(orchestrator+telemetry): S1-008 + S1-009
```

### Files touched (5)

| File | Change |
|---|---|
| `apps/api/src/app.ts` | added `genReqId: () => randomUUID()`; switched default logger config to a Pino transport with `pino/file` (stdout) + `pino-roll` (rotating file) targets |
| `apps/api/package.json` | new dep `pino-roll ^4.0.0` (official Pino rotating-file target, no peer-dep surprises) |
| `pnpm-lock.yaml` | regenerated for `pino-roll` install |
| `apps/api/src/__tests__/req_id_uuid.test.ts` | **new** — asserts two consecutive `req.id` values are UUID-shaped and unequal (uses the same Supabase mock pattern as `error_sanitization.test.ts`) |
| `BKM/sop_infra.md` | **new** — documents log retention policy + deploy-readiness checklist |

`apps/api/logs/` is intentionally NOT created in git — the root `.gitignore` already excludes `logs/` and `*.log` globally. Verified `git status` does not list any `.log` file before commit. `pino-roll` is configured with `mkdir: true` so the directory is auto-created on first write.

---

## Code changes (annotated)

`apps/api/src/app.ts`:

```ts
import { randomUUID } from 'node:crypto';
// ...
function defaultLoggerConfig(): object {
  const logFile = path.resolve(process.cwd(), 'logs', 'api.log');
  return {
    level: process.env.LOG_LEVEL ?? 'info',
    transport: {
      targets: [
        { target: 'pino/file', options: { destination: 1 }, level: ... },
        { target: 'pino-roll', options: {
            file: logFile,
            frequency: 'daily',
            size: '10m',
            limit: { count: 7 },
            mkdir: true,
          }, level: ... },
      ],
    },
  };
}

const app = Fastify({
  logger: opts.logger ?? defaultLoggerConfig(),
  genReqId: () => randomUUID(),
});
```

Notes:
- Tests still pass `logger: false`, so no file I/O / worker-thread overhead in the test suite (verified — 18 baseline tests still complete in ~600ms).
- `genReqId` is set unconditionally — applies in dev, prod, AND tests. The new test exercises it through the same `app.inject()` path that the sanitizer uses, so the production code path is verified end-to-end.
- The log file path resolves relative to `process.cwd()`. Since `pnpm dev` / `pnpm start` runs from `apps/api`, the file lands at `apps/api/logs/api.log`. Confirmed live (see "Live verification" below).

---

## Live verification — two real `requestId` values

Booted the API with stub Supabase creds on port 3457 and hit `GET /api/v1/projects/<uuid>` twice. The sanitizer kicked in (Supabase fetch fails against `stub.local` — 500/`DatabaseError`), and the response bodies carried:

```
Request 1: {"error":"DatabaseError","message":"Could not complete the request.","requestId":"ebbe7e17-1337-4eda-a62b-6e410a3b4974"}
Request 2: {"error":"DatabaseError","message":"Could not complete the request.","requestId":"29131520-48e7-4722-a32a-d5e5e639cfee"}
```

Both are valid v4-shaped UUIDs (match `/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i`) and obviously unequal. The legacy `req-1, req-2, ...` counter is gone — Jasmin's MINOR #1 from S1-013 is closed.

The log file `apps/api/logs/api.1.log` was created by `pino-roll` on first write (3 KB after a few requests). It contained the matching `reqId` lines including the full error correlation chain:

```
{"level":50,"reqId":"29131520-48e7-4722-a32a-d5e5e639cfee","err":{...full PostgREST/fetch error...},"requestId":"29131520-48e7-4722-a32a-d5e5e639cfee","id":"33333333-...","msg":"project fetch failed"}
```

This is exactly the lookup workflow the sanitizer was designed for: client sees `requestId`, support greps the log file for that UUID, finds the raw upstream error. Pre-S1-014 the log line existed but only in stdout — now it survives process restarts.

---

## Test results

```
RUN  v1.6.1 D:/BuildAR/apps/api

 ✓ src/__tests__/req_id_uuid.test.ts          (1 test)   93ms
 ✓ src/__tests__/error_sanitization.test.ts   (4 tests)  116ms
 ✓ src/__tests__/sessions_telemetry.test.ts   (3 tests)  124ms
 ✓ src/__tests__/smoke.test.ts                (5 tests)  132ms
 ✓ src/__tests__/orchestrator.test.ts         (6 tests)  150ms

 Test Files  5 passed (5)
      Tests  19 passed (19)
```

- Baseline 18/18 still green (target: ≥18 → met).
- 1 new test (`req_id_uuid.test.ts`) — asserts both UUIDs match the regex AND that neither matches the legacy `req-\d+` shape (defense in depth).
- `pnpm --filter @buildar/api typecheck` exits 0.
- `pnpm --filter @buildar/api lint` exits 0.

Total: 19/19 (target ≥19, met exactly).

---

## Success criteria — all 5 met

- [x] **1.** `genReqId: () => randomUUID()` added to `Fastify(...)` factory in `apps/api/src/app.ts`. Grep confirms no prior `genReqId` override — nothing was silently shadowed.
- [x] **2.** `pino-roll` installed as a direct dep of `@buildar/api`. Logger transport writes to `apps/api/logs/api.log` with daily rotation, 10 MB cap, 7-day retention. `logs/` is gitignored (root `.gitignore` line 8 + `*.log` line 9). `mkdir: true` means no manual setup needed.
- [x] **3.** No regression — 18 baseline tests still pass.
- [x] **4.** 1 new test added — asserts two `req.id` values are UUID-regex-valid AND unequal AND not the legacy `req-N` shape.
- [x] **5.** Test suite total: 19 passing (target ≥19).

---

## Log rotation policy — plain English

- The API writes structured JSON log lines to two places simultaneously: stdout (for `pnpm dev` watch / Docker stdout / etc.) and `apps/api/logs/api.log` (for `requestId` correlation lookups).
- The file is **rotated daily**. When a new calendar day starts, `pino-roll` opens a new file (`api.2.log`, `api.3.log`, …) and the old one is sealed.
- The file is **also rotated when it hits 10 MB**, even mid-day. Prevents a runaway log from filling disk.
- **7 files are kept.** The 8th rotation deletes the oldest. Worst-case disk usage: 7 × 10 MB = 70 MB.
- **No remote shipping.** Local file only. Stage 2 will add a collector when BuildAR Pro moves off the dev machine — tracked in `BKM/sop_infra.md` deploy-readiness checklist.

---

## Findings — Infrastructure vs Design (per Rubric)

### Infrastructure

1. **`pino-roll` rotation — verified by library docs, not by synthetic disk fill.** The brief allowed either approach; I went with docs. `pino-roll` v4 is the official Pino rotating-file target maintained by the Pino org. `frequency: 'daily'`, `size: '10m'`, and `limit.count: 7` are documented and tested upstream. If we want a defense-in-depth test, we'd need to ship a 10 MB log line in CI — not worth it for Stage 1. Recommendation: spot-check rotation manually after one week of actual dev use.
2. **`pino-roll` peer-dep check.** Installed cleanly with no peer-dep warnings on Node 20.x (project's stated minimum). No native bindings; pure JS. Adds 2 transitive packages (`pino-roll` + `path-to-regexp`-style helper). Acceptable.
3. **Log directory creation.** `mkdir: true` means we never crash on first boot if `apps/api/logs/` is absent. Verified — deleted the dir, booted, dir was recreated on first request. (Note: the directory existed before my run from an aborted earlier attempt, so the verification is from the second clean boot.)
4. **`process.cwd()` dependence.** `apps/api/logs/` is resolved relative to where the API is started. `pnpm dev` and `pnpm start` both run from `apps/api/`, so this is correct for the current entrypoint scripts. If we ever switch to running the API from the repo root, the path resolves elsewhere — flagging as a future-deploy gotcha. Mitigation: change to a `LOG_DIR` env var when the deploy target is concrete.
5. **Carry-forward from Jasmin's S1-013 QA #1:** the log file existing on disk does NOT replace a real log collector for multi-host or multi-replica deploys. Stage 1 single-host is fine. Pre-prod (multi-host) blocker is still open — explicitly tracked in `BKM/sop_infra.md` deploy-readiness checklist.

### Design

1. **`randomUUID()` over `nanoid`.** `randomUUID` is zero-dependency (built into `node:crypto` since Node 14.17). `nanoid` would give shorter ids but adds a dep, and Fastify's `reqId` is rarely surfaced to humans — it lives in logs and the sanitized error body, both machine-consumed. Chose simplicity.
2. **Two transport targets, not one.** Could have used `pino-roll` alone (file-only) and asked the user to `tail` the file. Kept stdout so `pnpm dev` still shows live logs in the terminal — preserves the existing developer ergonomics. Cost is a slightly more complex transport config. Worth it.
3. **No `pino-pretty` in the dev target.** Pretty-printing is a separate dep and was not in the brief. Logs are JSON either way — easier to grep and forward later. If devs want pretty output, they can pipe stdout through `pino-pretty` themselves.
4. **Log levels unchanged.** Did not address Jasmin's S1-013 carry-forward note about downgrading 404 sanitizations to `warn`. That's a separate sanitizer-side change and out of scope for this task — flagging for the next sanitization-related task.
5. **The test uses the same mock pattern as `error_sanitization.test.ts`.** Kept the test isolated in its own file (`req_id_uuid.test.ts`) rather than tacking it onto the existing sanitization tests. Cleaner separation — the UUID assertion is about the Fastify factory config, not about sanitizer behavior; if either changes independently, the failure mode is more readable.

---

## Out of scope (still carry-forward)

- Jasmin S1-006 MINOR #2 — type-parity assertions for `ProjectStep / Asset / Event / ProjectWithSteps / UpdateSessionBody`. Explicitly excluded per brief.
- Remote log shipping (S1-013 Infra #1, also flagged in `BKM/sop_infra.md`). Stage 2 task.
- Unifying the two error envelope shapes (S1-013 Design #1). Versioned API bump candidate.
- Log-level downgrade for 404 sanitizations (Jasmin's note in §3 of her S1-013 QA). Separate task.

---

## Reminders for Jasmin (re-QA scope)

1. Branch `feat/orchestrator-mvp`, commit `d71aeac` (not pushed).
2. Pull the branch (no rebase needed — clean linear add on top of `49bbed6`).
3. Confirm `pnpm --filter @buildar/api test` shows 19/19.
4. Boot the API with stub creds and hit any `/api/v1/projects/<uuid>` twice — verify the returned `requestId` is a UUID and that consecutive values differ. (Two example values captured in this report at `ebbe7e17-…` and `29131520-…`.)
5. Verify `apps/api/logs/api.1.log` is created on first request and contains the same `reqId` as the response body. Verify it is NOT tracked by git (`git ls-files apps/api/logs/` returns nothing).
6. Eyeball `BKM/sop_infra.md` for the retention policy — confirm it matches what's in the code.

— Yoni
