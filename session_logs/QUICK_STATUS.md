---
updated: 2026-05-02
---

# Quick Status — Andy Framework

## Last Session (2026-05-02 — autonomous run)
Full autonomous session while Inon was away. 4 agents dispatched and completed. Net: 8 tasks marked done (CV, product plan, Tomy research, infra, CV download, mobile audit, Trademetrics fixes, Lena design), 4 new BuildARPro sprint tasks added, WhatsApp MCP configured (needs bridge process + restart).

## Active Tasks (compact)

| ID | Title | Priority | Owner | Status |
|----|-------|----------|-------|--------|
| ELBIT-APPLY-001 | Submit CV to Elbit | high | Cole | pending-owner — Gmail draft ready, attach v4 PDF |
| CV-GENERIC-001 | Generic Senior PM CV PDF | high | Yoni | **done ✓** |
| PROMAKER-AR-002 | BuildARPro product plan | high | Andy | **done ✓** |
| PROMAKER-AR-003 | BuildARPro pitch deck stealth | high | Cole | partial (apply text to PPTX manually; styled PPTX at scratchpad/) |
| PROMAKER-AR-005 | Connect LlamaParse API | high | Mack | blocked — needs Supabase restore |
| PROMAKER-AR-006 | BuildARPro AR concept images | medium | Owner | blocked — Owner runs image prompts |
| PROMAKER-AR-007 | BuildARPro PPTX + banners design | high | Lena | **done ✓** |
| PROMAKER-AR-008 | BuildARPro data flow + Vuforia research | high | Tomy | **done ✓** |
| PROMAKER-AR-009 | Restore Supabase Pro maker AR | high | Owner | pending — Inon does this (2026-05-03) |
| PROMAKER-AR-010 | Apply Supabase schema | high | Silas | blocked — needs PROMAKER-AR-009 |
| PROMAKER-AR-011 | AR.js investor demo (1 tool) | high | Yoni | pending |
| PROMAKER-AR-012 | Stripe product + subscription setup | high | Mack | blocked — needs PROMAKER-AR-009 |
| PROMAKER-AR-013 | Vuforia account + first Image Target | high | Yoni | pending |
| INFRA-001 | Keep-alive schedule all projects | high | Mack | **done ✓** |
| WHATSAPP-001 | WhatsApp MCP config in Claude Code | medium | Mack | pending-owner — start bridge + restart Claude Code |
| WEBSITE-001-SEC-01 | Remove Base44 badge | critical | Rex | blocked — Owner disables in dashboard |
| WEBSITE-001-SEC-04 | Security headers | high | Rex | partial (code done; Base44 dashboard needed) |
| WEBSITE-001-DESIGN-01 | Awwwards redesign | high | Rex | pending (Lena spec now done — Rex can start) |
| WEBSITE-001-UX-04 | CV download live PDF | medium | Rex | **done ✓** |
| WEBSITE-001-CONTENT-01 | Thought leadership journal | medium | Rex | in-progress |
| MOBILE-AUDIT-001 | Mobile audit — website | high | Vera | **done ✓** |
| MOBILE-AUDIT-002 | Mobile fixes — Trademetrics | medium | Rex | **done ✓** (commit 8e266c5) |
| LINKEDIN-001 | 5 LinkedIn posts ready | medium | Sage | partial — awaiting Owner approval |
| REPO-CLEANUP-001 | Repository cleanup | low | Owner | blocked — decisions needed |

## Owner Blockers (prioritized)
1. **Supabase restore** — supabase.com/dashboard → "Restore backup to new Supabase project" (unblocks PROMAKER-AR-005/010/012 — 3 tasks)
2. **Elbit application** — open Gmail Drafts → attach v4_Inon_Baasov_CV_TrainingPM.pdf → submit at https://elbitsystemscareer.com/job/?jid=20344
3. **WhatsApp activation** — run `cd C:\tools\whatsapp-mcp\whatsapp-bridge && .\whatsapp-bridge.exe`, then restart Claude Code → WhatsApp messaging live
4. **LinkedIn approval** — owner_inbox/linkedin_posts_refreshed.md (5 posts waiting)
5. **Base44 badge** — base44.app → app settings → disable platform badge
6. **Trademetrics icons** — upload optimized 192px/512px PNGs via Base44 dashboard
7. **AR concept images** — prompts at owner_inbox/promaker_ar_images_brief.md

## New in owner_inbox (this session)
- `buildarpro_product_plan.md` — MVP plan, roadmap, pricing, sprint tasks
- `buildarpro_architecture_research.md` — Tomy's full tech research (LlamaParse + Vuforia)
- `buildarpro_design_spec.md` — Lena's brand spec (colors, type, spacing, do/don'ts)
- `elbit_cover_letter_6486.md` — Training PM cover letter (Gmail draft created)
- `trademetrics_mobile_fixes.md` — Rex's fix summary (commit 8e266c5)
- `whatsapp_mcp_status.md` — Mack's WhatsApp config summary

## New in scratchpad (ready to use)
- `buildarpro_banner.html` — hero banner (responsive, dark/orange)
- `buildarpro_social_banner.html` — LinkedIn/Twitter 1200×628 banner
- `buildarpro_pptx_style.py` — run to generate styled pitch deck
- `BuildARPro_PitchDeck_Styled.pptx` — already generated, ready to open
