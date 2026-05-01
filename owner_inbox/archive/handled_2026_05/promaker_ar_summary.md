# BuildARPro — 1-Page Summary
**For:** Inon | **Date:** 2026-04-30 | **Purpose:** Direction check — is this the right product to build?

---

## What it is

BuildARPro is a phone app that turns a physical paper manual into a live 3D AR guide. You point your camera at the manual — the app reads it via OCR, builds a rotatable 3D model of what the manual depicts, and then overlays step-by-step AR visual cues onto your actual workspace as you build. Each step is explained in real time. Think: your IKEA paper manual becomes a guide that stands next to you, points at exactly where the next piece goes, and explains every step out loud — on your phone, no headset required.

Target: everyday consumers in Israel first. Stage: stealth, no users yet, you're the solo founder.

---

## The Market

- Mobile AR is a $30.6B market in 2025, growing at 31% annually — 2 billion people already use it monthly
- The DIY/home improvement market is $800B globally; AR-guided assembly is an $8.9B sub-segment by 2033
- No consumer product today does what BuildARPro does — all AR competitors stop at visualization (IKEA Place, Wayfair AR), none guide the actual build

---

## Why we can win

- **The gap is real and undefended.** IKEA Place shows you furniture in your room. Nobody shows you how to build it. That's a complete white space in a massive market.
- **Paper manuals are the universal pain point.** Every consumer product with assembly instructions — furniture, electronics, toys, appliances — is a potential entry point. The market is everywhere.
- **OCR-to-3D is the moat.** If you can reliably turn any paper manual into an AR guide (not just IKEA, not just one brand), you become a platform — not a niche app. That's the defensible edge.

---

## Tech path

MVP is a native iOS/Android app (React Native + ARKit/ARCore). The core pipeline: phone camera → OCR reads the manual text and diagrams → 3D model is generated matching the manual's illustrations → AR session overlays step indicators onto the user's physical workspace as they build. Start with one well-structured manual format (IKEA-style) to prove the pipeline, then expand. Full OCR-to-3D on arbitrary manuals is hard; a curated library of pre-processed manuals is the practical MVP path.

---

## Business model

Freemium consumer app: free for basic access, Pro subscription at ~$8/month for unlimited projects, voice guidance, and AI step explanations — launch free to build users, monetize at month 3.

---

## Next 3 months (MVP scope)

- Build the OCR + 3D interpretation pipeline for one manual format (IKEA or similar)
- AR step overlay working on iOS (ARKit) — arrows and numbered highlights on real workspace
- 10–15 pre-processed manuals available at launch
- Basic step sequencer: "step 1 of 8 → check → step 2 of 8"
- User account + project save (Supabase)
- App Store submission (iOS first)

---

## What we need to decide

1. **Manual sourcing strategy:** Do we pre-process a curated library (predictable, limited), or build a true OCR pipeline for any manual a user scans (hard, but the real prize)? Which is MVP?
2. **Israel-first launch — what does that mean?** Hebrew manual support? Hebrew UI? Or just "first users are Israeli" with English product?
3. **Solo founder → first hire:** The AR development (ARKit/ViroReact + OCR + 3D generation) is a serious technical challenge. Do you build it, hire a CTO, or scope MVP down to something buildable solo?
4. **3D model generation approach:** Free-form 3D generation from manual diagrams is a research-grade problem. Is the MVP actually "pre-built 3D models matched to known manuals" rather than true auto-generation? If yes, that changes the pitch significantly — be honest about this now.
