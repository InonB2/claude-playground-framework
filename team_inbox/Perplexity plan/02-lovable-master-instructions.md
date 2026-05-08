# BuildAR — Lovable Master Instructions

## Purpose

This file is the master brief for **Lovable**. Lovable is the primary builder for the internal web UI surfaces: CMS, Creator Studio, admin tooling, content operations, and selected diagnostics views.

Lovable is a **consumer of the backbone**, not the owner of the architecture. It must build quickly, cleanly, and within the backend constraints provided by Claude Code.[web:71]

---

## Mission

Build an internal web application that allows the BuildAR team to:
- manage projects,
- manage steps,
- manage media assets,
- preview content structure,
- operate the initial project library,
- and support internal workflows without redefining backend architecture.

---

## Authority boundaries

Lovable is allowed to:
- build within `/apps/web`,
- create and refine internal admin UX,
- connect to the existing Supabase instance and stable APIs,
- consume shared types,
- build forms, dashboards, asset workflows, and content operations.

Lovable is **not** allowed to:
- redesign database schema,
- create new backend contracts unilaterally,
- duplicate domain types locally,
- modify mobile app logic,
- bypass the orchestrator with direct frontend model calls,
- add B2B complexity in the first implementation window.

---

## Build order for Lovable

Lovable should not begin feature-rich work until Claude Code has completed:
- stable schema,
- shared types,
- auth,
- basic project/session contracts.

### Lovable Phase 1 — CMS v0
1. Project list view.
2. Project create/edit screen.
3. Step list and step editor.
4. Asset manager.
5. Role-aware access guard for admin/creator users.

### Lovable Phase 2 — Operational polish
1. Better filtering/search.
2. Publishing workflow.
3. Error-state handling.
4. Internal diagnostics/read-only event views.

### Deferred
Do not build yet unless approved:
- tenant admin,
- partner analytics,
- public creator marketplace,
- schema management features.

---

## Required product assumptions

Lovable must work from the assumption that:
- the CMS is initially an **internal operations tool**,
- the content library is initially seeded by the team,
- the first goal is operational speed, not creator-platform sophistication,
- forms and workflows should be optimized for reliability over visual spectacle.

---

## Technical rules

### App location
Lovable works only inside `/apps/web`.

### Shared contracts
Lovable must import shared types from the monorepo. No duplicated interfaces.

### Data access
Lovable should use the agreed backend access pattern:
- either server-side Supabase access for internal tools,
- or stable API routes supplied by Claude Code.

Do not invent mixed data paths per feature.

### Internationalization
The UI should be designed to support English and Hebrew, including RTL-ready layout where practical, but full multilingual productization should not block the first working CMS.[file:65][file:62]

### UX principle
Use a form-centric operational interface, not a marketing-site aesthetic. The CMS must optimize for speed, clarity, and error prevention.

---

## Required features for v0

### Project list
- list all projects,
- filter by status/category,
- create project,
- open project.

### Project editor
- title,
- slug,
- summary,
- category,
- difficulty,
- estimated time,
- status.

### Step editor
- ordered step list,
- create/edit/delete steps,
- step title,
- description,
- estimated time,
- overlay type,
- overlay metadata.

### Asset manager
- upload to Supabase Storage,
- preview existing assets,
- associate assets with project or step content.

### Access control
Restrict interface use to admin/creator roles according to the backend schema.

---

## UX guardrails

Lovable must avoid:
- over-animated dashboards,
- decorative complexity,
- hidden workflow steps,
- custom state machines that obscure CRUD behavior,
- introducing schema fields not yet defined.

The UI should make the data model visible and understandable.

---

## QA requirements

Lovable must ensure:
- forms validate before save,
- error states are visible and human-readable,
- loading states exist,
- no broken routes or dead buttons,
- no unauthorized access for non-admin/non-creator users.

---

## Handoff expectations

Lovable must document:
- what tables/endpoints it consumes,
- what assumptions it makes,
- any blockers caused by missing backend capability,
- and any required contract changes for Claude Code review.

Lovable should ask for backend changes rather than improvising them.
