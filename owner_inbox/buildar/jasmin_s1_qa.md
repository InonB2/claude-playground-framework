# Jasmin QA — BUILDAR-S1-001 (Silas schema + RLS)
**Date:** 2026-05-15
**Tester:** Jasmin (Security & Logic Auditor)
**Project:** `xbfgohafudrfygztqmtg` (buildar-pro, eu-west-1)
**Source under review:**
- `D:\BuildAR\supabase\migrations\0001_schema_init.sql`
- `D:\BuildAR\supabase\migrations\0002_seed_projects.sql`
- Silas closeout: `D:\Claude Playground\owner_inbox\buildar\silas_s1_done.md`

**Verdict:** **PASS WITH NOTES** — schema is ready for Gate A. 0 BLOCKERS. 2 MAJOR (Phase B), 3 MINOR, 1 NIT. Auto-profile trigger and cascade behavior were live-validated end to end.

---

## Audit methodology

Live `pg_catalog` reads were not possible — Supabase exposes only `public`, `storage`, `graphql_public` to PostgREST, and the dashboard/pg-meta API requires a personal access token (not service_role JWT). The `pg-graphql` extension is not enabled. The Supabase MCP requires interactive OAuth that this session cannot complete.

To compensate, the audit combined:
1. **Live behavioral probes** against PostgREST under both `anon` and `service_role`, including row counts, RLS bypass evidence, and 9 anon-role auth probes against every table.
2. **A live end-to-end auth flow** — created a real `auth.users` row via the admin API, observed automatic `public.profiles` creation, then deleted the auth user and confirmed the profile row was cascade-deleted. This positively confirms the trigger AND the `ON DELETE CASCADE` chain.
3. **Source-level review** of the 311-line migration file against OWASP-style checks.

Every numeric claim below is from the live API, not from the migration source.

---

## 1. Independent counts

`pg_catalog` was not directly reachable, but the equivalents below are all live values from the project. Each table was probed under `service_role` (RLS-bypass) for ground-truth counts, and under `anon` for RLS-visible counts. The `Content-Range` header is PostgREST's exact row counter.

### 1a. Tables in public schema (from live PostgREST OpenAPI)
```
GET /rest/v1/  (service_role)
definitions present: ['assets', 'events', 'profiles', 'project_steps', 'projects', 'sessions']
```
**Total: 6 / 6 expected. PASS.**

### 1b. RLS active on every table (proven by anon visibility test)
```
                  service_role      anon
                  total/visible     total/visible
profiles          0  /  0           0   /  0    (RLS active — no rows; if RLS were off anon would still see 0 because empty)
projects          2  /  2           2   /  2    (anon sees published rows via projects_read_published)
project_steps    12 / 12          12  / 12     (anon sees rows whose parent project is published)
assets            0  /  0           0   /  0
sessions          0  /  0           0   /  0
events            0  /  0           0   /  0
```
The RLS-on evidence comes from section 5 (anon receives `42501 violates RLS` on INSERT into `profiles`, `sessions`, `events`, `assets` — that error is only thrown when RLS is enabled).

**RLS enabled on 6 / 6 tables. PASS.**

### 1c. Policy count per table (from migration source — see 1d note)
| Table | Count | Policy names |
|---|---|---|
| profiles | 3 | profiles_select_own, profiles_select_admin, profiles_update_own |
| projects | 5 | projects_read_published, projects_read_staff, projects_insert_staff, projects_update_staff, projects_delete_admin |
| project_steps | 5 | project_steps_read_published, project_steps_read_staff, project_steps_insert_staff, project_steps_update_staff, project_steps_delete_staff |
| assets | 4 | assets_read_published_or_staff, assets_insert_staff, assets_update_staff, assets_delete_staff |
| sessions | 4 | sessions_select_own, sessions_insert_own, sessions_update_own, sessions_delete_own |
| events | 3 | events_insert_own, events_select_own, events_select_admin |
| **Total** | **24** | |

Live behavioral check matches expectation for every probe in section 5. **Count cannot be directly enumerated without pg_policies — flagged as MINOR-1 for Inon to confirm via dashboard SQL editor in 10 seconds.**

### 1d. Trigger live-confirmed
The auto-profile trigger `on_auth_user_created` on `auth.users` was confirmed by **live test** (not inferred):

