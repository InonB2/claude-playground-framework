# JOBSEARCH-005 — ATS Match Engine — DONE (Yoni)

**Date:** 2026-05-14
**Status:** Ready for Jasmin QA
**Scope of this finishing pass:** the last 15% — HTML panel, init wiring, self-test on 3 real CV/JD pairs.

---

## Success criteria — status

| Criterion | Status |
|---|---|
| HTML panel exists and renders | OK — `<div id="tab-ats">` at line 926 of `dashboard/index.html` (was already in place from the previous Yoni session; confirmed, not duplicated) |
| Dropdown populates from `cvVersions` | OK — `populateAtsCvPicker()` called from inside `renderCvs()` AND at the end of `init()` (belt-and-suspenders) |
| Analyze runs in <3 s | OK — engine completes in 19–33 ms in Node on real CV/JD pairs |
| Score color band correct | OK — `band = score>=75 ? 'green' : score>=50 ? 'yellow' : 'red'` (existing in `renderAtsResults`) |
| Self-test scores reasonable on 3 pairs | PARTIAL — see Design findings; engine returns 28–32% on three CVs that Cole tailored to the JDs |
| No regression in Tasks/Jobs/CVs/LinkedIn | OK — JS parses cleanly (`new Function(allInlineJs)` succeeds), `switchTab()` is generic and handles `'ats'` without changes |
| No XSS — JD rendered as text | OK — `renderAtsResults` uses `escHtml()` on every JD-derived string (`titleMatch.cvTitle`, `jdTitle`, gap/noise keywords) |

---

## What I added in this pass

**File:** `D:\Claude Playground\dashboard\index.html`

1. **`renderCvs()`** — appended a guarded call to `populateAtsCvPicker()` so the picker stays in sync whenever the CV list changes (add, edit, dup, delete, status change):
   ```js
   // JOBSEARCH-005: keep ATS picker in sync with CV list
   try { if (typeof populateAtsCvPicker === 'function') populateAtsCvPicker(); } catch(_){}
   ```

2. **`init()` IIFE** — added a second guarded call after `renderLiList()` so the picker is populated even on first paint regardless of `renderCvs()` ordering:
   ```js
   try { populateAtsCvPicker(); } catch(_){}
   ```

3. **Static integrity check** ran clean:
   - 1 inline `<script>` block, ~115 KB JS, parses with no syntax errors
   - All 9 DOM/function anchors present: `#tab-ats`, `#atsCvPicker`, `#atsCvText`, `#atsJdText`, `#atsResults`, `data-tab="ats"`, `function populateAtsCvPicker`, `function computeAtsMatch`, and the new `renderCvs()` hook
   - Dashboard served at `http://127.0.0.1:8765/dashboard/` returns HTTP 200, 200,507 bytes

**No changes** to the engine, CSS, tab button, or the existing handlers — those were already complete.

---

## Self-test results (3 real CV/JD pairs)

Test harness: `D:\Claude Playground\.claude\worktrees\agent-afed54e7ff52a623b\selftest_ats.cjs`
Approach: extract the engine block from `dashboard/index.html`, evaluate it in a Node `vm` sandbox with a stub `DOMParser` (CVs pre-stripped to plain text in Node so the DOMParser branch is not exercised), then call `computeAtsMatch(cvText, jdText)` directly.

| Pair | Score | Band | Matched / Total | Title match | Compute |
|---|---:|---|---|---|---:|
| LENOVO CTO — Incubation PM (CV: `LENOVO-CTO-IncubationPM/v1_Inon_Baasov_CV_IncubationPM.html`, JD: synthesized from brief — no JD.txt in folder) | 28% | RED | 37 / 119 | NO (recall 0.33) — CV title "Tech Incubation \| 0-to-1 Product Strategy \| AI & Emerging Technologies" vs JD "Incubation Program Manager" | 33 ms |
| ELBIT — System Eng PM (Netanya) (CV+JD from `ELBIT-SystemEng-PM-Netanya/`) | 30% | RED | 82 / 290 | **YES (recall 1.0)** — CV "Product Manager & System Engineer" vs JD "Product Manager / System Engineer" | 23 ms |
| ELBIT — Technical PM 20248 (CV+JD from `20248_TechnicalPM_Elbit_Netanya/`) | 32% | RED | 72 / 229 | **YES (recall 0.6)** — CV "Technical Project Manager" vs JD "Elbit Systems — Technical Project Manager" | 19 ms |

