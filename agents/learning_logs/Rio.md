# Rio — Learning Log

## Purpose
Track insights, patterns, and self-corrections across sessions. Updated at session close by Rio, flagged to Andy.

## Log entries

---

### ONBOARDING ENTRY — 2026-05-18

**Date:** 2026-05-18
**Task:** ONBOARDING-RIO-001 — Initial agent onboarding
**Completed by:** Nolan (Agent Architect)

---

#### SOPs Read

| SOP | File | Status |
|-----|------|--------|
| Core Onboarding | `BKM/sop_onboarding.md` | READ |
| Skills Usage | `skills/sop_skills.md` | READ |
| Web Security Audit | `BKM/sop_web_security.md` | READ |
| Web Design & Visual | `BKM/sop_web_design.md` | READ |
| Web Development | `BKM/sop_web_development.md` | READ |
| CV Management | `BKM/sop_cv_management.md` | READ |
| Session Logging | `BKM/sop_session_logging.md` | READ |
| Writing Style Influences | `BKM/writing_style.md` | READ |
| Infrastructure Standards | `BKM/sop_infra.md` | READ |
| Infrastructure Triage | `BKM/sop_infra_triage.md` | READ |
| Env Secrets / `.env` | `BKM/sop_env_secrets.md` | READ |
| Agent Roster | `agents/roster.md` | READ |

---

#### SOP Conflicts Flagged to Andy

**FLAG 1 — CV Management SOP references deprecated `/output/cv_archive/` path (Minor)**
`sop_cv_management.md` Step 8 directs approved CVs to `/output/cv_archive/`. Per CLAUDE.md, the `/output/` folder is deprecated and removed. The correct archive path is `/owner_inbox/archive/`. This is a stale reference in the SOP, not a conflict with Rio's persona, but Rio should be aware of the correct path if ever involved in content routing.
- Recommended fix: Nolan to flag to Andy for Cole/Silas to update the SOP.

**FLAG 2 — `packages/ui/` ownership gap (Significant for Rio)**
Rio's persona explicitly flags `packages/ui/` as an UNRESOLVED ownership boundary between Rio and Yoni. No SOP exists governing shared package ownership resolution or the coordination log format for `scratchpad/file_ownership_[date].md`. The scratchpad naming convention in `sop_onboarding.md` does not include a file ownership coordination entry.
- Risk: If Rio is assigned a task touching `packages/ui/` before this is resolved, Rio has no SOP to reference — only persona guidance.
- Recommended fix: Andy to formally resolve ownership with Yoni and log it. A `sop_shared_package_ownership.md` SOP would close this gap permanently.

**FLAG 3 — Infrastructure SOP (`sop_infra.md`) covers Rio's EAS build environment but has no mobile-specific env var discipline for `.env.local`**
`sop_infra.md` defines `apps/mobile/.env.example` as the canonical env template, with real secrets living in EAS secrets. `sop_env_secrets.md` covers the Python/Telegram use case only. There is no SOP governing how Rio handles local secrets (e.g., `apps/mobile/.env.local`) on the development machine. Rio should defer to `sop_infra.md` Section 2 for env discipline but should be aware no Python-pattern equivalent exists for the Expo/React Native side.
- Impact: Low risk during normal operation; higher risk if Rio ever needs to configure a dev machine from scratch.

---

#### SOP Gaps Relevant to Rio's Role

1. **No Mobile-Specific SOP exists.** All coding SOPs (`sop_web_development.md`) target React/TypeScript web development. Rio's persona file contains Rio's own checklist (Mobile QA Pre-Handoff), but this lives only in the persona — not as a standalone, versioned BKM SOP. This means the checklist can drift with persona edits and is not visible to QA agents (Vera, Jasmin) without reading Rio's full persona.
   - Recommended: Create `BKM/sop_mobile_development.md` mirroring the pattern of `sop_web_development.md`, extracting Rio's checklist into it.

2. **No file ownership coordination SOP.** Noted above under FLAG 2. The gap affects every agent that works in the BuildAR Pro monorepo with shared packages — not Rio alone.

3. **Session logging SOP (`sop_session_logging.md`) is written for Andy.** Rule 1 states "Andy writes the session log." Rio's session close protocol requires writing to `agents/learning_logs/Rio.md` only — there is no conflict, but Rio should understand that Rio does not write to `session_logs/` directly; that is Andy's responsibility.

---

#### Key Persona Directives Confirmed

- Rio owns `apps/mobile/` exclusively. Never touches `apps/api/`, `supabase/`, CI/CD workflows.
- All code drafts go to `/scratchpad/code_[task_id]/` before any production path.
- QA handoff: Vera for UI/visual (`QA APPROVED`), Jasmin for logic/API (`READY FOR DEPLOY`).
- Rio does NOT move output to `/owner_inbox/` — QA agents do this after sign-off.
- Ralph Loop applies: max 5 iterations, report to Andy either way.
- Session close: write to this log, flag persona updates to Andy.
- Chain of command: only execute tasks assigned by Andy via `tasks/active_tasks.json`.

---

**STATUS: ONBOARDING COMPLETE — ready for task assignment**

---
### Entry template (copy for each new entry):
**Date:** YYYY-MM-DD
**Task:** [task ID and title]
**What worked:** 
**What didn't:** 
**Key insight:** 
**Process change:** [what to do differently next time]
**Persona update flagged to Andy:** [yes/no — if yes, describe]
