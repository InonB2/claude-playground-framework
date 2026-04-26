# Skill: LYRA Prompting

**Trigger:** Every time a user or agent submits a complex, multi-part, or ambiguous prompt  
**Owner:** All agents (mandatory pre-execution step); Andy applies it before decomposing tasks  
**Version:** 1.0 — 2026-04-24

---

## Purpose

LYRA is a clarification-first prompting methodology. It prevents wasted effort by surfacing ambiguities, hidden assumptions, and scope misalignments **before** any execution begins. A prompt answered precisely is worth ten prompts answered approximately.

---

## The LYRA Framework

| Letter | Step    | Question to Ask                                              |
|--------|---------|--------------------------------------------------------------|
| **L**  | Listen  | What is the full literal scope of this request?              |
| **Y**  | Yield   | What is unclear, ambiguous, or has unstated assumptions?     |
| **R**  | Reflect | What is the underlying goal — the "why" behind the request?  |
| **A**  | Act     | Ask targeted questions, then execute with precision          |

---

## Input

- The raw prompt or task description from the user or Orchestrator.

---

## Process

### Step 1 — Listen
Read the entire prompt without jumping to solutions. Catalog every distinct request. Count them. Note dependencies between items.

### Step 2 — Yield
For each item, ask:
- Is the expected output format defined?
- Are credentials, URLs, or external resources needed but not provided?
- Could "X" mean two different things?
- What would need to be true for this to succeed?

Flag every ambiguity. Do not assume. Do not guess.

### Step 3 — Reflect
Group the items into **Core Goal** and **Supporting Requests**. Identify:
- What the user ultimately wants to achieve (the "why")
- What order dependencies exist (what must happen before what)
- What is in-scope vs. out-of-scope

### Step 4 — Act
Produce a structured clarification block:

```
LYRA Applied:

L — [N] distinct requests identified: [list them]

Y — Ambiguities:
  1. [Specific question]
  2. [Specific question]
  ...

R — Core goal: [One sentence on the underlying objective]

A — Proceeding with: [Items that are unambiguous]
    Waiting on: [Items blocked by the questions above]
```

After presenting the LYRA block, immediately begin executing unambiguous tasks. Do not wait for clarification on every item — only pause on items that are genuinely blocked.

---

## Output

- A LYRA clarification block surfaced to the user or logged in `/scratchpad/lyra_[task_id].md`
- Execution of all unambiguous items
- Explicit blockers logged for items requiring clarification

---

## Constraints

- Do NOT use LYRA to delay work indefinitely. Ask only the minimum viable questions.
- Do NOT ask questions whose answers are already present in the conversation or `/memory/session_log.db`.
- LYRA is not a blocker — it runs in parallel with execution of clear items.
- For simple, unambiguous single-step prompts, LYRA is not required.

---

## Example

**Prompt:** "Build me a dashboard and connect it to the database and make it look good."

**LYRA Output:**
```
L — 3 requests: build dashboard UI, connect to database, apply visual design.

Y — Ambiguities:
  1. Which database? (PostgreSQL, SQLite, MongoDB?)
  2. What data should the dashboard display?
  3. "Look good" — is there a brand guide, color palette, or reference design?

R — Core goal: A functional, styled data visualization interface.

A — Proceeding with: scaffolding dashboard component structure.
    Waiting on: database type, data schema, and design references.
```
