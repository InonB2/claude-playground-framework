# BuildAR Pro CMS — Lovable Handoff (Ready to Use)

**Audience:** Inon, when you sit at the computer and want to ship the CMS.
**Status:** Ready to consume. Andy prepared this while you were away (2026-05-17).
**Estimated session time:** 60–90 minutes (most of it is Lovable generating + you reviewing).

---

## What this is

The internal **CMS** (admin web app) for BuildAR Pro. It is what the team uses to seed and manage the project library — projects, steps, image assets — without touching SQL. It is **not** the consumer mobile app. It is **not** public. It is a form-centric, utilitarian admin tool.

Lena wrote the full UX brief at `owner_inbox/design/buildar_cms_ux_brief.md` on 2026-05-15. The Lovable prompt below is extracted from that brief, untouched — Lena built it as paste-ready.

---

## Why this can only be done with you at the computer

Lovable's flow requires interactive steps that an agent cannot do:
1. Logging into lovable.dev with your account
2. Pasting the prompt and watching the generation stream
3. Connecting Lovable to the **live Supabase project** (auth grant, key paste)
4. Reviewing what was generated before approving deploy
5. Pulling the generated code into `D:/BuildAR/apps/web/` and committing

Everything else — schema, types, RLS, storage bucket — is being prepared in parallel by Silas right now so it is **ready when you arrive**.

---

## Pre-flight checklist — verify BEFORE pasting into Lovable

Andy will keep this section in sync as the pieces land. Check each box when you sit down.

- [ ] **Storage bucket exists.** Bucket name: `project-assets`. RLS: admin can upload, signed-URL read for app users.
  → Silas's BUILDAR-S2-002 (in progress today). Verify in Supabase Dashboard → Storage → Buckets. If it isn't there, the Asset Manager screen will fail on first upload.
- [ ] **FK ON DELETE clauses are live.** Migration 0004 adds `ON DELETE SET NULL` on `projects.published_by` and `events.user_id`.
  → Silas's BUILDAR-S2-001 (in progress today). Verify by running the migration's verification queries from the report in `agents/andy/inbox/silas_phase_b_done.md` (will exist when Silas finishes).
- [ ] **Shared types package is in place.** Lovable needs `@buildar/core-types` available. It already is — Yoni shipped it in BUILDAR-S1-006. Confirm: `D:/BuildAR/packages/core-types/src/` has `Project`, `ProjectStep`, `Asset`, `Session`, `Profile`, `Event` types.
- [ ] **You have these env values handy** to paste into Lovable when it asks:
  - `SUPABASE_URL` = `https://xbfgohafudrfygztqmtg.supabase.co` (live project)
  - `SUPABASE_ANON_KEY` = (from Supabase Dashboard → Settings → API → anon/public key — DO NOT use service_role key in Lovable)

---

## Step-by-step — what to do at the computer

### 1. Open Lovable
Go to https://lovable.dev. Sign in. Click "New Project".

### 2. Paste the full prompt below
Copy everything inside the `=== LOVABLE PROMPT START ===` / `=== END ===` block. Paste it into Lovable's initial prompt field. Hit Generate.

### 3. Connect Supabase when Lovable prompts you
Lovable will ask to connect a Supabase project. Choose "Connect existing project" and paste:
- URL: `https://xbfgohafudrfygztqmtg.supabase.co`
- Anon key: (from Supabase Dashboard)

**Do not** paste the service_role key into Lovable. The CMS uses anon key + RLS only.

### 4. Review the generated UI
Lovable will scaffold the app. Walk through it:
- Sidebar shows Projects + Assets
- Projects list shows the 2 seed projects (Wall Shelf Install, Table Assembly)
- Click "Edit" on a project — fields populate
- Steps section shows the 12 seeded steps in correct order
- Try drag-reordering one step — it should save
- Go to Assets tab — should be empty grid, "Upload Image" button visible

If anything is wrong, refine in Lovable (don't hand-edit code yet). Most fixes are 1 prompt-iteration.

### 5. Test access control (critical)
Lovable should restrict to admin/creator roles. Sign in with a non-admin user (or temporarily downgrade your role in `profiles` table via Supabase Dashboard) — you should see the full-page "Access restricted" screen, NOT the CMS UI.

### 6. Pull the code into the monorepo
Lovable lets you export or push to GitHub. Either:
- **Option A (recommended):** Connect Lovable's "Push to GitHub" to `InonB2/buildar-pro` on a branch like `feat/cms-v0-lovable`. This creates a PR that Yoni can review.
- **Option B:** Export as a ZIP, drop the contents into `D:/BuildAR/apps/web/`, commit to a branch yourself.

Either way: the destination is `D:/BuildAR/apps/web/`. Yoni's monorepo already reserves that directory.

### 7. Verify CI passes
Open the PR. The 5-job CI workflow (lint, typecheck, test, migration-validate) should run automatically. If lint or typecheck fails, ping Andy — we'll dispatch Dev or Yoni to clean up.

### 8. Tell Andy "Lovable CMS pushed, PR #X open"
Andy will dispatch Vera (UI QA) + Jasmin (security/access-control QA) for sign-off, then merge.

---

## === LOVABLE PROMPT START ===

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

Assets are stored in Supabase Storage bucket `project-assets`. Each asset record in the database has: id, filename, storage_path, url, created_at.

Loading state: show a grid of grey skeleton tiles (matching tile dimensions) while the asset list loads.

Empty state: centered message — "No assets yet. Upload your first image."

Error on upload: show an error message above the grid — "Upload failed. Only JPEG, PNG, and WebP files are supported. Max file size: 10MB."

Error on load: inline error above grid with retry button.

---

### Data access pattern

Connect directly to Supabase using the project's Supabase client instance. Import and use shared TypeScript types from `@buildar/core-types` for all data models (Project, ProjectStep, Asset). Do not define local type duplicates — import from the shared package.

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

## === LOVABLE PROMPT END ===

---

## Success criteria — Gate C closes when

- [ ] CMS deployed at a private URL (Lovable hosts, or pushed to apps/web in monorepo and deployed via Vercel)
- [ ] Internal user with admin role can log in, see project list, edit a project, reorder its steps, upload an image asset
- [ ] Non-admin user is blocked at the access-denied screen
- [ ] All data is in the live Supabase project (xbfgohafudrfygztqmtg) — no separate database, no schema hacks
- [ ] CI passes on the PR (lint, typecheck, tests, migration-validate)
- [ ] Vera QA: PASS on UX + a11y; Jasmin QA: PASS on access control + RLS pass-through

When all 6 are green, Gate C is closed and we are ready for Gate B testing on real content the operator created.

---

## Open questions that should NOT block you

These have answers already — listed in case you wonder:

1. **Why not let Lovable manage the schema?** Lovable can be over-eager and add columns. Schema is owned by Silas + migration files. Lovable consumes; it does not define.
2. **Why not let Lovable own auth?** Auth is already live in Supabase (BUILDAR-S1-001). Lovable uses the existing auth.
3. **Why no creator/marketplace features?** Out of scope for Phase 0–1 per Perplexity plan (`04-product-prd-phase-0-1.md` § Non-goals).
4. **What if Lovable generates ugly code?** Fine — internal tool, utilitarian. Yoni can refactor later if needed. Function over form.
5. **What if Lovable picks a different state-management library than Yoni's mobile shell?** Fine — CMS is web (React), mobile is React Native. They don't share a frontend bundle.

---

## If you hit a blocker

Send a Telegram to Andy with the screenshot and `BLOCKER: Lovable CMS` in the message. Andy will dispatch Yoni or Dev as needed and reply with next steps within minutes.
