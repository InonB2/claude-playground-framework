# SOP: Shared Package Ownership — Parallel Coding Agents

> **File:** `BKM/sop_shared_package_ownership.md`
> **Applies To:** Rio + Yoni (primary); any future pair of coding agents on the same repo/sprint
> **Last updated:** 2026-05-18 | Author: Nolan
> **Review authority:** Andy

---

## 1. Purpose

When two coding agents (currently Rio and Yoni) are active on the same monorepo within the same sprint, file conflict risk is high and can silently corrupt each other's work. This SOP defines who owns what, how to coordinate before and during a sprint, and how to handle disputes — eliminating ambiguity as the root cause of conflicts.

This SOP applies to the BuildAR Pro monorepo today. The same rules generalize to any future pair of coding agents assigned to the same repo simultaneously.

---

## 2. Package Ownership Map — BuildAR Pro Monorepo

### Yoni owns (exclusively):

| Path | Notes |
|------|-------|
| `packages/api/` | REST/GraphQL API surface |
| `packages/core/` | Backend business logic |
| `packages/db/` | Database clients, query helpers |
| `apps/api/` and all backend `apps/` | Node/Express/Fastify server apps |
| `supabase/` | Migrations, RLS policies, schema — coordinate with Silas |
| CI configs (`.github/workflows/`, `turbo.json`, `pnpm-workspace.yaml`) | Dev owns CI infra; Yoni coordinates with Dev |

### Rio owns (exclusively):

| Path | Notes |
|------|-------|
| `apps/mobile/` | Full React Native / Expo application package |
| `packages/mobile-ui/` | Mobile-specific UI primitives |
| Device test configs | Detox, EAS Build profiles, `eas.json` |
| Expo config files | `app.json`, `app.config.ts` within the mobile package |

### Shared / coordinated packages:

| Path | Owner | Rule |
|------|-------|------|
| `packages/types/` | Both | Either agent may read. Edits require a coordination note in `/scratchpad/file_ownership_[date].md` signed off by both agents before any changes land. |
| `packages/shared/` | Both | Same rule as `packages/types/`. |

### `packages/ui/` — OPEN QUESTION, UNRESOLVED

> **BLOCKED TERRITORY. Neither Rio nor Yoni may touch `packages/ui/` until Andy logs a formal ownership decision in Section 5 of this SOP.**
>
> Any task that requires changes to `packages/ui/` must be flagged to Andy before the agent begins work. Andy will record the decision in Section 5 below. Until that entry exists, both agents must treat `packages/ui/` as off-limits — no reads-with-intent-to-edit, no PRs, no scratchpad drafts targeting it.

---

## 3. Pre-Sprint Coordination Protocol

Before any sprint where both Rio and Yoni are assigned active tasks on the BuildAR Pro monorepo:

1. **Both agents read this SOP** at session start (before writing any code).

2. **Both agents post a file-ownership declaration** in their task notes. Format:

   ```
   ## File Ownership Declaration — [AGENT NAME] — Sprint [ID] — [DATE]
   Task: [task_id]
   Files/packages I will touch this sprint:
   - [list every file or package path]
   Confirmed I have read: BKM/sop_shared_package_ownership.md
   ```

   This declaration goes in `/scratchpad/file_ownership_[date].md`, one block per agent, appended — not overwritten.

3. **Andy reviews both declarations** before either agent writes code. If the same path appears in both declarations:
   - Andy arbitrates before either agent begins (see Section 4 for resolution options).
   - Neither agent proceeds on the contested path until Andy's resolution is logged.

4. If a sprint is solo (only one coding agent active), the pre-sprint check is still required — log which packages you will touch so the record exists for any agent who joins mid-sprint.

---

## 4. Mid-Sprint Conflict Rule

If at any point during a sprint an agent discovers they need to touch a file or package owned by the other agent:

**STOP. Do not proceed. Do not make the edit.**

1. Post a blocker note immediately to `/scratchpad/file_ownership_[date].md`:
   ```
   ## BLOCKER — [AGENT NAME] — [DATE TIME]
   Task: [task_id]
   I need to edit: [exact file or package path]
   Reason: [one sentence]
   Currently owned by: [other agent name]
   Awaiting Andy resolution.
   ```

2. Mark the task as **Blocked** in `tasks/active_tasks.json`.

3. Do not proceed on that file until Andy responds with a logged resolution.

### Andy's resolution options:

| Option | When to use | What Andy does |
|--------|------------|----------------|
| **(a) Reassign the cross-boundary work** | The change is cleanly scoped to the owning agent's domain | Andy delegates the specific sub-task to the owning agent; requesting agent resumes their own track |
| **(b) Log a formal exception** | The requesting agent is the right person to make the change for architectural reasons | Andy logs an exception in `/scratchpad/file_ownership_[date].md` with scope limits (exactly which files, what kind of change, expiry at sprint end) and updates the task notes |

No other resolution paths are valid. Agents may not self-authorize cross-boundary edits under any circumstances.

---

## 5. Resolving `packages/ui/` Ownership

This section is the authoritative record for the `packages/ui/` ownership decision.

**Current status: UNRESOLVED — as of 2026-05-18**

> Andy will log the decision here when made. Until a dated entry appears below this line, both agents treat `packages/ui/` as blocked territory (see Section 2).

---

### [DECISION PENDING — Andy logs here when resolved]

```
Date decided: ___________
Decided by: Andy
Owner: ___________
Scope of ownership: ___________
Conditions / exceptions: ___________
```

---

## 6. Generalization to Future Agent Pairs

This SOP is not Rio-and-Yoni-specific. Any future pair of coding agents assigned to the same monorepo must follow the same protocol:

1. Andy defines ownership boundaries in the delegation prompt before the sprint begins — or explicitly references this SOP and assigns Andy to arbitrate Section 3.
2. The pre-sprint declaration (Section 3) is mandatory regardless of which agents are involved.
3. The mid-sprint conflict rule (Section 4) is non-negotiable regardless of urgency.
4. New repos or new monorepos get their own ownership table appended to this SOP (or a new SOP linked from INDEX.md if the scope warrants it) — Andy decides which.

If a gap exists (a package not listed in any agent's ownership table), it is implicitly contested territory and must be escalated to Andy before either agent touches it — same as Section 4.

---

## Appendix: Quick Reference Card

| Situation | Action |
|-----------|--------|
| Starting a sprint with both agents active | Both read SOP → both post declarations → Andy reviews → proceed |
| File appears in both declarations | Stop. Andy arbitrates. Neither agent starts on that file. |
| Mid-sprint: I need to touch the other agent's file | STOP. Post blocker. Await Andy resolution. |
| Task touches `packages/ui/` | Flag to Andy before starting. See Section 5. |
| Package not in any ownership table | Treat as contested. Escalate to Andy before touching. |
| Solo sprint | Still post a declaration for the record. |
