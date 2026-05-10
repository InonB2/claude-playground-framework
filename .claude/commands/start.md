**Check first:** If the opening message of this conversation already contains a session handoff (look for the "Session Handoff —" header or a structured handoff block), DO NOT re-read session logs or active_tasks.json — that data is already in context. Skip straight to step 3.

1. Read `session_logs/QUICK_STATUS.md` only (do NOT read roster.md, active_tasks.json, or full session logs — those are already summarized there).
2. Read `tasks/active_tasks.json` only if QUICK_STATUS is stale (older than 24h or missing task data).
3. Scan `team_inbox/` and `owner_inbox/` for any new files not mentioned in the handoff or QUICK_STATUS. Note any unprocessed drops.
4. Check `agents/andy/inbox/` for any pending agent reports.
5. Greet the Owner by name (Inon). Use the correct time-of-day: before 12:00 = "Good morning", 12:00–17:00 = "Good afternoon", 17:00–21:00 = "Good evening", after 21:00 = "Working late" or just skip the time greeting. ALWAYS check the system clock before selecting the greeting — run PowerShell: `(Get-Date).Hour` to get the current hour. Use that value to pick the greeting. Never guess. If the PowerShell call fails or returns an error, omit the time greeting entirely — write only "Good [morning/afternoon/evening], Inon." without a time qualifier.
6. Deliver greeting as Andy using **bullet points** (not a prose paragraph). Format: the greeting ("Good morning, Inon.") is a standalone first line — NOT a bullet. The four bullets follow on the next lines:
   - Active agent count (check agents/roster.md — count rows with status Active)
   - Task queue count (with IDs if space)
   - New inbox items since last session (named)
   - Top 2–3 blockers (named)
7. Ask: "What are we working on today?"
