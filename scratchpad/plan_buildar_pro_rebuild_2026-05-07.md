# Plan: BuildAR Pro — Full Rebuild Attack Plan
**Date:** 2026-05-07  
**Author:** Andy (Orchestrator)  
**Status:** Awaiting Inon confirmation + answers to 6 open questions before first agent dispatch

---

## What I read

- `team_inbox/Perplexity plan/` — 5 files (01–04, 06; file 05 deliberately absent — B2B is deferred)
- `team_inbox/BuildAR Pro/PRD for Lovable and Andy/` — prior PRD set + sprint 0–1 plan
- `tasks/active_tasks.json` — 4 in-flight BuildARPro tasks
- `scratchpad/buildarpro_schema.sql` — Silas's existing 5-table schema (deployed to `meonilvpqerbemeikrfk`)

---

## Honest assessment of the Perplexity plan

### What's excellent — do not change

1. **Backbone-first sequencing.** Monorepo → schema → types → auth → APIs → mobile → CMS. This is the right order. Lovable should not touch the CMS until shared contracts are stable.
2. **Lovable as consumer, not owner.** Lovable builds within `/apps/web` only. Backend contracts belong to Claude Code (our team). This prevents schema drift.
3. **AR abstraction layer.** Not blocking on advanced AR fidelity. Fallback mode lets the product loop run before AR is perfect. Smart.
4. **Thin orchestrator MVP first.** TutorAgent + SafetyAgent only. Defer planning mode, dynamic tools, and complex graph. Correct.
5. **Acceptance gates (A/B/C).** Clear go/no-go criteria at each major transition. This is how you prevent scope creep.
6. **Prompt caching built in.** Repeated session context should be cached from day one. This is already coded into our `packages/ai-client` spec.
7. **Vertical slice over horizontal layers.** One working user flow end-to-end before anything else.

### What I'd change or flag

#### 1. Schema conflict — existing vs. new
Silas's deployed schema uses a `users` table. The new plan uses `profiles`. The new plan also requires 6 tables; Silas deployed 5.  
**Decision needed:** Do we adopt the existing Supabase project (`meonilvpqerbemeikrfk`) and migrate it, or start fresh with a clean project?  
**My recommendation:** Start fresh. The existing schema was a prototype; building clean migrations on top will be faster than patching.

#### 2. "Claude Code" = our team agents
The plan is written for a single "Claude Code" actor. In our setup:
- **Yoni** = monorepo init, shared types, APIs, orchestrator
- **Silas** = Supabase schema, migrations, RLS
- **Mack** = GitHub repo, CI/CD pipeline, secrets/env management
- **Lena** = Mobile UX design (screen flows)
- **Tomy** = Pre-build research (AR lib, Expo vs bare RN)
- **Jasmin/Maya/Vera** = review gates

Lovable = Inon runs the Lovable tool with our master instructions (file 02 from Perplexity plan).

#### 3. Open questions must be answered before build starts
File 06 lists 6 questions that agents should NOT guess. These are the gate to Sprint 0 start.

#### 4. Deferred BuildARPro tasks need status change
Three existing tasks conflict with the new approach and should be formally deferred:
- `PROMAKER-AR-005` (LlamaParse) — not in Phase 0–1 scope
- `PROMAKER-AR-012` (Stripe) — monetization deferred until loop is proven
- `PROMAKER-AR-013` (Vuforia) — specific AR vendor TBD; deferred pending Tomy's research

#### 5. HR gap — DevOps agent
No dedicated DevOps/CI-CD agent on the team. The CI/CD pipeline design (GitHub Actions, PNPM workspaces, Supabase branching, preview environments) is complex. Mack handles automation, but this is a heavier infrastructure job. Recommend Pat research a DevOps/Cloud Infrastructure agent profile.

#### 6. AR library not specified
The plan says "React Native with native AR capability behind an abstraction layer" but doesn't commit to a specific library. Options: WebXR, ViroReact, ARKit/ARCore native modules, Expo Camera + Three.js, 8th Wall. This decision gates the mobile shell.  
**Tomy must research this before Yoni starts mobile work.**

---

## Attack Plan — Stage by Stage

### Stage 0: Alignment (Today — before any agent starts)

**Goal:** Answer all open questions. Agree on scope. Clean up old tasks.

**Owner:** Andy + Inon

Actions:
1. Inon answers 6 open questions (see section below).
2. Andy updates `tasks/active_tasks.json`: defer PROMAKER-AR-005, -012, -013.
3. Andy confirms whether to use existing Supabase project or create fresh one.
4. Andy dispatches Tomy for pre-build research (parallel, non-blocking).

**Exit criteria:** 6 questions answered, task list cleaned, research dispatched.

---

### Stage 1: Pre-build Research (Parallel while Inon answers questions)

