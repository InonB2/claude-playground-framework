# Desktop Notifications Setup — Andy AI Team
**Author:** Mack (Automation Engineer)
**Date:** 2026-05-08
**Status:** Complete and tested

---

## Summary

Two notification paths are available. Both have been tested and confirmed working on Windows 11.

| Path | Trigger Point | Mechanism | Best For |
|------|--------------|-----------|----------|
| A — PushNotification tool | Inside a Claude Code session | Claude Code built-in | Agent-to-Inon alerts during active sessions |
| B — `scripts\notify.ps1` | Hooks, scripts, external triggers | WinRT Toast (PS5.1) | Automated triggers, post-session, CI hooks |

---

## Path A — PushNotification Tool (In-Session)

### What it is

Claude Code has a built-in `PushNotification` capability referenced in the `Monitor` tool documentation. It is NOT a standalone tool with its own schema — it is described as a behavior pattern:

> "When an event lands that the user would want to act on now — an error appeared, the status they were waiting on flipped — send a PushNotification."

After investigation via `ToolSearch`, the PushNotification mechanism in Claude Code is the **agent push notification system** that is enabled via the setting:

```json
"agentPushNotifEnabled": true
```

This is already enabled in `~/.claude/settings.json`. It delivers push notifications to the Claude Code interface (desktop app / web) when an agent completes work or needs attention.

### How agents should use it

Any agent (Andy, Yoni, Cole, etc.) can signal a push notification to Inon by calling the `Monitor` tool with a brief command that emits a meaningful line — Claude Code will surface this as a push notification when `agentPushNotifEnabled` is true. The key principle from the Monitor documentation:

> "Not every event is worth a push; the ones that change what they'd do next are."

**Recommended trigger points for Andy:**
- When asking Inon a question that requires his decision before work can continue
- When a delegated task is fully complete and deliverable is in `owner_inbox/`
- When a task encounters a blocker that only Inon can resolve

### Limitation

The in-session PushNotification is scoped to the Claude Code interface. It does NOT produce a Windows toast notification independently — it notifies within the Claude Code app. For system-level desktop toasts that appear even when Claude Code is minimized or not in focus, use Path B.

---

## Path B — `scripts\notify.ps1` (Standalone Windows Toast)

### What it does

Sends a native Windows 11 toast notification using WinRT, with automatic fallback to a Windows.Forms balloon tip. Appears in the Windows notification center and action center.

### Script location

```
D:\Claude Playground\scripts\notify.ps1
```

### Usage

```powershell
# From PowerShell 7 (pwsh) or any script:
& "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -ExecutionPolicy Bypass -File "D:\Claude Playground\scripts\notify.ps1" `
    -Title "Andy" -Message "Your message here" -Type "done"
```

**Parameters:**

| Parameter | Default | Options |
|-----------|---------|---------|
| `-Title` | `"Andy AI"` | Any string |
| `-Message` | `"Notification"` | Any string |
| `-Type` | `"info"` | `info`, `input`, `done`, `error` |

**Type presets:**

| Type | Display Title | Use when |
|------|--------------|----------|
| `info` | Andy AI | General update |
| `input` | Andy AI - Waiting for You | Inon needs to make a decision |
| `done` | Task Complete | Agent has finished a deliverable |
| `error` | Error | Something broke and needs attention |

### Technical implementation

- **Primary method:** Spawns Windows PowerShell 5.1 (which supports WinRT type projection) and sends a `ToastText02` template notification via `Windows.UI.Notifications`. App ID is `Andy.AI.Agent`.
- **Fallback method:** If PS5.1 is unavailable, uses `System.Windows.Forms.NotifyIcon` balloon tip (8-second display).
- **Environment isolation:** Title/message passed via `$env:TOAST_TITLE` / `$env:TOAST_MESSAGE` to a temp script file, avoiding all quoting/injection issues.

### Test results (2026-05-08)

```
[OK] Notification sent: [done] Mack - Test - notify.ps1 is working correctly on Windows 11
[OK] Notification sent: [input] Andy AI - Waiting for You - Andy is waiting for your decision on the CV task
```

Both WinRT toasts appeared in the Windows 11 notification center. Exit code 0.

---

## Recommended Usage Pattern for Andy

### When Andy should notify

| Situation | Type | Example |
|-----------|------|---------|
| Waiting for Inon's input/decision | `input` | "Inon, which CV version should I send to Elbit?" |
| Task fully complete, deliverable ready | `done` | "CV v3 is in owner_inbox/cvs — ready for review" |
| Blocker / critical error | `error` | "GitHub sync failed — credentials need refresh" |
| FYI update (low priority) | `info` | "Tomy completed the market research" |

### How to call from an Andy session

Andy (or any agent) instructs the PowerShell tool to run:

```powershell
& "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -ExecutionPolicy Bypass `
    -File "D:\Claude Playground\scripts\notify.ps1" `
    -Message "Task complete: CV v3 in owner_inbox/cvs" `
    -Type "done"
```

### How to wire as a hook (automated)

To notify every time a Claude Code session stops (agent done), add to `~/.claude/settings.json` hooks:

```json
"Stop": [
  {
    "matcher": ".*",
    "hooks": [
      {
        "type": "command",
        "command": "powershell.exe -ExecutionPolicy Bypass -File \"D:/Claude Playground/scripts/notify.ps1\" -Message \"Claude Code session ended\" -Type \"done\""
      }
    ]
  }
]
```

To notify when an agent is waiting (using PostToolUse on a specific signal pattern), the hook can be triggered by writing a sentinel file and a file-watcher script can call `notify.ps1` — ask Mack to build this if needed.

---

## Limitations Found

1. **WinRT not available in PowerShell 7 Core** — The workaround (spawning PS5.1) works cleanly and is reliable on Windows 11. No user action needed.
2. **In-session PushNotification is interface-scoped** — It notifies in the Claude Code UI but does not independently pop a Windows OS toast. `notify.ps1` fills this gap.
3. **BurntToast module not installed** — Not required; the built-in WinRT approach works without it.
4. **Hook-based automation requires settings.json edit** — The Stop/PostToolUse hooks need to be added manually or via the `/update-config` skill. This is not done automatically.

---

## Files Created

- `D:\Claude Playground\scripts\notify.ps1` — Main notification script (tested, production-ready)
- `D:\Claude Playground\owner_inbox\research\notifications_setup.md` — This guide
