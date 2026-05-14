# JOBSEARCH-008 — ATS Format Checker — DONE

**From:** Jasmin (Security & Logic Auditor)
**To:** Andy
**Date:** 2026-05-13
**Task:** JOBSEARCH-008 — Build automated ATS format checker + update Cole's persona
**Status:** Complete — ready for deploy

---

## Deliverable Summary

1. **Script built and verified:** `D:\Claude Playground\scripts\ats_format_check.py`
2. **Cole's persona updated:** mandatory pre-delivery ATS check added to `D:\Claude Playground\agents\cole.md`
3. **Self-test on 3 existing CVs:** all three PASS (5 pass / 1 warn / 0 fail each)

Success criteria met:
- Six required checks implemented (tables, images, columns, headers/footers, fonts, date consistency)
- CLI matches spec: `python scripts\ats_format_check.py <path-to-cv.html>`
- Exit code 0 on PASS, 1 on FAIL (verified with synthetic bad-CV smoke test)
- Cole's persona now blocks any CV from shipping without a clean run
- Findings reported only; no CVs were modified by Jasmin (per task instruction)

---

## Script: `scripts/ats_format_check.py`

**Language:** Python 3.11 (consistent with the new MCP server pattern)
**Dependency:** `beautifulsoup4` (installed via `pip install beautifulsoup4` — version 4.14.3)
**Lines:** ~340

### Checks implemented

| # | Check | Hard fail / warn | Notes |
|---|-------|------------------|-------|
| 1 | No `<table>` tags | FAIL | Any `<table>` element fails the build. |
| 2 | No images | FAIL | `<img>` tags OR CSS `background-image` (excluding `none`) fail. |
| 3 | No CSS columns | FAIL on `column-count`/`columns`/`column-width` (multi-col only — `column-count: 1` and `auto` ignored). WARN on flex/grid in non-header body classes. |
| 4 | No semantic `<header>`/`<footer>` in body | WARN with ATS-risk explanation (per spec — many CVs use these visually). |
| 5 | Standard fonts only | FAIL on any font outside the approved 12 (Arial, Calibri, Cambria, Garamond, Georgia, Helvetica, Lato, Open Sans, Tahoma, Times New Roman, Trebuchet MS, Verdana). Generic CSS fallbacks (`sans-serif`, `system-ui`, `-apple-system`, etc.) are allowed. |
| 6 | Date format consistency | WARN when more than one format is detected. Recognizes 6 formats: Month YYYY, MM/YYYY, YYYY-MM, MM-DD-YYYY, DD/MM/YYYY, YYYY range (e.g. "2018 – 2024" or "2024 – Present"). |

### Output format
- Per-check section: `[PASS]` / `[WARN]` / `[FAIL]` + one-line message + up to 8 detail lines
- Summary line: pass/warn/fail counts
- Final verdict: `PASS` or `FAIL`
- Exit code: 0 on PASS, 1 on FAIL, 2 on usage error

### Edge cases handled
- CSS comments stripped before regex matching (`/* ... */` blocks)
- `column-count: 1` and `column-count: auto` correctly treated as non-multi-column
- Flex/grid is allowed on header/title/contact/section-title/job-header/row classes (those are universal CV header alignment patterns, not body multi-column flows)
- Inline `style="..."` attributes are collected and analyzed alongside `<style>` blocks
- HTML comments and `<script>`/`<style>` text excluded from date scan
- Generic CSS keywords (`inherit`, `initial`, `unset`) are allowed in font-family

### Smoke test (synthetic bad CV)
Built a deliberately ATS-hostile HTML fragment with `<table>`, `<img>`, `background-image`, `column-count: 2`, `<header>`, `<footer>`, Comic Sans font, mixed date formats. Result:
- 4 FAIL (tables, images, columns, fonts)
- 2 WARN (header/footer, mixed dates)
- 0 PASS
- Exit code: 1
Confirms the failure path fires correctly.

---

## Self-test results on existing CVs

All three CVs PASS the checker with identical findings:

### 1. `LENOVO-CTO-IncubationPM\v1_Inon_Baasov_CV_IncubationPM.html`
- 5 PASS, 1 WARN, 0 FAIL → **PASS**
- WARN (check 3): `.skills-grid` uses `display: flex`. Verified manually: this is the skills chip row, not body content — safe.

### 2. `ELBIT-SystemEng-PM-Netanya\v1_Inon_Baasov_CV_SystemEngPM.html`
- 5 PASS, 1 WARN, 0 FAIL → **PASS**
- Same `.skills-grid` warning. Safe.

### 3. `20248_TechnicalPM_Elbit_Netanya\v1_Inon_Baasov_CV_TechnicalPM.html`
- 5 PASS, 1 WARN, 0 FAIL → **PASS**
- Same `.skills-grid` warning. Safe.

