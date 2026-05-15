# Mack — AI News Scanner + Task Sync Scanner — DONE

**Date:** 2026-05-15
**Agent:** Mack
**Status:** Both routines built, scheduled, and verified by manual run.

---

## TL;DR

Two daily Python scripts wired into Windows Task Scheduler:

| Routine | Script | Schedule (Asia/Jerusalem) | Output |
|---|---|---|---|
| AI News Scanner | `scripts/ai_news_scan.py` | Daily **09:00** | `owner_inbox/research/ai_news_daily.md` (+ monthly archive) |
| Task Sync Audit | `scripts/task_sync_scanner.py` | Daily **08:00** | `agents/andy/inbox/task_sync_audit_YYYY-MM-DD.md` |

Both scheduled tasks created and verified: `AndyTeam_AINewsScan` (Next Run 2026-05-16 09:00) and `AndyTeam_TaskSyncScan` (Next Run 2026-05-16 08:00).

---

## Routine 1 — AI News Scanner

### Files
- **Script:** `D:\Claude Playground\scripts\ai_news_scan.py`
- **Daily output:** `D:\Claude Playground\owner_inbox\research\ai_news_daily.md`
- **Archive (auto-created):** `D:\Claude Playground\owner_inbox\research\ai_news_archive_YYYY-MM.md`

### Sources scanned (15)
- **Anthropic / Claude:** anthropic.com/news (×2 — also acts as Release Notes)
- **OpenAI / ChatGPT / Codex:** openai.com/news, openai.com/research
- **Google / Gemini:** deepmind.google/discover/blog, blog.google/technology/ai
- **xAI / Grok:** x.ai/news
- **Perplexity:** perplexity.ai/hub/blog
- **OpenCog** (best-effort interpretation of "OpenClaw"): opencog.org/category/blog
- **Other LLMs:** Mistral AI news, Meta AI blog, Cohere blog
- **Claude Code ecosystem:** docs.claude.com/release-notes/claude-code, MCP servers GitHub releases, MCP spec GitHub releases

If "OpenClaw" was meant literally and isn't OpenCog, please clarify and I'll swap the source.

### Sample first-run output (manual)
Excerpt from today's `ai_news_daily.md` (full file is 90 lines):

```
## 2026-05-15 (Asia/Jerusalem)

_Sources scanned: 15 — succeeded: 13, failed: 2_

### Anthropic / Claude
- **Anthropic — News** (https://www.anthropic.com/news)
  - [Introducing Claude Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7) — Our latest Opus model brings stronger performance across coding, agents, vision, and multi-step tasks...
  - [Introducing Claude Design by Anthropic Labs](https://www.anthropic.com/news/claude-design-anthropic-labs) — Today, we're launching Claude Design...

### Google / Gemini
- **Google DeepMind — Blog** (https://deepmind.google/discover/blog/)
  - [Reimagining the mouse pointer for the AI era](https://deepmind.google/blog/ai-pointer/)
  - [AlphaEvolve: How our Gemini-powered coding agent is scaling impact across fields](...)

### xAI / Grok
- **xAI — News** (https://x.ai/news)
  - [New Compute Partnership with Anthropic](https://x.ai/news/anthropic-compute-partnership)
  - [Connectors in web, iOS, and Android](https://x.ai/news/grok-connectors)

### Other LLMs
- **Mistral AI — News** (https://mistral.ai/news/)
  - [Introducing Mistral Medium 3.5, remote coding agents in Vibe, plus new Work mode in Le Chat...]
- **Meta AI — Blog** — [fetch failed: HTTP 400](https://ai.meta.com/blog/)
```

13/15 sources succeeded; Meta AI returned HTTP 400 (likely WAF/cookie check) and OpenCog/blog returned 404. Both failures are logged inline — never abort the run. Note: a couple of high-signal sources (Anthropic news, DeepMind, xAI, Mistral, Perplexity) extracted real titles + excerpts; a few noisier pages (OpenAI News, Cohere) fell through to "link only". This is fine for a daily digest — Tomy or Inon can click through if a card looks interesting.

### Schedule mechanism — chosen: Windows Task Scheduler

