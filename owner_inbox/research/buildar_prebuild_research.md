# BuildARPro Pre-Build Research
**Prepared by:** Tomy (Research Agent)
**Date:** 2026-05-10
**For:** Andy + Yoni — decision making before sprint start

---

## Section 1: AR Library for React Native

### Options Evaluated

#### ViroReact (ReactVision/viro)
- **iOS + Android:** Yes. Uses ARKit on iOS, ARCore on Android.
- **Expo managed workflow:** Partial. Does NOT run in Expo Go. Requires a config plugin (`@reactvision/react-viro` in `app.json`) + `npx expo prebuild --clean` + local device run. This is Expo's "managed prebuild" path — you write JS/JSON config, never touch native files directly, but you do compile locally or via EAS.
- **Active maintenance 2025/2026:** Yes, actively maintained. Latest release is v2.54.0 (April 2, 2026). Includes Android 15/16 compatibility, semantic masking, animated GLB models. The community (ReactVision) took ownership in 2020 and has been shipping consistent releases.
- **Fallback mode:** ViroReact has a `ViroARSceneNavigator` for AR and a `Viro3DSceneNavigator` (non-AR 3D mode). You can wrap both behind an `ARView` component that swaps based on device capability or a feature flag. No AR session required for the fallback — it renders a 3D scene without camera passthrough.
- **Risk:** Requires prebuild/native compile. Cannot use Expo Go for daily dev.

#### React Native Vision Camera + Custom AR
- **iOS + Android:** Yes, Vision Camera supports both.
- **Expo managed workflow:** Vision Camera has a config plugin; works with managed prebuild path. But "AR on top of Vision Camera" is largely DIY — you use Vision Camera for the camera feed, then layer Three.js / react-three-fiber / custom shaders on top with manual ARKit/ARCore frame processing.
- **Active maintenance:** Vision Camera is actively maintained (v4.x in 2025). The AR integration layer is not a packaged library — it's custom engineering work.
- **Fallback mode:** Easy — just disable AR processing and show the camera or a static 3D view.
- **Risk:** High build cost. No pre-built AR anchoring, plane detection, or object placement. Every AR primitive is custom. Wrong choice for Phase 0-1 velocity.

#### Expo Camera + Three.js / WebXR
- **iOS + Android:** Expo Camera works on both. WebXR in a WebView works on Chrome Android but iOS WebXR support is limited (Safari requires a flag, not production-ready as of 2026).
- **Expo managed workflow:** Yes, Expo Camera works in managed workflow including Expo Go.
- **Active maintenance:** Expo Camera is actively maintained. Three.js/R3F are actively maintained.
- **Fallback mode:** Trivially easy — no AR at all, just 3D rendering.
- **Risk:** WebXR-in-WebView is a compromise, not a real native AR solution. Performance penalty. iOS support unreliable. Not viable for a production AR product.

#### 8th Wall (Web AR)
- **iOS + Android:** Browser-based, works on both via WebXR/proprietary engine.
- **Expo managed workflow:** N/A — web only, used in a WebView.
- **Active maintenance:** DEAD as a commercial platform. Niantic shut down 8th Wall in February 2026. Open-sourced MIT components, but the closed-source engine binary is frozen. Do not use.
- **Fallback mode:** N/A.
- **Risk:** Platform is shut down. Hard no.

#### ARKit/ARCore Direct via Native Modules
- **iOS + Android:** ARKit = iOS only. ARCore = Android only. Requires separate modules for each platform.
- **Expo managed workflow:** No official Expo SDK support. Requires bare workflow and writing native bridging code.
- **Active maintenance:** ARKit and ARCore themselves are actively maintained by Apple/Google. The React Native binding layer is the problem — `react-native-arkit` is abandoned (last commit 2020, project seeking maintainers, iOS only).
- **Fallback mode:** Custom — no abstraction layer provided.
- **Risk:** Maximum native complexity, dual codebase, no abstraction. Only viable if you need platform-specific features ViroReact doesn't expose.

