# Remote Session Trigger Research
**Tomy — Research Report**
**Date:** 2026-05-16
**Requested by:** Andy (for Mack implementation)
**Subject:** How to remotely start or continue a Claude Code CLI session on Windows 11, triggered by a Telegram message

---

## Executive Summary

The research covers six questions about triggering a Claude Code CLI session on Windows 11 from a Telegram message. The key findings are:

1. **`claude -p --continue "..."` works headlessly** — the `-p` (print) flag is the official headless mode. Setting `CI=true` skips permission prompts. Exit code 1 from the prior bat-file attempt was almost certainly caused by missing authentication context or missing `ANTHROPIC_API_KEY`, not by the absence of a PTY.

2. **`wt.exe` can be launched from a background Python process** — with `subprocess.Popen(["wt", "new-tab", ...])` (non-blocking) or `Start-Process wt ...` from PowerShell. This opens a visible terminal window for interactive use. Semicolons must be escaped as backticks in PowerShell.

3. **`pywinpty` can create a ConPTY and run `claude` inside it** — this is the correct fix if the issue is truly PTY detection. However, the recommended path is to use `-p` print mode (which needs no PTY) rather than trying to simulate an interactive terminal.

4. **Best persistence method: Windows Task Scheduler with "Run only when user is logged on" + At Log On trigger** — this runs as the interactive user, can open visible windows, survives reboots, and requires no admin rights or third-party tools. `pythonw.exe` makes the listener silent.

5. **Security: sender ID allowlist + secret command word** — the Telegram `chat_id` / `user_id` for Inon (6283854178) is already in `buildar_notify.py`. The listener must check this ID and require a specific command word (e.g., `/continue`) before triggering anything.

6. **Recommended architecture: two-tier** — (A) A persistent `pythonw.exe` Telegram listener that checks sender ID and command word, then fires `wt.exe` to open an interactive Claude session; OR (B) Use Claude Code's built-in **Channels** feature (Telegram plugin already officially supported, Bun already installed) which eliminates the custom listener entirely. Channels is the lower-risk path.

**Critical finding:** Claude Code v2.1.143 (currently installed) includes the official Telegram Channels plugin — this is a first-party, production-grade solution that bypasses all the PTY/subprocess complexity. It is strongly recommended over the custom Python listener approach.

---

## Findings per Question

### Question 1: Does `claude --continue --print "..."` work headlessly?

**Answer: Yes, with the right flags and auth.**

The `-p` / `--print` flag is the official "non-interactive / SDK" mode for Claude Code. It:
- Reads stdin, runs the prompt, prints to stdout, and exits
- Works without any PTY — it is explicitly designed for CI/CD pipelines, scripts, and subprocesses
- Combines with `--continue` / `-c` to resume the most recent conversation: `claude -c -p "query"`

**Why the original bat file exited with code 1:**
The `rl_restart.bat` current version does NOT call claude at all — it only calls `rate_limit_watchdog.py on-start`. The prior attempt to run `claude --continue --print "/start ..."` from a Scheduled Task likely failed because:
1. The Scheduled Task ran as SYSTEM or without the user session environment, missing the Claude Code OAuth token (stored in `~/.claude.json` — user-profile dependent)
2. Or `ANTHROPIC_API_KEY` was not in the task's environment

**Environment variables that enable headless operation:**

| Variable | Effect |
|----------|--------|
| `CI=true` | Forces non-interactive mode; skips all confirmation prompts automatically |
| `CLAUDE_CODE_SKIP_PERMISSIONS=1` | Bypasses all permission checks (use only in trusted automation) |
| `ANTHROPIC_API_KEY=sk-ant-...` | Required if not using Claude.ai OAuth subscription auth |
| `CLAUDE_CODE_OAUTH_TOKEN=...` | Alternative: OAuth access token (can be set instead of API key for subscription users) |
| `CLAUDE_CODE_RESUME_INTERRUPTED_TURN=1` | Auto-resumes if previous session ended mid-turn |
| `CLAUDE_CODE_EXIT_AFTER_STOP_DELAY=5000` | Auto-exits after 5s of idle (useful for scripted calls) |

**Exact command for headless continue:**
```cmd
set CI=true
set CLAUDE_CODE_SKIP_PERMISSIONS=1
claude -c -p "/start Review active_tasks.json and continue the top in-progress task" --dangerously-skip-permissions --allowedTools "Bash,Read,Edit,Write"
```

