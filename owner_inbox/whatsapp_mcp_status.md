# WhatsApp MCP Status Report

**By:** Mack (Automation Engineer)  
**Task:** WHATSAPP-001  
**Date:** 2026-05-02  
**Status:** COMPLETE — restart Claude Code to activate

---

## What Was Done

The WhatsApp MCP server is now registered in Claude Code's `settings.json`. After a Claude Code restart, WhatsApp tools will be available in every Claude Code session.

---

## Findings

### Go
- **Installed:** Yes — `go version go1.26.2 windows/amd64`
- The previous setup guide noted Go was not installed; it has since been installed.

### whatsapp-mcp Installation
- **Path:** `C:\tools\whatsapp-mcp`
- **Cloned:** 2026-04-28 (already done in a prior session)
- **Structure:**
  - `whatsapp-bridge/` — Go bridge (has `main.go` + compiled `whatsapp-bridge.exe`)
  - `whatsapp-mcp-server/` — Python MCP server (`main.py`, uses `mcp[cli]`)

### WhatsApp Authentication DB
- **Path:** `D:\Claude Playground\store\whatsapp.db`
- **Size:** 7,864,320 bytes (7.5 MB) — populated, authentication was successful
- **messages.db:** 16,826,368 bytes (16 MB) — message history loaded
- **Last modified:** 2026-05-01 13:43 — active and up to date

### Python Dependencies
- `uv` was NOT installed (required by the README's official config).
- **Resolution:** Installed `mcp[cli]` and `httpx` directly via `pip` into the Windows Store Python 3.11.9 installation.
- Verified: `import mcp` and `import httpx` both succeed with `C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\python.exe`

---

## What Was Added to settings.json

Added a new `mcpServers` block at the top of `C:\Users\Inon Baasov\.claude\settings.json`:

```json
"mcpServers": {
  "whatsapp": {
    "command": "C:\\Users\\Inon Baasov\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe",
    "args": ["C:\\tools\\whatsapp-mcp\\whatsapp-mcp-server\\main.py"],
    "cwd": "C:\\tools\\whatsapp-mcp\\whatsapp-mcp-server"
  }
}
```

All existing settings (permissions, hooks, statusLine, theme, etc.) were preserved unchanged.

---

## What Inon Needs to Do Next

### Step 1 — Start the Go bridge (required each session)

The bridge must be running for the MCP server to send/receive WhatsApp messages. Open a PowerShell window and run:

```powershell
cd C:\tools\whatsapp-mcp\whatsapp-bridge
.\whatsapp-bridge.exe
```

Leave this window open. It will auto-reconnect using the stored session (no QR scan needed — already authenticated).

### Step 2 — Restart Claude Code

Close and reopen Claude Code. The WhatsApp MCP server will start automatically. You should see `whatsapp` appear in the connected MCP servers list.

### Step 3 — Verify tools are available

In Claude Code, ask: "What WhatsApp tools do you have?" — you should see tools like `search_contacts`, `send_message`, `list_chats`, etc.

---

## Architecture Reminder

```
Claude Code (MCP client)
    ↕  stdio
Python MCP Server (whatsapp-mcp-server/main.py)
    ↕  HTTP (port 8080)
Go WhatsApp Bridge (whatsapp-bridge.exe)
    ↕  WhatsApp Web API (multidevice)
WhatsApp servers
```

The Go bridge must be running as a separate process for the Python MCP server to function. If the bridge is not running, WhatsApp tool calls will fail with connection errors.

---

## Known Limitation

`uv` (the package manager recommended by the official README) is not installed. The current config uses system Python directly with pip-installed dependencies. This works fine, but if Python packages are ever reset or a new Python version is installed, re-run:

```powershell
pip install "mcp[cli]>=1.6.0" httpx requests
```
