# BuildAR Pro — Static Security Audit
**Auditor:** Jasmin (Security & QA)
**Date:** 2026-05-15
**Target:** Project `xbfgohafudrfygztqmtg` (eu-west-1)
**Migrations audited:** `0001_schema_init.sql`, `0002_seed_projects.sql`
**Method:** Static analysis only — live pg_catalog queries not possible (see Credential section)

---

## VERDICT: PASS WITH NOTES

No critical exploitable vulnerabilities found in the static SQL. Several medium-severity design gaps and one notable credential hygiene issue require action before production launch. All findings are actionable from the migration files alone; five additional checks require the live service role key.

---

## Infrastructure Findings

### INF-1 — Credential hygiene: service_role key IS present in `.env.local` (contradicts Silas's report)
**Severity: HIGH (credential exposure risk)**

`.env.local` contains the service_role key at line 4, but the variable name is `SUPABASE_service_role_KEY` (mixed case). Supabase client libraries and most tooling look for `SUPABASE_SERVICE_ROLE_KEY` (all-caps). This means:
- The key is in the file but silently ignored by the app/CLI due to casing mismatch — explaining why Silas reported it as missing.
- The key is committed to the repo (or at least present on disk) in plaintext. If this file is tracked by git, it is a credential leak.

**Recommendation:**
1. Rename the variable to `SUPABASE_SERVICE_ROLE_KEY` (all-caps) so tooling picks it up.
2. **Immediately verify whether `.env.local` is in `.gitignore`.** If it is tracked, rotate the service_role key in the Supabase dashboard now — treat the current key as compromised.
3. Add `.env.local` to `.gitignore` if not already present.

**What requires live access to verify:** Whether this key is currently valid / has been rotated.

---

### INF-2 — SECURITY DEFINER functions and `search_path` (Silas risk #1)
**Verdict: NOT A RISK as written — but conditionally safe**

`has_role()`, `is_admin()`, `is_creator_or_admin()`, `handle_new_user()`, and `set_updated_at()` all carry `SET search_path = public`. This is the correct mitigation for schema-shadowing (a malicious user creating a `public`-schema object to intercept a `pg_catalog` lookup). The pattern used here is the Supabase-recommended hardening approach.

The residual risk is: `SET search_path = public` pins resolution to `public` but does NOT include `pg_catalog`. Postgres always searches `pg_catalog` first regardless of `search_path`, so built-in functions remain safe. The concern would only materialise if an attacker could CREATE objects in `public` — which is blocked by RLS and role grants in a correctly configured Supabase project.

**Caveat requiring live verification:** Supabase projects grant `CREATE` on the `public` schema to the `authenticated` role by default in some older configurations. Confirm with:
```sql
SELECT has_schema_privilege('authenticated', 'public', 'CREATE');
```
If this returns `true`, revoke it: `REVOKE CREATE ON SCHEMA public FROM authenticated;`

---

### INF-3 — `profiles` has no INSERT policy (Silas risk #2)
**Verdict: CONFIRMED RISK — medium severity**

There is no `INSERT` policy on `profiles`. The only write path is `handle_new_user()` (SECURITY DEFINER trigger on `auth.users`). This is intentional and generally sound, but creates two real risks:

**Risk A — Silent trigger failure:** If `handle_new_user()` raises an exception (e.g., `auth.users` row has a `full_name` collision with a malformed `raw_user_meta_data`), the INSERT into `auth.users` itself will be rolled back (trigger is `AFTER INSERT`, not `AFTER INSERT ... DEFERRED`). The user signup appears to fail from the app's perspective but the root cause is opaque. No fallback or alerting mechanism exists.

**Risk B — profileless authenticated users:** If the trigger is ever disabled, dropped, or fails silently (e.g., due to a future Supabase platform change in trigger execution), a user can exist in `auth.users` with no corresponding `profiles` row. Any policy that calls `has_role()` will then return `false` for that user — they become locked out of all content, including published projects, because `projects_read_staff` depends on `is_creator_or_admin()`. The `projects_read_published` policy uses no auth function, so anonymous/public reads still work — but the logged-in user gets no elevated access and no error message.