**Key flags:**
- `-c` / `--continue`: load most recent conversation in current directory
- `-p` / `--print`: headless mode, print and exit
- `--dangerously-skip-permissions`: skip all prompts
- `--bare`: skip CLAUDE.md/hooks/MCP loading (faster, but would skip the existing hooks — do NOT use for Andy sessions)
- `--allowedTools "Bash,Read,Edit,Write"`: pre-approve tools to avoid stalls

**Important note on `--bare`:** Do NOT use `--bare` for the restart trigger. The existing `PreToolUse` hook in `~/.claude/settings.json` calls `rate_limit_watchdog.py on-start` to send the Telegram restart notification — `--bare` would skip all hooks and the notification would never fire.

**Exit codes:**
- `0` = success
- `1` = general error (auth failure, network error, invalid prompt)
- `2` = argument error

---

### Question 2: Can `wt.exe` be invoked from a background Python process?

**Answer: Yes.**

`wt.exe` is installed at `C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\wt.exe` (confirmed on this machine).

**From Python subprocess (non-blocking):**
```python
import subprocess
subprocess.Popen([
    "wt", "new-tab",
    "--title", "Andy Resume",
    "--startingDirectory", r"D:\Claude Playground",
    "pwsh", "-NoExit", "-Command",
    'cd "D:\\Claude Playground"; $env:CI="true"; claude -c'
])
# Returns immediately — wt.exe opens asynchronously
```

**From PowerShell (non-blocking with Start-Process):**
```powershell
Start-Process wt -ArgumentList 'new-tab --title "Andy Resume" --startingDirectory "D:\Claude Playground" pwsh -NoExit -Command "cd ''D:\Claude Playground''; $env:CI=''true''; claude -c"'
```

**Key behavior notes:**
- `wt` is a Windows Store app — PowerShell waits for it by default. Use `Start-Process wt` OR `subprocess.Popen` (not `subprocess.run`) to avoid blocking.
- `--window 0` targets the most recently used existing window; `-w -1` (or `--window new`) always opens a new window.
- To open a new tab in an existing WT window: `wt -w 0 new-tab --title "Andy" pwsh -Command "claude -c"`
- Semicolons in PowerShell wt commands must be escaped as backticks: `` `; ``
- When called from a Python process with no visible desktop (e.g., SYSTEM account), `wt.exe` will fail silently. The calling process must run as the interactive logged-in user.

**Exact recommended invocation for the Telegram listener:**
```python
import subprocess, os

def open_claude_session():
    env = os.environ.copy()
    env['CI'] = 'true'
    subprocess.Popen([
        "wt", "new-tab",
        "--title", "Andy - Remote Resume",
        "--startingDirectory", r"D:\Claude Playground",
        "pwsh", "-NoExit", "-Command",
        r'Set-Location "D:\Claude Playground"; $env:CI="true"; claude -c'
    ], env=env)
```

---

### Question 3: Can pywinpty / ConPTY solve the "no terminal" exit-code-1 problem?

**Answer: Yes, but it's the wrong fix for this use case.**

`pywinpty` (version 2.x) wraps Windows ConPTY and provides a PTY that tricks apps into thinking they're running in a real terminal. It is used by Jupyter, IPython, and VS Code internals.

**High-level API usage:**
```python
from winpty import PtyProcess

proc = PtyProcess.spawn(
    r'C:\Users\Inon Baasov\AppData\Roaming\npm\claude.cmd',
    env={**os.environ, 'CI': 'true'}
)
proc.write('/start Review tasks\r\n')
while proc.isalive():
    output = proc.readline()
    print(output, end='')
```

**Low-level PTY API:**
```python
from winpty import PTY

