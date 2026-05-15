# Jasmin — QA of Mack's Two Automation Routines

**Date:** 2026-05-15
**Agent:** Jasmin
**Scope:** Code review + run verification + scheduling + per-hit triage of the first task-sync audit
**Subject:** `scripts/ai_news_scan.py` and `scripts/task_sync_scanner.py` (Mack, 2026-05-15)

---

## Verdict: **PASS WITH NOTES**

Both scripts are well-built, run cleanly, and are safely scheduled. No security issues, no script-crashing bugs, no write-anywhere paths, no injection vectors. The scanner's first audit is **mostly correctly catching real signal**, but a meaningful nuance about the `pending-owner` lifecycle state is worth Andy's attention (details in §3).

Three small-to-medium notes (none blocking):
- AI news scanner uses a browser-mimicking UA, doesn't check robots.txt, no retry/backoff.
- Both scheduled tasks are **"Interactive only"** logon mode → they will not fire if the user is logged off at 08:00 / 09:00. Worth flipping to "Run whether user is logged on or not" if Inon wants guaranteed daily runs.
- The "stray `{` at line 272" issue Mack reported in `active_tasks.json` is **no longer present** — JSON parses cleanly today; the tolerant fallback path didn't trigger on my run. Andy or someone fixed it between Mack's run and mine. Tolerant fallback is still good defensive code to keep.

---

## 1) Code review — Infrastructure

### ai_news_scan.py
| Check | Finding |
|---|---|
| Shell injection / subprocess | None — no subprocess calls |
| File-write safety | All writes pinned under `ROOT/owner_inbox/research/`; archive filename derived from `\d{4}-\d{2}-\d{2}` regex match → no path traversal |
| Credentials / secrets | None — fully public sources |
| Network politeness | 12 s timeout, 0.8 s sleep between sources, single fetch per source per run |
| User-Agent | `Mozilla/5.0 … Chrome/123.0 Safari/537.36 ai-news-scan/1.0` — identifies itself at the end, but mimics a desktop browser. **Acceptable but not maximally polite.** Best practice: prefer `ai-news-scan/1.0 (https://github.com/InonB2/claude-playground-framework)` or include an email. |
| robots.txt | Not checked. None of the 15 sources have hostile policies for low-rate access, but if Mack adds more sources we should consider `urllib.robotparser` |
| HTML parser | `BeautifulSoup(html, "html.parser")` — stdlib, no XXE / XML expansion risk |
| Error handling | Per-source try/except catches `RequestException` + broad `Exception`; one source down ≠ script crash. Verified: my run got HTTP 404 (OpenCog) and HTTP 400 (Meta AI) both surfaced inline, run exited 0 |
| Python dependencies | `requests` 2.33.1, `beautifulsoup4` 4.14.3 — both current, no known CVEs |
| Disk pressure | Daily file rotates at 7 days, archives roll into monthly files — no unbounded growth |
| Idempotency | Re-running same day replaces today's block via `blocks = [(d,b) for ... if d != today]` — verified |

### task_sync_scanner.py
| Check | Finding |
|---|---|
| Shell injection / subprocess | `subprocess.run(["git", "log", ...])` — list-form args, no shell, no injection |
| File-write safety | Single write to `INBOX_DIR / f"task_sync_audit_{today.isoformat()}.md"` — pinned, date-formatted |
| Credentials / secrets | None |
| JSON parse robustness | Three-tier: strict → strip-stray-`{` → regex-extract per task. Solid defensive design |
| Bounded reads | Inbox preview capped at 400 chars; git log capped at 80 commits — no memory blowup |
| Regex DoS | All patterns bounded by literal anchors or character classes; no nested quantifiers — no ReDoS risk |
| Side effects | Read-only on `active_tasks.json` — explicit design choice. Only writes the report file |
| `tasks/active_tasks.json` today | Parses cleanly via `json.loads` — Mack's repair path did not trigger. Tolerant code is still valuable for future malformations |

---

## 2) Code review — Design

### ai_news_scan.py
- **Two-tier extraction (CSS selector → page-title fallback)** is the right call for a scraper across 15 heterogeneous sources. Failures degrade to "link only" rather than empty cards — Inon still sees that the source was alive.
- **Group-aware rendering** keeps the digest readable; sorted group order keeps day-to-day diffs minimal.
- **Trailing sleep in `scan_all`** — there's a 0.8 s sleep *after* the last source too. Tiny waste (<1 s), cosmetic only.
- **Generic-fetch sources (OpenCog, GitHub Releases)** produce only the page title; that's fine for an at-a-glance digest. If Inon wants richer GitHub data, the GitHub API would beat HTML scraping (no auth needed for public release lists).
- **"OpenClaw" interpretation as OpenCog** is Mack's best guess. Inon should confirm; if "OpenClaw" was a typo for something else, swap the source.
- **No retry/backoff** — single attempt per source. For a daily digest this is fine; one missed day per source is not material. Not worth adding.