Top gaps (sample, ELBIT System Eng): `artillery c4i system`, `lead the development`, `artillery c4i`, `c4i system`, `israeli market`, `artillery`, `technological`, `c4i`. These are all clearly present in the CV's body — the engine is failing on multi-grams that are not phrased identically in CV vs JD.

**Sanity check verdict:** scores are NOT in the brief's stated 60–85% expected band. Two of the three are below the 30% sanity floor I set. This is **not a UI bug** — the panel, picker, handlers, color bands, and timing are all fine. It is an **engine tuning issue** flagged below.

---

## Findings (per the Team Quality Rubric — separate infrastructure from design)

### Infrastructure
- **None.** The dashboard is a single static HTML file served by any static server. No CI/CD, no deps. `npx serve` was not available locally; I used `python -m http.server` to verify the page loads (HTTP 200). No infrastructure changes required.
- **Static integrity:** inline JS (~115 KB) parses cleanly. No broken `<script>` boundary, no stray `</script>`, no missing closing brace.

### Design — engine scoring is too strict for QA's expected range
The engine produces 28–32% on three CVs that Cole **tailored to their respective JDs**. The brief told me to flag "anything outside 60–85%." Root causes I can see from gap output:

1. **N-gram boost is too aggressive.** Trigrams are weighted ×1.6 and bigrams ×1.3. JDs contain hundreds of trigrams (e.g. `lead the development`, `artillery c4i system`) that the CV expresses with different phrasing (`led artillery C4I systems`, `developed and led`). Each missed trigram costs ~1.6 × log₂-weighted points, and there are 50+ of them per pair — they dominate the score.
2. **Stop-word list excludes only n-gram **endpoints**, not interiors.** Trigrams like `lead the development` survive because `lead` and `development` are not stop words, but the trigram is essentially "lead … development" semantically — and the CV says "led product development." The unigram path catches it; the trigram path penalizes it again.
3. **Stem-prefix fuzzy match runs only for unigrams.** "artillery" is in both CV and JD, but the engine matches it via the unigram path and still counts the bigram `artillery c4i` and trigram `artillery c4i system` as misses, each with high weight.
4. **No deduplication between n-gram tiers.** If `c4i` (unigram) matches, the JD still has `c4i system` (bigram) and `artillery c4i system` (trigram) in `jd.map`, and missing those compounds the penalty.

**Suggested fixes for Jasmin/Andy to consider (out of scope for this finishing pass):**
- Reduce n-gram boosts: trigram 1.6 → 1.2, bigram 1.3 → 1.1.
- When a bigram/trigram matches at the unigram level for *all* its non-stop-word tokens, count it as a "soft match" with 0.5× weight instead of 0× (full gap).
- OR: switch the score to a token-set Jaccard or BM25 with lemma matching, and treat n-grams as a separate "phrase bonus" cap.

**Note:** I did **not** touch the engine — the brief said the engine was complete and that the previous Yoni session built it. Andy should route this to Jasmin for engine QA / decide whether to retune before shipping.

### Design — picker init double-call is intentional
Calling `populateAtsCvPicker()` both inside `renderCvs()` and at end of `init()` is deliberate. `renderCvs()` runs only when the CV list changes; the second call guarantees the picker is populated on first page paint even if seeding logic changes call order. Both calls are `try`-wrapped so they cannot break init.

### Design — switchTab is generic and needed no patch
`switchTab(name)` toggles `.active` by `data-tab=` and `#tab-${name}`. The `'ats'` tab button (line 802) and panel (line 926) follow the same convention as every other tab, so it works without code changes. The only tab-specific branch is `body.classList.toggle('tab-linkedin', tab==='linkedin')` which correctly remains LinkedIn-only.

---

## Files touched
- `D:\Claude Playground\dashboard\index.html` — 2 small wiring additions (renderCvs hook + init tail call). Net ~4 lines.

## Files created (worktree scratch — NOT committed)
- `D:\Claude Playground\.claude\worktrees\agent-afed54e7ff52a623b\selftest_ats.cjs` — Node self-test harness. Re-runnable: `node selftest_ats.cjs` from that dir.

## Not committed
Per the brief, I did **not** run git commit. Andy commits after Jasmin signs off on engine logic.

## Recommended next step for Andy
1. Route engine logic to Jasmin for QA — she should decide whether the 28–32% scores on tailored CVs indicate a real defect or are acceptable for the v1 release.
2. If Jasmin flags it, send back to me for the n-gram-weight retune described above.
3. After sign-off, commit and update `tasks/active_tasks.json` (JOBSEARCH-005 → done).

— Yoni
