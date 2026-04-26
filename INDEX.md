# Framework Master Index

> Root navigation for the Autonomous Agentic Framework v2.  
> Start here. Everything has an index.  
> Last updated: 2026-04-24

## System Map

| Directory       | Index File               | Purpose                                               |
|-----------------|--------------------------|-------------------------------------------------------|
| `/agents/`      | [agents/INDEX.md](agents/INDEX.md) | All agent personas and delegation map        |
| `/BKM/`         | [BKM/INDEX.md](BKM/INDEX.md)       | Standard Operating Procedures library        |
| `/skills/`      | [skills/INDEX.md](skills/INDEX.md) | Reusable skill registry                      |
| `/tasks/`       | [tasks/active_tasks.json](tasks/active_tasks.json) | Live task queue              |
| `/memory/`      | [memory/session_log.db](memory/session_log.db)   | SQLite activity log          |
| `/scratchpad/`  | *(no index — ephemeral)* | Temporary drafts and intermediates                    |
| `/team_inbox/`  | *(no index — drop zone)* | Raw inputs from Owner for Andy to scan                |
| `/owner_inbox/` | *(no index — gate)*      | Approved deliverables awaiting Owner sign-off         |
| `/output/`      | *(no index — final)*     | Owner-approved deliverables                           |

## Key Entry Points

- **New task?** → Drop in `/team_inbox/` or prompt Andy directly.
- **Who's available?** → [`/agents/roster.md`](agents/roster.md)
- **What's the protocol?** → [`/BKM/sop_onboarding.md`](BKM/sop_onboarding.md)
- **Add a skill?** → [`/skills/sop_skills.md`](skills/sop_skills.md)
- **Hire a new agent?** → Ping Andy: *"Initiate recruitment pipeline with Pat and Nolan."*
- **Full README** → [`README.md`](README.md)
