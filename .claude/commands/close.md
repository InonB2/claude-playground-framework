Run end-of-session protocol:
1. Write a session log entry to session_logs/ using today's date (format: session_YYYY-MM-DD.md) — include: what was accomplished, which agents were active, what tasks moved forward, what's pending next session
2. Update tasks/active_tasks.json with current task statuses
3. Run: git add -A && git commit -m "Session close: [today's date]" && git push origin master
4. Confirm: "Session closed and pushed to GitHub."
