---
updated: 2026-04-29
---

# Quick Status — Andy Framework

## Last Session (2026-04-29)
WhatsApp bridge fully rebuilt (whatsmeow context.Context API + foreign-key pragma fix + fresh QR). CV scale pipeline live at scripts/cv_scale.py (JD->PPTX->PDF from V4 template). Statusline redesigned with colour bars + clear labels. LinkedIn post drafted. ProMaker AR assessed.

## Active Tasks (compact)

| ID | Title | Priority | Owner | Status |
|----|-------|----------|-------|--------|
| CV-FIX-RENAME | Clean cv_archive + rename files | critical | Cole | pending |
| ELBIT-APPLY-001 | Submit CV to Elbit | high | Cole | blocked (CV-FIX-RENAME + V4 approval) |
| CV-SCALE-001 | CV scale pipeline | high | Cole | done ✓ |
| PROMAKER-AR-001 | Assess ProMaker AR repo | high | Tomy | done ✓ |
| PROMAKER-AR-002 | Agent plan for ProMaker AR | high | Andy | pending (needs gh auth) |
| GITHUB-001 | Push framework to GitHub | high | Mack | done ✓ |
| GITHUB-002 | website-product-portfolio repo | high | Mack | done ✓ |
| WHATSAPP-001 | WhatsApp QR scan | high | Mack | **waiting for Inon to scan** |
| WEBSITE-001-SEC-01 | Remove dev widget | critical | Rex | pending (gh auth + live site check) |
| WEBSITE-001-SEC-02 | Fix page title (Andy) | critical | Rex | done ✓ (title correct in source) |
| WEBSITE-001-DESIGN-01 | Awwwards redesign | high | Rex | pending (gh auth + pre-work) |
| WEBSITE-001-UX-03 | Replace emoji icons | high | Lena | pending |
| WEBSITE-001-COPY-01 | Sharpen hero copy | medium | Lena | pending |
| WEBSITE-001-SEC-03 | Add contact form | high | Rex | pending (gh auth) |
| WEBSITE-001-SEC-04 | Security headers audit | high | Maya | pending |
| WEBSITE-001-SEO-01 | SEO meta tags | high | Rex | pending (gh auth) |
| WEBSITE-001-UX-01 | Testimonials section | high | Rex | blocked (Owner supplies quotes) |
| WEBSITE-001-UX-02 | Audit portfolio links | high | Rex | pending (gh auth) |
| WEBSITE-001-UX-04 | Downloadable CV button | medium | Rex | partial (committed, push + PDF URL needed) |
| WEBSITE-001-DESIGN-02 | Scroll animations + counters | medium | Rex | done ✓ (already in source) |
| WEBSITE-001-UX-05 | Minimal contact form | medium | Rex | pending (gh auth) |
| WEBSITE-MIGRATE-001 | Migrate website to GitHub | high | Mack | done ✓ |
| LINKEDIN-001 | Draft LinkedIn post | medium | Sage | done ✓ (in owner_inbox, awaiting approval) |
| WEBSITE-001-PERF-01 | Mobile audit | low | Vera | pending |
| WEBSITE-001-A11Y-01 | Accessibility audit | low | Vera | pending |
| WEBSITE-001-CONTENT-01 | Thought leadership section | low | Lena | blocked (Owner supplies content) |

## Owner Blockers (prioritized)
1. **WhatsApp QR**: `! "/c/tools/whatsapp-mcp/whatsapp-bridge/whatsapp-bridge.exe"` → scan in WhatsApp → Linked Devices
2. **gh auth login**: `! gh auth login` → unlocks ALL website tasks (10+ tasks) + Launchpad repo access
3. **V4 PPTX approval**: review v4_Inon_Baasov_CV_TrainingPM.pptx → tell Andy "approved" → PDF generated → Elbit submission
4. **CV PDF URL**: upload CV PDF to Google Drive or GitHub → paste URL to Andy → Rex updates website button
5. **LinkedIn post**: review owner_inbox/linkedin_post_draft_001.md → say "approved" → Sage posts
6. **Testimonials**: 2-3 quotes (name + role) for website
7. **Close open PPTX**: lock file ~$v4_...pptx blocking git (PowerPoint has file open)
