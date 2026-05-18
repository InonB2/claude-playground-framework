# Silas — BuildAR Pro Sprint 1, BUILDAR-S1-010 (Events Schema Alignment)

**From:** Andy
**Dispatched:** 2026-05-17
**Task:** BUILDAR-S1-010 — Migration 0006 to align live events table with the schema Yoni's orchestrator code already assumes
**Bundled doc-fixes:** NIT-1 (orchestrator injection-mitigation comment) + NIT-2 (recordEvent dropped-event comment) — see §3 below
**Model:** Opus 4.7
**Tester:** Jasmin

---

## Why now

Yoni's S1-009 telemetry helper writes via an **adapter** because the live events table doesn't match the brief:
- Missing columns: `project_id`, `step_id`, `payload`
- Missing enum value: `session_resumed`
- `session_id` is NOT NULL but brief expected nullable
- `sessions.current_step_id` doesn't exist — only `current_step_index`

The adapter folds extras into `metadata` jsonb (lossless), but analytics queries against `metadata->>'project_id'` are clunky vs proper columns. Jasmin signed off the adapter as a stopgap and queued this task for cleanup.

When this migration ships + Yoni updates the adapter (small follow-up), the helper becomes a 5-line passthrough.

**This is sequential after Yoni's mobile shell (just completed).** No concurrent agents in `D:\BuildAR\` per `feedback_parallel_agents_shared_repo` memory.

---

## Yoni's proposed SQL (source of truth)

Full schema_request: `D:\Claude Playground\agents\yoni\scratchpad\schema_request.md` — read it first.

His proposal in summary:

```sql
ALTER TABLE public.events
  ADD COLUMN IF NOT EXISTS project_id uuid REFERENCES public.projects(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS step_id    uuid REFERENCES public.project_steps(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS payload    jsonb;

UPDATE public.events SET payload = metadata WHERE payload IS NULL;

ALTER TABLE public.events ALTER COLUMN session_id DROP NOT NULL;

ALTER TABLE public.events DROP CONSTRAINT events_event_type_check;
ALTER TABLE public.events ADD CONSTRAINT events_event_type_check
  CHECK (event_type IN (
    'session_started', 'session_resumed', 'step_viewed',
    'step_completed', 'assistant_invoked', 'session_completed'
  ));

CREATE INDEX IF NOT EXISTS events_project_id_idx ON public.events(project_id);
CREATE INDEX IF NOT EXISTS events_step_id_idx    ON public.events(step_id);
```

Plus optional:
```sql
ALTER TABLE public.sessions
  ADD COLUMN IF NOT EXISTS current_step_id uuid REFERENCES public.project_steps(id);
UPDATE public.sessions s SET current_step_id = ps.id
FROM public.project_steps ps
WHERE ps.project_id = s.project_id AND ps.step_index = s.current_step_index;
```

---

## What I want from you

### 1. Migration 0006 — `D:\BuildAR\supabase\migrations\0006_events_schema_alignment.sql`

Take Yoni's SQL above and:

- **Wrap in BEGIN/COMMIT** (same style as 0003 + 0004).
- **Apply ALL of it including the optional sessions.current_step_id** — Jasmin's verdict said the orchestrator's step lookup becomes a single join with this column instead of per-call resolution. Worth the small cost now to avoid a follow-up migration.
- **Verify backfill is correct** — your job to confirm the UPDATE statements work as intended without orphaning data.
- **Idempotent:** `ADD COLUMN IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, `DROP CONSTRAINT ... IF EXISTS` before re-adding. Standard pattern.
- **Verification queries as comments inline** at the bottom of the file — same style as 0004.

### 2. Done-report deliverables — `D:\Claude Playground\agents\andy\inbox\silas_s1_010_done.md`

Same structure as your `silas_phase_b_done.md`:
- File paths
- Paste-ready SQL block for Inon (Supabase Dashboard SQL Editor)
- Verification queries (paste-ready) with expected output
- Open questions or follow-ups
- Status: DONE or BLOCKED

### 3. Bundled doc-only fixes (no code logic change)

Two NIT items from Jasmin's QA. You're a database architect, not a TypeScript engineer — but these are 1-line comment additions in TS files and adding them while you're already in the repo saves a separate Yoni dispatch. If you're uncomfortable touching TS, skip and note in your report.

**NIT-1 (optional):** In `D:\BuildAR\apps\api\src\routes\orchestrator.ts`, near the top of the handler (after Zod validation, before the Safety call), add a one-line comment:
```ts
// Note: the 2000-char question cap is the only input mitigation;
// Safety system prompt's instruction-following is the actual safety boundary.
```

**NIT-2 (optional):** In `D:\BuildAR\packages\utils\src\events.ts`, near the `if (!input.session_id)` check that drops top-of-funnel events, add a one-line comment:
```ts
// Top-of-funnel events (session_id=null) are silently dropped today
// because events.session_id is NOT NULL. Re-evaluate after migration 0006
// drops the NOT NULL constraint — at that point this branch can record.
```

If you DO touch these files, commit them as a separate commit on the same branch with message:
```
docs(comments): NIT-1 + NIT-2 from Jasmin S1+S2 QA (orchestrator injection note, events helper migration note)
```

---

## Constraints

- **Repo:** `D:\BuildAR\`
- **Branch:** `feat/events-schema-alignment` off main. NOT pushed.
- **Do NOT apply migrations to live DB.** Inon pastes via Supabase SQL Editor (same pattern as 0003/0004/0005).
- **You are the ONLY agent in `D:\BuildAR\` right now.** Yoni just finished. Don't spawn helpers.

---

## When done, send Telegram

```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-010" "Migration 0006 ready (events schema alignment + sessions.current_step_id). Paste-ready SQL in agents/andy/inbox/silas_s1_010_done.md. NIT-1+NIT-2: <applied|skipped>"
```

---

## What happens after you finish

Andy dispatches Vera (mobile UI/UX QA against Lena's brief) then Jasmin (code+security QA on mobile shell + S1-010 SQL review) sequentially. Three agents max before we're ready to merge everything to main + close Gate B.

— Andy
