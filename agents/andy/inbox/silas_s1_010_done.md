# Silas — BuildAR Pro Sprint 1, BUILDAR-S1-010 (DONE)

**To:** Andy
**From:** Silas (Database Architect)
**Date:** 2026-05-17
**Task:** BUILDAR-S1-010 — Events Schema Alignment (Migration 0006)
**Branch:** `feat/events-schema-alignment` off `main` in `D:\BuildAR\` (NOT pushed)
**Commit:** `9a5f36b feat(db): 0006 events schema alignment + sessions.current_step_id`
**Status:** DONE — awaiting Inon to paste SQL into Supabase SQL Editor, then Jasmin SQL review + behavioral QA.

---

## 1. Deliverables

| File | Purpose |
|------|---------|
| `D:\BuildAR\supabase\migrations\0006_events_schema_alignment.sql` | Adds events.{project_id, step_id, payload}, drops NOT NULL on events.session_id, extends event_type CHECK with 'session_resumed', backfills payload from metadata, adds 2 indexes, AND adds sessions.current_step_id with backfill from current_step_index. Fully idempotent. |
| `agents/andy/inbox/silas_s1_010_done.md` | This report. |

Branch `feat/events-schema-alignment` is clean — one commit, one new file.

**NIT-1 + NIT-2: SKIPPED.** Reason: the target files (`apps/api/src/routes/orchestrator.ts` and `packages/utils/src/events.ts`) **do not exist on `main`**. Yoni's S1-008/S1-009 work (orchestrator route + events helper) lives on `feat/orchestrar-mvp` and has not been merged. Adding doc-only comments to non-existent files would create the files prematurely on the wrong branch. Recommendation: Andy schedules NIT-1 + NIT-2 as a 1-line follow-up Yoni dispatch attached to whichever PR lands the orchestrator code. See §6 for the exact 2-line diff Yoni would apply.

---

## 2. What the migration changes

### `public.events`
- `+ project_id  uuid` REFERENCES `projects(id)`       ON DELETE SET NULL
- `+ step_id     uuid` REFERENCES `project_steps(id)`  ON DELETE SET NULL
- `+ payload     jsonb` (named to match the brief; backfilled from `metadata`)
- `* session_id` NOT NULL → NULLABLE (top-of-funnel events)
- `* event_type` CHECK extended with `'session_resumed'`
- `+ events_project_id_idx` btree on `project_id`
- `+ events_step_id_idx`    btree on `step_id`

### `public.sessions`
- `+ current_step_id  uuid` REFERENCES `project_steps(id)`
  (bare FK, no ON DELETE — matches existing `sessions.step_id` pattern from 0001)
- backfilled from the existing `(project_id, current_step_index)` join

### What is NOT changed
- `events.metadata` jsonb is **retained** as a sibling to the new `payload` column. Drop is deferred to a follow-up once Yoni's helper writes exclusively to `payload`.
- `sessions.current_step_index` int is **retained** as a sibling to the new `current_step_id` uuid. Drop is deferred once application code reads exclusively from `current_step_id`.
- All other tables, RLS policies, functions, and triggers are untouched.

---

## 3. SQL block — paste into Supabase SQL Editor (migration 0006)

```sql
-- ============================================================
-- BuildAR Pro — 0006_events_schema_alignment
-- BUILDAR-S1-010 — align events with orchestrator helper signature
-- ============================================================

BEGIN;

