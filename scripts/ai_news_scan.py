#!/usr/bin/env python3
"""
ai_news_scan.py — Daily AI News Scanner

Scans blog/news/changelog pages of major LLM vendors and the Claude Code
plugin ecosystem, extracts the latest entries, and writes a dated digest to:

    owner_inbox/research/ai_news_daily.md

Behaviour:
  - Latest day on top (digest is rewritten each run)
  - Keeps last 7 daily blocks; older days are appended to:
        owner_inbox/research/ai_news_archive_YYYY-MM.md
  - One HTTP fetch per source per run (be polite)
  - Single-process, no threads; ~12s end-to-end on a normal link
  - Failures per source are logged inline ("[fetch failed]") — never abort
    the whole run

Run manually:
    python scripts/ai_news_scan.py
    python scripts/ai_news_scan.py --once          # no rotation/archive
    python scripts/ai_news_scan.py --dry-run       # print only
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DIR = ROOT / "owner_inbox" / "research"
DAILY_FILE = RESEARCH_DIR / "ai_news_daily.md"
KEEP_DAYS = 7  # number of daily blocks to keep in the live file
HTTP_TIMEOUT = 12  # seconds
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0 Safari/537.36 ai-news-scan/1.0"
)
MAX_ITEMS_PER_SOURCE = 5
MIN_SLEEP_BETWEEN_FETCHES = 0.8  # seconds

TIMEZONE_LABEL = "Asia/Jerusalem"


@dataclass
class Source:
    name: str          # display name
    group: str         # company / product bucket
    url: str           # page to scan
    # CSS-ish hints; we keep extraction simple/robust
    item_selector: str = "article, li, div"
    title_selector: str = "h1, h2, h3, h4"
    link_selector: str = "a"
    # If True, treat as a generic page — just dump page title + URL
    generic: bool = False


SOURCES: list[Source] = [
    # --- Anthropic / Claude ---
    Source("Anthropic — News", "Anthropic / Claude",
           "https://www.anthropic.com/news"),
    Source("Claude — Release Notes", "Anthropic / Claude",
           "https://www.anthropic.com/news",
           item_selector="article, li"),

    # --- OpenAI ---
    Source("OpenAI — News", "OpenAI / ChatGPT / Codex",
           "https://openai.com/news/"),
    Source("OpenAI — Research", "OpenAI / ChatGPT / Codex",
           "https://openai.com/research/"),

    # --- Google / Gemini ---
    Source("Google DeepMind — Blog", "Google / Gemini",
           "https://deepmind.google/discover/blog/"),
    Source("Google AI — Blog", "Google / Gemini",
           "https://blog.google/technology/ai/"),

    # --- xAI / Grok ---
    Source("xAI — News", "xAI / Grok",
           "https://x.ai/news"),

    # --- Perplexity ---
    Source("Perplexity — Changelog", "Perplexity",
           "https://www.perplexity.ai/hub/blog"),

    # --- OpenCog (best-effort interpretation of "OpenClaw") ---
    Source("OpenCog Foundation — Blog", "OpenCog (interpreted from 'OpenClaw')",
           "https://opencog.org/category/blog/", generic=True),

    # --- Other major LLM news ---
    Source("Mistral AI — News", "Other LLMs",
           "https://mistral.ai/news/"),
    Source("Meta AI — Blog", "Other LLMs",
           "https://ai.meta.com/blog/"),
    Source("Cohere — Blog", "Other LLMs",
           "https://cohere.com/blog"),

    # --- Claude Code plugin ecosystem ---
    Source("Claude Code — Docs Changelog", "Claude Code Ecosystem",
           "https://docs.claude.com/en/release-notes/claude-code"),
    Source("Anthropic — MCP Servers (GitHub releases)", "Claude Code Ecosystem",
           "https://github.com/modelcontextprotocol/servers/releases",
           generic=True),
    Source("MCP — Spec releases (GitHub)", "Claude Code Ecosystem",
           "https://github.com/modelcontextprotocol/specification/releases",
           generic=True),
]


# ----------------------------------------------------------------------------
# Fetch + parse
# ----------------------------------------------------------------------------

@dataclass
class Item:
    title: str
    link: str
    excerpt: str = ""


@dataclass
class SourceResult:
    source: Source
    items: list[Item] = field(default_factory=list)
    error: str | None = None


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def fetch(url: str) -> tuple[int, str]:
    """Return (status_code, html) or raise."""
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"}
    resp = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT,
                        allow_redirects=True)
    return resp.status_code, resp.text


def extract_items(html: str, src: Source) -> list[Item]:
    soup = BeautifulSoup(html, "html.parser")

    if src.generic:
        title = _clean(soup.title.string if soup.title else src.name)
        return [Item(title=title, link=src.url,
                     excerpt="(generic fetch — see link)")]

    items: list[Item] = []
    seen_links: set[str] = set()

    # Strategy: scan candidate containers, pull first heading + first link
    selectors = [s.strip() for s in src.item_selector.split(",")]
    candidates = []
    for sel in selectors:
        candidates.extend(soup.select(sel))

    for el in candidates:
        h = el.select_one(src.title_selector)
        a = el.select_one(src.link_selector)
        if not h or not a:
            continue
        title = _clean(h.get_text(" "))
        href = a.get("href", "").strip()
        if not title or not href:
            continue
        link = urljoin(src.url, href)
        # Filter junk (nav links, anchors, login, social)
        if link in seen_links:
            continue
        if any(bad in link.lower() for bad in (
                "javascript:", "mailto:", "#", "/login", "/signin",
                "twitter.com/intent", "facebook.com/share",
        )) and link == href:
            continue
        if len(title) < 6:
            continue
        seen_links.add(link)
        # Excerpt: first paragraph-ish text in the same container
        p = el.find("p")
        excerpt = _clean(p.get_text(" "))[:240] if p else ""
        items.append(Item(title=title, link=link, excerpt=excerpt))
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break

    # Fallback: if nothing matched, give a generic page-title link
    if not items:
        title = _clean(soup.title.string if soup.title else src.name)
        items = [Item(title=title, link=src.url,
                      excerpt="(no items parsed — link only)")]
    return items


def scan_source(src: Source) -> SourceResult:
    try:
        code, html = fetch(src.url)
        if code >= 400:
            return SourceResult(src, error=f"HTTP {code}")
        items = extract_items(html, src)
        return SourceResult(src, items=items)
    except requests.RequestException as e:
        return SourceResult(src, error=f"request error: {e.__class__.__name__}")
    except Exception as e:  # pragma: no cover — defensive
        return SourceResult(src, error=f"parse error: {e.__class__.__name__}: {e}")


def scan_all(sources: Iterable[Source]) -> list[SourceResult]:
    out: list[SourceResult] = []
    for s in sources:
        out.append(scan_source(s))
        time.sleep(MIN_SLEEP_BETWEEN_FETCHES)
    return out


# ----------------------------------------------------------------------------
# Render + rotate
# ----------------------------------------------------------------------------

def render_day_block(results: list[SourceResult], today: dt.date) -> str:
    by_group: dict[str, list[SourceResult]] = {}
    for r in results:
        by_group.setdefault(r.source.group, []).append(r)

    lines: list[str] = []
    lines.append(f"## {today.isoformat()} ({TIMEZONE_LABEL})")
    lines.append("")
    ok = sum(1 for r in results if not r.error)
    lines.append(f"_Sources scanned: {len(results)} — succeeded: {ok}, "
                 f"failed: {len(results) - ok}_")
    lines.append("")

    for group in sorted(by_group.keys()):
        lines.append(f"### {group}")
        lines.append("")
        for r in by_group[group]:
            if r.error:
                lines.append(f"- **{r.source.name}** — [fetch failed: {r.error}]"
                             f"({r.source.url})")
                continue
            lines.append(f"- **{r.source.name}** ({r.source.url})")
            for it in r.items:
                if it.excerpt:
                    lines.append(f"  - [{it.title}]({it.link}) — {it.excerpt}")
                else:
                    lines.append(f"  - [{it.title}]({it.link})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


HEADER = (
    "# AI News — Daily Digest\n\n"
    "Auto-generated by `scripts/ai_news_scan.py`. Latest day on top; "
    f"only the last {KEEP_DAYS} days are kept here. Older days move to "
    "`ai_news_archive_YYYY-MM.md`.\n\n"
    "---\n\n"
)


def split_existing(text: str) -> list[tuple[str, str]]:
    """Return list of (date_str, full_block) from an existing daily file."""
    if not text.strip():
        return []
    # Strip header (everything up to and including first '---' separator)
    body = text
    if "---\n" in body:
        body = body.split("---\n", 1)[1]
    # Split on day headings (## YYYY-MM-DD ...)
    parts = re.split(r"(?m)^(?=##\s+\d{4}-\d{2}-\d{2})", body)
    out: list[tuple[str, str]] = []
    for p in parts:
        m = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})", p.strip())
        if not m:
            continue
        out.append((m.group(1), p.strip() + "\n"))
    return out


def rotate_and_write(today_block: str, today: dt.date, *, archive: bool) -> None:
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    existing = ""
    if DAILY_FILE.exists():
        existing = DAILY_FILE.read_text(encoding="utf-8")

    blocks = split_existing(existing)
    # Remove today's date if present (we replace it)
    blocks = [(d, b) for (d, b) in blocks if d != today.isoformat()]

    # Newest first: today + previous blocks (already in file order, newest first)
    blocks_sorted = sorted(blocks, key=lambda x: x[0], reverse=True)
    keep = blocks_sorted[: KEEP_DAYS - 1]
    drop = blocks_sorted[KEEP_DAYS - 1:]

    # Archive dropped blocks
    if archive and drop:
        for date_str, block in drop:
            month_key = date_str[:7]
            arch = RESEARCH_DIR / f"ai_news_archive_{month_key}.md"
            prev = arch.read_text(encoding="utf-8") if arch.exists() else (
                f"# AI News — Archive {month_key}\n\n"
            )
            # Avoid duplicates if the same date is somehow already archived
            if f"## {date_str}" in prev:
                continue
            arch.write_text(prev + "\n" + block, encoding="utf-8")

    final = HEADER + today_block + "\n" + "\n".join(b for _, b in keep)
    DAILY_FILE.write_text(final.rstrip() + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Daily AI news scanner")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the day's block to stdout; do not write files.")
    ap.add_argument("--once", action="store_true",
                    help="Write daily file but skip rotation/archiving.")
    args = ap.parse_args(argv)

    today = dt.date.today()
    print(f"[ai-news-scan] {today.isoformat()} — scanning {len(SOURCES)} sources",
          file=sys.stderr)
    results = scan_all(SOURCES)

    ok = sum(1 for r in results if not r.error)
    print(f"[ai-news-scan] done — {ok}/{len(results)} succeeded",
          file=sys.stderr)

    block = render_day_block(results, today)

    if args.dry_run:
        sys.stdout.write(block)
        return 0

    rotate_and_write(block, today, archive=not args.once)
    print(f"[ai-news-scan] wrote {DAILY_FILE}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
