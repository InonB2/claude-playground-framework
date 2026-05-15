#!/usr/bin/env python3
"""
task_sync_scanner.py — Daily Task Sync Audit (PM-style drift detector)

Reads tasks/active_tasks.json and looks for tasks that LOOK done but are
still marked as pending / in-progress / partial / pending-owner / pending-restart.

Signals checked (per task):
  1. Recent git log commit messages (last N=80 commits)
  2. Recent files in agents/andy/inbox/ (filename + first 400 chars)
  3. Heuristic keyword overlap between task title and signal text

Writes a REPORT to:
    agents/andy/inbox/task_sync_audit_YYYY-MM-DD.md

Does NOT modify active_tasks.json. Auto-edits are too risky — Andy decides.

Run manually:
    python scripts/task_sync_scanner.py
    python scripts/task_sync_scanner.py --stdout   # print only
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_FILE = ROOT / "tasks" / "active_tasks.json"
INBOX_DIR = ROOT / "agents" / "andy" / "inbox"
GIT_LOG_LIMIT = 80
INBOX_RECENT_DAYS = 21
INBOX_PREVIEW_CHARS = 400

OPEN_STATUSES = {
    "pending", "in-progress", "partial", "pending-owner",
    "pending-restart", "in_progress", "blocked",
}

# Words to ignore when scoring keyword overlap
STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "for", "to", "in", "on", "with",
    "via", "by", "at", "is", "be", "from", "into", "new", "task",
    "tasks", "fix", "fixes", "fixed", "add", "added", "update", "updated",
    "build", "built", "create", "created", "setup", "set", "up",
}


# ----------------------------------------------------------------------------
# Tolerant JSON loader (the live file has had stray-comma issues before)
# ----------------------------------------------------------------------------

def load_tasks_tolerant(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
        return data.get("tasks", [])
    except json.JSONDecodeError as e:
        # Try a minimal repair: drop stray standalone '{' lines.
        sys.stderr.write(
            f"[task-sync] JSON parse failed ({e.msg} at line {e.lineno}); "
            "attempting tolerant parse\n")
        lines = raw.splitlines()
        cleaned = []
        for ln in lines:
            stripped = ln.strip()
            # Drop lone "{" that aren't preceded by a key/array context
            if stripped == "{" and (not cleaned or
                                    cleaned[-1].rstrip().endswith(",")):
                continue
            cleaned.append(ln)
        repaired = "\n".join(cleaned)
        try:
            data = json.loads(repaired)
            return data.get("tasks", [])
        except json.JSONDecodeError:
            pass
        # Last-ditch: regex out each task object and parse fields leniently.
        # We grab the substring from one "task_id" to the next so we can also
        # read notes/assigned_to (which may contain quoted text — handle with
        # a non-greedy match up to the next task_id boundary).
        sys.stderr.write("[task-sync] tolerant repair failed; "
                         "falling back to regex extraction\n")
        tasks = []
        # Split raw on "task_id" boundaries, keep each chunk.
        chunks = re.split(r'(?="task_id"\s*:\s*")', raw)
        for chunk in chunks:
            m_id = re.search(r'"task_id"\s*:\s*"([^"]+)"', chunk)
            if not m_id:
                continue
            m_title = re.search(r'"title"\s*:\s*"((?:[^"\\]|\\.)*)"', chunk)
            m_status = re.search(r'"status"\s*:\s*"([^"]+)"', chunk)
            m_assigned = re.search(
                r'"assigned_to"\s*:\s*"((?:[^"\\]|\\.)*)"', chunk)
            m_notes = re.search(
                r'"notes"\s*:\s*"((?:[^"\\]|\\.)*)"', chunk)
            if not (m_title and m_status):
                continue
            tasks.append({
                "task_id": m_id.group(1),
                "title": m_title.group(1),
                "status": m_status.group(1),
                "notes": (m_notes.group(1) if m_notes else "")
                    .replace('\\"', '"').replace('\\n', '\n'),
                "assigned_to": m_assigned.group(1) if m_assigned else "",
            })
        return tasks


# ----------------------------------------------------------------------------
# Evidence gathering
# ----------------------------------------------------------------------------

@dataclass
class GitCommit:
    sha: str
    subject: str
    body: str

    @property
    def text(self) -> str:
        return f"{self.subject}\n{self.body}"


@dataclass
class InboxFile:
    path: Path
    mtime: dt.datetime
    preview: str


def git_recent(limit: int) -> list[GitCommit]:
    try:
        out = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%H%x1f%s%x1f%b%x1e"],
            cwd=ROOT, capture_output=True, text=True, check=True,
            encoding="utf-8", errors="replace",
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        sys.stderr.write(f"[task-sync] git log failed: {e}\n")
        return []
    commits = []
    for chunk in out.split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split("\x1f")
        if len(parts) < 3:
            continue
        commits.append(GitCommit(parts[0][:12], parts[1].strip(),
                                 parts[2].strip()))
    return commits


def inbox_recent(days: int) -> list[InboxFile]:
    if not INBOX_DIR.exists():
        return []
    cutoff = dt.datetime.now() - dt.timedelta(days=days)
    out: list[InboxFile] = []
    for p in sorted(INBOX_DIR.glob("*.md"),
                    key=lambda x: x.stat().st_mtime, reverse=True):
        mtime = dt.datetime.fromtimestamp(p.stat().st_mtime)
        if mtime < cutoff:
            continue
        try:
            preview = p.read_text(encoding="utf-8",
                                  errors="replace")[:INBOX_PREVIEW_CHARS]
        except OSError:
            preview = ""
        out.append(InboxFile(p, mtime, preview))
    return out


# ----------------------------------------------------------------------------
# Matching
# ----------------------------------------------------------------------------

def _tokens(text: str) -> set[str]:
    raw = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]{2,}", text.lower())
    return {t for t in raw if t not in STOPWORDS}


def score_overlap(task_tokens: set[str], signal_text: str) -> tuple[int, set[str]]:
    sig_tokens = _tokens(signal_text)
    common = task_tokens & sig_tokens
    return len(common), common


@dataclass
class Finding:
    task: dict
    confidence: str             # high / medium / low
    reasons: list[str] = field(default_factory=list)


def audit(tasks: list[dict], commits: list[GitCommit],
          inbox: list[InboxFile]) -> tuple[list[Finding], list[Finding]]:
    """Return (looks_done, status_uncertain)."""
    looks_done: list[Finding] = []
    uncertain: list[Finding] = []

    done_keywords = re.compile(
        r"\b(completed|done|delivered|shipped|fixed|landed)\b", re.I)

    for t in tasks:
        status = (t.get("status") or "").lower()
        if status not in OPEN_STATUSES:
            continue

        task_id = t.get("task_id", "")
        title = t.get("title", "")
        notes = t.get("notes", "") or ""
        task_tokens = _tokens(f"{task_id} {title}")
        if not task_tokens:
            continue

        reasons: list[str] = []
        score = 0

        # 1) Task ID literally appears in commits or inbox
        id_hits_commits = [c for c in commits
                           if task_id and task_id.lower() in c.text.lower()]
        id_hits_inbox = [f for f in inbox
                         if task_id and task_id.lower() in
                         (f.path.name.lower() + " " + f.preview.lower())]
        if id_hits_commits:
            score += 3
            reasons.append(
                f"task_id `{task_id}` found in {len(id_hits_commits)} commit(s): "
                + ", ".join(f"`{c.sha}` ({c.subject[:60]})"
                            for c in id_hits_commits[:3]))
        if id_hits_inbox:
            score += 3
            reasons.append(
                f"task_id `{task_id}` found in {len(id_hits_inbox)} inbox file(s): "
                + ", ".join(f.path.name for f in id_hits_inbox[:3]))

        # 2) Title keyword overlap with commits
        best_commit = None
        best_commit_score = 0
        best_commit_words: set[str] = set()
        for c in commits:
            s, words = score_overlap(task_tokens, c.text)
            if s > best_commit_score:
                best_commit_score, best_commit_words, best_commit = s, words, c
        if best_commit and best_commit_score >= 3:
            score += 2
            reasons.append(
                f"commit `{best_commit.sha}` matches {best_commit_score} "
                f"title keywords ({', '.join(sorted(best_commit_words))}): "
                f"\"{best_commit.subject[:80]}\"")
        elif best_commit and best_commit_score == 2:
            score += 1
            reasons.append(
                f"commit `{best_commit.sha}` weakly matches title "
                f"({', '.join(sorted(best_commit_words))}): "
                f"\"{best_commit.subject[:80]}\"")

        # 3) Title keyword overlap with inbox reports
        best_inbox = None
        best_inbox_score = 0
        best_inbox_words: set[str] = set()
        for f in inbox:
            s, words = score_overlap(
                task_tokens, f.path.name + " " + f.preview)
            if s > best_inbox_score:
                best_inbox_score, best_inbox_words, best_inbox = s, words, f
        if best_inbox and best_inbox_score >= 3:
            score += 2
            done_flag = (done_keywords.search(best_inbox.preview)
                         or "done" in best_inbox.path.name.lower())
            if done_flag:
                score += 1
            reasons.append(
                f"inbox file `{best_inbox.path.name}` matches "
                f"{best_inbox_score} keywords "
                f"({', '.join(sorted(best_inbox_words))})"
                + ("; contains 'done/completed' marker" if done_flag else ""))
        elif best_inbox and best_inbox_score == 2:
            score += 1
            reasons.append(
                f"inbox file `{best_inbox.path.name}` weakly matches title "
                f"({', '.join(sorted(best_inbox_words))})")

        # 4) Notes already say "COMPLETED" but status not "done"
        if re.search(r"\b(COMPLETED|DELIVERED|SHIPPED)\b\s+\d{4}-\d{2}-\d{2}",
                     notes):
            score += 4
            reasons.append("notes field contains a `COMPLETED YYYY-MM-DD` "
                           "marker but status is not `done`")

        if not reasons:
            continue

        if score >= 5:
            confidence = "high"
        elif score >= 3:
            confidence = "medium"
        else:
            confidence = "low"

        finding = Finding(task=t, confidence=confidence, reasons=reasons)
        if confidence in ("high", "medium"):
            looks_done.append(finding)
        else:
            uncertain.append(finding)

    looks_done.sort(key=lambda f: (
        {"high": 0, "medium": 1}[f.confidence], f.task.get("task_id", "")))
    uncertain.sort(key=lambda f: f.task.get("task_id", ""))
    return looks_done, uncertain


# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------

def render_report(today: dt.date, tasks: list[dict],
                  commits: list[GitCommit], inbox: list[InboxFile],
                  looks_done: list[Finding],
                  uncertain: list[Finding]) -> str:
    open_count = sum(1 for t in tasks
                     if (t.get("status") or "").lower() in OPEN_STATUSES)
    lines = [
        f"# Task Sync Audit — {today.isoformat()}",
        "",
        "_Auto-generated by `scripts/task_sync_scanner.py`. "
        "This report is read-only: no task statuses were modified._",
        "",
        "## Coverage",
        "",
        f"- Tasks scanned: **{len(tasks)}** "
        f"(open: **{open_count}**, signals checked only for open tasks)",
        f"- Git commits inspected: **{len(commits)}** (most recent first)",
        f"- Inbox files inspected: **{len(inbox)}** "
        f"(last {INBOX_RECENT_DAYS} days)",
        "",
        f"## Tasks that LOOK done (Andy should review and close): "
        f"**{len(looks_done)}**",
        "",
    ]

    if not looks_done:
        lines.append("_(none)_")
        lines.append("")
    else:
        for f in looks_done:
            t = f.task
            lines.append(
                f"### `{t.get('task_id')}` — {t.get('title', '(no title)')}")
            lines.append("")
            lines.append(f"- **Confidence:** {f.confidence}")
            lines.append(f"- **Status:** `{t.get('status')}` "
                         f"(assigned to {t.get('assigned_to', '?')})")
            lines.append("- **Evidence:**")
            for r in f.reasons:
                lines.append(f"  - {r}")
            lines.append("")

    lines.append(
        f"## Tasks where status MIGHT be wrong (weaker evidence): "
        f"**{len(uncertain)}**")
    lines.append("")
    if not uncertain:
        lines.append("_(none)_")
        lines.append("")
    else:
        for f in uncertain:
            t = f.task
            lines.append(
                f"- `{t.get('task_id')}` ({t.get('status')}): "
                f"{t.get('title', '')[:80]} — "
                + "; ".join(f.reasons[:2]))
        lines.append("")

    lines.append("## How to use this report")
    lines.append("")
    lines.append(
        "1. For each high/medium-confidence entry above, open the cited commit "
        "or inbox file and decide whether to mark `status: \"done\"`.")
    lines.append(
        "2. If the evidence is wrong (false positive), no action needed — the "
        "task stays as-is; the scanner will rescan tomorrow.")
    lines.append(
        "3. If you want to suppress a task from future scans, add "
        "`\"sync_audit_ignore\": true` to its JSON entry (the scanner reads "
        "but does not yet enforce this — wire it up if false positives pile up).")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Daily task sync audit")
    ap.add_argument("--stdout", action="store_true",
                    help="Print report to stdout; do not write a file.")
    args = ap.parse_args(argv)

    today = dt.date.today()
    tasks = load_tasks_tolerant(TASKS_FILE)
    if not tasks:
        sys.stderr.write("[task-sync] no tasks parsed; aborting\n")
        return 2

    commits = git_recent(GIT_LOG_LIMIT)
    inbox = inbox_recent(INBOX_RECENT_DAYS)
    looks_done, uncertain = audit(tasks, commits, inbox)
    report = render_report(today, tasks, commits, inbox, looks_done, uncertain)

    if args.stdout:
        sys.stdout.write(report)
        return 0

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    out_path = INBOX_DIR / f"task_sync_audit_{today.isoformat()}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"[task-sync] wrote {out_path}", file=sys.stderr)
    print(f"[task-sync] looks-done: {len(looks_done)}, "
          f"uncertain: {len(uncertain)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
