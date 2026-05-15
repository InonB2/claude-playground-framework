# Cole — Elbit CV Keyword Fix (v2) — DONE

**Date:** 2026-05-14
**Agent:** Cole — Conversion Copywriter
**Trigger:** Jasmin's ATS Match engine QA (JOBSEARCH-005) surfaced genuine JD-vocabulary gaps in two Elbit CVs.
**Principle applied:** Honesty over score. Zero fabrication. A keyword that cannot trace to genuine background was NOT forced in — it was documented as un-integrable.

---

## Summary of results

| CV | v1 score | v2 score | Δ | v1 matched | v2 matched | ATS format check |
|---|---:|---:|---:|---:|---:|---|
| ELBIT System Eng PM | 39% | **48%** | **+9 pts** | 120/290 | 146/290 | PASS (exit 0) |
| ELBIT Technical PM  | 42% | **51%** | **+9 pts** | 109/229 | 131/229 | PASS (exit 0) |

Scores measured by running the real `computeAtsMatch` engine extracted from `dashboard/index.html` against v1 and v2 CV text vs the respective JD text. v1 baselines (39% / 42%) reproduce Jasmin's QA numbers exactly, confirming the harness is faithful.

Files created (v1 untouched):
- `owner_inbox/archive/cv_archive/ELBIT-SystemEng-PM-Netanya/v2_Inon_Baasov_CV_SystemEngPM.html`
- `owner_inbox/archive/cv_archive/20248_TechnicalPM_Elbit_Netanya/v2_Inon_Baasov_CV_TechnicalPM.html`

---

## CV 1 — ELBIT System Engineer PM

**JD-critical terms flagged missing:** `artillery`, `c4i`, `c4i system`, `artillery c4i`

### Keywords I integrated honestly (and how)

| Keyword | v1→v2 count | Where / honest basis |
|---|---|---|
| `databases` / `database` | 0 → 4 | JD requirement: "Design system architecture with emphasis on databases and overall system performance." Inon genuinely defined database models for AiRakoon and architected database-backed system performance for the TouchE multi-platform SDK. Real work, JD's exact words. |
| `system performance` | 0 → 3 | Same JD line. TouchE SDK was genuinely architected for high availability / 99.99% uptime — that IS system-performance engineering. |
| `algorithms` / `algorithm` | 0 → 3 | TouchE's AI Recommendation Engine genuinely ran recommendation and ranking algorithms; Inon owned their requirements, performance criteria, and tuning. Also algorithm/model selection criteria in the consulting role. Genuine. |
| `system architecture` | 0 → 4 | Already implied in v1; now stated explicitly with the JD's phrasing. Inon genuinely owned architecture decisions at TouchE and AiRakoon. |
| `technology` / `technological` | thin → 4 | JD: "Rapidly learn new technologies." Inon genuinely ran a 12-month technology roadmap and learns new tech across 4 startups. |
| `matrix-based` (development team) | reworded → 3 | JD: "Manage a matrix-based development team." Inon genuinely ran 4 cross-functional squads at TouchE — relabelled to the JD's exact phrase. |
| `operational doctrine` | 0 → 1 | **Carefully scoped.** Inon's IAF Planning & Control role operated *within* established operational doctrine and command-and-control procedures. Phrased as "operating within established operational doctrine" — he did not author doctrine, so I did not claim he did. This is the honest framing of genuine military service (CV-GENERIC-001 establishes the service is real). |
| Summary rewritten | — | Now mirrors the JD's responsibility verbs ("define, integrate, and lead the development… from design through delivery within Agile processes," "comprehensive system-wide vision," "coherence across workflows and system configurations") using only genuine experience. |

### Keywords I could NOT integrate (and why)

| Keyword | Reason |
|---|---|
| `c4i`, `c4i system`, `artillery c4i`, `artillery c4i system` | **Inon's CV Permanent Rule #3 forbids "C4I" anywhere in the CV** — it reads as too narrow / pigeonholing. This is an explicit Owner rule that overrides ATS instincts. The CV uses "Defense Domain" instead. Un-integrable by policy, not by honesty alone. |
| `artillery` | Inon has **zero artillery background**. His IAF service was Planning & Control (operational roster, shift planning, readiness logistics) — not artillery systems, algorithms, or artillery doctrine. Forcing "artillery" in would be fabrication. Not done. |

**Honest finding:** the single biggest score ceiling on this CV is the artillery/C4I product vocabulary, which is genuinely absent from Inon's career AND partly blocked by his own CV rule. A System Eng PM applying to an artillery-C4I group will always show a vocabulary gap here unless he has artillery experience he has not disclosed. The 48% is the honest ceiling for the current background; pushing higher means fabrication.