I chose **Windows Task Scheduler** over claude.ai/code/routines for this one because:
1. Output is to the local repo on this Windows box. A remote routine running on Anthropic's side has no write access to `D:\Claude Playground\` — it would need a roundtrip through a webhook + a local listener. Pure local scheduling is one moving part.
2. The FamilyFlow keep-alive routines were remote because the *target* (Supabase MCP) is remote. Here the target is the local filesystem.
3. No outbound webhook, no claude.ai dashboard editing — easy to inspect/disable with `schtasks`.

Registered as:
```
schtasks /Create /TN AndyTeam_AINewsScan ^
  /TR "\"C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\python.exe\" \"D:\Claude Playground\scripts\ai_news_scan.py\"" ^
  /SC DAILY /ST 09:00 /F
```

Verified: Status=Ready, Next Run Time=16/05/2026 9:00:00. System timezone confirmed `(UTC+02:00) Jerusalem` — Israel Standard Time — so 09:00 local == Asia/Jerusalem 09:00.

### LinkedIn-tab integration spec for Rex (DO NOT wire — Rex owns the file)

Inon asked the dashboard's LinkedIn tab to surface the top 3–5 AI news entries as a "Post idea source" panel. I deliberately did **not** edit `dashboard/index.html` because Rex is currently in there (lesson from JOBSEARCH-006 worktree-glitch).

**Spec for Rex** (drop into a follow-up task as `LINKEDIN-NEWS-FEED-001`):

1. **Add a section to the LinkedIn tab**, placed above the post pipeline, titled **"Post idea source — today's AI news"**.
2. **Data source:** read `owner_inbox/research/ai_news_daily.md` via `fetch()` (the dashboard already runs against a local server per CAREER-DASH-001 notes, so a relative fetch works).
3. **Parsing:** the file has a stable top-block format starting with `## YYYY-MM-DD (Asia/Jerusalem)`. Take only the first day-block (everything from the first `## ` until the next `## ` or EOF).
4. **Display:** for each `### Group` under that block, render a card with the group name and the first 1–2 bullets. Cap total at **5 cards** to match Inon's "3-5 entries" request.
5. **Each card** should have an "Use as post draft" button that prefills a new LinkedIn post item with `{title: bullet.title, source_url: bullet.link, language: "he", status: "draft"}` — same shape Rex already uses for the LinkedIn pipeline (per CAREER-DASH-001 + LINKEDIN-001 dashboard updates).
6. **Refresh:** auto-refresh on tab activation (cheap — single file read).
7. **Empty state:** if `ai_news_daily.md` is missing or the parser finds zero blocks, show "No news scan yet — runs daily at 09:00." (do not error).
8. **XSS guard:** mandatory — these are external titles. Use the existing `escHtml` helper Rex used in DASH-SYNC-001.

If Rex prefers JSON over markdown for stability, I can add a `--json` flag to `ai_news_scan.py` that writes a parallel `ai_news_daily.json` — flag me and I'll ship in <30 min.

### Findings — Infrastructure
- **Python runtime:** `python.exe` is the Windows Store wrapper at `C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\python.exe`. Tested OK with `requests==2.33.1` and `beautifulsoup4==4.14.3` — both already installed.
- **Timezone:** confirmed `(UTC+02:00) Jerusalem`, so local-time schedule == required schedule.
- **Username with space:** the path `C:\Users\Inon Baasov\...` is quoted in the schtasks command line — no PATH-with-spaces bug like the Telegram MCP one (TELEGRAM-001).
- **Output dir:** `owner_inbox/research/` already exists and is in active use (anthropic_news.md, codex_news.md, gemini_news.md, perplexity_news.md). The new `ai_news_daily.md` does **not** overwrite those — they are separate, hand-curated files.

### Findings — Design
- **Single-pass each source:** one HTTP fetch per source per day with 0.8 s spacing — respectful, well under any sane rate limit.
- **Two fallback layers per source:** (a) preferred CSS-selector extraction → (b) page-title link → (c) inline `[fetch failed: <reason>]` message. Run never aborts; partial data is the norm.
- **Rotation built in:** the daily file keeps last 7 days and auto-archives older days to `ai_news_archive_YYYY-MM.md`. No unbounded file growth.
- **Idempotent:** running twice the same day replaces today's block; doesn't double up. (Tested by running scan twice in dev.)
- **Tradeoff accepted:** some sources (OpenAI News, Cohere) extract noisy items. Inon said "don't over-engineer — dump excerpt + link." I followed that — but the LinkedIn-feed for Rex defaults to *first 1–2 bullets per group*, which favors the cleaner top-of-list items.

