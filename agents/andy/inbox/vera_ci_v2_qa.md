# Vera — BUILDAR-CI-001 Re-QA (v2)
Date: 2026-05-16
Verdict: PASS

## Infrastructure

1. PASS — Exactly 5 jobs present: `install` (line 17), `lint` (line 48), `typecheck` (line 80), `test` (line 112), `migration-validate` (line 144).

2. PASS — `needs: install` present on all four downstream jobs: lint (line 50), typecheck (line 82), test (line 114), migration-validate (line 145).

3. PASS — `pnpm/action-setup@v3` with `version: 9` in ALL 5 jobs: install (lines 25–27), lint (lines 57–59), typecheck (lines 89–91), test (lines 121–123), migration-validate (lines 174–176).

4. PASS — `actions/setup-node@v4` with `cache: 'pnpm'` AND `cache-dependency-path: pnpm-lock.yaml` in ALL 5 jobs: install (lines 30–34), lint (lines 62–66), typecheck (lines 94–98), test (lines 126–130), migration-validate (lines 179–183).

5. PASS — `actions/cache@v4` SAVE step in install job (lines 40–46). Path covers `node_modules`, `apps/*/node_modules`, `packages/*/node_modules`. Key: `node-modules-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}` (line 46). Note: the step is named "Cache node_modules" and runs after the install step — correct placement for a save.

6. PASS — `actions/cache@v4` RESTORE step in all four downstream jobs with identical path set and identical key: lint (lines 69–75), typecheck (lines 101–107), test (lines 133–139), migration-validate (lines 186–192).

7. PASS — Cache key is exactly `node-modules-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}` in all five occurrences (lines 46, 75, 107, 139, 192).

8. PASS — `permissions: contents: read` at workflow level (lines 9–10).

9. PASS — `concurrency` block with `cancel-in-progress: true` at workflow level (lines 12–14). Group: `${{ github.workflow }}-${{ github.ref }}`.

10. PASS — Triggers: push to `main` (lines 4–5) and pull_request targeting `main` (lines 6–7).

11. PASS — `if: contains(github.event.pull_request.labels.*.name, 'validate-migrations')` on migration-validate job (line 148).

12. PASS — Postgres 16 service container in migration-validate (lines 149–168): image `postgres:16`, health check via `pg_isready -U postgres`, interval 10s, timeout 5s, retries 5. Port 5432:5432 mapped.

13. PASS — Zero `secrets.*` references in the entire file (confirmed by grep scan).

## Design

14. PASS — `pnpm install --frozen-lockfile` appears ONLY in the install job (line 37). No downstream job runs a full install; they restore from cache instead.

15. PASS — Recursive flag present on all three commands: `pnpm -r lint` (line 78), `pnpm -r typecheck` (line 110), `pnpm -r test` (line 142).

16. PASS — No duplicate full-install steps in downstream jobs. Each downstream job: checkout → setup pnpm → setup node → restore cache → run command. Clean and correct — no re-install pollution.

## Summary

All 16 checklist items PASS. The v2 rewrite fully satisfies the BUILDAR-CI-001 spec.

Dev's claims are confirmed:
- 5-job pipeline is present with correct dependency graph.
- Cache save/restore pattern is correct and consistent across all jobs.
- pnpm/action-setup@v3 precedes actions/setup-node@v4 in all jobs.
- actions/cache@v4 used with matching paths and keys.
- migration-validate is label-gated with Postgres 16 service container and health check.
- No secrets references. Permissions and concurrency correctly set at workflow level.

**Verdict: PASS — confirmed ready for commit.**

Tester: Vera
Task: BUILDAR-CI-001 (re-QA after v2 rewrite)