---

## CV 2 — ELBIT Technical PM (Job 20248, Smart Sensing Group, C4I and Cyber)

**JD-critical terms flagged missing:** `smart sensing`, `sensing`, `cyber`, and related sensing/technical vocabulary

### Keywords I integrated honestly (and how)

| Keyword | v1→v2 count | Where / honest basis |
|---|---|---|
| `software development` | 0 → 5 | JD requirement: "At least 3 years of experience in software development." Inon genuinely led software development of the full TouchE stack (Web/Mobile/Smart TV SDKs, CMS, AI engine) and builds his own apps. v1 said "built/shipped" — v2 uses the JD's exact term. Genuine. |
| `algorithms` / `algorithm` | 0 → 6 | JD: "complex software and advanced algorithms." TouchE's AI Recommendation Engine genuinely involved recommendation and ranking algorithms; consulting work includes algorithm/model evaluation frameworks. Genuine. |
| `system thinking` | 0 → 4 | JD: "system thinking" listed in requirements. Inon genuinely applies system-level thinking across multidisciplinary projects — stated explicitly now. |
| `requirements and design reviews` / `design reviews` | thin → 6 | JD: "Prepare and participate in requirements and design reviews with stakeholders." Inon genuinely ran stakeholder design reviews at TouchE and Arena Plus. JD's exact phrase. |
| `integration and testing` | thin → 2 | JD: "Lead integration and testing of software and hardware." Inon genuinely led integration and testing of the TouchE SDKs. Now uses the JD phrase verbatim. |
| `hardware` | 1 → 2 | JD asks for software + hardware integration. TouchE Smart TV SDK genuinely spanned hardware and software layers (device integration). Honest, kept modest. |
| `requirements` (analysis) | thin → 8 | JD: "Analyze customer needs and translate them into clear engineering requirements." Inon genuinely did requirements analysis across all three roles. |
| Summary rewritten | — | Now mirrors the JD's responsibility list ("own all system engineering activities across the project lifecycle," "analyze customer needs and translate them into clear engineering requirements," "Product Owner in agile teams," "integration and testing of software and hardware") — all genuine. |

### Keywords I could NOT integrate (and why)

| Keyword | Reason |
|---|---|
| `smart sensing`, `sensing`, `smart sensing group`, `sensing group` | "Smart Sensing Group" is **Elbit's internal org/product-group name**. Inon has **no sensing-hardware or sensor-systems background**. Echoing "smart sensing" would claim domain experience he does not have — fabrication. Not done. |
| `cyber`, `c4i and cyber`, `c4i` | Inon has **no cybersecurity background**, and **CV Permanent Rule #3 forbids "C4I"** anywhere. Both un-integrable — `cyber` by honesty, `c4i` by Owner policy. CV uses "Defense Domain" instead. |
| `group` | Pure JD org-label noise ("Smart Sensing Group", "C4I and Cyber"); not a real skill keyword. Correctly left out. |

**Honest finding:** the remaining gap is entirely Elbit's product-group taxonomy (smart sensing / cyber / C4I). The CV is now strongly aligned on the *role's actual work* — software development, algorithms, system engineering lifecycle, Agile/PO, integration & testing, design reviews — which is what the Responsibilities and Requirements sections actually screen for. 51% is the honest ceiling without a sensing/cyber background.

---

## Verification evidence

### ATS format check (mandatory pre-delivery gate)

Both v2 files: `python scripts/ats_format_check.py <path>` → **5 pass, 1 warn, 0 fail — FINAL VERDICT: PASS — exit 0.**

- The one WARN on both: `.skills-grid` uses `display:flex`. **Decision: accepted with rationale** — identical to v1. The flex container holds short skill *chips* (a wrapping tag list), not side-by-side body paragraphs/sections; ATS parsers read it as an inline list, not a multi-column layout. No change needed; v1 shipped with the same construct.

### Keyword / score improvement (ATS Match engine)

Ran the real `window.computeAtsMatch` from `dashboard/index.html` via a Node harness (DOMParser shimmed to strip script/style then tags → text; engine logic untouched). v1 baseline reproduced Jasmin's exact numbers (39% / 42%), confirming fidelity.

```
ELBIT System Eng PM   39% -> 48%   (+9 pts)   matched 120 -> 146 / 290
ELBIT Technical PM    42% -> 51%   (+9 pts)   matched 109 -> 131 / 229
```

