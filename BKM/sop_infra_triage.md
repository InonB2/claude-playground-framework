# SOP: Infrastructure Triage

**Owner:** Finn
**Last reviewed:** 2026-05-15
**Applies to:** All infrastructure triage on this team

---

This SOP is the operational playbook for Finn (Infrastructure Triage Engineer). It defines what Finn handles directly, what gets escalated, and the exact diagnostic steps for the failure modes this team sees most often. Deployment topology, CI/CD design, and net-new pipeline construction are out of scope for this file — see Dev's `sop_infra.md` for those.

---

## 1. Triage Scope

### 1.1 Finn handles directly

- **MCP health** — `claude mcp list`, restart/re-register, transport inspection in `~\.claude.json`
- **Bot recovery** — Telegram bot PID, allowlist sanity, token presence, zombie process cleanup
- **Plugin diagnostics** — dropped skills, empty caches, plugin-scoped vs session-scoped failures
- **Env var audits** — missing keys, CRLF corruption, scope mismatches in `.env` / `settings.json` / `.mcp.json`
- **Service restarts** — Telegram bot, WhatsApp bridge, MCP servers, scheduled tasks
- **Log analysis** — reading logs to identify root cause before touching state
- **Port conflicts** — collisions on 8080 (WhatsApp), MCP local ports, anything bound by a stale PID
- **Stale PIDs** — orphaned bot processes, half-dead Node workers, locked file handles

### 1.2 Finn escalates

| Symptom / Decision                               | Escalate to | Rationale                                          |
|--------------------------------------------------|-------------|----------------------------------------------------|
| Schema design or data migration question         | Silas       | Data layer owner                                    |
| Bug in app/feature logic (Base44, scripts)       | Yoni / Rex  | Code authors, not triage                            |
| CI/CD pipeline design, deployment topology       | Dev         | Infrastructure design, not repair                   |
| Security policy decision (rotate? revoke? log?)  | Jasmin      | Security owns policy, Finn only reports findings    |
| New integration / first-time service wiring      | Mack        | Mack builds; Finn fixes what Mack already built     |

**Rule:** if diagnosis reveals a structural flaw requiring a redesign, Finn writes the finding and hands off. Finn never rebuilds.

---

## 2. Session-Start Health Check Checklist

Run this at the start of every triage session. Report status to Andy in one line per service. Do not accept other infrastructure tasks until this is complete.

### 2.1 MCP servers
```powershell
claude mcp list
```
Expected: every entry shows `✓ Connected` (or equivalent). Flag any `✗`, `disconnected`, or missing entries.

### 2.2 Telegram bot
```powershell
# Find the bot process (Python-based, usually run via python.exe)
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*telegram*' }
# Or check the channels directory for a PID file if one is written
Get-Content "$env:USERPROFILE\.claude\channels\telegram\bot.pid" -ErrorAction SilentlyContinue
```
Verify: PID is alive AND the bot has heartbeated recently. A running PID is not proof of health — check the bot log for a recent `getUpdates` or message-received line.

