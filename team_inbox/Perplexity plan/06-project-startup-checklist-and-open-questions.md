# BuildAR — Startup Checklist, Open Questions, and Additional Information

## Purpose

This file captures everything else needed to start the project cleanly: startup checklist, risk list, open decisions, and recommended defaults.

---

## Startup checklist

### Business and product
- Confirm phase 0–1 scope.
- Confirm first 2–5 seed projects.
- Confirm success definition for the first demo.

### Infrastructure
- Create GitHub repo.
- Create Supabase project.
- Decide preview and persistent branch strategy in Supabase.[web:71][web:72]
- Prepare Anthropic API key.
- Decide hosting targets for web, API, orchestrator, and mobile CI.

### Engineering
- Confirm monorepo standard.
- Confirm TypeScript everywhere.
- Confirm shared type package.
- Confirm migration-first schema policy.

### Product ops
- Decide who reviews content quality.
- Decide who approves publish status.
- Decide whether all seed projects are internal-only initially.

---

## Recommended defaults

If you want the cleanest start, use these defaults:

- PNPM monorepo
- Supabase for DB/Auth/Storage
- preview and persistent branching in Supabase for safe schema testing.[web:71][web:86]
- React Native mobile shell with AR abstraction
- Claude orchestrator with prompt caching hooks for repeated project context.[web:80][web:94]
- internal CMS first, not creator platform first

---

## Main project risks

### Risk 1 — Scope creep
The project naturally invites expansion into creator tools, B2B, computer vision, and hardware surfaces too early.

### Risk 2 — Contract drift
If Lovable and Claude build against different assumptions, rework cost will rise quickly.

### Risk 3 — AR blocking the loop
If advanced AR becomes a gate, the team can lose weeks without validating user value.

### Risk 4 — Orchestrator cost/latency
Without caching and prompt discipline, repeated contextual assistant calls may become slower and more expensive than necessary.[web:80][web:94][web:96]

### Risk 5 — Environment instability
Without branching and preview-safe workflows, schema changes can destabilize active development.[web:71][web:72]

---

## Open questions you should answer before build starts fully

These are the only important unresolved questions that should be answered now rather than guessed later:

1. **Mobile path:** Do you want Expo-managed as the initial path, or do you already expect native eject/custom modules from the beginning?
2. **Web data access:** Should the CMS use direct server-side Supabase access, or should everything go through your internal API layer?
3. **Deployment topology:** Do you want `/api` and `/orchestrator` as separate deployables, or one backend service with clear internal modules?
4. **Language requirement:** Is Hebrew required in the first usable internal CMS release, or only architecture support for RTL/i18n?
5. **Seed library:** Which exact 2–5 projects should be the first seed set?
6. **Publishing model:** Who is allowed to publish project changes initially?

These questions are small enough to answer now and important enough that agents should not guess them.

---

## Recommended first-demo definition

The best first demo is:
- one authenticated user,
- one seeded project,
- one complete guided session,
- one contextual assistant question,
- one successful completion,
- visible event logging,
- and one CMS edit reflected in the app after content update.

---

## Final guidance

Do not optimize for breadth. Optimize for one demonstrably real loop with stable foundations.
