# JOBSEARCH-010 — Job URL Auto-Parser — DONE (Mack)

**Date:** 2026-05-14
**Status:** Ready for QA (Jasmin — Python logic/script; Vera — dashboard UI). **Do NOT commit yet — Andy commits after QA sign-off.**
**Files touched (two):**
- NEW: `D:\Claude Playground\scripts\job_url_parser.py`
- MODIFIED: `D:\Claude Playground\dashboard\index.html` (one file, additive only)

---

## Architecture decision + rationale

**Two-piece solution, as the brief recommended — and it's the only sane path.** The dashboard is a static HTML file with no backend. Browser JS *cannot* fetch LinkedIn/Indeed/Glassdoor pages: CORS blocks cross-origin fetches outright, and even if it didn't, those boards actively block non-browser clients. So the network fetch has to happen somewhere with no CORS sandbox and the ability to send a real User-Agent — i.e. a server-side Python CLI.

1. **`scripts/job_url_parser.py`** — fetches the page server-side, extracts structured fields, prints clean JSON to stdout.
2. **Dashboard "Import Job" modal** — two input modes: paste the parser's JSON (Mode A), or paste raw copied job text (Mode B, the universal zero-network fallback). Both show an **editable preview** before committing a job card.

The split is deliberate: the Python half does the one thing a browser can't (authenticated-looking network fetch + HTML parsing), and the dashboard half does the one thing Python shouldn't (own the data model and the UI). Mode B exists because **some boards block even server-side fetches** — when the Python script fails, it explicitly tells the user to fall back to Mode B, which works for *any* board because it never touches the network.

---

## Part 1 — Python parser (`scripts/job_url_parser.py`)

### Usage
```
python scripts/job_url_parser.py "<job-url>"              # fetch + parse a live URL
python scripts/job_url_parser.py --file saved.html --url "<orig-url>"   # parse a saved page
python scripts/job_url_parser.py --selftest               # built-in JSON-LD extraction test
```
Output is **always JSON** on stdout (success object or `{error, hint}` object) — the caller never has to parse stderr. Exit code 0 on success, 1 on graceful error.

### Extraction strategy (3 layers, in priority order)
1. **JSON-LD `JobPosting` schema** — `<script type="application/ld+json">`. This is the most reliable path and is board-agnostic: Google for Jobs *requires* this markup, so Glassdoor, Indeed, most Greenhouse/Lever/Workday-backed boards, RemoteOK, and any Google-indexed posting embed it. Handles `@graph` arrays, nested `hiringOrganization`/`jobLocation` dicts-or-strings-or-lists, and lenient recovery of slightly-broken JSON-LD (trailing commas, control chars).
2. **Per-board HTML selectors** — explicit CSS-selector fallbacks for LinkedIn, Indeed, Glassdoor, Google Jobs when JSON-LD is absent or partial.
3. **Generic heuristics** — `og:` meta tags, `<h1>`, longest `<article>`/`main`/`[class*=description]` block. Works on many smaller boards with no structured data at all.

