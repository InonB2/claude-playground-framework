# Mack — httpx logger leak fix DONE

**From:** Mack
**To:** Andy
**Date:** 2026-05-18
**Task:** TELEGRAM-LOGGER-LEAK_fix (follow-up to TELEGRAM-TOKEN-ROTATE)
**Tester:** Jasmin (pending re-verification)
**Status:** DONE

---

## Summary

All 7 success criteria met. The httpx logger token leak Jasmin flagged in QA is closed. Listener is running on the new code with a fresh PID, log is clean, post-fix grep returns 0 occurrences, and the final Telegram notification landed in Inon's chat.

---

## Code changes — `scripts/telegram_listener.py`

All three code changes were already shipped in the file at the start of this run (the prior task launch that hit the rate limit at ~12:20pm had written the diff before timing out). I verified the source is correct:

1. **httpx logger silenced** (line 130):
   ```python
   logging.getLogger("httpx").setLevel(logging.WARNING)
   ```

2. **RotatingFileHandler in place** (lines 114-116):
   ```python
   _file_handler = RotatingFileHandler(
       LOG_FILE, maxBytes=512_000, backupCount=3, encoding="utf-8"
   )
   ```
   Plus `from logging.handlers import RotatingFileHandler` added at line 30 with the other stdlib imports (no import-order issues).

3. **Redaction filter applied to all root-logger handlers** (lines 84-110, 132-136):
   ```python
   _TOKEN_RE = re.compile(r"bot\d+:[A-Za-z0-9_-]{30,}")
   class _RedactTokenFilter(logging.Filter):
       def filter(self, record):
           if isinstance(record.msg, str) and _TOKEN_RE.search(record.msg):
               record.msg = _TOKEN_RE.sub("bot<REDACTED>", record.msg)
               record.args = None
           ...
   ```
   Pattern-based — no literal token in source. Filter renders args defensively so tokens hiding in `record.args` are caught too.

Net diff vs the pre-task version was approximately +30 lines (filter class + handler swap + httpx silencer + import). No removals beyond the old `basicConfig` file-handler argument.

---

## Operational steps

### Truncate
```powershell
Clear-Content 'D:\Claude Playground\scratchpad\telegram_listener.log'
```
- Result: log size 19833 → 0 bytes.
- No rotated backups existed (`telegram_listener.log.1` etc. not present), nothing else to clear.

### Restart
- Stopped old listener PID 52076 (started 07:52:45 today — was already running current source, but restart was needed to satisfy the "fresh PID + clean polling proof" criterion).
- No watchdog process was running on the host, so it did not auto-respawn. Started the listener directly with the same `pythonw.exe` command pattern the watchdog uses:
  ```
  pythonw.exe "D:\Claude Playground\scripts\telegram_listener.py"
  ```
- **New PID: 68044** (started 13:07:11 IL).

### Clean polling proof — full fresh log content
```
2026-05-18 13:07:15,570 INFO ============================================================
2026-05-18 13:07:15,571 INFO Andy Telegram Listener starting
2026-05-18 13:07:15,571 INFO Allowed user ID: 6283854178
2026-05-18 13:07:15,571 INFO Trigger commands: {'/start', '/continue', '/resume'}
2026-05-18 13:07:15,572 INFO Rate-limit queue: D:\Claude Playground\scratchpad\rate_limit_queue.json
2026-05-18 13:07:15,572 INFO Bot token (masked): 8731882312...
2026-05-18 13:07:15,572 INFO Singleton port: 50917
2026-05-18 13:07:15,572 INFO ============================================================
2026-05-18 13:07:15,574 INFO Singleton lock acquired.
2026-05-18 13:07:17,031 INFO Polling started (poll_interval=2s, timeout=30s)
2026-05-18 13:07:17,736 INFO Application started
```
- No 409 Conflict, no auth error, no httpx INFO entries (silencer working — pre-fix this log would have had ~1 INFO line every 2s with the full `bot<TOKEN>/getUpdates` URL).
- Bot token line shows the existing intentional 10-char prefix mask only (`8731882312...`) — that mask predates this task and is harmless (no secret-half).

### Post-fix grep
```powershell
$secret = (Get-Content 'D:\Claude Playground\.env' | Select-String 'TELEGRAM_BOT_TOKEN').Line.Split(':',2)[1].Trim()
(Get-Content 'D:\Claude Playground\scratchpad\telegram_listener.log' -Raw | Select-String -Pattern $secret -SimpleMatch -AllMatches).Matches.Count
```
**Result: 0**

### Final Telegram send
```
python "D:/Claude Playground/scripts/buildar_notify.py" update "Httpx logger leak closed (Mack). Log truncated; rotation in place."
```
- Output: `[OK] Notification sent (update)`
- Message delivered to Inon's Telegram via the same rotated token — confirms the rotation + the logging-fix path are both healthy end-to-end.

---

## Infrastructure vs Design (per Rubric)

**Infrastructure**
- Listener respawn was manual, not via watchdog: no watchdog process was running on the host when I stopped the old listener. Followup recommendation for Andy: confirm whether watchdog auto-start is intended at this point in the day or if it's been intentionally paused. Not part of this task to fix, but flagging so it doesn't surprise the next person who kills the listener.
- `from logging.handlers import RotatingFileHandler` placed with stdlib imports at line 30 — no import-order weirdness. Listener started cleanly first try.
- Old PID 52076 (07:52:45) was actually already running the post-fix source code (script mtime 07:52:11 — earlier task run shipped the file just before launching the process). Pre-fix grep at start of this run was already 0 because that earlier-spawned process had been running the silenced version for ~5 hours. Truncate + restart was still performed to give a definitive clean-state proof.

**Design**
- BKM updated: `BKM/sop_env_secrets.md` "Known follow-ups" section marked RESOLVED with the closing changeset summary, and a new "Lessons" section added with the one-liner Andy requested:
  > Silence third-party DEBUG/INFO loggers that include URLs when secrets travel in query strings or headers.
- Redaction filter uses a regex pattern (`bot\d+:[A-Za-z0-9_-]{30,}`), not the literal token — survives future rotations without code change.

---

## Hard rules — confirmation

- Token value never printed to chat, log, or this report. Only the existing 10-char masked prefix appears in the fresh log (pre-existing design, no secret-half).
- `.env`, `buildar_notify.py`, `tasks/active_tasks.json` — untouched.
- No GitHub push. No token rotation.

---

## Files touched

- `scripts/telegram_listener.py` — verified (no new edits this run; changes already shipped in prior partial run).
- `scratchpad/telegram_listener.log` — truncated.
- `BKM/sop_env_secrets.md` — updated (follow-up RESOLVED + Lessons section).
- `agents/andy/inbox/mack_httpx_leak_fix_done.md` — this report.

— Mack
