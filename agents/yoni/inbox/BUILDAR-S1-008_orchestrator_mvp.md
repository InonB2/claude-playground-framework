# Yoni — BuildAR Pro Sprint 1, Wave 1 (Orchestrator MVP + Telemetry)

**From:** Andy
**Dispatched:** 2026-05-17
**Tasks:** BUILDAR-S1-008 (Orchestrator MVP) + BUILDAR-S1-009 (Telemetry wiring)
**Model:** Opus 4.7
**Tester:** Jasmin (code, security, contract conformance)

---

## Why this matters

Gate B = "Product loop accepted" cannot close until a user can ask the in-app assistant a question mid-session AND the team can inspect event telemetry. The mobile shell (your next wave) depends on a stable orchestrator contract, so we ship orchestrator first. Both pieces are pure backend — no device build required, no UI to test by hand — so they're the right thing to do autonomously while Inon is away.

You already shipped the 4 API routes + types + Zod validation last sprint (BUILDAR-S1-006 — Jasmin PASS WITH NOTES). This wave extends apps/api with one more route, adds the ai-client package, and wires events.

---

## BUILDAR-S1-008 — Orchestrator MVP

### What to build

1. **`packages/ai-client`** — new package in the monorepo.
   - Wraps Anthropic SDK calls.
   - Exposes one function: `assist(input: AssistRequest): Promise<AssistResponse>` (types live in `@buildar/core-types`).
   - Internally constructs the prompt from: system prompt (cached), Tutor agent system message (cached), Safety agent system message (cached), then the per-call context (session + project + step + user question — uncached).
   - Use `cache_control: { type: "ephemeral" }` on all 3 static blocks per Anthropic prompt caching docs. This is the cost-control discipline the Perplexity plan calls out (`01-claude-code-master-instructions.md` § LLM and orchestrator discipline).
   - Model: `claude-sonnet-4-6` for assist calls (good quality/cost balance for tutor work). Make the model name a constant at the top of the file so it's easy to swap.
   - Retries: 2 retries on 429/5xx with exponential backoff (200ms, 800ms). Log each retry.
   - Timeout: 30s per call. On timeout, return a graceful error response, not a thrown exception.
   - Reads `ANTHROPIC_API_KEY` from env. Throws on boot if missing.

2. **Tutor agent system prompt** — concise, single string constant in `packages/ai-client/src/agents/tutor.ts`.
   - Role: a patient DIY assistant for a person physically doing the task in the moment.
   - Style: short paragraphs, plain language, no markdown headings, ≤ 4 sentences per response unless safety dictates more.
   - Constraints: do not invent steps that aren't in the project's step list. If unsure, say so and suggest the user re-read the current step.

3. **Safety agent system prompt** — separate constant in `packages/ai-client/src/agents/safety.ts`.
   - Runs as a **pre-check** on the user's question, NOT as a post-filter on Tutor's answer. (One round-trip per assist call.)
   - Decides one of: `proceed`, `warn-and-proceed`, `block`.
   - `block` reasons: tool misuse with imminent injury risk (e.g., "can I use a power drill on a live wire"), instructions that would damage the dwelling (e.g., load-bearing wall demolition without permit), explicit harm to self/others.
   - Returns: `{ verdict, reason }` JSON. Implement via a small structured-output call.

