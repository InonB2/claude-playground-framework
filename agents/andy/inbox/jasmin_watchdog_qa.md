# Jasmin — Watchdog QA Sign-Off
Date: 2026-05-16
Verdict: PASS WITH NOTES

---

## Infrastructure

**1. PLACEHOLDER tuple — on_stop unexpanded guard**
PASS. Line 137: `PLACEHOLDER = ("{{rate_limits.five_hour.used_percentage}}", "{{rate_limits.five_hour.resets_at}}", "0", "")`. Both template strings, the literal "0", and empty string are caught. If either arg matches PLACEHOLDER, `pct` or `epoch` is set to 0, causing an early return (pct < THRESHOLD = 95). Additionally, `len(args) < 2` guard on line 136 exits cleanly before the PLACEHOLDER check. Full unexpanded guard confirmed.

**2. write_diag — always writes, silent on exception**
PASS. Lines 99–112: called unconditionally as the first action in `on_stop` (line 135). Entire body wrapped in `try/except Exception`, which prints a warning to stderr but does not raise. Hook cannot crash from a diag-write failure.

**3. schedule_task — uses rl_restart.bat, correctly quoted with spaces in path**
PASS. Line 125: `/TR` argument is `f'"{RESTART_BAT}"'` — the path is wrapped in an inner double-quote pair so that the space in "D:\Claude Playground\scripts\rl_restart.bat" is handled by schtasks. `RESTART_BAT` constant (line 62) resolves to the `.bat` file, not an inline `cmd /c` chain. No nested-quote fragility.

**4. rl_restart.bat — correct invocation, ASCII-only comments, correct paths**
PASS. Line 6: `python "D:\Claude Playground\scripts\rate_limit_watchdog.py" on-start` — no `claude --continue`. Comments on lines 2–4 use ASCII only (no Unicode, no smart quotes). `cd /d "D:\Claude Playground"` on line 5 sets working directory correctly before the Python call. File is 6 lines, clean.

**5. Hook wiring — Stop has both notify hook AND watchdog on-stop; PreToolUse has on-start**
PASS. settings.json Stop array (lines 86–106): two entries — first fires `notify.ps1` (desktop toast), second fires `rate_limit_watchdog.py on-stop` with both template args. PreToolUse array (lines 66–84): two entries — first fires `token_warn.sh`, second fires `rate_limit_watchdog.py on-start`. All four hooks wired correctly.

**6. Constants correctness**
PASS.
- `QUEUE_FILE`: `<ROOT>/scratchpad/rate_limit_queue.json` — correct
- `DIAG_LOG`: `<ROOT>/scratchpad/watchdog_stop_log.json` — correct
- `NOTIFY`: `<ROOT>/scripts/buildar_notify.py` — correct
- `TASKS`: `<ROOT>/tasks/active_tasks.json` — correct
- `RESTART_BAT`: `<ROOT>/scripts/rl_restart.bat` — correct
- `TASK_NAME`: `"ANDY_RL_RESTART"` — matches schtasks and fire-test docstring
- `THRESHOLD`: `95` — correct

**7. next_task() — safe read, returns "" on any failure**
PASS. Lines 69–75: entire body in `try/except Exception: return ""`. Handles missing file, malformed JSON, missing keys, empty list. Returns `active[0].get("title","")` — uses `.get` with default, safe even if "title" key absent. Status filter includes "in-progress", "in_progress", "partial", "pending" — covers known variants.

**8. telegram() — warns on failure, does NOT crash**
PASS. Lines 77–81: `subprocess.run` with `capture_output=True`, `timeout=15`. Non-zero returncode prints to stderr with `[WARN]` prefix; no `sys.exit`, no raise. The function returns `None` in both success and failure paths. Hook pipeline cannot be terminated by a Telegram delivery failure.

---

## Design

**9. on_start fires on every PreToolUse but is no-op without queue**
PASS. Lines 150–155: first action is `q = read_queue()`. If `rate_limit_hit` key is absent or falsy, function returns immediately. `read_queue()` returns `{}` on FileNotFoundError (no queue file). Normal sessions incur only a file-stat miss per tool call — negligible overhead.

**10. Threshold is 95% — correct for near-limit detection**
PASS. `THRESHOLD = 95` on line 64. Rationale documented in docstring: "session may terminate before full saturation." Comparison on line 142 is strict less-than (`pct < THRESHOLD`), so exactly 95% triggers action. Correct.

