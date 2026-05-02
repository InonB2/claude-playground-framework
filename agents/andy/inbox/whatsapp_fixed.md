# WhatsApp MCP Debug Report
**Agent:** Mack  
**Date:** 2026-05-02  
**Status:** Config verified — bridge startup is the only missing step

---

## What was investigated

1. `C:\Users\Inon Baasov\.claude\settings.json` — MCP entry for `whatsapp`
2. `C:\tools\whatsapp-mcp\whatsapp-mcp-server\` — Python MCP server files
3. `C:\tools\whatsapp-mcp\whatsapp-bridge\` — Go bridge binary and session store
4. Python binary at configured path — version and package availability
5. All required Python imports (mcp, FastMCP, requests, whatsapp module)
6. DB path resolution from the configured cwd

---

## Findings

### What is correct (no changes needed)

| Item | Status |
|------|--------|
| Python binary path | OK — `C:\Users\Inon Baasov\AppData\Local\Python\bin\python.exe` exists, Python 3.14.4 |
| main.py path | OK — file exists at `C:\tools\whatsapp-mcp\whatsapp-mcp-server\main.py` |
| cwd setting | OK — `C:\tools\whatsapp-mcp\whatsapp-mcp-server` is correct |
| mcp package | OK — `from mcp.server.fastmcp import FastMCP` imports cleanly |
| requests package | OK — installed |
| whatsapp module | OK — imports cleanly |
| DB path resolution | OK — resolves to `C:\tools\whatsapp-mcp\whatsapp-bridge\store\messages.db` |
| Session files | OK — `whatsapp.db` (2.1 MB) and `messages.db` (64 KB) exist in bridge/store/ — QR scan was successful |
| MCP server startup | OK — starts without errors in stdio mode |

### Root cause: Bridge not running

The MCP Python server connects to the Go bridge at `http://localhost:8080/api`. The bridge process (`whatsapp-bridge.exe`) was **not running** at investigation time. Claude Code MCP servers start when Claude Code starts — if the bridge is not already running, any tool call that hits the API will fail with a connection refused error.

This is not a config issue. The settings.json entry is correct as-is.

**The one and only fix: start the bridge before starting Claude Code.**

---

## Current settings.json entry (correct — no change made)

```json
"whatsapp": {
  "command": "C:\\Users\\Inon Baasov\\AppData\\Local\\Python\\bin\\python.exe",
  "args": ["C:\\tools\\whatsapp-mcp\\whatsapp-mcp-server\\main.py"],
  "cwd": "C:\\tools\\whatsapp-mcp\\whatsapp-mcp-server"
}
```

Note: The upstream README suggests using `uv run` as the command. `uv` is not installed on this machine. The direct Python approach works because all dependencies (mcp, requests) are installed in that Python environment. No change needed.

---

## What Inon needs to do

### Every time before starting Claude Code:

**Option A — Manual start (run once in a terminal, leave it open):**
```powershell
Start-Process -FilePath "C:\tools\whatsapp-mcp\whatsapp-bridge\whatsapp-bridge.exe" -WorkingDirectory "C:\tools\whatsapp-mcp\whatsapp-bridge"
```
Or just double-click `whatsapp-bridge.exe` in Explorer.

**Option B — Background start (recommended, run in PowerShell):**
```powershell
Start-Process -FilePath "C:\tools\whatsapp-mcp\whatsapp-bridge\whatsapp-bridge.exe" `
  -WorkingDirectory "C:\tools\whatsapp-mcp\whatsapp-bridge" `
  -WindowStyle Hidden
```

**Option C — Auto-start with Windows Task Scheduler (set-and-forget):**
Create a task that runs `whatsapp-bridge.exe` at user login. Mack can set this up via the scheduled-tasks MCP if requested.

### After starting the bridge:
1. Start Claude Code (or restart if already open)
2. The `whatsapp` MCP tools will appear in the tool list
3. First tool call will verify connection to `http://localhost:8080/api`

### Re-authentication:
The bridge uses the session in `whatsapp-bridge\store\whatsapp.db`. You will need to re-scan the QR code approximately every 20 days (WhatsApp multi-device limitation). Run the bridge in a visible window when re-auth is needed.

---

## No settings.json changes were made

The config is already correct. The only action required is establishing the bridge startup habit described above.
