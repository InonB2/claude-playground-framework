# BuildAR System Backbone PRD (For Lovable & Claude Agents)

## 1. Purpose and Audience

This PRD defines the **core backend and architecture backbone** for the BuildAR platform: repositories, environments, infrastructure, and conventions Lovable/Claude agents must use when generating and modifying code.

Audience:
- AI agents (Lovable, Claude) writing TypeScript, SQL, and infra code.
- Human maintainers who will review, extend, and operate the system.

This PRD is source‑of‑truth for **how the system is structured**, **where code lives**, and **how new features should be integrated**.

> NOTE: Prior AR market and product research is captured in separate research reports and should be treated as context, not re‑implemented here.[file:3]

---

## 2. Goals and Non‑Goals

### 2.1 Goals

1. Define a **clean, AI‑friendly monorepo structure** that allows Lovable/Claude agents to add features safely and consistently.
2. Standardize **stack choices** around Supabase, TypeScript, and React/React Native to minimize integration friction.
3. Provide a **minimal but robust backend backbone** for:
   - Auth and user accounts.
   - Project CMS (projects, steps, assets metadata).
   - Multi‑agent orchestration API (to be detailed in a separate PRD file).
   - Basic telemetry and logging.
4. Make it easy to **ship vertical slices** end‑to‑end (DB → API → client) using best practices from modern AI‑native SaaS.

### 2.2 Non‑Goals (for this PRD)

- Detailed AR client implementation (covered in a separate `02-ar-guided-diy-mvp-prd.md`).
- Detailed multi‑agent design (covered in `03-multi-agent-orchestrator-prd.md`).
- Detailed Creator Studio UX (covered in `04-project-cms-creator-studio-prd.md`).

---

## 3. High‑Level Architecture

### 3.1 Overview

The system is a **TypeScript monorepo** backed by **Supabase** (Postgres + Auth + Storage) and a **Node/Edge orchestration layer** that interfaces with Claude and other models.

Key pieces:
- **Supabase project**: database, auth, storage, edge functions.
- **Backend service**: Node/TypeScript server (Next.js API routes or stand‑alone Express/Fastify) exposing JSON APIs to clients and orchestrator.
- **Client apps**: web dashboard (Next.js/React) and mobile client (React Native) consuming the APIs.
- **Multi‑agent orchestration service**: runs in the backend (can be implemented as a set of edge functions or a separate service).

### 3.2 Monorepo Layout

Use a monorepo with PNPM or Yarn workspaces.

```text
/ (root)
  package.json
  pnpm-workspace.yaml
  README.md
  /apps
    /web          # Web dashboard (creator/admin + internal tools)
    /api          # Backend REST/GraphQL API (if not using Next.js in /web)
    /mobile       # React Native app (AR client shell)
  /packages
    /core-types   # Shared TypeScript types (DB entities, APIs, agent contracts)
    /utils        # Shared utilities (logging, error handling, feature flags)
  /supabase
    /migrations   # SQL migrations
    /seed         # Seed data
  /infra
    # CI/CD, deployment configs
```

Requirements for AI agents:
- **Never create new apps/packages** without updating workspace config and documenting rationale.
- **Prefer reusing `core-types`** for entity and API typing instead of redefining interfaces.

---

## 4. Technology Stack Decisions

### 4.1 Backend

- Language: **TypeScript**.
- Runtime:
  - Primary: Node 20 LTS.
  - Option A: Next.js API routes (`/apps/web`) if Lovable defaults to full‑stack Next.js.
  - Option B: Separate `/apps/api` with Fastify/Express to keep API independent.
- Database: **Supabase Postgres**.
- Auth: **Supabase Auth** (email + OAuth providers as configured in Supabase dashboard).
- Storage: **Supabase Storage** for user‑generated images, 3D assets, and other binary files.
- Background jobs / async:
  - Start with **Supabase Edge Functions** for simple jobs.
  - Later: optional queue (e.g., worker service in `/apps/api`) if necessary.

### 4.2 Frontend

- Web: **Next.js 14+ w/ React 18**, TypeScript, App Router.
- Mobile: **React Native** (Expo where practical) with a dedicated AR module (specified in AR PRD).

### 4.3 AI / LLM Integrations

- Primary LLM: **Claude** via official API (through Lovable’s built‑in integration if available).
- Orchestration: All LLM calls must go through a **single abstraction module** in the backend (e.g., `/packages/ai-client`) so keys and model selection are centralized.

### 4.4 Observability

- Logging: Use a shared logger utility (`/packages/utils/logger`) with JSON logs and severity levels.
- Metrics: Initially simple (request counts, latency) via chosen hosting platform; later can add a dedicated APM.