-- 1. events: add project_id, step_id, payload columns
ALTER TABLE public.events
  ADD COLUMN IF NOT EXISTS project_id uuid
    REFERENCES public.projects(id)      ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS step_id    uuid
    REFERENCES public.project_steps(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS payload    jsonb;

-- 2. events: backfill payload from metadata (idempotent)
UPDATE public.events
   SET payload = metadata
 WHERE payload IS NULL
   AND metadata IS NOT NULL;

-- 3. events: drop NOT NULL on session_id (top-of-funnel events)
ALTER TABLE public.events
  ALTER COLUMN session_id DROP NOT NULL;

-- 4. events: extend event_type CHECK with 'session_resumed'
ALTER TABLE public.events
  DROP CONSTRAINT IF EXISTS events_event_type_check;

ALTER TABLE public.events
  ADD CONSTRAINT events_event_type_check
  CHECK (event_type IN (
    'session_started',
    'session_resumed',
    'step_viewed',
    'step_completed',
    'assistant_invoked',
    'session_completed'
  ));

-- 5. events: indexes on new FK columns
CREATE INDEX IF NOT EXISTS events_project_id_idx
  ON public.events(project_id);

CREATE INDEX IF NOT EXISTS events_step_id_idx
  ON public.events(step_id);

-- 6. sessions: add current_step_id + backfill from current_step_index
ALTER TABLE public.sessions
  ADD COLUMN IF NOT EXISTS current_step_id uuid
    REFERENCES public.project_steps(id);

UPDATE public.sessions s
   SET current_step_id = ps.id
  FROM public.project_steps ps
 WHERE ps.project_id = s.project_id
   AND ps.step_index = s.current_step_index
   AND s.current_step_id IS NULL;

COMMIT;
```

---

## 4. Verification queries — paste-ready

### Query 1 — new columns on events

```sql
SELECT column_name, data_type, is_nullable
  FROM information_schema.columns
 WHERE table_schema = 'public'
   AND table_name   = 'events'
   AND column_name IN ('payload', 'project_id', 'step_id', 'session_id')
 ORDER BY column_name;
```

**Expected (4 rows):**

| column_name | data_type | is_nullable |
|---|---|---|
| payload | jsonb | YES |
| project_id | uuid | YES |
| session_id | uuid | YES |
| step_id | uuid | YES |

The `session_id` row going from `NO` to `YES` is the load-bearing signal that the DROP NOT NULL landed.

### Query 2 — event_type CHECK includes session_resumed

```sql
SELECT conname, pg_get_constraintdef(oid) AS definition
  FROM pg_constraint
 WHERE conname = 'events_event_type_check';
```

**Expected (1 row):** the `definition` column should contain the literal substring `'session_resumed'`.

### Query 3 — FKs on new event columns target the right parents with SET NULL

```sql
SELECT
  c.conname,
  c.confdeltype,        -- 'n' = SET NULL
  t.relname  AS table_name,
  a.attname  AS column_name
FROM pg_constraint c
JOIN pg_class      t ON t.oid = c.conrelid
JOIN pg_attribute  a ON a.attrelid = c.conrelid
                      AND a.attnum = ANY (c.conkey)
WHERE c.contype = 'f'
  AND c.conrelid = 'public.events'::regclass
  AND c.conname IN ('events_project_id_fkey', 'events_step_id_fkey')
ORDER BY c.conname;
```

**Expected (2 rows):**

| conname | confdeltype | table_name | column_name |
|---|---|---|---|
| events_project_id_fkey | n | events | project_id |
| events_step_id_fkey | n | events | step_id |

### Query 4 — new indexes exist

```sql
SELECT indexname, indexdef
  FROM pg_indexes
 WHERE schemaname = 'public'
   AND tablename  = 'events'
   AND indexname IN ('events_project_id_idx', 'events_step_id_idx')
 ORDER BY indexname;
```

**Expected (2 rows):** indexes named `events_project_id_idx` and `events_step_id_idx`.

### Query 5 — sessions.current_step_id exists, uuid, nullable

```sql
SELECT column_name, data_type, is_nullable
  FROM information_schema.columns
 WHERE table_schema = 'public'
   AND table_name   = 'sessions'
   AND column_name  = 'current_step_id';
```

**Expected (1 row):** `current_step_id | uuid | YES`

### Query 6 — sessions backfill is complete (no orphan sessions)

```sql
SELECT COUNT(*) AS unbackfilled_count
  FROM public.sessions s
  JOIN public.project_steps ps
    ON ps.project_id = s.project_id
   AND ps.step_index = s.current_step_index
 WHERE s.current_step_id IS NULL;
```

**Expected:** `unbackfilled_count = 0`

Reads "for every session that has a project_steps row matching its (project_id, current_step_index) pair, current_step_id should now be populated." Zero violations means the backfill landed.

### Query 7 — payload backfill is complete

```sql
SELECT COUNT(*) AS missing_payload_count
  FROM public.events
 WHERE metadata IS NOT NULL
   AND payload  IS NULL;
```

**Expected:** `missing_payload_count = 0`

---

## 5. Idempotency posture

Re-applying 0006 against an already-migrated database is a no-op:

- `ADD COLUMN IF NOT EXISTS` — safe.
- `UPDATE ... WHERE payload IS NULL` and `WHERE current_step_id IS NULL` — re-runs touch zero rows once the backfill has happened.
- `ALTER COLUMN ... DROP NOT NULL` — silently no-op if already nullable.
- `DROP CONSTRAINT IF EXISTS events_event_type_check` followed by `ADD CONSTRAINT` — re-creates the same CHECK; if rows have been inserted with the legacy enum only, they still satisfy the extended enum (superset).
- `CREATE INDEX IF NOT EXISTS` — safe.

If Inon re-pastes the block by accident, no harm done.

---

## 6. NIT-1 + NIT-2 — exact diff for the future Yoni dispatch

Both target files do not exist on `main` (Yoni's S1-008/S1-009 lives on `feat/orchestrar-mvp`). When Andy lands that branch, attach this 1-line-each diff:

### NIT-1: `apps/api/src/routes/orchestrator.ts`
After Zod validation, before the Safety call, insert this comment:
```ts
// Note: the 2000-char question cap is the only input mitigation;
// Safety system prompt's instruction-following is the actual safety boundary.
```

### NIT-2: `packages/utils/src/events.ts`
Near the `if (!input.session_id)` early-drop branch, insert this comment:
```ts
// Top-of-funnel events (session_id=null) are silently dropped today
// because events.session_id is NOT NULL. Re-evaluate after migration 0006
// drops the NOT NULL constraint — at that point this branch can record.
```

Commit message: `docs(comments): NIT-1 + NIT-2 from Jasmin S1+S2 QA (orchestrator injection note, events helper migration note)`

**Important:** by the time Yoni applies NIT-2, the comment's "after migration 0006" should be rewritten as "now that migration 0006 has dropped the NOT NULL constraint, this branch should be removed and the helper should write the row instead of silently dropping it." That's a behavioural change beyond a doc-only NIT, so it belongs to Yoni's helper-update follow-up, not to the comment-only NIT.

---

## 7. Design rationale on the two judgment calls

### (a) Retain `events.metadata` instead of renaming to `payload`

Yoni's schema_request implied a rename. I added `payload` as a sibling and backfilled it. Reasons:

1. **Zero-downtime.** Any analytics dashboard, view, or function currently reading `metadata->>'whatever'` keeps working post-migration. A rename would break readers the instant the migration commits.
2. **Reversible.** If something is found pointing at metadata that we missed, the column is still there. A 0007 drop after Yoni's helper switches to payload is cheap.
3. **Adapter shrink path is clean.** Yoni's helper rewrites to write `payload` directly; existing metadata-based queries continue against the legacy column until they're individually migrated.

### (b) Retain `sessions.current_step_index` instead of dropping

Same reasoning. The orchestrator can begin reading via `current_step_id` immediately, but any background job or admin query that reads `current_step_index` keeps working until separately ported. Drop is queued in §FOLLOW-UPS at the bottom of the migration file.

### (c) Bare FK on `sessions.current_step_id` (no ON DELETE)

Default NO ACTION will block deletion of a `project_steps` row that's still pointed at by a live session. That's correct: if you're trying to delete a step while a session is currently on it, the right answer is to drain/close the session first. SET NULL would silently strand the session; CASCADE would delete the session (way too aggressive). NO ACTION = surface the conflict to the admin. This matches the pattern Yoni used for `sessions.step_id` in 0001.

---

## 8. Constraints honored

- Repo: `D:\BuildAR\`
- Branch: `feat/events-schema-alignment` off `main`, one new file, one commit, **NOT pushed**.
- Migration NOT applied to live DB — Inon pastes via Supabase SQL Editor (per 0003/0004/0005 pattern).
- Single agent in repo (Yoni's branch is already done, no concurrent edits — verified `git status` clean before branching).
- Style matches 0004: header block, BEGIN/COMMIT, verification queries inline as comments.
- Idempotent: `IF NOT EXISTS`, `DROP CONSTRAINT IF EXISTS`, gated UPDATE.

---

## 9. Open questions / follow-ups for Andy

1. **NIT-1 + NIT-2 scheduling.** Attach the 2-line diff in §6 to whichever PR lands `feat/orchestrar-mvp` (Yoni's S1-008/009 branch). Not blocking 0006.
2. **Helper passthrough rewrite.** Once Inon applies 0006, Yoni's `packages/utils/src/events.ts` should drop the metadata-folding logic and the silent-drop branch. Recommend that as a small Yoni dispatch (~10-line diff) right after Jasmin signs off 0006 — keeps the schema and helper in lockstep.
3. **`events.metadata` drop.** Once §helper-rewrite is in and you've grepped every consumer for `metadata` references, schedule `0007_drop_events_metadata.sql`. Same story for `sessions.current_step_index`.
4. **Constraint name sanity.** The Postgres auto-name for the 0001 inline CHECK is reliably `events_event_type_check`, but `DROP CONSTRAINT IF EXISTS` makes the migration safe even if the auto-name ever differs in a fresh clone. Jasmin may want to confirm against the live DB before paste.

---

## 10. Handoff

Andy: paste-ready SQL is in §3, verification in §4. Surface to Inon via Telegram when he's at the desk. After he confirms applied + Queries 1-7 land the expected output, dispatch Jasmin for SQL review + behavioral QA (a real INSERT with `event_type='session_resumed'` and a NULL `session_id` should now succeed; before the migration it would have raised 23514 / 23502).

Status: **DONE.**

— Silas
