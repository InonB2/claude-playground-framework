# Vera QA — BUILDAR-S1-005 (Dev's CI workflow)
**Date:** 2026-05-16
**Tester:** Vera
**Verdict:** FAIL

> **Root cause of FAIL:** The file actually present at `D:\BuildAR\.github\workflows\ci.yml` is **not** the 5-job, label-gated, concurrency-controlled workflow that Dev's closeout report (`dev_ci_workflow_done.md`) describes. The shipped file is a single-job, `name: ci` workflow with steps `checkout → install pnpm → setup-node → install → typecheck → lint → build`. There is **no** `install` job, **no** `test` job, **no** `migration-validate` job, **no** `concurrency` block, **no** workflow-level `permissions:` block, **no** `needs:` chain, **no** `pnpm/action-setup@v3`, and **no** `actions/cache@v4`. The companion `README.md` and `CODEOWNERS` files describe the spec'd 5-job workflow, so the docs and the workflow are now out of sync. Either Dev wrote the report against a draft that never got saved, or the wrong file is on disk. Either way, the success criteria for BUILDAR-S1-005 are not met.

---

## Checks

### 1. YAML syntax — PASS

`powershell-yaml` `ConvertFrom-Yaml` on `D:\BuildAR\.github\workflows\ci.yml`:

```
YAML OK
Top-level keys: name, jobs, on
Jobs: ci
  - ci  needs=  if=
```

File parses cleanly. **Verdict: PASS** (syntax only — content is wrong, see check 3).

### 2. actionlint — SKIP (not installed)

```
PS> Get-Command actionlint -ErrorAction SilentlyContinue
PS> # (empty)
actionlint NOT installed on PATH
```

`actionlint` is **not** on PATH on this machine. Dev's closeout report claims he downloaded `actionlint_1.7.1_windows_amd64` and ran it with zero findings. I cannot reproduce that claim — there is no `actionlint` binary on PATH, in the repo, or in the workflows directory. The claim is unverifiable from the current machine state. **Verdict: SKIP / UNVERIFIED.** Treat Dev's "0 findings" as unconfirmed.

### 3. Job graph sanity — FAIL (BLOCKER)

Expected per Dev's report and the spec (`BKM/sop_infra.md §6`):
- 5 jobs: `install`, `lint`, `typecheck`, `test`, `migration-validate`
- `lint`/`typecheck`/`test` all `needs: install`
- `migration-validate` label-gated on `validate-migrations`
- Workflow-level `concurrency` with `cancel-in-progress: true`
- Workflow-level `permissions: contents: read`

Actual (from parser output above and direct read of `ci.yml`):
- **1 job** named `ci`. Not 5.
- No `needs:` anywhere. No job dependencies.
- No `migration-validate` job at all. No label gating.
- No `concurrency:` block at workflow or job level.
- No `permissions:` block at workflow or job level.
- Steps inside the single `ci` job: `Checkout → Install pnpm (via npm i -g pnpm@9) → Setup Node 20 → Install deps → Typecheck → Lint → Build`. **No `test` step.** There is a `Build` step that the spec doesn't ask for in Phase A.

**Verdict: FAIL — BLOCKER.** The workflow on disk implements ~30% of what the report and README claim.

### 4. Action pinning — PASS (limited surface)

All `uses:` lines in the shipped file:

```
16:        uses: actions/checkout@v4
22:        uses: actions/setup-node@v4
```

Both pinned to a major version (`@v4`). Neither uses `@main`, `@master`, or floats. **Verdict: PASS** for what is present. Note that Dev's report also claims `actions/cache@v4` and `pnpm/action-setup@v3` are used — they are not in the shipped file.

### 5. Local equivalence — PASS

