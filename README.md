# Autonomous Agentic Framework — v2

## Directory Structure

| Path             | Purpose                                                                 |
|------------------|-------------------------------------------------------------------------|
| `/agents/`       | System prompts and persona definitions for each agent                   |
| `/BKM/`          | Business Knowledge Management — SOPs and procedural standards           |
| `/memory/`       | Shared memory: SQLite session log and long-term context                 |
| `/tasks/`        | Task management: active queue and backlog                               |
| `/scratchpad/`   | Temporary workspace — ALL drafts and intermediates go here first        |
| `/team_inbox/`   | **Input funnel** — Drop raw screenshots, notes, or files here. Andy scans this. |
| `/owner_inbox/`  | **Approval gate** — Jasmin places reviewed deliverables here for Owner sign-off. |
| `/output/`       | Final deliverables — only moved here after Owner approval               |

## Active Agents

| Name   | Role                   | File                          |
|--------|------------------------|-------------------------------|
| Andy   | Orchestrator           | `agents/orchestrator.md`      |
| Tomy   | Researcher             | `agents/researcher.md`        |
| Yoni   | Lead Coder             | `agents/coder.md`             |
| Jasmin | Reviewer               | `agents/reviewer.md`          |
| Pat    | HR Researcher          | `agents/hr_researcher.md`     |
| Nolan  | HR Agent               | `agents/hr_agent.md`          |

Full delegation map and status: [`/agents/roster.md`](agents/roster.md)

## Agent Protocol (All Agents)

**Before starting any action:**
1. Read `/agents/roster.md` — know who is available (Andy does this first).
2. Query `/memory/session_log.db` — understand current project state.
3. Read your assigned task from `/tasks/active_tasks.json`.
4. Read any relevant SOPs in `/BKM/` before executing.

**During execution:**
- All intermediate work goes to `/scratchpad/` — never directly to production paths.
- Follow the naming conventions in [`/BKM/sop_onboarding.md`](BKM/sop_onboarding.md).

**After finishing:**
- Log your action, timestamp, output path, and next step to `/memory/session_log.db`.
- Update `/tasks/active_tasks.json` with new task status.
- Jasmin places approved work in `/owner_inbox/` — Owner moves it to `/output/`.

## Memory System

| File                            | Type   | Purpose                                          |
|---------------------------------|--------|--------------------------------------------------|
| `memory/session_log.db`         | SQLite | Queryable log of all agent actions and decisions |
| `memory/long_term_context.json` | JSON   | Persistent cross-session knowledge base          |
| `memory/init_db.py`             | Python | Run once to initialize the SQLite schema         |

### SQLite Tables
- **`session_log`** — every agent action with timestamp, task ID, status, output path
- **`decisions`** — strategic decisions with rationale and outcome
- **`tasks`** — task lifecycle tracking (pending → in_progress → completed)

## Activating the Team

Drop your objective in `/team_inbox/` or use this prompt directly:

```
I have a new objective: [INSERT TASK HERE].

Andy — read the roster, decompose this objective, and initiate the pipeline.
```

## Recruiting a New Agent

```
Andy, we need a specialist to manage [capability gap].
Initiate the recruitment pipeline with Pat and Nolan.
```
