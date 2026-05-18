# BuildAR Pro CMS — Sequential Lovable Build Plan

**For:** Inon — paste these in order, review between each
**Status:** Ready to consume when you're at the computer
**Author:** Andy (orchestrating) + Lena (UX brief is the source of truth)
**Date:** 2026-05-17

---

## Why sequential, not one big prompt?

Lovable is more reliable when building one feature at a time. The earlier single-prompt approach (preserved in §Appendix A as a fallback) puts the whole CMS into one generation pass — fast but harder to course-correct if something goes wrong.

This sequential plan splits the work into **5 paste-and-review cycles**. Between each:
- You see exactly what Lovable built
- You verify it works before moving on
- If something is wrong, you fix it without losing earlier progress
- You understand the architecture as it grows, instead of decoding a black-box result

Lovable maintains project state between prompts. Prompt 2 EXTENDS what Prompt 1 built — it doesn't replace anything. Your auth, your sidebar, your Supabase connection persist.

**Total estimated time at desk:** 90–150 minutes (5 paste-and-review cycles).

---

## What gets built across the 5 prompts

| # | Prompt | What ships | Lovable gen | Your review |
|---|---|---|---|---|
| 1 | Skeleton + Auth + Layout | App scaffold, Supabase connection, sign-in screen, sidebar nav with Projects + Assets links, role-gated access (admin/creator only — non-admin sees full-page "Access restricted") | ~10 min | ~10 min |
| 2 | Projects List | Read `/projects`, table with Title/Category/Difficulty/Time/Status/Actions, filter buttons (All/Draft/Published), "New Project" button (no destination yet) | ~5 min | ~10 min |
| 3 | Project Form (Create/Edit) | Form with Title/Slug/Summary/Category/Difficulty/Time/Status, slug auto-generation, validation, Save flow, Edit pre-population | ~10 min | ~15 min |
| 4 | Steps section | Embedded in Project Edit — drag-to-reorder, inline edit/add/delete, image asset selector | ~15 min | ~15 min |
| 5 | Assets | Asset grid + Upload button + Supabase Storage integration + delete with inline confirm | ~10 min | ~10 min |
| | **TOTAL** | Complete internal CMS | ~50 min | ~60 min |

---

## Pre-flight checklist — do ONCE before Prompt 1

These must be true before you start. Andy is preparing them in parallel today.

- [ ] **Storage bucket `project-assets` exists** with 4 RLS policies (admin/creator upload, authenticated read, admin update, admin delete). → Silas's migration 0005, paste-ready SQL in `agents/andy/inbox/silas_phase_b_done.md`. Run before Prompt 5 at the latest.
- [ ] **FK ON DELETE clauses live** on `projects.published_by` (SET NULL) and `events.user_id` (CASCADE). → Silas's migration 0004, same paste-ready report. Idempotent no-op if 0003 already applied — safe to run anyway.
- [ ] **Shared types package** `@buildar/core-types` is in place at `D:\BuildAR\packages\core-types\src\`. Already done by Yoni (S1-006). The CMS imports types from here — DO NOT let Lovable define local duplicates.
- [ ] **Env values you'll need handy** when Lovable asks to connect Supabase:
  - `SUPABASE_URL`: `https://xbfgohafudrfygztqmtg.supabase.co`
  - `SUPABASE_ANON_KEY`: get from Supabase Dashboard → Settings → API → `anon` `public` key
  - **NEVER paste the `service_role` key into Lovable.** CMS uses anon + RLS only.
- [ ] **You have at least one user with `role = 'admin'`** in `public.profiles`. Check in Supabase Dashboard → Table Editor → profiles. If not: insert one, or update your own profile row, before Prompt 1.

---

## How to operate between prompts

After each Lovable generation:
1. **Read what Lovable summarizes** at the top of its response — it tells you what it built/changed.
2. **Click through the verification checklist** for that prompt (each section below has one).
3. **If something is wrong:** tell Lovable in plain English ("the sign-in form is missing the toggle to sign-up mode — add it as a link below the Continue button"). Do NOT paste the next prompt until the current one is clean. Lovable's "fix what you just made" loop is reliable.
4. **If something is RIGHT but ugly:** skip it. This is an internal admin tool. Form > beauty.
5. **When clean: paste the next prompt.**

If Lovable starts inventing fields or adding marketing pages: stop it ("don't add a landing page; this app has no public surface — only authenticated users see it"). Lovable's defaults lean consumer-app — keep redirecting it to internal-ops.

---

## Prompt 1 — App Skeleton + Auth + Layout

### What this prompt builds