4. **`POST /api/v1/orchestrator/assist` endpoint** — new route in `apps/api/src/routes/orchestrator.ts`.
   - Auth required (existing JWT middleware — same pattern as your sessions routes).
   - Zod input schema (in `packages/validation`): `{ session_id: uuid, step_id: uuid | null, question: string (max 2000) }`.
   - Flow:
     1. Validate input (Zod).
     2. Load session, project, current step from DB. If session not owned by user → 404 (not 403, per the convention you established in S1-006).
     3. Run Safety check on the question. If `block`, return 200 with `{ blocked: true, reason }` — do not call Tutor.
     4. If `warn-and-proceed` or `proceed`, call Tutor with full context.
     5. Insert an `event` row: `event_type = 'assistant_invoked'`, payload includes safety verdict, question length, latency, model. (Telemetry — see S1-009.)
     6. Return `{ blocked: false, response: string, safety: { verdict, reason } }`.
   - Errors: any unhandled exception returns 500 with `{ error: "Internal error" }` — DO NOT forward PostgREST error.message verbatim (Jasmin's S1-006 minor #1).

5. **Type-parity assertion** for AssistRequest/AssistResponse (Jasmin's S1-006 minor #2) — add the missing assertions in your existing test file.

### Smoke tests (apps/api/src/__tests__/orchestrator.test.ts)

5 minimum:
- 401 when no JWT
- 400 when question is missing or > 2000 chars
- 404 when session_id is valid UUID but not owned by caller
- 200 with `blocked: true` when Safety returns block (mock the ai-client in this test)
- 200 with `blocked: false` and a non-empty `response` when Tutor proceeds (mock the ai-client)

Use mock for ai-client in tests — do NOT call live Anthropic in CI. Add a separate `npm run test:live` script that DOES call live Anthropic, for manual local sanity. Mark it skip in CI.

### Deliverables

- `packages/ai-client/` complete with tsconfig, package.json, src/index.ts, src/agents/tutor.ts, src/agents/safety.ts
- `packages/validation/` extended with assist input schema
- `packages/core-types/` extended with AssistRequest, AssistResponse, SafetyVerdict types
- `apps/api/src/routes/orchestrator.ts`
- `apps/api/src/__tests__/orchestrator.test.ts`
- All TypeScript strict mode, no `any`, no `@ts-ignore`

---

## BUILDAR-S1-009 — Telemetry wiring

### What to build

1. **Event helper** at `packages/utils/src/events.ts`:
   ```
   export async function recordEvent(input: {
     event_type: 'session_started' | 'session_resumed' | 'step_viewed' | 'step_completed' | 'assistant_invoked' | 'session_completed',
     user_id: string,
     session_id: string | null,
     project_id: string | null,
     step_id: string | null,
     payload: Record<string, unknown>
   }): Promise<void>
   ```
   - Inserts into `events` table using the user's JWT (RLS-respecting).
   - Never throws on telemetry failure — log the error and continue. Telemetry must not break user flows.

2. **Wire it into existing routes** (don't refactor — just add the calls):
   - `POST /sessions` → after successful insert, call `recordEvent('session_started')`.
   - `PATCH /sessions/:id` →
     - if `current_step_id` changed, `recordEvent('step_viewed')` for the new step
     - if `status` changed to `in_progress` from a previous state, `recordEvent('session_resumed')`
     - if `status` changed to `completed`, `recordEvent('session_completed')`
     - if step status indicates completion (your existing convention), `recordEvent('step_completed')`
   - The orchestrator route already records `assistant_invoked` in S1-008. Use this helper there too.

3. **Smoke tests**: extend existing sessions.test.ts to assert event rows are created. 2 tests minimum (start, complete).

### Deliverables

- `packages/utils/src/events.ts`
- Modifications to existing sessions route + orchestrator route to use it
- Tests assert event row insertion

---

## Definition of done (BOTH tasks)

Before you write your done-report:

1. `pnpm install` clean — no warnings.
2. `pnpm -r lint` passes.
3. `pnpm -r typecheck` passes.
4. `pnpm -r test` passes (orchestrator tests use mocks).
5. `apps/api` boots locally (`pnpm --filter @buildar/api dev` should print "API listening on :3000" or similar without errors).
6. Manual live test (you do this once before reporting done): make one curl call with a valid JWT to `/api/v1/orchestrator/assist` with a real question on a real session. Confirm: response returns, event row appears in `events` table. Capture the response in your done-report.
7. `git diff --stat` — paste the file list in your done-report.

---

## Constraints

- **Repo:** `D:\BuildAR\`
- **Branch:** Create `feat/orchestrator-mvp` off main. Do NOT push to main directly.
- **Do not modify schema.** If you need a column that doesn't exist, STOP and write a note to `agents/yoni/scratchpad/schema_request.md`, then continue with the rest of the work. Andy will route the schema change to Silas.
- **Do not commit secrets.** ANTHROPIC_API_KEY is in `.env` (gitignored). The CI workflow will pass it as a GitHub Secret — Mack will set that up when needed; for now, document the requirement in your done-report.
- **PostgREST error.message** — sanitize at the boundary. Never forward upstream error strings to the API caller.

---

## Report back to

`agents/andy/inbox/yoni_s1_008_009_done.md` — include:
- Files changed (git diff --stat)
- Test counts (pass/fail)
- Manual live-test transcript (request + response)
- Open questions or follow-ups
- Schema request file path (if any)
- Status: DONE or BLOCKED

Andy will dispatch Jasmin for QA. Your task is closed when Jasmin signs off.

---

## Why these specifically and not the mobile shell

Mobile shell needs ViroReact native build + device testing. Inon is away. Mobile is your Wave 3 — it lands after Jasmin signs off on this wave and the storage bucket is ready (Silas is working on that in parallel today). One stable thing at a time.

— Andy
