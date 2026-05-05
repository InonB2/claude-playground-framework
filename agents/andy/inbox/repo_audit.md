# GitHub Repository Audit — InonB2 (Corrected, Full)
**Audited by:** Tomy (Research Agent)  
**Date:** 2026-05-02  
**Method:** Authenticated GitHub API (`type=all`, `per_page=100`)  
**Previous audit status:** INCORRECT — only captured 4 public repos via unauthenticated call

---

## Summary

| Metric | Count |
|--------|-------|
| Total InonB2 repos | **11** |
| Public | 3 |
| Private | 8 |
| Org repos (excluded) | 1 (`code50/180543788` — CS50 course auto-repo) |

The previous audit (4 repos) was incomplete. An unauthenticated API call only returns public repos. Authenticated call reveals all 11.

---

## Full Repo Table

| # | Repo Name | Visibility | Last Push | Language | Description |
|---|-----------|-----------|-----------|----------|-------------|
| 1 | `claude-playground-framework` | **public** | 2026-05-02 | Python | Claude AI Agent Framework — automated agents, CV archive, workflow automation |
| 2 | `desktop-tutorial` | **private** | 2024-09-05 | — | GitHub Desktop tutorial repository (auto-generated onboarding) |
| 3 | `family-flow-he` | **private** | 2026-04-30 | TypeScript | Hebrew-locale FamilyFlow variant |
| 4 | `FamilyFlow` | **private** | 2026-03-25 | — | Personal family chore repository |
| 5 | `inon-baasov-cv-career` | **private** | 2026-05-02 | — | CV drafts, templates, JD analysis, career architecture |
| 6 | `inon-baasov-website` | **public** | 2026-05-02 | JavaScript | Portfolio website — inon-baasov-website.base44.app (**LIVE SITE**) |
| 7 | `inon-baasov-website-base44` | **private** | 2026-05-01 | JavaScript | Base44 App: Inon Baasov Portfolio |
| 8 | `pro-maker-ar` | **private** | 2026-05-01 | TypeScript | BuildARPro / ProMaker AR app (created 2025-01-26; 1 star) |
| 9 | `project-launchpad` | **private** | 2026-05-01 | TypeScript | (no description) |
| 10 | `trademetrics` | **private** | 2026-05-02 | JavaScript | Base44 App: TradeMetrics |
| 11 | `website-product-portfolio` | **public** | 2026-05-01 | JavaScript | Inon Baasov — Personal Portfolio Website (homepage: https://inon-baasov-website.base44.app) |

---

## Key Findings

### 1. Live portfolio site (`inon-baasov-website.base44.app`)

Two repos reference this URL:

- **`inon-baasov-website`** (public) — description explicitly states "Portfolio website — inon-baasov-website.base44.app". Last pushed 2026-05-02. **Owner confirmed this is the live site.**
- **`website-product-portfolio`** (public) — `homepage` field set to `https://inon-baasov-website.base44.app`. Last pushed 2026-05-01.

**Correction to previous audit:** `inon-baasov-website` was wrongly flagged as a duplicate/archive candidate. Owner confirmed it IS the live site. Do NOT archive it.

The relationship between the two repos needs owner clarification — both reference the same live URL. `inon-baasov-website-base44` (private) is likely the Base44 platform backend config for the same site.

### 2. BuildARPro / ProMaker repo

**Found: `pro-maker-ar`** (PRIVATE)  
- Created: 2025-01-26  
- Last push: 2026-05-01  
- Language: TypeScript  
- 1 star  
- Active development — do not archive.

The previous audit conclusion ("no dedicated BuildARPro repo found") was wrong — the repo was invisible because it is private.

### 3. Private repos (all 8)

| Repo | Activity | Notes |
|------|----------|-------|
| `desktop-tutorial` | Stale (2024-09-05) | GitHub Desktop auto-generated tutorial. Zero value. Safe to archive. |
| `FamilyFlow` | Low (2026-03-25) | Likely superseded by `family-flow-he`. Verify before archiving. |
| `family-flow-he` | Active (2026-04-30) | Hebrew variant, TypeScript — active development. |
| `inon-baasov-cv-career` | Active (2026-05-02) | CV/career materials. Contains PII — keep private. |
| `inon-baasov-website-base44` | Active (2026-05-01) | Base44 platform config for portfolio. Do not archive. |
| `pro-maker-ar` | Active (2026-05-01) | BuildARPro/ProMaker AR — active. |
| `project-launchpad` | Active (2026-05-01) | Recently active — do not archive without owner review. |
| `trademetrics` | Active (2026-05-02) | TradeMetrics app — active. |

### 4. Safe to archive

| Repo | Reason |
|------|--------|
| `desktop-tutorial` | GitHub Desktop onboarding auto-repo from Sep 2024. Never meaningfully used. Safe to delete or archive. |
| `FamilyFlow` | Appears superseded by `family-flow-he`. Confirm with owner before archiving. |

---

## Corrections to Previous Audit

| Previous finding | Corrected finding |
|-----------------|------------------|
| Only 4 repos found | 11 repos exist (8 private, 3 public) |
| `inon-baasov-website` flagged as duplicate — archive candidate | INCORRECT. Owner confirmed it is the live site. Do NOT archive. |
| "No BuildARPro/ProMaker repo found" | INCORRECT. `pro-maker-ar` (private) exists, created 2025-01-26, actively maintained. |
| TradeMetrics, FamilyFlow, project-launchpad "not present as standalone repos" | INCORRECT. All three exist as private repos. |

---

## Org Repo (Not counted in InonB2 total)

| Repo | Owner | Notes |
|------|-------|-------|
| `180543788` | `code50` (org) | CS50 Harvard course auto-repo — not directly owned by InonB2. Ignore. |