### Malfunction + prevention plan
| What could break | How the routine handles it | Prevention going forward |
|---|---|---|
| A vendor changes their HTML structure (e.g., DeepMind moves to a JS-rendered SPA) | Source falls through to "link only"; never crashes | Daily report always shows succeeded/failed count at top — Inon sees the regression within 24 h |
| Network timeout / rate-limit | `requests` 12 s timeout, source marked `[fetch failed: <reason>]` | Sleep between fetches; no parallel hammering |
| Disk full / write fails | Python raises; schtasks logs non-zero exit | Status will show in `schtasks /Query` with Last Result != 0 — Andy's morning audit catches it |
| Two runs collide (manual + scheduled) | Atomic single-write per file; idempotent | N/A — last writer wins, both writes produce equivalent content for the same day |
| Stale source URLs over time | Will show as `[fetch failed]` consistently | Quarterly Mack review (added to my learning log) |

---

## Routine 2 — Task Sync Scanner

### Files
- **Script:** `D:\Claude Playground\scripts\task_sync_scanner.py`
- **Daily output:** `D:\Claude Playground\agents\andy\inbox\task_sync_audit_YYYY-MM-DD.md`

### What it does
For each task in `tasks/active_tasks.json` with status in `{pending, in-progress, partial, pending-owner, pending-restart, blocked, in_progress}`:
1. Greps last **80** git commit messages for the task_id and for keyword overlap with the title
2. Greps last **21 days** of files in `agents/andy/inbox/` for the same
3. Scans the task's `notes` field for `COMPLETED YYYY-MM-DD` / `DELIVERED` / `SHIPPED` markers
4. Scores each task and buckets into:
   - **looks done — Andy should review and close** (high/medium confidence)
   - **status might be wrong — weaker evidence** (low confidence)
5. Writes a markdown report. **Does NOT modify `active_tasks.json`** (auto-edits = too risky).

### Sample first-run output (manual, 2026-05-15)

Full report at `agents/andy/inbox/task_sync_audit_2026-05-15.md`. Highlights:

- Tasks scanned: **37** (open: **14**)
- Looks-done: **5** — all but one are HIGH confidence
- Uncertain: **8**

The high-confidence catches are exactly the kind Inon flagged:
- `ELBIT-SYSENG-001`, `ELBIT-TPM-001`, `LENOVO-INC-001` — notes say "COMPLETED 2026-05-XX" but status is still `pending-owner`
- `LINKEDIN-001` — task_id literally appears in a commit (`9ddddf446e99 feat(cv-scale): ... LinkedIn post draft`) plus matching inbox QA file
- `FINN-ONBOARD-001` — matches `pat_infra_triage_profile_done.md` (note: this is a related-but-distinct task — Pat scoped Finn, Finn still needs to write his own SOP — likely a FALSE POSITIVE; this is exactly the kind of thing Inon wanted Andy, not the scanner, to judge)

The Base44 badge case (`WEBSITE-001-SEC-01`) that originally motivated this routine is **already marked done** — not an open task today — so it correctly doesn't appear in this run. But the same detection logic would have caught it: the notes field contained `COMPLETED 2026-05-09` while the JSON status was still pending.

### Schedule mechanism — chosen: Windows Task Scheduler
Same reasoning as Routine 1 — the input and output are both local files in this repo.

Registered as:
```
schtasks /Create /TN AndyTeam_TaskSyncScan ^
  /TR "\"C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\python.exe\" \"D:\Claude Playground\scripts\task_sync_scanner.py\"" ^
  /SC DAILY /ST 08:00 /F
```

Verified: Status=Ready, Next Run Time=16/05/2026 8:00:00. I also triggered a `schtasks /Run` to confirm it executes cleanly under the scheduler.

