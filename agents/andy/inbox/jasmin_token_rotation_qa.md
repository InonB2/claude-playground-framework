# Jasmin — Token Rotation QA Verdict

**From:** Jasmin (tester)
**To:** Andy
**Date:** 2026-05-18
**Task:** TELEGRAM-TOKEN-ROTATE-2026-05-17 — Step 3 (QA)
**Worker:** Mack
**Tester:** Jasmin
**Verdict:** **PASS WITH NOTES**

---

## TL;DR

Mack's six rotation claims all verify independently. The listener is alive on the new token, polling cleanly (200 OK on `getMe` / `deleteWebhook` / `getUpdates`), no 409 Conflict, no auth errors. My own end-to-end send via `buildar_notify.py update` returned `[OK]` with exit code 0. Scripts hard-fail if `TELEGRAM_BOT_TOKEN` is missing, and no hardcoded fallback exists in either file. SOP `BKM/sop_env_secrets.md` is present, accurate, and indexed.

The httpx-logger leak Mack flagged is **real and active**: the secret half of the live token appears 9 times in `scratchpad/telegram_listener.log` (confirmed via length-only count, never echoed). Severity is **Medium** — gitignored and on a single-user laptop, so the public-internet blast radius is zero — but it violates the same "secrets never live on disk in plaintext" principle we just enforced for scripts, and the log grows unbounded with new poll entries every ~30 s. Recommendation: dispatch a small follow-up to Yoni/Mack to raise the httpx logger to WARNING (one-line fix) and add basic log rotation. Not a blocker on this rotation task.

---

## Findings — Infrastructure

### 1. Grep proof — tracked tree is clean (PASS)

`git grep "AAEyGQODr6F1dXVlvabJO9MX_u1JFONdr1I"` from `D:\Claude Playground` returned zero hits. The old (revoked) token is no longer in any tracked file on master. Mack's three documented residual locations (the brief in `agents/mack/inbox/`, gitignored `scratchpad/telegram_listener.log`, and `.claude/worktrees/agent-*/` snapshots) are out-of-scope per the rotation brief and harmless because the token itself is dead.

### 2. Both scripts require env, no hardcoded fallback (PASS)

- `scripts/telegram_listener.py` lines 53–66: `load_dotenv(ENV_FILE)`, then `os.environ.get("TELEGRAM_BOT_TOKEN")`, then `sys.exit(2)` with a clear FATAL message if unset. No literal token in the file.
- `scripts/buildar_notify.py` lines 23–51: `_load_dotenv()` helper (python-dotenv primary, manual stdlib fallback), then `os.environ.get("TELEGRAM_BOT_TOKEN")`, then `raise SystemExit(...)` if unset. No literal token in the file.

Both scripts will refuse to start without `.env` populated. Mechanically impossible to commit a working token through these scripts.

### 3. `.env` loader works (PASS)

Confirmed by source trace (above) and by behaviour: the end-to-end send (item 5) succeeded against `D:\Claude Playground\.env`, proving the loader populates `os.environ` correctly. `python-dotenv` 1.2.2 is installed on the host. `buildar_notify.py` also has a 6-line stdlib fallback parser so it still works on a stripped fresh machine.

### 4. Listener alive on the new token (PASS)

- Process: `pythonw.exe ... telegram_listener.py`, **PID 65832**, started 2026-05-18 07:48:09 — matches Mack's claimed PID exactly. Singleton lock on port 50917 acquired.
- Last 30 lines of `scratchpad/telegram_listener.log` show: `Application started` at 07:48:11, then `getUpdates` polls at 07:48:41, 07:49:13, 07:49:46, 07:50:18, all `HTTP/1.1 200 OK`.
- Zero 409 Conflict events. Zero `InvalidToken` / 401 / 403 errors anywhere since the restart.
- Bot-token mask in log header shows `8731882312...` (just the public bot ID portion) — confirms the new token is what the process is using.

### 5. End-to-end send works (PASS — verified by Jasmin, not relying on Mack)

```
> python "D:/Claude Playground/scripts/buildar_notify.py" update "Jasmin QA verification - token rotation OK"
[OK] Notification sent (update)
EXITCODE=0
```

Inon's Telegram should now show that message as proof. End-to-end chain (env loader → new token → Telegram Bot API → Inon's chat) is intact.

### 6. BKM SOP exists, correct, and indexed (PASS)

