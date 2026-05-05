# Repository Audit — Refactor Plan
**Audited by:** Tomy (Researcher)
**Date:** 2026-05-01
**Repos covered:** claude-playground-framework, website-product-portfolio, pro-maker-ar, .claude/worktrees/

---

## REPO 1: claude-playground-framework
**Path:** `D:/Claude Playground/`
**Remote:** https://github.com/InonB2/claude-playground-framework
**Branch:** master (ahead of origin/master by 1 commit — unpushed)

### Git Status
- **Unpushed commit:** Yes (1 commit ahead of origin/master). Run `git push` to sync.
- **Unstaged deletions (large):** The entire `team_inbox/cv_archive/` tree (50+ CV .pdf/.pptx files for 2025 and 2026) shows as deleted — these were physically removed but never committed as deletions. This is the biggest noise item in `git status`.
- **Unstaged modifications:**
  - `CLAUDE.md` — modified
  - `owner_inbox/linkedin_posts_refreshed.md` — modified
  - `sites/website-product-portfolio` — submodule has new commits (normal)
- **Untracked files (6 items):**
  - `archive/` — new folder, untracked
  - `owner_inbox/BuildARPro_scan3d_options.md`
  - `owner_inbox/cv_selection_recommendation.md`
  - `owner_inbox/thought_leadership_batch_001.md`
  - `scratchpad/buildarproapp_scan3d_research.md`
  - `scratchpad/linkedin_video_posts_v2.md`

### Branches
- **Local stale branches:** `claude/elastic-jepsen-7f43fb`, `claude/reverent-antonelli-a23449`, `claude/sharp-payne-f30a08` — all are old Claude Code worktree branches. None have unique commits ahead of master (verified). Safe to delete.
- **Remote stale branches:** `origin/claude/reverent-antonelli-a23449`, `origin/claude/sharp-payne-f30a08` — pushed to GitHub and also stale.

