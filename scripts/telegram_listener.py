"""
telegram_listener.py — Andy Remote Trigger via Telegram
=======================================================
Usage:
  python "D:\\Claude Playground\\scripts\\telegram_listener.py"

Runs persistently in the background (use pythonw.exe for silent mode).
Listens for /continue, /start, /resume from Inon's Telegram.
When triggered, opens Windows Terminal with an interactive Claude session.

Security:
  - Only Inon's Telegram user ID (6283854178) can trigger actions.
  - Unauthorized senders get a silent drop (no reply).
  - Rate-limit guard: if a rate-limit queue file exists with a future
    resets_at timestamp, replies with an estimated retry time.

DO NOT run two instances — only one poller per bot token is allowed.
"""

import os
import sys
import subprocess
import logging
import json
from datetime import datetime
from pathlib import Path

try:
    import zoneinfo
    IL_TZ = zoneinfo.ZoneInfo("Asia/Jerusalem")
except ImportError:
    from datetime import timezone, timedelta
    IL_TZ = timezone(timedelta(hours=3))  # fallback: UTC+3

# pip install python-telegram-bot
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.error import Conflict, NetworkError

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN",
                              "8731882312:AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I")
ALLOWED_ID   = 6283854178          # Inon's Telegram user ID
TRIGGER_CMDS = {"/continue", "/start", "/resume"}

# Derive paths relative to this script so they work regardless of CWD
_ROOT      = Path(__file__).resolve().parent.parent   # D:\Claude Playground
WORKSPACE  = str(_ROOT)
LOG_FILE   = str(_ROOT / "scratchpad" / "telegram_listener.log")
QUEUE_FILE = str(_ROOT / "scratchpad" / "rate_limit_queue.json")

# ---------------------------------------------------------------------------
# Logging — always goes to file; also stdout so interactive runs show output
# ---------------------------------------------------------------------------
Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

_handlers = [logging.FileHandler(LOG_FILE, encoding="utf-8")]
if sys.stdout and sys.stdout.isatty():
    _handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=_handlers,
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate-limit guard
# ---------------------------------------------------------------------------
def check_rate_limit() -> str | None:
    """
    Returns a human-readable retry string if still rate-limited, else None.
    Reads scratchpad/rate_limit_queue.json. If rate_limit_hit is True and
    resets_at epoch is in the future, returns "HH:MM IL".
    """
    try:
        with open(QUEUE_FILE, encoding="utf-8") as f:
            q = json.load(f)
        if not q.get("rate_limit_hit"):
            return None
        resets_at = q.get("resets_at")
        if resets_at is None:
            return None
        now_ts = datetime.now().timestamp()
        if resets_at > now_ts:
            # Format retry time in Israel timezone
            reset_dt = datetime.fromtimestamp(resets_at, tz=IL_TZ)
            return reset_dt.strftime("%H:%M")
        return None
    except FileNotFoundError:
        return None
    except Exception as exc:
        log.warning(f"Rate-limit queue read error: {exc}")
        return None

# ---------------------------------------------------------------------------
# Open Claude session
# ---------------------------------------------------------------------------
def open_claude_session():
    """
    Fire wt.exe (Windows Terminal) with a new tab running claude -c.
    Non-blocking — returns immediately.
    Note: --channels flag is NOT available in claude 2.1.143; use plain claude -c.
    """
    log.info("Launching Windows Terminal → claude -c")
    try:
        subprocess.Popen([
            "wt", "new-tab",
            "--title", "Andy - Telegram Resume",
            "--startingDirectory", r"D:\Claude Playground",
            "pwsh", "-NoExit", "-File",
            r"D:\Claude Playground\scripts\open_claude.ps1",
        ])
        log.info("wt.exe launched successfully")
    except FileNotFoundError:
        log.error("wt.exe not found — Windows Terminal may not be installed")
    except Exception as exc:
        log.error(f"Failed to launch wt.exe: {exc}")

# ---------------------------------------------------------------------------
# Message handler
# ---------------------------------------------------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    user = update.effective_user
    user_id = user.id if user else None
    text = (update.message.text or "").strip()

    log.info(f"Message from user_id={user_id}: {text!r}")

    # --- Security: silent drop for unauthorized senders ---
    if user_id != ALLOWED_ID:
        log.warning(f"Unauthorized sender {user_id} — silent drop")
        return

    # --- Normalize: lowercase for command matching ---
    text_lower = text.lower()

    # --- Unknown command ---
    if text_lower not in TRIGGER_CMDS:
        log.info(f"Unknown command from authorized user: {text!r}")
        await update.message.reply_text(
            "Unknown command. Available commands:\n"
            "  /continue — resume last Claude session\n"
            "  /start    — same as /continue\n"
            "  /resume   — same as /continue"
        )
        return

    # --- Authorized trigger command ---
    log.info(f"Authorized trigger from {user_id}: {text!r}")

    # Rate-limit guard
    retry_at = check_rate_limit()
    if retry_at:
        log.info(f"Rate-limited — resets at {retry_at} IL. Not opening Claude.")
        await update.message.reply_text(
            f"Still rate limited. Claude cannot be started yet.\n"
            f"Retry at {retry_at} IL time."
        )
        return

    # All checks passed — trigger session
    await update.message.reply_text(
        "Starting Claude session on your machine... Check Windows Terminal."
    )
    open_claude_session()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    log.info("=" * 60)
    log.info("Andy Telegram Listener starting")
    log.info(f"Allowed user ID: {ALLOWED_ID}")
    log.info(f"Trigger commands: {TRIGGER_CMDS}")
    log.info(f"Rate-limit queue: {QUEUE_FILE}")
    log.info(f"Bot token (masked): {BOT_TOKEN[:10]}...")
    log.info("=" * 60)

    app = Application.builder().token(BOT_TOKEN).build()

    # Handle all text messages (commands and plain text)
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error handler — log Conflict (duplicate poller) as a clear warning
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        exc = context.error
        if isinstance(exc, Conflict):
            log.critical(
                "Conflict: another bot instance is already polling. "
                "Stop the duplicate process and restart this one. Exiting."
            )
            # Exit so Task Scheduler can restart after the other instance is gone
            import os as _os; _os._exit(1)
        elif isinstance(exc, NetworkError):
            log.warning(f"Network error (will retry): {exc}")
        else:
            log.error(f"Unhandled error: {exc}", exc_info=exc)

    app.add_error_handler(error_handler)

    log.info("Polling started (poll_interval=2s, timeout=30s)")
    app.run_polling(
        poll_interval=2.0,
        timeout=30,
        drop_pending_updates=True,   # ignore backlog from while listener was offline
    )

if __name__ == "__main__":
    main()
