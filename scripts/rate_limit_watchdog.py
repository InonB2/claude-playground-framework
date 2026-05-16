"""
rate_limit_watchdog.py — Claude Code rate-limit detector and restart scheduler

USAGE:
  python scripts/rate_limit_watchdog.py on-stop <used_pct> <resets_at_epoch>
      Stop hook: log args received; if pct >= 95, send Telegram alert, write queue
      file, schedule Windows Task ANDY_RL_RESTART to fire rl_restart.bat at resets_at.

  python scripts/rate_limit_watchdog.py on-start
      Startup hook: if queue file exists, send Telegram restart notification
      with last-task context, then clear the queue file.

  python scripts/rate_limit_watchdog.py test
      Dry-run: simulate 100% rate-limit, +130 min restart. Sends Telegram,
      writes queue file, creates ANDY_RL_RESTART scheduled task.

  python scripts/rate_limit_watchdog.py fire-test
      Schedule ANDY_RL_RESTART to fire in 3 minutes. Use to verify that the
      scheduled task actually executes (check scratchpad/watchdog_stop_log.json
      and Telegram for restart notification after 2 min).

  python scripts/rate_limit_watchdog.py check
      Print queue file contents or "clean state".

HOOK SETUP in ~/.claude/settings.json -> "hooks":
  "Stop":  python "D:/Claude Playground/scripts/rate_limit_watchdog.py"
               on-stop "{{rate_limits.five_hour.used_percentage}}"
                        "{{rate_limits.five_hour.resets_at}}"
  "PreToolUse": python "D:/Claude Playground/scripts/rate_limit_watchdog.py" on-start

HOW IT WORKS — Infrastructure:
  Stop hook fires on any session end. Args are logged to scratchpad/watchdog_stop_log.json
  every time so template expansion can be verified. If five_hour.used_percentage >= 95%,
  write scratchpad/rate_limit_queue.json, send Telegram ratelimit alert, and register a
  one-shot Windows Task (ANDY_RL_RESTART) to fire scripts/rl_restart.bat at the exact
  resets_at epoch.

  The restart batch file runs claude --continue --print "/start ...", which triggers the
  on-start PreToolUse hook. That hook reads the queue, sends a Telegram restart
  notification, and clears the queue.

  Design decisions:
  - Threshold 95% (not 100%): session may terminate before full saturation.
  - Batch file (rl_restart.bat) avoids nested-quote fragility in schtasks /TR.
  - Queue file persists if schtasks fails, so the next manual start still fires
    the Telegram restart notification automatically via on-start.
  - Pure stdlib, no external deps.
"""

import sys, os, json, subprocess, ctypes
from datetime import datetime, timedelta
try:
    import zoneinfo; IL_TZ = zoneinfo.ZoneInfo("Asia/Jerusalem")
except ImportError:
    import pytz; IL_TZ = pytz.timezone("Asia/Jerusalem")  # type: ignore

ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_FILE = os.path.join(ROOT, "scratchpad", "rate_limit_queue.json")
DIAG_LOG   = os.path.join(ROOT, "scratchpad", "watchdog_stop_log.json")
NOTIFY     = os.path.join(ROOT, "scripts", "buildar_notify.py")
TASKS      = os.path.join(ROOT, "tasks", "active_tasks.json")
RESTART_BAT = os.path.join(ROOT, "scripts", "rl_restart.bat")
TASK_NAME  = "ANDY_RL_RESTART"
THRESHOLD  = 95  # percent

il_now = lambda: datetime.now(IL_TZ)
il_str = lambda epoch: datetime.fromtimestamp(epoch, tz=IL_TZ).strftime("%H:%M")

def next_task():
    try:
        data = json.load(open(TASKS, encoding="utf-8"))
        active = [t for t in data.get("tasks", [])
                  if t.get("status") in ("in-progress","in_progress","partial","pending")]
        return active[0].get("title","") if active else ""
    except Exception: return ""

def telegram(cmd, *args):
    r = subprocess.run([sys.executable, NOTIFY, cmd, *args],
                       capture_output=True, text=True, timeout=15)
    if r.returncode: print(f"[WARN] Telegram {cmd}: {r.stderr.strip()}", file=sys.stderr)
    else: print(f"[OK] Telegram sent ({cmd})")

def write_queue(epoch, task):
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    json.dump({"rate_limit_hit": True, "resets_at": epoch, "resets_at_il": il_str(epoch),
               "last_task": task, "written_at": il_now().isoformat()},
              open(QUEUE_FILE, "w", encoding="utf-8"), indent=2)
    print(f"[OK] Queue file written: {QUEUE_FILE}")

def read_queue():
    try: return json.load(open(QUEUE_FILE, encoding="utf-8"))
    except FileNotFoundError: return {}
    except Exception as e: print(f"[WARN] {e}", file=sys.stderr); return {}

def del_queue():
    try: os.remove(QUEUE_FILE); print("[OK] Queue cleared")
    except FileNotFoundError: pass

