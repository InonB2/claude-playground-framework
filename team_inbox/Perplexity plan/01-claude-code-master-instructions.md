# BuildAR — Claude Code Master Instructions

## Purpose

This file is the master implementation brief for **Claude Code**. Claude Code is the primary builder for the system backbone, Supabase schema and migrations, shared types, backend APIs, orchestrator, mobile application scaffolding, integration discipline, and technical quality gates.[web:71][web:85][web:94]

Claude Code must act as the **architecture-preserving agent**. It should prefer correctness, consistency, and maintainability over speed when those goals conflict.

---

## Mission

Build the first production-shaped version of BuildAR as a stable, AI-friendly platform with:
- a clean monorepo,
- a reliable Supabase core,
- a typed API surface,
- a modular orchestration service,
- a React Native mobile app shell,
- and clean integration boundaries for Lovable.[web:71][web:85]

Claude Code owns the canonical implementation of the system contracts.

---

## Authority boundaries

Claude Code is allowed to:
- create and refactor repository structure,
- define and evolve database schema through migrations,
- create shared TypeScript packages,
- implement APIs and orchestration services,
- scaffold and extend the mobile app,
- configure CI/CD and environment discipline,
- define testing conventions,
- enforce interface contracts used by other agents.

Claude Code is **not** allowed to:
- invent a conflicting product scope,
- let frontend convenience override architecture,
- allow Lovable to modify schema without review,
- implement B2B/tenant complexity before the MVP loop is stable,
- bypass the orchestrator abstraction for LLM calls.

---

## Build order

Claude Code must execute work in this order.

### Phase 0 — Backbone
1. Initialize monorepo.
2. Initialize Supabase and migrations.
3. Create shared types and validation layer.
4. Implement auth and JWT validation.
5. Implement core APIs: projects, project details, sessions.
6. Seed a minimal project library.
7. Configure CI/CD and preview-safe environment flow.[web:71][web:72]

### Phase 1 — Core product loop
1. Create mobile shell.
2. Add project browsing and session lifecycle.
3. Add AR session abstraction and fallback mode.
4. Implement orchestrator assist mode.
5. Add telemetry and observability.
6. Stabilize the loop end-to-end.[web:85][web:92]

### Phase 2 — Internal tooling support
1. Expose stable contracts for the CMS.
2. Support content operations needed by Lovable.
3. Add admin-safe diagnostics for events and errors.

### Phase 3 — Deferred expansion
Only after approval:
- advanced CV,
- B2B tenanting,
- credentials and identity extensions,
- deeper multi-agent execution,
- headset support.

---

## Required technical decisions

### Monorepo
Use a single PNPM monorepo with these top-level directories:

```text
/apps
  /web
  /mobile
  /api
  /orchestrator
/packages
  /core-types
  /validation
  /utils
  /ai-client
/supabase
  /migrations
  /seed
/infra
```

If `/api` and `/orchestrator` are combined, the code must still preserve clear module boundaries.

### Database and backend
Use Supabase for:
- Postgres,
- Auth,
- Storage,
- optional Edge Functions when justified.[web:71][web:72]

All schema changes must be migration-driven and version controlled.

### Branching discipline
Adopt Supabase branching for preview and persistent environments. Supabase documents that each branch is a separate environment with its own credentials, with preview branches suited for focused testing and persistent branches suited for longer-lived environments.[web:71][web:72] Claude Code must structure the workflow so schema and integration changes can be tested safely before merge.[web:86]

### Mobile discipline
Mobile should be React Native with native AR capability kept behind an abstraction layer. Expo performance guidance emphasizes reducing startup lag and avoiding unnecessary UI-thread pressure, and Sentry’s 2025 React Native performance guidance similarly emphasizes lazy loading, careful state management, and protecting frame rate.[web:85][web:92]

### LLM and orchestrator discipline
All LLM calls must go through a shared client abstraction. Prompt caching must be designed in early for repeated static prompt segments because Anthropic-compatible prompt caching can materially reduce latency and cost for repeated system prompts, tool definitions, and repeated context.[web:94][web:96]

---

## Data model scope for MVP

Claude Code must implement only the minimum domain model required for the first loop.

### Required tables
- `profiles`
- `projects`
- `project_steps`
- `assets`
- `sessions`
- `events`

### Optional later tables
Do not implement in initial phase unless explicitly requested:
- `tenants`
- `tenant_members`
- `partner_projects`
- `agents`
- `agent_runs`
- `credentials`

---

## API contract rules

All APIs must:
- be versioned under `/api/v1/`,
- use JSON,
- derive user identity from auth tokens,
- avoid exposing raw internal tables directly.

### Minimum endpoints
- `GET /api/v1/projects`
- `GET /api/v1/projects/:id`
- `POST /api/v1/sessions`
- `PATCH /api/v1/sessions/:id`
- `POST /api/v1/orchestrator/assist`

The orchestrator may internally keep a richer module design, but the first public contract should remain minimal.

---

## Orchestrator requirements

Claude Code must implement a **thin orchestrator MVP** first.

### MVP only
- assist mode only,
- one shared LLM client,
- Tutor agent,
- Safety agent,
- structured logging,
- project/session/step contextualization,
- prompt caching hooks.[web:80][web:94]

### Defer
- heavy planning mode,
- dynamic tool marketplaces,
- complex multi-agent recursion,
- advanced CV checks.

### Core rule
The orchestrator exists to control quality, cost, safety, and future extensibility. It must not become a dumping ground for ad hoc prompts.

---

## Shared packages

Claude Code must create and maintain these packages.

### `packages/core-types`
Canonical domain types for:
- Project
- ProjectStep
- Session
- Profile
- Event
- API payloads

### `packages/validation`
Use a schema validation layer such as Zod or equivalent to validate:
- API input,
- orchestrator payloads,
- DB payload mapping.

### `packages/ai-client`
Wrap model calls, retries, timeouts, and prompt caching behavior.[web:94][web:96]

### `packages/utils`
Shared logging, env parsing, feature flags, and error helpers.

---

## Quality bar

Claude Code must enforce the following:

### Tests
- unit tests for shared validation and orchestration routing,
- integration tests for API endpoints,
- migration sanity checks,
- smoke tests for seeded project flows.

### CI
Every PR must run:
- lint,
- typecheck,
- tests,
- migration validation,
- environment checks.

### Observability
At minimum, log:
- session lifecycle,
- assistant invocations,
- API failures,
- orchestrator warnings,
- migration/app boot errors.

---

## Guardrails

Claude Code must refuse or flag any change that:
- causes schema drift outside migrations,
- duplicates types in app folders,
- adds B2B features before approval,
- allows direct client-side LLM calls,
- collapses API/orchestrator boundaries,
- introduces breaking changes without versioning.

---

## Done criteria

Claude Code phase is considered acceptable when:
- the repo boots cleanly,
- migrations run in controlled environments,
- the mobile app can browse seeded projects,
- a session can be started and resumed,
- orchestrator assist works in context,
- logs and telemetry are inspectable,
- Lovable can build CMS features on top without changing backend contracts.
