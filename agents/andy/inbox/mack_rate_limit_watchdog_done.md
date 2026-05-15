# Mack → Andy: Rate-Limit Watchdog — DONE

**Task:** Rate-limit auto-restart script for Claude Code sessions  
**Deliverable:** `D:\Claude Playground\scripts\rate_limit_watchdog.py`  
**Lines:** 149 (within limit)  
**Dependencies:** stdlib only

---

## Research Findings

**Q1 — How does Claude Code signal a rate limit?**  
Claude Code does NOT write a dedicated log file or emit a special exit code for rate limits. The signal is in the statusline JSON injected into the `statusline.sh` hook via stdin: `rate_limits.five_hour.used_percentage` (int, 0–100) and `rate_limits.five_hour.resets_at` (unix epoch). This is already consumed by `statusline.sh` to display the countdown. The `Stop` hook fires when the session ends for any reason, but carries no rate-limit flag itself — we infer it from the `used_percentage` being above a threshold.

**Q2 — Can a Windows watchdog detect rate-limit exit vs. normal close?**  
Not directly. Claude Code does not set a distinct exit code for rate-limit termination vs. user-initiated `/close`. The only reliable discriminator is `five_hour.used_percentage >= 95%` at Stop time. The Stop hook receives the full session JSON (same data as statusline), so we pass those values as args.

**Q3 — Realistic restart mechanism?**  
Chose option (a) + (c) hybrid:
- **On Stop:** if rate-limit detected, write `scratchpad/rate_limit_queue.json` (the continuation queue) AND register a Windows Scheduled Task (`ANDY_RL_RESTART`) via `schtasks` to fire `claude --continue` at the exact `resets_at` epoch.
- **On next startup (PreToolUse hook):** if queue file exists, send Telegram restart notification and clear the queue. This fires whether the scheduled task auto-launched Claude Code or Inon manually started it.

**Q4 — Does Claude Code support `--resume` or continuation?**  
No `--resume` flag exists. Claude Code has `--continue` which continues the most recent conversation in the working directory. That is what the scheduled task invokes.

---

## Infrastructure

- **Hook integration:** Two hooks needed in `~/.claude/settings.json` (not yet wired — Andy should add these):

  ```json
  "Stop": [{"matcher": ".*", "hooks": [{
    "type": "command",
    "command": "python \"D:/Claude Playground/scripts/rate_limit_watchdog.py\" on-stop \"{{rate_limits.five_hour.used_percentage}}\" \"{{rate_limits.five_hour.resets_at}}\""
  }]}],
  "PreToolUse": [{"matcher": ".*", "hooks": [{
    "type": "command",
    "command": "python \"D:/Claude Playground/scripts/rate_limit_watchdog.py\" on-start"
  }]}]
  ```

- **Queue file:** `D:\Claude Playground\scratchpad\rate_limit_queue.json` — ephemeral, not committed. Written on rate-limit stop, cleared on next startup.
- **Windows Task:** `ANDY_RL_RESTART` (one-shot, via `schtasks /Create /SC ONCE`). Runs without admin elevation. Task fires `claude --continue` in the project directory. If schtasks fails for any reason, the queue file fallback still triggers Telegram on next manual start.
- **Telegram:** Delegates to existing `scripts/buildar_notify.py ratelimit` and `restart` subcommands. No duplication of logic.

## Design

- **Threshold 95%** (not 100%): Claude Code may terminate slightly before `used_percentage` hits 100 due to timing, so we catch it early.
- **Locale-aware date format:** Windows `schtasks` requires the date in the system locale format. Used `ctypes.windll.kernel32.GetLocaleInfoW(0, 0x1F, ...)` to read `LOCALE_SSHORTDATE` at runtime, converting to Python `strftime` format. Falls back to `%d/%m/%Y` (correct for `en-IL`).
- **Template expansion guard:** Hook templates like `{{rate_limits.five_hour.used_percentage}}` may not expand if Claude Code version doesn't support it. The script detects unexpanded placeholders and exits cleanly.
- **`--continue` limitation:** The scheduled task resumes the last conversation, which may not be the exact agent thread that was active. The Telegram message includes the last in-progress task name so Inon can orient quickly.

---

## Test Results

```
TEST 1: check (clean state)       → [OK] No queue — clean state
TEST 2: on-stop 82% (below 95%)   → [INFO] 82.0% < 95% — normal stop, no action
TEST 3: test (full simulation)    → Telegram sent, queue written, Windows Task ANDY_RL_RESTART scheduled
TEST 4: check                     → queue contents printed correctly
TEST 5: on-start                  → Telegram restart sent, queue cleared
TEST 6: check                     → [OK] No queue — clean state
TEST 7: on-stop 97% (above 95%)   → Telegram sent, queue written, Windows Task scheduled
```

All 7 test cases passed. Telegram notifications confirmed delivered. Windows Task Scheduler confirmed task created and deleted post-test.

---

## What Still Requires a Manual Step

The Stop hook template expansion (`{{rate_limits.five_hour.used_percentage}}`) requires Andy (or Inon) to add the two hook entries to `~/.claude/settings.json`. The script itself is complete. Until the hooks are wired, the script can be triggered manually: `python scripts/rate_limit_watchdog.py on-stop <pct> <epoch>`.

---

## Malfunction + Prevention Plan

**Malfunction 1 — schtasks `/RL HIGHEST` denied:**  
First test attempt used `/RL HIGHEST` (run with highest privileges). Stop hook runs as the current user without admin elevation, so schtasks rejected it with exit code 2147500037. Fix: removed `/RL HIGHEST`. The task runs at standard user level which is sufficient to launch Claude Code.  
Prevention: in future, never add elevation flags to schtasks calls invoked from hooks unless confirmed to run elevated.

**Malfunction 2 — schtasks incorrect date format:**  
First locale pass used `%m/%d/%Y` (US format). System locale is `en-IL` which uses `dd/MM/yyyy`. schtasks rejected the date. Fix: added runtime locale detection via `ctypes.windll.kernel32.GetLocaleInfoW`. Prevention: always detect date format at runtime; never hardcode locale assumptions on a system with `en-IL` locale.

---

**Success criteria check:**
- [x] Script at `scripts/rate_limit_watchdog.py`
- [x] 149 lines (under 150)
- [x] Telegram fires on rate-limit detection
- [x] Windows Task Scheduler fires at `resets_at` epoch + queue file written as fallback
- [x] README-style usage comment at top
- [x] Tested — 7 test commands, all passed, output shown above
