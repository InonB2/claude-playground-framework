# Project CMS & Creator Studio PRD (For Lovable & Claude Agents)

## 1. Purpose and Audience

This PRD defines the **Project Content Management System (CMS)** and **Creator Studio** used to author, manage, and publish AR‑guided DIY projects.

Audience:
- AI agents (Lovable, Claude) implementing web UI and backend APIs.
- Human admins and creators managing project content.

This system is used initially by internal staff to create 10–20 seed projects, then later by external creators (phased rollout).

---

## 2. Goals and Non‑Goals

### 2.1 Goals

1. Provide a web‑based interface to **create, edit, and publish projects and steps**.
2. Store project data in Supabase with **strong typing and versioning**.
3. Provide a structured way to define **AR overlay metadata** per step.
4. Prepare for external creator onboarding (permissions & roles), even if MVP uses internal authors only.

### 2.2 Non‑Goals

- Complex monetization, pricing, and marketplace UX.
- In‑browser 3D editing (start with simple forms and attachments).

---

## 3. Web App Scope

- Implemented in `/apps/web` (Next.js 14+).
- Sections:
  - Admin dashboard (internal only at first).
  - Project list, project editor, step editor.
  - Asset management (simple view of uploaded files).

Auth:
- Restrict CMS access to users with `role IN ('admin','creator')` in `profiles` table.

---

## 4. Data Model (Supabase)

### 4.1 Tables

#### 4.1.1 `projects`

Columns (subset):
- `id` (uuid, pk)
- `slug` (text, unique)
- `title` (text)
- `summary` (text)
- `category` (text)
- `difficulty` (text)
- `estimated_minutes` (int)
- `hero_image_asset_id` (uuid, fk → `assets.id`, nullable)
- `status` (enum: 'draft' | 'published' | 'archived')
- `created_by` (uuid, fk → `profiles.id`)
- `created_at`, `updated_at`

#### 4.1.2 `project_steps`

- `id` (uuid, pk)
- `project_id` (uuid, fk → `projects.id`)
- `index` (int)
- `title` (text)
- `description` (text)
- `overlay_type` (text: 'arrow'|'ghost_model'|'highlight'|'none')
- `overlay_data` (jsonb)
- `estimated_minutes` (int, nullable)

Indices:
- Unique (`project_id`, `index`).

#### 4.1.3 `assets`

- `id` (uuid, pk)
- `bucket` (text)
- `path` (text)
- `type` (text: 'image'|'model'|'doc'|...)
- `created_by` (uuid)
- `created_at`

#### 4.1.4 `profiles`

- Extended from Auth; add columns:
  - `role` (enum: 'user' | 'creator' | 'admin')

#### 4.1.5 `project_versions` (optional Phase 2)

- `id` (uuid)
- `project_id` (uuid)
- `data` (jsonb) – snapshot of project + steps
- `created_at`, `created_by`

---

## 5. CMS Features

### 5.1 Project List

- Table view with columns: title, status, category, updated_at.
- Filters: status, category, creator.
- Actions:
  - Create project.
  - Edit project.
  - Archive project.

### 5.2 Project Editor

Sections:
1. **Metadata Panel:** title, summary, category, difficulty, estimated time.
2. **Hero Image:** upload/select from assets.
3. **Tools & Materials:**
   - Simple repeatable text fields for MVP.
4. **Steps List:**
   - Reorderable list of steps with index, title, time.

Actions:
- Save draft.
- Publish (sets status = 'published').

### 5.3 Step Editor

For each step:
- Title (text).
- Description (rich text or multiline plain text).
- Estimated time.
- Overlay configuration:
  - `overlay_type` (select).
  - JSON editor/structured form for `overlay_data` (MVP: simple key/value pairs like `"anchor": "wall_plane"`, `"arrowDirection": "down"`).

Future:
- Visual helpers for overlay (e.g., diagrams or screenshots) can be attached as assets.

### 5.4 Asset Management

- Simple list of uploaded files with search by name and type.
- Link to Supabase Storage buckets and paths.
- Allow selection of assets for hero images or step illustrations.

---

## 6. API Contracts (Web ↔ Backend)

Implement internal API routes or direct Supabase client usage in Next.js server components for CMS.

Shared types defined in `/packages/core-types`:

```ts
export interface ProjectInput {
  title: string;
  summary: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedMinutes: number;
  heroImageAssetId?: string;
}

export interface ProjectStepInput {
  title: string;
  description: string;
  overlayType: 'arrow' | 'ghost_model' | 'highlight' | 'none';
  overlayData: Record<string, any>;
  estimatedMinutes?: number;
}
```

Operations:
- `createProject(input: ProjectInput)` → `Project`.
- `updateProject(id, input)`.
- `createStep(projectId, input)`.
- `updateStep(id, input)`.
- `reorderSteps(projectId, orderedStepIds)`.

Implementation can be inside `/apps/web` or `/apps/api`, but must use shared types.

---

## 7. Roles and Permissions

- `admin`:
  - Can create/edit/delete projects and steps.
  - Can publish/unpublish.
  - Can manage roles of other profiles.
- `creator`:
  - Can create/edit projects they own.
  - Can propose publish; admin approves (MVP: admin manually sets status).
- `user`:
  - Cannot access CMS.

RLS must enforce that `creator` only sees and edits projects where `created_by = auth.uid()`.

---

## 8. UX and Design Guidelines

- Keep UI **form‑centric and minimal** for MVP so Lovable agents can implement quickly.
- Use a consistent design system (buttons, inputs, cards) shared with user‑facing web where possible.
- Provide inline help text for AR overlay fields to reduce confusion.

---

## 9. Implementation Guidance for AI Agents

1. **Use Supabase client** in server components / API routes to interact with DB.
2. Reuse `core-types` and avoid re‑declaring interfaces.
3. Validate inputs on both client and server; return clear error messages for required fields.
4. Ensure RLS rules are in place and tested (attempt unauthorized access in tests).

---

## 10. Acceptance Criteria

CMS & Creator Studio MVP is complete when:

1. An admin can:
   - Create a project with metadata.
   - Add and reorder steps.
   - Configure basic overlay metadata.
   - Publish the project.
2. Mobile client can:
   - Fetch `published` projects and steps and use them for AR sessions.
3. RLS rules prevent non‑authorized users from editing projects they do not own.
4. At least 10 real seed projects are authored and usable end‑to‑end.