Post-v2 top gap lists confirm the honesty story: remaining gaps are exactly the un-integrable terms (`artillery`, `c4i`, `smart sensing`, `cyber`) plus pure JD-header noise (`elbit systems netanya`, `title product manager`, `url https`, `job jid`, `source pasted`). Nothing honestly integrable was left on the table.

Raw keyword counts (v1 → v2):
- SysEng v2: `database` 0→4, `algorithm` 0→3, `system performance` 0→3, `system architecture` →4, `technology` →4, `operational doctrine` 0→1, `matrix-based` →3 | `artillery` 0→0, `c4i` 0→0 (correctly un-integrable)
- TechPM v2: `software development` 0→5, `algorithm` 0→6, `system thinking` 0→4, `design review` →6, `integration and testing` →2, `hardware` 1→2 | `smart sensing` 0→0, `cyber` 0→0, `c4i` 0→0 (correctly un-integrable)

---

## Findings — Infrastructure vs Design (per Team Quality Rubric)

### Infrastructure
- **No infrastructure defects.** Both CVs are single static HTML files, no deps, no build. ATS format checker runs clean (exit 0) on both v2 files.
- The dashboard `computeAtsMatch` engine is browser-coupled (`DOMParser`). For repeatable CV-vs-JD scoring outside a browser, a small Node harness with a DOMParser shim works and reproduces engine output exactly — **recommend** Andy keep a permanent `scripts/ats_score.cjs` so any agent can re-score a CV without opening the dashboard. (Not built this session — flagging as a process improvement.)

### Design
- **Root cause of the low v1 scores was genuine content gap, not formatting** — exactly as Jasmin's QA concluded. v1 CVs were thematically aligned but did not echo the JD's literal vocabulary on the integrable terms (`databases`, `algorithms`, `software development`, `design reviews`, `system thinking`). v2 fixes that for every term that maps to real experience.
- **Two distinct ceilings remain, both legitimate:**
  1. *Policy ceiling* — CV Permanent Rule #3 (no "C4I") blocks a JD-critical term in both CVs. This is an intentional Owner trade-off (avoid pigeonholing) accepted at the cost of ~a few ATS points. Worth Andy confirming with Inon whether the rule should hold for defense-sector applications specifically, or whether "C4I" is acceptable in a Military Service context only. **That is an Owner decision, not Cole's to override.**
  2. *Experience ceiling* — `artillery`, `smart sensing`, `cyber` map to domains Inon has not worked in. No honest CV edit closes these. The ATS Match dashboard is doing its job: surfacing a real fit gap.

### Prevention plan (per Rubric)
- **Why the gap happened:** v1 CVs were written to convey Inon's experience in *his* vocabulary, before the ATS Match engine existed to measure literal JD-term overlap. No measurement loop existed at v1 authoring time.
- **Prevention:** From now on, every tailored CV gets scored against its JD with `computeAtsMatch` *before* delivery, and the gap list is triaged into (a) honestly integrable — integrate, (b) un-integrable — document with reason. This becomes a step in Cole's CV Tailoring Playbook alongside the existing mandatory ATS *format* check. Two gates now: format (parser-readable) + match (vocabulary-aligned).

---

## Success criteria — status

- [x] v2 of both CVs created; v1 untouched (v1 .html files unchanged, v1 .pdf preserved)
- [x] Target keywords honestly integrated where genuine, OR explicitly documented as un-integrable with reason (artillery / c4i / smart sensing / cyber — documented above)
- [x] Both v2 CVs PASS `ats_format_check.py` (exit 0, 5 pass / 1 warn / 0 fail; warn accepted with rationale)
- [x] Measurable keyword improvement: SysEng +9 pts (39→48%), TechPM +9 pts (42→51%); raw keyword counts reported
- [x] Zero fabricated experience — every new keyword traces to genuine TouchE / consulting / Arena Plus / IAF background
- [x] v1 strengths preserved — 9 permanent CV rules honored (no location, reverse-chron order, no "C4I" label, military section kept & not over-labelled, no hyperbolic claims, education present, "clients" not "countries", builder work included, one-page constraint maintained — no content added beyond existing page bounds)

## Not done (per brief)
- No git commit. Andy commits after Jasmin QA.

## Recommendation to Andy
1. Route both v2 CVs to Jasmin for QA sign-off (re-run her engine + spot-check honesty).
2. Surface the **Rule #3 / "C4I"** question to Inon — it is the one lever that could lift both scores further, but only he can decide whether to relax it for defense-sector applications. I will not override a permanent rule.
3. Set expectation with Inon: 48% / 51% are *honest* scores. The remaining gap is real domain vocabulary (artillery, sensing, cyber) he genuinely lacks — that is signal about role fit, not a CV defect.

— Cole
