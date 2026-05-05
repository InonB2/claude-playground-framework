Review THIS conversation from start to now. Identify every task that was touched, progressed, blocked, or completed during this session.

For each affected task:
1. Update `tasks/active_tasks.json` — set the correct status and update the notes field with what happened and what's next
2. Update `owner_inbox/TODO.md` if the task appears there — keep it in sync

Rules:
- Only update tasks that were actually worked on this session — don't touch untouched tasks
- Status values: pending | in-progress | partial | pending-owner | blocked | done
- Notes must say: what was done, what is blocking (if any), and the exact next step
- After updating, print a one-line summary per task: [TASK-ID] old-status → new-status — reason

Do not ask for confirmation. Execute directly.
