Review THIS conversation — from the first message to now. Do NOT read session logs or historical files. Output a handoff summary for this session only in the chat. Aim for under 50 lines; hard cap 150 lines.

After outputting the handoff to chat, **also overwrite `session_logs/QUICK_STATUS.md`** with an updated version of the file using the format below — this ensures /start has accurate data next session.

---
# Session Handoff — $CURRENT_DATE

## This Session
[1–2 sentences: what we set out to do and what we actually accomplished]

## Decisions Made
- [Each decision locked this session — one bullet per decision, include reasoning if it affects future sessions]
- [Skip anything decided in prior sessions]

## What Shipped
- [Each completed item — file path + one-line description]

## Left Unfinished
- [Items started but not completed, with reason and who/what is blocking]

## Next Session: Pick Up Here
1. [First action — specific: name the file, agent, or command]
2. [Second action]
3. [Continue in priority order, minimum 3 items]

## New Owner Blockers
- [Only blockers discovered or clarified this session — skip ones from before]

---
*Paste this at the start of your next session.*
