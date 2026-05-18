# Mack — httpx logger token-leak fix (follow-up to TELEGRAM-TOKEN-ROTATE)

**From:** Andy
**Dispatched:** 2026-05-18
**Worker:** Mack (you)
**Tester:** Jasmin
**Jasmin's QA report on the rotation:** `D:\Claude Playground\agents\andy\inbox\jasmin_token_rotation_qa.md` (verdict: PASS WITH NOTES — this fix closes the NOTES)

---

## Context

You finished the token rotation cleanly. Jasmin verified all 6 success criteria PASS. She independently confirmed your httpx-logger flag: 9 occurrences of the new token's secret-half currently sit in `scratchpad/telegram_listener.log`. Severity Medium (gitignored + single-user laptop), but the log is unbounded and ACL allows `Authenticated Users` / `BUILTIN\Users` read.

This task closes the leak.

---

## Success criteria

### Code change — `scripts/telegram_listener.py`
1. Add near the existing `logging.basicConfig(...)` / logger setup:
   ```python
   logging.getLogger("httpx").setLevel(logging.WARNING)
   ```
   This silences the per-request INFO log that contains the full URL (and therefore the token).

2. Swap the file handler to `logging.handlers.RotatingFileHandler`:
   ```python
   from logging.handlers import RotatingFileHandler
   handler = RotatingFileHandler(LOG_FILE, maxBytes=512_000, backupCount=3, encoding="utf-8")
   ```
   Cap at ~500 KB with 3 backups (≈2 MB total). Reasoning: prevents unbounded growth + caps blast radius if a leak slips through again.

3. (Defensive — optional but recommended) Add a redaction filter that scans every log record's message for the pattern `bot<digits>:[A-Za-z0-9_-]{30,}` and replaces it with `bot<REDACTED>`. Apply to the root logger. This is belt-and-suspenders — even if a future dependency logs the URL at a different level, the filter strips it.

### Operational
4. **Truncate the existing log** to evict the 9 historical token occurrences. Use:
   ```powershell
   Clear-Content "D:\Claude Playground\scratchpad\telegram_listener.log"
   ```
   (Don't delete the file — the listener has it open; truncate-in-place is safer.)

   Also clear any rotated backups if they already exist (unlikely on the current run, but check `telegram_listener.log.1` etc.).

5. **Restart listener via watchdog.** The watchdog should pick up the code change on next spawn. Confirm new PID, confirm log starts fresh, confirm clean polling (no 409, no auth error).

6. **Verify the leak is closed.** After ~30 seconds of polling on the new process, run:
   ```powershell
   $secret = (Get-Content 'D:\Claude Playground\.env' | Select-String 'TELEGRAM_BOT_TOKEN').Line.Split(':',2)[1].Trim()
   (Get-Content 'D:\Claude Playground\scratchpad\telegram_listener.log' -Raw | Select-String -Pattern $secret -SimpleMatch -AllMatches).Matches.Count
   ```
   Expected output: `0`. If non-zero, the filter or the level change didn't take effect — STOP and report BLOCKED.

### Test the watchdog respawn
7. Confirm `buildar_notify.py` still works end-to-end (POST sendMessage — separate from the listener, but it's the same token, worth a sanity check). Send ONE message:
   ```
   python "D:/Claude Playground/scripts/buildar_notify.py" update "Httpx logger leak closed (Mack). Log truncated; rotation in place."
   ```
   This message landing in Inon's Telegram is your final proof.

---

## What NOT to do

- Do NOT regenerate or rotate the token again — current token is fine; this is a logging fix.
- Do NOT print the token value into the redaction filter as a literal — use a regex pattern (`bot<digits>:[A-Za-z0-9_-]{30,}`) so the filter survives future rotations without code change.
- Do NOT touch `.env`, `buildar_notify.py`, or `tasks/active_tasks.json`.
- Do NOT push to GitHub.

---

## Infrastructure vs Design (per Rubric)

**Infrastructure:** Note in your report whether the watchdog spawned cleanly after your change, and whether the `from logging.handlers import` introduced any import-order weirdness.

**Design:** Document in `BKM/sop_env_secrets.md` (the doc you just created) under "Known follow-ups" → mark this as RESOLVED and add a one-line "Lesson: silence third-party DEBUG/INFO loggers that include URLs when secrets travel in query strings or headers."

---

## Reporting

Write to `D:\Claude Playground\agents\andy\inbox\mack_httpx_leak_fix_done.md`:
- Lines added/removed (small diff — should be ≤30 lines total)
- Truncation confirmation
- New listener PID + clean-poll proof
- Post-fix grep result (must be 0)
- Final Telegram send result
- Status: DONE or BLOCKED

— Andy
