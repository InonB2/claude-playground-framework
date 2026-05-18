# Silas — BuildAR Pro Phase B Prerequisites (FK ON DELETE + Storage bucket)

**From:** Andy
**Dispatched:** 2026-05-17
**Tasks:** BUILDAR-S2-001 (FK ON DELETE clauses) + BUILDAR-S2-002 (Storage bucket + RLS)
**Model:** Opus 4.7
**Tester:** Jasmin (RLS behavioral probes + delete-cascade verification)

---

## Why these matter NOW

Yoni starts the mobile shell as soon as Wave 1 (orchestrator) is QA-passed. Mobile shell:
1. Reads asset URLs for project steps → **storage bucket must exist with signed-URL-read RLS**.
2. Inserts events tied to `user_id` → **events.user_id ON DELETE CASCADE** prevents dangling rows when a user is deleted.

These were both flagged by Jasmin as MAJOR in your BUILDAR-S1-001 QA report (2026-05-16 — `owner_inbox/buildar/jasmin_s1_qa.md`). Gate A is closed, so Phase B work is unblocked.

---

## BUILDAR-S2-001 — FK ON DELETE clauses

### Migration: `D:\BuildAR\supabase\migrations\0004_fk_ondelete_clauses.sql`

Two changes:

1. **`projects.published_by`** → `ON DELETE SET NULL`
   - Rationale: a project published by a user should NOT be deleted when that user is deleted; it should become "publisher unknown" and stay in the catalog. Aligns with Jasmin's recommendation.
2. **`events.user_id`** → `ON DELETE CASCADE`
   - Rationale: events are personal user activity; when a user deletes their account, their event history goes with them (GDPR-friendly). Diverges from Jasmin's "SET NULL" suggestion — explain choice in your report. If you disagree with CASCADE for events, push back and use SET NULL; document why.

### How to alter without breaking existing rows

PostgreSQL requires `ALTER TABLE DROP CONSTRAINT ... ADD CONSTRAINT ...` for FK ON DELETE changes. Wrap both in a transaction. Add a `COMMIT` at the end.

### Verification queries (paste in done-report)

```sql
SELECT conname, confdeltype FROM pg_constraint
WHERE conrelid::regclass::text IN ('projects', 'events')
  AND contype = 'f';
-- confdeltype 'n' = SET NULL, 'c' = CASCADE, 'r' = RESTRICT, 'a' = NO ACTION
```

Apply via Supabase SQL Editor (Inon will paste — same pattern as 0003 since MCP OAuth still pending). Include the SQL in your done-report and Andy will surface it to Inon via Telegram when ready.

---

## BUILDAR-S2-002 — Storage bucket + RLS

### Migration: `D:\BuildAR\supabase\migrations\0005_storage_bucket_project_assets.sql`

1. **Create bucket `project-assets`** (public: false).
2. **RLS policies on `storage.objects`** for this bucket:
   - **Upload:** authenticated users with `role = 'admin'` OR `role = 'creator'` (derive from `auth.jwt() -> 'user_metadata' ->> 'role'`).
   - **Read:** all authenticated users (mobile app users need to render step images). Sign URLs server-side via the API for tighter control — but the policy itself should be `authenticated` SELECT.
   - **Delete:** admin only.
   - **Update (metadata):** admin only.
4. **Path convention** to enforce in policies: `project-assets/{project_id}/{asset_filename}`. Policies should optionally validate the project_id segment, but if that complicates the policy, skip it for now and rely on application-layer enforcement.

### Why bucket and policies in a migration file (not Dashboard click-ops)

So we can rebuild from migrations alone, and so Yoni's mobile + Lovable CMS pick up the bucket automatically when they connect to the same Supabase project. Avoid Dashboard-only state.

### Verification queries (paste in done-report)

```sql
-- Bucket exists
SELECT id, name, public FROM storage.buckets WHERE name = 'project-assets';

-- Policies attached
SELECT polname, polcmd, pg_get_expr(polqual, polrelid) AS using_expr,
       pg_get_expr(polwithcheck, polrelid) AS check_expr
FROM pg_policy
WHERE polrelid = 'storage.objects'::regclass
ORDER BY polname;

-- Should show 4 policies prefixed with 'project_assets_'
```

---

## Definition of done (BOTH tasks)

1. Both migration files exist in `D:\BuildAR\supabase\migrations\` with sequential numbering.
2. SQL is idempotent where reasonable (use `IF NOT EXISTS` for policy creation, `DROP CONSTRAINT IF EXISTS` for FK changes).
3. Verification queries included in done-report.
4. Done-report explicitly notes which of the two FK choices you made for `events.user_id` (CASCADE vs SET NULL) and why.
5. Done-report includes the exact SQL Inon should paste into Supabase SQL Editor — separated as two copy-paste blocks (0004 and 0005).

---

## Report back to

`agents/andy/inbox/silas_phase_b_done.md` — include:
- Migration file paths
- SQL to paste into Dashboard (2 blocks)
- Verification queries
- FK choice rationale
- Open questions
- Status: DONE or BLOCKED

Andy will dispatch Jasmin for behavioral probes (verify the deletes actually cascade/set-null, verify upload denied for non-admin) once Inon has applied the SQL.

---

## Constraints

- **Repo:** `D:\BuildAR\`
- **Branch:** `feat/phase-b-prereqs` off main.
- **Do not apply migrations to live DB** — Inon applies via Supabase Dashboard SQL Editor (same pattern as 0003). You write the SQL.
- **Do not change existing tables beyond these two FK alters.** This is a tight, surgical migration. Schema-drift discipline.

— Andy
