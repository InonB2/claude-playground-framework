# Schema Request — Yoni → Silas (via Andy)

**From:** Yoni
**Date:** 2026-05-17
**Context:** BUILDAR-S1-008 / S1-009 (Orchestrator MVP + Telemetry)
**Status:** Not blocking — Yoni adapted around it; see "Workaround" below.

## What the S1-008/009 brief assumes vs what the DB has

The brief (`agents/yoni/inbox/BUILDAR-S1-008_orchestrator_mvp.md`)
specifies the `recordEvent` helper signature:

```ts
recordEvent(input: {
  event_type: 'session_started' | 'session_resumed' | 'step_viewed'
            | 'step_completed' | 'assistant_invoked' | 'session_completed',
  user_id: string,
  session_id: string | null,
  project_id: string | null,
  step_id: string | null,
  payload: Record<string, unknown>
})
```

But `public.events` (0001_schema_init.sql) is:

```sql
CREATE TABLE public.events (
  id          uuid PRIMARY KEY,
  session_id  uuid NOT NULL REFERENCES sessions(id),
  user_id     uuid NOT NULL REFERENCES profiles(id),
  event_type  text CHECK (event_type IN (
                'session_started', 'step_viewed', 'step_completed',
                'assistant_invoked', 'session_completed')),  -- NO session_resumed
  step_index  int,
  metadata    jsonb,
  created_at  timestamptz
);
```

Concrete deltas:

| Field needed by brief | DB reality | Impact |
|---|---|---|
| `event_type = 'session_resumed'` | Not in CHECK | INSERT would 23514 |
| `session_id` nullable | NOT NULL | Cannot record top-of-funnel events with no session |
| `project_id` column | Absent | Caller's project_id has nowhere to live |
| `step_id` (uuid) column | Only `step_index` (int) exists | Cannot store the UUID directly |
| `payload` column name | Column is `metadata` | Naming mismatch only |

The PATCH /sessions/:id wiring in S1-009 also assumes
`current_step_id` (uuid) on sessions; live schema has
`current_step_index` (int). Same root cause: brief was written
against a planned schema, not the shipped one.

## Workaround (already shipped on `feat/orchestrar-mvp`)

`packages/utils/src/events.ts` accepts the brief's signature unchanged
and adapts at write time:
- `event_type='session_resumed'` is folded to `'step_viewed'` +
  `metadata.resumed = true`.
- `project_id` (uuid) is folded into `metadata.project_id`.
- `step_id` (uuid) is folded into `metadata.step_id`; numeric
  `step_index` is accepted as an optional sibling and used as the
  real column.
- `payload` is written into `metadata`.
- If `session_id` is null, the helper logs and drops the event
  (session_id NOT NULL would otherwise crash).

This keeps `recordEvent`'s public signature forward-compatible: when
Silas ships the schema below, the helper switches to native columns
with zero API caller change.

## What I'd like Silas to ship

Migration `0006_events_schema_alignment.sql`:

```sql
ALTER TABLE public.events
  ADD COLUMN IF NOT EXISTS project_id uuid REFERENCES public.projects(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS step_id    uuid REFERENCES public.project_steps(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS payload    jsonb;

-- Backfill payload from metadata so the rename is transparent.
UPDATE public.events SET payload = metadata WHERE payload IS NULL;

-- Allow events that aren't bound to a session (rare, but the brief
-- explicitly says session_id should be nullable).
ALTER TABLE public.events ALTER COLUMN session_id DROP NOT NULL;

-- Extend the event_type CHECK to include 'session_resumed'.
ALTER TABLE public.events DROP CONSTRAINT events_event_type_check;
ALTER TABLE public.events ADD CONSTRAINT events_event_type_check
  CHECK (event_type IN (
    'session_started', 'session_resumed', 'step_viewed',
    'step_completed', 'assistant_invoked', 'session_completed'
  ));

CREATE INDEX IF NOT EXISTS events_project_id_idx ON public.events(project_id);
CREATE INDEX IF NOT EXISTS events_step_id_idx    ON public.events(step_id);
```

And a small change to `public.sessions` if we want true step-id linkage:

```sql
-- OPTIONAL but recommended — lets the orchestrator load the current step
-- with one join instead of a step_index lookup.
ALTER TABLE public.sessions
  ADD COLUMN IF NOT EXISTS current_step_id uuid REFERENCES public.project_steps(id);
-- Backfill from current_step_index.
UPDATE public.sessions s SET current_step_id = ps.id
FROM public.project_steps ps
WHERE ps.project_id = s.project_id AND ps.step_index = s.current_step_index;
```

If Silas approves only the events alignment and not the sessions
change, the orchestrator still works — it just keeps resolving
`step_id` UUID → `step_index` per call.

## Open question for Andy

Should we also extend `core-types.EventType` to include
`'session_resumed'` *before* Silas ships the migration, so the
public type and the DB align in one PR rather than two? My
preference: yes, ship in the same PR as the migration — keeps the
type the source of truth.

— Yoni
