# BuildAR Sprint 0–1 Execution Plan

## Objective

This document translates the existing BuildAR PRDs into the **best first implementation sequence** for Lovable and Claude so the team can start building safely, quickly, and with minimal rework.

The sequencing principle is simple: start with the **backbone and contracts first**, then implement one thin but working vertical slice end-to-end, then add authoring and partner complexity later.[code_file:55][code_file:56][code_file:57][code_file:58][code_file:59]

---

## Why this order

The first milestone should not be “build everything.” It should be **establish a stable repo, database, contracts, and one working user flow**. That is the fastest path in modern AI-native product building because AI coding agents are strongest when:

- The architecture is explicit.
- Types and contracts are centralized.
- Tasks are small and vertically scoped.
- The number of moving parts is intentionally limited in early iterations.[code_file:55][code_file:57]

That means the right order is:

1. **Backbone**
2. **One vertical slice**
3. **Agent orchestration**
4. **CMS / authoring**
5. **B2B and identity extensions**

---

## Delivery philosophy

### Principles for Lovable and Claude

- Build in **vertical slices**, not horizontal layers only.[code_file:55]
- Reuse existing Lovable output **only if it does not distort the target architecture**; if current scaffolding conflicts with the PRDs, prefer clean replacement over patchwork.[code_file:55]
- Keep all domain contracts in shared types so the mobile client, web app, and backend do not drift.[code_file:55]
- Put all AI calls behind the orchestrator abstraction from day one, even if only one simple Claude call exists at first.[code_file:57]
- Do not open B2B, multi-tenant, or creator complexity before the core consumer flow works.[code_file:58][code_file:59]

---

## Sprint 0

## Goal

Establish the technical foundation so every following feature can be built with low ambiguity and low rework.[code_file:55]

## Sprint 0 exit criteria

By the end of Sprint 0:

- Monorepo structure exists and is clean.[code_file:55]
- Supabase project is initialized with the minimum core schema.[code_file:55]
- Shared domain types exist and are imported by apps/services.[code_file:55]
- Base auth works.
- Basic API endpoints exist for projects and sessions.[code_file:55]
- CI runs lint, type-check, and tests.[code_file:55]

## Sprint 0 workstreams

### 0.1 Repo and workspace setup

**Owner:** Lovable / Claude codegen

Build from `01-system-architecture-prd.md` first.[code_file:55]

Deliverables:
- PNPM/Yarn workspace setup.
- `/apps/web`
- `/apps/api` (or backend inside `/apps/web` if Lovable strongly prefers this and it stays clean)
- `/apps/mobile`
- `/packages/core-types`
- `/packages/utils`
- `/supabase/migrations`
- `/infra`

Definition of done:
- Install succeeds with one command.
- TypeScript compiles across all workspaces.
- Shared aliases/import paths work.

### 0.2 Supabase initialization

**Owner:** Claude/Lovable + Supabase SQL generation

Create the minimum schema from PRD 01.[code_file:55]

Tables required in Sprint 0:
- `profiles`
- `projects`
- `project_steps`
- `assets`
- `sessions`
- `events`

Must include:
- RLS on user-scoped entities.
- Trigger or service logic to create `profiles` from auth users.
- Seed data for at least 2 sample projects.

Definition of done:
- Local/dev migration can be applied cleanly.
- Basic read/write works through Supabase.

### 0.3 Shared contracts

**Owner:** Claude

Create shared type definitions in `/packages/core-types` based on PRDs 01, 02, 03, and 04.[code_file:55][code_file:56][code_file:57][code_file:58]

Minimum exports:
- `Project`
- `ProjectStep`
- `Session`
- `Profile`
- `OrchestratorRequest`
- `OrchestratorResponse`

Definition of done:
- Backend and frontend both import these types.
- No duplicate domain interfaces in app folders.

### 0.4 Auth baseline

**Owner:** Lovable web + mobile auth flows

Implement:
- Supabase email auth for web and mobile.
- Session/token handling.
- Protected routes for CMS/admin pages.

Definition of done:
- A user can sign up and sign in.
- Authenticated requests can hit protected APIs.

### 0.5 Minimal backend API

**Owner:** Claude backend

Build first-pass endpoints from PRD 01.[code_file:55]

Required endpoints:
- `GET /api/v1/projects`
- `GET /api/v1/projects/:id`
- `POST /api/v1/sessions`
- `PATCH /api/v1/sessions/:id`

Definition of done:
- Endpoints are typed.
- They use Supabase correctly.
- They are covered by basic integration tests.

### 0.6 CI/CD and quality gates

**Owner:** Lovable / Claude infra

Implement:
- ESLint
- Prettier
- Type check
- Test run in CI

Definition of done:
- Pull requests fail on broken types or lint errors.

---

## Sprint 1

## Goal

Ship the first **real vertical slice**: browse a project, start a session, move through steps, ask the AI assistant a question, and complete the project.[code_file:56][code_file:57]

This is the first meaningful proof of product value.

## Sprint 1 exit criteria

By the end of Sprint 1:

- User can sign in on mobile.[code_file:56]
- User can browse at least 2–5 seeded projects.[code_file:56]
- User can start a session and move through steps.[code_file:56]
- Basic AR session shell exists, with non-AR fallback if needed.[code_file:56]
- AI assistant works through the orchestrator endpoint.[code_file:57]
- Completion is persisted and key telemetry events are logged.[code_file:56][code_file:57]

## Sprint 1 workstreams

### 1.1 Mobile shell and navigation

**Owner:** Lovable mobile

From `02-ar-guided-diy-mvp-prd.md`.[code_file:56]

Build these screens first:
- Sign-in / sign-up
- Home / Project list
- Project details
- Session screen
- Completion summary

