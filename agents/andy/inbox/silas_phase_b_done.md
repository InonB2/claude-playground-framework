# Silas — BuildAR Pro Phase B Prereqs (DONE)

**To:** Andy
**From:** Silas (Database Architect)
**Date:** 2026-05-17
**Tasks:** BUILDAR-S2-001 (FK ON DELETE) + BUILDAR-S2-002 (storage bucket + RLS)
**Branch:** `feat/phase-b-prereqs` off `main` in `D:\BuildAR\`
**Status:** DONE — awaiting Inon to paste SQL into Supabase SQL Editor, then Jasmin behavioral QA.

---

## 1. Deliverables

| File | Purpose |
|------|---------|
| `D:\BuildAR\supabase\migrations\0004_fk_ondelete_clauses.sql` | Reaffirms `projects.published_by` ON DELETE SET NULL + `events.user_id` ON DELETE CASCADE. Idempotent. |
| `D:\BuildAR\supabase\migrations\0005_storage_bucket_project_assets.sql` | Creates private `project-assets` bucket + 4 RLS policies on `storage.objects` scoped to that bucket. |
| `agents/andy/inbox/silas_phase_b_done.md` | This report. |

Both migrations live on branch `feat/phase-b-prereqs` (clean — only these two files added).

---

## 2. Important context: overlap with migration 0003

Migration `0003_security_fixes.sql` (shipped 2026-05-16, Fix 3 + Fix 4) **already contains** the same two FK changes that 0004 reaffirms. I deliberately wrote 0004 anyway because:

1. The Phase B plan tracks BUILDAR-S2-001 as its own work item, and migrations should map 1:1 to that audit trail.
2. 0004 is fully idempotent (`DROP CONSTRAINT IF EXISTS` + `ADD CONSTRAINT`). If 0003 has been applied, running 0004 is a safe no-op that just reconfirms the desired end state.
3. **If Inon has NOT applied 0003 yet**, 0004 still lands the FK state correctly on its own.

Practical implication for Andy: if 0003 is still un-applied in the live DB, paste 0003 first, then 0004, then 0005. Otherwise just paste 0004 and 0005.

---

## 3. SQL block #1 — paste into Supabase SQL Editor (migration 0004)

```sql
-- ============================================================
-- BuildAR Pro — 0004_fk_ondelete_clauses
-- BUILDAR-S2-001 — reaffirm FK ON DELETE clauses
-- ============================================================

BEGIN;

-- projects.published_by -> ON DELETE SET NULL
ALTER TABLE public.projects
  DROP CONSTRAINT IF EXISTS projects_published_by_fkey;

ALTER TABLE public.projects
  ADD CONSTRAINT projects_published_by_fkey
  FOREIGN KEY (published_by)
  REFERENCES public.profiles(id)
  ON DELETE SET NULL;

-- events.user_id -> ON DELETE CASCADE
ALTER TABLE public.events
  DROP CONSTRAINT IF EXISTS events_user_id_fkey;

ALTER TABLE public.events
  ADD CONSTRAINT events_user_id_fkey
  FOREIGN KEY (user_id)
  REFERENCES public.profiles(id)
  ON DELETE CASCADE;

COMMIT;
```

### Verification query for block #1

```sql
SELECT
  c.conname,
  c.confdeltype,        -- 'n' = SET NULL, 'c' = CASCADE
  t.relname  AS table_name,
  a.attname  AS column_name
FROM pg_constraint c
JOIN pg_class      t ON t.oid = c.conrelid
JOIN pg_attribute  a ON a.attrelid = c.conrelid
                      AND a.attnum = ANY (c.conkey)
WHERE c.contype = 'f'
  AND c.conname IN ('projects_published_by_fkey', 'events_user_id_fkey')
ORDER BY c.conname;
```

**Expected output (2 rows):**

| conname | confdeltype | table_name | column_name |
|---|---|---|---|
| events_user_id_fkey | c | events | user_id |
| projects_published_by_fkey | n | projects | published_by |

---

## 4. SQL block #2 — paste into Supabase SQL Editor (migration 0005)

```sql
-- ============================================================
-- BuildAR Pro — 0005_storage_bucket_project_assets
-- BUILDAR-S2-002 — private bucket + 4 RLS policies
-- ============================================================

-- 1. Bucket (private, idempotent)
INSERT INTO storage.buckets (id, name, public)
VALUES ('project-assets', 'project-assets', false)
ON CONFLICT (id) DO NOTHING;

-- 2. INSERT (upload) : creators + admins
DROP POLICY IF EXISTS "project_assets_insert_creator_or_admin"
  ON storage.objects;

CREATE POLICY "project_assets_insert_creator_or_admin"
  ON storage.objects
  FOR INSERT
  TO authenticated
  WITH CHECK (
    bucket_id = 'project-assets'
    AND public.is_creator_or_admin()
  );

-- 3. SELECT (read) : any authenticated user
DROP POLICY IF EXISTS "project_assets_select_authenticated"
  ON storage.objects;

CREATE POLICY "project_assets_select_authenticated"
  ON storage.objects
  FOR SELECT
  TO authenticated
  USING (bucket_id = 'project-assets');

-- 4. UPDATE (metadata / overwrite) : admin only
DROP POLICY IF EXISTS "project_assets_update_admin"
  ON storage.objects;

CREATE POLICY "project_assets_update_admin"
  ON storage.objects
  FOR UPDATE
  TO authenticated
  USING (
    bucket_id = 'project-assets'
    AND public.is_admin()
  )
  WITH CHECK (
    bucket_id = 'project-assets'
    AND public.is_admin()
  );

-- 5. DELETE : admin only
DROP POLICY IF EXISTS "project_assets_delete_admin"
  ON storage.objects;