### .gitignore Health
Current `.gitignore` covers: `.env`, `*.key`, `*.pem`, `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `node_modules/`, `.DS_Store`, `Thumbs.db`.

**Missing patterns:**
- `*.db` — `memory/session_log.db` and `store/*.db` are binary SQLite files being tracked
- `store/` — `store/messages.db`, `store/whatsapp.db` are tracked; should likely be ignored
- `*.pptx`, `*.pdf`, `*.docx` — large binary CV/Office files are being tracked in `team_inbox/cv_archive/` and `owner_inbox/`. These inflate repo size significantly.
- `scratchpad/cv_template/`, `scratchpad/cv_v9/` — exploded PPTX internals (XML files) were committed and should not be tracked
- `output/cv_archive/cv_archive.db` — database binary
- `bun.lockb` — lock file in pro-maker-ar (if ever used here)

### README Accuracy
**File:** `D:/Claude Playground/README.md`
**Issues found:**
- Lines 16, 20, 67, 96 reference `/output/` and `/output/cv_archive/` — this folder is **deprecated and removed** per CLAUDE.md. README is stale on this point.
- Table row: `| /output/cv_archive/ | output/cv_archive/INDEX.md | CV versions + applications |` — INDEX.md is gone (folder deleted).
- Line 96: `conn = sqlite3.connect("output/cv_archive/cv_archive.db")` — wrong path; archive now lives in `owner_inbox/archive/cv_archive/`.
- `package.json` only contains `pptxgenjs` — README does not mention this dependency at all. Low priority but worth noting.

### Folder Structure Issues
- `archive/cv_inon/2025/` and `archive/cv_inon/2026/` — untracked folder at repo root containing CV files by year. Unclear whether this is intentional or a misplaced copy of what used to be `team_inbox/cv_archive/`. Needs owner decision: keep and add to .gitignore, or move to `owner_inbox/archive/`.
- `scratchpad/cv_template/` and `scratchpad/cv_v9/` — exploded PPTX directory trees (XML fragments). These are binary exploded artifacts committed by mistake. Safe to delete.
- `scratchpad/transcripts/` — two YouTube transcript .txt files (`AtTLckneAQU_transcript.txt`, `vJBAzdOACD8_transcript.txt`). Ephemeral research; safe to delete.
- `scratchpad/` has 19 loose .md files. Most appear to be completed deliverables now duplicated in `owner_inbox/`. Recommend a pass to delete files whose content has been promoted (e.g., `accessibility_audit.md`, `mobile_audit.md`, `hero_copy_draft.md`, `icon_audit.md`, `security_headers_audit.md`, `security_headers_rex_note.md`, `linkedin_refreshed_001.md` — all of which have counterparts in `owner_inbox/`).
- `store/` — appears to contain WhatsApp/messaging databases (`.db` binary files). Not mentioned in folder map. Should be gitignored.

---

## REPO 2: website-product-portfolio
**Path:** `D:/Claude Playground/sites/website-product-portfolio/`
**Remote:** (separate git repo, linked as submodule in framework repo)
**Branch:** main (ahead of origin/main by 1 commit — unpushed)

### Git Status
- Clean working tree. One unpushed commit: `381f07c feat(website): hero copy, icon SVGs, security fixes, URL cleanup`.
- Run: `git -C "D:/Claude Playground/sites/website-product-portfolio" push`

### Branches
- Only `main` branch — clean, no stale branches.

### .gitignore
**No `.gitignore` file exists in this repo.** This is a gap. Currently tracked files include:
- `public/Inon_Baasov_CV.pdf` (61KB) — a downloadable CV PDF. Tracked in git, which is acceptable for a small PDF, but any future CV updates will bloat history.
- `cv-drafts/*.md` — 11 tailored CV markdown files tracked. Fine, but sensitive (contains job application strategy).
- `docs/agent_system.md`, `docs/cv_master_template.md` — internal agent documentation tracked in a public-facing website repo.

**Recommended .gitignore for this repo:**
```
node_modules/
.DS_Store
Thumbs.db
*.local
dist/
.env
```

### README Accuracy
**File:** `D:/Claude Playground/sites/website-product-portfolio/README.md`
- README is accurate and up to date. Phone number was already removed (SEC-07 comment present). No stale paths. Minor: uses emoji in section headers (cosmetic).
- The README references the live URL `https://inon-baasov-website.base44.app` — should be verified that this is still the active deploy URL.

### Folder Structure Issues
- `docs/` folder contains `agent_system.md` and `cv_master_template.md` — internal framework documentation that has no business being in the portfolio website repo. These appear to have been accidentally committed during initial setup.
- `cv-drafts/` contains 11 tailored CVs including `PRODUCT_RESEARCH_REPORT.md` — this is a research artifact, not a CV draft. Misplaced.
- No `node_modules/` (correct — Base44 platform doesn't require local install). Good.

---

## REPO 3: pro-maker-ar (BuildARPro)
**Path:** `D:/Claude Playground/pro-maker-ar/`
**Remote:** https://github.com/InonB2/pro-maker-ar.git
**Branch:** main (up to date with origin/main — clean)

### Git Status
- Clean. Nothing uncommitted. Up to date with remote.

### Branches
- Only `main` — clean.

### .gitignore Health
Standard Vite `.gitignore`. Covers `node_modules`, `dist`, `*.local`, `.vscode/*`, `.DS_Store`. 
**Missing:**
- `.env` — not in .gitignore. If a `.env` file is ever created locally it would be unprotected.
- `supabase/.temp/` — Supabase CLI temp files not covered.

### package.json Health
- Generated by Lovable (gpt-engineer). All `@radix-ui/*` packages pinned to `^1.x` — compatible.
- `lovable-tagger: ^1.0.19` is a devDependency — this is a Lovable-platform-specific package; if this app is ever moved off Lovable it should be removed.
- `bun.lockb` committed alongside `package-lock.json` — **two competing lock files**. This happens because the project was initialized with Bun but npm was also used at some point. Should standardize on one package manager and delete the other lock file.
- `package-lock.json` (253KB) is committed — very large for a lock file; this is normal but worth noting.
- No `node_modules/` committed (correct).

### Security Issue — HIGH PRIORITY
**File:** `D:/Claude Playground/pro-maker-ar/src/integrations/supabase/client.ts`
- The Supabase `anon` (publishable) key is hardcoded directly in source: `SUPABASE_PUBLISHABLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."` 
- This key is committed to git history (commit `8e6fbd8 Add API keys to project` by gpt-engineer-app bot).
- **Mitigation:** Supabase `anon` keys are designed to be public (they only grant row-level-security-protected access), so this is not a critical secret leak. However, it is bad practice to hardcode them. The correct approach is to move them to environment variables via `.env` and Vite's `import.meta.env`.
- The commit message "Add API keys to project" suggests the developer is aware these are keys, but the Lovable platform auto-generates this pattern.

### README Accuracy
**File:** `D:/Claude Playground/pro-maker-ar/README.md`
- This is the **default Lovable/Lovable template README** — it does not describe what BuildARPro actually is, what it does, or its current state. It is entirely generic boilerplate.
- No mention of the app's purpose (AR product visualization for IKEA/furniture items), the Supabase backend, or how to configure API keys.

---

## REPO 4: .claude/worktrees/
**Path:** `D:/Claude Playground/.claude/worktrees/`

### Status: 3 stale worktrees confirmed
All three are registered git worktrees that should be pruned:

| Worktree | Branch | Commit | Unique commits vs master |
|---|---|---|---|
| `elastic-jepsen-7f43fb` | `claude/elastic-jepsen-7f43fb` | `26830a8` | 0 — fully merged into master |
| `reverent-antonelli-a23449` | `claude/reverent-antonelli-a23449` | `917f6bf` | 0 — fully merged into master |
| `sharp-payne-f30a08` | `claude/sharp-payne-f30a08` | `5cf20e3` | 1 — contains session-close commit from 2026-04-29 (already superseded by master) |

All three worktrees are safe to remove. The `sharp-payne` branch content (session close 2026-04-29) is effectively duplicated by later master commits.

---

## PRIORITIZED REFACTOR PLAN

### PRIORITY 1 — Quick Wins (under 5 min each)

**1.1 — Remove stale worktrees**
```bash
git -C "D:/Claude Playground" worktree remove .claude/worktrees/elastic-jepsen-7f43fb --force
git -C "D:/Claude Playground" worktree remove .claude/worktrees/reverent-antonelli-a23449 --force
git -C "D:/Claude Playground" worktree remove .claude/worktrees/sharp-payne-f30a08 --force
git -C "D:/Claude Playground" branch -d claude/elastic-jepsen-7f43fb
git -C "D:/Claude Playground" branch -d claude/reverent-antonelli-a23449
git -C "D:/Claude Playground" branch -d claude/sharp-payne-f30a08
git -C "D:/Claude Playground" push origin --delete claude/reverent-antonelli-a23449
git -C "D:/Claude Playground" push origin --delete claude/sharp-payne-f30a08
```

**1.2 — Push unpushed commits to remote**
```bash
git -C "D:/Claude Playground" push
git -C "D:/Claude Playground/sites/website-product-portfolio" push
```

**1.3 — Delete scratchpad exploded-PPTX folders**
```
D:/Claude Playground/scratchpad/cv_template/    (entire folder — PPTX XML fragments)
D:/Claude Playground/scratchpad/cv_v9/          (entire folder — PPTX XML fragments)
D:/Claude Playground/scratchpad/transcripts/    (YouTube transcript .txt files)
```

**1.4 — Delete completed scratchpad files already promoted to owner_inbox**
Files safe to delete from `D:/Claude Playground/scratchpad/`:
- `accessibility_audit.md` (duplicate of `owner_inbox/accessibility_audit.md`)
- `mobile_audit.md` (duplicate of `owner_inbox/mobile_audit.md`)
- `hero_copy_draft.md` (promoted to `owner_inbox/copy01_hero_draft.md`)
- `icon_audit.md` (promoted to `owner_inbox/ux03_icon_replacements.md`)
- `security_headers_audit.md` (promoted to `owner_inbox/security_headers_audit.md`)
- `security_headers_rex_note.md` (superseded)
- `linkedin_refreshed_001.md` (promoted to `owner_inbox/linkedin_posts_refreshed.md`)

**1.5 — Add .gitignore to website-product-portfolio repo**
Create `D:/Claude Playground/sites/website-product-portfolio/.gitignore`:
```
node_modules/
.DS_Store
Thumbs.db
*.local
dist/
.env
```

---

### PRIORITY 2 — Medium Tasks (under 30 min each)

**2.1 — Commit the cv_archive deletions in framework repo**
The `team_inbox/cv_archive/` files (50+ CV files) have been deleted from disk but not from git tracking. This must be committed:
```bash
git -C "D:/Claude Playground" add -u team_inbox/cv_archive/
git -C "D:/Claude Playground" commit -m "chore: remove team_inbox/cv_archive — files migrated to owner_inbox/archive"
```
This will clean up `git status` significantly.

**2.2 — Update framework README.md**
`D:/Claude Playground/README.md` has four stale references to the deprecated `/output/` folder (lines 16, 20, 67, 96). Update to reflect current structure:
- Replace `/output/cv_archive/` → `/owner_inbox/archive/cv_archive/`
- Replace `APPROVE filename.md → moves to /output/` → `moves to /owner_inbox/archive/`
- Replace SQLite path: `output/cv_archive/cv_archive.db` → `owner_inbox/archive/cv_archive/cv_archive.db`

**2.3 — Update framework .gitignore**
Add to `D:/Claude Playground/.gitignore`:
```
*.db
store/
scratchpad/cv_template/
scratchpad/cv_v9/
archive/
*.pptx
*.pdf
*.docx
*.xlsx
```
Note: Adding `*.pdf`, `*.pptx`, `*.docx` will require explicit `git add -f` for any binary deliverables intentionally tracked (like `owner_inbox/archive/cv_archive/Inon_Baasov_CV_Elbit_2026.pdf`).

**2.4 — Clarify / relocate `archive/cv_inon/` folder**
`D:/Claude Playground/archive/` is untracked and contains `cv_inon/2025/` and `cv_inon/2026/`. Owner decision needed: is this a working copy of CVs for local use only? If so, add `archive/` to `.gitignore`. If it should be tracked, move it to `owner_inbox/archive/cv_inon/` to match the canonical folder structure.

**2.5 — Write a proper README for pro-maker-ar**
`D:/Claude Playground/pro-maker-ar/README.md` is entirely Lovable boilerplate. It should describe:
- What BuildARPro is (AR product visualization app)
- Tech stack (Vite + React + TypeScript + Supabase + shadcn-ui + Tailwind)
- How to configure `.env` with Supabase URL and anon key
- How to run dev server (`npm run dev`)
- Current status (prototype / under development)

**2.6 — Move internal docs out of portfolio website repo**
Files to move or delete from `D:/Claude Playground/sites/website-product-portfolio/docs/`:
- `agent_system.md` — belongs in `D:/Claude Playground/BKM/` or `agents/`
- `cv_master_template.md` — belongs in `D:/Claude Playground/owner_inbox/archive/`
Also: `cv-drafts/PRODUCT_RESEARCH_REPORT.md` — misplaced; belongs in `D:/Claude Playground/scratchpad/` or `owner_inbox/`.

---

### PRIORITY 3 — Complex Tasks (delegate to Yoni)

**3.1 — Rewrite pro-maker-ar Supabase key to use env vars**
`D:/Claude Playground/pro-maker-ar/src/integrations/supabase/client.ts`
Move hardcoded keys to `.env`:
```
VITE_SUPABASE_URL=https://nlxoazmcrlzsezsyvdre.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
```
Update client.ts to use `import.meta.env.VITE_SUPABASE_URL` and `import.meta.env.VITE_SUPABASE_ANON_KEY`.
Add `.env` to `.gitignore`.
Note: The anon key is already in git history — if it ever needs to be rotated, use Supabase dashboard → Project Settings → API → Regenerate anon key.

**3.2 — Resolve dual lock files in pro-maker-ar**
`bun.lockb` and `package-lock.json` both exist. Decide on one package manager:
- If keeping npm: delete `bun.lockb`, run `npm install` to regenerate `package-lock.json`
- If keeping Bun: delete `package-lock.json`, run `bun install`
Commit the cleanup.

**3.3 — Audit and prune binary files from framework git history**
The framework repo has tracked large binary files (CV .pptx, .pdf, .docx, .db) across many commits. Consider using `git filter-repo` or BFG Repo Cleaner to strip these from history, then force-push. This would significantly reduce repo clone size. Needs careful planning and a backup first.

---

## Summary Table

| Item | Repo | Type | Priority |
|---|---|---|---|
| Remove 3 stale worktrees | framework | Quick Win | P1 |
| Push 2 unpushed commits | framework + portfolio | Quick Win | P1 |
| Delete scratchpad/cv_template/, cv_v9/, transcripts/ | framework | Quick Win | P1 |
| Delete 7 promoted scratchpad files | framework | Quick Win | P1 |
| Add .gitignore to portfolio repo | portfolio | Quick Win | P1 |
| Commit team_inbox/cv_archive deletions | framework | Medium | P2 |
| Update README (remove /output/ references) | framework | Medium | P2 |
| Update .gitignore (add *.db, store/, archives) | framework | Medium | P2 |
| Clarify archive/cv_inon/ folder | framework | Medium | P2 |
| Rewrite pro-maker-ar README | pro-maker-ar | Medium | P2 |
| Move docs/ files out of portfolio repo | portfolio | Medium | P2 |
| Move Supabase keys to .env | pro-maker-ar | Complex/Yoni | P3 |
| Resolve dual lock files (bun.lockb vs package-lock.json) | pro-maker-ar | Complex/Yoni | P3 |
| Strip binary files from git history | framework | Complex/Yoni | P3 |