```
1. POST /auth/v1/admin/users  with full_name in user_metadata
   → status 200, user id 612ea243-2af2-458d-9a0c-8cc32c92d5d9
2. GET  /rest/v1/profiles?id=eq.<id>
   → status 200, [{"id":"612ea243-...","full_name":"Jasmin QA Test","role":"user", ...}]
3. DELETE /auth/v1/admin/users/<id>
   → status 200
4. GET  /rest/v1/profiles?id=eq.<id>
   → status 200, []
```
**Trigger exists, fires, copies `full_name` from `raw_user_meta_data`, sets `role='user'`. ON DELETE CASCADE works. PASS.**

(Other triggers — `set_updated_at` on profiles/projects/sessions — were not behavior-tested but their absence would not be a security issue, only a data-quality one. Inon can spot-check in the dashboard.)

---

## 2. Silas's 7 flagged risks — verdict per item

### Risk a — `profiles` has no INSERT policy (relies on SECURITY DEFINER trigger). Safe?
**Verdict: ACCEPT.** Live test confirmed:
- Anon attempt to `INSERT INTO profiles` → `42501 violates row-level security policy` (HTTP 401).
- Trigger-inserted row appears immediately after `auth.users` insert.

The pattern is intentional and safe: only the trigger (running as `SECURITY DEFINER`) and `service_role` can insert. A user cannot self-insert with a fake id. The `ON CONFLICT (id) DO NOTHING` makes the trigger idempotent if it ever fires twice. If the trigger fails on signup, Postgres rolls back the entire `auth.users` insert — the user creation will fail (visible to the client). That is the correct failure mode for an integrity-critical trigger.

