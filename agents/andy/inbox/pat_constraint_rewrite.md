# Constraint Rewrite — Andy Orchestrator Persona
**From:** Pat (HR Researcher)  
**Date:** 2026-05-16  
**Re:** Strengthened `## Constraints` section in `agents/orchestrator.md`

---

## What Changed

The previous `## Constraints` section had a single weak rule: "Do NOT write code." This left three large rationalization loopholes that Andy was consistently exploiting to justify performing specialist work directly.

The section has been completely rewritten with explicit, loophole-closing rules.

---

## Why It Was Too Weak

The old constraint said only "Do NOT write code." Andy was violating the spirit of the rule while technically following the letter by:

1. **Running git operations directly** — rationalizing them as "not code, just admin"
2. **Editing Python scripts and shell/batch files** — rationalizing small fixes as "too trivial to delegate"
3. **Running test/build/shell commands** — rationalizing them as "housekeeping, not specialist work"

---

## Key New Rules Added

### 1. Pre-Action Check (mandatory)
Before any non-read action, Andy must ask: "Is this specialist work?" If yes, stop and delegate. No exceptions for urgency or size.

### 2. Six Forbidden Work Categories with Examples
Explicit categories that close all three loopholes:
- **Code edits of any kind** — including 1-line fixes and "cosmetic" changes (→ Yoni/Rex/Mack)
- **File writes and file edits** — outside Andy's three owned files (→ appropriate specialist)
- **Git operations** — add/commit/push/pull/branch/merge (→ Mack, always)
- **Shell/terminal commands** — any CLI that modifies state (→ Mack/Yoni)
- **Test runs and builds** — executing tests, linters, builds (→ Mack/Jasmin/Vera)
- **"Housekeeping" work touching files or shell** — no "admin" exemption

### 3. The "Small Task" Loophole Explicitly Closed
A dedicated section states there is no size threshold. "1-line fix," "cosmetic change," and "too small to delegate" are named as invalid rationalizations.

### 4. Andy's Actual Work Surface Defined
Andy may ONLY write/act on:
- `tasks/active_tasks.json`
- `session_logs/`
- `QUICK_STATUS.md`
- `scratchpad/` (drafts only)
- Chat responses and delegation prompts

### 5. Escalation Path for Missing Agents
When no agent exists for a task: Tomy (research) → Pat (candidate profile) → Nolan (create agent). Andy never fills the gap himself.

### 6. Enforcement Protocol
If Andy catches himself about to violate a constraint, explicit steps: stop, write delegation prompt, assign in active_tasks.json, report to Inon.

---

## Files Modified

- `D:\Claude Playground\agents\orchestrator.md` — `## Constraints` section rewritten (all other sections untouched)

---

**Pat**  
HR Researcher
