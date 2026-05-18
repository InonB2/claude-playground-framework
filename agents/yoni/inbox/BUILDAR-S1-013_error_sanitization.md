# Yoni — BuildAR Pro S1-013: PostgREST error sanitization (Phase B carry-forward)

**From:** Andy
**Dispatched:** 2026-05-18
**Task:** BUILDAR-S1-013 — closes Jasmin S1-006 MINOR from Wave 1 QA
**Branch:** continue on `feat/orchestrator-mvp` (extend with 1 commit)
**Tester:** Jasmin

---

## Why this matters

When you shipped S1-006 (API routes), Jasmin QA'd and found 2 MINORs. One of them: **PostgREST error.message is forwarded verbatim** to the client. Quote from her report:

> PostgREST `error.message` forwarded verbatim — sanitize in Phase B.

PostgREST error messages can leak schema details (column names, constraint names, type info, sometimes hint snippets) that help a hostile client probe the data model. The fix is: log the full error server-side, return only a safe shape to the client.

Other Jasmin MINOR from S1-006 (type-parity assertions for ProjectStep/Asset/Event/ProjectWithSteps/UpdateSessionBody) is a separate larger task — NOT in scope here.

---

## Success criteria

### Code (small, surgical)
1. **Identify every `throw` or response path that includes PostgREST error data.** Likely in `apps/api/src/routes/projects.ts`, `sessions.ts`, `events.ts`, and the orchestrator's `assist` route. Grep for `error.message`, `error.code`, `error.details`, `error.hint`.
2. **Sanitize on the way out.** Replace each verbatim forwarding with a generic shape:
   ```ts
   {
     error: "DatabaseError",   // or 'BadRequest', 'NotFound' — map from PostgREST codes
     message: "Could not complete the request.",   // safe, user-facing
     requestId: <short random or correlation id>    // for log lookup
   }
   ```
3. **Log the full PostgREST error server-side** with the same `requestId`. Use the existing logger (Fastify's req.log).
4. **Preserve HTTP status semantics.** PostgREST 404 → 404, 409 conflict → 409, 23505 unique violation → 409, 22P02 invalid_text_representation → 400, default → 500. Don't collapse everything to 500.
5. **No new dependency.** Pure code change.

### Tests
6. Add 3 tests minimum in `apps/api/src/__tests__/`:
   - 404 path returns 404 with sanitized body (no schema leak)
   - Validation failure (e.g., missing required field) returns 400 with sanitized body
   - 5xx path returns 500 with sanitized body + requestId
7. Existing 5/5 smoke tests must still pass.

---

## What NOT to do

- Do NOT add a type-parity assertion test for ProjectStep/Asset/Event/ProjectWithSteps/UpdateSessionBody — that's the other Jasmin MINOR, separate task.
- Do NOT change route signatures, request validators, or domain types.
- Do NOT touch the mobile-shell branch.
- Do NOT push to GitHub.
- Do NOT modify `tasks/active_tasks.json`.

---

## Infrastructure vs Design (per CLAUDE.md Rubric)

**Infrastructure:** Confirm the existing logger writes to a location that's retained (server-side logs). If logger output is ephemeral (console only) and there's no log file or structured-log shipping yet, note it as a finding — sanitization is undermined if there's no server-side audit trail to look up by requestId.

**Design:** Document the error shape contract at the top of whatever utility file you create (e.g., `apps/api/src/lib/errors.ts`). Decide once whether `requestId` is generated per-request by Fastify middleware (preferred — already wired) or per-error (works but more code).

---

## Commit strategy

1 commit on `feat/orchestrator-mvp`:
```
feat(api): sanitize PostgREST errors before returning to client

- new lib/errors.ts maps PostgREST codes → safe client shape + status
- routes use sanitizeError() on all DB error paths
- full error logged server-side with requestId for lookup
- 3 new tests cover 404 / 400 / 500 paths
- closes Jasmin S1-006 MINOR (Wave 1 QA carry-forward)
```

NOT pushed.

---

## Reporting

Write to `D:\Claude Playground\agents\andy\inbox\yoni_s1_013_done.md`:
- Commit SHA + git log --oneline (since branch tip)
- Files touched
- Test count (target: at least 8 passing — 5 baseline + 3 new)
- Error shape contract (paste the type)
- Status code mapping table
- Status: DONE or BLOCKED

Telegram when done:
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-013" "PostgREST error sanitization shipped. <test counts>. Report at agents/andy/inbox/yoni_s1_013_done.md."
```

---

## Constraints

- **Repo:** `D:\BuildAR\` on `feat/orchestrator-mvp` branch (different from feat/mobile-shell — switch back).
- **You are the ONLY agent in `D:\BuildAR\` right now.** Sequential.
- **Token discipline:** target ≤200 tool uses.

After you: Jasmin re-QA on this specific sanitization.

— Andy