The foundation. After this prompt completes, you'll have:
- A working Lovable app connected to your live Supabase project
- A sign-in screen (email + password, no social/OAuth)
- After successful sign-in, a layout with a left sidebar (Projects + Assets links, sign-out at bottom, logged-in email shown)
- **Access control:** users WITHOUT `admin` or `creator` role see a full-page "Access restricted" message — they cannot see any of the CMS. Role is checked from `public.profiles.role` (single source of truth used by all other RLS in the system).

The sidebar links won't work yet (no destination screens) — that's intentional. Prompt 2 wires Projects, Prompt 5 wires Assets.

### Why this order

Auth + access control FIRST means every later prompt can assume the user is authenticated and authorized. Lovable won't accidentally generate a public route or leak a form. If you build screens first and try to bolt auth on later, you get inconsistent route guards.

### What you'll verify after Prompt 1

- [ ] Lovable shows you a preview URL — open it
- [ ] You see the sign-in screen at the root
- [ ] Sign in with your admin email/password
- [ ] You land on a page with a sidebar (left, ~220px wide) showing "Projects" and "Assets" links + your email at the bottom + a Sign out link
- [ ] Click Sign out — you return to sign-in screen
- [ ] Sign in again — to test access denial, temporarily change your role in Supabase Dashboard → Table Editor → profiles → set your role to `user`. Refresh the CMS. You should see a full-page "Access restricted. Contact your administrator." message with NO sidebar, NO Projects/Assets links. Set your role back to `admin` afterwards.
- [ ] Open browser DevTools → Network tab during sign-in — confirm calls go to `xbfgohafudrfygztqmtg.supabase.co`, NOT some Lovable-generated test backend.

### Common pitfalls + how to push back

- **Lovable adds a "Sign up" option:** push back. "Remove the sign-up form. Users are seeded by admins; there is no self-serve sign-up." (We'll never give creators a sign-up page — they're invited.)
- **Lovable adds a landing page or marketing copy:** push back. "Remove the landing page. The app should redirect to /sign-in if unauthenticated, and to /projects if authenticated. There is no public-facing content."
- **Lovable uses the `service_role` key:** STOP. Re-check what key you pasted. Service role bypasses RLS — if Lovable uses it, the access denial won't work because RLS won't enforce.
- **Lovable adds social login (Google/GitHub):** push back. "Email and password only. No OAuth providers, no magic links."

### === LOVABLE PROMPT 1 — PASTE THIS ===

This is the first of 5 prompts to build an internal CMS for BuildAR Pro, a mobile DIY guidance app. Only admin and creator role users can access. Build this as a form-centric utilitarian web interface — not a marketing site, not a consumer app. The visual style is clean and operational: sidebar navigation, form-first layouts, no hero sections, no landing pages.

### This first prompt — what to build

1. **Supabase connection.** Use the Supabase project I'll connect. Email + password authentication only. Do NOT add Google, GitHub, magic link, or any other OAuth providers. Do NOT add a self-serve sign-up form — users are seeded by admins directly in the database.

2. **Sign-in screen** at `/sign-in`:
   - Centered card on the page
   - Email input (full width, autofocus, keyboard type email)
   - Password input (with show/hide toggle)
   - "Sign in" button (primary, full-width)
   - On submit: call Supabase `signInWithPassword`. On success, redirect to `/projects`. On failure, show inline error below the form: "Incorrect email or password."
   - No "Forgot password" link, no "Sign up" link, no social buttons.

3. **Access control gate:**
   - When a user authenticates, fetch their profile from the `public.profiles` table: `SELECT role FROM profiles WHERE id = auth.uid()`.
   - If `role` is `admin` or `creator` → grant access to the CMS layout.
   - If `role` is anything else (e.g. `user`) OR the profile lookup fails → show a full-page screen with the message "Access restricted. Contact your administrator." in the center. NO sidebar, NO navigation, NO other UI. The only action available is a Sign out button.
   - Do NOT show a 404. Do NOT use Supabase JWT `user_metadata` for the role check — read from the `profiles` table only. The `profiles.role` column is the single source of truth.

4. **Authenticated layout** (only shown when access is granted):
   - Persistent left sidebar, fixed width 220px, full screen height
   - Sidebar contents (top to bottom):
     - App label at top: "BuildAR Pro CMS" (plain text, small)
     - Navigation links: "Projects" (links to `/projects`) and "Assets" (links to `/assets`)
     - At the bottom: logged-in user's email (small, muted)
     - Below the email: "Sign out" link (small)
   - Main content area fills the remaining width
   - On `/projects` route show a placeholder "Projects list — coming in next prompt"
   - On `/assets` route show a placeholder "Assets — coming in later prompt"
   - Sign out clears the session and redirects to `/sign-in`