#### NativeAR / react-native-arkit
- **iOS + Android:** iOS only (ARKit-based).
- **Expo managed workflow:** No.
- **Active maintenance:** Abandoned. The repo explicitly directs users to ViroReact as an alternative.
- **Fallback mode:** None provided.
- **Risk:** Do not use.

### Comparison Summary

| Library | iOS+Android | Expo Managed | Maintained 2026 | Fallback Mode |
|---|---|---|---|---|
| ViroReact | Yes | Prebuild only | Yes (v2.54.0) | Yes (3D scene navigator) |
| Vision Camera + custom | Yes | Prebuild only | Vision Camera yes; AR layer = custom | Yes (skip AR processing) |
| Expo Camera + WebXR | Partial (iOS WebXR broken) | Yes | Yes | Yes (trivial) |
| 8th Wall | Yes (browser) | N/A | Shut down Feb 2026 | N/A |
| ARKit/ARCore direct | Split by platform | No | Engine yes; bindings abandoned | Custom only |
| react-native-arkit | iOS only | No | Abandoned | None |

### Key Constraint Fit: ARView Abstraction with Non-AR Fallback

ViroReact is the only option that (a) ships both AR and non-AR scene navigators as first-class APIs, (b) supports iOS + Android from a single codebase, (c) has a config plugin for Expo managed prebuild, and (d) is actively maintained. Wrapping `ViroARSceneNavigator` / `Viro3DSceneNavigator` behind a single `<ARView>` component with a capability-check is the natural pattern for Phase 0-1.

**Recommendation:** Use ViroReact (ReactVision) via Expo managed prebuild. It is the only production-grade, cross-platform, actively maintained AR library for React Native that supports a clean non-AR fallback without custom engineering.

---

## Section 2: Expo Managed vs. Bare React Native for AR

### Can ViroReact work in Expo managed workflow?

Yes, with a precise caveat. ViroReact does NOT work in Expo Go (the sandboxed dev client). It requires the "managed prebuild" path:
1. Add the config plugin to `app.json`
2. Run `npx expo prebuild --clean` — this generates `/ios` and `/android` native project folders
3. Build and run locally with `npx expo run:ios` / `npx expo run:android`, or via EAS Build

This is not "bare" in the traditional sense — you never manually write Swift/Kotlin. Expo's config plugin system handles native configuration declaratively. The generated native folders are gitignore-able if you use EAS Build exclusively.

### Expo SDK version (early 2026)

- **SDK 53** — Released April 2025. New Architecture (Fabric/JSI) enabled by default.
- **SDK 54** — Released September 2025. React Native 0.81, native tabs beta, edge-to-edge Android layouts.
- ViroReact v2.54.0 (April 2026) explicitly targets Expo 52+ and React Native 0.76.9+. SDK 52/53/54 compatibility confirmed.

The relevant camera/AR APIs (AVFoundation on iOS, Camera2/ARCore on Android) are accessed by ViroReact directly via native modules — Expo SDK does not need to expose them separately.

### Eject cost when native AR modules are needed later

With the managed prebuild path, "ejecting" is less dramatic than it used to be. The native folders already exist after `expo prebuild`. The real eject cost is:
- Losing over-the-air (OTA) update simplicity for native code changes
- Maintaining native project files manually in git
- EAS Build setup becomes more complex for custom native code

For BuildARPro, if you need to go beyond ViroReact's API surface (e.g., custom ARCore depth sensing, LiDAR access on iOS Pro), you would add a custom native module to the already-generated native project — not a full framework migration. Estimated cost: 1-2 days of Yoni's time per custom native feature.

### Which path do modern production React Native AR apps use?

Expo managed prebuild (the middle path) is the dominant choice for new AR projects in 2025/2026. Full bare workflow is reserved for apps with heavy custom native codebases. Pure Expo Go managed workflow is not viable for AR.

