# Mack Delivery: Telegram Listener — Done
**From:** Mack (Automation Engineer)
**To:** Andy
**Date:** 2026-05-16
**Task:** Remote session trigger via Telegram

---

## Summary

The Telegram listener is built, tested, and running as a background Task Scheduler service. Sending `/continue` from Inon's Telegram will open Windows Terminal with `claude -c` on his machine.

---

## Phase Results

### Phase 1: Prerequisites — DONE

- `python-telegram-bot==22.7` installed successfully
- `claude auth status`: `authMethod: claude.ai`, `subscriptionType: pro` — OAuth confirmed
- Bot token obtained from `buildar_notify.py`: `<REDACTED — see .env>` (token rotated 2026-05-18, old value scrubbed)

### Phase 2: Channels Plugin — NOT AVAILABLE AS CLI FLAG

- Telegram plugin `telegram@claude-plugins-official v0.0.6` IS installed
- BUT: `claude --help` shows NO `--channels` flag in v2.1.143
- The `--channels` flag referenced in Tomy's research appears to be a research preview not yet available in the public CLI build
- Decision: proceed with Architecture B (Python listener + wt.exe) — the correct path for cold-start anyway
- The Channels plugin (when/if `--channels` becomes available) can be added later by changing the wt.exe command in `open_claude_session()`

### Phase 3: Script Built — DONE

File: `D:\Claude Playground\scripts\telegram_listener.py`

Key implementation details:
- `ALLOWED_ID = 6283854178` — unauthorized senders silently dropped
- `TRIGGER_CMDS = {"/continue", "/start", "/resume"}` — case-insensitive matching
- Bot token from `TELEGRAM_BOT_TOKEN` env var, fallback to hardcoded value from `buildar_notify.py`
- Rate-limit guard reads `scratchpad/rate_limit_queue.json` — if `rate_limit_hit=true` and `resets_at` is in the future, replies with retry time instead of opening Claude
- Paths derived from `Path(__file__).resolve().parent.parent` so they work regardless of CWD
- Error handler for Conflict (duplicate poller) and NetworkError added
- `drop_pending_updates=True` — ignores message backlog when listener was offline
- `wt.exe` invocation: `wt new-tab --title "Andy - Telegram Resume" --startingDirectory "D:\Claude Playground" pwsh -NoExit -Command "Set-Location ...; $env:CI='true'; claude -c"`
- Log file: `scratchpad/telegram_listener.log`

### Phase 4: Manual Tests — ALL PASSED (logic level)

Six handler logic tests passed in isolation:

| Test | Expected | Result |
|------|----------|--------|
| Unauthorized sender (ID 999999) | Silent drop | PASS |
| Authorized `/continue`, no rate limit | Opens Claude | PASS |
| Authorized `/hello` (unknown cmd) | Polite error reply | PASS |
| Authorized `/continue`, rate-limited (2h queue) | Rate-limit reply with time | PASS |
| `/start` and `/resume` commands | Opens Claude | PASS |
| `/Continue` (mixed case) | Opens Claude (case-insensitive) | PASS |

Live Telegram tests (actual messages from phone) must be performed by Inon — cannot be automated.

Listener startup confirmed: connected to Telegram API, polled successfully with 200 OK responses.

### Phase 5: Task Scheduler — DONE

Task `AndyTelegramListener` registered and running.

Settings:
- Program: `C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\pythonw.exe`
- Arguments: `"D:\Claude Playground\scripts\telegram_listener.py"`
- Working dir: `D:\Claude Playground`
- Trigger: At Log On (user: Inon Baasov)
- Run as: Interactive user (RunLevel Limited)
- Multiple instances: IgnoreNew
- Restart: 3x, 1-minute interval
- Execution time limit: None (runs indefinitely)

Task state at handoff: `Running`
Process: `pythonw3.11` PID 39420, started 2026-05-16 15:57:29

### Phase 6: End-to-End — PARTIAL

The service is running. Telegram poll cycle confirmed (200 OK every ~32 seconds). Full end-to-end test (Inon's phone → Windows Terminal opens) cannot be verified without Inon sending a message. The wt.exe logic has been verified in prior session work and is identical to the researched blueprint.

---

## Known Limitations

1. **`--channels` flag not available** — The Tomy research referenced `claude -c --channels plugin:telegram@claude-plugins-official` but this flag does not exist in v2.1.143. The listener uses plain `claude -c`. When/if Channels becomes available, update one line in `open_claude_session()`.

2. **Process name is `pythonw3.11` not `pythonw`** — The Windows Store Python names its headless process `pythonw3.11`. Use `Get-Process -Name "pythonw3.11"` to check if listener is running, not `pythonw`.

3. **Live E2E test pending** — Inon must send `/continue` from his Telegram to confirm the full flow (message → Windows Terminal opens with Claude). The listener is running and ready.

4. **One-poller rule** — Only one process can poll per bot token. If you restart the listener, ensure no orphaned pythonw3.11 instances are running first: `Stop-Process -Name "pythonw3.11" -Force`.

5. **Rate-limit queue path** — The `check_rate_limit()` function reads the queue file written by `rate_limit_watchdog.py`. This works correctly as confirmed by unit tests. No changes to watchdog.

---

## Trigger Commands

All case-insensitive:
- `/continue` — primary trigger
- `/start` — alias
- `/resume` — alias

---

## Files Created/Modified

- **Created:** `D:\Claude Playground\scripts\telegram_listener.py`
- **Created:** Task Scheduler task `AndyTelegramListener`
- **Did NOT modify:** `buildar_notify.py`, `rate_limit_watchdog.py`
- **Did NOT install:** NSSM or any third-party service manager

---

## Deviations from Tomy's Blueprint

| Blueprint | Actual | Reason |
|-----------|--------|--------|
| `claude -c --channels plugin:telegram@claude-plugins-official` | `claude -c` only | `--channels` flag not in v2.1.143 CLI |
| `pythonw.exe` (short name) | `pythonw3.11.exe` (full path) | Windows Store Python uses versioned name; packages installed at PythonSoftwareFoundation path |
| `C:\Users\Inon Baasov\AppData\Local\Programs\Python\Python311\pythonw.exe` | `C:\Users\...\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\pythonw.exe` | Python installed via MS Store, not traditional installer |

---

## Next Steps for Andy

1. Ask Inon to send `/continue` from his Telegram to verify the full E2E flow
2. If Windows Terminal opens with Claude — task is done
3. If not — check `scratchpad/telegram_listener.log` for the trigger entry
4. Optionally delegate GitHub commit to a coder agent after QA

---

*Mack — Automation Engineer*
*2026-05-16*
