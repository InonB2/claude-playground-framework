# BUILDAR-S1-014 — QA re-verification (UUID req.id + rotating logs)

**Agent:** Jasmin (QA / Security)
**Date:** 2026-05-18
**Repo:** `D:\BuildAR\`
**Branch:** `feat/orchestrator-mvp`
**Commit reviewed:** `d71aeac` (local-only, not pushed)
**Verdict:** **PASS** — both S1-013 blockers (enumerable req.id + log-shipping gap) are closed. No new findings rise to HOLD; one minor observation logged below.

---

## TL;DR

- `genReqId: () => randomUUID()` wired into the Fastify factory (live-verified two distinct v4 UUIDs).
- Persistent rotating log file `apps/api/logs/api.1.log` is created on first write and contains the same `reqId` that the sanitizer returns to the client — end-to-end correlation works.
- Log directory is correctly gitignored; nothing log-shaped is tracked.
- 19/19 tests pass; new test asserts UUID shape + uniqueness + non-`req-N` legacy shape.
- No request bodies, query strings, headers, or cookies added to the log envelope. Pino default `req` serializer = method/url/hostname/remoteAddress/remotePort only.
- `pino-roll` is the official Matteo Collina / Damien Simonin Feugas package — not a typosquat.

S1-013 MINOR #1 (enumerable counter) and S1-013 carry-forward Infra #1 (request-id unrecoverable after process death on single host) — both **closed**.

---

## Findings — Infrastructure

1. **`genReqId` is wired into the live factory, not just defined.** Verified `apps/api/src/app.ts` line 65 — `genReqId: () => randomUUID()` is passed in the same `Fastify({...})` options object as `logger`. No earlier override could shadow it. Live boot on port 3458 with stub Supabase produced two consecutive sanitized error bodies carrying `requestId: "bd49e9c3-0222-4cb5-8556-bbc7aecd7e7c"` and `requestId: "4601d37b-70c4-400b-93b5-13e8ae88da96"` — both match `/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i`, both distinct, neither matches `/^req-\d+$/`. **PASS.**

2. **`apps/api/logs/` is gitignored.** `git check-ignore -v apps/api/logs/api.log` → `.gitignore:9:logs/	apps/api/logs/api.log`. Same for the rotated `api.1.log`. `git ls-files apps/api/logs/` returns empty. Root `.gitignore` already had both `*.log` (line 8 equivalent) and `logs/` (line 9) — no change needed and none made. **PASS.**

3. **`pino-roll` is the official package.** Inspected `apps/api/node_modules/pino-roll/package.json`: repository `git+https://github.com/mcollina/pino-roll.git`, contributor `Matteo Collina <hello@matteocollina.com>` (Pino + Fastify core maintainer), author Damien Simonin Feugas. License MIT. Dependencies = `date-fns` + `sonic-boom` (the latter is Pino's own underlying file writer). Not a typosquat. **PASS.**

4. **Log file actually rotates / mkdir works.** Deleted `apps/api/logs/` entirely, booted API, hit it twice — directory was recreated and `api.1.log` (2.2 KB, 7 lines) appeared with the expected content. Rotation mechanism: `pino-roll` opens `api.1.log`, rolls to `api.2.log` on daily boundary OR when size hits `10m`, deletes oldest after `limit.count: 7`. Did NOT synthetically fill 10 MB to force size-rotation in this QA cycle — risk is low, library is upstream-tested. Documented as a one-week spot-check item in `BKM/sop_infra.md` already (Yoni). **PASS — noted.**

5. **`process.cwd()`-relative log path is a deploy-time gotcha (carry-forward).** `apps/api/src/app.ts` line 30 resolves `path.resolve(process.cwd(), 'logs', 'api.log')`. Correct today because `pnpm dev` / `pnpm start` both run from `apps/api/`. Will misroute if anyone ever invokes the API from the repo root or via a Docker `WORKDIR` change. Yoni already flagged this in his report; SOP also flags. Acceptable for Stage 1, must be replaced with a `LOG_DIR` env var before deploy. **PASS — carry-forward.**

6. **Log-shipping for multi-host deploy.** Still NOT solved — by design. Stage 1 is single-host. Multi-host needs a real collector. SOP `BKM/sop_infra.md` deploy-readiness checklist captures this. **PASS — carry-forward.**

