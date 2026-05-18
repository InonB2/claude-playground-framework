# SOP: Agent Domain Boundaries

**File Path:** `/BKM/sop_agent_domain_boundaries.md`
**Authority:** Andy (Orchestrator)
**Version:** 1.0 — 2026-05-18

---

## Purpose

This document is Andy's dispatch reference when a task touches the boundary between two agents with overlapping specializations. Each section defines exclusive ownership, explicit exclusions, and the escalation rule that moves work from one agent to the other.

**Rule of thumb:** If in doubt, dispatch to the agent listed first in each section. Only escalate when the trigger condition is met.

---

## 1. Quinn vs Jasmin — Logic/Content QA vs Security/Architecture QA

| What Quinn owns | What Jasmin owns |
|---|---|
| Python/Bash script logic review | TypeScript / Node application code review |
| SQL migration logic and rollback safety | Auth flows, token handling, access control |
| RLS policy structural correctness (syntax, clause correctness) | RLS policy access-control correctness (exploitability, privilege) |
| Automation output validation | Security vulnerabilities in any code |
| Content accuracy — CVs, proposals, copy | Architecture decisions (coupling, modularity, API contracts) |
| CI YAML step logic (non-security) | PII exposure and injection risk |
| Factual claim verification in documents | Deployment gating — final sign-off before production |

**Not Quinn's domain:** Any script, migration, or config touching secrets, user data access, privilege escalation, or cryptographic operations.

**Not Jasmin's domain:** Script output correctness, content accuracy, migration rollback logic, CI step ordering where no secrets are involved.

**Escalation rule:** Quinn reviews first. If Quinn encounters credentials, user data access, privilege escalation, or secret handling anywhere in the deliverable — stop, flag in the review file, and escalate to Jasmin before writing `LOGIC APPROVED`. Jasmin is not the default CV reviewer; Quinn is.

---

## 2. Cole vs Sage — Writing/CVs vs LinkedIn/Brand

| What Cole owns | What Sage owns |
|---|---|
| CVs — tailoring, formatting, ATS compliance | LinkedIn posts — thought leadership, project showcases |
| Cover letters — personalized, company-specific | LinkedIn profile copy — About section, headline, banner |
| Website hero copy and body copy | Content calendar planning and cadence strategy |
| Cold email outreach to hiring managers | LinkedIn engagement strategy and algorithm optimization |
| Consulting proposals — value-led, outcome-focused | Personal brand positioning and audience targeting |
| ATS format checking and keyword alignment | LinkedIn-native content (no links, no external attribution) |

**Not Cole's domain:** LinkedIn post drafting, content calendar, algorithm-aware format choices for LinkedIn, brand growth strategy.

**Not Sage's domain:** CV production, ATS compliance, cover letter writing, website body copy, proposal writing.

**Escalation rule:** If a request involves LinkedIn as the publication channel, it goes to Sage. If it involves a document delivered to a recruiter, employer, or client (CV, cover letter, proposal), it goes to Cole. The channel determines the agent. Edge case — LinkedIn About section rewrite: Sage drafts it; Cole reviews for voice consistency with the CV if both assets are being updated in the same session.

---

## 3. Mack vs Yoni — Automation Scripts/Integrations vs Application Code

| What Mack owns | What Yoni owns |
|---|---|
| Webhooks — inbound and outbound | Backend application code — APIs, services, business logic |
| OAuth flows and API credential management | Data models and backend schema interactions |
| Telegram bot scripts | REST/GraphQL endpoint implementation |
| GitHub sync automation (PowerShell scripts) | Unit-testable backend modules |
| MCP server wiring and inter-system bridges | Architectural decisions on backend coupling and structure |
| Rate-limit watchdog and notification scripts | Node/Express/Fastify application layer |
| Integration glue scripts (Python/Bash pipelines) | Backend TypeScript — strict-mode, typed modules |

**Not Mack's domain:** Application layer logic, data models, REST endpoint design, backend architecture. Mack builds the pipe; Yoni builds what the pipe connects to.

**Not Yoni's domain:** Webhook handlers, OAuth flows, bot scripts, GitHub sync, MCP wiring, third-party API integration scripts. Yoni builds the application; Mack wires it to the outside world.

**Escalation rule:** If the primary output is a script that moves data between two external systems or triggers an action via an API, it is Mack's work. If the primary output is application logic that processes data internally or exposes an API endpoint, it is Yoni's work. When a task spans both (e.g., a webhook that calls internal application logic), dispatch Mack for the integration layer and Yoni for the application layer — coordinate file ownership before both start.

---

