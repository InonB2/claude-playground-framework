# WhatsApp ↔ Claude Bridge: Setup Guide

**By:** Mack (Automation Engineer)
**Date:** 2026-04-27
**Task ID:** WHATSAPP-001

---

## Why WhatsApp Is Harder Than Telegram

WhatsApp does not have an official public bot API. The three options below range from easiest to most powerful:

---

## ~~Option 1 — `npx claude-code-whatsapp`~~ (REMOVED — package does not exist on npm)

This option was removed from the guide. `claude-code-whatsapp` returns a 404 from the npm registry.
**Use Option 2 or Option 3 instead.**

---

## Option 2 — WhatsApp MCP Server (More Powerful)

**What it does:** Full integration — Claude can read your messages, send replies, search chat history.

### Popular Open-Source Options
- [whatsapp-mcp](https://github.com/lharries/whatsapp-mcp) — Go-based bridge
- [mcp-whatsapp](https://github.com/mario-andradeino/mcp-whatsapp) — Node.js bridge

### Setup Steps (whatsapp-mcp)
1. Install Go: [golang.org/dl](https://golang.org/dl/)
2. Clone the repo:
   ```bash
   git clone https://github.com/lharries/whatsapp-mcp
   cd whatsapp-mcp
   go run .
   ```
3. Scan the QR code with your WhatsApp
4. Add to Claude Code config (`~/.claude/settings.json` or Claude Desktop config):
   ```json
   {
     "mcpServers": {
       "whatsapp": {
         "command": "go",
         "args": ["run", "C:/path/to/whatsapp-mcp/main.go"]
       }
     }
   }
   ```
5. Restart Claude Code — new WhatsApp tools will appear

---

## Option 3 — Custom WhatsApp MCP (Our Own)

**What it does:** A bespoke MCP server tailored to the framework — notifies you of `/owner_inbox/` updates, accepts tasks from WhatsApp, connects to the agent pipeline.

### Why Build Our Own?
- Tailored exactly to our inbox/outbox flow
- Can trigger Andy directly from WhatsApp
- Can send approval requests + accept "APPROVE" replies
- No dependency on external repos

### Implementation Plan (Mack will build this)
1. Node.js server using `@whiskeysockets/baileys` (WhatsApp Web API)
2. MCP tool definitions:
   - `send_whatsapp_message(to, text)` — send a message
   - `get_new_messages()` — poll for new messages
   - `watch_owner_inbox()` — notify when files appear in `/owner_inbox/`
3. File: `scripts/whatsapp_mcp_server.js`
4. Register in `~/.claude/settings.json`

### Estimated Build Time: 2-3 hours

---

## Recommendation (Updated 2026-04-28)

| Option | Setup Time | Power | Requires | Status |
|--------|-----------|-------|----------|--------|
| ~~`npx claude-code-whatsapp`~~ | ~~5 min~~ | ~~Basic~~ | ~~Node.js~~ | **REMOVED — package 404** |
| whatsapp-mcp (Option 2) | 30-45 min | Full read/write | Go + Python | Available — install Go first |
| Custom MCP (Option 3) | 2-3 hrs | Full + framework-integrated | Node.js only | **RECOMMENDED** — Mack builds this |

**Recommended path:**
- **Short term:** Install Go from [golang.org/dl](https://golang.org/dl/) → follow Option 2 steps above
- **Long term:** Mack builds Option 3 (Node.js + baileys) for full framework integration — no Go needed

**Current blocker:** Go is not installed on the machine. Python 3.11.9 ✓, Node.js 24.15.0 ✓, Go ✗.

## Quick Start (Option 2 — Do This When Ready)

```powershell
# 1. Install Go from golang.org/dl (LTS installer)
# 2. Restart terminal
# 3. Then:
git clone https://github.com/lharries/whatsapp-mcp.git C:\tools\whatsapp-mcp
cd C:\tools\whatsapp-mcp
go run .
# Scan QR code with WhatsApp → Linked Devices → Link a Device
```
