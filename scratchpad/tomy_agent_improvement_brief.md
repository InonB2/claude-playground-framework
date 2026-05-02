# Tomy Research Brief: Agent Self-Improvement, Ralph Loop, and Status Dashboard Design

**Date:** 2026-05-02  
**Author:** Tomy (The Researcher)  
**Requested by:** Andy (for Owner/Inon)  
**Status:** Complete — all three parts resolved with definitive recommendations

---

## Part 1: The Ralph Loop — Definitive Finding

### Verdict: This is a real, published, widely-adopted framework (2025–2026)

The "Ralph Loop" is **not** a term the Owner invented. It is a recognized, actively-discussed AI agent execution paradigm that emerged in late 2024 and became mainstream in early 2026. It is named after Ralph Wiggum from The Simpsons — the character who keeps trying despite repeated failure.

### What It Is

The Ralph Loop is a **continuous agent execution pattern** designed to solve the core reliability failure of LLM-based agents: the agent exits when it *subjectively believes* a task is done, rather than when the task is *verifiably complete* by objective criteria.

The core insight: **"State lives in files and git history, not in the LLM's context window."** Because of this, you can reset the agent's context as many times as needed without losing progress. The agent always picks up from current file state, not from memory.

### Canonical Structure

```
┌─────────────────────────────────────────────────────┐
│              RALPH LOOP (Infinite Outer Loop)        │
│                                                     │
│  1. READ       → Load current state from files     │
│                   (progress.txt, prd.json, git log)  │
│                                                     │
│  2. WORK       → Agent executes on highest-priority  │
│                   incomplete task                    │
│                                                     │
│  3. TEST       → Automated verification runs         │
│                   (tests, linting, build checks)     │
│                                                     │
│  4. EVALUATE   → Stop Hook intercepts exit attempt   │
│                   → Did verifyCompletion() pass?     │
│                   → YES: mark task done, continue    │
│                   → NO: log failure to progress.txt  │
│                         inject original task again   │
│                                                     │
│  5. CONTEXT MANAGEMENT (three zones):               │
│     GREEN  (<60% tokens) → work freely              │
│     YELLOW (60–80%)      → wrap up current task     │
│     RED    (>80%)        → forced context reset      │
│                           fresh agent, same files    │
│                                                     │
│  6. GUARDRAILS → Agent reads .ralph/guardrails.md   │
│                   before starting each iteration     │
│                   (lessons from past failures)       │
└─────────────────────────────────────────────────────┘
```

### Key Files Maintained Across Iterations

| File | Purpose |
|------|---------|
| `progress.txt` | Cumulative log of attempts, what failed, what was learned |
| `prd.json` / `tasks.json` | Structured task list with per-item pass/fail status |
| `.ralph/guardrails.md` | Lessons from past failures — read first each iteration |
| Git commit history | Immutable state record — serves as agent "long-term memory" |

### How It Differs From Prior Frameworks

| Framework | Timing | Memory | Stops When |
|-----------|--------|--------|-----------|
| **ReAct** | Online (during execution) | Single context window | LLM decides it's done |
| **Reflexion** | Post-hoc (after full attempt) | Textual episodic memory | Iteration limit hit |
| **Ralph Loop** | Continuous outer loop | Files + git | Objective verification passes |

### RPI Methodology (Sub-Pattern)

A common Ralph-adjacent pattern for legacy systems is **Research → Plan → Implement**:
- **Research:** Agent understands existing system before touching it
- **Plan:** Architecture written out before code changes
- **Implement:** Code generation occurs with guardrails active

This is particularly effective for brownfield (existing) codebases. For greenfield work, pure task-list execution is preferred.

### Primary Sources

- Alibaba Cloud Blog: "From ReAct to Ralph Loop: A Continuous Iteration Paradigm for AI Agents"  
  https://www.alibabacloud.com/blog/from-react-to-ralph-loop-a-continuous-iteration-paradigm-for-ai-agents_602799
- GitHub: vercel-labs/ralph-loop-agent  
  https://github.com/vercel-labs/ralph-loop-agent
- GitHub: snarktank/ralph  
  https://github.com/snarktank/ralph
- DEV Community: "2026 — The Year of the Ralph Loop Agent"  
  https://dev.to/alexandergekov/2026-the-year-of-the-ralph-loop-agent-1gkj
