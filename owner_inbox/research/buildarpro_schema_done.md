# BuildARPro — Schema Migration Report
**Agent:** Silas (Database Agent)
**Task:** PROMAKER-AR-010
**Date:** 2026-05-02
**Status:** BLOCKED — migration SQL ready, deployment pending new project

---

## What Was Done

1. Schema extracted from `buildarpro_architecture_research.md` (Q9) and cross-referenced with `buildarpro_product_plan.md`.
2. Full migration SQL written with RLS policies, indexes, and trigger — saved to `scratchpad/buildarpro_schema.sql`.
3. Deployment attempted on two Supabase projects — both blocked (see below).

---

## Blocker: No Deployable Project Available

Two projects were investigated:

| Project | ID | Status | Result |
|---|---|---|---|
| Pro maker AR (original) | `nlxoazmcrlzsezsyvdre` | INACTIVE — paused >90 days | Cannot restore — Supabase permanent block |
| Lovable Cloud project | `yfpwajzpwswjflzwcnff` | Unknown — not in account | No permission — owned by Lovable, not linked to inonbaasov@gmail.com |

**Action required from Inon:** Create a new Supabase project at supabase.com under your account, then run the migration SQL file below.

---

## Migration SQL Location

**File:** `D:\Claude Playground\scratchpad\buildarpro_schema.sql`

Apply it via Supabase Dashboard > SQL Editor, or by running:
```
supabase db push
```
Or paste the SQL directly into the Supabase SQL editor on the new project.

---

## Tables (5 total)

| Table | Purpose | RLS |
|---|---|---|
| `users` | Profile extension of Supabase Auth | ENABLED |
| `guides` | AR guide catalog (steps as JSONB) | ENABLED |
| `image_targets` | Vuforia target registry per guide | ENABLED |
| `subscriptions` | Stripe subscription state per user | ENABLED |
| `guide_views` | Usage analytics (nullable user_id for anon) | ENABLED |

---

## RLS Policy Summary

- **users:** Select + update own row only.
- **guides:** Owner has full CRUD; any authenticated user can read published guides.
- **image_targets:** Owner has full CRUD; authenticated users can read targets for published guides.
- **subscriptions:** Users read own row only; writes restricted to `service_role` (Stripe webhook Edge Function).
- **guide_views:** Owner can read analytics for their guides; authenticated + anon + service_role can insert.

---

## Additional Schema Decisions (beyond Q9 base)

- `UNIQUE (user_id)` on `subscriptions` — one active subscription record per user.
- `CHECK` constraints on `plan_tier` (`free|pro|team|enterprise`), `status` (`active|past_due|canceled|trialing`), `target_type` (`image|model`), `rating` (0–5).
- `handle_new_user()` trigger auto-creates a `users` row on Supabase Auth signup.
- 8 indexes added for FK columns and common query patterns (`is_published`, `product_sku`, `viewed_at`).

---

## Next Steps for Inon

1. Create a new Supabase project at https://supabase.com (eu-west-1 recommended for latency).
2. Copy the new project ID.
3. Tell Andy the new project ID — Silas will apply the migration in under 2 minutes.
4. Alternatively, paste `scratchpad/buildarpro_schema.sql` directly into the SQL editor.

---

## Project URL (once created)

Format: `https://supabase.com/dashboard/project/<new-project-id>`

---

*Silas — Database Agent | PROMAKER-AR-010 | 2026-05-02*
