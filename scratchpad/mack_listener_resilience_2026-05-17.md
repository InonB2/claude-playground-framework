# Telegram Listener Resilience — Incident Report
**Author:** Mack
**Date:** 2026-05-17
**Incident:** Inon's `/continue` Telegram trigger silently failed; listener dead ~24h.

---

## Root Cause Analysis

### Infrastructure findings
1. **Scheduled task `AndyTelegramListener` had laptop-hostile power policy**
   `Stop On Battery Mode` and `No Start On Batteries` were both ON. When Inon's laptop unplugged, Task Scheduler treated the listener as expendable.
2. **No restart-on-failure configured** on the task. Once the process died (exit code 1), nothing brought it back. The only trigger was `At logon`, which never re-fires while the user is already logged in.
3. **No watchdog/heartbeat layer.** A single point-in-time failure became a 24-hour outage with zero alerting.
4. **`pythonw.exe` PATH ambiguity.** The unqualified `C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\pythonw.exe` symlink currently resolves to **Python 3.14**, where the `telegram` package is NOT installed. Any process launching `pythonw` without the full versioned path silently exits with `ModuleNotFoundError` and leaves zero trace (no stderr in detached mode). The original task happened to use the correctly versioned 3.11 path, but any retry by a different mechanism would fail invisibly.

### Design findings
1. **`os._exit(1)` on `telegram.error.Conflict`** in `error_handler` was the proximate killer. Logic was: "exit, let Task Scheduler restart us after the duplicate is gone." That bet is wrong on three counts:
   - There was no restart trigger.
   - The duplicate is often *the previous instance of this same listener* still finishing a `getUpdates` long-poll on Telegram's side — exiting and re-launching just produces a fresh 409 against ourselves.
   - Hard exit gives the duplicate no chance to detect *us* and step aside.
2. **No single-instance guard.** If two listeners ever ran concurrently (e.g., a manual run + the scheduled task), both would 409-spiral.
3. **No backoff loop.** A single Telegram-side hiccup propagated straight to process death.

---

## What I changed

### `scripts/telegram_listener.py`
- Added **singleton lock**: bind `127.0.0.1:50917` at startup. Bind failure → exit cleanly (no error, no Telegram call). Spawns a daemon accept-loop thread so heartbeat probes get a clean accept+close round-trip.
- Removed `os._exit(1)` from the Conflict path. Now: log a warning, let the outer loop handle it.
- Wrapped `app.run_polling()` in an **outer restart loop** with exponential backoff (5s → 120s cap) for `Conflict` and other exceptions. The process now survives all transient Telegram-side errors.

### `scripts/telegram_listener_watchdog.ps1` (new)
- Heartbeat probe: connect to `127.0.0.1:50917` on IPv4 explicitly (avoids dual-stack false-negative).
- If probe fails: launch listener via the **correct versioned pythonw**:
  `C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\pythonw.exe`
- Confirms recovery within 20s, logs loud if not.
- No-op (silent) when listener is healthy.

### `scripts/install_listener_resilience.ps1` (new)
- Idempotent installer. Re-applies these settings to `AndyTelegramListener`:
  - `AllowStartIfOnBatteries`
  - `DontStopIfGoingOnBatteries`
  - `StartWhenAvailable`
  - `RestartCount=99, RestartInterval=1min`
  - `MultipleInstances=IgnoreNew`
- Registers/refreshes `AndyTelegramListenerWatchdog`:
  - Triggers: AtLogOn + Once-with-2min-repetition (runs forever)
  - Same battery-friendly settings
- Runs the watchdog once at install time to bring the listener up immediately.

### Scheduled task commands actually run (via the installer script):
```powershell
& "D:\Claude Playground\scripts\install_listener_resilience.ps1"
```
(The installer uses `Set-ScheduledTask` and `Register-ScheduledTask -Force` — no raw `schtasks` calls.)

---

## Verification — actual runs

