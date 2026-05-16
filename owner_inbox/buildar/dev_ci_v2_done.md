# Dev — CI Workflow v2 Closeout
**Date:** 2026-05-16
**Agent:** Dev (DevOps/Cloud Infrastructure)
**Task:** BUILDAR-S1-005 — Replace single-job ci.yml with 5-job pipeline (Vera FAIL re-submission)

---

## Status: DONE — ready for Vera re-QA

---

## What changed

### File replaced
`D:\BuildAR\.github\workflows\ci.yml` has been fully rewritten. The previous version on disk (which Vera's parser read as a single `ci` job) has been replaced with the spec'd 5-job pipeline.

**Correction:** After re-reading both Vera's report and the file, the version on disk at QA time was a partial multi-job attempt that was missing:
1. `actions/cache@v4` node_modules caching in the `install` job
2. `actions/cache@v4` restore steps in all downstream jobs (`lint`, `typecheck`, `test`, `migration-validate`)
3. `cache-dependency-path: pnpm-lock.yaml` in every `actions/setup-node@v4` step
4. `pnpm -r` recursive flag on all workspace commands (`lint`, `typecheck`, `test`)

All four are fixed in v2.

---

## Full final YAML

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  install:
    name: Install
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Setup Node 20
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
          cache-dependency-path: pnpm-lock.yaml

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Cache node_modules
        uses: actions/cache@v4
        with:
          path: |
            node_modules
            apps/*/node_modules
            packages/*/node_modules
          key: node-modules-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}

  lint:
    name: Lint
    needs: install
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Setup Node 20
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
          cache-dependency-path: pnpm-lock.yaml

      - name: Restore node_modules cache
        uses: actions/cache@v4
        with:
          path: |
            node_modules
            apps/*/node_modules
            packages/*/node_modules
          key: node-modules-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}

      - name: Lint
        run: pnpm -r lint

  typecheck:
    name: Typecheck
    needs: install
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Setup Node 20
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
          cache-dependency-path: pnpm-lock.yaml

      - name: Restore node_modules cache
        uses: actions/cache@v4
        with:
          path: |
            node_modules
            apps/*/node_modules
            packages/*/node_modules
          key: node-modules-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}

      - name: Typecheck
        run: pnpm -r typecheck

  test:
    name: Test
    needs: install
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Setup Node 20
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
          cache-dependency-path: pnpm-lock.yaml

      - name: Restore node_modules cache
        uses: actions/cache@v4
        with:
          path: |
            node_modules
            apps/*/node_modules
            packages/*/node_modules
          key: node-modules-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}

      - name: Test
        run: pnpm -r test

  migration-validate:
    name: Migration Validate
    needs: install
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'validate-migrations')
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    env:
      PGHOST: localhost
      PGPORT: 5432
      PGUSER: postgres
      PGPASSWORD: postgres
      PGDATABASE: postgres
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Setup Node 20
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
          cache-dependency-path: pnpm-lock.yaml

      - name: Restore node_modules cache
        uses: actions/cache@v4
        with:
          path: |
            node_modules
            apps/*/node_modules
            packages/*/node_modules
          key: node-modules-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}

      - name: Install psql client
        run: |
          sudo apt-get update
          sudo apt-get install -y postgresql-client

      - name: Wait for Postgres
        run: |
          for i in {1..30}; do
            if pg_isready -h localhost -p 5432 -U postgres; then
              echo "Postgres is ready"
              exit 0
            fi
            echo "Waiting for Postgres... ($i/30)"
            sleep 2
          done
          echo "Postgres did not become ready in time"
          exit 1

      - name: Validate migrations (psql syntax check)
        run: |
          shopt -s nullglob
          files=(supabase/migrations/*.sql)
          if [ ${#files[@]} -eq 0 ]; then
            echo "No migration files found under supabase/migrations/ — nothing to validate."
            exit 0
          fi
          for f in "${files[@]}"; do
            echo "::group::Validating $f"
            psql --variable=ON_ERROR_STOP=1 -h localhost -p 5432 -U postgres -d postgres -f "$f"
            echo "::endgroup::"
          done
          echo "Migration SQL files validated"
```

---

## YAML validation output

```
python -c "import yaml; data = yaml.safe_load(open('D:/BuildAR/.github/workflows/ci.yml')); print('YAML OK'); print('Top-level keys:', list(data.keys())); print('Jobs:', list(data['jobs'].keys()))"

YAML OK
Top-level keys: ['name', True, 'permissions', 'concurrency', 'jobs']
Jobs: ['install', 'lint', 'typecheck', 'test', 'migration-validate']
```

Note: Python renders the `on:` key as `True` because YAML 1.1 treats bare `on` as a boolean alias. This is a known Python/PyYAML quirk with GitHub Actions files; the YAML is valid and GitHub Actions parses it correctly. All 5 jobs confirmed present.

---

## pnpm/action-setup order explanation

The canonical order is `pnpm/action-setup@v3` BEFORE `actions/setup-node@v4`. Here is why:

`actions/setup-node@v4` with `cache: 'pnpm'` needs to locate the pnpm binary to determine the pnpm store path (`~/.local/share/pnpm/store` on Linux) so it can build the correct cache key. If pnpm is not on PATH when `setup-node` runs, the action will either fail or fall back to a generic key that misses the store entirely.

`pnpm/action-setup@v3` installs pnpm via its own managed download and puts it on PATH before `setup-node` is invoked. That ensures `setup-node` finds pnpm, reads the store path, and keys the cache correctly.

The previous version on disk used `npm install -g pnpm@9` as a workaround — this worked in practice because npm's global bin is on PATH, but it is slower (npm round-trip + global install), depends on the npm version bundled with the runner's Node, and is not idiomatic. `pnpm/action-setup@v3` is the official, faster path.

---

## README drift — resolved

`D:\BuildAR\.github\workflows\README.md` describes:
- 5-job pipeline with `install`/`lint`/`typecheck`/`test`/`migration-validate`
- `needs:` chain (`lint`/`typecheck`/`test`/`migration-validate` all need `install`)
- `pnpm -r` recursive commands
- Label-gated `migration-validate` with Postgres 16 service container
- Concurrency block and `permissions: contents: read`

The new `ci.yml` matches all of this exactly. **README drift: resolved. No README edits needed.**

---

## Spec checklist

| Requirement | v1 (shipped) | v2 (this file) |
|---|---|---|
| Trigger: push to main + PR targeting main | PASS | PASS |
| `permissions: contents: read` at workflow level | PASS | PASS |
| `concurrency` with `cancel-in-progress: true` | PASS | PASS |
| 5 jobs: install / lint / typecheck / test / migration-validate | FAIL | PASS |
| `needs: install` on all downstream jobs | PARTIAL | PASS |
| `pnpm/action-setup@v3` (not npm global install) | FAIL | PASS |
| `actions/setup-node@v4` with `cache-dependency-path` | FAIL | PASS |
| `actions/cache@v4` to save node_modules in install | FAIL | PASS |
| `actions/cache@v4` restore in lint/typecheck/test/migration-validate | FAIL | PASS |
| `pnpm -r lint` / `pnpm -r typecheck` / `pnpm -r test` | FAIL (no -r) | PASS |
| migration-validate label-gated on `validate-migrations` | PASS | PASS |
| Postgres 16 service container in migration-validate | PASS | PASS |
| `echo "Migration SQL files validated"` final step | FAIL (missing) | PASS |
| Zero `secrets.*` references | PASS | PASS |

---

## Malfunction + prevention

### What happened (why the wrong file landed on disk the first time)

The v1 file that Vera QA'd was a partial draft. It had the correct structure for the `install` and `migration-validate` jobs (Vera confirmed these were better-formed than a true single-job file), but the `lint`, `typecheck`, and `test` jobs each ran `pnpm install --frozen-lockfile` from scratch rather than restoring a shared `node_modules` cache. The `cache-dependency-path`, `actions/cache@v4` save, and `actions/cache@v4` restore steps were never added, and the `pnpm -r` recursive flag was dropped from the workspace commands. The closeout report was written against the intended spec rather than the file that was actually saved.

**Fix:** Replaced the file with a version that implements all spec requirements, verified against the spec checklist above, and validated YAML syntax with Python's yaml parser.

**Prevention:**
1. Pre-commit self-check: before marking a CI workflow task done, run the spec checklist table against the actual file on disk, not the draft in memory.
2. Diff against the README before closing: `workflows/README.md` is the contract — run a mental diff between the README job table and the YAML jobs block before submitting.
3. YAML validation is mandatory (done here via Python yaml). Actionlint should be added to the local toolchain — install with `winget install rhysd.actionlint` and document in the repo README so QA can reproduce the check.

---

Ready for Vera re-QA.

— Dev
