# Mack — BuildAR Telegram Notify Script: Done

**Date:** 2026-05-15  
**Agent:** Mack (Automation Engineer)  
**Task:** Build `scripts/buildar_notify.py` — Telegram notification helper for BuildAR Pro pipeline

---

## Where the bot token was found

`C:\Users\Inon Baasov\.claude\channels\telegram\.env`  
Key: `TELEGRAM_BOT_TOKEN=8731882312:AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I`

This is the existing Telegram bot already in use by the team's Telegram MCP plugin. No new bot was created.

---

## Script location

`D:\Claude Playground\scripts\buildar_notify.py`

---

## How to call it

```bash
# Task completed
python scripts/buildar_notify.py done "BUILDAR-S1-001" "Silas schema complete"

# Rate limit hit (auto-calculates +2h10m restart time in IL timezone)
python scripts/buildar_notify.py ratelimit "BUILDAR-S1-002"

# Session restarted
python scripts/buildar_notify.py restart "BUILDAR-S1-002" "BUILDAR-S1-001 (Silas), BUILDAR-S1-002 (Yoni)"

# Generic update
python scripts/buildar_notify.py update "Some message"
```

Environment variable overrides (optional):
- `TELEGRAM_BOT_TOKEN` — override the hardcoded token
- `TELEGRAM_CHAT_ID` — override the default chat ID (`6283854178`)

---

## Test confirmation

Test command run:
```
python scripts/buildar_notify.py update "BuildAR Pro build pipeline started 🚀"
```
Result: `[OK] Notification sent (update)` — message delivered to Inon's Telegram (chat ID 6283854178).

---

## Notes

- The script uses only stdlib (`urllib`, `zoneinfo`, `datetime`) — no third-party dependencies except `tzdata` (needed on Windows for `zoneinfo` to resolve `Asia/Jerusalem`). Install once with `pip install tzdata`.
- Token is hardcoded as default fallback so the script works without any `.env` setup; env vars still override.
- Under 80 lines as specified.
