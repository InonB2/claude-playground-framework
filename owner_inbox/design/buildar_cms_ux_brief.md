# BuildAR Pro — CMS UX Brief (Lovable Prompt)
**Version:** 1.0  
**Author:** Lena (UI/UX Designer)  
**Date:** 2026-05-15  
**Audience:** Inon (paste into Lovable), Yoni (implementation reference)

---

## How to use this document

The section titled **"Lovable Prompt"** below is the complete prompt to paste into Lovable. Everything above and below that section is context for the team — do not paste it into Lovable.

---

## Internal context (do not paste into Lovable)

This CMS is an internal operational tool for the BuildAR Pro team. It is not a public product. Its job is to let one or two content operators manage the project library without touching the database directly. It must be functional, readable, and reliable — not beautiful. Lovable will generate a frontend; the data layer is Supabase with shared types from `@buildar/core-types`. The generated code should be clean enough that Yoni can extend it.

---

## Lovable Prompt

---

This is an internal CMS for BuildAR Pro, a mobile DIY guidance app. Only admin/creator role users have access. Build this as a form-centric operational web interface — not a marketing site, not a consumer app. The design should be clean and utilitarian: sidebar navigation on the left, main content area on the right, no decorative hero sections or landing page patterns.

### Access control

If the authenticated user does not have the `admin` or `creator` role, show a full-page access denied screen with the message "Access restricted. Contact your administrator." and no navigation. Do not show a 404 — show an explicit access denied state. Role is derived from the Supabase auth JWT using `user_metadata.role`.

### Layout

Use a persistent left sidebar (fixed width, ~220px) with the following navigation items:
- Projects
- Assets

The main content area fills the remaining width. No top navigation bar is needed. Show the logged-in user's email at the bottom of the sidebar. Include a "Sign out" link at the bottom of the sidebar.

All pages use the main content area — the sidebar never changes during normal use.

---

### Screen: Projects List

Route: `/projects`

Show a table of all projects. Columns: Title, Category, Difficulty (1–5 numeric), Estimated time (minutes), Status, Actions.

The Status column shows a badge: "Draft" (muted/grey) or "Published" (green). 

Above the table, show two filter buttons: "All", "Draft", "Published". Clicking a filter updates the table in place — no page reload. Default to "All" on load.

Each row in the Actions column has two icon buttons: Edit (pencil icon) and Delete (trash icon). 

- Edit navigates to the Project Edit screen for that project.
- Delete shows an inline confirmation directly in the row (replace the icon buttons with "Delete?" and "Yes, delete" / "Cancel" text buttons) before performing the delete. Do not use a modal dialog for delete confirmation.

Above the filter buttons, show a "New Project" button (primary style, right-aligned). It navigates to the Project Create screen.

Loading state: show a full-width skeleton table with 3 placeholder rows while data fetches.

Empty state (no projects, or no projects matching the current filter): centered message in the table area — "No projects found." with a "Create your first project" link if the filter is "All".

Error state: inline error message above the table — "Failed to load projects. Try again." with a retry button.

---

### Screen: Project Create / Edit

Route: `/projects/new` and `/projects/:id/edit`

Both routes use the same form. On the Edit route, pre-populate all fields from the existing project record.

Form fields:

| Field | Input type | Validation |
|---|---|---|
| Title | Text input | Required, max 120 characters |
| Slug | Text input | Required, lowercase letters/numbers/hyphens only, auto-generated from Title (user can override) |
| Summary | Textarea | Required, max 500 characters. Show character count below the field. |
| Category | Text input | Required |
| Difficulty | Number input (1–5) or segmented control showing "1 2 3 4 5" | Required, integer 1–5 |
| Estimated minutes | Number input | Required, positive integer |
| Status | Select dropdown: "Draft" / "Published" | Required, defaults to "Draft" on create |

Below the form, show a "Steps" section (only on Edit route — not on Create). See the Steps section below.

Form footer: "Save" button (primary, right-aligned) and "Cancel" link (left-aligned, navigates back to Projects List).

Validation behavior: validate all fields on "Save" click before submitting. Show inline error messages directly below the field that failed — do not use a toast or a summary at the top of the form. Do not disable the Save button while the form is untouched; only show errors after a save attempt.

Loading state on Save: replace the "Save" button label with a spinner. Keep the button disabled until the request completes.

Success: after save, navigate to the Projects List and show a brief success toast at the bottom of the screen — "Project saved."

Error on save: restore the Save button to its default state and show an inline message above the Save button — "Save failed. Check your connection and try again."

