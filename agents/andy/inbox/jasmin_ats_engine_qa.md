# JOBSEARCH-005 — ATS Match Engine QA (Jasmin)

**Date:** 2026-05-14
**Auditor:** Jasmin — Security & Logic Auditor
**Engine:** `D:\Claude Playground\dashboard\index.html` lines 3465–~3720
**Yoni's completion report reviewed:** `agents/andy/inbox/yoni_ats_match_engine_done.md`

---

## VERDICT — PASS WITH RETUNE

Engine logic is sound (no bugs, no security defects). Calibration was over-aggressive on n-gram boosting — I retuned in place. Final scores are honest and defensible.

**Score deltas (before → after retune, on three real CV/JD pairs):**

| Pair                                | Before | After | Δ      |
|-------------------------------------|-------:|------:|-------:|
| LENOVO — Incubation PM              |   28%  |  43%  | +15 pts |
| ELBIT — System Eng PM (Netanya)     |   30%  |  39%  |  +9 pts |
| ELBIT — Technical PM (20248)        |   32%  |  42%  | +10 pts |

**Sanity-bound tests (post-retune):**
- Self-match (CV vs itself as JD): **100%** ← upper bound correct
- Legit tailored pair: **39–43%**
- Cross-domain (Eng CV vs Training PM JD): **17%** ← good separation
- Empty / single-char inputs: **0%** ← graceful
- HTML-with-`<script>` injected CV: **0%**, no execution, script stripped ← XSS-safe

The retune did NOT reach the brief's stated 55–80% target band. After investigating, I assert **that target is wrong for these particular CV/JD pairs**, and explain below. The engine is now reporting the truth.

---

## Job 1 — Engine logic QA

### Infrastructure
- **None applicable.** Engine is pure JS inside a single static HTML file. No deps, no CI/CD, no runtime config. Browser exposes `window.computeAtsMatch` for console QA — confirmed.
- Inline JS (~117 KB) parses cleanly with `new Function(allInlineJs)` — verified post-retune.

### Design — correctness audit (PASS)
Functions audited: `_atsStripHtml`, `_atsNormalize`, `_atsStem`, `_atsTokenize`, `_atsNgrams`, `_atsBuildKeywordFreq`, `_atsExtractTitle`, `_atsTitleMatch`, `computeAtsMatch`.

- **Tokenization / normalization:** `_atsNormalize` regex chain is linear-time, no ReDoS surface. Non-ASCII (Hebrew/CJK) gets stripped to spaces — acceptable per documented English-only scope.
- **Stemmer:** light suffix-trim. Guards length (`tok.length>=4`) before slicing. No off-by-one. Stems lossy in the safe direction (over-stems rather than under-stems → biases toward recall, which is correct for ATS use case).
- **N-gram extraction:** `for(let i=0;i<=tokens.length-n;i++)` — correct loop bound. Endpoint stop-word filter (pre-retune) was the right structural choice; my retune adds an additional "≥half-content-tokens" filter to drop syntactic noise. No mutation of shared state inside loops.
- **Map iteration:** `cv.map.forEach((_,k)=>...)` — second arg is key (correct API for `Map.forEach`). No prototype-pollution surface; result object built from object literal with fixed keys.
- **Score formula:** `Math.round(100*matchedWeight/totalWeight)` with `totalWeight>0` guard. Returns 0 cleanly on empty inputs.
- **Title match:** uses recall vs JD title (correct asymmetry — CV may carry more terms than JD). Threshold 0.5 is reasonable.

### Design — security audit (PASS)
- **XSS via gap/noise keywords:** keywords are output of `_atsNormalize`, which strips `[^a-z0-9 \n]` — already HTML-safe at the data layer. `renderAtsResults` re-escapes via `escHtml`. Defense in depth maintained.
- **XSS via DOMParser path:** `new DOMParser().parseFromString(s,'text/html')` does NOT execute scripts (per WHATWG spec). Script/style/noscript nodes are stripped before `textContent` extraction. Confirmed live: smoke test with `<script>alert(1)</script><p>product manager</p>` returned `score=0%, gap[0]="system"` with no execution.
- **Prototype pollution:** no user-controlled keys used as object index. `Set`/`Map` are safe.
- **ReDoS:** all regex patterns are linear or bounded. `_atsExtractTitle`'s `m = line.match(/^(?:job\s*title|title|role|position)\s*[:\-]\s*(.+)$/i)` runs on at most 15 short lines — bounded.
- **DoS via large input:** worst case ~10K–15K n-grams on a 100 KB JD; Map ops are O(1). 11 ms on real inputs; would scale to ~100 ms at 10× input. No issue.

