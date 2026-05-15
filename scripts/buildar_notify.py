"""
buildar_notify.py — BuildAR Pro build pipeline Telegram notifier
Usage:
  python scripts/buildar_notify.py done "BUILDAR-S1-001" "Silas schema complete"
  python scripts/buildar_notify.py ratelimit "BUILDAR-S1-002"
  python scripts/buildar_notify.py restart "BUILDAR-S1-002"
  python scripts/buildar_notify.py update "Some message"
"""
import os
import sys
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import zoneinfo

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8731882312:AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I")
CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "6283854178")
IL_TZ     = zoneinfo.ZoneInfo("Asia/Jerusalem")

def il_time(dt=None):
    dt = dt or datetime.now(IL_TZ)
    return dt.strftime("%H:%M")

def send(text):
    if not BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set.", file=sys.stderr)
        sys.exit(1)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": CHAT_ID, "text": text}).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if not result.get("ok"):
                print(f"Telegram error: {result}", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"ERROR sending message: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_done(task_id, detail=""):
    text = f"🟢 [BUILDAR] Task done: {task_id}\n{detail}"
    send(text)

def cmd_ratelimit(last_task=""):
    restart_dt = datetime.now(IL_TZ) + timedelta(hours=2, minutes=10)
    text = (
        f"⚠️ [BUILDAR] Rate limit hit. Session context full.\n"
        f"Expected restart: ~2h 10min from now ({il_time(restart_dt)} IL time)\n"
        f"Next session will pick up from: {last_task or '(unknown)'}"
    )
    send(text)

def cmd_restart(from_task="", active=""):
    active_line = f"Active: {active}" if active else ""
    text = (
        f"✅ [BUILDAR] Session restarted. Picking up from: {from_task or '(unknown)'}"
        + (f"\n{active_line}" if active_line else "")
    )
    send(text)

def cmd_update(message):
    send(f"📋 [BUILDAR] {message}")

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: buildar_notify.py <done|ratelimit|restart|update> [args...]")
        sys.exit(1)
    cmd = args[0]
    if cmd == "done":
        cmd_done(args[1] if len(args) > 1 else "", args[2] if len(args) > 2 else "")
    elif cmd == "ratelimit":
        cmd_ratelimit(args[1] if len(args) > 1 else "")
    elif cmd == "restart":
        cmd_restart(args[1] if len(args) > 1 else "", args[2] if len(args) > 2 else "")
    elif cmd == "update":
        cmd_update(args[1] if len(args) > 1 else "")
    else:
        print(f"Unknown command: {cmd}. Use: done | ratelimit | restart | update", file=sys.stderr)
        sys.exit(1)
    print(f"[OK] Notification sent ({cmd})")

if __name__ == "__main__":
    main()
