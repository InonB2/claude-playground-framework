# BuildAR — Agent Coordination, Communication, and Build Order

## Purpose

This file defines how Claude Code, Lovable, and the human operator coordinate work so the system is built in a predictable order with minimal rework.

---

## Operating model

There are three actors:

1. **Claude Code** — architecture, backend, mobile, schema, integrations.
2. **Lovable** — internal web CMS/admin UX.
3. **Human operator** — sequencing, approvals, environment management, review, acceptance, and conflict resolution.

Claude Code is the **source of truth for contracts**.
Lovable is the **source of truth for internal UI implementation**.
The human operator is the **source of truth for sequencing and business acceptance**.

---

## Core rule

No agent should begin a downstream dependency before its upstream contract is stable enough to consume.

That means:
- Lovable should not start meaningful CMS work until the schema and shared types are stable.
- Mobile should not integrate the assistant until the orchestrator contract is stable.
- No B2B work begins before the core loop is accepted.

---

## Build order

### Stage 0 — Alignment
Human confirms:
- product scope for 0–1,
- chosen stack,
- repo ownership,
- Supabase project strategy,
- Anthropic/API credentials,
- deployment targets.

### Stage 1 — Backbone by Claude Code
Claude Code builds:
- monorepo,
- schema and migrations,
- shared packages,
- auth,
- core APIs,
- seed content,
- CI/CD.

### Stage 2 — Product loop by Claude Code
Claude Code builds:
- mobile shell,
- project/session flows,
- AR abstraction,
- orchestrator assist,
- telemetry.

### Stage 3 — CMS by Lovable
Lovable builds:
- project CRUD,
- step CRUD,
- asset manager,
- operational admin views.

### Stage 4 — Hardening
Both agents contribute only after review:
- bug fixes,
- UX polish,
- diagnostics,
- test coverage,
- release prep.

### Stage 5 — Deferred expansion
Only with explicit approval:
- tenanting,
- B2B APIs,
- advanced CV,
- deeper agent architecture,
- identity extensions.

---

## Communication protocol

### Every agent output should include
- what was changed,
- what assumptions were made,
- what remains blocked,
- what contract was consumed,
- whether any upstream/downstream agent is affected.

### If Lovable needs a backend change
Lovable must raise a structured request:
- business need,
- exact data missing,
- proposed contract change,
- urgency level,
- whether a UI workaround exists.

### If Claude Code needs product clarification
Claude must ask before proceeding when a change would affect:
- schema permanence,
- security model,
- environment strategy,
- mobile stack selection,
- rollout scope.

---

## Change control

### Allowed without extra approval
- implementation details within an agreed contract,
- internal refactors without changed behavior,
- UI refinements that do not alter data semantics,
- tests, logging, error handling, CI hardening.

### Requires operator approval
- new tables,
- renamed fields,
- major stack changes,
- B2B scope pull-forward,
- auth model changes,
- public API changes,
- moving logic from backend to frontend.

---

## Acceptance gates

### Gate A — Backbone accepted
Must be true:
- migrations run cleanly,
- auth works,
- projects and sessions endpoints work,
- shared types are in place,
- seeded data exists.

### Gate B — Product loop accepted
Must be true:
- user can browse project,
- start session,
- move through steps,
- ask assistant question,
- complete session,
- events are logged.

### Gate C — CMS accepted
Must be true:
- internal user can manage projects and steps,
- assets can be uploaded and linked,
- access control works,
- CMS does not require schema hacks.

---

## Escalation rules

The human operator should pause implementation and review when:
- agents propose conflicting stack choices,
- the schema is changing frequently,
- Lovable starts compensating for missing backend logic in the UI,
- Claude begins over-engineering beyond MVP scope,
- AR implementation starts blocking the workflow proof.

---

## Best-practice operating principle

Prefer **one working vertical slice** over broad parallelism. Parallel work is useful only when contracts are already stable.
