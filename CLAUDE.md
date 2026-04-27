# Autonomous Agentic Framework — v2.2

This is a professional AI agent workspace. Read this file on every session start before doing anything else.

## What this folder is

A multi-agent framework for Inon Baasov (Owner). 14 specialized agents collaborate on business, coding, design, writing, and automation tasks. You are always one of these agents, coordinated by Andy (the Orchestrator).

## Key files — read these before acting

| File | Purpose |
|------|---------|
| `agents/roster.md` | All 14 agents, their roles, and the delegation map |
| `tasks/active_tasks.json` | Current task queue — what's in progress |
| `BKM/sop_onboarding.md` | How new tasks enter the system |
| `BKM/sop_session_logging.md` | How to log sessions |
| `session_logs/INDEX.md` | History of past sessions |
| `memory/session_log.db` | SQLite activity log |

## Agent protocol (mandatory)

**Before every action:**
1. Read `agents/roster.md` — identify which agent you are
2. Check `tasks/active_tasks.json` — understand what's active
3. Read the relevant SOP from `BKM/` for the task type

**After every action:**
- Log to `memory/session_log.db` or `session_logs/`
- Update task status in `tasks/active_tasks.json`
- Tag the next agent

## Activation phrases

- New task: `I have a new objective: [TASK]. Andy — read the roster, decompose, and initiate the pipeline.`
- Hire an agent: `Andy, we need a specialist for [capability]. Initiate the recruitment pipeline with Pat and Nolan.`
- Status check: `/status`

## Folder structure

```
/agents/      — 14 agent persona files
/BKM/         — Standard Operating Procedures
/skills/      — Reusable skill files (LYRA prompting, etc.)
/tasks/       — Task queue (JSON)
/memory/      — SQLite session log
/session_logs/— Markdown session records
/scratchpad/  — Temporary drafts (ephemeral)
/team_inbox/  — Raw inputs from Owner (Andy scans this)
/owner_inbox/ — Items awaiting Owner approval
/output/      — Final approved deliverables
/scripts/     — Automation (CV generator, GitHub sync, Telegram bot)
```

## GitHub

Repo: https://github.com/InonB2/claude-playground-framework  
Sync: `powershell -ExecutionPolicy Bypass -File scripts\github_sync.ps1`

## Rules

- Never commit sensitive data (.env files, tokens, passwords)
- Always use LYRA prompting for complex/ambiguous requests (`skills/lyra_prompting.md`)
- Plan before executing on any destructive or multi-step task
- Keep scratchpad/ ephemeral — finished outputs go to /output/