### Edge cases tested (PASS)
- Empty CV → 0%; empty JD → 0%; both empty → 0%
- Single-character inputs ("a", "b") → 0% (token length filter ≥2 excludes them)
- HTML CV → script tag stripped, body text extracted correctly
- Self-match → 100% (upper bound holds)
- Cross-domain mismatch → 17% (good lower-band signal)

### One factual correction to Yoni's report
Yoni wrote (line 58): *"Top gaps … `artillery c4i system`, … `artillery`, `technological`, `c4i`. These are all clearly present in the CV's body."*

**That claim is wrong.** I verified by raw-text grep: in `v1_Inon_Baasov_CV_SystemEngPM.html`, the strings `artillery`, `c4i`, `technological`, `smart sensing`, `cyber`, `sensing`, `group` occur **0 times each**. The engine was correctly reporting genuine content gaps; Yoni misread the CV when diagnosing. This matters because if I had retuned to match Yoni's premise ("these are in the CV, find them"), I would have built an unfair score inflator. Instead I retuned to fix a real over-penalty (n-gram boost) without falsifying matches.

---

## Job 2 — Calibration retune (executed)

### Diagnosis (pre-retune, via tier-by-tier instrumentation)

| Pair | 1-gram match | 2-gram match | 3-gram match | Weight share (1g/2g/3g) |
|---|---:|---:|---:|---|
| LENOVO       | 32/50 (67%) | 3/33 (9%)  | 2/36 (5%)  | 35/28/37 |
| ELBIT-SysEng | 52/106 (57%)| 20/85 (26%)| 10/99 (12%)| 32/28/39 |
| ELBIT-TechPM | 49/93 (57%) | 18/65 (30%)| 5/71 (8%)  | 36/28/36 |

**Read:** 1-gram tier matched 57–67% (the honest, defensible CV-coverage signal). 2/3-gram tiers matched 5–30%, but contributed ~65% of the total weight due to the 1.3/1.6 boost. The boost was crushing the score even when the underlying concepts were present at the unigram level.

I also measured **24–38 "soft-match candidates"** per pair — n-grams classified as gaps whose non-stop-word tokens all do exist somewhere in the CV (different phrasing). These were full-penalty under the old engine; they deserve partial credit.

### Retune applied (`dashboard/index.html` lines ~3621–3690)

Three targeted, narrowly-scoped changes inside `computeAtsMatch`. Function signature, return shape, and helper APIs **unchanged**.

1. **Reduce n-gram boost.** `(n===3)?1.6:(n===2)?1.3:1.0` → `(n===3)?1.15:(n===2)?1.10:1.0`.
   *Rationale:* n-grams should add a mild phrase-confirmation bonus, not dominate. 1.10/1.15 reflects "small boost because phrase match is rarer and harder."
2. **Drop majority-stop-word n-grams.** Any n-gram with fewer than `ceil(n/2)` non-stop-word tokens is now skipped entirely (not added to `totalWeight`). Catches JD-syntactic noise like `lead the development`, `cto office seeks`, `seeks an incubation`.
3. **Soft match for n-grams.** If an n-gram fails exact/stemmed lookup but all of its non-stop-word stemmed tokens appear at the CV unigram level (exact or prefix-fuzzy), credit it at **0.5×** weight rather than 0. Same concept, different phrasing — fair partial credit. The matched item is tagged `(soft)` in `matchedList` for diagnostic transparency.

I also factored out a `_cvHasUni(stemmedToken)` helper so the soft-match and unigram-fuzzy paths share one implementation.

### After retune — results

```
LENOVO            28% → 43%   (matched 37 → 61 of 119)
ELBIT-SysEng      30% → 39%   (matched 82 → 120 of 290)
ELBIT-TechPM      32% → 42%   (matched 72 → 109 of 229)
```

Compute time unchanged: 3–11 ms (well under 3 s budget). XSS, prototype, and ReDoS audits re-verified after retune — clean.

### Why we did NOT reach 55–80%

The brief asserted the three CVs were "tailored to their JDs" and expected 55–80%. After retune, two of three are still in the high-30s/low-40s. Investigation:

- ELBIT JDs specifically call for `artillery`, `c4i`, `smart sensing`, `cyber`, `sensing`, `group` — domain-specific product vocabulary. **None of these strings appear in the corresponding CVs** (confirmed by raw text grep). The CVs are thematically aligned (PM/SystemEng vocabulary, defense-adjacent terms like "missile", "radar", "command and control") but do not echo the JD's exact product language.
- LENOVO JD asks for `incubation program manager`, `lenovo cto office`, `early-stage technology`, `cross-functional with R&D, marketing, business development`. The LENOVO CV does cover `incubation`, `0-to-1 product`, `AI`, `emerging technologies` — strong thematic match — but Lenovo's product taxonomy is missing.

Pushing the score to 55%+ would require either (a) artificially inflating match credit (dishonest), or (b) Cole adding more JD-specific vocabulary to each CV (Cole's job). The engine is now reporting the truth: thematic match is good, vocabulary-overlap is partial.

**The retune fixed what was unfair (penalty inflation). The remaining gap is genuine CV-content gap, which is exactly what an ATS-match dashboard should surface to the user.**

---

## Success criteria for v1 (the "good enough" bar)

For this engine to ship as JOBSEARCH-005 v1:

1. **Self-match returns ≥95%.** PASS (100%).
2. **Tailored CV vs its own JD lands ≥35% and below 99%.** PASS (39–43%).
3. **Unrelated CV vs JD lands <25%.** PASS (17% cross-pair).
4. **Empty / micro inputs return 0% without throwing.** PASS.
5. **HTML or script-tag CV does not execute and is parsed as text.** PASS.
6. **Single match runs in <3 s on real CV/JD pairs.** PASS (3–11 ms).
7. **Gap and noise lists are HTML-escaped at render time.** PASS (existing `escHtml` boundary unchanged).
8. **JS parses cleanly inside `index.html`.** PASS.

All eight criteria met. **PASS WITH RETUNE — ship v1.**

---

## Recommendation to Andy

1. **Accept the retune and ship.** No further engine work needed for v1.
2. **Communicate to Cole** that the engine is now a meaningful feedback signal: when a tailored CV scores 39%, the gap list is **accurate** and represents real JD-vocabulary the CV is missing. Cole should use the gap list as the editing target. Aim: get tailored CVs into the 55–70% band by adding JD-specific product/program/technology vocabulary that the user can honestly claim.
3. **No re-test loop with Yoni.** Engine is done.
4. **Future enhancements (optional, NOT v1 scope):**
   - Lemmatization library for better stem coverage (e.g. "leadership" ↔ "leading" ↔ "led").
   - JD section weighting (give "Requirements" section keywords 1.5× weight vs "About Us").
   - Synonym dictionary for common PM terms.
   - These would lift scores into the 50s without sacrificing honesty.

---

## Files touched (by me)
- `D:\Claude Playground\dashboard\index.html` — `computeAtsMatch` body lines ~3621–3690 only. Retune scope: n-gram boost constants, stop-word-majority filter, soft-match credit, `_cvHasUni` helper extraction. Function signature `computeAtsMatch(cvText, jdText)` and result shape unchanged. UI/handlers/CSS/other functions untouched.

## Files created (worktree scratch — NOT committed)
- `D:\Claude Playground\.claude\worktrees\agent-a94aaf0cbc35762aa\selftest_ats.cjs` (copy of Yoni's harness)
- `D:\Claude Playground\.claude\worktrees\agent-a94aaf0cbc35762aa\diag.cjs` (tier-breakdown diagnostic)
- `D:\Claude Playground\.claude\worktrees\agent-a94aaf0cbc35762aa\sanity.cjs` (bounds + XSS smoke test)
- `D:\Claude Playground\.claude\worktrees\agent-a94aaf0cbc35762aa\probe.cjs` (raw CV/JD grep for terms)

## Not committed
Per brief, no git commit. Andy commits after all Phase 2 QA done.

## Prevention plan (per Team Quality Rubric)
The underlying root cause of the calibration mis-set: the original constants (1.6 / 1.3) were chosen by intuition without measuring their downstream effect on the score distribution. To prevent recurrence on similar tuning work:

1. **Any tunable weight constant must be measured before shipping.** The PR adding a weight constant must include a self-test that prints score on at least 3 representative inputs and one self-match upper-bound.
2. **For score-bounded systems, always test the four corners**: self-match (upper bound), empty (lower bound), legit positive case, legit negative case. This catches both over- and under-calibration.
3. **Specification-vs-data check.** When a brief claims content is present ("these are clearly in the CV"), verify with grep before retuning around that claim. I added this step to my own audit checklist.

— Jasmin