---

## Findings — Design

1. **No PII / request-body leak introduced by the logger change.** Audited every `req.log.*` / `app.log.*` call in `apps/api/src` (orchestrator.ts, projects.ts, sessions.ts, app.ts, server.ts, lib/errors.ts). All log payloads are `{ err, requestId, id, project_id }` style — never `req.body`, never `req.headers`, never `req.query`. No new `serializers`, `logBody`, or `redact` config was added. Log file inspection confirms the actual on-disk shape: `method`, `url`, `hostname`, `remoteAddress`, `remotePort`, `statusCode`, `responseTime`, plus the error chain. **PASS.**
   - *Note (not a finding):* `remoteAddress` (client IP) is part of Fastify's default `req` serializer. Was already being logged to stdout pre-S1-014; the only delta is that it now also lands in a file. Not introduced by this task. Worth tracking separately if/when GDPR-style data-retention rules come into play — flag for Mack/Silas at deploy time.

2. **Two-target transport (stdout + file).** Preserves dev ergonomics (live tail via `pnpm dev`) AND gives the support workflow a grep-able file. Right call. Cost = a slightly heavier transport thread, but negligible at Stage 1 traffic. **PASS.**

3. **Test isolation.** The new `req_id_uuid.test.ts` runs with `logger: false`, so the file I/O / pino-roll worker thread doesn't fire during the suite. 19/19 still finish in ~1.9s. Same Supabase mock pattern as `error_sanitization.test.ts` — readable, no flakiness signal. **PASS.**

4. **`randomUUID` over `nanoid`.** Built into `node:crypto`, zero new deps, FIPS-compliant CSPRNG, ~128 bits of entropy. Right call for a security-driven change. **PASS.**

5. **Log levels for 404-from-sanitizer still `error`.** Carry-forward from my S1-013 QA — out of scope for this task per brief. Not a HOLD. Will be picked up by the next sanitizer-side ticket.

---

## Verification log

```
$ pnpm --filter @buildar/api test
 ✓ src/__tests__/req_id_uuid.test.ts          (1 test)   73ms
 ✓ src/__tests__/error_sanitization.test.ts   (4 tests)  95ms
 ✓ src/__tests__/smoke.test.ts                (5 tests)  97ms
 ✓ src/__tests__/sessions_telemetry.test.ts   (3 tests)  105ms
 ✓ src/__tests__/orchestrator.test.ts         (6 tests)  148ms
 Test Files  5 passed (5)
      Tests  19 passed (19)
 Duration    1.87s

$ git check-ignore -v apps/api/logs/api.log
.gitignore:9:logs/  apps/api/logs/api.log

$ git ls-files apps/api/logs/
(empty)

$ # Live boot on 127.0.0.1:3458, two requests with stub Supabase creds
Response 1: {"error":"DatabaseError","message":"Could not complete the request.","requestId":"bd49e9c3-0222-4cb5-8556-bbc7aecd7e7c"}
Response 2: {"error":"DatabaseError","message":"Could not complete the request.","requestId":"4601d37b-70c4-400b-93b5-13e8ae88da96"}

$ grep -c "bd49e9c3-0222-4cb5-8556-bbc7aecd7e7c" apps/api/logs/api.1.log
3   # incoming request + error + request completed

$ grep -c "4601d37b-70c4-400b-93b5-13e8ae88da96" apps/api/logs/api.1.log
3
```

End-to-end: client sees `requestId` → operator greps `apps/api/logs/api.1.log` for that UUID → finds full upstream `fetch failed / ENOTFOUND stub.local` error chain. Lookup workflow works.

---

## Carry-forward into next QA cycle

(Not blockers — already tracked.)

- Log path `LOG_DIR` env var before any non-dev deploy (Infra #5).
- Remote log shipping for multi-host (Infra #6 + SOP checklist).
- 404-sanitizer log level (Design #5 — separate sanitizer task).
- Client IP retention policy (Design #1 note — flag for Mack/Silas at deploy).
- Type-parity MINOR from S1-006 — explicitly out of scope per brief.

---

**Verdict: PASS.** S1-014 is clean. No HOLD, no Telegram. Andy can move the card to Done.

— Jasmin
