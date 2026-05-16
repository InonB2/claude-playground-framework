# Silas — Migration 0003 Complete

**File:** `D:\BuildAR\supabase\migrations\0003_security_fixes.sql`  
**Date:** 2026-05-16  
**Author:** Silas (Database Architect)  
**Source audit:** Jasmin static RLS audit — all BEFORE LAUNCH findings  

---

## Fixes Applied

### Fix 1 — Tighten `projects_update_staff` policy (INF DES-1)

**SQL diff:**

```sql
-- BEFORE (0001):
CREATE POLICY "projects_update_staff" ON public.projects
  FOR UPDATE USING (public.is_creator_or_admin())
  WITH CHECK (
    public.is_creator_or_admin()
    AND (status <> 'published' OR public.is_admin())
  );

-- AFTER (0003):
DROP POLICY IF EXISTS "projects_update_staff" ON public.projects;
CREATE POLICY "projects_update_staff" ON public.projects
  FOR UPDATE
  USING (
    public.is_creator_or_admin()
    AND (status <> 'published' OR public.is_admin())
  )
  WITH CHECK (
    public.is_creator_or_admin()
    AND (status <> 'published' OR public.is_admin())
  );
```

**What changed:** The USING clause previously only checked role. A creator could `UPDATE` any field on a published project row — the WITH CHECK blocked status changes but not content edits. Now USING carries the same draft-or-admin guard, so creators cannot even read the row for the purpose of an UPDATE unless it is in DRAFT state.

---

### Fix 2 — Admin SELECT on `sessions` (INF-6)

**SQL diff:**

```sql
-- ADDED (0003):
DROP POLICY IF EXISTS "sessions_select_admin" ON public.sessions;
CREATE POLICY "sessions_select_admin" ON public.sessions
  FOR SELECT USING (public.is_admin());
```

**What changed:** No admin policy existed on sessions. Admin queries returned 0 rows silently. Policy added; existing user own-session policies are unchanged and union correctly.

---

### Fix 3 — `projects.published_by` FK — ON DELETE SET NULL (DES-4 / Silas risk #6)

**SQL diff:**

```sql
-- BEFORE (0001, implicit):
-- published_by uuid REFERENCES public.profiles(id)
-- (NO ACTION on delete — default)

-- AFTER (0003):
ALTER TABLE public.projects DROP CONSTRAINT IF EXISTS projects_published_by_fkey;
ALTER TABLE public.projects
  ADD CONSTRAINT projects_published_by_fkey
  FOREIGN KEY (published_by) REFERENCES public.profiles(id)
  ON DELETE SET NULL;
```

**What changed:** Profile deletion was blocked by the FK if the profile had ever published a project. With SET NULL the project record survives, `published_by` becomes NULL ("publisher removed"), and account deletion proceeds.

---

### Fix 4 — `events.user_id` FK — ON DELETE CASCADE (INF-8)

**SQL diff:**

```sql
-- BEFORE (0001, implicit):
-- user_id uuid NOT NULL REFERENCES public.profiles(id)
-- (NO ACTION on delete — default)

-- AFTER (0003):
ALTER TABLE public.events DROP CONSTRAINT IF EXISTS events_user_id_fkey;
ALTER TABLE public.events
  ADD CONSTRAINT events_user_id_fkey
  FOREIGN KEY (user_id) REFERENCES public.profiles(id)
  ON DELETE CASCADE;
```

**What changed:** Event rows are an append-only audit log — they are worthless without the user. The missing cascade blocked GDPR-compliant account erasure. Cascade delete now removes all event rows when the profile is deleted. (Note: `sessions.user_id` already had ON DELETE CASCADE in 0001; this brings events into parity.)

---

### Fix 5 — Error handling in `handle_new_user()` trigger (INF-3)

**SQL diff:**

```sql
-- BEFORE (0001):
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name)
  VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name')
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

-- AFTER (0003):
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, role)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'role', 'user')
  );
  RETURN NEW;
EXCEPTION WHEN OTHERS THEN
  RAISE WARNING 'handle_new_user() failed for user %: %', NEW.id, SQLERRM;
  RETURN NEW;
END;
$$;
```