The four commands the README tells contributors to run locally were executed from `D:\BuildAR\`:

```
pnpm install --frozen-lockfile  → EXIT 0  ("Already up to date", 8 workspaces)
pnpm -r lint                    → EXIT 0  (7 workspaces ran, all Done)
pnpm -r typecheck               → EXIT 0  (7 workspaces ran, all Done)
pnpm -r test                    → EXIT 0  (no workspace has a test script — pnpm -r skipped them silently, confirming Dev's claim in check 10)
pnpm -r build                   → EXIT 0  (7 workspaces ran, all Done — relevant because the shipped workflow actually runs `build`, not `test`)
```

Local environment: pnpm 11.1.2 (workflow pins pnpm 9 via `npm install -g pnpm@9` — version drift is fine for Phase A). `pnpm-lock.yaml` present and committed.

**Verdict: PASS.** The shipped workflow's commands will all be green on the first PR. The 5-job spec workflow's commands (`lint`/`typecheck`/`test`) would also all be green.

### 6. Secrets discipline — PASS

```
PS> Grep "secrets\." D:\BuildAR\.github\workflows\ci.yml
No matches found
```

Zero references to `secrets.*` anywhere in the file. **Verdict: PASS.**

### 7. README sanity — FAIL (drift vs. shipped workflow)

`workflows/README.md` describes a 5-job workflow with `install`/`lint`/`typecheck`/`test`/`migration-validate`, a `needs:` graph, label-gated migration validation, and a `concurrency` block. **None of that exists in `ci.yml`.** The README is correct against the spec; the workflow is not. A new contributor reading the README and looking at the file would be confused immediately.

Strictly on its own merits the README is well-written (job table, local-run instructions, gating explanation, "how to add a new workflow" section, Phase B roadmap). The problem is divergence from the shipped file.

**Verdict: FAIL — MAJOR.** Either rewrite the workflow to match the README, or rewrite the README to match the workflow. Recommended fix: rewrite the workflow (the README/spec is the contract).

### 8. CODEOWNERS sanity — PASS WITH NOTES

File exists at `D:\BuildAR\.github\CODEOWNERS`. Format inspected: each non-comment line is `pattern owner [owner ...]` with `@InonB2` as the owner. Patterns cover: default `*`, `/apps/api/`, `/apps/mobile/`, `/apps/web/`, `/packages/`, `/supabase/`, `/.github/workflows/`, `/BKM/sop_infra.md`. Syntactically valid.

All owners are `@InonB2` placeholders with inline `TODO: replace with @<agent>` markers, also flagged in the file's header comment. Dev's report calls this out as intentional pending real GitHub handles per agent.

**Verdict: PASS WITH NOTES.** Open follow-up: replace placeholders once individual agents have GitHub handles or once `@buildar/<area>` teams exist.

### 9. Caching — FAIL (incomplete vs. spec)

Shipped workflow caching:

```yaml
- name: Setup Node 20
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'pnpm'
    cache-dependency-path: pnpm-lock.yaml
```

This is the correct `actions/setup-node@v4` pattern for caching the pnpm **store** (`~/.local/share/pnpm/store`), keyed on `pnpm-lock.yaml`. By itself this is valid and matches the official docs.

However, Dev's report claims the workflow also uses `actions/cache@v4` to cache `node_modules` and workspace `node_modules` keyed on the lockfile hash, with downstream jobs restoring that cache and falling back to `pnpm install` on a miss. **There is no `actions/cache@v4` step in the file.** The spec'd multi-job design depends on this for `lint`/`typecheck`/`test` to skip reinstalls — but since there are no downstream jobs in the shipped file, the missing cache is moot for the file as it stands.

**Verdict: FAIL** as a deviation from the spec'd design. **PASS** if judged purely as "is the pnpm store cache wired correctly for this single-job workflow" — yes, the syntax is right.

### 10. No-op `pnpm -r test` — PASS

Verified empirically in check 5: `pnpm -r test` from `D:\BuildAR\` exits 0 with output:

```
Scope: 7 of 8 workspace projects
EXIT test=0
```

No workspace currently defines a `test` script. pnpm `-r` silently skips them and returns 0. Dev's claim is correct. The moment any workspace adds a `test` script it will start running. **Verdict: PASS.**

(Note: this check is for the spec'd workflow — the shipped workflow doesn't actually run `pnpm test`.)

---

## Findings

### BLOCKER

1. **Workflow file does not match the spec, the README, or Dev's own closeout report.** Shipped `ci.yml` is a single-job pipeline with `checkout → install pnpm → setup-node → install → typecheck → lint → build`. Spec/report/README describe a 5-job pipeline (`install`, `lint`, `typecheck`, `test`, `migration-validate`) with `needs:` chains, label-gating, `concurrency`, and `permissions`. Either the wrong file is on disk or the report was written against a draft that never landed. This is the blocker — fix this and most other findings collapse.

### MAJOR

2. **README drift.** `workflows/README.md` describes the 5-job pipeline that doesn't exist. New contributors will be misled. Rewrite whichever side is wrong (the workflow, per the spec).
3. **No `concurrency:` block.** Superseded PR runs will keep burning minutes. Spec requires `concurrency: { group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true }`.
4. **No `permissions:` block.** Workflow defaults to whatever the repo-wide token scope is — should be explicitly `permissions: { contents: read }` at workflow level per spec and least-privilege.
5. **No `migration-validate` job.** Phase A spec calls for a label-gated Postgres dry-run over `supabase/migrations/*.sql`. Not present.
6. **No `test` step.** Spec includes `test`; the shipped workflow runs `build` instead. Even if both eventually pass, the contract says test.

### MINOR

7. **`actionlint` claim unverifiable.** Dev says he installed actionlint 1.7.1 and got 0 findings. The binary is not on PATH on this machine and is not in the repo. The claim may be true but cannot be reproduced here. Recommend either committing a `tools/actionlint.exe` (or a `winget install rhysd.actionlint` line in README setup), or routing actionlint through a CI step so the verification is repeatable rather than tribal.
8. **Single-step job has no fan-out.** Even if intentionally collapsed to one job for Phase A, splitting into `install`/`lint`/`typecheck`/`test` would give faster failure signal and matches the README. Right now a lint error blocks the build step from ever running, so contributors see one failure at a time instead of all in parallel.

### NIT

9. **`Install pnpm` via `npm install -g pnpm@9`** — works, but `pnpm/action-setup@v3` is the idiomatic and faster path (no global npm install round-trip). Spec lists `pnpm/action-setup@v3`.
10. **`actions/setup-node@v4`'s `cache: 'pnpm'` is configured before pnpm is necessarily on PATH** in the way `setup-node` expects. In practice it works because the previous step `npm install -g pnpm@9` puts pnpm on PATH globally, but the canonical order is `pnpm/action-setup` → `setup-node`. Low risk, but worth fixing alongside finding 9.
11. **CODEOWNERS placeholders.** Documented and intentional — flagged as follow-up only.

---

## Sign-off

**FAIL — send back to Dev.**

The shipped workflow does not implement the BUILDAR-S1-005 spec. The README and CODEOWNERS files are good and can stay as-is once the workflow is corrected to match them.

**Recommended action for Dev:**
1. Replace `D:\BuildAR\.github\workflows\ci.yml` with the 5-job, concurrency-controlled, permission-scoped, label-gated workflow described in his own closeout report and in `workflows/README.md`. (My read is that he already wrote this file once — the report is too specific to be invented — so this should be a "find the right version and commit it" exercise, not a rewrite.)
2. Re-run `actionlint` against the corrected file and paste the output into a fresh closeout note. Bonus: drop the `actionlint` binary into the repo (or document `winget install rhysd.actionlint`) so QA can reproduce.
3. Confirm `pnpm-lock.yaml` is still committed (it is — verified) and `--frozen-lockfile` still works (it does — verified).
4. Re-submit for QA. I will re-run all 10 checks against the new file.

**Do not move to Done.** Card stays in "In Progress" with Dev as `assigned_to` and `tested_by` left blank.

— Vera