**Recommendation:**
1. Add error handling inside `handle_new_user()`: wrap the INSERT in a `BEGIN...EXCEPTION` block and log failures to a `system_errors` table or use `RAISE WARNING` so Supabase logs capture it.
2. Consider adding an application-layer check post-signup: if `profiles` row is missing, the API should retry profile creation via an RPC function rather than failing silently.
3. The absence of an INSERT policy is deliberate and correct — do not add one, as it would allow users to self-insert profiles with arbitrary roles.

---

### INF-4 — `set_updated_at()` is NOT SECURITY DEFINER (minor)
**Severity: LOW**

`set_updated_at()` lacks `SECURITY DEFINER` and `SET search_path`. Since it only sets `NEW.updated_at = now()` with no schema lookups, this is not exploitable — but it is inconsistent with the rest of the codebase. For consistency and defence-in-depth, add `SET search_path = public`.

---

### INF-5 — `events` table: no UPDATE or DELETE policy for users
**Severity: LOW — design intent, but confirm**

Events are insert-only for regular users (`events_insert_own`) with no UPDATE or DELETE policy. This is correct for an audit/event log — immutability is desirable. However, if the app ever needs to soft-delete or amend events (e.g., GDPR right-to-erasure), there is no mechanism. Confirm this is intentional and document it.

**What requires live access:** Verify that Postgres denies UPDATE/DELETE from the `authenticated` role when no policy covers that operation (expected behaviour with RLS enabled — rejections default to deny).

---

### INF-6 — `sessions` table: no admin read policy
**Severity: MEDIUM**

Users can SELECT/INSERT/UPDATE/DELETE their own sessions. Admins have no policy granting them SELECT on sessions. This means admins cannot inspect user progress, debug stuck sessions, or generate analytics from the sessions table. For an AR training platform, admin visibility into sessions is almost certainly required operationally.

**Recommendation:** Add:
```sql
CREATE POLICY "sessions_select_admin" ON public.sessions
  FOR SELECT USING (public.is_admin());
```

---

### INF-7 — `sessions.project_id` has no ON DELETE clause
**Severity: MEDIUM**

`sessions.project_id` references `public.projects(id)` with no `ON DELETE` specification (defaults to `NO ACTION` / `RESTRICT`). This means deleting a project that has associated sessions will fail with a foreign key violation. Combined with the fact that only admins can delete projects, this will silently block project cleanup unless sessions are manually purged first. This should be `ON DELETE RESTRICT` (explicit) or `ON DELETE CASCADE` (if sessions should be wiped with the project) — the current implicit RESTRICT is correct in intent but should be made explicit to signal intent to future maintainers.

---

### INF-8 — `events.user_id` has no ON DELETE clause
**Severity: MEDIUM**

`events.user_id` references `public.profiles(id)` with no ON DELETE specification (defaults to NO ACTION). Since `profiles.id` cascades from `auth.users(id) ON DELETE CASCADE`, deleting a user from `auth.users` cascades to `profiles`, but then blocks on `events.user_id`. This will cause user deletion to fail if any events exist for that user — a GDPR concern. Either `ON DELETE CASCADE` (wipe events on user delete) or `ON DELETE SET NULL` (anonymise) should be chosen and documented.

---

## Design Findings

### DES-1 — `projects_update_staff` policy logic (Silas risk #3)
**Verdict: CONFIRMED RISK — logic gap, medium severity**

The policy is:
```sql
FOR UPDATE USING (public.is_creator_or_admin())
WITH CHECK (
  status <> 'published' OR public.is_admin()
)
```

The `USING` clause checks the row's state BEFORE the update. The `WITH CHECK` clause checks the row's state AFTER the update. The intent is: "a creator can edit a draft, but only an admin can flip it to published." However, there is a gap:

A creator who is editing a **published** row passes the `USING` check (they are a creator), then the `WITH CHECK` allows the update as long as `status` remains `'published'`. This means **a creator can modify any field of a published project** (title, description, steps, slug, category, difficulty) as long as they do not change `status`. This is likely unintended — published content should typically be locked to admins only, or at minimum require an explicit editorial workflow.

**Recommendation:** If published projects should be admin-only for all edits:
```sql
FOR UPDATE USING (
  public.is_creator_or_admin()
  AND (status <> 'published' OR public.is_admin())
)
WITH CHECK (
  public.is_creator_or_admin()
  AND (status <> 'published' OR public.is_admin())
)
```
If creators should be allowed to edit published content (but not change status), the current logic is correct but should be explicitly documented.