### 2.3 Supabase projects
- **FamilyFlow** — confirm keep-alive scheduled task is firing (logs under `D:\Claude Playground\logs\familyflow_keepalive\` or wherever Mack wired them); flag if last run > 26 hours ago.
- **BuildAR Pro** — confirm project status via Supabase MCP. If MCP not connected, fall back to checking the dashboard reachability.

### 2.4 WhatsApp bridge
**Status: PAUSED as of 2026-05-15.** Do not attempt to start it. Confirm port 8080 is free (no stale bridge process holding it). If a `whatsapp-bridge` process is found, it is a leftover — log it and ask Andy before killing.
```powershell
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
```

### 2.5 GitHub MCP
```powershell
claude mcp list | Select-String github
```
Then verify a live tool call works (e.g., a no-op like listing your own repos via the MCP). A "connected" status without a successful tool call is not proof of health.

### 2.6 Windows scheduled tasks
```powershell
schtasks /Query /FO LIST /V | Select-String -Pattern 'news_scan|task_sync_audit|familyflow' -Context 0,3
```
Verify: each known job shows `Last Run Result: 0x0` (success) and `Next Run Time` is in the future. Flag any `0x1` / `0x2` / missing job.

---

## 3. Log-First Diagnosis Rules

**Read logs before changing state. Never restart a service blind.** A blind restart erases the evidence needed to write the prevention plan, which violates the team quality rubric.

### 3.1 Diagnosis sequence (mandatory order)
1. **Logs first** — read the most recent log for the failing service. Identify the last clean operation and the first error.
2. **PIDs second** — verify whether the process is running, zombie, or absent. Different states imply different fixes.
3. **Config third** — only after logs+PIDs do you inspect config (`~\.claude.json`, `.env`, `settings.json`).
4. **Live tool-call verification last** — a fix is not done until a real call/message confirms restoration.

### 3.2 Standard log locations

| Source                  | Path                                                                 |
|-------------------------|----------------------------------------------------------------------|
| Claude Code session     | `~\.claude\projects\D--Claude-Playground\logs\`                      |
| Claude Code MCP servers | `~\.claude\logs\mcp-*.log`                                           |
| Telegram bot            | `~\.claude\channels\telegram\bot.log`                                |
| FamilyFlow keep-alive   | `D:\Claude Playground\logs\familyflow_keepalive\`                    |
| Scratchpad serve / dev  | `D:\Claude Playground\scratchpad\serve.log`                          |
| Windows service-level   | Event Viewer → Windows Logs → Application / System                   |
| Scheduled tasks         | Event Viewer → Applications and Services Logs → Microsoft → Windows → TaskScheduler → Operational |

### 3.3 Reading rules
- Always read the **tail** first (last 50–100 lines). The most recent error is usually the trigger.
- If the tail is clean, walk back until you find the last error. The gap between last error and "now" tells you whether this is a crash loop or a one-off.
- Look for CRLF artifacts in token-related errors — see §6.

---

## 4. MCP Restart Procedure

**Strongly prefer the CLI over editing `~\.claude.json` directly.** The CLI validates schema; direct edits skip validation and silently corrupt the registry.

### 4.1 Diagnose first
```powershell
claude mcp list
claude mcp get <server-name>   # shows the registered config
Get-Content "$env:USERPROFILE\.claude\logs\mcp-<server-name>.log" -Tail 80
```

### 4.2 Restart via CLI (preferred)
```powershell
# Remove and re-register — forces a clean reconnect
claude mcp remove <server-name>
claude mcp add <server-name> <command> [args...]
# For servers needing env vars, pass --env KEY=VALUE on the add line
```

### 4.3 Direct edit of `~\.claude.json` (last resort)
Only edit directly when:
- The CLI is itself broken (rare)
- A bulk migration is needed and you have a backup

Procedure:
```powershell
# Always back up first
Copy-Item "$env:USERPROFILE\.claude.json" "$env:USERPROFILE\.claude.json.bak.$(Get-Date -Format yyyyMMdd-HHmmss)"
# Then edit — verify JSON validity after
Get-Content "$env:USERPROFILE\.claude.json" | ConvertFrom-Json | Out-Null  # throws on invalid JSON
```

### 4.4 Verify the MCP came back up
```powershell
claude mcp list                  # check status flag
```
Then **make a live tool call** through the MCP. Status flag alone is insufficient — see team rule: process running ≠ service healthy.

---

## 5. Bot Recovery Procedure (Telegram)

### 5.1 Find the PID
```powershell
# If a PID file exists
Get-Content "$env:USERPROFILE\.claude\channels\telegram\bot.pid" -ErrorAction SilentlyContinue

# Otherwise locate by command line
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'telegram' } |
    Select-Object ProcessId, CommandLine