- `BKM/sop_env_secrets.md` exists, dated 2026-05-18, owned by Mack. Contents cover: the env-only rule, the required Python pattern (copy-pasteable), fresh-machine setup, the leak-rotation drill (rotate at source → scrub tree → restart processes → verify → don't rewrite history), and the known httpx-logger follow-up.
- `BKM/INDEX.md` row 19 lists `sop_env_secrets.md` with the correct file path, owner, and one-line summary.

---

## Findings — Design

### D1. httpx INFO logger is leaking the live token to disk (Medium — confirmed independently)

**Reproduction.** Extracted the secret-half of `TELEGRAM_BOT_TOKEN` from `.env` programmatically (never echoed to stdout), grepped `scratchpad/telegram_listener.log` for it via `Select-String -SimpleMatch -AllMatches` reporting only the count:

```
Secret-half hits in listener log: 9
```

Leak is real and active. Each future `getUpdates` poll (every ~30 s) adds one more occurrence. After 1 hour of uptime that's ~120 more; after a day, ~2,800.

**Severity assessment.**

| Vector | Status | Impact |
|--------|--------|--------|
| Git exposure | Mitigated | `scratchpad/telegram_listener.log` is explicitly listed in `.gitignore` line 23. No risk of accidental commit via `git add -A` — gitignore takes precedence. |
| Local filesystem ACL | Loose | File ACL: `Authenticated Users` allow Modify; `BUILTIN\Users` allow ReadAndExecute. Any local Windows account on this machine can read the file. On Inon's single-user laptop this is currently a one-account threat surface, but tightening to owner-only would be defensible. |
| Log rotation | Absent | No `RotatingFileHandler` / `TimedRotatingFileHandler` in `telegram_listener.py`. Log grows unbounded. Currently 1,442 lines / 191 KB after 2 days. The token will accumulate indefinitely until the next rotation. |
| Realistic threat model | Low-but-not-zero | Single-user laptop, no remote shell exposed, no cloud sync configured on `scratchpad/` (verified separately is not in scope here but worth checking). Any tool with read access to the working tree — IDE plugins, backup software, OS indexers — can lift the token. |

**Conclusion:** Same conceptual severity class as the original leak (plaintext live token sitting on disk where it doesn't need to be), but the blast radius is far smaller because there's no public-internet path. Not a blocker on this rotation task; **should be dispatched as a follow-up** before another agent commits or syncs anything from `scratchpad/`.

### D2. Recommended remediation — Quick fix, with one structural follow-up

**Pick: Quick fix (raise httpx logger to WARNING).**

Justification:
- One line added near `telegram_listener.py`'s logging setup: `logging.getLogger("httpx").setLevel(logging.WARNING)`.
- Eliminates the leak vector at the source with zero risk to functionality (httpx WARNING/ERROR will still surface real problems).
- The stricter alternative (custom redacting filter) is more code, more fragile (regex on URL params), and overkill for what is essentially noisy debug output we never use.

Structural follow-up worth bundling: add a `RotatingFileHandler` (e.g. 5 MB × 3 backups) so that even if some future logger does leak a secret, the disk footprint is bounded and old logs eventually evict.

### D3. Script style inconsistency (Cosmetic — Mack flagged this already)

`telegram_listener.py` uses `sys.exit(2)`, `buildar_notify.py` uses `raise SystemExit(...)`. Functionally identical. Not worth a fix on its own; harmonize next time either file gets touched.

### D4. `TELEGRAM_CHAT_ID` default kept (correct call — not a finding)

The chat ID `6283854178` is Inon's public user ID, not a secret. Keeping the default in `buildar_notify.py` is fine — agents calling the notifier don't need to thread the chat ID through every call. No change required.

---

## What I deliberately did NOT do

- Did NOT print or echo the new token (or its secret half) anywhere in this report — used length-only count for verification.
- Did NOT modify any script, `.env`, or `tasks/active_tasks.json`.
- Did NOT push to GitHub.
- Did NOT send a Telegram HOLD alert (verdict is PASS WITH NOTES, not HOLD).
- Did NOT clean up or rotate `scratchpad/telegram_listener.log` — that's a worker job for the follow-up.

---

## Recommended next steps for Andy

1. **Mark TELEGRAM-TOKEN-ROTATE-2026-05-17 as Done** in `tasks/active_tasks.json` — worker=Mack, tester=Jasmin.
2. **Dispatch a small follow-up task** (1-line code change + log rotation): assign to Yoni or Mack to add `logging.getLogger("httpx").setLevel(logging.WARNING)` and a `RotatingFileHandler` in `scripts/telegram_listener.py`, then truncate/rotate the existing `scratchpad/telegram_listener.log` so the historical leaked entries are evicted. QA: any agent except the worker (likely me or Vera).
3. **Optional defence-in-depth** for later: add a `gitleaks` pre-commit hook so the next someone-tries-to-commit-a-secret event fails locally instead of reaching GitHub.

---

**Final verdict:** PASS WITH NOTES.

— Jasmin
