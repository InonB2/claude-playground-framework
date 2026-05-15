"""
rate_limit_watchdog.py — Claude Code rate-limit detector and restart scheduler

USAGE:
  python scripts/rate_limit_watchdog.py on-stop <used_pct> <resets_at_epoch>
      Stop hook: if pct >= 95, send Telegram alert, write queue file,
      schedule Windows Task to relaunch claude --continue at resets_at time.

  python scripts/rate_limit_watchdog.py on-start
      Startup hook: if queue file exists, send Telegram restart notification
      with last-task context, then clear the queue file.

  python scripts/rate_limit_watchdog.py test
      Dry-run: simulate 100% rate-limit, +130 min restart. Sends Telegram,
      writes queue file, creates ANDY_RL_RESTART scheduled task.

  python scripts/rate_limit_watchdog.py check
      Print queue file contents or "clean state".

HOOK SETUP in ~/.claude/settings.json → "hooks":
  "Stop":  python "D:/Claude Playground/scripts/rate_limit_watchdog.py"
               on-stop "{{rate_limits.five_hour.used_percentage}}"
                        "{{rate_limits.five_hour.resets_at}}"
  "PreToolUse": python "D:/Claude Playground/scripts/rate_limit_watchdog.py" on-start

HOW IT WORKS — Infrastructure:
  Stop hook fires on any session end. If five_hour.used_percentage >= 95%,
  we treat this as a rate-limit termination: write scratchpad/rate_limit_queue.json,
  send Telegram ratelimit alert, and register a one-shot Windows Task (schtasks)
  to fire `claude --continue` at the exact resets_at epoch. The scheduled task
  runs without admin elevation (/RL HIGHEST is omitted intentionally).

  Design decisions:
  - Threshold 95% (not 100%): session may terminate before full saturation.
  - Claude Code has no --resume flag; --continue continues last conversation.
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
NOTIFY     = os.path.join(ROOT, "scripts", "buildar_notify.py")
TASKS      = os.path.join(ROOT, "tasks", "active_tasks.json")
CLAUDE_EXE = r"C:\Users\Inon Baasov\AppData\Roaming\npm\claude.cmd"
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

def schedule_task(epoch):
    local = datetime.fromtimestamp(epoch, tz=IL_TZ).astimezone().replace(tzinfo=None)
    # Detect locale short-date format via Windows API (avoids locale mismatch)
    try:
        buf = ctypes.create_unicode_buffer(80)
        ctypes.windll.kernel32.GetLocaleInfoW(0, 0x1F, buf, 80)
        fmt = buf.value.replace("yyyy","%Y").replace("MM","%m").replace("dd","%d")
        date_str = local.strftime(fmt)
    except Exception:
        date_str = local.strftime("%d/%m/%Y")
    action = (f'cmd /c "cd /d {ROOT} && "{CLAUDE_EXE}" --continue --print '
              f'"/start Session restarted after rate-limit window. Continue active tasks.""')
    r = subprocess.run(["schtasks","/Create","/F","/TN",TASK_NAME,"/TR",action,
                        "/SC","ONCE","/SD",date_str,"/ST",local.strftime("%H:%M")],
                       capture_output=True, text=True, timeout=15)
    if r.returncode == 0: print(f"[OK] Task '{TASK_NAME}' scheduled at {local.strftime('%H:%M')} local")
    else: print(f"[WARN] schtasks failed: {r.stderr.strip()} — queue still active", file=sys.stderr)

def on_stop(args):
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

def check(_):
    q = read_queue()
    if not q: print("[OK] No queue — clean state")
    else: print("\n".join(f"  {k}: {v}" for k,v in q.items()))

CMDS = {"on-stop": on_stop, "on-start": on_start, "test": test, "check": check}

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in CMDS: print(__doc__); sys.exit(0)
    CMDS[args[0]](args[1:])