---

### DES-2 — `events_select_admin` overlaps `events_select_own` (Silas risk #4)
**Verdict: NOT A RISK — correct Postgres behaviour**

Two SELECT policies on the same table are OR'd together by Postgres when using `PERMISSIVE` mode (the default). A row is visible if ANY applicable policy returns true. So:
- A regular user sees only their own events (via `events_select_own`).
- An admin user satisfies `events_select_admin` AND `events_select_own` — both return true for their own events, but `events_select_admin` alone covers all rows.
- There is no data leak: a regular user cannot satisfy `is_admin()`.

This is the standard Supabase pattern. No change needed.

---

### DES-3 — Orphaned assets after project/step deletion (Silas risk #5)
**Verdict: DATA HYGIENE RISK — not a security issue, but operationally significant**

`assets.project_id` and `assets.step_id` are both nullable with `ON DELETE SET NULL`. This means deleting a project sets `assets.project_id = NULL` (and similarly for steps). The asset row persists in the database with both foreign keys nulled out — it becomes unreachable via normal RLS policies (the SELECT policy checks `project_id IS NOT NULL`), effectively a dark orphan.

These orphaned rows:
- Cannot be selected by regular users (project_id IS NULL fails the policy check).
- CAN be seen by staff (`is_creator_or_admin()` OR branch in `assets_read_published_or_staff`).
- Accumulate storage references that are never cleaned up from Supabase Storage buckets.

**Recommendation:**
1. Add a scheduled cleanup job (Supabase Edge Function or pg_cron) to delete `assets WHERE project_id IS NULL AND step_id IS NULL`.
2. Or change to `ON DELETE CASCADE` if assets are always owned by a specific project/step and have no standalone value.

---

### DES-4 — `profiles.published_by` chain (Silas risk #6)
**Verdict: CONFIRMED RISK — operational blocker**

`projects.published_by` references `public.profiles(id)` with no ON DELETE clause (defaults to NO ACTION). This means deleting a profile (and thus the auth.users row, which cascades) will fail with a foreign key violation if that user has any `published_by` references in projects. This makes it impossible to delete an admin/creator account that has published content — a GDPR and operational concern.

**Recommendation:**
```sql
-- In a future migration:
ALTER TABLE public.projects
  ALTER COLUMN published_by DROP NOT NULL; -- already nullable, confirm
-- And add:
ALTER TABLE public.projects
  ADD CONSTRAINT projects_published_by_fk
  FOREIGN KEY (published_by) REFERENCES public.profiles(id)
  ON DELETE SET NULL;
```
Drop and recreate the FK with `ON DELETE SET NULL` so that profile deletion nulls out `published_by` rather than blocking.

---

### DES-5 — No `pgvector` extension (Silas risk #7)
**Verdict: NOT A RISK for Stage 1 — noted for Stage 3**

Absence of `pgvector` is expected and correct at this stage. No action required. Flag for Stage 3 planning: add `CREATE EXTENSION IF NOT EXISTS vector;` in the appropriate migration, and ensure the Supabase project tier supports pgvector (requires Pro plan or above on eu-west-1).

---

### DES-6 — Seed data bypasses RLS (0002)
**Verdict: ACCEPTABLE for migrations — document the assumption**

`0002_seed_projects.sql` inserts rows directly without setting a user context. In Supabase migrations, SQL runs as the `postgres` superuser (bypasses RLS by default). The seeded projects have `status = 'published'` and no `published_by` (NULL). This is acceptable for initial seed data, but:
- `published_by` is NULL for both seed projects — if any application logic requires `published_by IS NOT NULL` for published content, these rows will cause errors.
- If migrations are ever re-run or reset in a dev environment, duplicate seed data will fail on the `slug UNIQUE` constraint — this is safe (it will error and abort) but should be wrapped in `ON CONFLICT DO NOTHING` for resilience.

**Recommendation:** Change seed INSERTs to use `ON CONFLICT (slug) DO NOTHING` pattern so re-runs are idempotent.

---

### DES-7 — No `project_steps` UPDATE WITH CHECK clause
**Severity: LOW**

