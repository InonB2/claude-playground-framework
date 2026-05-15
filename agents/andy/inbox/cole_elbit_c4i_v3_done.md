# Cole — Elbit CV C4I Integration (v3) — DONE

**Date:** 2026-05-14
**Agent:** Cole — Conversion Copywriter
**Trigger:** Inon relaxed CV Permanent Rule #3 on 2026-05-14 — "C4I" now PERMITTED for defense-sector roles where genuinely grounded. Follow-up to the v2 keyword fix.
**Principle applied:** Honesty over score, unchanged. C4I is now *unlocked* (was policy-blocked), but only `artillery`, `smart sensing`, `cyber` remain genuine experience gaps and stay OUT. C4I integrated only where it traces to real background.

---

## Summary of results

| CV | v2 score | v3 score | Δ | v2 matched | v3 matched | ATS format check |
|---|---:|---:|---:|---:|---:|---|
| ELBIT System Eng PM | 48% | **49%** | **+1 pt** | 146/290 | 149/290 | PASS (exit 0) |
| ELBIT Technical PM  | 51% | **52%** | **+1 pt** | 131/229 | 132/229 | PASS (exit 0) |

Scores from the real `computeAtsMatch` engine extracted from `dashboard/index.html`, run via a Node harness (DOMParser shimmed to strip script/style then tags → text; engine logic untouched). v2 baselines (48% / 51%) reproduce the prior report's numbers exactly.

Files created (v2 untouched — see note below):
- `owner_inbox/archive/cv_archive/ELBIT-SystemEng-PM-Netanya/v3_Inon_Baasov_CV_SystemEngPM.html`
- `owner_inbox/archive/cv_archive/20248_TechnicalPM_Elbit_Netanya/v3_Inon_Baasov_CV_TechnicalPM.html`

---

## CV 1 — ELBIT System Engineer PM (v3) — C4I integrated

This is a defense-sector role (group: "Artillery C4I system"). C4I permitted per relaxed Rule #3. Inon's IAF Planning & Control role (2000–2003) is a command-and-control environment — legitimate C4I-adjacent grounding per Rules 3 & 4.

### Exactly where/how C4I was placed (5 instances, all genuine)

| Location | Before (v2) | After (v3) |
|---|---|---|
| Header title line | `… \| Defense Domain` | `… \| Defense / C4I Domain` |
| Summary (closing sentence) | "Defense-domain background in a mission-critical operational environment (Israeli Air Force)." | "**C4I** / defense-domain background in a mission-critical operational environment, gained in the **Israeli Air Force** Planning & Control Department — a command-and-control setting." |
| Key Skills line | "… Operational Environments …" | "… **C4I & Operational Environments** …" |
| Military Service — role title | "Israeli Air Force — Planning and Control Department" | "Israeli Air Force — Planning and Control Department **(C4I)**" — the Rule 4 label, now permitted for defense roles |
| Military Service — bullet | "… in a mission-critical environment …" | "… in a mission-critical **C4I** environment …" |

No new bullets, no new sections — only relabelling of existing genuine content. One-page constraint unaffected. All 9 permanent CV rules honored (reverse-chron order intact, no location in header, education present, military section kept & now correctly labelled per relaxed Rule 4, builder work retained, no hyperbolic claims, "clients" not "countries").

### Score effect
- v2 → v3: **48% → 49% (+1 pt)**, matched 146 → 149 / 290.
- `c4i` and `c4i system` **dropped out of the gap list** — now matched (grep-confirmed: C4I appears 5× in v3).
- Remaining top gap: `artillery`, `artillery c4i`, `artillery c4i system` — all blocked by the `artillery` token. **Inon has zero artillery background** (IAF service was Planning & Control, not artillery systems/doctrine). Forcing "artillery" would be fabrication — correctly NOT done. The bigrams/trigrams containing C4I still don't match purely because the `artillery` half is genuinely absent.

**Honest finding:** the modest +1 pt is expected and correct. C4I was only 4 distinct JD keyword forms, three of which (`artillery c4i`, `artillery c4i system`) are still gated by the un-fabricable `artillery` term. The lift from C4I alone is real but small — the artillery experience gap is the true score ceiling, and that is legitimate role-fit signal, not a CV defect.

---

## CV 2 — ELBIT Technical PM (Job 20248) — judgment call: v3 PRODUCED

**The brief asked me to judge whether C4I genuinely fits here. It does — I produced a v3.**

Reasoning:
- The JD group line is **"Smart Sensing Group, C4I and Cyber"** and the description states the role joins "the Smart Sensing Group **in C4I and Cyber**." So "C4I" is literally in this JD — as the division/org context.
- This is a defense-sector role (Elbit). Per relaxed Rule #3, C4I "MAY be used as a label where genuinely grounded." Inon's IAF Planning & Control C4I-adjacent background is the *same* genuine grounding that justifies it on the SysEng CV — it does not stop being true just because the JD's headline domain is sensing.
- **Distinction held:** `smart sensing` and `cyber` remain genuine domain gaps — Inon has no sensing-hardware or cybersecurity background — so those stayed OUT (no fabrication). Only `c4i`, which is grounded, was integrated. This is exactly the "don't force it" discipline the brief asked for, applied at the keyword level: C4I fits, smart sensing/cyber do not.

### Where C4I was placed in TechPM v3 (4 instances, all genuine)
| Location | After (v3) |
|---|---|
| Header title line | "Technical Project Manager \| System Engineering \| **Defense / C4I**" |
| Summary | "Defense-domain background in a mission-critical **C4I** environment — Israeli Air Force Planning & Control (command-and-control) …" |
| Military Service — role title | "Israeli Air Force — Planning and Control Department **(C4I)**" |
| Military Service — bullet | "Command & Control (**C4I**) operations: managed a 27-soldier roster …" |
| Skills chip | "Defense Domain" → "**Defense / C4I Domain**" |