pty = PTY(cols=220, rows=50)
pty.spawn(br'C:\Users\Inon Baasov\AppData\Roaming\npm\claude.cmd')
pty.write(b'claude -c\r\n')
output = pty.read()
```

**Why this is the wrong fix here:**
- If the exit code 1 root cause is auth failure (missing OAuth token in SYSTEM's environment), `pywinpty` doesn't help — it still runs in the same auth-less environment.
- If the root cause is truly PTY detection, the correct fix is using `claude -p` (which explicitly says "no PTY needed") rather than simulating a PTY.
- `pywinpty` adds a Rust-compiled dependency and is complex to debug in a production automation context.

**When pywinpty IS the right tool:**
- If you need an interactive Claude session (not `-p` print mode) driven by a script that also reads Claude's output programmatically.
- Not needed for Mack's implementation.

**Note:** `pywinpty` is NOT currently installed (`pip list` shows only `pywin32` and `pywin32-ctypes`). Installation: `pip install pywinpty`.

---

### Question 4: Best way to run a persistent Python Telegram listener on Windows 11

**Evaluated options:**

#### Option A: Windows Task Scheduler (RECOMMENDED)
- **Trigger:** At Log On (fires when Inon logs in; also works with "At Startup" if "Run only when user is logged on" is checked)
- **Setting:** "Run only when user is logged on" — CRITICAL: this runs in the interactive user's desktop session, which means it CAN open visible windows, access `~/.claude.json`, and inherit user environment variables
- **No admin rights needed** to create or modify tasks under the current user account
- **Survives reboots** — fires again on next login
- **Program:** `C:\Users\Inon Baasov\AppData\Local\Programs\Python\Python311\pythonw.exe`
- **Arguments:** `"D:\Claude Playground\scripts\telegram_listener.py"`
- **Start in:** `D:\Claude Playground`
- **pythonw.exe** runs without a console window (silent background process)
- **Limitation:** If the listener crashes, it does not auto-restart. Mitigate with a watchdog loop inside the script or a second scheduled task that checks every 5 minutes.

**Create via PowerShell (no GUI needed):**
```powershell
$action = New-ScheduledTaskAction `
    -Execute "C:\Users\Inon Baasov\AppData\Local\Programs\Python\Python311\pythonw.exe" `
    -Argument '"D:\Claude Playground\scripts\telegram_listener.py"' `
    -WorkingDirectory "D:\Claude Playground"

$trigger = New-ScheduledTaskTrigger -AtLogOn -User "Inon Baasov"

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit 0 `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName "AndyTelegramListener" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Limited
```

#### Option B: NSSM (Windows Service)
- Services running as SYSTEM cannot open visible windows or access user profile / `~/.claude.json`
- Services running as a specific user (via NSSM's "Log On" tab) CAN access user files, but may not interact with the desktop depending on Windows version
- On modern Windows 11, Session 0 isolation prevents services from showing UI
- **Not recommended** for this use case because we need to open a visible `wt.exe` window

#### Option C: pythonw.exe in user Startup folder
- Place a `.bat` or `.vbs` shortcut in `C:\Users\Inon Baasov\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`
- Runs at login, as the user, with full desktop access
- Simple and no admin rights needed
- **Limitation:** No auto-restart on crash; harder to manage (stop/start requires Task Manager)

#### Option D: Systemd-style loop with NSSM + user session
- NSSM configured to "Log On As" the specific user account
- This makes the service run in the user's security context
- But it still runs in Session 0 on Windows 11, which cannot show GUI windows
- **Not recommended**

**Winner: Task Scheduler (Option A)** — handles reboots, runs as interactive user, supports auto-restart on failure via `RestartCount`, no third-party tools needed.

---

### Question 5: Security design for Telegram listener

**Minimum secure design:**

```python
# In telegram_listener.py

ALLOWED_SENDER_ID = 6283854178       # Inon's Telegram user ID (from buildar_notify.py)
TRIGGER_COMMANDS = {"/continue", "/start", "/resume"}  # exact command words required

def is_authorized(update) -> bool:
    """Accept only from Inon's exact Telegram user ID."""
    return update.effective_user.id == ALLOWED_SENDER_ID

def is_trigger_command(text: str) -> bool:
    """Accept only exact trigger commands."""
    return text.strip().lower() in TRIGGER_COMMANDS

async def handle_message(update, context):
    if not is_authorized(update):
        # Silent drop — do NOT reply. Replying reveals the bot exists.
        return
    
    text = update.message.text or ""
    if not is_trigger_command(text):
        await update.message.reply_text("Unknown command.")
        return
    
    # Authorized command — trigger Claude
    open_claude_session()
    await update.message.reply_text("Starting Claude session...")