## 4. Rex vs Yoni — Web Frontend/Dashboard vs Backend Application Code

| What Rex owns | What Yoni owns |
|---|---|
| React/TypeScript frontend components | Backend APIs consumed by the frontend |
| Dashboard UI, tabs, visual layout | Business logic powering the dashboard data |
| SEO, accessibility (WCAG), performance | Data models and database queries |
| Base44 application-layer implementation | Node/Express/Fastify server code |
| Frontend state management | Backend authentication and authorization |
| Responsive layout and design-system compliance | REST/GraphQL schema and endpoint contracts |
| ESLint/TypeScript strict compliance on frontend | Backend unit tests and integration tests |

**Not Rex's domain:** Backend APIs, data models, server logic, database queries. Rex implements the view; Yoni implements what the view consumes.

**Not Yoni's domain:** React components, frontend layout, CSS/design-system tokens, SEO tags, accessibility attributes, Base44 platform code. Yoni implements the backend; Rex implements the interface.

**Escalation rule:** The primary question is where the change lives in the stack. Frontend component or UI behavior → Rex. Backend data, logic, or API contract → Yoni. When a bug spans both layers (e.g., data arrives incorrectly shaped at the frontend), dispatch Yoni to fix the API response first, then Rex to consume the corrected shape. Never have both editing the same file simultaneously.

---

## 5. Maya vs Jasmin — Security Audit vs Code/Logic Review

| What Maya owns | What Jasmin owns |
|---|---|
| OWASP Top 10 audit against live web applications | Code-level security review (source code, not live site) |
| HTTP header analysis (CSP, HSTS, X-Frame-Options) | Auth flow correctness in code |
| PII exposure in page source, HTML, JS bundles | Logic correctness in TypeScript/Node code |
| Cookie flag audits (Secure, HttpOnly, SameSite) | RLS access-control correctness |
| Third-party script origin analysis | Injection risk identification in source |
| Form CSRF token presence and input validation (observable) | Architecture and coupling review |
| Information disclosure via client-observable signals | Deployment gating — `READY FOR DEPLOY` sign-off |

**Not Maya's domain:** Source code review, backend logic, deployment decisions. Maya audits the running application from the outside; she never touches the codebase.

**Not Jasmin's domain:** Live-site HTTP header inspection, OWASP checklist against URLs, cookie flag auditing, PII in rendered HTML. Jasmin reviews code; Maya reviews the deployed surface.

**Escalation rule:** Maya runs first on any new web application before Rex begins remediation. Maya produces a findings report; Rex remediates; Jasmin reviews the remediated code. If Maya's audit surfaces a finding that requires source code inspection to confirm (e.g., a suspected injection vector), Maya notes it as "Unconfirmed — requires developer verification" and escalates to Jasmin for source-level review.

---

## 6. Rio vs Yoni — Mobile/React Native vs Backend/Node

| What Rio owns | What Yoni owns |
|---|---|
| `apps/mobile/` — entire React Native / Expo package | `apps/api/` — entire Node/Express/Fastify backend package |
| Mobile UI components, screens, navigation | REST/GraphQL API endpoints and backend services |
| Device feature integration (camera, ARKit, permissions) | Backend business logic and data processing |
| Expo config (`app.json`, `eas.json`) in mobile package | Backend TypeScript — server-side strict-mode modules |
| Mobile-side Supabase client reads | Supabase edge functions and server-side DB logic |
| React Navigation, gesture handling, Reanimated | Authentication, authorization, session management |
| Mobile performance (FlatList, memoization, Hermes) | Backend unit and integration tests |

**Shared boundary — negotiate before touching:**
- `packages/ui/` (shared UI library) — ownership unresolved; confirm with Andy before either agent edits it
- `packages/types/` or `packages/shared/` — both agents post a coordination note to `/scratchpad/file_ownership_[date].md` and confirm with Andy before editing

**Not Rio's domain:** `apps/api/`, `supabase/`, `packages/shared/` backend code, GitHub Actions CI files, any file Yoni is actively editing in the current session.

**Not Yoni's domain:** `apps/mobile/`, React Native components, Expo config, mobile UI, device feature code, mobile-specific navigation.

**Escalation rule:** Package path determines ownership. `apps/mobile/` → Rio. `apps/api/` → Yoni. Any shared package triggers mandatory coordination before either agent writes a line. When a feature requires both mobile and backend work (e.g., a new API endpoint consumed by a new mobile screen), dispatch Yoni for the backend first, then Rio for the mobile implementation once the API contract is confirmed. Sequential dispatch — never concurrent on shared packages.
