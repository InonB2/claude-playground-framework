# Mack — Token Rotation Cleanup: DONE

**From:** Mack
**To:** Andy
**Date:** 2026-05-18
**Task:** TELEGRAM-TOKEN-ROTATE-2026-05-17 — Step 2
**Tester (next):** Jasmin
**Status:** DONE

---

## TL;DR

New token in `.env` is live. Both scripts now load `.env` and hard-fail if `TELEGRAM_BOT_TOKEN` is missing — no hardcoded fallback anywhere. Old listener (PID 60508, running the revoked token) was killed; new listener (PID 65832) is polling cleanly with the new token via the watchdog. End-to-end Telegram send via `buildar_notify.py update` succeeded — that message landing in Inon's chat is the proof.

---

## Success criteria — pass/fail

| # | Criterion | Result |
|---|-----------|--------|
| 1 | No old token in working tree (scripts) | PASS — `scripts/telegram_listener.py` and `scripts/buildar_notify.py` both clean. See "Remaining hits" below for the harmless residue. |
| 2 | No hardcoded fallback in either script | PASS — both replaced with `os.environ.get("TELEGRAM_BOT_TOKEN")` + `SystemExit` if unset |
| 3 | Scripts load `.env` automatically | PASS — `python-dotenv` is installed (1.2.2) and used by both; manual parser fallback added in `buildar_notify.py` for fresh machines |
| 4 | Listener restarted with new token | PASS — old PID 60508 killed; watchdog spawned new PID 65832 |
| 5 | Outgoing send works | PASS — `buildar_notify.py update` returned `[OK] Notification sent (update)` |
| 6 | No 409 Conflict, no auth error in log | PASS — `getMe` 200, `deleteWebhook` 200, `getUpdates` 200; zero `Conflict`/`InvalidToken` after restart |

---

## Files touched