5. **Routing:**
   - `/sign-in` — sign-in screen (only accessible if NOT authenticated; if authenticated, redirect to `/projects`)
   - `/projects` — placeholder for now (only accessible if authenticated + admin/creator)
   - `/assets` — placeholder for now (only accessible if authenticated + admin/creator)
   - `/` — redirect to `/projects` (if authenticated) or `/sign-in` (if not)
   - Any other route — 404 (but the access denial takes precedence over 404 for authenticated-but-unauthorized users)

6. **Visual:**
   - Sidebar background: very light grey (#F5F5F0 or similar warm off-white)
   - Main content background: white
   - Text: near-black (#1A1A1A)
   - Primary button color: a saturated orange (#FF6B2B — construction-orange, matching the BuildAR Pro mobile app)
   - Use the system font stack
   - 8px spacing grid (margins/paddings should be multiples of 8)

7. **Do NOT build in this prompt:** the Projects list (next prompt), the project form, the steps section, the Assets manager, any analytics or dashboard.

### === END PROMPT 1 ===

After Lovable finishes generating, run the verification checklist above. Once clean, move to Prompt 2.

---

## Prompt 2 — Projects List Screen

### What this prompt builds

The `/projects` route gets a real table. After this prompt:
- The placeholder is replaced with a project list table showing all rows from the `projects` table
- Columns: Title, Category, Difficulty (numeric), Estimated time, Status badge, Actions (Edit + Delete)
- Filter buttons above the table: All / Draft / Published
- "New Project" button (top right) — this goes to a Create route but the Create form doesn't exist yet (Prompt 3). For now, clicking it can go to a placeholder route.
- Edit button on each row → placeholder route (wired up in Prompt 3)
- Delete button → inline confirmation right inside the table row (NO modal dialog)
- Loading state (3 skeleton rows), empty state ("No projects found"), error state ("Failed to load projects" + retry)

### Why this order

Projects List FIRST means you can see your seed data ("Wall Shelf Install" + "Table Assembly") immediately — proves the Supabase connection is reading the right tables. Form work is more error-prone, so we validate the read path first.

### What you'll verify after Prompt 2

- [ ] Sign in, land on `/projects` — see a table with 2 rows (the seeded projects)
- [ ] Difficulty shows as a number (1–5)
- [ ] Status badge shows "Draft" (grey) or "Published" (green) — both seed projects are Published
- [ ] Click "All" / "Draft" / "Published" filter buttons — table filters in place, no page reload
- [ ] Filter to "Draft" — table should be empty with "No projects found" message
- [ ] Filter back to "All"
- [ ] Click Delete on a row (don't actually delete!) — confirmation appears inline in the row ("Delete? Yes / Cancel"), NOT a modal popup. Click Cancel.
- [ ] DevTools Network tab: confirm GET to `xbfgohafudrfygztqmtg.supabase.co/rest/v1/projects` returns 200
- [ ] Open Supabase Dashboard → Logs — confirm the SELECT is happening as the authenticated user (RLS-respecting)

### Common pitfalls + how to push back

- **Lovable adds a search bar:** push back. "Remove search. There are 2 seed projects in Phase 0–1. Pagination, search, infinite scroll — none of these belong yet."
- **Lovable uses stars for difficulty:** push back. "Difficulty is a plain number 1–5. Not stars, not icons. Stars in this context are generic and don't read as 'tool difficulty'."
- **Delete is a modal:** push back. "Delete confirmation must be inline in the row — replace the Edit/Delete icons with 'Delete?' text + 'Yes, delete' / 'Cancel' buttons. Modals interrupt; this is a high-frequency admin action."
- **Lovable adds pagination:** push back. "No pagination. Show all rows in one table. We'll never have more than ~50 projects in this admin tool."

### === LOVABLE PROMPT 2 — PASTE THIS ===

This is the second of 5 prompts. The app skeleton, auth, and access control are already in place from Prompt 1. Extend the `/projects` route — replace the placeholder with a real Projects List table.

### What to build

1. **Projects List table** at `/projects` (extend, don't replace, the existing route):
   - Fetch all rows from the Supabase `projects` table using the authenticated client (respects RLS). Import the `Project` type from `@buildar/core-types` — do not define a local type.
   - Show a table with these columns in this order: Title, Category, Difficulty, Estimated minutes, Status, Actions.
   - Status column: render a badge — "Draft" with muted/grey style, "Published" with green style.
   - Actions column: two icon buttons per row — Edit (pencil icon) and Delete (trash icon).

2. **Filter buttons** above the table:
   - Three buttons in a row, left-aligned: "All", "Draft", "Published".
   - Active filter has a distinct style (filled background); inactive is outline.
   - Clicking a filter updates the table in place, no page reload.
   - Default to "All" on load.

3. **"New Project" button** (top right of the page, above the filter row):
   - Primary style (orange #FF6B2B background, white text).
   - Clicking it navigates to `/projects/new`. That route doesn't have a real form yet (next prompt) — for now just show "Create form — coming in next prompt" on that page.

4. **Edit action:** clicking the Edit icon on a row navigates to `/projects/:id/edit`. That route also shows a placeholder for now.

5. **Delete action — INLINE confirmation:**
   - Clicking the Delete icon replaces the Edit/Delete icons in that row's Actions cell with two text buttons: "Delete?" (as a label) + "Yes, delete" (red text) + "Cancel" (muted text). NO MODAL DIALOG.
   - Clicking "Yes, delete" sends a DELETE to Supabase for that row. On success, the row vanishes from the table. On failure, restore the Edit/Delete icons and show an inline error message above the table: "Couldn't delete project. Try again."
   - Clicking "Cancel" reverts the row to the normal Edit/Delete icons.

6. **States:**
   - Loading: full-width skeleton table with 3 placeholder rows (grey shimmer rectangles in each cell) while the SELECT is in flight.
   - Empty (no rows matching current filter): centered in the table body: "No projects found." If the filter is "All", also show a link below: "Create your first project" linking to `/projects/new`.
   - Error: inline error banner above the table — "Failed to load projects. Try again." with a "Retry" button that re-runs the fetch.

7. **Do NOT build in this prompt:**
   - The actual create/edit form (next prompt)
   - The Steps section (later prompt)
   - Pagination, search, infinite scroll, sort controls
   - Stars or any non-numeric difficulty display

### === END PROMPT 2 ===

Verify, then move to Prompt 3.

---

## Prompt 3 — Project Create / Edit Form

### What this prompt builds

The `/projects/new` and `/projects/:id/edit` routes both render a real form. After this prompt:
- Both routes use the same form component (Edit pre-populates from the existing project)
- 7 form fields with proper validation (Title, Slug, Summary, Category, Difficulty, Estimated minutes, Status)
- Slug auto-generates from Title (but user can override)
- Inline validation errors below the failed field (no toast, no top-of-form summary)
- Save flow with loading state
- Steps section is NOT built yet — that's Prompt 4

### Why this order

Forms are where Lovable can most easily go off-script. By isolating the form prompt, you can iterate on it without touching the table or the steps section. Validation and slug auto-gen are subtle — easier to nail when you can review the form in isolation.

### What you'll verify after Prompt 3

- [ ] On Projects List, click "New Project" — `/projects/new` shows an empty form
- [ ] Form has 7 fields in this order: Title, Slug, Summary (with character count), Category, Difficulty, Estimated minutes, Status (dropdown default "Draft")
- [ ] Type a Title — the Slug field updates in real time (lowercase, hyphens for spaces, alphanumeric only)
- [ ] Manually edit the Slug — typing more in Title no longer overrides your slug (auto-gen stops after manual edit)
- [ ] Click Save with empty Title — inline error below Title field: "Title is required"
- [ ] Click Save with Title only — multiple inline errors appear (one per failed field)
- [ ] Fill all fields correctly, click Save — button shows spinner, redirects to `/projects` on success, success toast appears at bottom: "Project saved."
- [ ] Refresh `/projects` — new project visible in the table
- [ ] Click Edit on that project — `/projects/:id/edit` opens with all 7 fields pre-populated
- [ ] Change the Title and Save — toast confirms, table reflects the new title

### Common pitfalls + how to push back

- **Slug auto-gen doesn't stop when user edits manually:** push back. "If the user edits the Slug field directly, stop auto-generating from Title for the rest of the session. They've taken ownership."
- **Validation shows as a toast or a banner at the top:** push back. "Validation errors must appear inline directly below the failed field — no toasts, no top-of-form summaries. Users need to see what to fix in context."
- **Save button is disabled until form is touched:** push back. "Don't disable Save based on touched state. Validate on Save click and show errors then. Pre-emptive disabling confuses users."
- **Lovable adds a 'Required' badge next to every field label:** annoying but harmless. Skip unless you care.
- **Difficulty is a slider:** acceptable; brief says number input OR segmented control 1-2-3-4-5 OR slider. Pick one.

### === LOVABLE PROMPT 3 — PASTE THIS ===

This is the third of 5 prompts. App skeleton, auth, and Projects List are already built. Now build the Project Create/Edit form.

### What to build

1. **Replace the placeholder** at `/projects/new` and `/projects/:id/edit` with a real form. Both routes render the SAME form component. On the Edit route, fetch the project by ID and pre-populate all fields. On Create, fields are empty.

2. **Form fields (in this order):**

   | # | Field | Input type | Validation |
   |---|---|---|---|
   | 1 | Title | Text input | Required, max 120 characters |
   | 2 | Slug | Text input | Required, lowercase letters/numbers/hyphens only, auto-generated from Title (user can override) |
   | 3 | Summary | Textarea (~4 rows tall) | Required, max 500 characters. Show character count "X / 500" below the field, updating live as the user types. |
   | 4 | Category | Text input | Required |
   | 5 | Difficulty | Number input 1–5 (or segmented control showing "1 2 3 4 5") | Required, integer 1–5 |
   | 6 | Estimated minutes | Number input | Required, positive integer |
   | 7 | Status | Select dropdown with options "Draft" and "Published" | Required, defaults to "Draft" on Create. On Edit, pre-populate from existing value. |

3. **Slug auto-generation behavior:**
   - As the user types in Title, populate Slug field by: lowercase + replace spaces with hyphens + strip non-alphanumeric characters.
   - If the user manually edits the Slug field (any keystroke directly in Slug), STOP auto-generating from Title for the rest of the session. The user has taken ownership.
   - On Edit route load: do NOT auto-regenerate the slug from the loaded Title — the slug came from the DB and is the user's chosen value.

4. **Validation behavior:**
   - Validate ALL fields on Save click, before submitting.
   - For each failed field, show an inline error message in red text directly BELOW that field — NOT a toast, NOT a summary banner at the top of the form.
   - Do NOT disable the Save button while the form is untouched. Only show errors after a save attempt.

5. **Save flow:**
   - Save button (primary style, right-aligned in the form footer)
   - Cancel link (left-aligned, navigates back to `/projects`)
   - On Save click (after validation passes): replace Save button label with a spinner, disable the button. Send INSERT (Create) or UPDATE (Edit) to Supabase `projects` table using the authenticated client.
   - On success: navigate to `/projects` and show a brief toast at the bottom of the screen: "Project saved." (auto-dismiss after 3 seconds)
   - On error: restore the Save button, show an inline error message above the Save button — "Save failed. Check your connection and try again."

6. **Loading state on Edit load:**
   - While fetching the project to pre-populate, show skeleton placeholders in each field (or just show a centered spinner with "Loading project…" — either is fine).
   - If the project ID doesn't exist (404 from Supabase): redirect to `/projects` and show a toast "Project not found."

7. **Do NOT build in this prompt:**
   - The Steps section (next prompt — that lives BELOW the form fields on the Edit route only)
   - Image upload for the project (not in the data model)
   - Any field beyond the 7 listed above (e.g. tags, description rich text, publish-date scheduler)

### === END PROMPT 3 ===

Verify, then move to Prompt 4.

---

## Prompt 4 — Steps Section (embedded in Project Edit)

### What this prompt builds

The Project Edit route gets a new section BELOW the form fields: a reorderable Steps list for that project. After this prompt:
- "Steps" heading + reorderable list, one row per step
- Each row: drag handle, order number, step title, Edit + Delete icons
- Drag-and-drop reorder (saves to DB immediately on drop)
- Edit a step: expands the row inline with Title + Description fields + image asset selector + Save/Cancel
- Add step: "Add Step" button at the bottom appends a blank row in edit mode
- Delete step: inline confirmation (same pattern as project delete)

This is the trickiest prompt because drag-and-drop in Lovable can have issues. Plan for 1-2 iterations.

### Why this order

Steps depend on the project existing — so they can only show on Edit, not Create. The form had to be built first. Steps also touch a different table (`project_steps`) with its own RLS, so it's a logically separate concern.

### What you'll verify after Prompt 4

- [ ] Open an existing project for Edit — below the form fields you see a "Steps" section with 6 (or 7) rows for that project's seeded steps
- [ ] Step rows are ordered correctly (step_index ascending)
- [ ] Drag a step from position 3 to position 1 — the order updates visually AND saves to the DB. Refresh the page — order persists.
- [ ] Click Edit (pencil) on a step — the row expands inline showing Title field, Description textarea, image selector ("No image attached" or asset picker), Save and Cancel buttons. Other rows are NOT affected.
- [ ] Change the Title, click Save — the row collapses back to display mode showing the new title.
- [ ] Click Delete on a step — inline confirmation appears in the row ("Delete? Yes / Cancel"). Click Cancel.
- [ ] Click "Add Step" at the bottom — a new blank step row appears at the end, in expanded edit mode, ready to fill in.
- [ ] Fill in the new step title + description, click Save — appears in the list at the bottom.
- [ ] Drag the new step to position 2 — order updates and saves.

### Common pitfalls + how to push back

- **Drag-and-drop doesn't work:** Lovable may use a library that fails. Tell Lovable: "Use react-beautiful-dnd or @dnd-kit/sortable for the drag-and-drop. Make sure each row has a unique key and the drag handle is on the left."
- **Reorder doesn't save to DB:** push back. "On drag end, immediately PATCH the affected step rows' `step_index` values to Supabase. Use optimistic UI — update the local list first, then send the update. If the update fails, restore the previous order and show an inline error."
- **Edit form opens in a modal:** push back. "Step editing must be INLINE — the row expands in place. Modals break flow when editing multiple steps in a row."
- **Lovable adds rich text editor for description:** push back. "Description is a plain textarea. No markdown, no WYSIWYG. We want simplicity over features."
- **Lovable creates a new `assets` lookup for the image selector and it doesn't show your real assets:** that's expected — Assets aren't built until Prompt 5. For now Lovable can show "Asset picker — assets will be available after the Assets screen is built" or a disabled selector. Don't sweat it; we wire it together later.

### === LOVABLE PROMPT 4 — PASTE THIS ===

This is the fourth of 5 prompts. The Project Edit form exists from Prompt 3. Now ADD a "Steps" section below the form fields on the Edit route ONLY (NOT on the Create route — steps require a saved project).

### What to build

1. **Add a "Steps" section** at the bottom of the `/projects/:id/edit` page, below the form fields and below the form's Save/Cancel buttons. Use a clear visual separator (horizontal line + section heading "Steps").

2. **Fetch step data:** query the Supabase `project_steps` table where `project_id = :id`, ordered by `step_index` ascending. Use the `Step` (or `ProjectStep`) type from `@buildar/core-types` — do NOT define a local type.

3. **Step list rows.** Each row shows (left to right):
   - Drag handle (e.g. a "≡" icon or 6-dot grid icon) — this is the only drag target
   - Order number badge (1, 2, 3, … — derived from position in the list)
   - Step title
   - Edit icon (pencil)
   - Delete icon (trash)

4. **Drag-to-reorder:**
   - User drags the drag handle to move the row up or down.
   - On drop, immediately update the local order visually AND send a PATCH to Supabase that updates the `step_index` value on the affected rows.
   - Show a brief "Saving..." inline indicator next to the Steps section heading while the request is in flight.
   - On error: restore the previous order and show an inline error message above the Steps section — "Couldn't save new order. Try again."
   - Use a robust drag library: `react-beautiful-dnd` or `@dnd-kit/sortable`.

5. **Edit step (inline):**
   - Clicking the Edit icon expands the row INLINE (not a modal). Other rows are unaffected.
   - Expanded row shows: Title input (required), Description textarea (required, ~3 rows tall), an image asset selector (see point 7), Save button (primary), Cancel link.
   - On Save: PATCH the step in Supabase. On success, collapse the row back to display mode showing the new title.
   - On Cancel: collapse the row, discard unsaved changes.
   - Validate: Title required, Description required. Errors inline below the failing field.

6. **Delete step (inline confirmation, NO modal):**
   - Click Delete icon → replace the Edit/Delete icons with "Delete?" + "Yes, delete" + "Cancel" text buttons in the row.
   - "Yes, delete" sends DELETE to Supabase. On success, the row vanishes and remaining rows renumber. On failure, restore icons and show inline error.
   - "Cancel" reverts.

7. **Image asset selector** (inside the Edit step row):
   - Shows the currently attached image asset (filename + small thumbnail) if one exists.
   - Shows "No image attached" if none.
   - A "Change image" button opens a dropdown or popover listing all available assets from the `assets` table (you'll wire this in Prompt 5 — for now, the list may be empty or show a placeholder "Upload assets in the Assets section first").
   - Selecting an asset attaches it to the step via the step's foreign key.

8. **"Add Step" button** at the bottom of the list:
   - Primary style or outline style (your choice).
   - Clicking it appends a new step row to the list, already in expanded edit mode, with empty Title and Description fields.
   - The new step's `step_index` is set to (current max + 1) so it appears at the bottom.
   - On Save, the step is INSERTed into Supabase.

9. **States:**
   - Loading: skeleton step rows while fetching.
   - Empty (no steps yet): show "No steps yet. Add your first step." with an "Add Step" link/button.

10. **Do NOT build in this prompt:**
    - A separate route for step editing (must stay inline)
    - A modal dialog for any step action (inline only)
    - A rich text editor for step description (plain textarea only)
    - Step-level access control distinct from project-level (RLS handles it)

### === END PROMPT 4 ===

Verify, then move to Prompt 5.

---

## Prompt 5 — Assets Screen

### What this prompt builds

The `/assets` route gets a real grid + upload. After this prompt:
- Grid of all uploaded image assets
- Each tile shows thumbnail + filename
- "Upload Image" button opens browser file picker
- Selected file uploads to Supabase Storage bucket `project-assets`
- Delete asset with inline confirmation (same pattern as everywhere else)
- After this, the Step image asset selector in Prompt 4 will start showing real assets

### Why this order

Assets last because (a) the storage bucket must exist (pre-flight requirement); (b) steps need to be built before image-asset linkage matters; (c) it's the simplest screen so it's a low-risk finisher.

### What you'll verify after Prompt 5

- [ ] `/assets` shows an empty grid + "Upload Image" button
- [ ] Click Upload, pick a small JPEG from your computer — upload progress shows in a new tile, then the tile shows the thumbnail + filename
- [ ] Open Supabase Dashboard → Storage → `project-assets` bucket — your file is there
- [ ] Open Supabase Dashboard → Table Editor → `assets` table — a row exists with filename + storage path
- [ ] Refresh `/assets` — the asset is still there (loaded from DB)
- [ ] Hover the tile — delete icon appears top-right
- [ ] Click Delete — inline "Delete? Yes / No" appears on the tile
- [ ] Cancel, then re-click Delete, then "Yes" — tile vanishes from grid, file is removed from Supabase Storage and the `assets` row is deleted
- [ ] Try uploading a 15MB PDF — error message: "Upload failed. Only JPEG, PNG, and WebP files are supported. Max file size: 10MB."
- [ ] Go back to a project's Edit page, expand a step's Edit row, click "Change image" — your uploaded assets now appear in the selector. Pick one, save. Refresh. The step retains the asset link.

### Common pitfalls + how to push back

- **Lovable uses a drag-and-drop upload zone:** push back. "File picker only. No drag-to-upload zone. Click button → native picker → upload immediately."
- **Lovable creates a separate Storage table not in our schema:** push back. "Use the existing `assets` table. Each row should have: id, filename, storage_path, url, created_at. Don't add columns I haven't approved."
- **Uploads fail with a CORS or RLS error:** check the storage bucket has the 4 RLS policies from migration 0005. The INSERT policy uses `is_creator_or_admin()` — confirm your user has role `admin` or `creator` in `profiles`.
- **Lovable wants to add image cropping/editing:** push back. "No editing, no cropping. Upload as-is. Display as-is. We're an admin tool."
- **Lovable adds a public URL gallery:** push back. "Bucket is private. URLs are signed. No public sharing UI."

### === LOVABLE PROMPT 5 — PASTE THIS ===

This is the fifth and final prompt. The CMS is mostly complete: auth + layout + Projects + Steps. Now build the Assets screen at `/assets`.

### What to build

1. **Replace the `/assets` placeholder** with a real screen.

2. **Asset grid:**
   - Layout: responsive grid of tiles. ~4 tiles per row on desktop (auto-fit to width).
   - Each tile shows:
     - Thumbnail preview: fill the tile with the image (object-fit: cover, ~150x150px or similar square).
     - Filename below the thumbnail (small text, truncate with ellipsis if long).
     - Delete icon in the top-right corner of the tile, visible only on hover.
   - Fetch all rows from the `assets` table using the authenticated client. Import the `Asset` type from `@buildar/core-types` — do not define a local type.

3. **"Upload Image" button** (top-right of the page, above the grid):
   - Primary style (orange background).
   - Clicking it opens the browser's native file picker, configured to accept: `image/jpeg`, `image/png`, `image/webp`.
   - After file is selected, upload immediately (no separate "Confirm" step).
   - During upload: insert a placeholder tile into the grid showing an upload progress indicator. When upload completes, replace placeholder with the real tile (thumbnail + filename).

4. **Upload flow (Supabase Storage):**
   - Upload the file to the Supabase Storage bucket named `project-assets` (pre-existing — created by migration 0005).
   - Path convention: `project-assets/{generated_uuid}_{original_filename}` (use a UUID prefix to avoid name collisions).
   - After successful upload, INSERT a row into the `assets` table with: `filename` (original filename), `storage_path` (the path you uploaded to), `url` (Supabase Storage's public/signed URL for that file).
   - Use `id` as a UUID PK (Supabase default).
   - Bucket access is private — use signed URLs (1 hour expiry) for display in the grid.

5. **Delete asset (inline confirmation, NO modal):**
   - Click Delete icon → replace the icon with "Delete? Yes / No" text buttons directly on the tile (overlay or replace the filename area).
   - "Yes" → delete the file from Supabase Storage AND delete the row from the `assets` table. On success, tile vanishes from grid. On failure, restore icon and show inline error above the grid: "Couldn't delete asset. Try again."
   - "No" → revert tile to normal display.

6. **States:**
   - Loading: grid of grey skeleton tiles (matching tile dimensions) while the asset list fetches.
   - Empty (no assets): centered message — "No assets yet. Upload your first image."
   - Upload error: above the grid, error message — "Upload failed. Only JPEG, PNG, and WebP files are supported. Max file size: 10MB."
   - Load error: above the grid, error message + retry button — "Couldn't load assets. Try again."

7. **File validation BEFORE upload:**
   - Reject files with MIME types other than image/jpeg, image/png, image/webp. Show the error message above the grid.
   - Reject files larger than 10MB. Show the error message above the grid.

8. **Connect to the Step image selector:**
   - In Prompt 4 you built a "Change image" selector inside step edit rows. Now that assets exist, that selector should populate with the list of assets from this screen.
   - Selecting an asset for a step writes the asset's URL or storage_path into the step's relevant column (in our schema, this would be a column on `project_steps` — check the `core-types` Step interface for the exact field name).

9. **Do NOT build in this prompt:**
   - A drag-and-drop upload zone (file picker only)
   - Image cropping, editing, or resizing
   - A public gallery, sharing UI, or download buttons
   - Folder/album organization
   - Search or filtering of assets (we have few enough to scroll)

### === END PROMPT 5 ===

After Prompt 5 + verification, the CMS is functionally complete.

---

## Final steps — after all 5 prompts

### 1. Sanity test the full flow

- Sign in as admin
- Create a new project via the form
- Add 3 steps to it
- Upload an image asset
- Edit one of the steps to attach the image
- Reorder the steps via drag
- Delete a step (use inline confirm)
- Mark the project Published via the Status dropdown
- Sign out
- Try to sign in with a non-admin user (or downgrade your role temporarily) → see access denied screen

If all of the above works: the CMS is done.

### 2. Pull the code into the monorepo

Lovable has two options:
- **Option A (recommended):** Lovable → Settings → "Push to GitHub" → connect to `InonB2/buildar-pro` → push to a new branch `feat/cms-v0-lovable`. This auto-creates a PR.
- **Option B:** Lovable → Export → ZIP. Extract into `D:\BuildAR\apps\web\`. Commit to a feature branch yourself.

Either way, the destination inside the monorepo is `D:\BuildAR\apps\web\`. The workspace is already reserved in `pnpm-workspace.yaml`.

### 3. Verify CI

Once the PR is open, the 5-job CI workflow (lint, typecheck, test, migration-validate) runs automatically on push. If lint or typecheck fails, ping Andy via Telegram and we'll dispatch Dev or Yoni to clean up.

### 4. Tell Andy "Lovable CMS PR open"

Andy queues Vera (UI/UX/a11y review) + Jasmin (access control + RLS pass-through security review). When both PASS, merge to main. **That closes Gate C.**

---

## Appendix A — Single-prompt fallback (if Lovable handles it well)

If you'd rather try the all-in-one approach (faster but harder to course-correct), the original single-prompt version lives at `owner_inbox/buildar/lovable_handoff_ready.md` (same directory). Same content, different packaging.

Use sequential if: you want to verify each step or you've seen Lovable get confused on complex prompts.
Use single-prompt if: you trust Lovable to handle 5 features at once and want to ship fast.

---

## Appendix B — If you hit a blocker

Send a Telegram to Andy with the screenshot and `BLOCKER: Lovable CMS [step X]`. Andy will dispatch Yoni (for code-level help) or me (for prompt refinement) and reply with next steps within minutes.

Common blockers and quick fixes:
- **Lovable can't connect to Supabase:** double-check the URL and ANON key (NOT service_role). Make sure you didn't accidentally paste a stale key.
- **Access control isn't working:** verify your user has `role = 'admin'` in `public.profiles`. Lovable reads from `profiles.role`, not from JWT `user_metadata`.
- **Upload fails with permission denied:** confirm migration 0005 is applied (4 RLS policies on `storage.objects` for the `project-assets` bucket). The INSERT policy requires `is_creator_or_admin()` — confirm the helper function exists in 0001.
- **Drag-to-reorder doesn't save:** check the Network tab during a drag — confirm the PATCH calls are firing and returning 200. If 403, it's an RLS issue on `project_steps`.
