# WhatsApp ↔ Claude Bridge: Setup Guide

**By:** Mack (Automation Engineer)
**Date:** 2026-04-27
**Task ID:** WHATSAPP-001

---

## Why WhatsApp Is Harder Than Telegram

WhatsApp does not have an official public bot API. The three options below range from easiest to most powerful:

---

## Option 1 — `npx claude-code-whatsapp` (RECOMMENDED — Easiest, 5 min)

**What it does:** Scans a QR code with your WhatsApp, then lets you message yourself to trigger Claude Code actions.

### Setup Steps

1. Open a terminal in your project folder (`D:/Claude Playground`)
2. Make sure Node.js is installed. Check: `node --version`
   - If not installed: download from [nodejs.org](https://nodejs.org) (LTS version)
3. Run:
   ```bash
   npx claude-code-whatsapp
   ```
4. A **QR code** will appear in your terminal
5. On your phone: WhatsApp → **Linked Devices** → **Link a Device** → scan the QR
6. Done. Send a message to **yourself** on WhatsApp like:
   ```
   What files are in the agents folder?
   ```
   Claude Code will respond directly in the chat.

### How It Works
- Acts as a WhatsApp Web session on your computer
- Messages to yourself trigger Claude Code
- Responses come back as WhatsApp messages
- No account, no API key, no business verification needed

### Limitations
- Must keep your computer running (it's a local process)
- Uses WhatsApp Web (unofficial API — Meta can block it, but rarely does for personal use)
- No persistent memory between sessions unless you run it continuously

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

## Recommendation

| Option | Setup Time | Power | Risk |
|--------|-----------|-------|------|
| `npx claude-code-whatsapp` | 5 min | Basic (message yourself) | Low |
| MCP Server (existing) | 30 min | Full read/write | Low-Medium |
| Custom MCP | 2-3 hrs | Full + framework-integrated | Low |

**Start with Option 1 today.** Let Mack build Option 3 in a future session for full integration.

---

## Quick Start (Option 1 — Do This Now)

```bash
# In your project terminal:
node --version          # confirm Node.js installed
npx claude-code-whatsapp
# Scan QR with your phone
# Done!
```