### Boards supported
| Board | How |
|---|---|
| **LinkedIn** | JSON-LD (primary) + `topcard__*` / `description__text` selectors (fallback) |
| **Indeed** | JSON-LD + `jobsearch-JobInfoHeader-*` / `#jobDescriptionText` selectors |
| **Glassdoor** | JSON-LD + `[data-test=job-title/employer-name/location]` selectors |
| **Google Jobs** | JSON-LD only realistically (it's an SPA — see findings); thin meta fallback |
| **Generic (any other board)** | JSON-LD `JobPosting` schema + `og:` meta + longest-content-block heuristic |

### Graceful failure
Every failure path returns `{error, hint, url, source}` with an **actionable hint**. When a board blocks the fetch (403/429/999) or serves an auth-wall/"verify you're human" page, the hint explicitly says: *open it in your browser, copy the text, use the paste-text fallback (Mode B)*. Timeouts, network errors, invalid URLs, missing args, missing deps — all return structured JSON, never a stack trace.

### Test results (honest — what worked, what blocked)
| Test | Result |
|---|---|
| `--selftest` (JSON-LD fixture) | **PASS** — title/company/location/JD all extracted, HTML stripped from JD, no markup leakage |
| **LinkedIn live URL** (`linkedin.com/jobs/view/4380617928`) | **PASS** — full extraction via JSON-LD: title "Technology Incubation – Early Stage Product Manager", company "Lenovo", location "California, United States", **7,878-char JD**, clean UTF-8 |
| **Indeed live URL** | **Blocked (HTTP 403)** — returned a clean `{error, hint}` telling the user to use Mode B. This is itself a finding (see Infrastructure below) — and exactly the designed-for behavior. |
| RemoteOK live URL (generic JobPosting board) | **PASS** — JSON-LD extracted, `source: generic` |
| Invalid URL / no args / unreadable `--file` | **PASS** — structured `{error, hint}` JSON, exit 1 |

So: **the LinkedIn success criterion is met with a real live URL.** Indeed blocks server-side fetches — documented, and the parser degrades gracefully to a Mode-B instruction rather than failing silently.

### Dependencies
`requests` + `beautifulsoup4` — **both already installed** (bs4 from Jasmin's ATS checker; requests was present). No new install needed in this environment. The script guards the import and prints a `pip install` hint if either is ever missing.

---

## Part 2 — Dashboard "Import Job" feature (`dashboard/index.html`)

### What was added (all additive, all namespaced `imp*` / `.imp-*` / `#imp*`)
- **"⇩ Import Job"** button in the Jobs-tab filterbar, next to "+ Add Application".
- **`#importJobModal`** — a modal with a 2-way mode switch:
  - **Mode A — Paste JSON:** paste the Python script's JSON output → "Parse & preview" → editable preview → "Add to board". Recognizes the parser's `{error}` objects and surfaces the hint instead of trying to import garbage.
  - **Mode B — Paste raw text:** paste copied job-posting text (+ optional URL) → JS heuristics extract title/company/location → editable preview → "Add to board". Universal fallback, zero network.
- **Editable preview** — every parsed field lands in an `<input>`/`<textarea>`/`<select>` the user can correct before committing. Stage defaults to **Bookmarked**.
- Imported card **flashes + scrolls into view** on commit (reuses Rex's existing `.flash-highlight` animation).

### Mode B heuristic parser
Copied job pages, once plain-text, follow loose-but-real conventions: title near the top, company on an early line (often the line right after the title, or `"<Title> at <Company>"`), a location line with a city/Remote token. The heuristic: detect `"at/@ <Company>"` patterns first, then first plausible non-chrome header line as title, then the line after the title as company, then first location-shaped line. LinkedIn's `" · 2 days ago"` decoration is trimmed off the location. The full pasted text becomes the JD. On a realistic LinkedIn-style paste it correctly pulled **title + company + location**; tested against `"PM at Stripe"`-style text too.

### Data-model fidelity (critical — verified)
Imported jobs are built to **exactly** the `saveJob()` shape:
`{id:'job-'+Date.now(), company, role, stage, rating:null, date:'', followUpDate:null, prepChecklist:defaultPrepChecklist(), url, notes}`
— plus `contacts:[]` and `createdAt:todayIsoLocal()`. **Note on those last two:** Rex's Phase 3 JS (`contacts`/`createdAt`) is **not yet merged into `index.html`** — only its CSS/HTML scaffolding is present (confirmed by grep: `JOBS_SEED_VER` still 5, no contacts JS). I seed `contacts:[]` and `createdAt` anyway so imported jobs are forward-compatible with Rex's incoming widget; his `migrateLegacyJobStages()` is idempotent and only writes missing fields, so this can't conflict. The JD text goes into `notes` (prefixed with `Location: …`) rather than a new `jdText` field — adding a model field was out of scope and would touch Rex's/Yoni's areas.

### XSS safety (verified)
Pasted JSON and pasted raw text are **never** rendered via `innerHTML`. Every parsed value reaches the DOM only through `.value` (inputs/textarea) or `.textContent` (status line). Test: an `<img onerror>` + `<script>` payload pasted into both modes produced **zero injected nodes**, the payload survived as literal text in the input `.value`, **no script executed**, and after committing + `renderJobs()` the existing `escHtml()` in the card renderer kept it inert in the kanban too.

### No regressions
`switchTab` untouched and still generic. All 6 tabs (Tasks/Jobs/CV/ATS/AI Toolkit/LinkedIn) still present and switchable post-import. `andy_jobs` localStorage still a plain array. No edits to engine, ATS, toolkit, or contacts code.

### Test results — dashboard
Full jsdom integration test: **86/86 PASS.** Covers: modal open/close, mode switch + aria state, invalid-JSON error, parser-`{error}`-object handling, valid-JSON preview population, commit creates a job with the **exact `saveJob()` key set** (compared field-by-field against a `saveJob()`-produced job), localStorage persistence + array shape, **XSS inert in both modes** (no injected nodes, no execution, before and after render), Mode B heuristic extraction on realistic LinkedIn-style text + `"at Company"` pattern, location-decoration trimming, empty-input guards, and full tab-switch regression. Inline JS parses clean (`new Function`), file 248,317 bytes.

---

## Findings — Infrastructure vs. Design (per CLAUDE.md rubric)

### Infrastructure
- **Indeed (and likely Glassdoor) block server-side fetches outright — HTTP 403.** This is the anti-scraping reality the brief warned about, confirmed live.
  - **Fix:** the parser detects 403/429/999 + auth-wall page text and returns an actionable `{error, hint}` pointing the user to Mode B (paste raw text), which has no network dependency and works for every board.
  - **Prevention:** Mode B is the structural prevention — the system never *depends* on any board allowing a fetch. Any board can break tomorrow and the workflow still functions via copy-paste. We should not invest in per-board scraper workarounds (proxies, headless browsers) — that's a maintenance treadmill against adversarial sites and likely against their ToS. The honest design is: try the fast path (URL → JSON), always have the universal path (paste text).
- **LinkedIn currently allows the fetch** and serves full JSON-LD — but this is not guaranteed to last. Same prevention applies: Mode B is the safety net.
- **Windows stdout encoding bug — found and fixed.** Python on Windows defaults stdout to cp1252; piping/redirecting the JSON corrupted UTF-8 (em-dashes, accented names → `0x96` mojibake), which would have fed broken data into the dashboard.
  - **Fix:** `sys.stdout.reconfigure(encoding='utf-8')` at startup + decode fetched bytes via the sniffed encoding. Verified: LinkedIn JD comes through as clean UTF-8 (0 replacement chars, en-dash preserved as U+2013).
  - **Prevention:** the script now forces UTF-8 I/O on every platform — this class of bug can't recur regardless of OS console default.
- **No new dependencies required** — `requests` + `beautifulsoup4` already installed. No CI/CD, no env config, no secrets (the parser uses no API keys — it's a plain HTTP GET with a browser UA).

### Design
- **Two input modes, not one.** Mode A (paste JSON) is the fast path for boards that parse cleanly; Mode B (paste raw text) is the universal fallback. A single "paste URL" box was never viable (CORS) and a JSON-only design would strand the user whenever a board blocks the script.
- **Editable preview before commit, both modes.** Heuristic extraction is best-effort by nature — the preview makes every field correctable, so a wrong guess is a 2-second edit, not a bad card. Matches the brief's friction-kills principle: fast capture, but never wrong-and-locked-in.
- **JD goes into `notes`, no new model field.** Keeps imported jobs identically-shaped to every other job so Rex's widgets and Yoni's toolkit don't need to know about imports. (Yoni's report flagged wanting a `jdText` field bundled with this task — I deliberately did **not** add it: it needs a migration and touches three agents' code. If Andy wants it, it's a clean separate task; for now the JD is captured and visible in Notes.)
- **Heuristic parser favors precision on title+company over guessing everything.** It confidently extracts title/company (the two fields that matter for a job card) and is best-effort on location; it never fabricates. If it can't find title or company, it still shows the preview with the full text as JD so the user can salvage it by hand rather than starting over.
- **Stage defaults to Bookmarked** — imported jobs are leads, not applications. Matches the funnel model from Video 1.
- **Everything namespaced `imp*`** — zero collision risk with Rex's `contacts`/snapshot code or Yoni's `tk*` toolkit code, even though all three land in the same file around the same time.

---

## Malfunctions found / prevention
1. **Windows cp1252 stdout mojibake** — fixed + prevented (see Infrastructure above; forced UTF-8 I/O).
2. **Indeed 403 block** — not a malfunction in our code; it's the environment. Handled by graceful-error design + Mode B fallback (see Infrastructure).
- **Process note:** Rex's Phase 3 JS is not yet in `index.html` (only scaffolding CSS/HTML). I built against the *actual current file state*, not Rex's report, and verified by grep — then made imported jobs forward-compatible with his incoming `contacts`/`createdAt` fields anyway. Prevention for the team: when a brief says "read agent X's report for current state," still grep the actual file — reports can describe work that's QA-pending and not yet merged.

## Recommended next steps for Andy
1. **Jasmin QA** — run `python scripts/job_url_parser.py --selftest`, a live LinkedIn URL, and a known-blocked board; confirm JSON output shape + graceful errors.
2. **Vera QA** — open the dashboard, click "⇩ Import Job", test Mode A with the parser's JSON output, test Mode B with copied text, paste an XSS payload into both, confirm imported cards are indistinguishable from added ones.
3. After sign-off: commit both files, set JOBSEARCH-010 → done in `tasks/active_tasks.json`. This closes Phase 3.

— Mack
