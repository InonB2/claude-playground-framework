# Owner Action Items
_Last updated: 2026-05-03_

## Decisions Needed

### [ELBIT-APPLY-001] Submit CV to Elbit Systems
**Context:** Cover letter drafted, Gmail draft ready, CV tailored.
**Action:** Open Gmail → Drafts → attach `v4_Inon_Baasov_CV_TrainingPM.pdf` → apply at https://elbitsystemscareer.com/job/?jid=20344
**Files:** `cvs/elbit_cover_letter_6486.md`

---

### [WHATSAPP-001] Activate WhatsApp MCP
**Context:** Everything is installed; only the bridge process needs to be started.
**Action:** Open PowerShell → run `cd C:\tools\whatsapp-mcp\whatsapp-bridge && .\whatsapp-bridge.exe` (keep running) → restart Claude Code.

---

### [WEBSITE-001-SEC-01] Remove Base44 platform badge
**Context:** Badge is injected at the hosting layer — cannot be removed from code.
**Action:** Log into base44.app → app settings → disable platform badge.

---

### [WEBSITE-001-SEC-04] Set security HTTP headers
**Context:** Code-side fixes done; headers (CSP, HSTS) require the hosting dashboard.
**Action:** Open Base44 dashboard → Custom Headers panel → add CSP/HSTS headers (or confirm Base44 doesn't support it so Rex can document).

---

~~### [PROMAKER-AR-010] Create new Supabase project for BuildARPro~~ ✅ DONE  
Project `meonilvpqerbemeikrfk` (eu-west-1) — all 5 tables live. Credentials at `scratchpad/buildarpro_supabase_env.txt`.

---

### [LINKEDIN-001] Approve and publish 5 LinkedIn posts
**Context:** Posts are drafted and ready.
**Action:** Review `posts/linkedin_posts_refreshed.md` → publish or approve each post.

---

### [TRADEMETRICS] Two manual Base44 dashboard fixes remaining
**Context:** Code fixes shipped; two items require a dashboard upload.
**Action:** (1) Resize app icon: upload new icon in Base44 settings (TP-MOB-05). (2) Update manifest name in Base44 settings (TP-MOB-08).
**Files:** `research/trademetrics_mobile_fixes.md`

---
