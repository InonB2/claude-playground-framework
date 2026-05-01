# LlamaParse Integration Plan — BuildARPro

**Author:** Mack (Automation Engineer)
**Date:** 2026-05-01
**Project:** pro-maker-ar (React + Vite + Supabase)

---

## 1. Current Codebase Overview

### Stack
- **Frontend:** React 18 + Vite + TypeScript + shadcn/ui + Tailwind CSS
- **Routing:** react-router-dom v6 (single route: `/` → `Index` page)
- **Backend:** Supabase (auth, database, edge functions)
- **Existing edge function:** `supabase/functions/validate-assembly-progress/` — calls Google Cloud Vision API to validate assembly photos

### Existing Supabase Tables
| Table | Key columns |
|---|---|
| `items` | id, name, description, manual_link, total_steps |
| `steps` | id, item_id, step_number, model_reference, state_metadata (JSONB) |
| `profiles` | id, email, username |
| `user_progress` | id, user_id, item_id, current_step, completed |

The `steps.state_metadata` JSONB column is exactly where parsed AR instruction data should live.

---

## 2. Where the Upload UI Should Go

**Recommended location:** New page at `/upload` with a matching component `src/pages/UploadManual.tsx`.

Rationale:
- The landing page (`Index.tsx`) is marketing-only. Upload is a logged-in power-user workflow.
- Add a protected route so only authenticated users can access it.
- Entry point: add a "Upload Manual" button in `Navbar.tsx` (visible after login).

**Component breakdown:**
```
src/pages/UploadManual.tsx          ← page shell + layout
src/components/ManualUploader.tsx   ← file input, drag-drop, progress, result preview
src/components/ARStepPreview.tsx    ← displays parsed steps before saving to DB
```

The upload flow inside `ManualUploader.tsx`:
1. User selects a PDF/image file via `<input type="file">` or drag-drop.
2. User fills in the item name and description.
3. On submit → POST to a **Supabase Edge Function** (`parse-manual`) which calls LlamaParse.
4. Edge function returns structured AR steps JSON.
5. Frontend displays a preview of extracted steps (`ARStepPreview`).
6. User confirms → steps are written to Supabase `items` + `steps` tables.

---

## 3. LlamaParse API Call — How It Works

### Authentication
All calls use an `Authorization: Bearer {LLAMAPARSE_API_KEY}` header.

SECURITY FLAG — The API key MUST live in the edge function environment, never in the browser. Do NOT use a `VITE_` prefix for this key. Using `VITE_LLAMAPARSE_API_KEY` would embed the secret into the compiled JavaScript bundle, exposing it to any user who opens DevTools.

### Step 1 — Upload the document
```
POST https://api.cloud.llamaindex.ai/api/parsing/upload
Headers:
  Authorization: Bearer {api_key}
Body: multipart/form-data
  file: <the PDF or image file>
  parsing_instruction: "Extract step-by-step assembly instructions. For each step, identify: step number, action description, part name or part number, and any warnings or safety notes."
```

Response:
```json
{
  "id": "job-uuid-here",
  "status": "PENDING"
}
```

### Step 2 — Poll for job completion
```
GET https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/json
Headers:
  Authorization: Bearer {api_key}
```

Poll every 2–3 seconds until `status` is `SUCCESS`.

### Step 3 — Result structure (JSON mode)
LlamaParse returns a structured JSON with pages and content blocks:
```json
{
  "pages": [
    {
      "page": 1,
      "text": "Step 1: Insert bolt A into slot B...",
      "items": [
        {
          "type": "text",
          "value": "Step 1: Insert bolt A into slot B. Warning: Do not overtighten."
        },
        {
          "type": "table",
          "rows": [
            ["Part", "Quantity"],
            ["Bolt A", "4"]
          ]
        }
      ]
    }
  ]
}
```

---

## 4. Transforming LlamaParse Output → AR Instruction Steps

The transformer function lives at `src/lib/llamaparse.js` (the stub, called server-side).

**Target AR step schema:**
```json
{
  "step_number": 1,
  "action": "Insert bolt A into slot B",
  "part_name": "Bolt A",
  "part_quantity": 4,
  "warning": "Do not overtighten",
  "model_reference": "bolt_a_slot_b"
}
```

