Run end-of-session protocol:
1. Write a session log to session_logs/session_YYYY-MM-DD.md — include: what was accomplished, which agents were active, tasks that moved forward, and Owner action items for next session
2. Update tasks/active_tasks.json with current statuses
3. Rewrite session_logs/QUICK_STATUS.md to reflect current state — this is the file /start reads, so keep it under 50 lines: last session summary (2 sentences), compact task table (ID, title, priority, owner, status), and Owner blockers
4. Run: git add -A && git commit -m "Session close [today's date] — [one-line summary]" && git push origin master
5. Confirm: "Session closed and pushed to GitHub."
