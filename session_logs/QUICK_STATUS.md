---
updated: 2026-05-02
---

# Quick Status — Andy Framework

## Last Session (2026-05-02 — autonomous run)
Inon left for the day. Andy launched autonomous work on 4 agents + completed product plan directly. Cole finished Elbit cover letter + Gmail draft. 3 agents still running (Mack-WhatsApp, Rex-Trademetrics, Lena-Banners). 4 new BuildARPro sprint tasks added. Product plan written.

## Active Tasks (compact)

| ID | Title | Priority | Owner | Status |
|----|-------|----------|-------|--------|
| ELBIT-APPLY-001 | Submit CV to Elbit | high | Cole | pending-owner — cover letter done, Gmail draft ready |
| CV-GENERIC-001 | Generic Senior PM CV PDF | high | Yoni | **done ✓** |
| PROMAKER-AR-002 | BuildARPro product plan | high | Andy | **done ✓** (owner_inbox/buildarpro_product_plan.md) |
| PROMAKER-AR-003 | BuildARPro pitch deck stealth | high | Cole | partial (text done; design pass pending Lena) |
| PROMAKER-AR-005 | Connect LlamaParse API | high | Mack | blocked — needs Supabase restore first |
| PROMAKER-AR-006 | BuildARPro 6 AR concept images | medium | Owner | blocked — Owner runs image prompts |
| PROMAKER-AR-007 | BuildARPro PPTX + banners design | high | Lena | in-progress (agent running) |
| PROMAKER-AR-008 | BuildARPro data flow + Vuforia research | high | Tomy | **done ✓** (owner_inbox/buildarpro_architecture_research.md) |
| PROMAKER-AR-009 | Restore Supabase Pro maker AR | high | Owner | pending — Inon does this today (2026-05-03) |
| PROMAKER-AR-010 | Apply Supabase schema | high | Silas | blocked — needs PROMAKER-AR-009 |
| PROMAKER-AR-011 | AR.js investor demo (1 tool) | high | Yoni | pending |
| PROMAKER-AR-012 | Stripe product + subscription setup | high | Mack | blocked — needs PROMAKER-AR-009 |
| PROMAKER-AR-013 | Vuforia account + first Image Target | high | Yoni | pending |
| INFRA-001 | Keep-alive schedule all projects | high | Mack | **done ✓** (routine live, Sunday 7am UTC) |
| WHATSAPP-001 | WhatsApp MCP config in Claude Code | medium | Mack | in-progress (agent running) |
| WEBSITE-001-SEC-01 | Remove Base44 badge | critical | Rex | blocked — Owner disables in dashboard |
| WEBSITE-001-SEC-04 | Security headers | high | Rex | partial (code done; Base44 dashboard needed) |
| WEBSITE-001-DESIGN-01 | Awwwards redesign | high | Rex | pending (waiting on Lena brief) |
| WEBSITE-001-UX-04 | CV download live PDF | medium | Rex | **done ✓** (generic CV deployed commit 772c24a) |
| WEBSITE-001-CONTENT-01 | Thought leadership journal | medium | Rex | in-progress |
| MOBILE-AUDIT-001 | Mobile audit — website | high | Vera | **done ✓** |
| MOBILE-AUDIT-002 | Mobile fixes — Trademetrics | medium | Rex | in-progress (agent running) |
| LINKEDIN-001 | 5 LinkedIn posts ready | medium | Sage | partial — awaiting Owner approval |
| REPO-CLEANUP-001 | Repository cleanup | low | Owner | blocked — decisions needed |

## Owner Blockers (prioritized)
1. **Supabase restore** — supabase.com/dashboard → "Restore backup to new Supabase project" (unblocks PROMAKER-AR-005/010/012)
2. **Add Supabase URL to infra/keep_alive_urls.txt** — after restore, paste new REST URL
3. **Elbit application** — open Gmail Drafts → attach v4_Inon_Baasov_CV_TrainingPM.pdf → apply at https://elbitsystemscareer.com/job/?jid=20344
4. **LinkedIn approval** — owner_inbox/linkedin_posts_refreshed.md (5 posts, Sage waiting)
5. **Base44 badge** — login to base44.app → app settings → disable platform badge
6. **AR concept images** — prompts at owner_inbox/promaker_ar_images_brief.md, run in Midjourney/DALL-E

## New in owner_inbox (ready for review)
- `buildarpro_product_plan.md` — full MVP plan, roadmap, pricing, Vuforia decisions
- `buildarpro_architecture_research.md` — Tomy's deep technical research
- `elbit_cover_letter_6486.md` — Elbit Training PM cover letter (+ Gmail draft)
- `cv_generic_done.md` — CV deployment confirmation
- `audit_familyflow_tradepulse.md` — Vera's mobile/accessibility audit
- `buildarpro_design_spec.md` — Lena's design spec (pending agent completion)
- `trademetrics_mobile_fixes.md` — Rex's fix summary (pending agent completion)
- `whatsapp_mcp_status.md` — Mack's WhatsApp config status (pending agent completion)