Definition of done:
- Navigation works smoothly.
- Project list and details are loaded from live API.

### 1.2 Project session flow

**Owner:** Claude + Lovable mobile/backend

Implement:
- Start session from project details.
- Track `currentStepIndex`.
- Persist session state in Supabase.
- Resume active session.

Definition of done:
- App restart does not lose session progress.

### 1.3 AR session shell

**Owner:** Lovable mobile

Important: do **not** block the sprint on advanced AR fidelity.

Implement:
- `ARView` abstraction.[code_file:56]
- Camera permission flow.
- Simple calibration UX.
- Step overlay placeholder support using metadata.
- Non-AR fallback view for unsupported devices.[code_file:56]

Definition of done:
- The session UI works with or without full AR perfection.
- One overlay type is rendered reliably.

### 1.4 Orchestrator MVP

**Owner:** Claude backend

Implement from `03-multi-agent-orchestrator-prd.md`.[code_file:57]

Scope for Sprint 1:
- `POST /api/v1/orchestrator/plan`
- Lyra 4-D pipeline in simple form
- `TutorAgent`
- `SafetyCheckerAgent`
- shared `callLLM()` abstraction

Defer for now:
- `VisionInspectorAgent`
- advanced planning mode
- deep multi-agent branching

Definition of done:
- User asks a question during a session and gets a context-aware answer.
- Safety warnings appear when relevant.
- Events are logged.

### 1.5 Telemetry and event logging

**Owner:** Claude backend + mobile

Emit at minimum:
- `session_started`
- `step_viewed`
- `step_completed`
- `assistant_invoked`
- `session_completed`[code_file:56]

Definition of done:
- Events are written and inspectable.
- Session funnel can be reconstructed from data.

### 1.6 Seed content for validation

**Owner:** Human + Claude assist, optionally simple CMS later

Before full Creator Studio, manually seed 2–5 genuinely usable projects in the database.[code_file:58]

Recommended first projects:
- Basic shelf assembly
- Curtain rod install
- Flat-pack chair assembly
- Simple wall hook install

Definition of done:
- A tester can complete a project using the app.

---

## What NOT to build yet

To protect speed and reduce confusion, do **not** prioritize these in Sprint 0–1:

- Full Creator Studio UX.[code_file:58]
- Marketplace monetization.
- Multi-tenant B2B admin.
- DID / verifiable credentials.[code_file:59]
- Advanced CV verification.[code_file:57]
- AR glasses support.[code_file:56]

These are valuable, but building them before the core loop works would increase rework risk.[code_file:58][code_file:59]

---

## Recommended implementation order for Lovable

Use this exact sequence when prompting Lovable:

1. **Implement PRD 01 only** — create the monorepo, Supabase schema, shared types, and core APIs.[code_file:55]
2. **Implement the mobile shell from PRD 02** — screens, auth, project browsing, session flow.[code_file:56]
3. **Implement the orchestrator MVP from PRD 03** — only assist mode, Tutor + Safety agents first.[code_file:57]
4. **Connect session telemetry and completion flow.**[code_file:56][code_file:57]
5. **Only after that**, implement internal CMS slices from PRD 04.[code_file:58]
6. **Only after consumer MVP is stable**, start B2B/tenant work from PRD 05.[code_file:59]

---

## Suggested prompting pattern for Lovable

### Prompt 1 — Backbone only

```text
Use 01-system-architecture-prd.md as the single source of truth.
Set up the monorepo, Supabase schema, shared packages, auth scaffolding, and core API endpoints exactly as specified.
Do not build AR UI, Creator Studio, or B2B features yet.
Keep the structure clean and AI-friendly.
```

### Prompt 2 — Mobile vertical slice

```text
Now use 02-ar-guided-diy-mvp-prd.md.
Build the mobile shell with auth, project list, project details, session creation, step progression, and completion flow.
Implement the ARView abstraction and a fallback non-AR mode.
Connect only to the existing v1 APIs.
```

### Prompt 3 — Orchestrator MVP

```text
Now use 03-multi-agent-orchestrator-prd.md.
Build the orchestrator endpoint in assist mode only.
Implement the Lyra-style 4-D flow in a simple version and support TutorAgent and SafetyCheckerAgent first.
All LLM calls must go through a shared abstraction.
```

### Prompt 4 — CMS after MVP loop works

```text
Now use 04-project-cms-creator-studio-prd.md.
Build the internal admin CMS for creating and editing projects and steps.
Keep it simple and form-based.
Do not build external creator marketplace features yet.
```

### Prompt 5 — B2B later

```text
Now use 05-b2b-identity-lyra-prd.md.
Add tenant tables, tenant admin pages, and tenant-scoped project APIs.
Design for future Lyra-compatible identity, but do not implement full DID/VC.
```

---

## Human review checklist after each Lovable pass

After each implementation pass, verify:

- Does the output still match the PRD rather than inventing new architecture?[code_file:55]
- Did Lovable centralize types and contracts instead of duplicating them?[code_file:55]
- Did it keep AI calls behind the orchestrator boundary?[code_file:57]
- Did it add unnecessary complexity too early?[code_file:58][code_file:59]
- Can the feature be demonstrated end-to-end right now?

If the answer to any of these is “no,” refine before moving forward.

---

## Best first milestone

The best first shippable milestone is:

**A signed-in user opens the app, picks a seeded DIY project, starts a session, follows steps in a simple AR or fallback view, asks one contextual AI question, and completes the project successfully.**[code_file:56][code_file:57]

That milestone proves:
- the architecture is real,
- the product loop is real,
- the agentic layer is real,
- and the business has something concrete to demo, test, and iterate on.

That is the right place to start.