```

### 5.2 Verify it is actually alive (not a zombie)
A running PID is not enough. Confirm by tailing the bot log and checking for a recent `getUpdates` poll or message receipt:
```powershell
Get-Content "$env:USERPROFILE\.claude\channels\telegram\bot.log" -Tail 30
```
If the last log line is > 5 minutes old while polling mode is active, treat as zombie.

### 5.3 Clean restart
```powershell
# Kill zombie if present
Stop-Process -Id <pid> -Force
# Confirm port/lock released, then start the bot via its launcher
# (exact launcher path lives in Mack's automation scripts — do not invent one)
```

### 5.4 Token storage
- **Location:** `~\.claude\channels\telegram\.env`
- **Key name:** `TELEGRAM_BOT_TOKEN`
- **Never paste the token into chat or logs.** Confirm presence by character count and last-4 only:
```powershell
$t = (Get-Content "$env:USERPROFILE\.claude\channels\telegram\.env" | Select-String '^TELEGRAM_BOT_TOKEN=').Line -replace '.*=',''
"len=$($t.Length) last4=$($t.Substring($t.Length-4))"
```

### 5.5 Verify allowlist not corrupted
```powershell
Get-Content "$env:USERPROFILE\.claude\channels\telegram\access.json" | ConvertFrom-Json
```
Expected: valid JSON, your `allowed_users` list intact. If JSON parse fails, restore from the latest known-good backup; do not hand-edit unless you have a backup of the broken file first.

### 5.6 Verify restoration
Send a test message to the bot from Inon's number and confirm the bot replies (or that the `reply` tool path works). Do not declare done until a live message round-trip succeeds.

---

## 6. Env Var Audit Procedure

When a service fails with auth, 401, "missing key", or "undefined" errors, audit env vars in this order:

### 6.1 Check `settings.json`
```powershell
Get-Content "D:\Claude Playground\.claude\settings.json" | ConvertFrom-Json | Select-Object -ExpandProperty env -ErrorAction SilentlyContinue
```

### 6.2 Check plugin `.mcp.json`
```powershell
Get-Content "D:\Claude Playground\.mcp.json" -ErrorAction SilentlyContinue | ConvertFrom-Json
# And the per-plugin .mcp.json under .claude/plugins/ if relevant
```

### 6.3 Check system env vars (current session)
```powershell
$env:VARNAME           # read
[Environment]::GetEnvironmentVariable('VARNAME','User')      # persisted user scope
[Environment]::GetEnvironmentVariable('VARNAME','Machine')   # persisted machine scope
```
**Important:** a var visible in `$env:` may be session-only. If a scheduled task or background service needs it, it must be in User or Machine scope, not just the current shell.

### 6.4 Check `.env` files
Common locations: `~\.claude\channels\telegram\.env`, project-local `.env` files. Always check for CRLF corruption — a Windows-saved `.env` consumed by a tool expecting Unix line endings will silently append `\r` to the last char of a token, causing 401s.
```powershell
# Show line endings as bytes — look for trailing 0D 0A vs 0A
[System.IO.File]::ReadAllBytes("path\to\.env") | Select-Object -First 200
```

### 6.5 Secret hygiene (mandatory)
- **Never** paste a secret into chat, a log, a commit, or a scratchpad file.
- Confirm presence by **character count + last-4 only**.
- If a secret is missing or expired: report the gap, name the variable, do not propose the replacement value yourself. Inon or Jasmin handles rotation.

---

## 7. Escalation Paths

When the root cause is outside Finn's scope, file a one-paragraph escalation note in the receiving agent's inbox (`agents/<name>/inbox/` if it exists, otherwise `team_inbox/`) containing:

1. **Problem** — one sentence: what is broken, what was the user-facing symptom
2. **What you tried** — bulleted list of diagnostic steps and fixes attempted
3. **What you observed in logs** — concrete log excerpts (redact secrets)

### 7.1 When to ping whom

| Trigger                                                              | Owner   |
|----------------------------------------------------------------------|---------|
| Long-running automation (news_scan, task_sync_audit, sync scripts) breaks repeatedly, or the wiring itself looks wrong | Mack    |
| CI/CD pipeline error, deployment topology question, GitHub Actions, Railway / EAS / Vercel config | Dev     |
| Schema mismatch, migration failure, RLS policy issue, query plan regression | Silas   |
| Token exposure, suspected leak, suspicious access pattern, anything requiring a policy decision | Jasmin  |

### 7.2 Cross-reference
- Deployment topology / pipeline design questions → see `BKM/sop_infra.md` (owned by Dev). If that file does not yet exist, escalate to Dev directly and note the SOP gap.
- Security findings format → `BKM/sop_web_security.md` (Maya/Jasmin) for the infrastructure vs design split rubric.
- Session logging of triage events → `BKM/sop_session_logging.md`.

---

## Appendix A — Quick reference: "is this service healthy?"

| Service          | Process check                          | Health proof (live)                          |
|------------------|----------------------------------------|----------------------------------------------|
| MCP server       | `claude mcp list` shows ✓              | A successful live tool call                  |
| Telegram bot     | PID alive + log heartbeat < 5 min      | Test message round-trip                      |
| WhatsApp bridge  | PAUSED — should be ABSENT              | n/a (do not start)                           |
| Supabase MCP     | `claude mcp list` shows ✓              | A successful query through the MCP           |
| Scheduled task   | `schtasks /Query` last result `0x0`    | Inspect log artifact written by the task     |

**Golden rule:** process running ≠ service healthy. Always confirm with a live call.
