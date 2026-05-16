# Rex — Job Cancellations Done
**Date:** 2026-05-16

## Changes Applied — dashboard/index.html

### Job Stage Updates (seed data + runtime patch)

| Job ID | Company | Role | Old Stage | New Stage | Reason |
|--------|---------|------|-----------|-----------|--------|
| `job-lenovo-inc-001` | Lenovo CTO Org | Tech Incubation PM | `Preparing` | `Rejected` | Employer rejection |
| `job-002` | Elbit Smart Sensing | Technical PM | `Applied` | `Archived` | Scrapped by Inon |
| `job-001` | Elbit Systems | Training PM | `Applied` | `Archived` | Scrapped by Inon |

### Artillery C4I / SysEng PM note
No job kanban card exists for "Elbit Artillery C4I / SystemEng PM" — only a CV entry (`cv-elbit-syseng-pm`) exists in the CV tab. No job application was ever created for this role, so nothing to move.

## Implementation Details

1. **`JOBS_SEED_VER`** bumped 6 → 7 (forces version re-check on next load)
2. **`seedDefaultJobs()`** — updated all three job entries to terminal stages in place
3. **`JOBS_V2_ENTRIES`** — updated Lenovo entry stage from `Preparing` → `Rejected` (covers existing users who received it via merge)
4. **`JOBS_V7_ENTRIES = []`** — added (no new entries; patch is handled by runtime function)
5. **`_patchCancelledJobs()`** — new function that fires once on load, forces the three IDs to their correct terminal stages for existing users whose localStorage already has the old data. Uses `andy_jobs_patch_v7` key to run exactly once.
6. **Init sequence** — `_patchCancelledJobs()` called immediately after `migrateLegacyJobStages()`

## Unchanged
- BuildARPro (job-003) — Interviewing, untouched
- CV tab — not modified
- Tasks tab — not modified
- All other dashboard tabs — not modified
