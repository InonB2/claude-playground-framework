# Autonomous Agentic Framework — v2.2

> **14 active agents. SQLite memory. Telegram bridge. CV archive. GitHub sync.**

---

## Quick Navigation

| Directory       | Index                          | Purpose                                               |
|-----------------|--------------------------------|-------------------------------------------------------|
| `/agents/`      | [agents/INDEX.md](agents/INDEX.md) | All 14 agent personas and delegation map          |
| `/BKM/`         | [BKM/INDEX.md](BKM/INDEX.md)       | Standard Operating Procedures (6 SOPs)            |
| `/skills/`      | [skills/INDEX.md](skills/INDEX.md) | Reusable skill registry (LYRA prompting, etc.)    |
| `/tasks/`       | [tasks/active_tasks.json](tasks/active_tasks.json) | Live task queue               |
| `/memory/`      | [memory/session_log.db](memory/session_log.db)    | SQLite activity log           |
| `/owner_inbox/archive/` | [owner_inbox/archive/](owner_inbox/archive/) | CV versions + approved deliverables |
| `/scratchpad/`  | *(ephemeral)*  | Temporary drafts and intermediates                    |
| `/team_inbox/`  | *(drop zone)*  | Raw inputs from Owner for Andy to scan                |
| `/owner_inbox/` | *(approval gate)* | Approved items awaiting Owner sign-off             |
| `/owner_inbox/archive/` | *(final)*      | Owner-approved deliverables                           |
| `/scripts/`     | —              | Automation scripts (CV generator, Telegram bot, sync) |

---

## Active Agents (14)

| Name   | Role                   | Key Skill                                            |
|--------|------------------------|------------------------------------------------------|
| Andy   | Orchestrator           | Decomposes goals, delegates, runs the pipeline       |
| Tomy   | Researcher             | Knowledge briefs, API/doc exploration                |
| Yoni   | Lead Coder             | Clean React/TS implementation, unit tests            |
| Jasmin | Reviewer               | Security audit, deployment gate                      |
| Pat    | HR Researcher          | Agent blueprinting and candidate profiles            |
| Nolan  | HR Agent               | Deploys new agents, updates roster                   |
| Maya   | Web Security Auditor   | OWASP, header analysis, PII exposure                 |
| Lena   | UI/UX Designer         | Design systems, awwwards-level visual specs          |
| Rex    | Web Developer          | GSAP, Lenis, React, Base44 implementation            |
| **Mack**  | Automation Engineer | Telegram bot, GitHub sync, webhook wiring            |
| **Sage**  | LinkedIn Strategist | Personal brand content, thought leadership           |
| **Cole**  | Conversion Copywriter | CVs, cover letters, website copy                  |
| **Silas** | Database Architect  | SQLite/Supabase schema, pgvector, migrations         |
| **Vera**  | QA Inspector        | Responsive QA, WCAG 2.1, Lighthouse                  |

---

## Setup Instructions

### 1. Telegram Bot (WhatsApp alternative — free, no Twilio needed)

**One-time setup (5 minutes):**
1. Open Telegram → search `@BotFather` → type `/newbot` → follow prompts
2. Copy your **Bot Token**
3. Start a chat with your new bot, send any message
4. Run: `python scripts/telegram_bot.py --get-chat-id`
5. Copy your **Chat ID**
6. Create `.env` file in project root:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```
7. Run: `python scripts/telegram_bot.py`

**What it does:**
- Notifies you when Andy processes a new item → `/team_inbox/`
- Sends approval requests when Jasmin moves work → `/owner_inbox/`
- Drop any message to the bot → automatically filed in `/team_inbox/`
- Reply `APPROVE filename.md` → moves to `/owner_inbox/archive/`
- Type `/status` → see inbox counts

---

### 2. GitHub Sync

**Repo:** [github.com/InonB2/claude-playground-framework](https://github.com/InonB2/claude-playground-framework) (already live)

**Manual sync (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File "scripts\github_sync.ps1"
```

**Daily auto-sync:** Active via Claude scheduled task (runs 9:00 AM daily)

---

### 3. CV Archive

**Generate a new CV:**
```bash
# Copy scripts/generate_elbit_cv.py and adapt for the new role
python scripts/generate_elbit_cv.py
```

**Log a new application:**
```python
import sqlite3
conn = sqlite3.connect("owner_inbox/archive/cv_archive/cv_archive.db")
conn.execute("""INSERT INTO applications (...) VALUES (...)""")
conn.commit()
```

---

## Agent Protocol

**Before every action:**
1. Read `/agents/roster.md` (Andy always first)
2. Query `/memory/session_log.db`
3. Read task from `/tasks/active_tasks.json`
4. Read relevant SOPs from `/BKM/`

**After every action:**
- Log to `/memory/session_log.db`
- Update task status
- Tag the next agent

**LYRA prompting:** Apply [`/skills/lyra_prompting.md`](skills/lyra_prompting.md) on every complex or ambiguous request.

---

## Activate the Team

```
I have a new objective: [INSERT TASK].
Andy — read the roster, decompose, and initiate the pipeline.
```

## Hire a New Agent

```
Andy, we need a specialist for [capability].
Initiate the recruitment pipeline with Pat and Nolan.
```
