# SOP: Skill Usage Standards

**File Path:** `/skills/sop_skills.md`  
**Authority:** Andy (Orchestrator)  
**Version:** 1.0 — 2026-04-24

---

## What Is a Skill?

A **Skill** is a reusable, named capability that any agent can invoke to perform a specialized task consistently. Skills are defined as markdown files in `/skills/`. They are not agents — they are **tools that agents use**.

---

## Skill File Structure

Every skill file must follow this template:

```markdown
# Skill: [Skill Name]

**Trigger:** [When should this skill be invoked?]
**Owner:** [Which agent(s) use this skill?]
**Version:** [x.x — YYYY-MM-DD]

## Purpose
[One-sentence description of what this skill does]

## Input
[What information/context is needed to run this skill?]

## Process
[Step-by-step execution of the skill]

## Output
[What does the skill produce? Where does it go?]

## Constraints
[Edge cases, failure modes, and what NOT to do]
```

---

## Skill Registry

All skills must be registered in `/skills/INDEX.md`. An unregistered skill does not officially exist in the system.

---

## Adding a New Skill

1. Create the skill file in `/skills/[skill_name].md` using the template above.
2. Add a row to `/skills/INDEX.md`.
3. Update any agent files that should use this skill to reference it in their Logic section.
4. Log the addition in `/memory/session_log.db`.

---

## Using a Skill

When an agent uses a skill, they must:
1. Reference the skill by name in their session log entry.
2. Pass all required inputs as defined in the skill file.
3. Log the output location upon completion.

---

## Current Skills

See [`/skills/INDEX.md`](INDEX.md) for the full registry.
