# Yoni — BuildAR Pro Sprint 1 Wave 2 (Mobile Shell + MINOR-1 fix)

**From:** Andy
**Dispatched:** 2026-05-17
**Tasks:** BUILDAR-S1-011 (Mobile shell — RN + ViroReact, 5 screens) + MINOR-1 hotfix (projects.ts PostgREST sanitization)
**Model:** Opus 4.7
**Testers:** Vera (UI/UX/a11y per Lena's brief) + Jasmin (orchestrator integration, telemetry, AR fallback logic)

**Prior wave QA:** Jasmin signed off Wave 1 (BUILDAR-S1-008 + S1-009) with PASS WITH NOTES — 0 blockers, 0 majors, 4 minors, 2 nits. Wave 3 (mobile) is GREEN. Full report: `agents/andy/inbox/jasmin_s1_s2_qa.md`.

---

## Why this matters

Mobile shell is the LAST major piece for Gate B. Once this lands and QA-passes, a user can: sign in → browse projects → start a session → walk through steps with AR (or fallback) → ask the assistant mid-step → complete session → see telemetry rows. That closes Gate B.

You already shipped:
- 4 REST routes (`GET /projects`, `GET /projects/:id`, `POST /sessions`, `PATCH /sessions/:id`) in S1-006
- POST /api/v1/orchestrator/assist + ai-client (Tutor + Safety) in S1-008
- Telemetry helper + 6 recordEvent call sites in S1-009

Mobile shell consumes all of that.

---

## BUILDAR-S1-011 — Mobile Shell

### Stack (non-negotiable per Perplexity plan)

- **Bare React Native** (NOT Expo Go). Use `expo prebuild` flow if you want config-plugin ergonomics — ViroReact requires this because it has native dependencies that Expo Go cannot host.
- **ViroReact** as the AR abstraction layer (v2.54.0 or latest stable). Use the Expo config plugin for ViroReact.
- **React Navigation v6** for stack navigation.
- **Supabase JS client** (`@supabase/supabase-js`) for auth + data access. Same Supabase project (xbfgohafudrfygztqmtg) — anon key only, never service role.
- **react-native-vector-icons** with MaterialCommunityIcons (per Lena's icon set decision).
- **TypeScript strict mode** — same discipline as the other apps.

### Where it lives

`D:\BuildAR\apps\mobile\` — the workspace is already reserved in `pnpm-workspace.yaml`. Scaffold inside.

### Lena's UX brief — your source of truth

Read `D:\Claude Playground\owner_inbox\design\buildar_mobile_ux_brief.md` END TO END before writing any code. It defines all 5 screens at component-level fidelity:
1. Sign-in / Sign-up
2. Home / Project List (with resume banner)
3. Project Detail
4. Session / Step View (with AR area + AI floating action button + bottom sheet)
5. Session Completion

Design tokens she specifies (do not deviate):
- **Primary color:** `#FF6B2B` (construction-orange)
- **Text:** `#1A1A1A` near-black
- **Background:** `#F5F5F0` warm off-white
- **Font stack:** System (San Francisco / Roboto — no custom fonts in Phase 0-1)
- **Spacing:** 8px grid (8/16/24/32/48/64 only)
- **Touch targets:** minimum 44x44pt
- **RTL:** use logical CSS properties (inline-start/inline-end), not left/right

### Critical screens — implementation discipline

**Screen 4 (Session/Step View) is the heart of the app.** Spend the most care here:
- AR view: when ViroReact native modules are available AND the device has AR capability, render the AR view. When not (Android emulator, devices without AR, ViroReact init failure), render the fallback rectangle with "AR unavailable" label. The fallback MUST look intentional, not broken.
- "Ask AI" floating action button → bottom sheet with text input + last response display. Calls `POST /api/v1/orchestrator/assist` with `session_id`, `step_id` (UUID), `question`. Renders response. If Safety returns `blocked: true`, show the `reason` field in the sheet instead of the response — DO NOT hide that the assistant blocked the query.
- Step progression: tap "Next" → PATCH `/sessions/:id` with `current_step_index: next`. Tap "Complete" on last step → PATCH with `status: completed`. Telemetry rows will write automatically via the routes you built in S1-009.
- Step transition animation: 150ms opacity fade between content. Do NOT slide (Lena's brief: disorienting mid-task).

**Screen 1 (Sign-in):** Email + password only. No social, no OAuth, no magic links. Sign up toggle in the same screen. Use Supabase auth `signInWithPassword` / `signUp`.

### Windows constraint — Android only

You're on Windows. iOS native build is impossible without macOS + Xcode. Approach:
- **Android build:** use Gradle. `pnpm --filter @buildar/mobile android` should boot the app in an Android emulator. Verify locally.
- **iOS build:** DO NOT attempt. Add iOS-specific Podfile/Info.plist boilerplate if `expo prebuild` generates it (it will), but do not try to compile. Document in done-report that iOS is deferred to a Mac-bearing follow-up session.
- **AR testing:** ViroReact on Android emulator does NOT support ARCore (no camera). You will not be able to test the AR happy path locally. Test the FALLBACK path (which is the more important one anyway — if AR breaks, the app must still work). Add a runtime feature-detection that prefers fallback when AR init fails or AR is unavailable.

### Code structure inside apps/mobile/

```
apps/mobile/
  package.json                  # dependencies, scripts, workspace import for @buildar/core-types
  tsconfig.json                 # extends tsconfig.base.json, strict
  app.json                      # Expo config (prebuild target), with ViroReact plugin
  babel.config.js
  metro.config.js               # workspace-aware metro for monorepo
  index.js                      # RN entry
  App.tsx                       # root with navigation + auth provider
  src/
    navigation/
      RootNavigator.tsx         # auth-gated stack
    screens/
      SignInScreen.tsx
      HomeScreen.tsx
      ProjectDetailScreen.tsx
      SessionScreen.tsx         # the big one — AR + step + AI sheet
      CompletionScreen.tsx
    components/
      DifficultyIndicator.tsx   # wrench filled/outline row
      ProjectCard.tsx
      StepProgressIndicator.tsx
      ARView.tsx                # ViroReact wrapper with fallback
      AssistantSheet.tsx        # bottom sheet with input + response
    lib/
      supabase.ts               # client init from env
      api.ts                    # typed fetch wrappers around /api/v1/*
    theme/
      colors.ts                 # FF6B2B, 1A1A1A, F5F5F0
      spacing.ts                # 8-grid constants
      typography.ts             # scale per Lena's brief
```

### Env vars (apps/mobile/.env)

```
EXPO_PUBLIC_SUPABASE_URL=https://xbfgohafudrfygztqmtg.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=<paste from D:\BuildAR\.env if present, else placeholder>
EXPO_PUBLIC_API_BASE_URL=http://10.0.2.2:3010/api/v1   # 10.0.2.2 is the Android emulator's host loopback
```

If the values aren't in `D:\BuildAR\.env`, put placeholder strings + document in your done-report so Inon can fill in.

### Tests (apps/mobile/src/__tests__/)

You will NOT be able to write full E2E mobile tests in this autonomous session. Acceptable substitute:
- **Component tests:** `@testing-library/react-native` for at least: `ProjectCard`, `DifficultyIndicator`, `AssistantSheet` (verify it renders blocked state correctly when Safety returns blocked:true).
- **Pure-function tests:** for any helpers in `lib/api.ts` or `theme/` that you can isolate.
- **Skip:** screen integration tests requiring native modules (ViroReact, full navigation). Document in done-report.
- Target: **≥10 component/unit tests passing**. If you can ship more, great.

### MINOR-1 fix (bundle on the same branch, separate commit)

`D:\BuildAR\apps\api\src\routes\projects.ts` at lines 31, 66, 82 — three sites still forward `error.message` verbatim via `ERR.UPSTREAM(error.message)`. Replace with the same pattern you used in sessions.ts:
- Log the upstream message via `req.log.error(...)` (already in place per Jasmin's review)
- Return `ERR.INTERNAL()` or `ERR.UPSTREAM('Upstream unavailable')` — generic message to the API caller

Commit this as a separate commit on the same `feat/mobile-shell` branch with message:
```
fix(api/projects): sanitize PostgREST error.message at boundary

Carry-over from S1-006 minor #1 — sessions.ts and orchestrator.ts
were fixed in S1-008/009 but projects.ts was missed. Jasmin
flagged in BUILDAR-S1-008 QA as MINOR-1.
```

---

## Definition of done

1. `pnpm install` clean in `apps/mobile/`.
2. `pnpm --filter @buildar/mobile lint` passes.
3. `pnpm --filter @buildar/mobile typecheck` passes.
4. `pnpm --filter @buildar/mobile test` passes (≥10 unit/component tests).
5. **Android emulator boot:** `pnpm --filter @buildar/mobile android` boots the app in an Android emulator (or Android Studio AVD). App opens to Sign-in screen. Cold boot is acceptable for first run — must be reproducible.
6. **Smoke test the happy path on emulator:** sign up (or use a seed user if you create one), see the project list (skeleton then 2 seed projects), tap a project, see detail, tap Start Session, see the Session screen with AR fallback rectangle (AR will not initialize on emulator — that's expected, the fallback should be visible), tap Next through all steps, see Completion screen, tap Back to Projects. CAPTURE A SCREENSHOT OF EACH SCREEN.
7. **AI sheet smoke test:** on the Session screen, open the AI sheet, type a question, submit. Should call /assist. If the API isn't running locally, this can be a documented skip — the network call shape must be verified by reading the code AND a unit test on `lib/api.ts`.
8. MINOR-1 fix committed as a separate commit.
9. `git diff --stat` + `git log --oneline` paste in done-report.

---

## Branch

`feat/mobile-shell` off main. NOT pushed.

---

## Constraints

- **No concurrent agents.** You are the ONLY agent in `D:\BuildAR\` right now. Don't spawn helpers.
- **No schema changes.** If you need any, document in `agents/yoni/scratchpad/schema_request_v2.md` and continue. Andy routes to Silas.
- **TypeScript strict** — no `any`, no `@ts-ignore`.
- **No new backend routes** — only consume existing ones. If you need a new route, document and stop that piece.

---

## Report destination

`D:\Claude Playground\agents\andy\inbox\yoni_s1_011_done.md` — include:
- Files changed (git diff --stat, git log --oneline)
- Test counts
- Android emulator boot proof (paste log lines + screenshot file paths if you captured any)
- Manual smoke transcript per Definition-of-done step 6
- MINOR-1 commit SHA
- iOS deferred notes
- Open questions / schema requests
- Status: DONE or BLOCKED

**When done, send Telegram:**
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-011" "Mobile shell shipped on feat/mobile-shell. <test counts>. Android emulator boot verified. iOS deferred. MINOR-1 fix bundled. Report at agents/andy/inbox/yoni_s1_011_done.md."
```

If you hit a hard blocker (ViroReact won't install, Android emulator can't boot), send `update` flavor with the blocker line and document fully in the report.

---

## What happens after you finish

Andy dispatches sequentially (concurrent BuildAR agents = no):
1. **Silas** — BUILDAR-S1-010 (events schema alignment migration 0006). Small.
2. **Vera + Jasmin** in sequence — Vera reviews UX/a11y against Lena's brief; Jasmin reviews orchestrator integration, telemetry, AR fallback logic + security.

The user (Inon) is away. You report to Andy. Take the time you need — Gate B closing this session is the goal but not at the cost of broken code.

— Andy
