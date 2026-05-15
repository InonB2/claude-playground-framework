#!/usr/bin/env python3
"""
job_url_parser.py — JOBSEARCH-010 — Job URL auto-parser (Mack)

Fetches a job-posting URL server-side and extracts structured fields
(title, company, location, JD text) as clean JSON for the dashboard's
"Import Job" feature (Mode A — paste JSON).

WHY A CLI AND NOT BROWSER JS:
  The dashboard is a static HTML file with no backend. Client-side JS
  cannot fetch LinkedIn/Indeed/Glassdoor pages — CORS blocks cross-origin
  fetches and these boards actively block scrapers. So the network fetch
  has to happen here, server-side, where there is no CORS and we can set
  a real User-Agent. The dashboard then consumes the JSON this prints.

USAGE:
  python scripts/job_url_parser.py "<job-url>"
  python scripts/job_url_parser.py --file saved_page.html --url "<original-url>"
  python scripts/job_url_parser.py --selftest

OUTPUT (stdout, always JSON):
  success:  {"title","company","location","jd","url","source"}
  failure:  {"error": "...", "hint": "...", "url": "...", "source": "..."}

DEPENDENCIES: requests, beautifulsoup4  (pip install requests beautifulsoup4)

EXTRACTION STRATEGY (in priority order):
  1. JSON-LD <script type="application/ld+json"> with @type JobPosting —
     the most reliable path; many boards (Glassdoor, Indeed, most
     Greenhouse/Lever/Workday-backed boards, Google-indexed postings)
     embed it because Google for Jobs requires it.
  2. Per-board HTML selectors — fallback when no JSON-LD.
  3. Generic <meta>/<title>/<h1> heuristics — last resort.

EXIT CODE: 0 on a successful parse, 1 on a graceful error (JSON still
printed either way so the caller never has to parse stderr).
"""

import sys
import json
import re
import argparse
import html as _html

# Windows consoles default stdout to cp1252, which corrupts the UTF-8 JSON
# we emit (em-dashes, smart quotes, accented names → mojibake / 0x96 bytes)
# the moment the output is piped or redirected. Force UTF-8 so the JSON the
# dashboard consumes is always clean, on every platform.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):  # pragma: no cover - very old Python
    pass

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:  # pragma: no cover - environment guard
    print(json.dumps({
        "error": f"Missing dependency: {e.name}",
        "hint": "Run: pip install requests beautifulsoup4",
        "url": "",
        "source": "none",
    }))
    sys.exit(1)


# A real desktop UA — boards 403 the python-requests default UA instantly.
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 12  # seconds — well under the dashboard's 5s target for cached/fast
              # boards; slow boards still bounded so the CLI never hangs.


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def _clean(text):
    """Collapse whitespace, unescape HTML entities, strip. Returns ''."""
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = _html.unescape(text)
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\n[ \t]*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _jd_from_html(raw_html):
    """Strip an HTML fragment (a JD body) down to readable plain text."""
    if not raw_html:
        return ""
    frag = BeautifulSoup(raw_html, "html.parser")
    for bad in frag(["script", "style"]):
        bad.decompose()
    # <br> and block elements → newlines so the JD keeps its shape.
    for br in frag.find_all("br"):
        br.replace_with("\n")
    for block in frag.find_all(["p", "li", "div", "h1", "h2", "h3", "h4"]):
        block.append("\n")
    return _clean(frag.get_text())


def detect_source(url):
    u = (url or "").lower()
    if "linkedin.com" in u:
        return "linkedin"
    if "indeed.com" in u:
        return "indeed"
    if "glassdoor." in u:
        return "glassdoor"
    if "google.com" in u and ("jobs" in u or "ibp" in u):
        return "google"
    return "generic"


def fetch(url):
    """Fetch a URL server-side. Raises requests exceptions on failure."""
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                        allow_redirects=True)
    resp.raise_for_status()
    # requests guesses latin-1 when a page omits a charset header, which
    # mangles UTF-8 smart-quotes/em-dashes into mojibake (e.g. "world's"
    # → "world?s"). Prefer the apparent (sniffed) encoding, then let
    # BeautifulSoup re-decode from the raw bytes for maximum fidelity.
    if resp.encoding is None or resp.encoding.lower() in ("iso-8859-1",
                                                          "latin-1"):
        resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.content.decode(resp.encoding, errors="replace")


# ──────────────────────────────────────────────────────────────────────
# Extraction layer 1 — JSON-LD JobPosting schema (most reliable)
# ──────────────────────────────────────────────────────────────────────