def write_diag(raw_args):
    """Always log on-stop invocation — proves whether {{...}} templates expanded."""
    try:
        os.makedirs(os.path.dirname(DIAG_LOG), exist_ok=True)
        entry = {
            "timestamp": il_now().isoformat(),
            "raw_args": list(raw_args),
            "templates_expanded": not any(
                a.startswith("{{") for a in raw_args
            ) if raw_args else False,
        }
        json.dump(entry, open(DIAG_LOG, "w", encoding="utf-8"), indent=2)
    except Exception as e:
        print(f"[WARN] diag log: {e}", file=sys.stderr)

def schedule_task(epoch):
    local = datetime.fromtimestamp(epoch, tz=IL_TZ).astimezone().replace(tzinfo=None)
    try:
        buf = ctypes.create_unicode_buffer(80)
        ctypes.windll.kernel32.GetLocaleInfoW(0, 0x1F, buf, 80)
        fmt = buf.value.replace("yyyy","%Y").replace("MM","%m").replace("dd","%d")
        date_str = local.strftime(fmt)
    except Exception:
        date_str = local.strftime("%d/%m/%Y")
    r = subprocess.run(
        ["schtasks", "/Create", "/F", "/TN", TASK_NAME,
         "/TR", f'"{RESTART_BAT}"',
         "/SC", "ONCE", "/SD", date_str, "/ST", local.strftime("%H:%M")],
        capture_output=True, text=True, timeout=15
    )
    if r.returncode == 0:
        print(f"[OK] Task '{TASK_NAME}' scheduled at {local.strftime('%H:%M')} local")
    else:
        print(f"[WARN] schtasks failed: {r.stderr.strip()} — queue still active", file=sys.stderr)

def on_stop(args):
    write_diag(args)  # always log — diagnostic for template expansion
    if len(args) < 2: print("[INFO] on-stop: no args (hook template not expanded)"); return
    PLACEHOLDER = ("{{rate_limits.five_hour.used_percentage}}", "{{rate_limits.five_hour.resets_at}}", "0", "")
    try:
        pct = float(args[0]) if args[0] not in PLACEHOLDER else 0
        epoch = float(args[1]) if args[1] not in PLACEHOLDER else 0
    except ValueError: print("[INFO] on-stop: non-numeric args"); return
    if pct < THRESHOLD: print(f"[INFO] {pct}% < {THRESHOLD}% — normal stop, no action"); return
    if not epoch: epoch = (il_now() + timedelta(hours=2, minutes=10)).timestamp()
    task = next_task()
    print(f"[INFO] Rate limit {pct}%. Restart ~{il_str(epoch)} IL. Task: {task}")
    telegram("ratelimit", task)
    write_queue(epoch, task)
    schedule_task(epoch)

def on_start(_):
    q = read_queue()
    if not q.get("rate_limit_hit"): return
    print(f"[INFO] Queue found — restarted after rate-limit. Last: {q.get('last_task','?')}")
    telegram("restart", q.get("last_task",""), f"rate window cleared (was {q.get('resets_at_il','?')} IL)")
    del_queue()

def test(_):
    print("=== WATCHDOG TEST ===")
    epoch = (il_now() + timedelta(minutes=130)).timestamp()
    task = next_task() or "TEST TASK"
    print(f"Simulating 100% rate-limit. Restart at {il_str(epoch)} IL. Task: {task}")
    telegram("ratelimit", f"[TEST] {task}")
    write_queue(epoch, f"[TEST] {task}")
    schedule_task(epoch)
    print(f"=== DONE — queue: {QUEUE_FILE} | task: {TASK_NAME} ===")

def fire_test(_):
    """Schedule ANDY_RL_RESTART to fire in 3 minutes for execution verification."""
    print("=== FIRE-TEST: scheduling ANDY_RL_RESTART in 2 minutes ===")
    epoch = (il_now() + timedelta(minutes=3)).timestamp()
    task = next_task() or "FIRE-TEST TASK"
    write_queue(epoch, f"[FIRE-TEST] {task}")
    schedule_task(epoch)
    print(f"[INFO] Task will fire at {il_str(epoch)} IL (about 3 min from now)")
    print("[INFO] Check Telegram for restart notification + scratchpad/rate_limit_queue.json cleanup")
    print("=== DONE ===")

def check(_):
    q = read_queue()
    if not q: print("[OK] No queue — clean state")
    else: print("\n".join(f"  {k}: {v}" for k,v in q.items()))
    # Also show diag log if present
    try:
        d = json.load(open(DIAG_LOG, encoding="utf-8"))
        print(f"\n[DIAG] Last on-stop call: {d.get('timestamp','?')}")
        print(f"  raw_args: {d.get('raw_args','?')}")
        print(f"  templates_expanded: {d.get('templates_expanded','?')}")
    except FileNotFoundError:
        print("\n[DIAG] No stop-log yet (on-stop never fired in this install)")

CMDS = {"on-stop": on_stop, "on-start": on_start, "test": test,
        "fire-test": fire_test, "check": check}

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in CMDS: print(__doc__); sys.exit(0)
    CMDS[args[0]](args[1:])
