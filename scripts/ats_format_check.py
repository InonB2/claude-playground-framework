#!/usr/bin/env python3
"""
ATS Format Checker — JOBSEARCH-008
Author: Jasmin (Security & Logic Auditor)

Scans an HTML CV and verifies it is ATS-friendly per Video 3 — ATS Reality
research (98% of Fortune 500 use ATS; format kills resumes before humans see them).

Checks:
  1. No tables           (FAIL on <table>)
  2. No images           (FAIL on <img> or CSS background-image)
  3. No columns          (FAIL on CSS column-count/columns; WARN on body flex/grid columns)
  4. No headers/footers  (WARN — many CVs use these for visual sectioning)
  5. Standard fonts only (FAIL on non-standard font-family)
  6. Date format consistency (WARN on mixed formats)

Usage:
  python scripts/ats_format_check.py <path-to-cv.html>

Exit codes:
  0 — PASS  (any combination of pass + warnings)
  1 — FAIL  (one or more hard-fail checks failed)
  2 — Usage / file error
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup, Comment
except ImportError:
    print("ERROR: beautifulsoup4 not installed. Run: pip install beautifulsoup4")
    sys.exit(2)


# ----- Config ---------------------------------------------------------------

STANDARD_FONTS = {
    "arial",
    "calibri",
    "cambria",
    "garamond",
    "georgia",
    "helvetica",
    "lato",
    "open sans",
    "tahoma",
    "times new roman",
    "trebuchet ms",
    "verdana",
}

# Generic CSS fallbacks always allowed
GENERIC_FONTS = {
    "serif",
    "sans-serif",
    "monospace",
    "cursive",
    "fantasy",
    "system-ui",
    "-apple-system",
    "blinkmacsystemfont",
    "ui-sans-serif",
    "ui-serif",
    "ui-monospace",
    "inherit",
    "initial",
    "unset",
}

# Common short month names + long
MONTH_RE = (
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|"
    r"January|February|March|April|June|July|August|September|October|November|December)"
)

DATE_PATTERNS = {
    # "Jan 2020", "January 2020"
    "Month YYYY": re.compile(rf"\b{MONTH_RE}\.?\s+\d{{4}}\b", re.IGNORECASE),
    # "01/2020", "1/2020"
    "MM/YYYY": re.compile(r"\b(0?[1-9]|1[0-2])/(19|20)\d{2}\b"),
    # "2020-01"  -- requires explicit YYYY 4-digit year followed by month
    "YYYY-MM": re.compile(r"\b(19|20)\d{2}-(0[1-9]|1[0-2])\b"),
    # "01-15-2020" full date
    "MM-DD-YYYY": re.compile(r"\b(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01])-(19|20)\d{2}\b"),
    "DD/MM/YYYY": re.compile(r"\b(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[0-2])/(19|20)\d{2}\b"),
    # Year-only ranges: "2018 – 2024", "2018-2024", "2018 — Present", "2024 – Present"
    "YYYY range": re.compile(
        r"\b(19|20)\d{2}\s*[-–—]\s*((19|20)\d{2}|Present|present|Current|current)\b"
    ),
}


# ----- Result types ---------------------------------------------------------

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"


class CheckResult:
    def __init__(self, name: str, status: str, message: str, details: list[str] | None = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or []

    def is_fail(self) -> bool:
        return self.status == FAIL


# ----- Helpers --------------------------------------------------------------

def collect_css(soup: BeautifulSoup, inline_styles: list[str]) -> str:
    """Combine all <style> blocks and inline style attributes into one string."""
    chunks: list[str] = []
    for style_tag in soup.find_all("style"):
        if style_tag.string:
            chunks.append(style_tag.string)
    chunks.extend(inline_styles)
    return "\n".join(chunks)


def get_inline_styles(soup: BeautifulSoup) -> list[str]:
    return [tag.get("style", "") for tag in soup.find_all(style=True)]


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


# ----- Checks ---------------------------------------------------------------

def check_no_tables(soup: BeautifulSoup) -> CheckResult:
    tables = soup.find_all("table")
    if tables:
        return CheckResult(
            "1. No tables",
            FAIL,
            f"Found {len(tables)} <table> element(s). ATS parsers commonly garble table cells.",
            [f"<table> at position {i+1}" for i in range(len(tables))],
        )
    return CheckResult("1. No tables", PASS, "No <table> elements found.")


def check_no_images(soup: BeautifulSoup, css: str) -> CheckResult:
    imgs = soup.find_all("img")
    # CSS background-image (ignore "background-image: none")
    bg_re = re.compile(r"background-image\s*:\s*(?!none\b)([^;}\n]+)", re.IGNORECASE)
    bg_matches = bg_re.findall(strip_comments(css))

    failures: list[str] = []
    if imgs:
        failures.append(f"{len(imgs)} <img> tag(s)")
    if bg_matches:
        failures.append(f"{len(bg_matches)} CSS background-image rule(s)")

    if failures:
        details = [f"<img src={img.get('src','?')!r}>" for img in imgs[:5]]
        details += [f"background-image: {m.strip()}" for m in bg_matches[:5]]
        return CheckResult(
            "2. No images",
            FAIL,
            "Images break ATS parsing — found: " + "; ".join(failures),
            details,
        )
    return CheckResult("2. No images", PASS, "No <img> tags or CSS background images.")


def check_no_columns(soup: BeautifulSoup, css: str) -> CheckResult:
    css_clean = strip_comments(css)

    # Hard fail: column-count / columns / column-width multi-col layout
    hard_re = re.compile(
        r"(?:^|[\s;{])(column-count|columns|column-width)\s*:\s*([^;}\n]+)",
        re.IGNORECASE | re.MULTILINE,
    )
    hard_hits = [(m.group(1), m.group(2).strip()) for m in hard_re.finditer(css_clean)]
    # Filter out "columns: auto" or "column-count: 1" which aren't multi-column
    real_hard = []
    for prop, val in hard_hits:
        v = val.lower().strip()
        if prop.lower() == "column-count" and v in ("1", "auto"):
            continue
        if prop.lower() == "columns" and (v.startswith("1 ") or v == "1" or v == "auto"):
            continue
        real_hard.append((prop, val))

    if real_hard:
        details = [f"{p}: {v}" for p, v in real_hard]
        return CheckResult(
            "3. No columns",
            FAIL,
            f"Found {len(real_hard)} CSS multi-column rule(s) — body text in columns breaks ATS reading order.",
            details,
        )

    # Soft warn: flex/grid used outside of the header area
    # Look for body-level rules with display:flex or display:grid in classes that aren't header/contact
    warn_hits = []
    flex_grid_re = re.compile(
        r"\.([\w-]+)\s*\{[^}]*display\s*:\s*(flex|grid)[^}]*\}",
        re.IGNORECASE,
    )
    for m in flex_grid_re.finditer(css_clean):
        cls = m.group(1).lower()
        if any(safe in cls for safe in ("header", "contact", "title", "top", "nav", "footer", "name")):
            continue
        # job-header is typically just title/date alignment — safe
        if "job-header" in cls or "section-title" in cls or "row" in cls:
            continue
        warn_hits.append(f".{m.group(1)} uses display:{m.group(2)}")

    if warn_hits:
        return CheckResult(
            "3. No columns",
            WARN,
            f"Flex/grid layouts found in {len(warn_hits)} non-header class(es). "
            "Confirm body content (not just headers/badges) does not flow side-by-side.",
            warn_hits[:8],
        )
    return CheckResult("3. No columns", PASS, "No CSS multi-column rules; flex/grid usage confined to safe header/title classes.")


def check_no_header_footer(soup: BeautifulSoup) -> CheckResult:
    # We look inside <body> specifically — semantic <header>/<footer> are ATS-risky
    body = soup.body or soup
    headers = body.find_all("header")
    footers = body.find_all("footer")
    if not headers and not footers:
        return CheckResult(
            "4. No headers/footers",
            PASS,
            "No semantic <header>/<footer> elements in body.",
        )
    parts = []
    if headers:
        parts.append(f"{len(headers)} <header>")
    if footers:
        parts.append(f"{len(footers)} <footer>")
    return CheckResult(
        "4. No headers/footers",
        WARN,
        f"Found {' and '.join(parts)} element(s). Many CVs use these for visual layout; "
        "some ATS systems ignore content inside semantic header/footer tags. "
        "Verify contact info / sections inside are also reachable elsewhere, or rename to <div>.",
        [f"<header>" for _ in headers] + [f"<footer>" for _ in footers],
    )


def _extract_fonts(value: str) -> list[str]:
    # font-family value may be a comma list: "Arial, Helvetica, sans-serif"
    raw = [f.strip().strip("'").strip('"').lower() for f in value.split(",")]
    return [f for f in raw if f]


def check_standard_fonts(css: str, soup: BeautifulSoup) -> CheckResult:
    css_clean = strip_comments(css)
    font_re = re.compile(r"font-family\s*:\s*([^;}\n]+)", re.IGNORECASE)
    seen: set[str] = set()
    bad: set[str] = set()
    for m in font_re.finditer(css_clean):
        for fam in _extract_fonts(m.group(1)):
            seen.add(fam)
            if fam in STANDARD_FONTS:
                continue
            if fam in GENERIC_FONTS:
                continue
            bad.add(fam)

    if bad:
        return CheckResult(
            "5. Standard fonts only",
            FAIL,
            f"Found {len(bad)} non-standard font(s). ATS parsers can substitute or drop unrecognized fonts.",
            sorted(bad),
        )
    if not seen:
        return CheckResult(
            "5. Standard fonts only",
            WARN,
            "No font-family rule found — browser default will be used. Consider specifying Arial/Calibri.",
        )
    return CheckResult(
        "5. Standard fonts only",
        PASS,
        f"All {len(seen)} font(s) are ATS-standard or generic fallbacks.",
        sorted(seen),
    )


def check_date_consistency(soup: BeautifulSoup) -> CheckResult:
    # Walk visible text only (skip script/style/comments)
    for s in soup(["script", "style"]):
        s.extract()
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    text = " ".join(soup.stripped_strings) if soup.body else " ".join(soup.stripped_strings)

    found: dict[str, list[str]] = {}
    for label, rgx in DATE_PATTERNS.items():
        hits = rgx.findall(text) if rgx.groups == 0 else [m.group(0) for m in rgx.finditer(text)]
        # findall on grouped patterns returns tuples — re-run with finditer to get full match strings
        hits = [m.group(0) for m in rgx.finditer(text)]
        if hits:
            found[label] = hits

    if len(found) <= 1:
        if found:
            (label, hits) = next(iter(found.items()))
            return CheckResult(
                "6. Date format consistency",
                PASS,
                f"All {len(hits)} date(s) use one consistent format: {label}.",
                hits[:8],
            )
        return CheckResult(
            "6. Date format consistency",
            WARN,
            "No standard date patterns detected. Verify dates are present and machine-readable.",
        )

    summary = ", ".join(f"{k} ({len(v)})" for k, v in found.items())
    details = []
    for label, hits in found.items():
        details.append(f"{label}: {', '.join(sorted(set(hits))[:6])}")
    return CheckResult(
        "6. Date format consistency",
        WARN,
        f"Mixed date formats detected: {summary}. ATS scoring can be inconsistent across formats.",
        details,
    )


# ----- Runner ---------------------------------------------------------------

def run_checks(html_path: Path) -> tuple[list[CheckResult], str]:
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    inline_styles = get_inline_styles(soup)
    css = collect_css(soup, inline_styles)

    results = [
        check_no_tables(soup),
        check_no_images(soup, css),
        check_no_columns(soup, css),
        check_no_header_footer(soup),
        check_standard_fonts(css, soup),
        # date check mutates soup — run last
        check_date_consistency(soup),
    ]

    verdict = FAIL if any(r.is_fail() for r in results) else PASS
    return results, verdict


def render_report(path: Path, results: list[CheckResult], verdict: str) -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append(f"ATS Format Check — {path.name}")
    lines.append(f"Path: {path}")
    lines.append("=" * 72)
    lines.append("")

    icon = {PASS: "[PASS]", FAIL: "[FAIL]", WARN: "[WARN]"}
    for r in results:
        lines.append(f"{icon[r.status]:6}  {r.name}")
        lines.append(f"         {r.message}")
        for d in r.details[:8]:
            lines.append(f"           - {d}")
        if len(r.details) > 8:
            lines.append(f"           ... (+{len(r.details)-8} more)")
        lines.append("")

    n_pass = sum(1 for r in results if r.status == PASS)
    n_warn = sum(1 for r in results if r.status == WARN)
    n_fail = sum(1 for r in results if r.status == FAIL)

    lines.append("-" * 72)
    lines.append(f"Summary: {n_pass} pass, {n_warn} warn, {n_fail} fail")
    lines.append(f"FINAL VERDICT: {verdict}")
    lines.append("-" * 72)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 2
    if not path.is_file():
        print(f"ERROR: not a file: {path}")
        return 2

    results, verdict = run_checks(path)
    print(render_report(path, results, verdict))
    return 0 if verdict == PASS else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
