# SOP — Environment Secrets & `.env` Discipline

**Owner:** Mack
**Applies to:** All agents touching scripts that need API keys, bot tokens, or DB credentials
**Created:** 2026-05-18
**Trigger event:** TELEGRAM-TOKEN-ROTATE-2026-05-17 (leaked bot token cleanup)

---

## The rule

Secrets live in `D:\Claude Playground\.env` only. Scripts read them from `os.environ`. No hardcoded fallback strings, ever.

If `.env` is missing or a required key is unset, the script must hard-fail with a clear message — never start with a wrong/empty token, never assume defaults.

## What `.env` contains today

```
TELEGRAM_BOT_TOKEN=<bot token from @BotFather>
TELEGRAM_CHAT_ID=6283854178      # Inon's Telegram user ID
```

File is in `.gitignore` — never `git add -f` it.

## Required pattern for any Python script needing a secret

```python
import os, sys
from pathlib import Path

def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=False)
        return
    except ImportError:
        pass
    # Manual fallback parser
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

_load_dotenv()

TOKEN = os.environ.get("MY_TOKEN")
if not TOKEN:
    raise SystemExit("FATAL: MY_TOKEN not set. Populate D:\\Claude Playground\\.env.")
```

`python-dotenv` is installed on the host (1.2.2) — preferred. Manual parser is the fallback if a fresh machine doesn't have it.

## Setup on a fresh machine

1. Copy `.env` from the password manager (never from the repo — it's gitignored).
2. Place it at `D:\Claude Playground\.env`.
3. Optional: `pip install python-dotenv` (already a dep of telegram_listener; the manual parser works without it).

## When a secret leaks

1. **Rotate the credential at the source** (BotFather, GitHub, cloud console). Old key dies — leaked commits become harmless.
2. **Scrub the working tree** — grep the old key, replace every occurrence with the env-only pattern above.
3. **Restart any long-running process** holding the old key in memory (listener, watchdog, etc.).
4. **Verify** with an end-to-end probe (e.g. send a real message, hit a real endpoint).
5. **Do NOT rewrite git history** on a public repo. The old key is already dead; rewrites break clones and history forensics.

## Known follow-ups

- **[RESOLVED 2026-05-18]** `python-telegram-bot` / httpx INFO log was writing full `https://api.telegram.org/bot<TOKEN>/...` URLs to `scratchpad/telegram_listener.log` on every poll. Closed by `TELEGRAM-LOGGER-LEAK_fix` (Mack): (1) `logging.getLogger("httpx").setLevel(logging.WARNING)` silences the per-request URL log; (2) `RotatingFileHandler(maxBytes=512_000, backupCount=3)` caps log growth and blast radius; (3) regex redaction filter `bot\d+:[A-Za-z0-9_-]{30,}` → `bot<REDACTED>` strips any token that slips through a future dependency. Verified post-fix grep = 0 occurrences in fresh log.

## Lessons

- **Silence third-party DEBUG/INFO loggers that include URLs when secrets travel in query strings or headers.** Library defaults assume URLs are non-sensitive; for any client that puts credentials in the path (Telegram Bot API, some webhook signers) or in query strings (signed URLs, API keys), explicitly raise the HTTP client logger (`httpx`, `urllib3`, `requests.packages.urllib3`) to WARNING before first request. Pair with a regex redaction filter on the root logger for defense in depth — pattern-based, never the literal secret, so the filter survives rotations.