| File | Change |
|------|--------|
| `scripts/telegram_listener.py` | Already edited externally during my session — adds `from dotenv import load_dotenv`, calls `load_dotenv(ENV_FILE)`, replaces `os.environ.get(..., "<old token>")` with `os.environ.get(...)` + `sys.exit(2)` on missing. I verified the final state. |
| `scripts/buildar_notify.py` | I added: `pathlib.Path` import, `_load_dotenv()` helper (python-dotenv primary, manual parser fallback), removed hardcoded fallback, `raise SystemExit` if `TELEGRAM_BOT_TOKEN` missing. `TELEGRAM_CHAT_ID` default kept (`6283854178` is Inon's user ID — public, not a secret). |
| `BKM/sop_env_secrets.md` | NEW — SOP documenting the `.env`-only secrets pattern, fresh-machine setup, leak-rotation drill, and known follow-ups. |
| `BKM/INDEX.md` | Added row pointing to `sop_env_secrets.md`. |
| `agents/andy/inbox/mack_telegram_listener_done.md` | Redacted old token from historical report. |
| `owner_inbox/buildar/mack_telegram_notify_done.md` | Redacted old token. |
| `owner_inbox/research/remote_session_trigger_research.md` | Redacted old token (5 occurrences). |

`.env` itself was NOT touched. Not committed (gitignored).

---

## Old-token grep — final state

After scrubbing, the literal old token still appears in:

1. `scratchpad/telegram_listener.log` — historical log lines from before the kill. Gitignored under `scratchpad/`, so it won't reach GitHub. Mention only for completeness; safe to delete the log file if you want a fully clean grep.
2. `agents/mack/inbox/TELEGRAM-TOKEN-ROTATE_cleanup.md` — the task brief itself (intentional; you wrote it that way so I had the literal string to grep for).
3. `.claude/worktrees/agent-*/` — 60 hits across 10 old Claude Code agent worktrees. These are sandboxed snapshots from prior agent runs, not on master, gitignored by Claude Code's own setup. Out of scope per brief ("working-tree-only files — scripts are the target").

All other paths — scripts, reports, research docs — are clean.

---

## Listener runtime state

| Field | Value |
|-------|-------|
| Old listener PID (killed) | 60508 |
| New listener PID (alive) | 65832 |
| Started via | `telegram_listener_watchdog.ps1` (manual invocation) |
| Singleton port held | 127.0.0.1:50917 |
| `getMe` response | 200 OK with new token |
| `getUpdates` response (first poll) | 200 OK |
| 409 Conflict count since restart | 0 |
| Auth errors since restart | 0 |
| Watchdog scheduled task | `AndyTelegramListenerWatchdog` (untouched, still active per 2026-05-17 commit 442c744) |

---

## Outgoing send test (the proof)

```
> python "D:/Claude Playground/scripts/buildar_notify.py" update "Token rotation complete - listener restarted with new token (Andy + Mack)."
[OK] Notification sent (update)
```

The message in Inon's Telegram is the end-to-end verification: it confirms `.env` loaded, new token was used, Telegram API accepted it, and the bot is fully operational.

---

## Findings — Infrastructure

1. **`python-dotenv` is already installed** (1.2.2). Both scripts now use it as primary, with a manual 6-line parser as fallback so a fresh checkout without the dep still works.
2. **Watchdog behaviour confirmed clean.** Killed the old process, ran `telegram_listener_watchdog.ps1` once manually, it detected port 50917 was free, spawned the new listener via pythonw, and confirmed up within the 20s window. Scheduled task on 2-min cadence will keep it up going forward.
3. **No other repo scripts hold a Telegram token.** Grep for `TELEGRAM_BOT_TOKEN` / `bot_token` found only the two target scripts plus markdown reports/research. No silent third script to fix.
4. **The Telegram listener log is leaking the new token at INFO level.** `python-telegram-bot`'s underlying httpx logger writes the full request URL — `https://api.telegram.org/bot<TOKEN>/getMe` etc — into `scratchpad/telegram_listener.log` on every poll. Not a git risk (scratchpad is gitignored), but anyone with file-system read access to that machine can lift the token. Mitigation: raise `httpx` / `telegram` logger level to WARNING, or add a filter that masks bot URLs. **Recommend dispatching a small follow-up to fix this — same severity class as the issue we just cleaned up.** Tracked in `BKM/sop_env_secrets.md` under "Known follow-ups".
5. **Prevention plan for the original leak**: the new env-only-with-hard-fail pattern makes it mechanically impossible to commit a working token via these scripts — there's nothing to commit. A future hire would need to deliberately edit the script to reintroduce a fallback. Add a pre-commit `gitleaks` hook if you want defence-in-depth.

## Findings — Design

1. **`TELEGRAM_CHAT_ID` defaulting kept.** The chat ID (`6283854178`) is Inon's user ID — public info, not a secret, and reasonable to keep as a default so notify calls don't need to pass it. Only `TELEGRAM_BOT_TOKEN` is treated as a secret.
2. **Consistency between the two scripts.** `telegram_listener.py` uses `sys.exit(2)` on missing token; `buildar_notify.py` uses `raise SystemExit(...)`. Functionally equivalent. Left both as-is to minimize diff surface, but flagging in case you want them harmonized.
3. **Manual-parser fallback in `buildar_notify.py` only.** `telegram_listener.py` requires `python-telegram-bot` anyway (heavy dep), so importing `dotenv` from the same vendor is fine. `buildar_notify.py` is dependency-free pure stdlib — keeping the manual fallback means it still works on a stripped machine. Design choice, not a bug.
4. **Documented in `BKM/sop_env_secrets.md`.** Next person who writes a script needing a secret has a copy-pasteable pattern + setup steps for a fresh machine + the leak-rotation drill. Added to `BKM/INDEX.md` as a discoverable row.

---

## Anything I deliberately did NOT do

- Did NOT touch `.env` (already populated correctly).
- Did NOT `git add -f` `.env`.
- Did NOT scrub git history — old commits with the dead token are harmless.
- Did NOT modify `tasks/active_tasks.json` — your job.
- Did NOT push to GitHub — your gate.
- Did NOT edit the brief in my inbox or the 10 `.claude/worktrees/` snapshots (out of scope).
- Did NOT print the new token anywhere in this report.

---

— Mack
