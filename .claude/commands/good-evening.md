Alias for /work-done. End-of-day wrap-up. Do the following:
1. Read session_logs/QUICK_STATUS.md
2. Read tasks/active_tasks.json
3. List all files in session_logs/ matching today's date (session_YYYY-MM-DD*.md) and read each one
4. Review THIS conversation as the current (most recent) session

Output a single end-of-day summary in the chat. This is designed to be pasted into tomorrow's first session to restore full context.

---
# Work Done — $CURRENT_DATE

## Today's Sessions
[List each session from today with one sentence on what it covered — chronological order]

## Today's Work Summary
[2–4 bullets: what was actually built, decided, or shipped today across all sessions]

## Current Session (emphasis)
[2–3 sentences on what happened in the session that just ended — the most recent context]

## Project State Right Now
- Tasks: [active count, blocked count]
- Owner inbox: [count of items waiting for Inon]
- Git: [uncommitted changes? last push?]
- Key open risks or blockers

## Tomorrow: Start Here
1. [Most important first action — specific: file, agent, command]
2. [Second action]
3. [Third action]
[Continue in priority order, minimum 5 items]

## Outstanding Owner Actions
[Full prioritized list of things only Inon can unblock — one line each with WHY it matters]

## Open Questions
[Unresolved decisions, deferred items, things explicitly parked — with reason]

---
*Paste this into tomorrow's session to restore full context.*
