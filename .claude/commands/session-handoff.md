Read session_logs/QUICK_STATUS.md and tasks/active_tasks.json, then review this conversation. Output a session handoff summary in the chat with exactly this structure — keep it under 150 lines, no filler:

---
# Session Handoff — $CURRENT_DATE

## Where We Started
[1–2 sentences: state of things at session open — include task counts, inbox state, key blockers]

## Decisions Locked
- [Each key decision — product, technical, strategic, framework — one bullet. Include reasoning where it affects future sessions.]
- [Writing style decisions, naming decisions, tool/approach decisions all count]
- [Stealth startup decisions, product positioning, MVP scope — always include]

## What Shipped
- [Each completed item with file path and brief description]
- [Include script tests, config changes, agent updates, not just "big" deliverables]

## Key Files Next Session
| File | Purpose |
|------|---------|
| [path] | [one line — be specific about what decision it captures] |

## Agent Updates Made
- [Any agent persona files updated, new SOPs added, onboarding changes]

## Running State
[In-progress tasks, background agents still running, git status, outstanding pushes]

## Verification Needed
[Items done but unconfirmed — what to check at next session start. Include: file paths, URLs to test, agent outputs to verify]

## Owner Blockers (full list, prioritized)
1. [Most urgent Owner action — include WHY it unblocks]
2. [Continue in priority order]

## Open Questions & Deferred
- [Owner-gated items, unresolved decisions, deferred tasks with reason]
- [Include any "we talked about X but didn't decide" items]

## ➡️  Pick Up From Here
1. [First action next session — be specific, name the agent/command]
2. [Second action...]
[Continue numbered list in priority order, min 5 items]

---
*Paste this into your next session to restore full context.*
