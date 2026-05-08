# BuildAR — Product PRD for Phase 0–1

## Product summary

BuildAR Phase 0–1 delivers the first working version of an AI-assisted, mobile-first guided DIY experience. The product must let a user authenticate, browse a small seeded project library, start a project session, move through guided steps with a simple AR-capable or fallback presentation layer, ask contextual AI questions, and complete the session successfully.[web:85][web:94]

The goal of this phase is not to build the entire long-term platform. The goal is to validate the product loop and establish a clean technical backbone that can support later CMS, creator, and B2B expansion.[web:71]

---

## Goals

1. Prove the consumer guidance loop works.
2. Establish stable architecture and shared contracts.
3. Capture enough telemetry to learn from first usage.
4. Enable internal content operations through a lightweight CMS.
5. Keep scope tight enough that AI agents can implement reliably.

---

## Non-goals

This phase explicitly excludes:
- full creator marketplace,
- partner tenanting,
- advanced computer vision verification,
- headset clients,
- DID/verifiable credential identity rails,
- public API platformization.

---

## Users

### End user
A consumer using a mobile app to complete a guided DIY or assembly task.

### Internal operator
A team member who seeds and manages projects, steps, and assets.

---

## User stories

### End-user stories
- As a user, I want to sign in and browse available projects.
- As a user, I want to understand what a project requires before starting.
- As a user, I want to start a session and resume later if interrupted.
- As a user, I want step-by-step guidance in a clear, low-friction mobile flow.
- As a user, I want to ask questions in context when I get stuck.
- As a user, I want to complete a project and feel confident I finished it.

### Internal operator stories
- As an operator, I want to create and edit projects and steps without touching SQL.
- As an operator, I want to upload and attach assets.
- As an operator, I want confidence that only approved roles can modify content.

---

## Scope

### Included in Phase 0–1
- monorepo backbone,
- Supabase schema and auth,
- seeded project library,
- mobile app shell,
- session lifecycle,
- simple AR abstraction and non-AR fallback,
- orchestrator assist mode,
- event logging,
- internal CMS v0.

### Deferred
- advanced AR precision,
- advanced agent graph,
- external creator tooling,
- tenant settings,
- partner analytics.

---

## Functional requirements

### 1. Authentication
- Users must be able to sign up and sign in.
- Authenticated APIs must derive identity from auth tokens.

### 2. Project discovery
- Users must be able to view a list of available projects.
- A project detail view must show title, summary, category, difficulty, time estimate, and required tools/materials when available.

### 3. Session lifecycle
- Starting a project creates a session.
- A session stores current step, status, and timestamps.
- A user can resume an active session.
- A user can complete a session.

### 4. Guided step flow
- Each project includes ordered steps.
- The session UI must show the current step and allow previous/next navigation where permitted.
- The session UI must support a basic AR-oriented view abstraction.
- If AR is unsupported or unstable, a fallback step presentation must still let the user proceed.

### 5. Assistant
- The user can ask contextual questions during a session.
- The assistant receives session, project, and step context.
- The assistant must be able to provide guidance and safety-oriented warnings.

### 6. CMS v0
- Internal users can list, create, and edit projects.
- Internal users can list, create, edit, and order project steps.
- Internal users can upload and attach assets.

### 7. Telemetry
- The system must log session start, step view, step completion, assistant invocation, and session completion.

---

## Non-functional requirements

### Reliability
- Core flows must work in dev and preview environments consistently.[web:71]

### Performance
- Mobile app startup and session navigation should remain lightweight; avoid unnecessary startup work and UI-thread blocking patterns.[web:85][web:92]

### Safety
- Assistant must include safety-aware behavior for risky instructions.

### Maintainability
- Shared types and validation must be centralized.
- Schema changes must be migration-driven.

### Cost control
- Repeated orchestrator context should be designed for caching where applicable to reduce repeated prompt overhead.[web:80][web:94]

---

## Success metrics

### Product metrics
- successful project session completion,
- assistant usage during sessions,
- step drop-off visibility,
- average session duration.

### Technical metrics
- clean migration success rate,
- API error rate,
- orchestrator latency,
- mobile crash-free sessions.

---

## Acceptance criteria

Phase 0–1 is complete when:
- a user can authenticate,
- browse a seeded project,
- start and resume a session,
- progress through all steps,
- ask at least one contextual question,
- complete the session,
- and the team can manage content through the CMS.