### Score effect
- v2 → v3: **51% → 52% (+1 pt)**, matched 131 → 132 / 229.
- Standalone `c4i` token **dropped out of the gap list** — now matched.
- Remaining top gap: `smart sensing`, `sensing`, `cyber`, `c4i and cyber`. The `c4i and cyber` trigram still doesn't match because `cyber` is a genuine gap — correctly not fabricated.

---

## Verification evidence

### ATS format check (mandatory pre-delivery gate)
Both v3 files: `python scripts/ats_format_check.py <path>` → **5 pass, 1 warn, 0 fail — FINAL VERDICT: PASS — exit 0.**
- The one WARN on both: `.skills-grid` uses `display:flex`. **Decision: accepted with rationale** — identical to v1/v2. The flex container holds short skill *chips* (a wrapping tag list), not side-by-side body paragraphs/sections; ATS parsers read it as an inline list. No change needed; v1 and v2 shipped with the same construct.

### Score (ATS Match engine)
```
ELBIT System Eng PM   48% -> 49%   (+1 pt)   matched 146 -> 149 / 290
ELBIT Technical PM    51% -> 52%   (+1 pt)   matched 131 -> 132 / 229
```
v2 baselines reproduced exactly, confirming harness fidelity. C4I grep-confirmed present in both v3 files (SysEng 5×, TechPM 4×); `c4i` removed from both gap lists.

### v2 untouched — note for Andy
`git status` shows `v2_Inon_Baasov_CV_SystemEngPM.html` as modified — **this is a pre-existing change from prior work, NOT from this session.** It was already `M` in the working-tree snapshot at session start. I made zero edits to either v2 file; every edit this session targeted the v3 copies. The v2 diff (Operational Doctrine→Environments wording, a military-bullet reword) predates this task. v2 SysEng and v2 TechPM content is exactly as it was when this task was dispatched.

---

## Findings — Infrastructure vs Design (per Team Quality Rubric)

### Infrastructure
- **No infrastructure defects.** Both v3 CVs are single static HTML files, no deps, no build. ATS format checker runs clean (exit 0) on both.
- **Re-flagging the prior recommendation:** the dashboard `computeAtsMatch` engine is browser-coupled (`DOMParser`). I again used a throwaway Node harness with a DOMParser shim and again it reproduced engine output exactly. **Recommend** Andy commission a permanent `scripts/ats_score.cjs` so any agent (and QA) can re-score a CV without opening the dashboard or rebuilding a shim each time. This is the second session it's been needed.

### Design
- **The Rule #3 relaxation worked as intended but is not a large lever.** v2's prior report named Rule #3 as "the one lever that could lift both scores further." Now relaxed, it delivered +1 pt each. That is honest and correct: C4I was a small share of JD keyword weight, and its highest-weight forms (`artillery c4i system`, `c4i and cyber`) are *compound* terms still gated by un-fabricable tokens (`artillery`, `cyber`). The lesson: relaxing a policy unlocks only the keywords that were *purely* policy-blocked — it cannot unlock keywords that were *also* experience-blocked.
- **The real ceilings are unchanged and legitimate:** `artillery` (SysEng), `smart sensing` + `cyber` (TechPM) map to domains Inon has not worked in. No honest edit closes these. 49% / 52% are the honest ceilings for the current background.

### Prevention plan (per Rubric)
- **Why the lift was smaller than the prior report implied:** the v2 report estimated the C4I/Rule-3 lever optimistically without modelling that C4I's heaviest JD forms are bigrams/trigrams co-bound to artillery/cyber. The scoring engine weights n-grams, and a partial match on a compound term scores nothing unless the *other* token also lands.
- **Prevention:** when triaging a JD gap list, classify each gap term by its **blocker type** before estimating lift — (a) policy-blocked only → fully unlockable, (b) experience-blocked → never unlockable honestly, (c) compound term mixing both → only the standalone form unlocks. Report expected lift against (a) and (c-standalone) only. This goes into Cole's CV Tailoring Playbook alongside the existing two gates (format check + match score).

---

## Success criteria — status

- [x] v3 SysEng CV created with C4I honestly integrated (5 instances, all traceable to IAF C4I-adjacent service)
- [x] v3 SysEng PASSES `ats_format_check.py` — exit 0 (5 pass / 1 warn / 0 fail; warn accepted with rationale)
- [x] Measurable ATS Match lift vs v2: SysEng 48% → 49% (+1 pt); `c4i` removed from gap list, grep-confirmed present 5×
- [x] Zero fabrication — `artillery`, `smart sensing`, `cyber` remain genuine gaps and were NOT added
- [x] v2 files untouched — no edits made to either v2 this session (pre-existing v2 SysEng diff predates this task)
- [x] TechPM judgment call made and executed — C4I genuinely fits (JD names the "C4I and Cyber" division; same IAF grounding applies), so v3 produced: 51% → 52% (+1 pt). smart sensing/cyber correctly left out.

## Not done (per brief)
- No git commit. Andy commits after Jasmin QA.

## Recommendation to Andy
1. Route both v3 CVs to Jasmin for QA sign-off (re-run her engine + spot-check that C4I placements are honest and that no artillery/sensing/cyber fabrication crept in).
2. Set expectation with Inon: the Rule #3 relaxation gave +1 pt on each CV — modest but honest. It was never going to be large, because the heaviest C4I keyword forms in these JDs are compound terms still gated by genuine experience gaps (artillery, cyber). 49% / 52% are honest ceilings.
3. Commission a permanent `scripts/ats_score.cjs` (second session this has been needed) so QA and agents can re-score without the dashboard.

— Cole
