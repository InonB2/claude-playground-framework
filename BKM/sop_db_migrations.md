# SOP: Database Migrations
**Domain:** Database Engineering
**Applies To:** Silas (author), Quinn (structural reviewer), Jasmin (RLS access-control reviewer), Dev (staging clearance), Inon (manual apply)
**File:** `BKM/sop_db_migrations.md`
**Last Updated:** 2026-05-18

---

## 1. When to Create a Migration

A new migration file is required whenever any of the following occur:

| Trigger | Examples |
|---|---|
| New table | `CREATE TABLE projects (...)` |
| Schema change | Add/drop/alter a column; change a column type or constraint |
| New index | `CREATE INDEX`, `CREATE UNIQUE INDEX` |
| RLS policy change | Enable RLS on a table; add, drop, or modify a `POLICY` |
| Data backfill | `UPDATE` or `INSERT` that sets column values for existing rows |
| Extension or function | `CREATE EXTENSION`, `CREATE FUNCTION`, `CREATE TRIGGER` |

**Do NOT create a migration for:** ad-hoc queries, analytics reads, one-off debugging statements, or non-persistent changes in the Supabase Dashboard that are not tracked in source control.

---

## 2. File Naming and Numbering Convention

### Format

```
migrations/NNNN_descriptive_slug.sql
```

- `NNNN` — zero-padded sequential integer, starting from `0001`
- `descriptive_slug` — snake_case summary of the change (no spaces)
- Extension: `.sql`
- Location: `migrations/` in the repo root

### Examples

```
migrations/0001_create_projects_table.sql
migrations/0002_add_status_column_to_projects.sql
migrations/0003_create_idx_projects_owner_id.sql
migrations/0004_enable_rls_projects.sql
migrations/0005_backfill_projects_default_status.sql
```

### Numbering rules

- Always check the highest existing number before creating a new file — never reuse or skip a number.
- If two migrations are created in the same session, number them sequentially in the order they must be applied.
- Never renumber a migration that has already been applied to any environment.

---

## 3. Migration File Structure

Every migration file must contain the following sections in order:

```sql
-- Migration: NNNN descriptive title matching the filename slug
-- Author: [Agent name, e.g., Silas]
-- Date: YYYY-MM-DD
-- Reversible: yes | no (if no, state reason)

-- =============================================================
-- UP
-- =============================================================

-- [SQL statements that apply the change]


-- =============================================================
-- DOWN
-- =============================================================

-- [SQL statements that exactly reverse the UP block]
-- If irreversible (e.g., destructive data drop), explain why and
-- document the manual recovery path instead:
--   IRREVERSIBLE: [reason]
--   Recovery: [manual steps or backup reference]
```

### Required header fields

| Field | Required | Notes |
|---|---|---|
| `Migration:` | Yes | ID + human-readable description |
| `Author:` | Yes | Agent name (e.g., Silas) |
| `Date:` | Yes | ISO 8601 date (`YYYY-MM-DD`) |
| `Reversible:` | Yes | `yes` or `no`; if `no`, reason must follow |

### UP block rules

- Contains only the forward-direction DDL/DML
- Statements must be idempotent where possible (`CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`)
- RLS policies: include `CREATE POLICY`, `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` here
- Data backfills: include a `WHERE` clause to limit scope to rows that need the change

### DOWN block rules

- Must exactly reverse the UP block in reverse order
- `CREATE TABLE` → `DROP TABLE`; `ADD COLUMN` → `DROP COLUMN`; `CREATE INDEX` → `DROP INDEX`
- If the UP contains a data backfill with no safe reverse (e.g., the original values were not preserved), mark as irreversible and document why
- Quinn will block any migration marked `Reversible: yes` that lacks a valid DOWN block

---

## 4. Review Workflow

Migration files go through a three-step review before Inon applies them. **No migration is applied without completing all applicable steps.**