- LinearB Blog: "Ralph loops make agentic coding reliable with ruthless context resets"  
  https://linearb.io/blog/dex-horthy-humanlayer-rpi-methodology-ralph-loop

---

## Part 2: Agent Self-Improvement Best Practices

### How Frameworks Handle Agent Improvement

#### Reflexion (NeurIPS 2023 — Shinn et al.)
The academic gold standard. An agent acts, receives feedback, then generates a **verbal self-critique stored in an episodic memory buffer**. The next attempt starts by reading that critique. No model retraining required — the LLM learns via accumulated linguistic feedback.

Architecture:
```
Actor → Outcome → Evaluator → Self-Reflection → Episodic Memory → Next Actor Attempt
```
Results: 91% pass@1 on HumanEval (vs. 80% for GPT-4 unaided). Proven in coding and sequential decision-making.  
Source: https://arxiv.org/abs/2303.11366

#### AutoGen (Microsoft)
Frames everything as agent-to-agent conversation. Self-improvement happens via **critic agents** — a dedicated agent whose role is to review another agent's output and return structured critique. The "Planner-Worker-Critic" triad is the standard pattern. No native learning loop built-in; improvement is designed into the topology.

#### CrewAI
Role-based delegation. Improvement comes from **task-level feedback injection** — the crew manager can route failed tasks back to the responsible agent with the evaluator's critique appended. Supports memory (short-term/long-term/entity memory) that persists across runs.

#### LangGraph
Graph-based state machine. The best production option for **instrumenting improvement**: every node's inputs and outputs are logged via LangSmith (step-by-step traces, replay from any checkpoint, per-node token counts). Human-in-the-loop is a first-class feature. Self-improvement is implemented as conditional edges: if evaluation node returns "fail," re-route to the working node with feedback injected into state.

#### Martin Fowler's "Feedback Flywheel"
The most practical human-AI team improvement framework (not agent-to-agent, but agent-team improvement). Defines four signal types from each interaction:
1. **Context Signal** — gaps in briefing/priming documents
2. **Instruction Signal** — prompts that worked and should become shared commands
3. **Workflow Signal** — sequences that should become team playbooks
4. **Failure Signal** — root-cause analyses pointing to specific artifacts to fix

Cadences:
- **Per-session:** "What should change for next session? Make that change now."
- **Daily standup:** Share useful discoveries from yesterday's AI work
- **Sprint retrospective:** Concrete agenda item — what worked, what needs updating
- **Quarterly:** Review artifact currency and prune stale docs

Source: https://martinfowler.com/articles/reduce-friction-ai/feedback-flywheel.html

---

### Concrete Recommendation for This 14-Agent Team

Our team is not a code-execution loop — it is a specialist delegation system. The Ralph Loop applies to how individual agents execute long tasks (particularly Yoni, Rex, Mack). The self-improvement mechanism is Reflexion-style verbal feedback, but adapted to our file-based, session-bounded workflow.

#### Recommended Protocol: "Session Retrospective Loop"

**Trigger:** End of every session (Andy runs this as part of `/close`)

**Step 1 — Per-Agent Outcome Log**
Each agent that worked this session writes 3–5 lines to their own log file:
```
agents/[name]/scratchpad/learning_log.md
```
Format (append-only):
```markdown
## [YYYY-MM-DD] Task [TASK-ID]
- What worked: [1 line]
- What failed or was slow: [1 line]
- Lesson for next time: [1 line]
- Proposed persona update: [Yes/No — what change?]
```

**Step 2 — Andy Reads Learning Logs**
At the start of the next session, Andy reads each active agent's `learning_log.md` before dispatching new tasks. If a proposed persona update is flagged, Andy reviews and applies it to `agents/[name].md` or surfaces it to the Owner.

**Step 3 — Guardrails Propagation**
Lessons that apply across agents (not just one specialist) get written to:
```
BKM/sop_[domain]_[topic].md
```
This is the team-level guardrails file — equivalent to `.ralph/guardrails.md` at the team scale.

**Step 4 — Quarterly Prune**
Every ~90 days (or when CLAUDE.md becomes stale), Andy reviews all learning logs and proposes:
- Persona file updates for agents who have repeated learnings
- Deprecation of SOPs that no longer apply
- New SOPs for workflows that have stabilized

#### File Format for Learning Logs

```markdown
# Learning Log — [Agent Name]
> Append-only. Do not edit past entries. Andy reads this at session start.

## [YYYY-MM-DD] Task [TASK-ID]: [One-line task summary]
- What worked: 
- What failed or was slow: 
- Lesson for next time: 
- Proposed persona update: [Yes: "Add X to startup protocol" | No]
```