CREATE POLICY "project_assets_delete_admin"
  ON storage.objects
  FOR DELETE
  TO authenticated
  USING (
    bucket_id = 'project-assets'
    AND public.is_admin()
  );
```

### Verification queries for block #2

```sql
-- (a) Bucket exists and is private
SELECT id, name, public
FROM storage.buckets
WHERE name = 'project-assets';
```

**Expected (1 row):**

| id | name | public |
|---|---|---|
| project-assets | project-assets | false |

```sql
-- (b) 4 RLS policies attached
SELECT
  polname,
  polcmd,                                       -- r=SELECT a=INSERT w=UPDATE d=DELETE
  pg_get_expr(polqual,      polrelid) AS using_expr,
  pg_get_expr(polwithcheck, polrelid) AS check_expr
FROM pg_policy
WHERE polrelid = 'storage.objects'::regclass
  AND polname LIKE 'project_assets_%'
ORDER BY polname;
```

**Expected (4 rows):**

| polname | polcmd |
|---|---|
| project_assets_delete_admin | d |
| project_assets_insert_creator_or_admin | a |
| project_assets_select_authenticated | r |
| project_assets_update_admin | w |

---

## 5. FK choice rationale — `events.user_id`

**Chose: ON DELETE CASCADE** (matches the brief, matches Fix 4 in 0003, diverges from Jasmin's earlier "SET NULL" suggestion).

Three reasons:

1. **Schema fact:** `events.user_id` is `NOT NULL` in `0001_schema_init.sql`. SET NULL would force dropping that NOT NULL constraint, which weakens insert-time integrity for live writes and lets future bugs insert orphaned rows that look intentional.
2. **GDPR cleanness:** events are personal activity records (`session_started`, `step_viewed`, `step_completed`, `assistant_invoked`, `session_completed`). Right-to-erasure means they need to disappear when the account does. SET NULL keeps the rows around, which is the exact pattern GDPR audits flag — pseudonymized identifiers in retained behavioral logs still count as personal data when joinable to surrounding tables.
3. **Analytics belong elsewhere:** if the product later needs anonymized aggregate analytics (funnel counts, per-event-type rollups), those should live in a separate analytics table populated by a scheduled job, not as orphaned rows mixed into the live `events` table. Keeping the two concerns separate keeps the GDPR story simple and defensible.

I would push back on SET NULL even if Jasmin re-raises it — the NOT NULL collision is the dealbreaker. If she wants retained anonymized analytics post-deletion, the right answer is a new table, not relaxing the events FK.

---

## 6. Constraints honored

- Migration files only; **NOT applied to live DB**.
- Branch `feat/phase-b-prereqs` off `main`, only 2 new files (`0004_*.sql`, `0005_*.sql`).
- Idempotent: `DROP CONSTRAINT IF EXISTS`, `DROP POLICY IF EXISTS`, `ON CONFLICT DO NOTHING`.
- No other schema touched (no table/column adds, no policy edits outside the `project_assets_*` scope, no function changes).
- Style matches 0003 (header block, BEGIN/COMMIT for FK transaction, verification queries inline as comments).

---

## 7. Open questions for Andy

1. **0003 application status.** Has Inon already pasted 0003 into Supabase? If not, the recommended paste order is 0003 -> 0004 -> 0005. If 0003 has been applied, 0004 is a no-op confirmation and Andy can present 0005 as the "the new one that actually changes state."
2. **Path-segment validation in storage RLS.** The brief explicitly allows skipping per-project-id validation in the policies; I did skip it (cleaner policies, application-layer enforces the `{project_id}/{asset_filename}` convention). Confirm this is the desired posture for Phase B; if Jasmin wants RLS to validate the project_id segment too, that's a follow-up migration (small, scoped).
3. **Role source for storage policies.** I read role via `public.is_creator_or_admin()` / `public.is_admin()` (which hit `public.profiles`), NOT from `auth.jwt() -> 'user_metadata' ->> 'role'` as the brief suggested. Reason: `user_metadata` is user-mutable in default Supabase configurations and `profiles.role` is the single source of truth used by every other table's RLS. Flag if you'd rather have the JWT path — easy to change but I'd argue against it.

---

## 7b. Branch hygiene incident (FYI for Andy)

A concurrent process / parallel agent (looks like Yoni's S1-006 work) committed onto `feat/phase-b-prereqs` while I was writing my migrations. As a result, commit `54c7863` ("chore(s1-006): baseline — apps/api routes + types + validation (prior PASS)") on the branch contains BOTH the S1-006 API/types/validation work AND my two new migration files (134 + 171 lines, content intact and verified).

Net effect:
- The migration SQL is correct and present on disk at the right paths.
- `feat/phase-b-prereqs` HEAD now also carries unrelated S1-006 work, not just my two files.
- The deliverable for Inon (paste-ready SQL in this report) is unaffected.

Recommendation: when carving a PR for these migrations, cherry-pick the migration files into a clean branch off `main`, or just paste from this report. Also worth flagging to Andy as another datapoint for the "parallel agent file conflicts" rule in memory — two agents touched the same repo working tree at the same time.

---

## 8. Handoff

Andy: surface the two SQL blocks above to Inon via Telegram when he's at the desk. Once he confirms applied + verification queries show the expected output, dispatch Jasmin for behavioral probes:

- Delete a throwaway profile -> confirm dependent project survives with `published_by = NULL`, dependent events rows are gone.
- INSERT into `storage.objects` for `project-assets` as a `user`-role JWT -> denied. Same INSERT as a `creator` JWT -> allowed. DELETE as a non-admin -> denied.

Status: **DONE.**

— Silas