```
Silas (writes) → Quinn (structural review) → [Jasmin if RLS] → Inon (manual apply)
```

### Step 1 — Silas writes the migration

1. Create the file in `migrations/` following Section 2 naming and Section 3 structure.
2. Self-check against the Quinn Migration Review Checklist (see `agents/quinn.md`, Migration Review Checklist).
3. Signal readiness in `/memory/session_log.db`: `Migration NNNN ready for Quinn review`.
4. Drop a scratchpad context note at `/scratchpad/code_notes_[task_id].md` summarising the intent, any data-loss risk, and whether RLS policies are present.

### Step 2 — Quinn performs structural review

Quinn reviews the migration file for:

- Header completeness (all four required fields present)
- UP migration logic: columns/tables/indexes created as specified
- DOWN migration present and correctly reversing the UP block
- No data-loss risk beyond what is explicitly accepted in the task brief
- Constraint correctness (NOT NULL, UNIQUE, FK) appropriate for schema intent
- Migration ordering: no dependency violations on earlier migrations
- RLS policies (if present): syntax correctness, table binding, `USING` / `WITH CHECK` clause structure (see Section 6)

**Quinn's sign-off token:** `LOGIC APPROVED`

Quinn writes this to `/scratchpad/review_[task_id].md` and `/memory/session_log.db` only when all structural checks pass and any RLS escalation to Jasmin has been resolved.

### Step 3 — Jasmin reviews RLS access-control (when applicable)

Quinn escalates to Jasmin whenever the migration contains any RLS policy. Quinn does not approve the migration as fully signed off until Jasmin confirms. See Section 6 for the exact split.

**Jasmin's confirmation** is recorded in `/scratchpad/review_[task_id].md` with the token: `ACCESS CONTROL APPROVED — Jasmin`.

### Step 4 — Inon applies manually

- Inon applies the migration via the **Supabase Dashboard SQL editor** (production panel).
- This step is always manual. There is no auto-apply pipeline.
- Inon pastes the contents of the UP block and runs it.
- After applying, Inon confirms to the team in the active session or via message: `Migration NNNN applied`.
- Silas then performs post-apply verification (Section 7).

---

## 5. No-Staging Fallback Rule

The standard workflow expects Quinn to validate migrations against a Supabase staging environment via schema diff or dry-run. When no staging environment is available, the following fallback applies:

1. Quinn performs a **full structural audit** of the migration files (UP and DOWN) — reading-only, no live execution.
2. The review file at `/scratchpad/review_[task_id].md` is tagged:

   > `schema-review only, live validation pending Dev environment`

3. This tag is also written to `/memory/session_log.db`.
4. Quinn may still write `LOGIC APPROVED` on structural correctness alone — but the live validation tag must remain open.
5. **Dev** is the named owner responsible for clearing this tag. Dev clears it by running the migration against a staging environment and recording the result in `/scratchpad/review_[task_id].md` with the token: `STAGING VALIDATED — Dev`.
6. Andy decides whether to proceed to production before the live validation tag is cleared. If proceeding without staging validation, Andy documents the decision in the task record.

**No other agent may clear the `schema-review only` tag. It belongs to Dev.**

---

## 6. RLS Policy Split (Explicit)

Supabase Row-Level Security policies sit at the boundary of SQL structure and access control. Quinn and Jasmin divide responsibility as follows:

| Aspect | Reviewer | What they check |
|---|---|---|
| Structural correctness | **Quinn** | Policy syntax is valid SQL; table binding is correct; `USING` clause is syntactically well-formed; `WITH CHECK` clause is present where write operations require it; policy name follows naming conventions |
| Access-control correctness | **Jasmin** | Does the policy actually restrict/permit the right users? Does `USING` leak rows it should not? Is `WITH CHECK` sufficient to block unauthorized writes? Is the policy exploitable given the threat model? |

### Protocol