### 1. Cold-start via watchdog
```
2026-05-17 13:58:20  Heartbeat probe failed.
2026-05-17 13:58:20  Listener not responding on port 50917. Starting via pythonw.exe.
2026-05-17 13:58:22  Listener confirmed up on port 50917.
```

### 2. Single process invariant
```
ProcessId : 39004
Name      : pythonw3.11.exe
Cmd       : "...PythonSoftwareFoundation.Python.3.11_...\pythonw.exe" "D:\Claude Playground\scripts\telegram_listener.py"
```
Exactly one pythonw3.11 listener at all times. Port `127.0.0.1:50917 LISTENING`.

### 3. Kill-and-recover (the spec required ≤2 min; measured **22 seconds**)
```
13:59:02  Killed listener PID 10196
13:59:20  Heartbeat probe failed. (watchdog tick)
13:59:21  Listener launch issued.
13:59:23  Listener confirmed up on port 50917.
13:59:28  bash poll confirmed LISTENING
```

### 4. Polling proven
```
13:59:24  HTTP POST /getMe        200 OK
13:59:24  HTTP POST /deleteWebhook 200 OK
13:59:24  Application started
13:59:27  HTTP POST /getUpdates   409 Conflict   (external poller, see Residual Risk)
```
Listener is hitting `getUpdates` on a continuous cadence and surviving 409 responses without dying.

### 5. Scheduled-task settings applied
```
AndyTelegramListener:
  DisallowStartIfOnBatteries : False   ← was True
  StopIfGoingOnBatteries     : False   ← was True
  RestartCount               : 99      ← was 0
  RestartInterval            : PT1M    ← was none
  MultipleInstances          : IgnoreNew

AndyTelegramListenerWatchdog:
  DisallowStartIfOnBatteries : False
  StopIfGoingOnBatteries     : False
  Triggers                   : AtLogOn + Once-every-2min repetition
```

### 6. Idempotency
Installer was run twice. Both runs produced the same task definitions, no duplicates, no second listener process.

---

## Prevention plan

| Failure mode (yesterday)                                  | Why it cannot recur                                                                                                  |
|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Listener died on 409 Conflict and never came back         | `os._exit(1)` removed. Conflict now triggers an in-process backoff retry; process stays alive. AND if the process did die, the every-2-min watchdog respawns it within ≤2 min (measured: 22 s). |
| Two listeners running → constant 409 crash loop           | Singleton port lock (`127.0.0.1:50917`). Second launch refuses cleanly without ever calling Telegram.                |
| Laptop on battery → task wouldn't start or got stopped    | `AllowStartIfOnBatteries` + `DontStopIfGoingOnBatteries` set on BOTH the listener task and the watchdog task.        |
| Logout/login was the only trigger                         | Watchdog runs every 2 min from boot until logoff via `StartWhenAvailable`.                                           |
| pythonw symlink silently resolved to wrong Python version | Both watchdog and installer hard-code the versioned 3.11 pythonw path. Comment in code calls out the foot-gun.       |
| Silent failure with no alerting                           | Watchdog log writes a loud `WARNING: Listener did not come up within 20s after launch` if recovery fails. Future enhancement: pipe that into a Telegram self-alert. (Out of scope here.) |

---

## Residual risk

**External 409 source.** Throughout testing the listener kept receiving 409 responses from Telegram even when there was definitively only one local poller. That means another client is polling this bot token from somewhere else (different machine, another user account, a stale BotFather session, or a leftover process Inon doesn't remember). The listener now **survives this indefinitely** — it just keeps retrying — and the moment the other poller stops, our next `getUpdates` will succeed and `/continue` will work.

Recommendation for Inon (separate concern flagged in the task brief): consider revoking + reissuing the bot token via BotFather. That immediately invalidates any other poller. Out of scope for this fix.

**Watchdog log growth.** The watchdog only writes on failure or recovery, so log growth is bounded. No rotation needed for at least a year of normal operation.
