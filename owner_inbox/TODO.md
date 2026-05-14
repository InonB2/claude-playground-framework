# Owner Action Items
_Last updated: 2026-05-14_

---

### [JOBSEARCH-PHASE-2] ✅ Phase 2 shipped — green-light Phase 3?
**Context (2026-05-14):** Phase 2 complete and QA-approved. Rex shipped prep checklist (5 items) per job + follow-up reminders with overdue banner. Yoni shipped ATS Match tab with weighted keyword engine. Jasmin retuned engine after self-test surfaced over-strict scoring. Vera: 194/194 jsdom PASS.
**Action:**
1. Open dashboard → check new ATS Match tab. Try pasting one of your Elbit JDs and the matching CV — note the gap keywords.
2. **Cole rework needed before Elbit submissions** — Jasmin's engine confirms `artillery`, `c4i`, `smart sensing`, `cyber` are missing from your Elbit CVs. Authorize Cole to integrate these keywords (without fabricating experience).
3. Say "go Phase 3" to dispatch contacts panel + AI Prompt Toolkit + URL auto-parser (3 features, Rex + Yoni + Mack).
**Files:** `owner_inbox/research/job_search_upgrade_plan.md`, `agents/andy/inbox/jasmin_ats_engine_qa.md`, `agents/andy/inbox/vera_jobsearch_phase2_qa.md`.

---

~~### [WHATSAPP-001] Fix bridge SQLite lock~~ — PAUSED
**2026-05-05:** All WhatsApp software stopped by Inon. Watchdog task deleted, bridge killed, no auto-start. GitHub credentials cleaned (removed stale InonBaasov + generic entries, kept InonB2 only — this also fixed the GitHub account-picker popup). Resume when ready — Green API is the recommended clean solution (2-way, no local bridge).

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

### [CV-WORKFLOW] Send a JD link to get a custom CV
**Context (2026-05-05):** Generic CV template is ready at `scratchpad/cv_senior_pm_generic.html` with 7 marked zones. Dashboard CV tab can now show HTML previews. Cole is briefed on the full workflow.
**Action:** Send Andy a JD URL. Cole will: (1) customize all 7 zones; (2) show HTML preview; (3) iterate until approved; (4) produce PPTX + PDF in `owner_inbox/cvs/[jd-slug]/`; (5) register in dashboard CV tab.

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
