# Owner Action Items
_Last updated: 2026-05-04_

---

### [WHATSAPP-001] Fix bridge SQLite lock — bridge is DOWN again
**Context (2026-05-04 session 2):** Bridge crashed again. Stale file `C:\tools\whatsapp-mcp\whatsapp-bridge\store\whatsapp.db-journal` is blocking startup with SQLITE_BUSY. Watchdog is registered but only monitors the Python server, not the Go bridge.
**Action:** Tell Andy "delete whatsapp.db-journal and restart the bridge" — or do it yourself:
1. Delete `C:\tools\whatsapp-mcp\whatsapp-bridge\store\whatsapp.db-journal`
2. Start `C:\tools\whatsapp-mcp\whatsapp-bridge\whatsapp-bridge.exe`
3. Restart Claude Code → test send to 972544445856

---

### [PROMAKER-AR-011] Check AR demo GitHub Pages
**Context:** Pages is enabled on ar-demo branch (confirmed in screenshot). May still show 404 while GH builds.
**Action:** Check github.com/InonB2/claude-playground-framework/actions → confirm "pages build and deployment" succeeded.
**URL when live:** https://inonb2.github.io/claude-playground-framework/

---

### [WEBSITE] Push BuildARPro images live
**Context:** Rex added BuildARPro as Product #05 in Home.jsx with images — won't render until pushed.
**Action:** Run `scripts\github_sync.ps1` (or `git add -A && git commit && git push`).

---

### [ELBIT-APPLY-001] Submit CV to Elbit Systems
**Context:** Gmail draft ready, CV tailored.
**Action:** Gmail → Drafts → attach `v4_Inon_Baasov_CV_TrainingPM.pdf` → apply at https://elbitsystemscareer.com/job/?jid=20344

---

### [LINKEDIN-001] Approve and publish 5 LinkedIn posts
**Action:** Review `posts/linkedin_posts_refreshed.md` → publish or approve each post.

---

### [WEBSITE-001-SEC-01] Remove Base44 platform badge
**Action:** base44.app → app settings → disable platform badge.

---

### [WEBSITE-001-SEC-04] Set security HTTP headers
**Action:** Base44 dashboard → Custom Headers panel → add CSP/HSTS (or confirm unsupported).

---

### [TRADEMETRICS] Two Base44 dashboard fixes
**Action:** (1) Upload resized app icon (TP-MOB-05). (2) Update manifest name (TP-MOB-08).
**Files:** `research/trademetrics_mobile_fixes.md`

---

~~### [PROMAKER-AR-010] Create new Supabase project~~ ✅ DONE
Project `meonilvpqerbemeikrfk` (eu-west-1). Credentials at `scratchpad/buildarpro_supabase_env.txt`.
