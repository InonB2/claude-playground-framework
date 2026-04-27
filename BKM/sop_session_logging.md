# SOP: Session Logging

**File Path:** `/BKM/sop_session_logging.md`
**Authority:** Andy (Orchestrator)
**Applies To:** All Agents — mandatory end-of-session protocol
**Version:** 1.0 — 2026-04-27

---

## Purpose

Every session must end with a written summary in `/session_logs/`. This is the system's long-term memory. Any agent — or the Owner — can read a session log to instantly understand what was done, what decisions were made, and exactly what needs to happen next. No context is lost between sessions.

---

## When to Write

- **End of every session** — before the Owner clears the conversation.
- **Mid-session** — if a major milestone is reached (a product shipped, a new agent deployed, a critical decision made).
- **On re-entry** — before starting work in a new session, read the most recent log to re-orient.

---

## File Naming Convention

```
session_logs/session_YYYY-MM-DD.md
```

If multiple sessions occur on the same day:
```
session_logs/session_YYYY-MM-DD_2.md
```

---

## Required Sections

```markdown
# Session Log — YYYY-MM-DD

## Session Summary
One paragraph. What was the overall theme or goal of this session?

## Major Accomplishments
Bullet list of everything completed. Be specific — file names, agent names, task IDs.

## Key Decisions Made
- [Decision]: [Rationale]
(List every architectural, design, or strategic decision — future sessions will need to know WHY)

## Files Created / Modified
| File | Action | Agent |
|------|--------|-------|

## Open Tasks (carry forward to next session)
| Task ID | Description | Assigned To | Priority | Status |
|---------|-------------|-------------|----------|--------|

## Blockers & Waiting On
What is blocked and what does it need to unblock?

## Owner Action Items
Things only the Owner can do (approvals, credentials, content to supply).

## Next Session — Start Here
Exactly what to do first when the next session opens.
```

---

## Agent Reading Protocol (Session Start)

Every agent must read the latest session log before taking any action:

1. Open `/session_logs/` → find the most recent file
2. Read "Open Tasks" — confirm your assigned tasks
3. Read "Next Session — Start Here" for context
4. Read "Blockers" — do not start work that is blocked
5. Log your session start in `/memory/session_log.db`

---

## Rules

1. **Andy writes the session log** — with input from all agents who worked that session.
2. The session log is **never deleted** — it is the permanent historical record.
3. **Be specific** — "updated the CV" is not enough. "Fixed 8 visual issues in `Inon_Baasov_CV_Elbit_2026.pdf`, regenerated via `scripts/generate_elbit_cv.py`" is correct.
4. Session logs are **read-only after writing** — do not edit a previous session's log.
5. Update `/session_logs/INDEX.md` after every new session log.
