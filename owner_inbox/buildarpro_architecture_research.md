# BuildARPro — Architecture Research Report

**Prepared by:** Tomy (Research Agent)
**Date:** 2026-05-02
**Audience:** Product Manager / Founder
**Purpose:** Deep-dive on both pipelines — content creation and end-user runtime — with pricing, schema, and MVP stack recommendations.

---

## Executive Summary

BuildARPro sits at the intersection of two mature but separate technology stacks: document intelligence (LlamaParse/LlamaExtract) and industrial AR (Vuforia). Both stacks are production-ready in 2025. The challenge: there is no off-the-shelf bridge between them — you will need to build a custom pipeline that converts parsed PDF steps into Unity scene content. Vuforia remains the correct choice for industrial tool recognition, and the Supabase + Stripe combination is proven for this type of SaaS. A web-based shortcut (AR.js) exists for a fast investor demo, but cannot replace Vuforia for production quality.

---

## ARROW 1 — Content Creation Pipeline

```
PDF MANUAL
    |
    v
[LlamaParse API]
    |  parses: text, headings, numbered lists, tables, images
    |  output: Markdown (default) or structured JSON items per page
    v
[LlamaExtract API]  <-- you define the schema
    |  you specify: step_number, action_text, component_name, diagram_ref
    |  output: clean validated JSON array of steps
    v
[Custom Transform Layer]  <-- this is your build work
    |  maps each step to a Unity-compatible data structure
    |  references 3D model annotations by step index
    v
[Unity + Vuforia AR Scene]
    |  each step = one AR "state" in the scene
    |  state contains: 3D label text, highlighted model part, arrow/pointer
    v
AR GUIDE READY FOR DEPLOYMENT
```

### Q1 — What does LlamaParse return?

LlamaParse v2 API returns output in multiple formats:

- **`markdown`** — Full document as Markdown, preserving headings, numbered lists, bullet points, tables. Natural output for a PDF instruction manual — Step 1, Step 2, etc. come out as a numbered Markdown list.
- **`items`** — Structured JSON objects per page: each paragraph, heading, and table is a separate JSON item with type tags.

**Critical:** LlamaParse's built-in "structured output" feature is deprecated. The correct tool for extracting step-by-step data into clean JSON is now **LlamaExtract** (separate product in the LlamaIndex ecosystem). LlamaExtract runs LlamaParse in the background, then applies a schema you define.

**Practical output with LlamaExtract (schema you define):**

```json
[
  { "step_number": 1, "action": "Lay all parts flat on a clean surface", "component": null, "note": "Check bag for 12 screws" },
  { "step_number": 2, "action": "Align panel A with bracket B", "component": "Panel A, Bracket B", "note": null },
  { "step_number": 3, "action": "Insert bolt A into slot B", "component": "Bolt A, Slot B", "note": "Do not overtighten" }
]
```

### Q2 — How do you get from JSON steps to a Vuforia AR guide?

There is **no off-the-shelf bridge**. You build it in Unity:

1. Backend stores JSON step array in Supabase.
2. Unity app fetches steps for the active guide from your API.
3. Unity renders each step as an AR "state" — text label, arrow GameObject, optionally highlighted 3D mesh.
4. User taps "Next" to advance through states.

No standard "AR guide" file format exists. The guide lives inside a Unity scene.

### Q3 — What converts "Insert bolt A into slot B" into a 3D annotation?

No automatic AI tool does this in 2025. The conversion is human-assisted:

- A developer maps each step's component references to specific parts of a 3D model.
- **Vuforia Studio** (PTC's authoring tool, separate from core SDK) provides drag-and-drop interface to attach 3D Labels, arrows, animations to model parts — no code needed for basic steps. Fastest content creation path.
- Fully automated annotation (LLM maps text → 3D part) = custom ML, does not exist out of the box.

**Blocker:** If the tool has no 3D model (CAD file), you cannot do part-level highlighting. Image Targets work without a 3D model but only overlay content anchored to the image plane.

### Q4 — What does a Vuforia AR overlay consist of technically?

A Unity scene hierarchy parented to a tracked target:
- `ARCamera` GameObject (processes camera feed)
- `ImageTarget` or `ModelTarget` GameObject (the anchor)
- **Child GameObjects**: 3D Labels (TextMeshPro), 3D Models (GLTF/FBX), arrows/highlights, videos (VideoPlayer), 2D UI (world-space Canvas)

When tracking is lost, child GameObjects hide. When target is found, they reappear in correct position. App compiles to native iOS/Android binary.

---

## ARROW 2 — End-User Runtime Pipeline

```
USER OPENS APP
    |
    v
[ARCamera activates]
    |  Vuforia SDK initializes with license key
    |  loads Image Target or Model Target database (local or cloud)
    v
[Camera feed processed in real-time]
    |  Vuforia extracts natural feature points from live video
    |  compares against registered target feature signatures
    v
[TARGET MATCHED]
    |  SDK fires: ObserverBehaviour.OnTargetStatusChanged callback
    |  status: TRACKED | EXTENDED_TRACKED | LIMITED
    v
[Target metadata retrieved]
    |  metadata field contains: guide_id (e.g., "dewalt_drill_v2")
    |  app queries Supabase: GET /guides/{guide_id}
    v
[Guide content loaded]
    |  step JSON downloaded and parsed
    |  Unity scene activates child GameObjects for Step 1
    v
[AR GUIDE PLAYS]
    |  user taps Next → advances step state
    |  overlaid labels, arrows, highlights update per step
```

### Q5 — How do Vuforia Image Targets work?

**Registration:**
1. Upload photo of the physical tool to developer.vuforia.com Target Manager.
2. Vuforia analyzes image, assigns rating 0–5 stars. Rating 3+ required for reliable tracking.
3. Download as `.unitypackage` (local) or leave in cloud database.

**Local vs Cloud:**
- **Local:** Target data bundled into app binary. Fast, works offline. Adding new tools requires app update.
- **Cloud:** Targets on Vuforia's servers. App queries real-time. Add new tools without app update → correct choice for BuildARPro.

**Model Targets (important):** Upload a 3D CAD model instead of a photo. Vuforia matches live camera view against 3D shape — works even for tools with no distinctive texture. Requires Premium license. Likely the right choice for industrial tools.

### Q6 — Vuforia Free vs Paid

| Feature | Basic (Free) | Premium | Enterprise |
|---|---|---|---|
| Image Targets (local) | Yes | Yes | Yes |
| App Store publishing | Yes | Yes | Yes |
| Model Targets | Dev/watermark only | Yes | Yes |
| Cloud Image Recognition | 1,000 recos/month | Add-on available | Add-on available |
| On-premise deployment | No | No | Yes |
| Price | Free | Quote (annual) | Quote (annual) |
| Cloud overage | Suspended at 1,000 | $0.01/reco | Custom |

**Key limit:** 1,000 cloud recognitions/month is total across ALL users of the app. At any scale you will hit this. Cloud add-on: ~$99/month for 10,000 recos.

**Pricing opacity:** PTC does not publish Premium/Enterprise prices. Community reports suggest several hundred to low thousands USD/year. Contact sales when ready.

### Q7 — How does the app know which guide to play?

Via the **metadata field** on each target (up to 1 MB JSON):

```json
{ "guide_id": "dewalt_drill_v2", "product_sku": "DCD777C2" }
```

SDK returns metadata alongside tracking result. App reads `guide_id`, queries Supabase, loads correct step sequence.

### Q8 — Full runtime SDK call flow

1. App starts → `VuforiaApplication.Instance.Initialize()` with license key
2. Camera activates, Vuforia processes frames
3. `ObserverBehaviour.OnTargetStatusChanged` fires with `status = TRACKED`
4. App reads `observerBehaviour.TargetName` + `cloudRecoResult.MetaData`
5. Network request to Supabase for guide content
6. Step UI activates; child GameObjects become visible
7. Tracking lost → `status = NO_POSE` → GameObjects hidden

Note: Use `ObserverBehaviour.OnTargetStatusChanged` (Vuforia Engine 10+), not the deprecated `DefaultTrackableEventHandler`.

---

## BACKEND + PRICING

### Q9 — Supabase Schema Sketch

```sql
-- Core identity
users
  id          uuid PK (from Supabase Auth)
  email       text
  full_name   text
  created_at  timestamptz

-- Product catalog
guides
  id                  uuid PK
  owner_id            uuid FK → users.id
  title               text
  description         text
  product_sku         text           -- e.g. "DCD777C2"
  vuforia_target_id   text           -- Vuforia cloud target ID
  steps               jsonb          -- [{step_number, action, component, note}]
  created_at          timestamptz
  is_published        boolean

-- Vuforia targets registry
image_targets
  id                    uuid PK
  guide_id              uuid FK → guides.id
  vuforia_target_name   text
  target_type           text           -- 'image' | 'model'
  rating                int            -- Vuforia augmentability 0-5
  metadata_json         jsonb
  uploaded_at           timestamptz

-- Subscription management (mirrors Stripe)
subscriptions
  id                    uuid PK
  user_id               uuid FK → users.id
  stripe_customer_id    text
  stripe_sub_id         text
  plan_tier             text           -- 'free' | 'pro' | 'enterprise'
  status                text           -- 'active' | 'past_due' | 'canceled'
  guides_limit          int            -- 3 for free, -1 for unlimited
  current_period_end    timestamptz
  created_at            timestamptz

-- Usage tracking
guide_views
  id          uuid PK
  guide_id    uuid FK → guides.id
  user_id     uuid FK → users.id (nullable for anonymous)
  viewed_at   timestamptz
  device_os   text
```

**RLS:** Users read only their own `subscriptions` and `guides`. Published guides readable by any authenticated user.

### Q10 — Stripe Integration Pattern

1. **Products in Stripe:** "BuildARPro Free" ($0) and "BuildARPro Pro" (e.g. $29/month or $249/year)
2. **Checkout:** Stripe-hosted Checkout Session (web URL) opened from within the app. On iOS in the US (post May 2025 Apple policy change), this bypasses App Store fees. On Android, works natively in-browser.
3. **Webhook handler:** Supabase Edge Function at `/functions/v1/stripe-webhook`. Handles `checkout.session.completed`, `customer.subscription.updated`, `invoice.payment_failed` → updates `subscriptions` table.
4. **Entitlement check:** On app launch, query `subscriptions.plan_tier` + `guides_limit`. Lock "Add Guide" if free and `guide_count >= 3`.
5. **Stripe Billing Portal:** Give users a link for self-serve cancellation — no custom cancel flow needed.

**Note (international):** Apple's external payment link policy applies only to US developers + US users as of May 2025. International iOS = App Store 30% fee still required.

### Q11 — Vuforia Cloud Recognition vs Local

- Supports 1M+ targets in one cloud database
- 1,000 recos/month free; $99/month for 10,000; $0.01/reco overage
- Metadata (1 MB per target) returned with each match
- Add/update targets via Vuforia Web Services API — no app update needed
- Cloud + local can run simultaneously in one app (local for offline/frequent tools, cloud for full catalog)

---

## ALTERNATIVES

### Q12 — Is Vuforia still the standard in 2025?

| Technology | Industrial AR Fitness |
|---|---|
| Vuforia Engine (PTC) | Excellent — purpose-built, Model Targets, cloud DB |
| AR Foundation (Unity + ARKit/ARCore) | Moderate — no Model Targets, no cloud target DB |
| ARKit / ARCore (native) | Weak — no enterprise target management |
| Wikitude | Moderate — smaller market share |

AR Foundation calls ARKit/ARCore under the hood. It does NOT replace Vuforia — it has less capability for industrial use. **Vuforia is the correct choice for BuildARPro.**

### Q13 — Web AR for fast demo

| Option | Demo Speed | Quality | Production? | Cost |
|---|---|---|---|---|
| AR.js | Hours | Low | No | Free |
| MindAR.js | Days | Medium | Limited | Free |
| 8th Wall | Weeks | High | Yes | $2,000+/month |
| Unity + Vuforia | Months | Highest | Yes | Free basic tier |

---

## MVP TECH STACK — Ranked by Speed to Demo

| Rank | Stack | Time to Demo | Cost |
|---|---|---|---|
| 1 | AR.js + Supabase | 1–2 weeks | Free |
| 2 | 8th Wall + Supabase | 2–4 weeks | $2,000+/month |
| 3 | Unity + Vuforia + Supabase + Stripe | 6–12 weeks | Free (dev) |

**Recommended path:**
- **Weeks 1–2:** AR.js prototype for investor validation. Point phone at tool, see text steps overlaid in browser. No app install.
- **Months 2–4:** Unity + Vuforia development in parallel. Convert one real PDF manual (e.g., DeWalt drill) with LlamaExtract. Build Supabase backend.
- **Months 4–6:** TestFlight/beta. Stripe subscriptions live. Cloud target DB seeded with 5–10 tools.

---

## BLOCKERS AND UNKNOWNS

1. **3D model availability:** Vuforia Model Targets require a CAD file (FBX, OBJ, or 3D scan). Most manufacturers don't publish CAD publicly. Without a 3D model, you're limited to Image Targets — which require distinctive visual texture. **Biggest technical risk.**
2. **Vuforia Premium pricing opacity:** Must contact PTC sales. Budget uncertainty.
3. **LlamaExtract schema tuning:** Each new manual type may need schema adjustments. Not fully automated.
4. **Stripe + App Store on iOS outside US:** 30% Apple fee still required for international subscriptions initiated in-app.
5. **Cloud recognition latency:** 1–3 second lag on poor connectivity (warehouse, construction site). Mitigate with local caching of previously-accessed guides.
6. **Vuforia roadmap risk:** PTC may change free-tier terms. Platform dependency risk for a startup.

---

*Sources verified via web search 2026-05-02. See full citations in Tomy's raw output.*
