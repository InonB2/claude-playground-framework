# Agent Roster

> **Andy must read this file first before delegating any task.**  
> Last updated: 2026-05-18 | v2.5 — Rio and Quinn added (18 agents)

| Name   | Title                      | Role                         | Specialty                                              | Status  |
|--------|----------------------------|------------------------------|--------------------------------------------------------|---------|
| Andy   | The Orchestrator           | Strategic Manager            | Task decomposition, delegation, pipeline management    | Active  |
| Tomy   | The Researcher             | Information Gatherer         | Documentation, API exploration, tech stack analysis    | Active  |
| Yoni   | The Lead Coder             | Senior Software Engineer     | Implementation, unit testing, modular architecture     | Active  |
| Jasmin | The Reviewer               | Security & Logic Auditor     | Bug detection, security review, deployment gating      | Active  |
| Pat    | The HR Researcher          | Talent Acquisition Analyst   | Agent capability profiling, role blueprint design      | Active  |
| Nolan  | The HR Agent               | Agent Creator & Integrator   | Agent onboarding, roster management, system integration| Active  |
| Maya   | The Web Security Auditor   | Application Security Analyst | OWASP audits, header analysis, PII exposure, CWE refs  | Active  |
| Lena   | The UI/UX Designer         | Senior UI/UX Designer        | Design systems, portfolio UX, visual redesign, WCAG    | Active  |
| Rex    | The Web Developer          | Senior Frontend Developer    | React/TS, SEO, accessibility, performance, Base44      | Active  |
| Mack   | The Automation Engineer    | Automation & API Specialist  | Webhooks, OAuth, Telegram bot, GitHub sync, MCP wiring | Active  |
| Sage   | The LinkedIn Strategist    | Personal Brand Specialist    | LinkedIn growth, thought leadership, CPO brand content | Active  |
| Cole   | The Conversion Copywriter  | Senior Copywriter            | CVs, cover letters, website copy, proposals            | Active  |
| Silas  | The Database Architect     | Data Systems Engineer        | SQLite/Supabase schemas, RLS, pgvector, migrations     | Active  |
| Vera   | The QA Inspector           | QA & Accessibility Auditor   | Responsive QA, WCAG 2.1, visual regression, Lighthouse | Active  |
| Dev    | The DevOps & Cloud Engineer| DevOps & Infrastructure Spec.| CI/CD pipelines, Supabase branching, Railway/EAS/Vercel | Active  |
| Finn   | The Infrastructure Triage Engineer | Infrastructure Triage Specialist | MCP health, bot recovery, env var audits, service restart | Active  |
| Rio    | The Mobile Engineer                | Mobile Software Engineer         | React Native / Expo / mobile UI / device testing / TypeScript | Active  |
| Quinn  | The Logic & Content Reviewer       | QA Reviewer — Logic, Scripts & Content | Python script review / SQL migrations / content accuracy / automation validation / CI config review | Active  |

## Adding New Agents
New rows must be added by **Nolan** only, after **Pat** has submitted a Candidate Profile Brief to `/scratchpad/`.

---

## Delegation Map

```
Owner / team_inbox
       │
       ▼
     Andy  ──────────────────────────────────────────────┐
       │                                                  │
       ├──► Tomy (Research)                               │
       │       ├──► Yoni (General Code)                   │
       │       │       └──► Jasmin (Review)               │
       │       │                └──► owner_inbox          │
       │       ├──► Rio (Mobile / React Native)           │
       │       │       ├──► Vera (UI QA → QA APPROVED)    │
       │       │       └──► Jasmin (Logic QA → READY FOR DEPLOY) │
       │       │                └──► owner_inbox          │
       │       └──► Web Pipeline:                         │
       │             Tomy → Maya (Security Audit)         │
       │             Tomy → Lena (Design Brief)           │
       │             Maya + Lena → Rex (Implementation)   │
       │                    └──► Jasmin (Review)          │
       │                             └──► owner_inbox     │
       ├──► Mack / Silas / Cole / Dev (specialist work)   │
       │       └──► Quinn (Logic & Content QA)            │
       │               ├──► LOGIC APPROVED → owner_inbox  │
       │               └──► Security flag → Jasmin        │
       └──► Pat (Profile) ──► Nolan (Deploy agent) ───────┘
```
