# Owner Action Items
_Last updated: 2026-05-18_

---

### [TELEGRAM-WATCHDOG-CHECK] Watchdog process not running on host
**Context (2026-05-18):** Mack rotated the Telegram token + closed the httpx logger leak. Listener PID 68044 is alive and polling cleanly. However: the watchdog (`scripts/telegram_listener_watchdog.ps1` + the `AndyTelegramListener` Scheduled Task) wasn't observed running during Mack's restart — he had to start the listener manually. If the machine reboots, /continue from Telegram may not auto-resume.
**Action when at desk:** Check Task Scheduler → AndyTelegramListener → Last Run Result. If disabled/failed, re-enable. Or tell Andy "fix the watchdog" and Mack will diagnose + restore auto-start.

---

### [BUILDAR-LOVABLE-CMS] Lovable CMS — ready when you're at the computer
**Context (2026-05-17):** Inon away today; Andy in autonomous mode on BuildAR. Lovable CMS requires interactive steps (sign-in, paste prompt, connect Supabase).
**Two options — pick when at desk:**
1. **Sequential (RECOMMENDED for first attempt):** `owner_inbox/buildar/lovable_sequential_prompts.md` — 5 paste-and-review cycles. You see what's being built at each step, can course-correct mid-way. ~90-150 min total.
2. **Single-prompt (faster, less control):** `owner_inbox/buildar/lovable_handoff_ready.md` — one big prompt builds the whole CMS in one Lovable pass. ~60-90 min total.
**Both reference:** Phase B SQL must be live first (Silas's 2 SQL blocks in `agents/andy/inbox/silas_phase_b_done.md`).

---

### [BUILDAR-SPRINT-1] Sprint 1 / Gate B — CODE COMPLETE, awaiting your authorization
**Status as of 2026-05-17 end-of-autonomous-run:**

All 4 branches are MERGE GREEN on local `D:\BuildAR\` (NOT pushed):
- `feat/orchestrator-mvp` — Wave 1 (ai-client + telemetry) — Jasmin PASS WITH NOTES
- `feat/phase-b-prereqs` — Migrations 0004 (FK) + 0005 (storage bucket) — Jasmin PASS (cherry-pick the 2 files into a clean branch for the PR; Yoni's S1-006 baseline polluted this branch from a parallel-agent incident)
- `feat/events-schema-alignment` — Migration 0006 (events alignment + sessions.current_step_id) — Jasmin PASS WITH NOTES
- `feat/mobile-shell` — 5 screens + WCAG-AA compliant + 35/35 tests + MINOR-1 hotfix bundled — Vera HOLD → Yoni fix → Jasmin re-verify → GREEN

**Your sequence of action items when at the desk (rough order):**

1. **URGENT — Rotate Telegram bot token via @BotFather.** Token leaked via public repo; external poller has been hijacking /continue. Step 1 is BotFather-only. Then Mack will scrub + restart. (See `tasks/active_tasks.json` → TELEGRAM-TOKEN-ROTATE-2026-05-17 for full notes.)

2. **Paste 3 SQL blocks into Supabase SQL Editor** (in order: 0004 → 0005 → 0006; 0004 is idempotent no-op if 0003 already applied):
   - SQL block #1 (0004 FK ON DELETE) + #2 (0005 storage bucket) — both in `agents/andy/inbox/silas_phase_b_done.md`
   - SQL block (0006 events alignment) — in `agents/andy/inbox/silas_s1_010_done.md`
   - Run verification queries in each report after pasting. Confirm expected output matches.

3. **Drop ANTHROPIC_API_KEY into `D:\BuildAR\.env`** — same key you use for Claude Code. Without it, Yoni's live /assist curl can't run as final S1-008 verification.

4. **Drop SUPABASE_ANON_KEY into `D:\BuildAR\apps\mobile\.env`** — copy from `.env.example`, paste real anon key from Supabase Dashboard.

5. **Authorize the 4-branch merge to main + push to GitHub** — I didn't auto-push (shared-state needs your sign-off). When ready, either:
   - Cherry-pick + open 4 PRs manually
   - Or tell me to dispatch Mack to push the branches and open the PRs

6. **Lovable CMS (when ready)** — two ways to consume:
   - **SEQUENTIAL (recommended for visibility into each step):** `owner_inbox/buildar/lovable_sequential_prompts.md` — 5 paste-and-review prompts with explanations
   - **SINGLE-PROMPT (faster):** `owner_inbox/buildar/lovable_handoff_ready.md` — all-in-one
   - Pre-flight requires SQL blocks 0004 + 0005 to be applied first (step 2 above)

7. **Optional Phase 2 follow-ups (deferred, not blocking):**
   - Android emulator boot verification — requires Android Studio + SDK on host (30-90 min)
   - iOS native build — requires macOS + Xcode
   - HomeScreen resume banner — client-side cache or new `GET /sessions?status=active` route
   - Migration 0006 backfill edge-case investigation (Jasmin's S1-010 review §C minor)
   - NIT-1 + NIT-2 doc comments (Silas skipped because target files weren't on main; can land after Yoni's S1-008/009 branch merges)

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

~~### [WEBSITE-001-SEC-01] Remove Base44 platform badge~~
~~**Action:** base44.app → app settings → disable platform badge.~~
**Status:** DONE — Fixed by Inon on Base44 directly — 2026-05-18.

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