def _iter_jsonld_objects(soup):
    """Yield every dict found in any <script type=application/ld+json>,
    flattening @graph arrays and bare lists."""
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text() or ""
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            # Some boards emit slightly broken JSON-LD — try a lenient
            # cleanup of trailing commas / control chars before giving up.
            cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
            cleaned = re.sub(r"[\x00-\x1f]", " ", cleaned)
            try:
                data = json.loads(cleaned)
            except (ValueError, TypeError):
                continue
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, dict):
                if "@graph" in item and isinstance(item["@graph"], list):
                    stack.extend(item["@graph"])
                yield item


def _jsonld_type_is_jobposting(obj):
    t = obj.get("@type", "")
    if isinstance(t, list):
        return any(str(x).lower() == "jobposting" for x in t)
    return str(t).lower() == "jobposting"


def extract_jsonld(soup, url, source):
    """Return a result dict from a JobPosting JSON-LD object, or None."""
    for obj in _iter_jsonld_objects(soup):
        if not _jsonld_type_is_jobposting(obj):
            continue

        title = _clean(obj.get("title"))

        # company — hiringOrganization can be a dict or a bare string.
        org = obj.get("hiringOrganization")
        company = ""
        if isinstance(org, dict):
            company = _clean(org.get("name"))
        elif isinstance(org, str):
            company = _clean(org)

        # location — jobLocation can be a dict, a list of dicts, or a string.
        location = _extract_jsonld_location(obj.get("jobLocation"))
        if not location and obj.get("applicantLocationRequirements"):
            location = _extract_jsonld_location(
                obj.get("applicantLocationRequirements"))
        if not location and obj.get("jobLocationType"):
            # e.g. "TELECOMMUTE"
            jlt = str(obj.get("jobLocationType"))
            location = "Remote" if "tele" in jlt.lower() else _clean(jlt)

        # description is HTML — strip it to plain text.
        jd = _jd_from_html(obj.get("description"))

        if title or company or jd:
            return {
                "title": title,
                "company": company,
                "location": location,
                "jd": jd,
                "url": url,
                "source": source,
                "_method": "json-ld",
            }
    return None


def _extract_jsonld_location(loc):
    if not loc:
        return ""
    if isinstance(loc, list):
        parts = [_extract_jsonld_location(x) for x in loc]
        parts = [p for p in parts if p]
        return "; ".join(dict.fromkeys(parts))  # dedupe, keep order
    if isinstance(loc, str):
        return _clean(loc)
    if isinstance(loc, dict):
        # Place → address → PostalAddress
        addr = loc.get("address", loc)
        if isinstance(addr, str):
            return _clean(addr)
        if isinstance(addr, dict):
            bits = [
                addr.get("addressLocality"),
                addr.get("addressRegion"),
                addr.get("addressCountry"),
            ]
            bits = [_clean(b if not isinstance(b, dict)
                           else b.get("name")) for b in bits]
            bits = [b for b in bits if b]
            return ", ".join(bits)
        if loc.get("name"):
            return _clean(loc.get("name"))
    return ""


# ──────────────────────────────────────────────────────────────────────
# Extraction layer 2 — per-board HTML selectors (fallback)
# ──────────────────────────────────────────────────────────────────────

def _first_text(soup, selectors):
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            txt = _clean(el.get_text())
            if txt:
                return txt
    return ""


def _meta(soup, *names):
    for name in names:
        el = (soup.find("meta", attrs={"property": name})
              or soup.find("meta", attrs={"name": name}))
        if el and el.get("content"):
            txt = _clean(el["content"])
            if txt:
                return txt
    return ""


def extract_linkedin(soup, url):
    title = (_first_text(soup, [
        "h1.top-card-layout__title",
        "h1.topcard__title",
        ".top-card-layout__title",
        "h1",
    ]) or _meta(soup, "og:title"))
    company = _first_text(soup, [
        "a.topcard__org-name-link",
        ".topcard__org-name-link",
        ".top-card-layout__card .topcard__flavor",
        "span.topcard__flavor",
    ])
    location = _first_text(soup, [
        ".topcard__flavor--bullet",
        ".top-card-layout__second-subline .topcard__flavor--bullet",
    ])
    jd = (_first_text(soup, [
        ".description__text",
        ".show-more-less-html__markup",
        "section.description",
    ]))
    return title, company, location, jd


def extract_indeed(soup, url):
    title = (_first_text(soup, [
        "h1.jobsearch-JobInfoHeader-title",
        ".jobsearch-JobInfoHeader-title",
        'h1[data-testid="jobsearch-JobInfoHeader-title"]',
        "h1",
    ]) or _meta(soup, "og:title"))
    company = _first_text(soup, [
        '[data-testid="inlineHeader-companyName"]',
        '[data-company-name="true"]',
        ".jobsearch-CompanyInfoContainer a",
        ".jobsearch-InlineCompanyRating div",
    ])
    location = _first_text(soup, [
        '[data-testid="inlineHeader-companyLocation"]',
        '[data-testid="job-location"]',
        ".jobsearch-JobInfoHeader-subtitle div",
    ])
    jd = _first_text(soup, [
        "#jobDescriptionText",
        ".jobsearch-JobComponent-description",
    ])
    return title, company, location, jd


