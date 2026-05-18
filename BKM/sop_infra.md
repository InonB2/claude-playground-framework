# SOP — Infrastructure Standards (BuildAR Pro)

**Owner:** Dev
**Last reviewed:** 2026-05-18
**Applies to:** BuildAR Pro infrastructure (`D:\BuildAR\`)

---

## 1. Stack Overview

BuildAR Pro is a PNPM-workspace monorepo with three deployable workspaces plus a shared backing platform. Each workspace targets a single, opinionated platform — no multi-cloud sprawl.

| Workspace | Platform | Purpose |
|---|---|---|
| `apps/api` | **Railway** (primary) / Render (fallback) | Node.js REST API + Anthropic orchestrator module. Single service, multiple modules (REST routes + `/api/v1/orchestrator/*`). |
| `apps/mobile` | **Expo EAS Build + EAS Update** | Bare React Native app. EAS handles native iOS/Android builds despite the bare workflow — no local Mac/Xcode needed. |
| `apps/web` | **Vercel** | Lovable-generated CMS / admin dashboard. Auto-deploys from `main`; preview deployments per PR. |
| Shared platform | **Supabase** (hosted) | Postgres DB, Auth (JWT), Storage buckets for AR assets. |

Rationale:
- Railway is chosen over Fly.io for the API because of Git-push deploys, built-in env var UI, and Supabase-friendly private networking. Render is the documented fallback if Railway pricing or region availability becomes a blocker.
- EAS is the only realistic CI for bare React Native without provisioning Mac runners.
- Vercel matches Lovable's default export target for `apps/web` — zero-config.

---

## 2. Environment Discipline

### File conventions

| File | Tracked? | Purpose |
|---|---|---|
| `.env.local` | **gitignored** | Developer-local secrets and overrides. Never committed. |
| `.env.example` | **committed** | Canonical list of required variable names with empty or placeholder values. No real secrets. Updated whenever a new var is introduced. |
| Platform env vars | n/a | Real values live in Railway / EAS / Vercel / GitHub Actions secrets — never in repo. |

Every workspace ships its own `.env.example`:

```
apps/api/.env.example
apps/mobile/.env.example
apps/web/.env.example
```

### Naming conventions

- `UPPER_SNAKE_CASE` for all variables.
- Public client vars must be prefixed:
  - Mobile (Expo): `EXPO_PUBLIC_*`
  - Web (Vercel/Vite or Next.js): `NEXT_PUBLIC_*` or `VITE_*` depending on Lovable's output.
- Server-only vars carry **no** public prefix. Anything without a public prefix must never be referenced from `apps/mobile` or `apps/web` source code.

### Required vars per service

**`apps/api` (Railway):**

```
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_ANON_KEY
ANTHROPIC_API_KEY
PORT
NODE_ENV                     # production | staging | preview
SENTRY_DSN_API
AXIOM_TOKEN
```

**`apps/mobile` (EAS):**

```
EXPO_PUBLIC_SUPABASE_URL
EXPO_PUBLIC_SUPABASE_ANON_KEY
EXPO_PUBLIC_API_BASE_URL
EXPO_PUBLIC_SENTRY_DSN_MOBILE
```

**`apps/web` (Vercel):**

```
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
NEXT_PUBLIC_API_BASE_URL
```

**GitHub Actions secrets (CI/CD):**

```
RAILWAY_TOKEN
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
EXPO_TOKEN
SUPABASE_ACCESS_TOKEN
SUPABASE_PROJECT_REF
SUPABASE_DB_PASSWORD
```

---

## 3. Secrets Management

Secrets are classified by who is allowed to see them. The classification dictates where the secret lives.

| Secret | Class | Location | Allowed bundles |
|---|---|---|---|
| `SUPABASE_SERVICE_ROLE_KEY` | **Server-only** | Railway env, GitHub Actions secret | Never bundled into mobile or web. Server-side use only. |
| `ANTHROPIC_API_KEY` | **Server-only** | Railway env | Only accessed by `apps/api` behind `/api/v1/orchestrator/assist`. Mobile and web call the API, never Anthropic directly. |
| `SUPABASE_ANON_KEY` | **Public** | Railway env, EAS secrets, Vercel env | Safe to bundle into mobile and web — RLS is the enforcement layer. |
| `SUPABASE_URL` | **Public** | All platforms | URL, not a secret, but managed via env vars for environment portability. |
| `SENTRY_DSN_*` | **Public** | Per-platform env | DSNs are public by Sentry design. |
| `RAILWAY_TOKEN`, `VERCEL_TOKEN`, `EXPO_TOKEN`, `SUPABASE_ACCESS_TOKEN` | **CI-only** | GitHub Actions secrets | Never in dev machines or app bundles. |

### Hard rules

- The Supabase service role key never appears in `apps/mobile` or `apps/web` source, builds, or env files. CI greps for `SUPABASE_SERVICE_ROLE_KEY` in those workspaces and fails the build if found.
- The Anthropic key is only accessed server-side. All AI calls are proxied through `apps/api` orchestrator endpoints (`/api/v1/orchestrator/*`).
- No secrets in source. Pre-commit hook runs `git-secrets` / `gitleaks` scan.

### Rotation policy

- Cadence: every **90 days** for all server-side secrets (`SUPABASE_SERVICE_ROLE_KEY`, `ANTHROPIC_API_KEY`, CI tokens).
- **Last rotation:** 2026-05-15
- **Next rotation due:** 2026-08-13
- Rotation procedure: generate new key in source platform → update Railway/EAS/Vercel/GitHub Actions env → redeploy → revoke old key after 24h overlap window.
- Rotation events are logged in `/session_logs/` with the date and which secrets rotated.

---

## 4. Deployment Topology

### `apps/api` — Railway

- **Single service** deployment. REST routes and the orchestrator live as modules in the same Node process (per the architecture decision — no separate orchestrator service in v1).
- Built from `apps/api/Dockerfile` using Railway's Docker build path.
- Two Railway environments: `staging` (deploys on push to `main`) and `production` (deploys on tagged release `v*`).
- Health check endpoint: `GET /api/v1/health` — Railway uses this for deployment gates.

### `apps/web` — Vercel

- Auto-deploys from `main` to production.
- Every PR gets an automatic preview deployment at `<branch>-<project>.vercel.app`.
- Root directory configured to `apps/web`; build command `pnpm --filter web build`; install command `pnpm install --frozen-lockfile`.

### `apps/mobile` — EAS

- Three EAS Build profiles in `apps/mobile/eas.json`:
  - `development` — internal distribution, dev client enabled
  - `preview` — internal distribution, built per PR by GitHub Actions
  - `production` — store submission via `eas submit`
- EAS Update channels mirror the profiles: `preview` for PR builds, `production` for release.
- Production releases require a tagged commit (`mobile-v*`) and are gated on `eas build --profile production` succeeding in CI.

---

## 5. Supabase Branching

- **Preview branches per PR** are enabled. This requires the **Pro tier** ($25/month/project) — confirmed in the project plan; document any tier change here when it happens.
- Each PR triggers a Supabase preview branch with an isolated database. The branch URL and anon key are injected into the PR's Vercel preview and EAS preview build automatically via GitHub Actions outputs.
- **Migrations are migration-first.** All schema changes live in `supabase/migrations/` as timestamped SQL files. Apply with:

  ```
  pnpm supabase db push --linked
  ```

- **No manual SQL in the Supabase console** — ever. Console SQL is for read-only inspection only. Any write executed via the console is a process violation and must be retroactively captured as a migration before the next deploy.
- Migration diff check runs in CI: `supabase db diff --linked` must return empty on the target branch before merge.

---

## 6. No-Staging Fallback

When Quinn (schema review) or Mack (automation scripts) cannot run output against a live or staging environment, they tag the review file with:

> `schema-review only, live validation pending Dev environment`

### What the tag means

Structural review passed — the SQL, script, or config is syntactically and logically correct based on static analysis. Live behavior (constraint enforcement, trigger execution, side-effects, timing) is **unverified** because no staging or preview environment was available at time of review.

### Who clears it — Dev is the named owner

Dev is responsible for clearing this tag. When a staging environment is provisioned or a test run becomes possible, Dev:

1. Runs the flagged output against the staging/preview environment.
2. Verifies actual behavior matches expected behavior (no constraint violations, correct row counts, no unintended side-effects).
3. Updates the review file with the sign-off line:

   ```
   [DEV SIGN-OFF] Live validation complete — [date] — [environment used]
   ```

No one else clears this tag. If Dev delegates the run to another agent, Dev still writes the sign-off after reviewing results.

### Escalation

If Dev cannot provision a staging environment within the current sprint:

- Dev flags to **Andy** with a clear blocker note: what is blocked, why staging is unavailable, and estimated time to resolve.
- Andy decides one of two paths:
  - **Hold** — task stays in Tested/Blocked until staging is available.
  - **Proceed with risk acknowledgement** — Andy presents the unverified items to Inon with an explicit `[RISK: live validation not yet run]` flag. Inon decides whether to accept the risk.

Dev does not make the hold/proceed call unilaterally.

### Scope

This protocol applies to:

| Output type | Primary author | Reviewer |
|---|---|---|
| SQL migrations (`supabase/migrations/`) | Quinn + Silas | Dev clears the tag |
| Automation scripts (`scripts/`) | Mack | Dev clears the tag |
| CI pipeline configs (`.github/workflows/`) | Dev | Dev self-clears after staging run |

---

## 7. CI/CD Requirements

Workflow lives at `.github/workflows/ci.yml` (Dev owns this file).

### Every PR runs

For each workspace (`apps/api`, `apps/mobile`, `apps/web`, plus any shared `packages/*`):

```
pnpm install --frozen-lockfile
pnpm --filter <workspace> lint
pnpm --filter <workspace> typecheck
pnpm --filter <workspace> test
```

Plus repo-wide:

```
supabase db diff --linked       # migration validation — must be empty
gitleaks detect                  # secrets scan
```

PNPM install is cached via `actions/cache` keyed on `pnpm-lock.yaml` hash. Path-based filtering (`dorny/paths-filter`) skips jobs for workspaces with no changed files.

### Branch gates

| Branch / event | Action |
|---|---|
| PR opened/updated | Full CI matrix; Vercel preview; Supabase preview branch; EAS `preview` build |
| Merge to `main` | Deploy `apps/api` to Railway staging; deploy `apps/web` to Vercel production |
| Tag `v*` (API/web release) | Deploy `apps/api` to Railway production |
| Tag `mobile-v*` | EAS Build `production` + `eas submit` |

All deploys block on CI green. No "force deploy" lane — if you need to bypass, fix the pipeline first.

---

## 7. Incident Response

For runtime incidents (API down, deploy failures, Supabase outages, EAS build queue failures), follow the triage playbook owned by Finn:

- **Playbook:** `BKM/sop_infra_triage.md` (maintained by Finn — verify the file exists before linking from agent personas; if absent, flag to Andy to commission it).

Dev's responsibility during an incident is to provide infrastructure context (recent deploys, env var diffs, platform status) to Finn and execute any rollback or env change Finn directs. Finn owns the incident itself end-to-end.

---

## Change log

- **2026-05-18** — Added Section 6 (No-Staging Fallback): named Dev as owner for clearing `schema-review only, live validation pending Dev environment` tags; defined escalation path to Andy. Minor fix: triage playbook hedge in Incident Response reworded to actionable language.
- **2026-05-15** — Initial SOP created by Dev as part of DEV-ONBOARD-001.
