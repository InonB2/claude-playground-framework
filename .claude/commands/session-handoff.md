Review THIS conversation — from the first message to now. Do NOT read or consult any external files (session logs, active_tasks.json, roster.md, or anything outside this conversation). Output a handoff summary covering ONLY what happened in THIS conversation. Aim for under 50 lines; hard cap 150 lines.

After outputting the handoff to chat, **also overwrite `session_logs/QUICK_STATUS.md`** with an updated version of the file using the format below — this ensures /start has accurate data next session.

The format must be concise enough that when pasted into the next session's opening message, the reader can orient themselves in under 30 seconds.

Before writing the handoff, determine today's date by running: `Get-Date -Format 'yyyy-MM-dd'`. Substitute the result for `$CURRENT_DATE` in the header.

---
# Session Handoff — $CURRENT_DATE

## This Session
[1–2 sentences: what we set out to do and what we actually accomplished]

## Decisions Made
- [ONLY decisions made in THIS conversation — one bullet per decision, include reasoning if it affects future sessions]
- [Do NOT include decisions from prior sessions. If none were made this session, write "None."]

## What Shipped
- [ONLY items completed in THIS conversation — file path + one-line description]
- [If nothing shipped, write "None."]

## Left Unfinished
- [ONLY tasks started in THIS conversation that were not completed — include reason and who/what is blocking]
- [Do NOT list all pending tasks in the system. Only items touched this session.]
- [If nothing was left unfinished, write "None."]

## Next Session: Pick Up Here
If 3+ actions arose from this session, list them in priority order. If fewer than 3 arose, list what you have and write "Continue from prior handoff." for the remainder. Do NOT fabricate items to reach the minimum.
1. [First action arising from THIS session's work — specific: name the file, agent, or command]
2. [Second action]
3. [Third action or "Continue from prior handoff."]

## New Owner Blockers
- [ONLY blockers discovered or clarified in THIS conversation — not pre-existing ones]
- [If none, write "None."]

---
*Paste this at the start of your next session.*