#### How Often
- Per-session: Every agent that completes a task writes to their log
- Andy reads: Every session start (before any delegation)
- Persona updates: When 2+ entries suggest the same change
- BKM updates: When the same lesson appears in 2+ agents' logs

#### Who Triggers It
- Andy triggers the "read learning logs" step at session start
- Each agent self-triggers "write to learning log" at task completion
- The Owner can manually trigger a "persona review" by asking Andy to audit all logs

---

## Part 3: QUICK_STATUS.md — Redesign

### Why the Current Format Fails

The current `session_logs/QUICK_STATUS.md` has three problems:
1. **Too long** — full task table with 24 rows is harder to scan than the actual `active_tasks.json`
2. **Not actionable** — no clear "what do I do right now" answer
3. **Stale by design** — it is updated at session-end and becomes wrong within hours

### What Great Async Status Docs Look Like

From research into Linear project pages, incident war rooms, and engineering standup formats, the best async status documents share these properties:

- **Single-screen readable** — no scrolling to get the full picture
- **Decision-forcing** — every section answers a question an opener would actually ask
- **Owner-first** — blockers requiring human action are always at top, not buried
- **Not a duplicate** — it links to sources of truth rather than reproducing them
- **Dated prominently** — staleness is immediately visible

### Proposed QUICK_STATUS.md Template

```markdown
---
updated: YYYY-MM-DD (session N of the day)
next_update: [next session or "when Owner unblocks X"]
---

# Quick Status — Andy Framework

## RIGHT NOW: Owner's Required Actions
> Everything blocked until Inon does one of these.

1. **[ACTION]** — [why it matters] → [link or file]
2. **[ACTION]** — ...
(Max 5 items. If nothing is blocked on Owner, write "Nothing blocked on Owner.")

## THIS SESSION: What Was Done
> One bullet per completed task. Agent name + task ID.

- [Agent]: [Task ID] — [one-line result] ([file or commit])
- ...

## ACTIVE: In-Flight Right Now
> Tasks currently assigned and running. Not blocked.

| Task ID | What | Who | ETA/Notes |
|---------|------|-----|-----------|
| ...     | ...  | ... | ...       |

## BLOCKED: Waiting on Something
> Not owner blockers (those are above). These wait on another task or external dependency.

| Task ID | Blocked By | Who Owns Unblock |
|---------|-----------|-----------------|
| ...     | ...       | ...             |

## DONE THIS WEEK
> Compact archive of completions since last Owner review. Move to session_log after Owner ACK.

- [Task ID]: [one-liner] — [date]
- ...

## NEW IN owner_inbox
> Files ready for Owner review or action.

- `filename.md` — [what it is, what decision it needs]
- ...

---
*Full task data: tasks/active_tasks.json*  
*Full session history: session_logs/*
```

### Rules for the New Template

1. **Max length: 60 lines** — if it exceeds this, items are too granular and belong in `active_tasks.json`
2. **"Owner's Required Actions" always comes first** — this is the most expensive stale information
3. **No task duplication** — QUICK_STATUS summarizes; `active_tasks.json` is the source of truth
4. **Updated timestamps are mandatory** — `updated:` and `next_update:` fields at the top
5. **"Done this week" section** — captures recent completions so Owner can review at a glance without reading every session log
6. **Links, not content** — files go in `owner_inbox/`; QUICK_STATUS just names them

### What to Exclude

- Full task tables with 20+ rows (link to `active_tasks.json` instead)
- Duplicate information that already exists in session logs
- Technical details about implementation (those belong in the task notes)
- Items marked "done" more than 1 week ago (move to session log)

---

## Summary of All Recommendations

| Topic | Recommendation |
|-------|---------------|
| Ralph Loop | Real framework. Apply it to Yoni/Rex/Mack for long-running tasks. Core pattern: outer loop + file-based state + context reset before degradation + guardrails file. |
| Agent self-improvement | Reflexion-style verbal feedback, stored as `learning_log.md` per agent. Andy reads at session start. Lessons that generalize → BKM SOPs. Persona updates when 2+ identical lessons. |
| QUICK_STATUS.md | Redesign to 60-line max, owner-blockers first, links not content, dated prominently. See template above. |

---
*Brief written by Tomy — 2026-05-02*