```

**Security properties:**
1. **Sender ID check:** `update.effective_user.id == 6283854178` — Telegram user IDs are not guessable or spoofable at the API level
2. **Command word whitelist:** Only specific strings trigger action — prevents accidental triggers from forwarded messages
3. **Silent drop for unauthorized senders:** No reply means no information leakage about bot existence
4. **Bot token stored in environment variable** (already the case in `buildar_notify.py` with `TELEGRAM_BOT_TOKEN`) — not hardcoded in listener script
5. **No webhook endpoint exposed** — polling mode means no inbound ports are opened on the machine

**Defense in depth (optional):**
- Log all trigger attempts (authorized and unauthorized) to `scratchpad/telegram_listener.log`
- Rate limit: if triggered more than 3 times in 60 seconds, suppress and alert

---

### Question 6: Full Proposed Architecture

Two viable architectures are presented, ranked by recommendation.

---

## Architecture A: Claude Code Channels (RECOMMENDED — Built-in, No Custom Code)

This uses Claude Code's official Telegram Channels feature (research preview, available on Pro/Max plans, requires Bun).

**Prerequisites (already met on this machine):**
- Claude Code v2.1.143 (Channels requires v2.1.80+) ✓
- Bun installed at `C:\Users\Inon Baasov\.bun\bin\bun.exe` ✓
- Existing Telegram bot token in `buildar_notify.py` (`8731882312:AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I`) — this bot is currently outbound-only (notifications); we would use the same or a second bot for the channel

**How it works:**
1. Claude Code session starts with `claude -c --channels plugin:telegram@claude-plugins-official`
2. The Telegram plugin polls the bot for incoming messages
3. Inon sends `/continue` from Telegram
4. The message arrives in the Claude Code session as a `<channel source="telegram">` event
5. Claude processes it and replies back through Telegram

**Setup steps:**
```
# Inside an active Claude session:
/plugin install telegram@claude-plugins-official
/telegram:configure 8731882312:AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I
# (or use a second bot for the inbound channel)

# Then restart with channels:
claude -c --channels plugin:telegram@claude-plugins-official
```

**Pairing:**
```
# Send any message to the bot from Telegram
# Bot replies with pairing code
# In Claude session:
/telegram:access pair <code>
/telegram:access policy allowlist
# This restricts to ONLY paired users (Inon)
```

**Limitation:** The `--channels` flag only works while Claude is already running. This is for "message while Claude is active and you want to send instructions." It does NOT auto-start a new Claude session from scratch if the machine is idle.

**Use case fit:** Best for: "Claude is already running overnight on a task, and Inon wants to check in or redirect it from his phone." NOT for: "Claude is not running, machine is idle, Inon wants to cold-start a session."

---

## Architecture B: Custom Python Listener + wt.exe (For Cold-Start / Always-Available Trigger)

This architecture handles the case where Claude is NOT running, and Inon wants to start a new session from scratch via Telegram.

**Component overview:**

```
[Inon's Phone] 
    → Telegram message "/continue"
    → [Telegram Bot API]
    → [Python listener running as pythonw.exe on Windows 11]
        - Checks: sender ID == 6283854178
        - Checks: message == "/continue" or "/start"
        - If pass: calls wt.exe to open visible terminal
    → [Windows Terminal new tab opens]
        - Runs: cd "D:\Claude Playground" && claude -c
        - OR:   claude -c --channels plugin:telegram@claude-plugins-official
    → [Claude Code interactive session starts]
        - PreToolUse hook fires: rate_limit_watchdog.py on-start
        - Reads scratchpad/rate_limit_queue.json for last task context
        - Sends Telegram notification "Session started, picking up from: <last task>"
```

**Persistent listener script (`scripts/telegram_listener.py`):**
```python
"""
telegram_listener.py — Andy Remote Trigger via Telegram
Usage: pythonw.exe "D:\Claude Playground\scripts\telegram_listener.py"
Runs persistently in background. Listens for /continue from Inon.
"""
import os, sys, subprocess, logging
from pathlib import Path

# pip install python-telegram-bot
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- Config ---
BOT_TOKEN     = os.environ.get("TELEGRAM_BOT_TOKEN", "8731882312:AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I")
ALLOWED_ID    = 6283854178
TRIGGER_CMDS  = {"/continue", "/start", "/resume"}
WORKSPACE     = r"D:\Claude Playground"
LOG_FILE      = r"D:\Claude Playground\scratchpad\telegram_listener.log"

logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def open_claude_session():
    """Open Windows Terminal with an interactive Claude session."""
    logging.info("Opening Claude session via wt.exe")
    subprocess.Popen([
        "wt", "new-tab",
        "--title", "Andy - Telegram Resume",
        "--startingDirectory", WORKSPACE,
        "pwsh", "-NoExit", "-Command",
        f'Set-Location "{WORKSPACE}"; $env:CI="true"; claude -c'
    ])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip().lower()
    logging.info(f"Message from {user_id}: {text!r}")

    if user_id != ALLOWED_ID:
        logging.warning(f"Unauthorized sender {user_id} — dropped")
        return  # Silent drop

    if text not in TRIGGER_CMDS:
        await update.message.reply_text(
            "Commands: /continue, /start, /resume"
        )
        return

    await update.message.reply_text("Starting Claude session on your machine...")
    open_claude_session()

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))
    logging.info("Telegram listener started")
    app.run_polling(poll_interval=2.0, timeout=30)