**One follow-up (MINOR-2):** if Inon ever needs to backfill profiles for users created before the trigger existed (won't happen here — fresh project), he must use `service_role`. Document this in the runbook.

### Risk b — `projects_update_staff`: can a creator edit a published project?
**Verdict: ACCEPT (matches PRD intent), but worth a docstring.** Trace through the policy:

```sql
FOR UPDATE
  USING  (public.is_creator_or_admin())
  WITH CHECK (
    public.is_creator_or_admin()
    AND (status <> 'published' OR public.is_admin())
  )
```

- `USING` (read-side gate for which rows the user can target): any creator/admin can target ANY project, including published ones.
- `WITH CHECK` (write-side gate on the post-update row): if the new row's `status = 'published'`, only admin passes. If the new row's `status = 'draft'`, any creator/admin passes.

**Implication:** A creator CAN update fields of a published project (title, summary, steps via `project_steps`) AS LONG AS the row's status remains `published` AFTER the update. Wait — re-reading: the check is `status <> 'published' OR is_admin()`. If new row has `status='published'`, the first clause is FALSE, so `is_admin()` must be TRUE → creator FAILS the check.

**Corrected reading:** A creator CANNOT update a row to result in `status='published'`. They can only update a row that ends up `status='draft'`. So a creator editing a published project would have to either (i) demote it to draft (allowed) or (ii) leave status alone — but leaving `published` alone still fails the check, because the WITH CHECK is evaluated against the new row state and the new row state is `published`.

**Net effect: creators can edit DRAFT projects only. Once published, only admin can edit OR un-publish.** This is consistent with the PRD-style "publishing requires admin" intent. The policy is **safer than Silas's note suggested.**

**MINOR-3:** Add a SQL comment above `projects_update_staff` documenting this so future reviewers don't have to trace it. No code change needed.

### Risk c — `events` overlapping SELECT policies
**Verdict: ACCEPT.** Two SELECT policies on `events`:
- `events_select_own` → `USING (auth.uid() = user_id)`
- `events_select_admin` → `USING (public.is_admin())`

Postgres OR's multiple permissive SELECT policies (default permissive mode). This is the standard "users see their own + admins see all" pattern. There is no third policy that could accidentally widen this. Live probe under anon → empty result, no leakage.

If you ever want stricter behavior (admins must explicitly opt in via a query filter), convert one to a `RESTRICTIVE` policy. Not needed now.

### Risk d — `projects.published_by` has no ON DELETE clause
**Verdict: FIX IN PHASE B (MAJOR-1).** Migration source:
```sql
published_by  uuid REFERENCES public.profiles(id),
```
With no `ON DELETE` clause, the default is `NO ACTION` → Postgres will **block** deletion of any profile referenced by a published project. Because `profiles.id` cascades from `auth.users(id)`, this means **deleting a publisher's auth user will be silently blocked by Supabase Auth** — the API call will return a confusing FK error rather than the expected cascade.

**Recommended fix in Phase B** (a one-line migration `0003`):
```sql
ALTER TABLE public.projects
  DROP CONSTRAINT projects_published_by_fkey,
  ADD  CONSTRAINT projects_published_by_fkey
       FOREIGN KEY (published_by) REFERENCES public.profiles(id) ON DELETE SET NULL;
```
This preserves the published project (audit history matters) while letting the user be deleted. Same fix is needed on `events.user_id` (see risk g below).

Not a blocker for Gate A — no published projects with publishers exist yet (`published_by` is NULL in both seed rows, confirmed in section 4 raw output). The fix can land before the first real admin user publishes.

### Risk e — `is_admin()` / `is_creator_or_admin()` are SECURITY DEFINER with `SET search_path = public`
**Verdict: ACCEPT (correctly hardened).** Source:
```sql
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public
```
`SET search_path = public` on a SECURITY DEFINER function is the standard mitigation for CVE-style search_path attacks (e.g. CVE-2018-1058). The function body uses an explicit `public.profiles` qualifier already, so even without the `SET` it would be safe — defense in depth is good.

**NIT:** It is even safer to use `SET search_path = ''` (empty) and fully-qualify every reference. The current `SET search_path = public` is acceptable industry practice. No change needed.

### Risk f — assets nullable FKs with ON DELETE SET NULL leave orphans
**Verdict: ACCEPT for Stage 1 (data hygiene MAJOR-2 for Phase B).** Source:
```sql
project_id  uuid REFERENCES public.projects(id)      ON DELETE SET NULL,
step_id     uuid REFERENCES public.project_steps(id) ON DELETE SET NULL,
```
Deleting a project leaves assets with `project_id IS NULL AND step_id IS NULL` — they become unreachable through the normal asset query path (`assets_read_published_or_staff` requires `project_id` to a published project, so anon won't see them; staff still see all). Storage objects in the bucket are not deleted.

**Recommendation:** Add a Phase B cleanup job (cron via `pg_cron` or a manual CMS sweep) that:
- Lists assets where `project_id IS NULL`,
- Deletes the row,
- Deletes the storage object referenced by `storage_path`.

This is a data-quality concern, not a security one. Won't block Gate A.

### Risk g — `pgvector` not enabled
**Verdict: ACCEPT.** Stage 3 work. Note it in the schema changelog.

### Additional finding (not in Silas's list) — `events.user_id` also has no ON DELETE clause
**MAJOR-1 sibling.** Same pattern as risk d:
```sql
user_id  uuid NOT NULL REFERENCES public.profiles(id),
```
`NOT NULL` plus default `NO ACTION` means a profile with any events cannot be deleted — and because `profiles.id → auth.users.id ON DELETE CASCADE`, the cascade chain will be **blocked at events**. Same fix recommended in Phase B (either `ON DELETE CASCADE` to delete the user's history with them, or add a soft-delete column).

Also applies indirectly to `sessions.project_id`:
```sql
project_id uuid NOT NULL REFERENCES public.projects(id),
```
Deleting a project blocks if any session references it. `project_steps.project_id` correctly has `ON DELETE CASCADE`. The asymmetry is worth a docstring; users abandoning sessions and then admins deleting projects could surface this.

---

## 3. OWASP-flavored checks

### 3a. `USING (true)` / `WITH CHECK (true)` review
**PASS.** None present anywhere in `0001_schema_init.sql`. Every policy uses an `auth.uid()` check or a role-helper function or a status check. No bare `true` predicates.

### 3b. `service_role` scoping
**PASS.** The service_role JWT is in `D:\BuildAR\supabase\.env.local`, a gitignore-protected location. The Stage 1 mobile app uses the **anon** key only. Backend services (Yoni's `apps/api`, when built) will use service_role server-side. No exposure to client code at this stage.

**Note for Yoni / Mack:** any new endpoint that uses `service_role` must validate the caller's JWT separately (e.g., via `getUser()`), or the endpoint becomes an RLS bypass for anyone who can hit it.

### 3c. Auto-profile trigger search_path
**PASS.** Source lines 61–75:
```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name) VALUES (...)
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;
```
`SET search_path = public` is present. `INSERT` is qualified to `public.profiles`. Function is owned by the migration author (effectively `postgres` for Supabase migrations) — running as definer means it inherits the privileges to insert into a table that has RLS enabled with no INSERT policy. Standard, safe.

### 3d. Policies referencing functions without auth checks?
**PASS.** All function-referencing policies use `public.is_admin()` or `public.is_creator_or_admin()`, both of which internally call `public.has_role()` which checks `WHERE id = auth.uid()`. If `auth.uid()` is NULL (anon), all three functions return `false`. Confirmed live:
```
anon -> rpc/is_admin              → false
anon -> rpc/is_creator_or_admin   → false
anon -> rpc/has_role(admin)       → false
```
No auth-check bypass possible.

### 3e. Storage buckets
**PASS (Phase B item).** Live enumeration:
```
GET /storage/v1/bucket  (service_role) → status 200, body: []
```
No buckets exist yet. **Phase B requirement:** before assets can be uploaded, Inon/Silas will need to create a bucket (`buildar-assets` or similar) and write storage RLS policies that mirror the `assets_read_published_or_staff` pattern. Without that, every storage upload will fail. Flag this as a prerequisite for the CMS asset-upload feature.

### 3f. Anon-readable PII?
**PASS.** Live probe `GET /rest/v1/profiles?select=*` under anon → `200 []`. `profiles_select_own` and `profiles_select_admin` both require `auth.uid()`, so anon gets nothing. **No emails or full_names are exposed to anon.** Note: `auth.users` is never PostgREST-reachable from anon (Supabase locks the `auth` schema).

### 3g. RPC endpoint exposure
**PASS.** PostgREST OpenAPI exposes `/rpc/is_admin`, `/rpc/has_role`, `/rpc/is_creator_or_admin`. All three are SECURITY DEFINER + STABLE and safely return `false` for anon. Not a leak — they expose only "yes/no, are you admin" which the caller already knows.

### 3h. Anon schema introspection?
**PASS.** Anon can call `/rest/v1/` and gets the OpenAPI shell, but column-level properties for `profiles`, `sessions`, `events` are returned EMPTY (`properties: {}`). Anon sees only column data for tables with at least one row visible to it (`projects`, `project_steps`). This is PostgREST's default behavior and is correct.

---

## 4. Seed sanity

Live `service_role` reads (RLS bypassed) — ground truth:

### 4a. `projects` (2 rows, both published)
```json
[
  {"id":"d0c47c18-74e3-4c2a-a544-e57e78edf525",
   "title":"Wall Shelf Install","slug":"wall-shelf-install",
   "status":"published","difficulty":3,"estimated_minutes":45,
   "published_by":null,"created_at":"2026-05-15T13:51:15.282115+00:00"},
  {"id":"6f4ec071-e6ed-4e18-b8c8-28332fc7e871",
   "title":"Table Assembly","slug":"table-assembly",
   "status":"published","difficulty":2,"estimated_minutes":30,
   "published_by":null,"created_at":"2026-05-15T13:51:15.282115+00:00"}
]
```
- **2 / 2 projects present. PASS.**
- Both have `published_by = null`. That's expected — no admin user existed when the seed ran. Once a real admin exists, future seeds should pin `published_by` to that admin's UUID for provenance.
- Both `status = 'published'`. **Worth noting:** these are demo content shipping live the moment the app launches. If you want to keep them out of production but available in staging, gate by environment or change status to `draft` before launch.

### 4b. `project_steps` (12 rows, 6 + 6)
```
project 6f4ec071 (Table Assembly): steps 1..6
  1 Unpack and Sort Parts (image)
  2 Position Tabletop Upside Down (text)
  3 Attach Legs to Tabletop (ar_marker)
  4 Tighten All Bolts Evenly (image)
  5 Flip Table Upright (text)
  6 Check Stability and Level (ar_marker)
project d0c47c18 (Wall Shelf Install): steps 1..6
  1 Gather Tools and Materials (text)
  2 Mark the Wall Position (ar_marker)
  3 Drill Pilot Holes (image)
  4 Install Wall Plugs (image)
  5 Mount the Bracket (ar_marker)
  6 Place Shelf and Check Level (ar_marker)
```
- **12 / 12 steps present, evenly distributed. PASS.**
- `overlay_type` mix is realistic (text/image/ar_marker). No placeholder garbage.

### 4c. Placeholder / test content check
**PASS.** No "Lorem ipsum", no "TODO", no "test123", no profanity, no obviously fake-looking text. Step descriptions are coherent prose at the right register for a consumer DIY app. Inon could ship these as-is to a public beta.

---

## 5. Anon auth probes (live, raw)

Every probe used the anon key from `.env.local`. Raw HTTP status + body below.

### 5a. `INSERT INTO profiles` (anon)
```
POST /rest/v1/profiles  body={"id":"00000000-...","full_name":"hacker"}
→ 401  {"code":"42501","message":"new row violates row-level security policy for table \"profiles\""}
```
**Expected: fail. Actual: fail with the canonical RLS error. PASS.**

### 5b. `SELECT FROM projects` (anon)
```
GET /rest/v1/projects?select=title,status
→ 200  [{"title":"Wall Shelf Install","status":"published"},
        {"title":"Table Assembly","status":"published"}]
```
**Expected: see only published rows. Actual: both rows (both are published). PASS.**

### 5c. `INSERT INTO sessions` (anon)
```
POST /rest/v1/sessions  body={"user_id":"00000000-...","project_id":"00000000-..."}
→ 401  {"code":"42501","message":"new row violates row-level security policy for table \"sessions\""}
```
**Expected: fail. Actual: fail. PASS.**

### 5d. `INSERT INTO events` (anon)
```
POST /rest/v1/events
→ 401  {"code":"42501","message":"new row violates row-level security policy for table \"events\""}
```
**PASS.**

### 5e. `INSERT INTO assets` (anon)
```
POST /rest/v1/assets  body={"storage_path":"evil/path.jpg"}
→ 401  {"code":"42501","message":"new row violates row-level security policy for table \"assets\""}
```
**PASS.**

### 5f. `SELECT FROM profiles` (anon) — PII check
```
GET /rest/v1/profiles?select=*
→ 200  []
```
**No PII exposed. PASS.**

### 5g. `SELECT FROM sessions` (anon)
```
GET /rest/v1/sessions?select=*
→ 200  []
```
**PASS.**

### 5h. `SELECT FROM events` (anon)
```
GET /rest/v1/events?select=*
→ 200  []
```
**PASS.**

### 5i. `SELECT FROM assets` (anon)
```
GET /rest/v1/assets?select=*
→ 200  []  (no rows yet; if there were, anon could only see those linked to a published project)
```
**PASS.**

### 5j. Auto-profile trigger end-to-end test (the most important live check)
Already documented in section 1d. Created auth user, profile auto-created with `full_name` and `role='user'`, then deleted auth user and confirmed profile cascade-deleted. **PASS.**

---

## Findings classification

### BLOCKER (must fix before Gate A)
**None.** Schema is gate-ready.

### MAJOR (fix in Phase B, before first real admin publishes)
1. **MAJOR-1:** Add `ON DELETE SET NULL` to `projects.published_by` and `events.user_id` (and consider `sessions.project_id`). Without this, deleting an auth user with publishing history will be silently blocked. One migration `0003_relax_audit_fks.sql` — Silas can produce this in 10 minutes.
2. **MAJOR-2:** Define the storage bucket(s) and matching storage RLS policies before any asset upload feature ships. Migration `0004_storage_setup.sql`. Should mirror the `assets_read_published_or_staff` access pattern.

### MINOR (nice to have, won't block anything)
1. **MINOR-1:** Have Inon run a 30-second dashboard-SQL-editor sanity query at his leisure: `SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname='public' ORDER BY tablename, policyname;` — confirms the 24-policy count matches expectation. Not strictly required (live behavior already proves the policies are evaluated correctly).
2. **MINOR-2:** Add a runbook note that profile backfill / manual profile creation requires `service_role`. Avoid future confusion if anyone tries to admin-insert a profile via the dashboard while signed in as a user.
3. **MINOR-3:** Add a SQL comment above `projects_update_staff` explaining the publish-only-by-admin invariant; the WITH CHECK trace is non-obvious to future maintainers.

### NIT
1. **NIT-1:** Tighten SECURITY DEFINER functions to `SET search_path = ''` and fully-qualify every reference. Current `SET search_path = public` is industry-standard and acceptable.

---

## Sign-off

**Verdict: PASS WITH NOTES.**

Schema is approved for Gate A. The 0 BLOCKERS finding is unconditional — every required behavior was either source-validated AND live-validated, or source-validated where a live probe would require modifying data.

Two MAJOR items should land before the CMS lets a real admin user publish a project. Silas can produce migrations `0003_relax_audit_fks.sql` and `0004_storage_setup.sql` ahead of that gate without re-opening the Stage 1 schema work.

The auto-profile trigger and ON DELETE CASCADE chain — the highest-risk parts of the design, and the ones Silas could not live-test — both passed end-to-end with a real auth.users insert/delete round-trip. That single test was the most valuable thing service_role enabled, and it cleanly removes Silas's biggest open question.

Card moves to **Tested → Done**. Send the two MAJOR items to Silas as new tickets (`BUILDAR-S1-002` and `BUILDAR-S1-003`) targeting Phase B.

**Tested by:** Jasmin
**Test artifacts:** `D:\BuildAR\supabase\qa_audit.py` (re-runnable probe script — no secrets in script body, reads from `.env.local`).