def extract_glassdoor(soup, url):
    title = (_first_text(soup, [
        '[data-test="job-title"]',
        "h1",
    ]) or _meta(soup, "og:title"))
    company = _first_text(soup, [
        '[data-test="employer-name"]',
        ".EmployerProfile_employerName__9MGcV",
        '[data-test="employerName"]',
    ])
    location = _first_text(soup, [
        '[data-test="location"]',
        '[data-test="emp-location"]',
    ])
    jd = _first_text(soup, [
        ".JobDetails_jobDescription__uW_fK",
        "#JobDescriptionContainer",
        '[class*="jobDescription"]',
    ])
    return title, company, location, jd


def extract_google(soup, url):
    # Google for Jobs is an SPA; a raw server fetch rarely yields the
    # posting body. JSON-LD is the only reliable path and is tried first
    # upstream. This selector pass is a thin best-effort.
    title = _meta(soup, "og:title") or _first_text(soup, ["h1"])
    company = ""
    location = ""
    jd = _meta(soup, "og:description", "description")
    return title, company, location, jd


BOARD_EXTRACTORS = {
    "linkedin": extract_linkedin,
    "indeed": extract_indeed,
    "glassdoor": extract_glassdoor,
    "google": extract_google,
}


# ──────────────────────────────────────────────────────────────────────
# Extraction layer 3 — generic heuristics (last resort)
# ──────────────────────────────────────────────────────────────────────

def extract_generic(soup, url):
    title = _meta(soup, "og:title", "twitter:title")
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = _clean(h1.get_text())
    if not title and soup.title:
        title = _clean(soup.title.get_text())

    company = _meta(soup, "og:site_name")

    # JD: prefer the longest <article> / main / role=main / large <div>.
    jd = ""
    candidates = soup.select(
        "article, main, [role=main], .job-description, "
        "[class*=description], [class*=job-detail], [id*=description]")
    best = ""
    for el in candidates:
        for bad in el(["script", "style", "nav", "header", "footer"]):
            bad.decompose()
        txt = _clean(el.get_text())
        if len(txt) > len(best):
            best = txt
    jd = best
    if not jd:
        jd = _meta(soup, "og:description", "description")

    location = ""
    return title, company, location, jd


# ──────────────────────────────────────────────────────────────────────
# Orchestration
# ──────────────────────────────────────────────────────────────────────

def parse_html(raw_html, url):
    """Parse already-fetched HTML. Returns a result dict (success or error)."""
    source = detect_source(url)
    soup = BeautifulSoup(raw_html, "html.parser")

    # Layer 1 — JSON-LD JobPosting (board-agnostic, most reliable).
    result = extract_jsonld(soup, url, source)
    if result and result.get("title") and result.get("jd"):
        result.pop("_method", None)
        result["source"] = source
        return result

    # Layer 2 — per-board selectors.
    partial = result or {}
    extractor = BOARD_EXTRACTORS.get(source)
    if extractor:
        t, c, l, j = extractor(soup, url)
        title = partial.get("title") or t
        company = partial.get("company") or c
        location = partial.get("location") or l
        jd = partial.get("jd") or j
    else:
        title = partial.get("title", "")
        company = partial.get("company", "")
        location = partial.get("location", "")
        jd = partial.get("jd", "")

    # Layer 3 — generic heuristics fill any remaining gaps.
    if not (title and jd):
        gt, gc, gl, gj = extract_generic(soup, url)
        title = title or gt
        company = company or gc
        location = location or gl
        jd = jd or gj

    title = _clean(title)
    company = _clean(company)
    location = _clean(location)
    jd = _clean(jd)

    # LinkedIn/Indeed often serve an auth-wall / "verify you're human" page
    # to server-side fetches. Detect that so we return a useful hint instead
    # of a garbage "title".
    blockish = re.search(
        r"(sign in|join linkedin|verify (you'?re|you are) human|"
        r"unusual traffic|are you a robot|enable javascript|"
        r"access to this page has been denied)",
        raw_html.lower())
    if not title and not jd:
        hint = _block_hint(source) if blockish else (
            "Could not find a job title or description on the page. "
            "The board may render content with JavaScript. Use the "
            "paste-text fallback (Mode B) in the dashboard.")
        return {
            "error": "No job data found in page",
            "hint": hint,
            "url": url,
            "source": source,
        }
    if blockish and not jd:
        # Got a title but the body looks like a wall — warn but still return.
        return {
            "title": title,
            "company": company,
            "location": location,
            "jd": jd,
            "url": url,
            "source": source,
            "warning": _block_hint(source),
        }

    return {
        "title": title,
        "company": company,
        "location": location,
        "jd": jd,
        "url": url,
        "source": source,
    }