**Recommendation:** Start with Expo managed prebuild (not bare, not pure managed). This gives the fastest initial setup, full ViroReact support, and a clear upgrade path to custom native modules later without framework migration.

---

## Section 3: PNPM Monorepo + Supabase Branching — Setup Gotchas

### PNPM Workspaces + React Native (Expo) — Known Issues

**Root problem:** PNPM uses an isolated, symlink-based dependency layout by default. React Native's Metro bundler expects a flat `node_modules` structure. This mismatch is the source of most errors.

**Known failure modes:**
1. **Metro can't resolve transitive dependencies** — e.g., `Unable to resolve module @babel/runtime/helpers/interopRequireDefault` even when the package exists. Metro follows symlinks incorrectly into the PNPM virtual store.
2. **Duplicate React instances** — If `react` resolves to different versions in different workspaces, you get runtime crashes. Must pin with `pnpm.overrides` in root `package.json`.
3. **Export Maps / Subpath Exports** — RN packages using `package.json` `exports` field cannot be resolved by default Metro config. Requires `resolver.unstable_conditionNames` config.
4. **EAS Build assumes Yarn** — Expo's EAS Build CI internally assumes Yarn/npm layout. PNPM monorepos require explicit `eas.json` configuration and sometimes a `.npmrc` or postinstall workaround.
5. **Isolated deps failure** — `PNPM + isolated deps fails` is a confirmed open Expo issue (expo/expo #41806).

**Recommended mitigations:**
- Set `node-linker=hoisted` in `.npmrc` or `pnpm-workspace.yaml` for the mobile workspace. This makes PNPM behave like npm for React Native packages.
- Configure `metro.config.js` in `apps/mobile` with: `watchFolders` = entire workspace root, `nodeModulesPaths` = `[workspaceRoot/node_modules, apps/mobile/node_modules]`, `disableHierarchicalLookup: true`.
- Use `unstable_enableSymlinks: true` in Metro config if staying with isolated linker.
- Pin React and React Native versions via `pnpm.overrides`.

Expo's `expo/metro-config` package (SDK 49+) has built-in monorepo support that auto-configures `watchFolders` and resolver paths for Bun, npm, pnpm, and Yarn. Use `withMetroMultiPlatform` or the standard `getDefaultConfig` with monorepo options — this eliminates most manual Metro config.

### apps/mobile vs apps/web in same PNPM monorepo

**No fundamental conflict** when properly structured. The community pattern (Turborepo + PNPM + Next.js + Expo) is well-documented and used in production as of 2025. Key requirements:
- Shared packages (e.g., `packages/ui`, `packages/types`) use platform-specific file extensions (`.web.tsx`, `.native.tsx`) to serve correct implementations to each bundler.
- Next.js (webpack/Turbopack) and Metro bundler are fully independent — they each resolve from their own workspace and do not interfere.
- React versions must match across `apps/web` and `apps/mobile`.
- Do not hoist React Native-specific packages (e.g., `react-native`, `expo`) to the workspace root — keep them scoped to `apps/mobile`.

### Supabase Branching — How It Works + Small Team Model

**Branching 2.0** (current as of 2025/2026) removes the Git requirement. Key facts:

- Each branch is a full copy of your Supabase project (schema, functions, config) minus production data.
- Two branch types:
  - **Preview branches** — ephemeral, auto-paused after inactivity, auto-deleted when a PR closes. Use for feature testing.
  - **Persistent branches** — long-lived, not auto-paused. Use for staging/QA.
- **Git-connected workflow:** Branches auto-create on PR open, auto-destroy on PR close. Migrations live in `supabase/migrations/` and are replayed on the branch.
- **Dashboard-only workflow (gitless):** Create branch from dashboard, make changes via Table Editor or SQL Editor, review schema diff, merge. No Git required.

**For a 1-2 person team (BuildARPro):**
- The git-connected workflow (branch-per-PR) is the recommended path. It ties schema changes to code changes and gives you an automatic audit trail.
- Practical flow: `supabase migration new <name>` locally → push PR → Supabase auto-provisions preview branch → test against preview → merge PR → Supabase auto-runs migration on production.
- Cost: Preview branches are included on Pro plan. On free tier, branching is limited — check current Supabase pricing before relying on it in CI.

**Known gotchas:**
- Preview branches do not copy production data by default — seed scripts are required for meaningful testing.
- Branch pausing (after inactivity) means cold-start latency on first request after idle.
- Supabase CLI (`supabase db diff`, `supabase migration new`) must be part of the development workflow or schema drift accumulates fast.

**Recommendation:** Use PNPM with `node-linker=hoisted` for the mobile workspace and configure Metro with Expo's built-in monorepo support. Use Supabase git-connected branching (branch-per-PR) for schema changes, with seed scripts for test data.

---

## Section 4: Schema Delta Analysis

### Silas's Existing Schema (5 tables, `buildarpro_schema.sql`)

The actual tables in the file are:
1. `users` — auth profile extension (id, email, full_name, created_at)
2. `guides` — core AR guide (owner_id, title, description, product_sku, vuforia_target_id, steps as jsonb, is_published)
3. `image_targets` — Vuforia target registry (guide_id, vuforia_target_name, target_type, rating, metadata_json)
4. `subscriptions` — Stripe subscription state (user_id, stripe_customer_id, stripe_sub_id, plan_tier, status, guides_limit, current_period_end)
5. `guide_views` — usage analytics (guide_id, user_id, viewed_at, device_os)

Note: The schema file header says "5-Table Schema" and mentions `users, projects, project_steps, assets, sessions` — but the actual SQL defines completely different tables (`users, guides, image_targets, subscriptions, guide_views`). The header comment is stale/incorrect. The actual content is what matters.

### New Plan's 6 Required Tables

Per the research task prompt: `profiles, projects, project_steps, assets, sessions, events`

### Table-by-Table Mapping

| New Plan Table | Silas's Equivalent | Status | Notes |
|---|---|---|---|
| `profiles` | `users` | Rename + minor delta | `users` is a functional profiles table — rename to `profiles`, keep the trigger pattern. Add `avatar_url`, `plan_tier` columns if needed (or keep plan_tier in subscriptions). |
| `projects` | `guides` | Rename + significant delta | `guides` tracks AR guides with Vuforia-specific fields (`vuforia_target_id`, `product_sku`). `projects` in the new plan likely has a broader schema. Core fields (owner_id, title, description, is_published) carry over. `steps` jsonb column likely moves to `project_steps` table. |
| `project_steps` | None (embedded in `guides.steps` jsonb) | New table | Steps were stored as jsonb blob inside `guides`. New plan normalizes this into a dedicated table — correct architectural move for AR step ordering, media assets per step, etc. |
| `assets` | None | New table | No assets table in Silas's schema. Assets were implicitly embedded in `image_targets` (Vuforia-specific). New `assets` table should be a generic media registry (S3/Storage bucket references). |
| `sessions` | None | New table | No sessions table in Silas's schema. This likely tracks AR session events (user opened guide, completed steps, etc.) |
| `events` | `guide_views` | Rename + significant expansion | `guide_views` only tracks view events with device_os. New `events` table is presumably a broader analytics event stream (session_start, step_complete, share, etc.). Core pattern (guide_id, user_id, timestamp) carries over. |
| `image_targets` | — | No equivalent in new plan | Vuforia-specific. May be absorbed into `assets` table with a `target_type` discriminator, or kept as a separate table if Vuforia is still the AR target engine. |
| `subscriptions` | `subscriptions` | Keep as-is | Clean, complete Stripe integration table. No migration needed — carry forward unchanged. |

### What's Missing in Old Schema

1. `project_steps` — normalized step table with ordering, per-step media
2. `assets` — generic media/file storage registry
3. `sessions` — AR session tracking

### What Would a Clean Migration Look Like

```sql
-- 1. Rename users -> profiles
ALTER TABLE public.users RENAME TO profiles;

-- 2. Rename guides -> projects; strip Vuforia-specific columns OR keep as nullable
ALTER TABLE public.guides RENAME TO projects;
ALTER TABLE public.projects RENAME COLUMN vuforia_target_id TO ar_target_id;
-- product_sku can stay or be dropped

-- 3. Create project_steps (normalize out of projects.steps jsonb)
CREATE TABLE public.project_steps (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  uuid NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  step_order  int NOT NULL,
  title       text,
  description text,
  ar_content  jsonb,
  created_at  timestamptz NOT NULL DEFAULT now()
);
-- Backfill: parse existing projects.steps jsonb into rows
-- Then: ALTER TABLE public.projects DROP COLUMN steps;

-- 4. Create assets table
CREATE TABLE public.assets (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  uuid REFERENCES public.projects(id) ON DELETE CASCADE,
  step_id     uuid REFERENCES public.project_steps(id) ON DELETE CASCADE,
  owner_id    uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  file_url    text NOT NULL,
  asset_type  text NOT NULL,  -- 'image_target', 'model_3d', 'audio', 'video'
  metadata    jsonb,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- 5. Create sessions table
CREATE TABLE public.sessions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  uuid NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id     uuid REFERENCES public.profiles(id) ON DELETE SET NULL,
  started_at  timestamptz NOT NULL DEFAULT now(),
  ended_at    timestamptz,
  device_os   text,
  metadata    jsonb
);

-- 6. Rename guide_views -> events; add event_type discriminator
ALTER TABLE public.guide_views RENAME TO events;
ALTER TABLE public.events ADD COLUMN event_type text NOT NULL DEFAULT 'view';
ALTER TABLE public.events ADD COLUMN session_id uuid REFERENCES public.sessions(id);
ALTER TABLE public.events RENAME COLUMN viewed_at TO occurred_at;

-- 7. Update all FK references (guides -> projects, users -> profiles)
-- Update triggers, policies, indexes accordingly

-- 8. image_targets: migrate into assets table, then drop
INSERT INTO public.assets (project_id, owner_id, file_url, asset_type, metadata)
  SELECT it.guide_id, p.owner_id, '', 'image_target',
         jsonb_build_object('vuforia_target_name', it.vuforia_target_name,
                            'target_type', it.target_type,
                            'rating', it.rating,
                            'metadata_json', it.metadata_json)
  FROM public.image_targets it
  JOIN public.projects p ON p.id = it.guide_id;
DROP TABLE public.image_targets;
```

### Migrate or Start Fresh?

**Start fresh is cleaner.** Reasons:
1. The old schema has schema header drift (the file header says `users, projects, project_steps, assets, sessions` but the actual SQL is `users, guides, image_targets, subscriptions, guide_views`). This suggests the schema was iterated ad hoc and may have diverged from any deployment.
2. The `guides.steps` jsonb column needs to be fully parsed and normalized — non-trivial backfill on a schema that may not have production data yet.
3. `image_targets` (Vuforia-specific) needs a decision: keep as separate table or absorb into `assets`. Starting fresh forces this decision cleanly.
4. All RLS policies, triggers, and indexes will need rewriting regardless — the rename cascade is almost as much work as a fresh schema.
5. There is no production data to preserve (BuildARPro is pre-launch).

The migration path above is provided as a reference for structural equivalence, but the recommendation is to write a clean schema from scratch using the new 6-table model, informed by what Silas got right (RLS pattern, trigger for profile auto-creation, subscription table structure).

**Recommendation:** Start fresh with a new 6-table schema (`profiles, projects, project_steps, assets, sessions, events`), carrying forward Silas's RLS patterns, the auto-profile trigger, and the `subscriptions` table unchanged. Do not attempt an in-place migration.

---

*End of research. Sources used: ReactVision/viro GitHub, ViroCommunity docs, Expo changelog, Callstack blog, Expo monorepo docs, Supabase Branching 2.0 blog, DEV Community PNPM articles, 8th Wall shutdown coverage.*
