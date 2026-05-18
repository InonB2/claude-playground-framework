# Mack — Telegram token rotation cleanup

**From:** Andy
**Dispatched:** 2026-05-18
**Task:** TELEGRAM-TOKEN-ROTATE-2026-05-17 — Step 2 (yours)
**Tester:** Jasmin
**Context:** Inon revoked the leaked token via @BotFather. The new token is already saved at `D:\Claude Playground\.env` as `TELEGRAM_BOT_TOKEN=...` (file is git-ignored). You do NOT need to ask for or read the value back to chat — just make sure the scripts pick it up from `.env`.

---

## Success criteria (definition of done)

1. **No old token in working tree.** `git grep "AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I"` on `D:\Claude Playground` returns zero hits (excluding the existing `tasks/active_tasks.json` historical note if you choose to leave it — but better to scrub).
2. **No hardcoded token fallback in either script.** Both `scripts/telegram_listener.py` and `scripts/buildar_notify.py` must require `TELEGRAM_BOT_TOKEN` from env — if missing, exit with a clear error. Remove the literal default values currently at:
   - `scripts/telegram_listener.py:47-48` (the multi-line default after `os.environ.get(...,`)
   - `scripts/buildar_notify.py:17` (the second-arg default)
3. **Scripts load `.env` automatically.** Add a tiny `.env` loader at the top of each script (no new dependency — use a 6-line manual parser, or `python-dotenv` only if already installed on the host; check first with `pip show python-dotenv`). Loader must read `D:\Claude Playground\.env`, skip blank lines and `#` comments, set `os.environ[key]` only if not already set.
4. **Listener restarted with new token.** Kill the current `telegram_listener.py` process if running, restart via the existing watchdog (`scripts/telegram_listener_watchdog.ps1`). Confirm a fresh process is running and the log (`scratchpad/telegram_listener.log`) shows clean polling (no 409 Conflict, no auth error).
5. **Outgoing send works.** Run `python "D:/Claude Playground/scripts/buildar_notify.py" update "Token rotation complete — listener restarted with new token (Andy + Mack)."` and confirm it lands in Inon's Telegram. Hold off until END of your work so the message confirms everything.
6. **Listener responds to /continue.** Tail `scratchpad/telegram_listener.log` for ~30 seconds after restart. Confirm no 409s. Inon can then send `/continue` to verify trigger.

---

## What NOT to do

- Do NOT touch `.env` itself — it's already populated correctly. Just read from it.
- Do NOT commit `.env` (gitignored anyway, but don't `git add -f`).
- Do NOT scrub git history on the public repo — that's destructive and the leaked token is already revoked. Old commits with the old token are harmless now. (If you really want to add a `.gitleaks-allow` note for the dead token, fine; otherwise skip.)
- Do NOT modify `active_tasks.json` — Andy handles task list.
- Do NOT push to GitHub. Andy gates pushes.

---

## Infrastructure vs design (per CLAUDE.md Rubric)

**Infrastructure findings to flag in your report:**
- Was the watchdog already running? Did it auto-restart cleanly?
- Did `pip show python-dotenv` come back installed or did you use the manual parser? (Note for future.)
- Any other scripts in the repo that import a Telegram token? Grep `bot_token` / `TELEGRAM` and report.

**Design findings:**
- Is the env-required pattern documented anywhere in `BKM/` for the next person who runs these scripts on a fresh machine? If not, add a 5-line note to `BKM/INDEX.md` or create `BKM/sop_env_secrets.md`.

---

## Reporting

Write to `D:\Claude Playground\agents\andy\inbox\mack_token_rotation_done.md`:
- Files touched (diff summary)
- Confirmation old token grep is clean
- Listener PID + watchdog status
- Outgoing send test result
- Any infra/design findings
- Status: DONE or BLOCKED

When done, no need to send a separate Telegram — your test message in step 5 IS the proof.

— Andy