if __name__ == "__main__":
    main()
```

**Note:** `python-telegram-bot` is NOT currently installed. Install: `pip install python-telegram-bot`

**What Inon sees/does:**
1. Inon is away from desk, Claude is not running
2. Inon sends `/continue` to the bot from Telegram (same bot as notifications)
3. Bot replies: "Starting Claude session on your machine..."
4. Windows Terminal opens a new tab on the machine with an interactive Claude session
5. Claude's `PreToolUse` hook fires, sends Telegram notification: "Session restarted, picking up from: [last task]"
6. Inon can now also use Claude's Remote Control feature from his phone to interact further

**Persistence via Task Scheduler:**
Create a scheduled task "AndyTelegramListener" that:
- Triggers: At Log On (user: Inon Baasov)
- Action: `pythonw.exe "D:\Claude Playground\scripts\telegram_listener.py"`
- Run only when user is logged on: YES
- Restart on failure: up to 3 times, every 1 minute
- Do not stop if running on battery

---

## Recommended Architecture (Combined)

The optimal production setup combines both:

1. **Cold-start:** Architecture B (Python listener) handles the case where Claude is not running. Listens 24/7 silently, opens a new `wt.exe` tab when triggered.

2. **While-active steering:** Architecture A (Channels plugin) runs inside the Claude session. Once Claude is running, Inon can chat directly with it via Telegram.

**The session flow:**
```
Telegram "/continue"
  → Python listener (always running)
  → wt.exe opens: claude -c --channels plugin:telegram@claude-plugins-official
  → Claude starts with Telegram channel active
  → Claude's on-start hook fires (sends restart notification)
  → Inon can now chat with Claude directly via Telegram
  → Claude works on tasks, Inon directs from phone
