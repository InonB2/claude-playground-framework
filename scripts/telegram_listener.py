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
import time
import socket
import atexit
import threading
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

# pip install python-telegram-bot python-dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.error import Conflict, NetworkError
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# Derive paths relative to this script so they work regardless of CWD
_ROOT      = Path(__file__).resolve().parent.parent   # D:\Claude Playground
WORKSPACE  = str(_ROOT)
LOG_FILE   = str(_ROOT / "scratchpad" / "telegram_listener.log")
QUEUE_FILE = str(_ROOT / "scratchpad" / "rate_limit_queue.json")
ENV_FILE   = _ROOT / ".env"

# Load .env so TELEGRAM_BOT_TOKEN is available. Policy (2026-05-18):
# token MUST come from environment only — no hardcoded fallback. This makes
# leaking the token via a committed file mechanically impossible.
load_dotenv(ENV_FILE)

BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    sys.stderr.write(
        f"FATAL: TELEGRAM_BOT_TOKEN not set. Expected in env or {ENV_FILE}.\n"
        "Refusing to start — no fallback token is permitted.\n"
    )
    sys.exit(2)

ALLOWED_ID   = 6283854178          # Inon's Telegram user ID
TRIGGER_CMDS = {"/continue", "/start", "/resume"}

# Single-instance lock — TCP loopback bind. If the port is taken, another
# listener owns it; we exit cleanly without ever calling Telegram.getUpdates,
# which is what creates the 409 Conflict storm.
SINGLETON_PORT = 50917  # arbitrary, well above ephemeral range
_singleton_socket: socket.socket | None = None

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
# Single-instance guard
# ---------------------------------------------------------------------------
def acquire_singleton_lock() -> bool:
    """
    Bind to a fixed loopback port to guarantee only one listener per machine.
    Returns True if we got the lock; False if another instance is already running.
    The socket lives in module-global state so the OS releases it on process exit.

    Also spawns a daemon accept-loop thread so heartbeat probes get a clean
    accept+close round-trip instead of stale CLOSE_WAIT/SYN_SENT entries.
    """
    global _singleton_socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", SINGLETON_PORT))
        s.listen(5)
        _singleton_socket = s
        atexit.register(_release_singleton_lock)

        def _accept_loop():
            while True:
                try:
                    conn, _ = s.accept()
                    try:
                        conn.close()
                    except Exception:
                        pass
                except OSError:
                    return  # socket closed (process shutting down)
                except Exception:
                    return

        t = threading.Thread(target=_accept_loop, name="singleton-heartbeat", daemon=True)
        t.start()
        return True
    except OSError as exc:
        log.warning(
            f"Singleton lock held by another process on port {SINGLETON_PORT} "
            f"({exc}). Exiting without polling — avoids Telegram 409 Conflict."
        )
        try:
            s.close()
        except Exception:
            pass
        return False

def _release_singleton_lock() -> None:
    global _singleton_socket
    if _singleton_socket is not None:
        try:
            _singleton_socket.close()
        except Exception:
            pass
        _singleton_socket = None

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
def _build_app():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error handler — Conflict is now soft: log + let outer loop back off and retry.
    # Hard-exit was the historical root cause of the listener disappearing for hours.
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        exc = context.error
        if isinstance(exc, Conflict):
            log.warning(
                "Conflict from Telegram (duplicate poller suspected). "
                "Will be handled by outer restart loop with backoff."
            )
        elif isinstance(exc, NetworkError):
            log.warning(f"Network error (will retry): {exc}")
        else:
            log.error(f"Unhandled error: {exc}", exc_info=exc)

    app.add_error_handler(error_handler)
    return app

def main():
    log.info("=" * 60)
    log.info("Andy Telegram Listener starting")
    log.info(f"Allowed user ID: {ALLOWED_ID}")
    log.info(f"Trigger commands: {TRIGGER_CMDS}")
    log.info(f"Rate-limit queue: {QUEUE_FILE}")
    log.info(f"Bot token (masked): {BOT_TOKEN[:10]}...")
    log.info(f"Singleton port: {SINGLETON_PORT}")
    log.info("=" * 60)

    # Refuse to start if another instance already holds the singleton lock.
    # This prevents the 409 Conflict crash storm caused by overlapping pollers.
    if not acquire_singleton_lock():
        log.info("Another listener instance is alive. Exiting cleanly (no error).")
        sys.exit(0)

    log.info("Singleton lock acquired.")

    # Outer restart loop — survives Conflict and transient errors.
    # Backoff bounded so the watchdog still has a heartbeat to check.
    backoff = 5
    max_backoff = 120
    while True:
        try:
            app = _build_app()
            log.info("Polling started (poll_interval=2s, timeout=30s)")
            app.run_polling(
                poll_interval=2.0,
                timeout=30,
                drop_pending_updates=True,
            )
            # If run_polling returns cleanly (shouldn't happen unless told to stop),
            # break out so the process can exit and the watchdog respawn it.
            log.info("run_polling returned cleanly. Exiting main loop.")
            break
        except Conflict:
            log.warning(
                f"Conflict caught at top level. Backing off {backoff}s before retry. "
                "If the duplicate poller is another listener instance on this machine, "
                "it should also see this and one of them will eventually win."
            )
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)
        except KeyboardInterrupt:
            log.info("KeyboardInterrupt — shutting down.")
            break
        except Exception as exc:
            log.error(f"Top-level exception: {exc}. Backing off {backoff}s.", exc_info=exc)
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)
        else:
            backoff = 5  # reset on a clean cycle

if __name__ == "__main__":
    main()