**Owner:** Tomy

Deliverables to `owner_inbox/research/buildar_prebuild_research.md`:
- AR library comparison for React Native (ViroReact, ARKit/ARCore native, Expo, WebXR, 8th Wall) — which is best for Phase 0–1 fallback-first approach?
- Expo managed vs bare workflow for AR — which keeps the abstraction layer clean?
- PNPM monorepo + Supabase branching — any known issues or setup gotchas in 2025/2026?
- Existing `meonilvpqerbemeikrfk` schema: compare Silas's 5 tables vs the 6 required tables in the new plan — delta analysis.

**Parallel:** No blockers. Tomy can start immediately.

---

### Stage 2: Backbone (Sprint 0)

**Gate:** Stage 0 complete + Tomy research delivered.

**Yoni (monorepo + APIs)**
- Initialize PNPM monorepo with structure from file 01
- Create `packages/core-types` with minimum domain types
- Create `packages/validation` (Zod)
- Create `packages/ai-client` (wrapper with prompt caching hooks)
- Create `packages/utils`
- Scaffold `/apps/api` with versioned routes: `GET /api/v1/projects`, `GET /api/v1/projects/:id`, `POST /api/v1/sessions`, `PATCH /api/v1/sessions/:id`
- Scaffold `/apps/mobile` (shell only)
- Scaffold `/apps/web` (empty — Lovable's territory)

**Silas (schema + migrations)**
- Design clean 6-table migration set aligned to new plan
- Tables: `profiles`, `projects`, `project_steps`, `assets`, `sessions`, `events`
- RLS on all user-scoped entities
- `profiles` auto-create trigger on auth.users insert
- Seed data: 2–5 projects (Inon confirms which ones)
- Migration-first; no manual SQL in Supabase console

**Mack (CI/CD + environment)**
- Create new GitHub repo `buildar-pro` (or confirm repo name with Inon)
- GitHub Actions: lint, typecheck, test, migration validation on every PR
- Environment file structure: `.env.example` with all required variables
- Configure Supabase branching for preview environments
- Add all API keys as GitHub secrets: Supabase service key, Anthropic key

**Jasmin (auth security review)**
- Review auth model (Supabase email auth) against OWASP
- Review RLS policies Silas designed
- Sign off before Gate A

**Gate A criteria:**
- Monorepo installs and compiles
- Migrations apply cleanly
- Auth works (signup + signin)
- Project + session endpoints return correct typed responses
- Seeded data exists
- CI passes on PR

---

### Stage 3: Product Loop (Sprint 1)

**Gate:** Gate A accepted by Andy + Inon.

**Yoni (mobile shell + session flow)**
- Mobile screens: Sign-in/up, Home/Project list, Project detail, Session, Step view, Completion
- Session lifecycle: create, resume, step navigation, complete
- AR abstraction layer: `ARView` component with fallback non-AR mode
- One overlay type rendered reliably

**Yoni (orchestrator MVP)**
- `POST /api/v1/orchestrator/assist`
- Shared `callLLM()` abstraction (through `packages/ai-client`)
- TutorAgent: contextual guidance using project/session/step context
- SafetyAgent: safety warnings for risky steps
- Structured logging of all invocations

**Yoni/Mack (telemetry)**
- Emit events: `session_started`, `step_viewed`, `step_completed`, `assistant_invoked`, `session_completed`
- Events written to `events` table, inspectable

**Lena (mobile UX design)**
- Design brief for all 5 mobile screens before Yoni implements them
- Focus on clarity and low friction — not marketing aesthetics
- RTL-compatible layout (Hebrew deferred but architecture support required)

**Gate B criteria:**
- User can authenticate
- Browse seeded projects
- Start a session, move through all steps
- Ask assistant one question, get context-aware response
- Complete session
- Events are logged and inspectable

---

### Stage 4: CMS via Lovable (parallel after Gate A)

**Gate:** Gate A accepted.

**Inon (runs Lovable):** Use `team_inbox/Perplexity plan/02-lovable-master-instructions.md` as the exact prompt to Lovable. Follow the suggested prompting sequence:
1. First: file 01 backbone (Lovable reads the stable contracts from our monorepo)
2. Then: CMS v0 features from file 02

**Lena (CMS UX design brief)**
- Simple operational interface spec for: project list, project editor, step editor, asset manager
- Form-centric, not marketing-site aesthetic
- Deliver before Inon runs Lovable CMS prompt

**Rex (Lovable output reviewer)**
- After each Lovable build pass, Rex reviews output against the checklist in `buildar_sprint0_sprint1_plan.md`
- Flags if Lovable invents types, breaks contracts, or adds unauthorized schema changes
- Rex does NOT reimplement — he flags for Inon to re-prompt Lovable

**Gate C criteria:**
- Internal user can create/edit projects and steps
- Assets can be uploaded and linked
- Access control works (admin/creator roles only)
- CMS makes no schema changes outside Silas's migrations

---

### Stage 5: Hardening

**Gate:** Gates B + C both accepted.

- **Jasmin:** Backend security gate review (API auth, RLS completeness, orchestrator safety)
- **Maya:** OWASP audit of API surface
- **Vera:** Mobile + CMS QA (responsive, accessibility, no broken flows)
- **Yoni/Silas:** Fix all findings, then Jasmin signs off
- Write release checklist + go-live prep

---

### Stage 6: HR Gap — New Agent Research

**Owner:** Pat → Nolan (if approved)

**Gaps to research:**

1. **DevOps / Cloud Infrastructure Agent**
   - Need: GitHub Actions monorepo CI, Supabase branching, preview environments, Railway/Fly.io/Vercel deployment, secrets management
   - Current coverage: Mack handles automation but not deep infra design
   - Pat deliverable: Candidate profile brief for a DevOps agent

2. **Mobile / React Native Specialist Agent** (decide after Tomy's AR research)
   - If Expo + AR abstraction stays clean, Yoni can handle it
   - If native AR modules are required, a specialist is needed
   - Pat deliverable: Hold pending Tomy research

**Pat starts on DevOps profile immediately (parallel).**

---

## 6 Open Questions — Inon must answer before Stage 2 starts

From `team_inbox/Perplexity plan/06-project-startup-checklist-and-open-questions.md`:

| # | Question | Why it matters |
|---|----------|---------------|
| 1 | **Mobile path:** Expo-managed or bare React Native from day one? | Gates AR library selection and Yoni's mobile scaffold |
| 2 | **Web data access:** CMS uses direct server-side Supabase, or only through `/api/v1/` routes? | Gates Silas's RLS design and Lovable's integration pattern |
| 3 | **Deployment topology:** Separate `/api` and `/orchestrator` deployables, or one backend service? | Gates Mack's CI/CD and Yoni's repo structure |
| 4 | **Hebrew in CMS v0:** Required in first usable release, or only architecture support? | Gates Lena's design brief and Lovable's scope |
| 5 | **Seed library:** Which exact 2–5 projects to seed? (e.g. shelf assembly, curtain rod, flat-pack chair, wall hook) | Gates Silas's seed data and first demo |
| 6 | **Publishing model:** Who can publish project changes initially — just you (Inon), or any creator role? | Gates RLS design and CMS access control |

Plus one Andy-added question:

| 7 | **Supabase project:** Use existing `meonilvpqerbemeikrfk` (migrate schema) or create a fresh project? | Gates Silas's migration strategy |

---

## What to do with existing BuildARPro tasks

| Task ID | Title | Recommended action |
|---------|-------|--------------------|
| PROMAKER-AR-005 | LlamaParse API connection | **Defer** — not in Phase 0–1 scope |
| PROMAKER-AR-012 | Stripe product + subscription | **Defer** — monetization after loop is proven |
| PROMAKER-AR-013 | Vuforia account + Image Target | **Defer** — specific AR vendor TBD pending Tomy research |
| PROMAKER-AR-003 | Pitch deck stealth version | Keep pending-owner — separate deliverable, not blocked |
| PROMAKER-AR-010 | Supabase schema applied | **Superseded** — new plan replaces this schema |

---

## Agent dispatch summary (if Inon confirms)

| Agent | When | Task |
|-------|------|------|
| Tomy | Immediately (no blockers) | Pre-build AR + monorepo research |
| Pat | Immediately (no blockers) | DevOps agent profile brief |
| Silas | After Q1–Q7 answered | Schema design + migrations |
| Mack | After Q3 answered (topology) | GitHub repo + CI/CD |
| Lena | After Q4 answered (Hebrew) | Mobile UX + CMS UX design briefs |
| Yoni | After Silas + Mack + Tomy done | Monorepo init + APIs + mobile shell |
| Jasmin | After Silas schema done | Auth + RLS security review |
| Rex | After Lovable CMS v0 | Review Lovable output vs checklist |
| Maya + Vera | After Gates B + C | Security audit + QA |

---

## Risks flagged

| Risk | Mitigation |
|------|-----------|
| Scope creep into Creator Studio / B2B | Acceptance gates A/B/C are hard stops |
| AR blocking the loop | Fallback non-AR mode is mandatory from day one |
| Contract drift between Lovable and our backend | Rex reviews every Lovable pass |
| Orchestrator cost/latency | Prompt caching in `packages/ai-client` from day one |
| Schema instability | Migration-first policy; Silas signs off all schema changes |
| DevOps gap slowing CI/CD | Pat researches agent immediately |