### task_sync_scanner.py
- **Multi-signal scoring (commits, inbox, notes-marker, keyword overlap)** is the right approach. Notes-marker `COMPLETED YYYY-MM-DD` correctly gets the highest weight (+4) — that's the most reliable signal.
- **Stop-word list** filters out the usual culprits ("task", "fix", "agent"); good.
- **Confidence bucketing** (high ≥5, medium ≥3, low <3) gives Andy a triage gradient instead of binary flags.
- **`pending-owner` blind spot** — see §3. The scanner treats `pending-owner` and `pending` identically when looking for "looks done" signals. But `pending-owner` is a *deliberate* waiting state for Inon-action. Today, 4/5 high-conf hits are `pending-owner` and the scanner is catching real work-completion. Suggested design tweak: weight `pending-owner` hits differently (e.g., a separate report section "Owner action awaited — agent work confirmed delivered"), so Inon sees them as a batch.
- **`sync_audit_ignore` field** is documented but unenforced. Acceptable; wire it up only if false positives compound.
- **Read-only by design** — correct. Auto-flipping statuses based on heuristics would be a disaster.

---

## 3) Per-hit verification of the 5 "looks done" tasks

I checked each cited file/commit independently.

| # | Task ID | Scanner verdict | My verdict | Evidence |
|---|---|---|---|---|
| 1 | `ELBIT-SYSENG-001` | high | **TRUE POSITIVE (agent work) / NEEDS ANDY REVIEW (lifecycle)** | CV file `v1_Inon_Baasov_CV_SystemEngPM.html` exists in `owner_inbox/archive/cv_archive/ELBIT-SystemEng-PM-Netanya/`, plus v2 and v3. Notes say `COMPLETED 2026-05-10`. Cole's work is genuinely done. Status `pending-owner` means awaiting Inon's review/submission, which is a valid state — not "wrongly open". Andy should decide whether `pending-owner` collapses to `done` once Cole's work is QA-approved, or stays as a distinct "waiting on Inon" bucket. |
| 2 | `ELBIT-TPM-001` | high | **TRUE POSITIVE (agent work) / NEEDS ANDY REVIEW (lifecycle)** | CV v1/v2/v3 exist in `owner_inbox/archive/cv_archive/20248_TechnicalPM_Elbit_Netanya/`. Notes say `COMPLETED 2026-05-06`. Same `pending-owner` semantics as above. |
| 3 | `LENOVO-INC-001` | high | **TRUE POSITIVE (agent work) / NEEDS ANDY REVIEW (lifecycle)** | CV `v1_Inon_Baasov_CV_IncubationPM.html` + PDF exist in `owner_inbox/archive/cv_archive/LENOVO-CTO-IncubationPM/`. **Note:** this folder is currently **untracked in git** (per session-start `git status`) — so the work was delivered but not committed yet. Andy should commit + close once Inon greenlights. |
| 4 | `LINKEDIN-001` | high | **TRUE POSITIVE (agent work) / NEEDS ANDY REVIEW (lifecycle)** | `owner_inbox/posts/linkedin_ai_news_2026-05-14.md` exists; Vera QA PASS 8/8 per notes. Sage delivered the new batch on 2026-05-14. Status `pending-owner` correctly reflects "awaiting Inon's approval to publish". |
| 5 | `FINN-ONBOARD-001` | medium | **FALSE POSITIVE** | The scanner matched on inbox file `pat_infra_triage_profile_done.md`, which documents **Pat's profile of Finn's role**, not Finn writing the SOP. I verified `BKM/sop_infra_triage.md` **does not exist** (only `sop_web_security.md`, `sop_web_design.md`, `sop_web_development.md`, `sop_cv_management.md`, `sop_session_logging.md`, `sop_onboarding.md`, `writing_style.md`, `INDEX.md` are in BKM/). Task correctly remains `pending`. Mack flagged this risk in his own report — the scanner's design intent is that the medium-confidence tier catches such adjacency cases; this is working as designed. |

### Pattern observation for Andy

4 of 5 high-confidence hits are `pending-owner` tasks where agent work is genuinely complete. This isn't scanner noise — it reflects a real backlog of "Inon, please approve/submit" items. Specifically:
- 3 Elbit/Lenovo CVs ready for Inon to send out
- 1 LinkedIn batch ready for Inon to approve and publish

Andy should consider creating a daily **"Owner action queue"** section in the C&C dashboard sourced from `tasks where status == pending-owner`. The scanner's value is then: catch tasks that *should* be `pending-owner` but are still mislabeled `pending` / `in-progress`. Today's run found one of those (LINKEDIN-001 is correctly `pending-owner` and the scanner agreed via task_id match in commit) and three that have proper `pending-owner` status — those are not drift, they are real owner-waiting items.

