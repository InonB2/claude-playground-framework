# BuildARPro — Product Plan v1
**Author:** Andy (Orchestrator)  
**Date:** 2026-05-02  
**Inputs:** Tomy architecture research (owner_inbox/buildarpro_architecture_research.md), Owner briefings, previous sessions  
**Status:** MVP scope locked. Task breakdown ready for delegation.

---

## What BuildARPro Is

A SaaS platform for industrial maintenance teams. Users point their phone camera at a tool or machine — the app recognizes it and overlays a step-by-step AR repair/maintenance guide. Replaces paper manuals and training videos.

**The pitch in one line:** "Stop Pausing VIDEOS, Start building BETTER"

---

## MVP Scope (locked)

**MVP = curated AR guide library.** We pre-build guides for 5–10 industrial tools. Users subscribe, unlock the library, and use the guides.

What MVP is NOT:
- Auto-parsing (user uploads paper manual → auto-generated AR guide) — this is v2
- Unlimited catalog — start with 5–10 curated guides
- Full industrial deployment — start with one vertically (e.g., power tools / HVAC)

---

## Tech Stack (confirmed by Tomy's research)

| Layer | Technology | Notes |
|---|---|---|
| AR runtime | Vuforia Engine + Unity | Model Targets for industrial tools, Cloud Recognition for catalog scale |
| Content pipeline | LlamaParse + LlamaExtract | For v2 auto-parsing; MVP guides built manually |
| Backend | Supabase | Auth, guide DB, subscriptions, RLS |
| Billing | Stripe | Hosted checkout, webhooks, billing portal |
| Demo (fast) | AR.js | Web-based, no install, investor demo only |
| Mobile app | Unity iOS + Android | Vuforia-based, compiles to native binary |

---

## Two-Phase Roadmap

### Phase 1 — Investor Demo (Weeks 1–2)
**Goal:** Something a VC can point their phone at and say "wow."

Stack: AR.js (web AR, no install) + one hardcoded guide.

Steps:
1. Pick one demo tool (e.g., DeWalt drill, HVAC filter replacement)
2. AR.js: detect the tool via image target, overlay 3–5 text steps
3. Host demo at a URL (no login required)
4. Use in pitch: "This is what our app does"

Deliverable: `demo.buildarpro.com` — a live, shareable AR demo.

Agents: Yoni (AR.js + hosting), Rex (landing page + demo embed).

### Phase 2 — MVP Product (Months 2–4)
**Goal:** Paying subscribers using real AR guides on their phone.

Steps:
1. Restore Supabase project (Owner — 2026-05-03, PROMAKER-AR-009)
2. Apply Tomy's schema to Supabase (Silas)
3. Unity + Vuforia app with 5 guides built-in (Yoni)
4. Stripe subscriptions (Mack + Yoni)
5. Register 5–10 Image Targets in Vuforia Cloud (Yoni)
6. TestFlight beta (Yoni + Owner)

Deliverable: App Store beta with 5 guides, Stripe billing live.

---

## Supabase Schema (from Tomy's research)

Five tables needed for MVP:

```sql
users          — auth.users extension (Supabase handles)
guides         — id, title, product_sku, vuforia_target_id, steps (jsonb), is_published
image_targets  — id, guide_id, vuforia_target_name, target_type, rating
subscriptions  — id, user_id, stripe_customer_id, plan_tier, guides_limit, status
guide_views    — id, guide_id, user_id, viewed_at (analytics)
```

Full schema with SQL at: `owner_inbox/buildarpro_architecture_research.md` → Q9.

---

## Pricing Model (recommended)

| Tier | Price | Guides access | Target user |
|---|---|---|---|
| Free | $0 | 1 demo guide | Evaluation |
| Pro | $29/month or $249/year | Full library (unlimited) | Solo technician |
| Team | $99/month | Full library + 5 seats | Small shop |
| Enterprise | Custom | Full library + custom guides | Industrial fleet |

Stripe products: Free, Pro, Team. Enterprise via sales call.

**Note on iOS:** Stripe hosted checkout works for international. Apple App Store 30% fee still applies for iOS users outside the US for in-app purchases — use web checkout link workaround (post May 2025 Apple policy).

---

## Vuforia Key Decisions

1. **Image Targets vs Model Targets:** Start with Image Targets (free tier). Upgrade to Model Targets (Premium license, needs CAD files) when we have 3D models. Contact PTC sales when approaching 5 guides.

2. **Cloud vs Local targets:** Use Cloud Recognition for the catalog. 1,000 recos/month free — enough for beta. Budget $99/month ($0.01/reco overage) at scale.

3. **Biggest technical risk:** CAD files. Vuforia Model Targets require a 3D CAD model of the tool (FBX/OBJ/3D scan). Most manufacturers don't publish these. Mitigation: start with Image Targets on high-texture tools (e.g., branded power tools with distinctive logos/shapes). Explore 3D scan (LiDAR on iPhone) as fallback.

---

## v2 Features (backlog — do not build now)

1. **Auto-parsing:** User uploads paper manual PDF → LlamaParse + LlamaExtract → structured steps → Unity AR guide. Tomy confirmed this is technically possible but requires a custom Transform Layer (steps JSON → Unity scene). 2–3 months of engineering.

2. **Vuforia Studio authoring:** PTC's drag-and-drop AR authoring tool. Speeds up guide creation for non-developers. Evaluate after MVP.

3. **Model Target upgrade:** Once we have CAD files or 3D scans, upgrade to Model Targets for better tracking on featureless surfaces.

---

## Immediate Agent Tasks (this sprint)

| Task ID | Task | Agent | Blocked by |
|---|---|---|---|
| PROMAKER-AR-009 | Restore Supabase | Owner | — (do today) |
| PROMAKER-AR-010 | Apply Supabase schema | Silas | PROMAKER-AR-009 |
| PROMAKER-AR-011 | AR.js investor demo (1 tool) | Yoni | — |
| PROMAKER-AR-012 | Stripe product setup | Mack | PROMAKER-AR-009 |
| PROMAKER-AR-005 | Connect LlamaParse API | Mack | PROMAKER-AR-009 |
| PROMAKER-AR-007 | PPTX + banners design | Lena | In progress |
| PROMAKER-AR-013 | Vuforia account + first Image Target | Yoni | — |

**New tasks for Andy to add to active_tasks.json:** PROMAKER-AR-010, PROMAKER-AR-011, PROMAKER-AR-012, PROMAKER-AR-013.

---

## Success Criteria for MVP

- [ ] Supabase restored, schema applied, RLS active
- [ ] At least 3 guides in the library (published, visible to subscribers)
- [ ] Stripe Pro plan live (can take real payment)
- [ ] Unity app builds for iOS + Android (TestFlight link)
- [ ] Pointing phone at a real tool triggers correct AR guide
- [ ] Free tier: 1 guide accessible without payment
- [ ] Pro tier: all guides accessible after payment

---

*Andy — Orchestrator | PROMAKER-AR-002 | 2026-05-02*
