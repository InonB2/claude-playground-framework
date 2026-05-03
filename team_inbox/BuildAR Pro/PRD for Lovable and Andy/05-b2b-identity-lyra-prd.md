# B2B Integrations, Identity & Lyra Evolution PRD (For Lovable & Claude Agents)

## 1. Purpose and Audience

This PRD defines the **B2B/partner integration layer** and the **identity/credential evolution path** inspired by Lyra Protocol for the BuildAR platform.

Audience:
- AI agents (Lovable, Claude) implementing partner‑facing APIs, webhooks, and tenanting.
- Human engineers and PMs responsible for B2B deals and safety/compliance.

It builds on the backbone (`01-system-architecture-prd.md`) and orchestrator (`03-multi-agent-orchestrator-prd.md`).

---

## 2. Goals and Non‑Goals

### 2.1 Goals

1. Enable **retailers, OEMs, and platforms** to integrate BuildAR as:
   - Embedded project guidance (deep links / SDK / iframe).
   - API/whitelabel AR instruction service.
2. Introduce a **tenant/partner model** in Supabase and the API.
3. Define a **progressive identity and credential scheme** for:
   - Partners (tenants).
   - Creators.
   - Internal agents (BOM, Safety, Tutor, etc.).
4. Prepare for future **Lyra‑style DID/VC integration** without blocking MVP.

### 2.2 Non‑Goals

- Full decentralized identity (DID) implementation.
- Detailed legal/commercial contract terms.

---

## 3. Partner/Tenant Model

### 3.1 Concepts

- **Tenant (Partner):** an external organization (e.g., retailer, OEM, training provider) that uses BuildAR capabilities.
- **Partner Project:** a project that is scoped to a tenant and may reference their products.
- **Channel:** mode of integration (embedded app, API‑only, etc.).

### 3.2 Data Model (Supabase)

New tables:

#### 3.2.1 `tenants`

- `id` (uuid, pk)
- `slug` (text, unique)
- `name` (text)
- `status` (enum: 'active'|'inactive')
- `created_at`, `updated_at`

#### 3.2.2 `tenant_members`

- `id` (uuid, pk)
- `tenant_id` (uuid, fk → `tenants.id`)
- `profile_id` (uuid, fk → `profiles.id`)
- `role` (enum: 'tenant_admin'|'tenant_editor'|'tenant_viewer')
- `created_at`

#### 3.2.3 `partner_projects`

- `id` (uuid, pk)
- `tenant_id` (uuid, fk → `tenants.id`)
- `project_id` (uuid, fk → `projects.id`)
- `integration_channel` (text: 'embedded'|'api'|'whitelabel')
- `external_ref` (text, nullable) – ID in partner system.
- `status` (enum: 'active'|'paused')

Add columns to existing tables:
- `projects.tenant_id` (nullable) – null = global consumer project; non‑null = owned by tenant.

RLS:
- Ensure that tenant‑scoped resources are only visible/editable to tenant members or internal admins.

---

## 4. B2B Integration Patterns

### 4.1 Deep Link / Embedded Mode (Low‑Friction)

Use case: Partner wants to add "AR assembly guide" buttons next to specific products.

Pattern:
- Partner stores a mapping from their SKU to `partner_projects.external_ref`.
- When customer taps "Open AR Guide" on partner site or app, they open a deep link:

`buildar://project/<partner_project_id>?tenant=<tenant_slug>&session_source=<partner>`

On web/mobile:
- App resolves `partner_project_id` and tenant.
- Creates a `session` with metadata (`source='partner:<id>'`).

Requirements for AI agents:
- Implement deep link handling in mobile and web.
- Ensure tenant branding (logo, primary color) can be injected into UI based on `tenant_id`.

### 4.2 API‑Based Integration (Headless)

Use case: Partner wants to call BuildAR APIs directly to:
- Fetch project steps and BOM.
- Embed instructions in their own app.

Endpoints (example):

- `GET /api/v1/tenants/:tenantId/projects` – list tenant projects.
- `GET /api/v1/tenants/:tenantId/projects/:projectId` – details + steps + BOM.