---

## 4) Schedule mechanism verification

`schtasks /Query /TN AndyTeam_AINewsScan` and `/TN AndyTeam_TaskSyncScan` — both **registered and Ready**.

| Task | Status | Next Run | Last Run | Last Result | Concern |
|---|---|---|---|---|---|
| `AndyTeam_AINewsScan` | Ready | 16/05/2026 09:00 | 30/11/1999 (never) | 267011 ("task has not yet run") | Has not yet hit its first scheduled run; expected, since it was registered today after 09:00 |
| `AndyTeam_TaskSyncScan` | Ready | 16/05/2026 08:00 | 15/05/2026 11:42:25 | **0 (success)** | Verified clean exit via Mack's manual `schtasks /Run` trigger |

Both use:
- `Run As User: Inon Baasov`
- `Logon Mode: Interactive only` → **WILL NOT RUN if the user is logged off.**
- `Stop On Battery Mode: Yes` → will not start if the laptop is on battery
- `Schedule Type: Daily, every 1 day`

### Note for Inon — power/logon coverage
If the laptop is closed or you're logged out at 08:00 / 09:00, both tasks silently skip. For Inon's use case this is probably fine — he uses this machine daily — but if a reliable daily run matters (especially the news scan), one of:
- Flip Logon Mode to "Run whether user is logged on or not" (requires storing password; needs admin)
- Add a catch-up trigger so the task fires at login if a scheduled run was missed
- Move the routine to a cloud-hosted GitHub Action triggered on cron (would lose the local-filesystem advantage Mack chose)

Recommended: keep current setup; add catch-up trigger via `schtasks /Change /TN ... /MO ...` if Andy sees a daily-output gap in the first 2 weeks of running.

---

## 5) Manual runs — verification log

```
# Both invoked from D:\Claude Playground
$ python scripts/ai_news_scan.py --dry-run
[ai-news-scan] 2026-05-15 — scanning 15 sources
[ai-news-scan] done — 13/15 succeeded
(produces 90-line markdown block; failures: OpenCog 404, Meta AI 400 — both inline)
Exit code: 0

$ python scripts/task_sync_scanner.py --stdout
(stderr is silent today — strict JSON parse succeeded; no tolerant-fallback path needed)
(produces 64-line audit; matches Mack's earlier output structurally)
Exit code: 0
```

The task_sync audit file written by Mack (`task_sync_audit_2026-05-15.md`) matches my re-run output for the 5 high-confidence findings; my fresh run shows 38 inbox files (Mack saw 36) and 22 commits inspected — both within expected drift from new files landing today.

---

## 6) Malfunction + prevention plan (Jasmin standard)

| Scenario | Coverage today | Prevention |
|---|---|---|
| Vendor site changes HTML structure | Falls through to generic title-link | Mack's planned quarterly review; the daily "succeeded N/M" line surfaces regressions in 24 h |
| `active_tasks.json` regresses to malformed | Tolerant 3-tier parser kicks in | Jasmin recommends: add a lightweight `python -m json.tool tasks/active_tasks.json` precommit check; Yoni can wire as a hook |
| Network outage during scheduled run | Per-source error caught; run completes with whatever it got | OK as-is for daily digest |
| Scheduled task silently skipped (logged out / on battery) | NOT caught today | Add catch-up trigger if daily gaps appear; or have a weekly `git log --grep="ai_news_daily"` check to confirm file is being updated |
| Scanner produces false-positive that gets Andy to close a real open task | Confidence bucketing + cited evidence per finding; Andy reads cited files before acting | Already in scanner design via "How to use this report" section + per-task evidence list |
| Mack-style "first audit shows 5 hits, all false alarms" pattern | Scanner remains read-only, no auto-action | OK — Andy filters, false positives are cheap |

---

## 7) Summary recommendations for Andy

**No blockers. Both scripts can stay live.**

Strongly suggested follow-ups (not blocking):
1. **Triage the 4 `pending-owner` hits today.** All four (ELBIT-SYSENG-001, ELBIT-TPM-001, LENOVO-INC-001, LINKEDIN-001) have real deliverables sitting in `owner_inbox/`. Inon needs to look at them this week.
2. **Commit the Lenovo CV folder** (`owner_inbox/archive/cv_archive/LENOVO-CTO-IncubationPM/`) — currently untracked.
3. **Decide on `pending-owner` semantics** team-wide: is it a state the scanner should ignore, or should the scanner have a separate "owner-action queue" section?
4. **Optional UA tweak** on `ai_news_scan.py`: add the repo URL to the user-agent string for politeness if Mack ever scales sources past 15.
5. **Optional**: flip Task Scheduler logon mode if missed runs appear in the first two weeks.

— Jasmin