def _block_hint(source):
    nice = {
        "linkedin": "LinkedIn",
        "indeed": "Indeed",
        "glassdoor": "Glassdoor",
        "google": "Google Jobs",
    }.get(source, "This board")
    return (f"{nice} blocked the server-side fetch (anti-scraping / "
            f"auth wall). Open the posting in your browser, select all "
            f"the job text, copy it, and use the paste-text fallback "
            f"(Mode B) in the dashboard's Import Job panel — that always "
            f"works because it never touches the network.")


def parse_url(url):
    """Fetch + parse a live URL. Returns a result dict (success or error)."""
    if not url or not re.match(r"^https?://", url, re.I):
        return {
            "error": "Invalid URL",
            "hint": "Pass a full http(s):// job-posting URL in quotes.",
            "url": url or "",
            "source": "none",
        }
    source = detect_source(url)
    try:
        raw = fetch(url)
    except requests.exceptions.Timeout:
        return {
            "error": "Request timed out",
            "hint": (f"{source} did not respond within {TIMEOUT}s. Try "
                     f"again, or use the paste-text fallback (Mode B)."),
            "url": url,
            "source": source,
        }
    except requests.exceptions.HTTPError as e:
        code = getattr(e.response, "status_code", "?")
        return {
            "error": f"HTTP {code} from {source}",
            "hint": _block_hint(source) if str(code) in ("403", "429", "999")
                    else (f"The page returned HTTP {code}. Check the URL is "
                          f"a live public posting, or use Mode B."),
            "url": url,
            "source": source,
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Network error: {type(e).__name__}",
            "hint": ("Could not reach the page. Check your connection and "
                     "the URL, or use the paste-text fallback (Mode B)."),
            "url": url,
            "source": source,
        }
    return parse_html(raw, url)


# ──────────────────────────────────────────────────────────────────────
# Self-test — runs the JSON-LD extractor against an inline fixture so the
# success criteria can be verified even when every live board blocks us.
# ──────────────────────────────────────────────────────────────────────

_FIXTURE = """<!doctype html><html><head><title>Senior Product Manager - Acme</title>
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "JobPosting",
  "title": "Senior Product Manager",
  "hiringOrganization": { "@type": "Organization", "name": "Acme Corp" },
  "jobLocation": { "@type": "Place", "address": {
      "@type": "PostalAddress", "addressLocality": "Tel Aviv",
      "addressRegion": "TA", "addressCountry": "IL" } },
  "description": "<p>We are hiring a <b>Senior Product Manager</b>.</p><ul><li>5+ years PM experience</li><li>Lead cross-functional teams</li></ul><p>Nice to have: data analysis.</p>"
}
</script></head><body><h1>Senior Product Manager</h1></body></html>"""


def _selftest():
    print("Running job_url_parser self-test (JSON-LD fixture)...\n")
    res = parse_html(_FIXTURE, "https://example.com/jobs/senior-pm")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    ok = (res.get("title") == "Senior Product Manager"
          and res.get("company") == "Acme Corp"
          and "Tel Aviv" in res.get("location", "")
          and "5+ years PM experience" in res.get("jd", "")
          and "<" not in res.get("jd", ""))
    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Parse a job-posting URL into structured JSON.")
    ap.add_argument("url", nargs="?", help="Job posting URL (http/https).")
    ap.add_argument("--file", help="Parse a saved HTML file instead of "
                                   "fetching (offline / fixture testing).")
    ap.add_argument("--selftest", action="store_true",
                    help="Run the built-in JSON-LD extraction self-test.")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(_selftest())

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8", errors="replace") as f:
                raw = f.read()
        except OSError as e:
            print(json.dumps({
                "error": f"Could not read file: {e}",
                "hint": "Check the --file path.",
                "url": args.url or "",
                "source": "none",
            }))
            sys.exit(1)
        result = parse_html(raw, args.url or args.file)
    elif args.url:
        result = parse_url(args.url)
    else:
        print(json.dumps({
            "error": "No URL provided",
            "hint": ("Usage: python scripts/job_url_parser.py \"<job-url>\"  "
                     "(or --file <saved.html> --url <orig-url>, or --selftest)"),
            "url": "",
            "source": "none",
        }))
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if "error" not in result else 1)


if __name__ == "__main__":
    main()
