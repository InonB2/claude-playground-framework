# GitHub Personal Access Token — Secure Setup Guide

**By:** Mack (Automation Engineer)
**Date:** 2026-04-27

---

## IMPORTANT: Never Paste Your Token in Chat

A GitHub Personal Access Token (PAT) is like a password. **Do not paste it here or anywhere visible.** Follow the steps below to use it securely.

---

## Step 1 — You Said You Created a Key — Here's Where It Lives

When you created a PAT on GitHub:
- Go to: `github.com` → Your profile photo → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
- Your token looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Copy it now** — GitHub only shows it once

---

## Step 2 — Store It Securely (Two Options)

### Option A — Windows Credential Manager (Recommended, no file needed)

1. Open **Git Bash** or **Command Prompt** in `D:/Claude Playground`
2. Run:
   ```bash
   git remote set-url origin https://github.com/InonBaasov/claude-playground-framework.git
   git push origin master
   ```
3. A **Windows login dialog** will pop up
4. Enter:
   - Username: `InonBaasov`
   - Password: **paste your token here** (not your GitHub password — your PAT)
5. Windows saves it — you won't need to enter it again

### Option B — `.env` File (For scripts that need it)

1. Create a file called `.env` in `D:/Claude Playground/` (it's already in `.gitignore` so it won't be committed)
2. Add this line:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   ```
3. To use it in the sync script:
   ```bash
   # In scripts/github_sync.sh, the token is read automatically
   source .env
   git remote set-url origin https://${GITHUB_TOKEN}@github.com/InonBaasov/claude-playground-framework.git
   git push origin master
   ```

---

## Step 3 — Push the Framework

Once credentials are stored, run from `D:/Claude Playground`:

```bash
git push origin master
```

Expected output:
```
Enumerating objects: 47, done.
Writing objects: 100%
To https://github.com/InonBaasov/claude-playground-framework.git
 * [new branch] master -> master
```

---

## Step 4 — Create the Website Portfolio Repo

1. Go to `github.com/new`
2. Name: `Website-product-portfolio`
3. Private or Public — your choice
4. **Do not** initialize with README (we'll push from local)
5. Click **Create repository**
6. Tell me the repo URL and Mack will set up the remote and push

---

## Step 5 — Auto-Sync Setup

After the first push works, run this to sync automatically:

```bash
bash scripts/github_sync.sh
```

For daily auto-sync, add to Windows Task Scheduler:
- **Action:** `bash "D:/Claude Playground/scripts/github_sync.sh"`
- **Trigger:** Daily at a set time, or on login

---

## Token Permissions Needed

When creating the PAT, make sure these are checked:
- [x] `repo` — Full control of private repositories
- [x] `workflow` — Update GitHub Actions (optional but useful later)

Token expiry: Set to **90 days** or **No expiration** (your preference).

---

## Quick Checklist

- [ ] Token created on GitHub (starts with `ghp_`)
- [ ] Token stored via Windows Credential Manager OR `.env` file
- [ ] `git push origin master` runs without asking for credentials
- [ ] `Website-product-portfolio` repo created on GitHub
- [ ] Mack wires up the website migration