1. Silas notes in the scratchpad context file whether the migration contains RLS changes.
2. Quinn reviews RLS policy structure first (syntax, table bindings, clause presence).
3. Quinn records any access-control questions — things that are syntactically valid but whose logic Quinn cannot assess — in the review file under `RLS ACCESS-CONTROL QUESTIONS FOR JASMIN`.
4. Quinn sends the escalation to Jasmin using the standard format (see `agents/quinn.md`, Escalation Protocol).
5. Jasmin reviews only the access-control side and records: `ACCESS CONTROL APPROVED — Jasmin` or returns blockers.
6. Quinn writes `LOGIC APPROVED` only after Jasmin's confirmation is recorded.

**A migration with RLS changes is never fully approved on Quinn's `LOGIC APPROVED` alone.**

---

## 7. Post-Apply Verification

After Inon confirms the migration ran, Silas performs the following checks and records findings in `/scratchpad/review_[task_id].md`:

| Check | How |
|---|---|
| Table/column exists | Query `information_schema.columns` or `information_schema.tables` for the expected objects |
| Index created | Query `pg_indexes` for the index name and table |
| Constraints in place | Query `information_schema.table_constraints` for NOT NULL, UNIQUE, FK |
| RLS enabled (if applicable) | Query `pg_tables` — `rowsecurity = true` for the affected table |
| RLS policies present | Query `pg_policies` for policy name, table, command, and roles |
| Data backfill correct | Count or sample the updated rows to confirm values match expectation |
| No unexpected side effects | Check row counts on affected tables; verify no cascades dropped unexpected data |

Silas reports the verification result to Andy in `/memory/session_log.db`:
- Pass: `Migration NNNN post-apply verification PASSED — Silas`
- Fail: `Migration NNNN post-apply verification FAILED — [issue] — Silas` → proceed to Section 8

---

## 8. Rollback Procedure

When a migration fails during apply or post-apply verification reveals a problem:

### If the UP block failed mid-run (partial apply)

1. Silas checks what statements executed successfully using `information_schema` and `pg_indexes` queries.
2. Silas manually constructs a targeted cleanup script to undo only the statements that ran — this is NOT necessarily the full DOWN block.
3. Silas presents the cleanup script to Quinn for a fast structural review before Inon runs it.
4. Inon runs the cleanup script via the Supabase Dashboard SQL editor.
5. Silas verifies the schema is back to the pre-migration state.

### If the UP block completed but post-apply verification failed

1. Silas triggers the DOWN block from the migration file.
2. Down block is reviewed by Quinn (structural) and Jasmin (if RLS was involved) before Inon applies it.
3. Inon runs the DOWN block via the Supabase Dashboard SQL editor.
4. Silas re-runs post-apply verification to confirm the rollback succeeded.

### If the migration is irreversible

1. Silas escalates to Andy immediately.
2. Andy assesses whether a data restore from backup is required.
3. No further schema changes proceed until the state is stabilised.
4. The incident is logged in `/session_logs/` with root cause and prevention notes.

### After any rollback

- The migration file is updated with a `-- ROLLBACK NOTE: [date] [reason]` comment at the top.
- The task is moved back to `In Progress` on the dashboard.
- A new migration (next sequential number) is created to re-attempt the change with the fix applied.
- Root cause and fix are documented in `/scratchpad/code_notes_[task_id].md`.

---

## Role Summary

| Role | Responsibility | Sign-off token |
|---|---|---|
| **Silas** | Write migration, self-check, signal readiness, post-apply verification | — |
| **Quinn** | Structural review: syntax, logic, UP/DOWN symmetry, RLS structure | `LOGIC APPROVED` |
| **Jasmin** | RLS access-control review: policy logic, threat model, exploitability | `ACCESS CONTROL APPROVED — Jasmin` |
| **Dev** | Clear `schema-review only` tag when staging environment validates the migration | `STAGING VALIDATED — Dev` |
| **Inon** | Manual apply via Supabase Dashboard SQL editor | Confirmation message |
