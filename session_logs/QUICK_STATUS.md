---
updated: 2026-05-03
next_update: next /close
---

# Quick Status — Andy Framework

## Last Session (2026-05-03 — midnight)
Fixed /start + /session-handoff skills, hardened Tomy's researcher.md, integrated BuildARPro images into website, researched Ralph Loop. 3 agents hit rate limit before finishing — re-dispatch at next session.

---

## Owner: Do These Now

| # | Action | Context |
|---|--------|---------|
| 1 | Start WhatsApp bridge + restart Claude Code | `C:\tools\whatsapp-mcp\whatsapp-bridge\whatsapp-bridge.exe` |
| 2 | Check GH Pages Actions tab for AR demo | github.com/InonB2/claude-playground-framework/actions |
| 3 | Run `scripts\github_sync.ps1` | Push BuildARPro images to make them live on website |
| 4 | Submit Elbit CV | Gmail Drafts → attach v4 PDF → elbitsystemscareer.com/job/?jid=20344 |
| 5 | Approve LinkedIn posts | owner_inbox/posts/linkedin_posts_refreshed.md |
| 6 | Base44 badge + headers | base44.app → app settings |

---

## Active Tasks

| ID | Title | Priority | Owner | Status |
|----|-------|----------|-------|--------|
| RALPH-LOOP-001 | Implement Ralph Loop | high | Mack | **pending — re-dispatch** |
| DASHBOARD-001 | C&C project filters + inline edit | high | Rex | **pending — re-dispatch** |
| SCRATCHPAD-001 | Scratchpad cleanup | low | General | **pending — re-dispatch** |
| PROMAKER-AR-005 | Connect LlamaParse API | high | Mack | pending (unblocked) |
| PROMAKER-AR-012 | Stripe setup | high | Mack | pending |
| PROMAKER-AR-013 | Vuforia account + Image Target | high | Yoni | pending |
| PROMAKER-AR-003 | Pitch deck stealth text | high | Cole | partial |
| WEBSITE-001-DESIGN-01 | Awwwards redesign | high | Rex | blocked (wrong repo) |
| WEBSITE-001-SEC-01 | Remove Base44 badge | critical | Rex | blocked (Owner) |
| WEBSITE-001-SEC-04 | Security headers | high | Rex | partial |
| WEBSITE-001-CONTENT-01 | Journal section | medium | Rex | in-progress |
| WHATSAPP-001 | WhatsApp MCP activate | high | Mack | pending-owner |
| LINKEDIN-001 | 5 LinkedIn posts | medium | Sage | pending-owner |
| ELBIT-APPLY-001 | Submit CV to Elbit | high | Cole | pending-owner |

---

## Next Session: Start Here

1. Re-dispatch Mack — RALPH-LOOP-001 (.ralph/guardrails.md, 14 learning_log.md files, fix github_sync.ps1, WhatsApp autostart)
2. Re-dispatch Rex — DASHBOARD-001 (project filters + inline edit on dashboard/index.html)
3. Re-dispatch scratchpad cleanup agent
4. Dispatch Mack — PROMAKER-AR-005 (set LLAMAPARSE_API_KEY secret on Supabase project meonilvpqerbemeikrfk)
5. Dispatch Yoni — update pro-maker-ar/.env with Supabase credentials from scratchpad/buildarpro_supabase_env.txt
