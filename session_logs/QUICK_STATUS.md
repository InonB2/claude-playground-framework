---
updated: 2026-04-29
---

# Quick Status — Andy Framework

## Last Session (2026-04-29)
Statusline redesigned: colour gradient + clear labels (5h session, ctx tokens, elapsed time, model).
WhatsApp bridge rebuilt: fixed whatsmeow context.Context API, modernc/sqlite foreign-key pragma, stale session cleared — QR code confirmed working.
CV Scale pipeline live: `scripts/cv_scale.py` — JD-in → PPTX tailored → PDF on approval.
ProMaker AR local assessment done. Launchpad is private GitHub repo; waiting for Inon to run `gh auth login` to unlock website + Launchpad push access.

## Active Tasks (compact)

| ID | Title | Priority | Owner | Status |
|----|-------|----------|-------|--------|
| CV-FIX-RENAME | Rename CV _NEW file / clean archive root | critical | Cole | pending |
| ELBIT-APPLY-001 | Submit CV to Elbit | high | Cole | blocked (CV-FIX-RENAME) |
| CV-SCALE-001 | CV scale pipeline | high | Cole | **done ✓** |
| PROMAKER-AR-001 | Assess ProMaker AR repo + brief | high | Tomy | **done ✓** (local copy; Launchpad=private) |
| PROMAKER-AR-002 | Define agent plan for ProMaker AR | high | Andy | pending (needs gh auth + Launchpad access) |
| GITHUB-001 | Push framework to GitHub | high | Mack | done ✓ |
| GITHUB-002 | Create Website-product-portfolio repo | high | Mack | done ✓ (repo exists) |
| WHATSAPP-001 | WhatsApp QR scan + Claude Desktop config | high | Mack | **waiting for Inon to scan QR** |
| WEBSITE-001-SEC-01 | Remove dev widget from production | critical | Rex | pending (needs gh auth) |
| WEBSITE-001-SEC-02 | Fix page title (remove 'Andy') | critical | Rex | pending (needs gh auth — title already correct in Home.jsx?) |
| WEBSITE-001-DESIGN-01 | Full awwwards-level redesign | high | Rex | pending (needs gh auth + pre-work) |
| WEBSITE-001-UX-03 | Replace emoji icons with real visuals | high | Lena | pending |
| WEBSITE-001-COPY-01 | Sharpen hero copy and bio | medium | Lena | pending |
| WEBSITE-001-SEC-03 | Add contact form | high | Rex | pending (needs gh auth) |
| WEBSITE-001-SEC-04 | Security headers audit | high | Maya | pending |
| WEBSITE-001-SEO-01 | SEO meta tags + structured data | high | Rex | pending (needs gh auth) |
| WEBSITE-001-UX-01 | Add testimonials section | high | Rex | blocked (Owner supplies quotes) |
| WEBSITE-001-UX-02 | Audit portfolio deep-dive links | high | Rex | pending |
| WEBSITE-001-UX-04 | Downloadable CV button | medium | Rex | blocked (CV-FIX-RENAME) |
| WEBSITE-001-DESIGN-02 | Scroll animations + counters | medium | Rex | pending |
| WEBSITE-001-UX-05 | Minimal contact form | medium | Rex | pending |
| WEBSITE-MIGRATE-001 | Migrate website to GitHub repo | high | Mack | done ✓ (repo exists at InonB2/inon-baasov-website) |
| LINKEDIN-001 | Draft first LinkedIn post | medium | Sage | pending |
| WEBSITE-001-PERF-01 | Mobile responsiveness audit | low | Vera | pending |
| WEBSITE-001-A11Y-01 | Accessibility audit | low | Vera | pending |
| WEBSITE-001-CONTENT-01 | Thought leadership section | low | Lena | blocked (Owner supplies content) |

## Owner Actions Needed (prioritized)
1. **WhatsApp QR**: `! "/c/tools/whatsapp-mcp/whatsapp-bridge/whatsapp-bridge.exe"` → scan QR in WhatsApp → Linked Devices
2. **GitHub auth**: `! gh auth login` → unlocks ALL website tasks + Launchpad access
3. **CV archive cleanup**: open `output/cv_archive/` in Explorer, close any open PPTX files (lock file present)
4. **Elbit CV review**: open v4_Inon_Baasov_CV_TrainingPM.pptx, review, tell Andy to submit
5. **Testimonial quotes** → 2-3 quotes with name/role for website
6. **Re-enable AV** if still disabled from debugging session

## Inbox
- team_inbox/: empty (new files scanned — V9.S.M4.TPMAI-E.pptx present, used in archive)
- owner_inbox/: empty

## ProMaker AR Brief (for PROMAKER-AR-002)
- App: AR-powered DIY assistant — "Make Every DIY a Pro Build"
- Stack: React 18 + Vite + Shadcn/ui + Supabase + Tailwind (Lovable-built)
- Supabase project (local copy): nlxoazmcrlzsezsyvdre — likely EXPIRED (90-day free tier)
- Launchpad = clone with fresh Supabase project_id (the live version Inon works in)
- GitHub remote (local copy): github.com/InonB2/pro-maker-ar.git
- Launchpad repo: github.com/InonB2/project-launchpad (private — needs gh auth to access)
- Pages: Index.tsx → Navbar, Hero, Features, Categories, HowItWorks, CTA, Footer
- Supabase function: validate-assembly-progress (JWT-protected)

## CV Scale Pipeline
Command: `python scripts/cv_scale.py generate --role "X" --company "Y" --location "Z" [--req-id N] [--jd jd.txt|--jd-url URL] [--summary "tailored text"]`
After approval: `python scripts/cv_scale.py topdf path/to/file.pptx`
Template: output/cv_archive/6486_TrainingPM_Elbit_Netanya/v4_Inon_Baasov_CV_TrainingPM.pptx