Auth:
- Use **API keys** or OAuth2 client credentials per tenant.
- Keys mapped to `tenants.id` in a `tenant_api_keys` table:
  - `id`, `tenant_id`, `key_hash`, `label`, `created_at`, `revoked_at`.

RLS:
- API keys may bypass some user‑level RLS but must be constrained to their `tenant_id`.

### 4.3 Whitelabel / OEM Mode (Future)

Use case: Partner ships a branded version of BuildAR.

Requirements (future):
- Per‑tenant configuration for:
  - Logo, color palette.
  - Default language.
  - Feature flags.
- Ability to generate tenant‑specific client builds (not MVP).

---

## 5. Identity & Credentials Evolution (Lyra‑Inspired)

### 5.1 Phase 1 (MVP) – Centralized Identity

- Use existing `profiles` and `tenants` tables.
- Store `role` and `tenant_members` associations.
- For agents (BOM, Safety, Tutor), identity is implied by code; no external representation yet.

Logging:
- Orchestrator logs should record `tenant_id` (if any) with each call.

### 5.2 Phase 2 – Internal Agent Identity

Introduce a minimal `agents` table:

- `id` (uuid, pk)
- `name` (text)
- `capabilities` (jsonb)
- `status` (enum: 'active'|'inactive')

And `agent_runs` table:

- `id` (uuid, pk)
- `agent_id` (uuid, fk → `agents.id`)
- `session_id` (uuid, fk → `sessions.id`)
- `request` (jsonb)
- `response` (jsonb)
- `created_at`

Benefits:
- Basic audit trail for how each agent influences outputs.

### 5.3 Phase 3 – Lyra/DID Integration (Conceptual)

Design the schema to be compatible with future **DID (Decentralized Identifier)** and **Verifiable Credentials (VC)**:

Add optional fields:
- `profiles.did` (text, nullable).
- `tenants.did` (text, nullable).
- `agents.did` (text, nullable).

Introduce `credentials` table:

- `id` (uuid, pk)
- `subject_type` (enum: 'profile'|'tenant'|'agent')
- `subject_id` (uuid)
- `type` (text) – e.g., 'safety_reviewer', 'licensed_electrician'
- `issuer` (text)
- `issued_at`, `expires_at`
- `payload` (jsonb) – may mirror a VC structure.

At this stage, orchestrator can:
- Prefer or require certain credentials for safety‑critical projects.
- Expose credential metadata in internal tooling.

Implementation of actual DID/VC protocols is out of scope for MVP; design DB to be ready.

---

## 6. API Security Considerations

- All partner APIs must be **rate‑limited** per tenant.
- API keys must be stored hashed; never log raw keys.
- For Q&A/agent endpoints used by partners, ensure **system prompts** include tenant policies (e.g., allowed task types, disclaimers, language).
- Add a `tenant_policy` field (jsonb) on `tenants` for:
  - Allowed project categories.
  - Custom safety disclaimers.

---

## 7. Admin & Ops Tools

Extend the web app (`/apps/web`) with an **Admin > Tenants** section:

- List tenants, create/edit forms.
- Manage tenant members and roles.
- Generate/revoke tenant API keys.
- View basic usage stats per tenant (sessions, orchestrator calls, warnings).

---

## 8. Implementation Guidance for AI Agents

1. **Respect tenant scoping** in all new queries and endpoints.
2. Add type definitions for `Tenant`, `TenantMember`, `PartnerProject`, `Agent`, and `Credential` in `/packages/core-types`.
3. When adding orchestrator features, always pass along `tenant_id` from session.
4. For new endpoints, ensure auth middleware can handle both user tokens and tenant API keys.

---

## 9. Acceptance Criteria

B2B/identity layer is considered MVP‑ready when:

1. Tenants can be created and assigned admins via web UI.
2. Projects can be associated with tenants and consumed via tenant‑scoped APIs.
3. Mobile app can open tenant projects via deep links.
4. Orchestrator logs record tenant information.
5. Basic `agents` and `agent_runs` tables exist for auditing, even if only partially used.
