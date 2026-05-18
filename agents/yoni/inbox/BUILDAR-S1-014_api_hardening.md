# Yoni — BuildAR Pro S1-014: API hardening (UUID req.id + persistent logger)

**From:** Andy
**Dispatched:** 2026-05-18
**Task:** BUILDAR-S1-014 — closes 2 hardening items from Jasmin S1-013 QA
**Branch:** continue on `feat/orchestrator-mvp` (extend with 1 commit)
**Tester:** Jasmin

---

## Why this matters

Jasmin's S1-013 QA returned PASS WITH NOTES. Two pre-prod blockers came out of it:

### 1. `req.id` is sequential — request enumeration risk
You claimed in your S1-013 report that `req.id` is "ULID-like" / unbounded. Jasmin probed live: actual output is `["req-1","req-2","req-3","req-4","req-5"]`. Fastify's default `genReqId` is a per-process monotonic counter. Now that every sanitized error response includes `requestId`, **every error exposes total request volume + process-restart events** to any client. That's an info-disclosure (low severity, but trivially exploitable).

**The fix is one line:** override `genReqId: () => randomUUID()` in the Fastify factory. `randomUUID` is in Node's built-in `node:crypto` — no new dependency.

### 2. Log-shipping gap — `requestId` lookups have no surviving log
You also flagged this yourself in your S1-013 Infrastructure section. The entire value of returning a `requestId` to clients depends on the server log surviving long enough to be queried. Today logs are stdout-only with no file or transport — sanitization is undermined.

**The fix is a Pino transport / file destination** with rotation. Pino is already what Fastify uses by default — point it at a rotating file in addition to stdout.

---

## Success criteria

### Code
1. **UUID req.id.** In whatever file constructs the Fastify instance (likely `apps/api/src/buildApp.ts` or `apps/api/src/server.ts`), add:
   ```ts
   import { randomUUID } from 'node:crypto';
   const app = Fastify({
     // ...existing options
     genReqId: () => randomUUID(),
   });
   ```
   Confirm no existing `genReqId` override is being silently shadowed.

2. **Persistent log transport.** Add a Pino file destination with rotation. Recommended: use `pino` built-in `transport` option with `pino-roll` (Pino's official rotating-file target). If `pino-roll` isn't installed, add it as a dep — it's official + small + maintained.
   ```ts
   logger: {
     transport: {
       targets: [
         { target: 'pino-pretty', options: { ... } },  // keep stdout pretty in dev
         { target: 'pino-roll', options: { file: 'logs/api.log', frequency: 'daily', size: '10m', limit: { count: 7 } } }
       ]
     }
   }
   ```
   Log directory: `D:\BuildAR\apps\api\logs\` — confirm it's gitignored before committing. If not, add `apps/api/logs/` to `.gitignore`.
   Keep it simple — 7-day retention, 10MB per file, daily rotation is fine for Stage 1.

3. **No regression.** All 18 existing tests must still pass. No new test required for the UUID change (trivially correct), but consider 1 sanity assertion that two consecutive `req.id` values are NOT lexicographically adjacent.

### Tests
4. Add 1 test minimum:
   - Assert two `req.id` values from two consecutive requests are valid UUIDs (regex `/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i`) AND not equal.
5. Existing 18/18 must still pass.

---

## What NOT to do

- Do NOT change the sanitizer or any route file (other than imports/factory wiring if needed).
- Do NOT swap the logger library — stick with Pino (Fastify's default).
- Do NOT widen the log to capture PII or request bodies — just the existing error log shape with the new UUID.
- Do NOT add log-shipping to a remote service (SaaS, Loki, etc.) — that's a separate Stage 2 task.
- Do NOT push to GitHub.
- Do NOT touch the feat/mobile-shell branch.
- Do NOT modify `tasks/active_tasks.json`.
- Do NOT address the type-parity MINOR — still separate.

---

## Infrastructure vs Design (per CLAUDE.md Rubric)

**Infrastructure:**
- Confirm `apps/api/logs/` is gitignored (add if missing).
- Confirm log rotation actually rotates by writing >10MB synthetically OR rely on the library docs — note which.
- If `pino-roll` requires a peer dep or specific Node version, note it.

**Design:**
- Document the log retention policy briefly in `BKM/sop_infra.md` (or create the file if missing — Dev's startup protocol already references it).
- Decide once: are dev-machine logs shipped or local-only? (Local-only is the right call for Stage 1.)

---

## Commit strategy

1 commit on `feat/orchestrator-mvp`:
```
feat(api): UUID request IDs + persistent rotating logs

- genReqId now uses crypto.randomUUID (closes Jasmin S1-013 MINOR — sequential req-N enabled enumeration)
- pino-roll transport writes apps/api/logs/api.log with daily/10mb rotation, 7-day retention
- 1 new test asserts UUID shape + uniqueness across two requests
- closes both pre-prod hardening items from Jasmin S1-013 QA
```

NOT pushed.

---

## Reporting

Write to `D:\Claude Playground\agents\andy\inbox\yoni_s1_014_done.md`:
- Commit SHA + git log --oneline (since branch tip)
- Files touched (incl. .gitignore + BKM update if applicable)
- Test count (target ≥19; was 18)
- 2 actual req.id values from a live request (to prove they're UUIDs and unequal)
- Log rotation policy in plain English
- Status: DONE or BLOCKED

Telegram when done:
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-014" "API hardening shipped (UUID req.id + rotating logs). <test counts>. Report at agents/andy/inbox/yoni_s1_014_done.md."
```

---

## Constraints

- **Repo:** `D:\BuildAR\` on `feat/orchestrator-mvp` branch.
- **You are the ONLY agent in `D:\BuildAR\` right now.** Sequential.
- **Token discipline:** target ≤200 tool uses. This is small.

After you: Jasmin re-QA (UUID format check + log file exists + rotation policy reasonable).

— Andy