**Common observation across all three CVs:**
- Fonts: `Arial`, plus generic fallbacks `sans-serif`, `system-ui`, `-apple-system` — clean.
- Dates: all use the `YYYY range` format consistently (e.g., `2024 – Present`, `2018 – 2024`).
- No tables, no images, no semantic header/footer, no CSS multi-column.

**No CV failures. No remediation required from Cole on existing CVs.**

---

## Cole persona changes

File: `D:\Claude Playground\agents\cole.md`
Added a new section between Inon's CV Preferences and Constraints titled **"Mandatory Pre-Delivery ATS Format Check"**.

Key clauses added:
1. The check is **mandatory** before any CV moves to `cv_archive`.
2. Documented CLI command and script path.
3. Defined hard rule: **exit 1 = no archive**; FAIL must be fixed before shipping.
4. Warnings must be **explicitly documented** in the CV's INDEX entry (accepted-with-rationale, or fixed).
5. Six-step workflow: finalize → check → fix-if-fail → document-if-warn → archive → paste report into metadata.
6. Rationale block ("Why this rule exists") tied to the Video 3 research (98% Fortune 500 ATS adoption).

Cole's existing rules (Inon's preferences 1–9) and Constraints section were not modified.

---

## Team Quality Rubric findings

Per the rubric in CLAUDE.md (rule 2), splitting findings into infrastructure vs. design:

### Infrastructure findings
1. **Python dependency added:** `beautifulsoup4` 4.14.3 was not previously installed. Installed via pip. **Prevention:** consider adding a `scripts/requirements.txt` listing `beautifulsoup4>=4.12` so future agents (and CI, when added) install dependencies deterministically rather than discovering missing packages at runtime.
2. **No CI hook yet.** The check is currently enforced by Cole's persona instruction — that is process, not infrastructure. **Recommended next step:** a pre-commit hook or `scripts/cv_release.ps1` wrapper that refuses to copy a CV into `cv_archive/` unless the checker returns 0. Cheap to add, eliminates the risk of Cole "forgetting" the check.
3. **Encoding caveat:** the console output renders the em-dash and en-dash as `?` on Windows CP1252 consoles. The script itself reads files as UTF-8 (correct) and emits UTF-8 text — the rendering is a terminal-encoding artifact only, not a script bug. **Prevention:** future scripts should call `sys.stdout.reconfigure(encoding='utf-8')` on Windows; non-blocking.

### Design findings
1. **`skills-grid` flex layout** triggers a WARN on every Inon CV. The check is correct — it cannot tell from CSS alone whether the flex container holds inline skill chips (safe) or full bullet-point columns (unsafe). The WARN is the right behavior. **Cole should document** in each CV INDEX entry: "Warning 3 (skills-grid flex): accepted — used for horizontal skill-chip wrapping only, no body content in columns."
2. **Date check is informational on year-range-only CVs.** Year ranges like "2018 – 2024" are detected as the `YYYY range` format. If a future CV mixes "Jan 2020 – Mar 2024" (month precision) with "2018 – 2024" (year only), the checker will WARN. That is correct — Cole should pick one precision per CV and stick to it.
3. **The 12 ATS-safe fonts list is conservative.** It mirrors the YouTube research and common ATS recommendations. If a future CV needs a font outside the list, Jasmin must approve the addition before the checker is loosened — fonts are a known kill-switch in ATS parsing and we should not relax this casually.
4. **No false positives on flex used in title/header/contact/section-title/job-header/row classes.** Confirmed against all three Inon CVs. If Cole introduces a new layout class containing body content in flex, it will correctly WARN.

---

## Files touched

| File | Change |
|------|--------|
| `D:\Claude Playground\scripts\ats_format_check.py` | **Created** — ATS format checker (~340 lines). |
| `D:\Claude Playground\agents\cole.md` | **Updated** — added "Mandatory Pre-Delivery ATS Format Check" section after rule 9, before Constraints. |
| `D:\Claude Playground\agents\andy\inbox\jasmin_ats_checker_done.md` | **Created** — this report. |

No CV files were modified.

---

## Recommended Andy follow-ups

1. **Endorse the Cole persona change** — Cole now must run the checker on every CV. Light touch but it changes Cole's working contract.
2. **Optionally add `scripts\requirements.txt`** with `beautifulsoup4>=4.12` so Yoni/Mack/Jasmin are working from a pinned dep set going forward (infra finding #1).
3. **Optionally schedule a Mack task** for a CI/pre-commit hook that runs the checker on any HTML staged into `cv_archive/` (infra finding #2). Not blocking — Cole's persona instruction is the floor.
4. **Spot-check the next CV Cole produces** to confirm the report-paste step lands in the CV's metadata block as designed.

---

**Ready for deploy. JOBSEARCH-008 complete.**
— Jasmin