`project_steps_update_staff` has `USING (public.is_creator_or_admin())` but no `WITH CHECK`. Without `WITH CHECK`, the post-update row is not validated against any policy. In practice this is fine here (the policy only gates on role, not on row content), but it means a creator could theoretically move a step to a different `project_id` via UPDATE — including a project they don't own (if per-project ownership is ever added). Add `WITH CHECK (public.is_creator_or_admin())` for completeness.

---

### DES-8 — `overlay_metadata` is unconstrained JSONB
**Severity: LOW**

`project_steps.overlay_metadata` is a JSONB column with no schema validation. Any JSON shape can be inserted. For an AR platform, this likely contains marker configuration, image references, or spatial data. Without a CHECK constraint or application-level validation:
- Malformed AR metadata will not be caught at the DB layer.
- Future schema migrations involving this field have no baseline to work from.

**Recommendation:** Document the expected JSON schema for each `overlay_type` value. Consider adding a CHECK constraint or a trigger-based validator once the AR metadata format is finalised.

---

## Summary Table — Silas's 7 Flagged Risks

| # | Silas's Risk | Verdict | Action Required |
|---|---|---|---|
| 1 | `is_admin()` / `is_creator_or_admin()` SECURITY DEFINER + `search_path = public` | NOT A RISK (as written) | Verify `authenticated` role lacks CREATE on public schema (live check) |
| 2 | `profiles` no INSERT policy — trigger-only path | CONFIRMED RISK (medium) | Add error handling to trigger; add app-layer retry |
| 3 | Creator can UPDATE published row if status unchanged | CONFIRMED RISK (medium) | Tighten USING clause to block creators on published rows |
| 4 | `events_select_admin` overlaps `events_select_own` | NOT A RISK | No action — standard permissive OR behaviour |
| 5 | Nullable FK + ON DELETE SET NULL → orphaned assets | DATA HYGIENE RISK (not security) | Add cleanup job or switch to CASCADE |
| 6 | `profiles.published_by` no ON DELETE → profile deletion blocked | CONFIRMED RISK (operational) | Add ON DELETE SET NULL to FK constraint |
| 7 | No pgvector | NOT A RISK (Stage 1) | Flag for Stage 3 planning |

---

## What Jasmin Can Verify Statically vs. What Requires Live Access

### Verified statically (this report):
- All RLS policy logic and completeness
- SECURITY DEFINER function correctness
- Foreign key constraint gaps
- Seed data safety
- Trigger function logic
- Credential file contents (key presence, variable name casing)

### Requires live service_role key:
1. Whether `authenticated` role has CREATE privilege on the `public` schema (schema-shadowing exposure check)
2. Whether the service_role key in `.env.local` is valid and not rotated
3. Whether the trigger `on_auth_user_created` is actually attached and enabled in `pg_triggers`
4. Whether any additional policies, functions, or extensions were created outside these migrations
5. Storage bucket RLS policies (not visible in migration SQL)

---

## Recommended Next Steps (Priority Order)

1. **[IMMEDIATE]** Verify `.env.local` is in `.gitignore`. If tracked, rotate the service_role key now.
2. **[IMMEDIATE]** Fix `SUPABASE_service_role_KEY` → `SUPABASE_SERVICE_ROLE_KEY` (casing) so Silas can run live checks.
3. **[BEFORE LAUNCH]** Fix `projects_update_staff` USING clause to block creators from editing published content (DES-1 / Silas risk #3).
4. **[BEFORE LAUNCH]** Add admin SELECT policy on `sessions` table (INF-6).
5. **[BEFORE LAUNCH]** Add ON DELETE SET NULL to `projects.published_by` FK (DES-4 / Silas risk #6).
6. **[BEFORE LAUNCH]** Add ON DELETE CASCADE or SET NULL to `events.user_id` FK (INF-8).
7. **[BEFORE LAUNCH]** Add error handling block to `handle_new_user()` trigger (INF-3).
8. **[POST-LAUNCH]** Add orphaned asset cleanup job (DES-3).
9. **[POST-LAUNCH]** Make seed inserts idempotent with ON CONFLICT DO NOTHING (DES-6).
10. **[STAGE 3]** pgvector extension (DES-5).

---

*Jasmin — Security & QA*
*Static audit complete. Live audit pending SUPABASE_SERVICE_ROLE_KEY fix.*