Slug auto-generation: when the user types in the Title field, automatically populate the Slug field by converting the title to lowercase, replacing spaces with hyphens, and stripping non-alphanumeric characters. If the user manually edits the Slug field, stop auto-generating from the Title for this session.

---

### Screen: Steps (embedded section in Project Edit)

This section appears below the project form fields on the Project Edit route. It is not a separate route.

Show a reorderable list of steps for the current project. Each row shows: drag handle (left), step order number, step title, and an Edit icon and Delete icon (right).

- Drag to reorder: use drag-and-drop on the drag handle. On drop, save the new order immediately via a PATCH request. Show a brief "Saving..." inline indicator next to the section heading while the request is in flight.
- Edit step: opens a step edit form inline (expand the row, do not navigate away). The inline form shows: Title (text, required), Description (textarea, required), Order (read-only, derived from position). A step can also have an attached image asset — show a simple asset selector (see Assets section) or "No image attached" if none. Save and Cancel buttons appear in the expanded row.
- Delete step: same inline confirmation pattern as project delete (no modal).
- "Add Step" button at the bottom of the list: appends a new blank step edit form at the end of the list.

Loading state for the steps list: skeleton rows while the step data loads alongside the project.

Empty state: "No steps yet. Add your first step." with an "Add Step" link.

Error on reorder: restore previous order visually and show an inline error — "Couldn't save new order. Try again."

---

### Screen: Assets

Route: `/assets`

Show a grid of uploaded image assets. Each tile shows: thumbnail preview (fill the tile, object-fit cover), filename below the thumbnail, and a delete icon (top-right corner of the tile, visible on hover).

Above the grid, show an "Upload Image" button that opens the browser's native file picker (accept: image/jpeg, image/png, image/webp). After a file is selected, upload it immediately (do not require a separate confirm step). Show an upload progress indicator in place of the tile while uploading. On completion, insert the new tile into the grid.

Delete: same inline confirmation pattern — clicking the delete icon replaces the icon with "Delete? Yes / No" directly on the tile.

Assets are stored in Supabase Storage. Each asset record in the database has: id, filename, storage_path, url, created_at.

Loading state: show a grid of grey skeleton tiles (matching tile dimensions) while the asset list loads.

Empty state: centered message — "No assets yet. Upload your first image."

Error on upload: show an error message above the grid — "Upload failed. Only JPEG, PNG, and WebP files are supported. Max file size: 10MB."

Error on load: inline error above grid with retry button.

---

### Data access pattern

Connect directly to Supabase using the project's Supabase client instance. Import and use shared TypeScript types from `@buildar/core-types` for all data models (Project, Step, Asset). Do not define local type duplicates — import from the shared package.

Use Supabase's Row Level Security for access control. The frontend should not implement its own permission logic beyond checking the user's role for the access denied screen — trust Supabase RLS for data-level enforcement.

All async operations (fetch, create, update, delete) must have:
- A loading state (spinner or skeleton, never a frozen UI)
- An error state with a user-visible message and a retry action where applicable
- No silent failures — every failed operation must show feedback to the user

---

### UX guardrails — what NOT to build

Do not build any of the following:

- **No creator marketplace** — this CMS is for internal operators only. There is no public-facing creator sign-up, no creator profiles, no submission or approval workflow.
- **No public-facing pages** — every route in this app requires authentication. There is no public homepage, no project preview page, no shareable link.
- **No tenant or B2B features** — there is one organization, one team. No workspace switching, no invite flows, no multi-tenant architecture.
- **No analytics or reporting screens** — no charts, no session metrics, no usage dashboards. Those live in Supabase Studio.
- **No rich text editor** — the Description field for steps is a plain textarea. No markdown preview, no WYSIWYG.
- **No drag-and-drop for assets** — file picker only. No drag-to-upload zone.
- **No pagination on the projects list** — there are 2 seed projects in Phase 0–1. A simple table with all results is correct. Do not add pagination, infinite scroll, or cursor-based loading.

---

*End of Lovable prompt.*

---

## Implementation notes for Yoni (not for Lovable)

- The CMS is a separate Lovable-generated app, not part of the React Native mobile bundle. It is a web app.
- Shared types from `@buildar/core-types` must be kept in sync with the Supabase schema — this is Yoni's responsibility when schema changes happen.
- Step reorder should use a `position` integer column on the `steps` table, updated atomically. Avoid floating-point ordering schemes.
- Asset URLs from Supabase Storage should be stored as public URLs in the `assets` table so the mobile app and CMS can reference them without re-signing.