### Findings — Infrastructure
- **active_tasks.json is currently malformed** — line 272 has a stray `{` that breaks `json.load()`. The scanner detects this and falls back to a tolerant regex parser (extracts task_id / title / status / notes / assigned_to per task). **This is a latent bug Andy should fix in the JSON** — a clean parse will let other downstream tooling consume the file. Repro: `python -c "import json; json.load(open('tasks/active_tasks.json'))"` → JSONDecodeError at line 272.
- **Git access:** runs `git log` via subprocess from repo root. Works fine for local dev; would need adjustment if scheduled task ran from a non-git context — already pinned to `cwd=ROOT`.
- **Inbox directory has 36 files within the last 21 days** — meaningful signal density.

### Findings — Design
- **READ-ONLY by design.** The scanner produces a report; Andy decides what to close. False positives are cheap — Inon just ignores them.
- **Confidence buckets, not booleans.** High/medium go in the "review and close" section; low go in "might be wrong" — Andy can skim or skip the latter.
- **Multi-signal scoring.** Most weight is on (a) explicit `COMPLETED` markers in notes (+4) and (b) literal task_id in commits/inbox (+3 each). Keyword overlap is a tiebreaker (+1 or +2). This is why the 4 CV/LinkedIn tasks ranked HIGH while the inbox-keyword-only matches stayed weak.
- **Stop-word list** keeps generic words ("task", "fix", "agent") from creating noise.
- **Suppression hook:** the report mentions a `sync_audit_ignore: true` JSON field. I documented but did NOT wire enforcement — the scanner currently scans everything. Wire enforcement if false positives become noisy; the read+respect logic is a 4-line change in `audit()`.

### Malfunction + prevention plan
| What could break | How the routine handles it | Prevention going forward |
|---|---|---|
| `active_tasks.json` malformed (today's case!) | Tolerant regex parser kicks in; logs the failure to stderr | Andy can fix the stray `{` at line 272 once; structural malformations remain detectable |
| Task_id collision with unrelated commit text | Keyword scoring degrades confidence to LOW; report says "might be wrong" | Andy uses the cited commit/inbox file to verify before flipping status |
| Inbox has report for adjacent-but-not-this task (FINN false-positive above) | Confidence drops to MEDIUM; Andy reads the cited file before acting | This is the intended workflow — scanner suggests, Andy judges |
| Scanner runs but writes nothing | Non-zero exit; schtasks logs Last Result != 0 | Daily inbox check from Andy — if no `task_sync_audit_YYYY-MM-DD.md`, look at schtasks |
| Owner mistakenly thinks scanner auto-closes tasks | Big banner: "**This report is read-only: no task statuses were modified.**" | Explicit in script docstring + report header + this report |

---

## Verification evidence

Manual smoke runs from 2026-05-15:

```
$ python scripts/ai_news_scan.py
[ai-news-scan] 2026-05-15 - scanning 15 sources
[ai-news-scan] done - 13/15 succeeded
[ai-news-scan] wrote D:\Claude Playground\owner_inbox\research\ai_news_daily.md

$ python scripts/task_sync_scanner.py
[task-sync] JSON parse failed (Expecting property name enclosed in double quotes at line 272); attempting tolerant parse
[task-sync] tolerant repair failed; falling back to regex extraction
[task-sync] wrote D:\Claude Playground\agents\andy\inbox\task_sync_audit_2026-05-15.md
[task-sync] looks-done: 5, uncertain: 8
```

`schtasks /Run /TN AndyTeam_TaskSyncScan` returned SUCCESS with Status=Ready. Both tasks show Next Run Time tomorrow at the requested local times.

---

## Suggested follow-ups (do NOT block on these)

1. **Fix the stray `{` at `tasks/active_tasks.json:272`.** A clean parse helps every downstream tool, not just this scanner.
2. **Have Rex wire the LinkedIn integration** per the spec above — single task, isolated edit, no shared-file conflict risk.
3. **(Optional)** add `--json` output to `ai_news_scan.py` if Rex prefers structured input over markdown parsing.
4. **(Optional)** wire the `sync_audit_ignore: true` field into the scanner once Andy has triaged the first week of reports and seen which tasks generate repeat false positives.

---

**Did not commit to git** per Inon's instruction. Andy can review and commit when ready.

— Mack