---

## 5. Supabase Schema Backbone

### 5.1 Core Tables (Backbone Only)

Define the following tables as the **minimum backbone** (detailed schema in CMS PRD, referenced here so agents know dependencies):

- `profiles`: per‑user profile (linked to Supabase `auth.users`).
- `projects`: high‑level DIY/assembly projects metadata.
- `project_steps`: ordered steps for each project.
- `assets`: references to stored images, 3D files, and other media.
- `sessions`: user project sessions (which user is doing which project, current step, timestamps).
- `events`: generic event log (step completed, error detected, AI suggestion used, etc.).

For now, **do not** model multi‑agent entities in the DB; they will be represented as code/config in the orchestrator service and only write to `events` and domain tables.

### 5.2 Naming and Conventions

- Use **snake_case** for table names and columns in Postgres.
- Use **camelCase** for TypeScript types and code.
- Always create matching TypeScript types in `/packages/core-types` for any new table or view.

---

## 6. API Design Principles

### 6.1 Style

- Use **JSON over HTTPS**.
- Prefer REST endpoints with clear resource names and verbs.
- Keep endpoints **coarse‑grained**, optimized for front‑end usage and multi‑agent flows.

### 6.2 Versioning

- Prefix all endpoints with `/api/v1/`.
- If breaking changes are needed later, introduce `/api/v2/` while keeping v1 stable.

### 6.3 Auth & Security

- All authenticated endpoints must validate Supabase JWT and derive `user_id` from it.
- Do not accept `user_id` from the client; always derive from token.
- Enforce RLS in Supabase for any table containing user‑specific data.

### 6.4 Example Core Endpoints

These are high‑level; details in feature PRDs.

- `GET /api/v1/projects` – list public projects.
- `GET /api/v1/projects/:id` – get project details, steps (excluding heavy assets when not needed).
- `POST /api/v1/sessions` – start a project session.
- `PATCH /api/v1/sessions/:id` – update current step, record completion.
- `POST /api/v1/orchestrator/plan` – entry point for Lyra‑style orchestrator (see orchestrator PRD).

AI agents MUST reuse these patterns when adding new resources.

---

## 7. Environments and Dev Workflow

### 7.1 Environments

- `local` – developer environment with local Supabase or remote dev instance.
- `dev` – shared environment for integration testing.
- `prod` – production.

Each environment has its own Supabase project and secrets.

### 7.2 Branching and CI/CD

- Default branch: `main` (always deployable).
- Feature branches: `feat/<short-description>`.
- Use GitHub Actions (or Lovable defaults) for:
  - Linting (`eslint`, `prettier`).
  - Type checking (`tsc --noEmit`).
  - Running tests.

Deployments:
- `main` → `prod` after successful CI.
- `dev` branch (or PR previews) → `dev` environment.

### 7.3 AI Agent Guidelines for Git Operations

- When Lovable/Claude agents propose changes, they must:
  - Modify existing files in place, respecting structure and conventions.
  - Add **clear, concise commit messages** summarizing feature, not implementation details.
  - Avoid large, multi‑concern changes; keep PRs focused on single vertical slices.

---

## 8. Vertical Slice Development Pattern

To align with modern AI‑native practices, all new features should be delivered as **vertical slices**, meaning:

1. DB schema migration (if needed).
2. Backend API endpoint(s).
3. Shared types updated in `/packages/core-types`.
4. Front‑end integration (web and/or mobile).
5. Minimal tests and telemetry (events emitted).

AI agents should **not**:
- Leave unused entities or endpoints.
- Expose low‑level tables directly to clients.

---

## 9. Extensibility Hooks

The backbone must prepare for:

- Multi‑agent orchestrator integration (dedicated endpoints and events).
- Future Creator Studio (additional tables and web UI).
- Future B2B integrations (webhooks, partner‑specific schemas).

AI agents implementing new features MUST:
- Respect the existing monorepo layout and separation of concerns.
- Integrate with the orchestrator abstraction instead of calling LLM APIs directly.

---

## 10. Acceptance Criteria

For this PRD to be considered complete in implementation:

1. Monorepo is set up with `/apps`, `/packages`, `/supabase`, `/infra` directories and workspace config.
2. Supabase project is initialized with the core tables listed above and RLS for user‑scoped data.
3. Backend service exposes base endpoints for projects, sessions, and orchestrator entrypoint.
4. Shared TypeScript types exist for all domain entities and are used by backend and clients.
5. CI pipeline runs lint, type‑check, and tests on PRs.

Once these are in place, additional feature PRDs (AR client, orchestrator, CMS, Creator Studio) can be implemented on top of this backbone with minimal friction.
