---
updated: 2026-05-01
---

# Quick Status — Andy Framework

## Last Session (2026-05-01)
Massive operational session: website hero copy + SVG icons + Journal section + 10 mobile fixes deployed live. Generic Senior PM CV converted to PDF + deployed. 5 LinkedIn posts + 3 thought leadership posts written. LlamaParse API integration built. WhatsApp bridge QR scanned. FamilyFlow + TradePulse mobile audits complete (TradePulse has 3 critical failures needing source repo).

## Active Tasks (compact)

| ID | Title | Priority | Owner | Status |
|----|-------|----------|-------|--------|
| ELBIT-APPLY-001 | Submit CV to Elbit | high | Cole | blocked — waiting on generic PDF (CV-GENERIC-001) |
| CV-GENERIC-001 | Generic Senior PM CV PDF | high | Yoni | in-progress (source: CV1_AskAI, output to cv_archive/) |
| PROMAKER-AR-002 | BuildARPro product plan | high | Andy | in-progress (stealth; OCR deferred; LlamaParse confirmed) |
| PROMAKER-AR-003 | BuildARPro pitch deck stealth | high | Cole | partial (v2 written to owner_inbox; Owner applies to PPTX manually) |
| PROMAKER-AR-005 | Connect LlamaParse API | high | Mack | pending (Owner must run: supabase secrets set LLAMAPARSE_API_KEY=...) |
| PROMAKER-AR-006 | BuildARPro 6 AR concept images | medium | Owner | blocked — Owner runs prompts (brief at owner_inbox/promaker_ar_images_brief.md) |
| WHATSAPP-001 | WhatsApp bridge sync | medium | Mack | in-progress (QR scanned; history syncing) |
| WEBSITE-001-SEC-01 | Remove Base44 badge | critical | Rex | blocked — Owner must disable in base44.app dashboard |
| WEBSITE-001-SEC-04 | Security headers | high | Rex | partial (code fixes done; HTTP headers need Base44 dashboard) |
| WEBSITE-001-DESIGN-01 | Full Awwwards redesign | high | Rex | pending (waiting on Lena design brief) |
| WEBSITE-001-UX-01 | Testimonials section | high | Rex | blocked — Owner supplies 2-3 quotes (name + role) |
| WEBSITE-001-UX-04 | CV download — live PDF | medium | Rex | blocked — waiting on CV-GENERIC-001 to replace current PDF |
| WEBSITE-001-CONTENT-01 | Thought leadership journal | medium | Rex | in-progress (3 posts live, UI built) |
| MOBILE-AUDIT-001 | Mobile audit — website | high | Vera | done ✓ |
| MOBILE-AUDIT-002 | Mobile audit — FamilyFlow + TradePulse | medium | Vera | in-progress (TradePulse: 3 critical failures; needs source repo) |
| LINKEDIN-001 | 5 LinkedIn posts ready | medium | Sage | partial — awaiting Owner approval to publish |
| REPO-CLEANUP-001 | Repo cleanup — 4 decisions | low | Owner | blocked — Owner decisions needed (see notes in tasks/) |

## Owner Blockers (prioritized)
1. **LinkedIn approval** — owner_inbox/linkedin_posts_refreshed.md (5 posts, ready to publish)
2. **LlamaParse API key** — `supabase secrets set LLAMAPARSE_API_KEY=llx-...` (unblocks PROMAKER-AR-005)
3. **TradePulse repo name** — 3 critical mobile/a11y failures ready to fix once Rex has repo access
4. **Base44 badge** — login to base44.app → app settings → disable platform badge
5. **Testimonials** — 2-3 quotes (name + role + company) for website
6. **Rotate Supabase anon key** — Supabase dashboard → Settings → API → Reset