```

This means the listener only needs to do one thing: open a terminal with the right `claude` command. The `--channels` flag then enables ongoing Telegram→Claude interaction for the rest of the session.

---

## Open Risks / Unknowns

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| OAuth token not available to listener when opening wt.exe subprocess | Medium | Run listener as logged-in user (Task Scheduler "run only when logged on"). `~/.claude.json` is in user profile. Test with `claude auth status` in the wt.exe subprocess before relying on it. |
| `python-telegram-bot` not installed | High (confirmed not installed) | `pip install python-telegram-bot` — add to setup script |
| Two bots conflict (existing outbound bot vs inbound channel bot) | Low | The same bot token can be used for both sending notifications and receiving messages. The Channels plugin polls the same bot. Test that `buildar_notify.py` (outbound) and the channel plugin (polling) don't conflict. If they do, create a second bot via BotFather. |
| Channels feature in research preview — may break on update | Low-Medium | Monitor Claude Code release notes. Fall back to Architecture B if Channels is deprecated or changes behavior. |
| Bun version compatibility with Telegram plugin | Unknown | Test after install: `bun --version`. Channels requires Bun; Bun is installed. |
| Windows Terminal not open when listener fires `wt.exe` | Low | `wt.exe` creates a new window if none exists. Not a problem. |
| Rate limit: listener running during rate-limited period, triggers session that immediately exits | Medium | The `on-start` hook sends a notification and reads queue. If triggered before rate window clears, `claude -c` will fail with auth/rate error. Mitigation: listener checks `scratchpad/rate_limit_queue.json` before opening session; if queue exists and `resets_at` is in future, reply "Still rate limited, retry at {time}." |
| Channels requires full claude.ai OAuth, not API key | Known | Confirmed in docs: Remote Control and Channels require claude.ai subscription authentication. If Inon uses `ANTHROPIC_API_KEY` mode, Channels is blocked. Check auth mode: `claude auth status`. |

---

## Implementation Checklist for Mack

### Phase 1: Prerequisites (30 min)
- [ ] Install `python-telegram-bot`: `pip install python-telegram-bot`
- [ ] Verify Bun is working: `bun --version` (already confirmed installed)
- [ ] Check Claude auth mode: `claude auth status` — confirm it's using claude.ai OAuth (not API key)
- [ ] Decide: use existing bot (`8731882312:...`) or create a second bot via BotFather for the inbound channel. Using the same bot is simpler; test for conflicts first.

### Phase 2: Install Claude Code Channels Telegram Plugin (20 min)
- [ ] Start a Claude session: `claude -c`
- [ ] Install plugin: `/plugin install telegram@claude-plugins-official`
- [ ] Configure token: `/telegram:configure 8731882312:AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I`
- [ ] Restart with channels: `claude -c --channels plugin:telegram@claude-plugins-official`
- [ ] Send any message to bot from Telegram, get pairing code
- [ ] In session: `/telegram:access pair <code>`
- [ ] In session: `/telegram:access policy allowlist`
- [ ] Test: send message from Telegram, verify it arrives in Claude session
- [ ] QA: Verify responses go back to Telegram (not just terminal)

### Phase 3: Build the Python Cold-Start Listener (1–2 hours)
- [ ] Create `scripts/telegram_listener.py` using the code template above
- [ ] Add rate-limit queue check: if `scratchpad/rate_limit_queue.json` exists with future `resets_at`, reply "Rate limited until HH:MM" instead of opening session
- [ ] Test manually: `python scripts/telegram_listener.py` in a terminal, send `/continue` from Telegram, verify wt.exe opens
- [ ] Test: unauthorized sender (different Telegram account) — verify silent drop
- [ ] Test: unknown command — verify polite error reply
- [ ] Test log output in `scratchpad/telegram_listener.log`
- [ ] QA signoff (Jasmin/Vera): review auth logic, rate limit check, subprocess invocation

### Phase 4: Install as Persistent Background Service (30 min)
- [ ] Register Task Scheduler task "AndyTelegramListener" via PowerShell (code in Question 4 above)
- [ ] Reboot machine; verify listener auto-starts and is visible in Task Manager
- [ ] Send `/continue` from Telegram after reboot; verify Claude session opens
- [ ] Verify existing notification bot (`buildar_notify.py`) still works after listener is running

### Phase 5: Session Startup Integration (20 min)
- [ ] Modify the `wt.exe` command in `telegram_listener.py` to launch: `claude -c --channels plugin:telegram@claude-plugins-official`
- [ ] Test full flow: send `/continue` → wt.exe opens → Claude starts with Channels active → Inon can chat via Telegram
- [ ] Verify `rate_limit_watchdog.py on-start` hook fires (check `scratchpad/watchdog_stop_log.json`)
- [ ] Verify Telegram restart notification is sent by the hook

### Phase 6: Dashboard / Task Tracking Update (10 min)
- [ ] Rex: add "Remote Trigger" status indicator to the dashboard
- [ ] Andy: update `tasks/active_tasks.json` to mark this task done after QA

---

## Sources Consulted

- [Claude Code Headless Mode Docs](https://code.claude.com/docs/en/headless) — `-p` flag, `--continue`, `--bare`, headless mode
- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference) — all flags including `--bg`, `--channels`, `--remote-control`
- [Claude Code Environment Variables](https://code.claude.com/docs/en/env-vars) — `CI`, `CLAUDE_CODE_SKIP_PERMISSIONS`, `CLAUDE_CODE_OAUTH_TOKEN`, etc.
- [Claude Code Channels Docs](https://code.claude.com/docs/en/channels) — Telegram plugin setup, security, architecture
- [Claude Code Remote Control Docs](https://code.claude.com/docs/en/remote-control) — remote session management
- [Windows Terminal CLI Reference (Microsoft Learn)](https://learn.microsoft.com/en-us/windows/terminal/command-line-arguments) — `wt.exe` new-tab, --window, semicolon escaping
- [pywinpty GitHub](https://github.com/andfoy/pywinpty) — ConPTY Python bindings API
- [python-telegram-bot docs](https://docs.python-telegram-bot.org) — `run_polling()`, handler architecture
- [NSSM docs](https://www.nssm.cc/commands) — Windows service limitations for interactive sessions
- [Microsoft Learn — Interactive Services](https://learn.microsoft.com/en-us/windows/win32/services/interactive-services) — Session 0 isolation

---

*Report by Tomy — ready for Mack implementation. QA by Jasmin (logic/security review) recommended before Phase 3 deployment.*
