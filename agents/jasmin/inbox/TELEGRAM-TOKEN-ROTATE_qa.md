# Jasmin — Token rotation QA + httpx logger leak verification

**From:** Andy
**Dispatched:** 2026-05-18
**Task:** TELEGRAM-TOKEN-ROTATE-2026-05-17 — Step 3 (yours, the verification)
**Worker:** Mack (just completed)
**Worker's report:** `D:\Claude Playground\agents\andy\inbox\mack_token_rotation_done.md`

---

## Context

Inon revoked the leaked Telegram bot token via @BotFather. New token is in `D:\Claude Playground\.env` (git-ignored). Mack:
1. Edited `scripts/buildar_notify.py` to load `.env` + hard-fail without `TELEGRAM_BOT_TOKEN`
2. Confirmed `scripts/telegram_listener.py` was already hardened the same way
3. Killed old listener (PID 60508), watchdog respawned new listener (PID 65832)
4. Sent end-to-end test message — landed in Inon's Telegram
5. Scrubbed dead token from 3 historical docs
6. Created `BKM/sop_env_secrets.md` and indexed it

**Mack flagged one critical follow-up he did not fix:** httpx INFO-level logger in `python-telegram-bot` writes full request URLs to `scratchpad/telegram_listener.log` on every `getUpdates` poll — and the URL contains the token. Not a git risk (scratchpad is gitignored) but anyone with filesystem read access can lift it. Same severity class as the original leak.

Your job is to verify everything Mack claims AND independently assess the httpx-logger finding.

---

## Success criteria (definition of done)

Split your verdict into Infrastructure vs Design per CLAUDE.md Rubric.

### Verification — Mack's 6 claims
1. **Grep proof.** Run `git grep "AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I"` in `D:\Claude Playground`. Confirm zero hits in tracked files. Worktree hits in `.claude/worktrees/` are expected (Mack noted them; they're historical snapshots, not on master).
2. **Both scripts require env.** Read `scripts/telegram_listener.py` lines ~45-50 and `scripts/buildar_notify.py` lines ~15-25. Confirm: no hardcoded token literal default, missing env → hard exit with clear message.
3. **`.env` loader works.** Confirm both scripts load `D:\Claude Playground\.env` automatically. Verify with: `python -c "import sys; sys.path.insert(0, 'scripts'); ..."` or just trace the import order in the source.
4. **Listener is alive on new token.** Tail last ~20 lines of `scratchpad/telegram_listener.log`. Confirm clean polling, no 409 Conflict, no auth/401/403 errors in the last 5 minutes. Get the listener PID (`Get-Process python` or `Get-CimInstance Win32_Process | Where {$_.CommandLine -match "telegram_listener"}`) and confirm it matches Mack's claimed 65832 OR is a fresh later restart (the watchdog may have respawned).
5. **End-to-end send works.** Send your OWN test message via `python "D:/Claude Playground/scripts/buildar_notify.py" update "Jasmin QA verification — token rotation OK"`. Confirm exit code 0 and stdout `[OK]`. Inon's Telegram will receive it; you trust that as proof.
6. **BKM doc exists and is correct.** Read `BKM/sop_env_secrets.md` and `BKM/INDEX.md`. Confirm the entry is in the index and the SOP describes the env-only pattern + fresh-machine setup + leak-rotation drill.

### Independent finding — httpx logger leak
7. **Reproduce the leak.** Grep `scratchpad/telegram_listener.log` for the new token's secret half (everything after the colon in `.env`'s `TELEGRAM_BOT_TOKEN`). If you find ANY hits, the leak is real and active.
8. **Assess severity.** Note in your report:
   - File permissions on `scratchpad/telegram_listener.log` (single-user vs accessible to others on the machine)
   - Is the scratchpad confirmed gitignored? (Check root `.gitignore`.)
   - Log rotation policy: does it ever get committed by accident (e.g., via `git add -A`)?
   - Realistic threat model on Inon's single-user Windows machine
9. **Recommend remediation.** Two reasonable paths:
   - **Quick:** raise `logging.getLogger("httpx").setLevel(logging.WARNING)` near the listener's logging setup
   - **Stricter:** custom logging filter that redacts the token from URL params
   Pick one and justify briefly.

---

## Verdict format

End your report with: `PASS` / `PASS WITH NOTES` / `HOLD`. Worker/tester naming for the task tracker: worker=Mack, tester=Jasmin.

Reporting destination: `D:\Claude Playground\agents\andy\inbox\jasmin_token_rotation_qa.md`

When done, no separate Telegram needed (Mack already sent the rotation-complete message; if you HOLD, send:
```
python "D:/Claude Playground/scripts/buildar_notify.py" update "Jasmin QA HOLD on token rotation — see jasmin_token_rotation_qa.md"
```
).

---

## Hard rules

- Do NOT print, log, or paste the new token value anywhere — chat, report, scratch. Refer only to "the new token from .env" or "the secret half" or grep for it without echoing back.
- Do NOT modify any scripts. You're a tester this round.
- Do NOT modify `.env` or `tasks/active_tasks.json`.

— Andy
