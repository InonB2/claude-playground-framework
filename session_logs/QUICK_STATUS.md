---
updated: 2026-05-02
---

# Quick Status — Andy Framework

## Last Session (2026-05-02)
Operational session: Supabase crisis diagnosed (Pro maker AR paused 90+ days, restore tomorrow). LlamaParse API key + GitHub token extracted from team_inbox docx. BuildARPro MVP scope clarified (curated guide library + Supabase backend; "magic" auto-parsing is v2). Weekly keep-alive routine live (trig_01PLxe72RNnPN1XVPThob1yG, every Sunday 10am). Tomy dispatched for full data flow + Vuforia architecture research (results arriving in owner_inbox). Task list overhauled: 20 tasks, 3 new added.

## Active Tasks (compact)

| ID | Title | Priority | Owner | Status |
|----|-------|----------|-------|--------|
| ELBIT-APPLY-001 | Submit CV to Elbit | high | Cole | blocked — waiting on CV-GENERIC-001 |
| CV-GENERIC-001 | Generic Senior PM CV PDF | high | Yoni | in-progress |
| PROMAKER-AR-002 | BuildARPro product plan | high | Andy | in-progress |
| PROMAKER-AR-003 | BuildARPro pitch deck stealth | high | Cole | partial (text done; design gap) |
| PROMAKER-AR-005 | Connect LlamaParse API | high | Mack | blocked — needs Supabase restore first |
| PROMAKER-AR-006 | BuildARPro 6 AR concept images | medium | Owner | blocked — Owner runs image prompts |
| PROMAKER-AR-007 | BuildARPro PPTX + banners design | high | Lena | pending |
| PROMAKER-AR-008 | BuildARPro data flow + Vuforia research | high | Tomy | in-progress (background, results in owner_inbox) |
| PROMAKER-AR-009 | Restore Supabase Pro maker AR | high | Owner | pending — tomorrow (2026-05-03) |
| INFRA-001 | Keep-alive schedule all projects | high | Mack | in-progress (routine live, Sunday 10am) |
| WHATSAPP-001 | WhatsApp bridge sync | medium | Mack | in-progress |
| WEBSITE-001-SEC-01 | Remove Base44 badge | critical | Rex | blocked — Owner disables in dashboard |
| WEBSITE-001-SEC-04 | Security headers | high | Rex | partial (code done; Base44 dashboard needed) |
| WEBSITE-001-DESIGN-01 | Awwwards redesign | high | Rex | pending (waiting on Lena brief) |
| WEBSITE-001-UX-04 | CV download live PDF | medium | Rex | blocked — waiting on CV-GENERIC-001 |
| WEBSITE-001-CONTENT-01 | Thought leadership journal | medium | Rex | in-progress |
| MOBILE-AUDIT-001 | Mobile audit — website | high | Vera | done ✓ |
| MOBILE-AUDIT-002 | Mobile fixes — Trademetrics | medium | Rex | pending (repo: github.com/InonB2/trademetrics.git) |
| LINKEDIN-001 | 5 LinkedIn posts ready | medium | Sage | partial — awaiting Owner approval |
| REPO-CLEANUP-001 | Repository cleanup | low | Owner | blocked — decisions needed |

## Owner Blockers (prioritized)
1. **Supabase restore** — supabase.com/dashboard → "Restore backup to new Supabase project" (unblocks all BuildARPro backend)
2. **Add Supabase URL to infra/keep_alive_urls.txt** — after restore, paste new REST URL
3. **LinkedIn approval** — owner_inbox/linkedin_posts_refreshed.md (5 posts, Sage waiting)
4. **Base44 badge** — login to base44.app → app settings → disable platform badge
5. **AR concept images** — prompts at owner_inbox/promaker_ar_images_brief.md, run in Midjourney/DALL-E