**11. Fallback epoch (+2h10m) fires if resets_at is 0 or missing**
PASS. Line 143: `if not epoch: epoch = (il_now() + timedelta(hours=2, minutes=10)).timestamp()`. Covers both the `PLACEHOLDER` path (epoch set to 0) and a genuine zero from the hook. The 2h10m offset is a reasonable conservative estimate for the 5-hour window rollover. Correct.

**12. fire-test schedules for +3 minutes**
NOTE — minor discrepancy. The docstring on lines 17–20 states "Schedule ANDY_RL_RESTART to fire in 2 minutes." The inline docstring on line 168 also says "2 minutes." However, the implementation on line 170 uses `timedelta(minutes=3)` and line 174 prints "about 3 min from now." The actual scheduling is +3 minutes. The docstring is stale by 1 minute. Functionally this is not a defect — 3 minutes is equally valid for production testing — but the user-visible doc says 2 and the code does 3. Recommend updating the module-level docstring to "3 minutes" for accuracy. Flagged as PASS WITH NOTES.

**13. check command shows both queue AND diag log**
PASS. Lines 178–189: first block prints queue contents or "clean state"; second block reads `DIAG_LOG` and prints timestamp, raw_args, and templates_expanded. `FileNotFoundError` on the diag log is caught and prints a clear message. Sufficient for next-session verification.

---

## Security

**14. No shell=True in any subprocess call**
PASS. Two `subprocess.run` calls in the file:
- Line 78 (`telegram`): `[sys.executable, NOTIFY, cmd, *args]` — list form, no `shell=True`
- Lines 123–128 (`schedule_task`): `["schtasks", "/Create", ...]` — list form, no `shell=True`
No shell injection vector in either call.

**15. No user-controlled data written unsanitized to disk**
PASS. Data written to `QUEUE_FILE` (line 85–87) and `DIAG_LOG` (line 103–110) originates from:
- `args` passed as hook template values (rate-limit metrics from Claude Code runtime — not user input)
- `next_task()` reading from `active_tasks.json` (operator-controlled file)
- `il_now().isoformat()` (system clock)
All data is serialized via `json.dump` — JSON encoding prevents injection. No raw string interpolation into file writes.

**16. Queue file path pinned under scratchpad/ — no traversal risk**
PASS. `QUEUE_FILE` is constructed via `os.path.join(ROOT, "scratchpad", "rate_limit_queue.json")` where `ROOT` is derived from `os.path.abspath(__file__)` at import time (line 57). Path is fully resolved at startup, not constructed from any runtime input. No traversal risk.

---

## Known gap

**Template expansion in production rate-limit event (not yet verified)**
The `{{rate_limits.five_hour.used_percentage}}` and `{{rate_limits.five_hour.resets_at}}` tokens must be expanded by the Claude Code hook engine at the moment a genuine rate-limit Stop fires. This has NOT been verified in a live rate-limit scenario — it requires the session to actually hit ≥95% on the 5-hour window.

The diagnostic instrument is in place: `scratchpad/watchdog_stop_log.json` is written on every Stop hook call and contains `raw_args` and `templates_expanded: true/false`. After the first real rate-limit event, check this file to confirm expansion. If `templates_expanded` is `false`, the templates are not supported in the Stop hook context and the watchdog's trigger path is broken (though the diag/no-op path would still function correctly).

This is the only unverified path. Everything else has been confirmed via Andy's test run.

---

## Summary

All 16 checklist items: **15 PASS, 1 PASS WITH NOTES** (item 12 — fire-test docstring says "2 minutes", code schedules 3 minutes; cosmetic only).

The rate-limit watchdog system is production-ready. Infrastructure is solid: PLACEHOLDER guard, silent diag logging, safe schtasks wiring, and a clean bat file. Design decisions are sound: 95% threshold, fallback epoch, no-op on-start, and a useful `check` command. Security posture is clean: no shell=True, no unsanitized writes, no traversal vectors.

**Recommendation:** Fix the "2 minutes" → "3 minutes" wording in the module docstring (lines 19 and 168). Not blocking production deployment.

**Blocking gap:** None. The template-expansion verification is flagged as a known deferred check, not a blocker — the PLACEHOLDER guard ensures safe behavior even if templates never expand.

**QA sign-off: Jasmin — PASS WITH NOTES**
Task may be moved to Tested. Andy may mark Done after noting the docstring fix recommendation.