**Transformation logic** (to be implemented in the edge function after LlamaParse returns):

1. Iterate through `pages[].items` where `type === "text"`.
2. Use a regex or LLM micro-prompt to extract step number, action, part, and warning from each text block.
3. Cross-reference tables for part quantities.
4. Assign sequential `step_number` values if the manual doesn't number them explicitly.
5. Generate a `model_reference` slug (e.g., `step-1-bolt-a`) for AR model lookup.

Suggested utility: `src/lib/transformSteps.js` — pure function, testable independently.

---

## 5. Supabase Storage Schema

### New table: `parsed_manuals`
Stores the raw LlamaParse job output alongside the item it belongs to.

```sql
CREATE TABLE parsed_manuals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID REFERENCES items(id) ON DELETE CASCADE,
  job_id TEXT NOT NULL,                  -- LlamaParse job UUID
  status TEXT NOT NULL DEFAULT 'pending', -- pending | processing | complete | failed
  raw_output JSONB,                      -- full LlamaParse JSON response
  parsed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### Updated `steps` table — add columns
The existing `steps.state_metadata` JSONB is a good fit. Populate it with:
```json
{
  "action": "Insert bolt A into slot B",
  "part_name": "Bolt A",
  "part_quantity": 4,
  "warning": "Do not overtighten",
  "source": "llamaparse"
}
```

No schema change required for `steps` — `state_metadata` is already JSONB and flexible.

---

## 6. Supabase Edge Function: `parse-manual`

Create `supabase/functions/parse-manual/index.ts`.

This function:
1. Receives `{ file_base64, file_name, item_name, description }` from the frontend.
2. Converts base64 to a Blob, uploads to LlamaParse.
3. Polls until complete.
4. Transforms result into AR steps.
5. Inserts a new `items` record + all `steps` records.
6. Returns the `item_id` and steps array to the frontend.

Environment secret to set in Supabase dashboard:
```
LLAMAPARSE_API_KEY = llx-your-key-here
```

Set via: `supabase secrets set LLAMAPARSE_API_KEY=llx-your-key-here`

---

## 7. Security Review

| Risk | Status | Mitigation |
|---|---|---|
| API key in browser bundle | BLOCKED | Key is NEVER prefixed with `VITE_`. Only accessible in edge function via `Deno.env.get('LLAMAPARSE_API_KEY')`. |
| API key in `.env.example` | SAFE | `.env.example` contains only a placeholder value (`llx-your-key-here`), not the real key. Real key goes in Supabase secrets. |
| File upload abuse | MEDIUM | Validate file type (PDF/image only) and size (<20MB) in the edge function before forwarding to LlamaParse. |
| Unauthenticated access | MEDIUM | Edge function must verify JWT (`verify_jwt = true` in config.toml). Frontend upload page behind auth guard. |
| LlamaParse polling timeout | LOW | Implement a max-retry (e.g., 30 attempts × 3s = 90s timeout) with graceful error response. |
| Raw output stored in DB | LOW | `parsed_manuals.raw_output` may contain PII from document. Add a note to the privacy policy. |

---

## 8. Implementation Order

1. Create `supabase/functions/parse-manual/index.ts` (edge function)
2. Set `LLAMAPARSE_API_KEY` secret in Supabase dashboard
3. Add `parse-manual` config block to `supabase/config.toml`
4. Create `src/lib/llamaparse.js` stub (this session — TASK 3)
5. Create `src/lib/transformSteps.js` transformer utility
6. Create `src/pages/UploadManual.tsx` + `src/components/ManualUploader.tsx`
7. Add `/upload` route in `App.tsx` with auth guard
8. Add "Upload Manual" nav link in `Navbar.tsx`
9. Run migration to create `parsed_manuals` table
10. Integration test end-to-end with a sample IKEA PDF

---

## Files Created This Session

- `pro-maker-ar/.env.example` — env template with LLAMAPARSE_API_KEY placeholder
- `pro-maker-ar/src/lib/llamaparse.js` — API stub (server-side only)
