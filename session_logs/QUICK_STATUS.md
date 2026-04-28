---
updated: 2026-04-28
---

# Quick Status — Andy Framework

## Last Session (2026-04-28)
WhatsApp bridge binary built and tested (pure-Go SQLite, AV workaround via -ldflags=-buildid=). Two Elbit PPTX CVs generated from user templates (Training PM #6486 + AI Innovation PM #5811). Session closed and pushed to GitHub.

## Active Tasks (compact)

| ID | Title | Priority | Owner | Status |
|----|-------|----------|-------|--------|
| CV-FIX-RENAME | Rename CV _NEW file | critical | Cole | pending |
| ELBIT-APPLY-001 | Submit CV to Elbit | high | Cole | blocked (CV-FIX-RENAME) |
| PROMAKER-AR-001 | Assess ProMaker AR repo + brief | high | Tomy | pending |
| PROMAKER-AR-002 | Define agent plan for ProMaker AR | high | Andy | blocked (AR-001) |
| GITHUB-001 | Push framework to GitHub | high | Mack | done ✓ |
| GITHUB-002 | Create Website-product-portfolio repo | high | Mack | blocked (Owner creates repo) |
| WHATSAPP-001 | WhatsApp bridge QR scan + Claude Desktop config | high | Mack | **ready-to-pair** |
| WEBSITE-001-SEC-01 | Remove dev widget from production | critical | Rex | pending (needs Base44) |
| WEBSITE-001-SEC-02 | Fix page title (remove 'Andy') | critical | Rex | pending (needs Base44) |
| WEBSITE-001-DESIGN-01 | Full awwwards-level redesign | high | Rex | pending (needs Base44 + pre-work) |
| WEBSITE-001-UX-03 | Replace emoji icons with real visuals | high | Lena | pending |
| WEBSITE-001-COPY-01 | Sharpen hero copy and bio | medium | Lena | pending |
| WEBSITE-001-SEC-03 | Add contact form | high | Rex | pending (needs Base44) |
| WEBSITE-001-SEC-04 | Security headers audit | high | Maya | pending |
| WEBSITE-001-SEO-01 | SEO meta tags + structured data | high | Rex | pending (needs Base44) |
| WEBSITE-001-UX-01 | Add testimonials section | high | Rex | blocked (Owner supplies quotes) |
| WEBSITE-001-UX-02 | Audit portfolio deep-dive links | high | Rex | pending (needs Base44) |
| WEBSITE-001-UX-04 | Downloadable CV button | medium | Rex | blocked (CV-FIX-RENAME) |
| WEBSITE-001-DESIGN-02 | Scroll animations + counters | medium | Rex | pending |
| WEBSITE-001-UX-05 | Minimal contact form | medium | Rex | pending |
| WEBSITE-MIGRATE-001 | Migrate website to GitHub repo | high | Mack | blocked (GITHUB-002) |
| LINKEDIN-001 | Draft first LinkedIn post | medium | Sage | pending |
| WEBSITE-001-PERF-01 | Mobile responsiveness audit | low | Vera | pending |
| WEBSITE-001-A11Y-01 | Accessibility audit | low | Vera | pending |
| WEBSITE-001-CONTENT-01 | Thought leadership section | low | Lena | blocked (Owner supplies content) |

## Owner Blockers (need your action)
- **WhatsApp QR**: Run `.\whatsapp-bridge.exe` in `C:\tools\whatsapp-mcp\whatsapp-bridge\` and scan QR
- **Training PM CV summary**: Open v4 PPTX and paste training-focused summary from JD.txt manually
- **Base44 access** → blocks all website tasks (10+ tasks waiting)
- **Testimonial quotes** → 2-3 quotes with name/role for website
- **Re-enable AV** if still disabled from debugging session

## Inbox
- team_inbox/: empty
- owner_inbox/: empty