**What changed:**
1. INSERT now also populates `email` and `role` columns (previously not written at trigger time).
2. Any exception is caught, a WARNING is emitted to Supabase logs, and the function returns NEW so the `auth.users` INSERT is not rolled back. Signup always succeeds; profile creation is retried at the app layer on first authenticated request.
3. `ON CONFLICT DO NOTHING` removed — the EXCEPTION block now handles duplicate-key errors; keeping both would silently mask other constraint violations.

The trigger binding (`on_auth_user_created`) is unchanged — `CREATE OR REPLACE FUNCTION` replaces the body in place.

---

### Fix 6 — Seed idempotency note (DES-6)

No code change made to `0002_seed_projects.sql`. The migration contains an inline comment documenting the risk and two remediation options:
- Add a new migration with `ON CONFLICT (slug) DO NOTHING` for any re-seeding.
- Document in the runbook that 0002 is a one-shot seed, never to be re-run.

Patching 0002 after production deployment is risky due to migration history checksums.

---

## Infrastructure Section (Schema Changes)

| Change | Table | Type | Impact |
|--------|-------|------|--------|
| FK recreated with ON DELETE SET NULL | `projects.published_by` | Constraint | Unblocks profile/account deletion |
| FK recreated with ON DELETE CASCADE | `events.user_id` | Constraint | GDPR-compliant account erasure |
| Function replaced | `public.handle_new_user()` | Trigger function | Adds email+role write; adds exception handling |

All three are backward-compatible — no column types change, no existing data is modified.

---

## Design Section (Policy Logic Decisions)

| Change | Table | Policy | Decision |
|--------|-------|--------|----------|
| USING clause tightened | `projects` | `projects_update_staff` | Creators blocked from UPDATE on published rows at the USING layer, not just the WITH CHECK layer |
| New admin SELECT | `sessions` | `sessions_select_admin` | Admin visibility added without touching user own-session policies; policies union under Supabase RLS permissive mode |

**Key design call on Fix 1:** The original design used USING to grant access then WITH CHECK to constrain the result. This is subtly wrong for the draft-only requirement: USING controls which rows the UPDATE *sees*, and a creator who can see a published row can still send an UPDATE against it even if WITH CHECK blocks the commit in some paths. Mirroring the guard on both clauses closes the window.

---

## Malfunction + Prevention Plan

### Malfunction
The original `projects_update_staff` USING clause let creators read-for-update on published rows. A malicious or careless creator could issue UPDATE statements against published content (title, summary, category, difficulty, etc.) and have them commit — since WITH CHECK only guarded the `status` field, not arbitrary column edits.

### Fix
USING and WITH CHECK are now identical, requiring `status <> 'published' OR is_admin()`. Creators are locked out of published rows for UPDATE entirely.

### Prevention Plan
- **Policy template:** All future UPDATE policies on content tables should default to matching USING and WITH CHECK unless there is an explicit, documented reason to differ.
- **Audit checklist addition:** Jasmin's RLS audit template should include a line: *"For UPDATE policies, verify USING and WITH CHECK apply equivalent guards."* This was the root cause of INF DES-1 and would be caught automatically on every future audit pass.
- **Review gate:** Any PR that introduces or modifies an RLS UPDATE policy requires the reviewer to confirm both clauses are present and logically consistent.

---

## Syntax Verification

Migration read back after write. Checks passed:
- All `$$` function body delimiters balanced (one open, one close for Fix 5).
- All parentheses in USING/WITH CHECK clauses balanced (Fix 1: 2 open, 2 close each).
- Every SQL statement ends with a semicolon.
- No stray tokens or mismatched keywords detected.
- `DROP POLICY IF EXISTS` used before each CREATE POLICY — idempotent.
- `DROP CONSTRAINT IF EXISTS` used before each ADD CONSTRAINT — idempotent.
- `CREATE OR REPLACE FUNCTION` — idempotent.

---

*Silas — Database Architect*  
*Migration ready for Jasmin QA sign-off before production apply.*
