# AR‑Guided DIY Mobile MVP PRD (For Lovable & Claude Agents)

## 1. Purpose and Audience

This PRD defines the **Phase 1 / MVP AR‑guided DIY mobile application**: UX, flows, and technical interfaces required for Lovable/Claude agents to implement the mobile client and its APIs.

Audience:
- AI agents (Lovable, Claude) implementing the React Native mobile app and related backend endpoints.
- Human reviewers validating UX and scope.

This MVP focuses on **mobile AR guidance for 10–20 curated projects**, with a thin AI assistant and minimal orchestrator integration.

---

## 2. Goals and Non‑Goals

### 2.1 Goals

1. Deliver a functional AR‑guided DIY app on iOS and Android that:
   - Guides users through projects step‑by‑step using overlays and text.
   - Tracks session progress and completion.
   - Collects telemetry (step times, drop‑offs) for future optimization.
2. Establish reusable **client patterns** for AR calibration, step sequencing, and AI Q&A.
3. Integrate with the backbone APIs defined in `01-system-architecture-prd.md`.

### 2.2 Non‑Goals

- Full Creator Studio authoring on mobile.
- Marketplace monetization or subscription flows.
- Advanced CV‑based error detection (basic hooks only).

---

## 3. Platforms and Stack

- **Platform:** React Native (Expo if compatible with AR stack; otherwise bare RN).
- **Target OS:**
  - iOS 16+ (ARKit capable devices).
  - Android 12+ (ARCore capable devices).
- **AR Engine:**
  - MVP: Utilize a community‑supported RN AR module (e.g., ViroReact or RN bridge to ARCore/ARKit) that Lovable can manage.
  - Design code to make AR module swappable later (wrap in an abstraction layer).

---

## 4. Core User Flows

### 4.1 Onboarding and Permissions

**Goal:** Ensure users understand AR requirements and grant necessary permissions.

Flow:
1. Splash → intro carousel (what the app does).
2. Permission screen(s):
   - Camera access (required for AR).
   - Optional: photo library if we capture completion photos.
3. Device capability check:
   - If AR not supported, offer non‑AR fallback (text + images) for projects.

AI agent requirements:
- Implement permission checks using platform best practices.
- Provide clear error messaging if AR is unavailable.

### 4.2 Project Discovery

Flow:
1. Home screen lists projects (from `/api/v1/projects`).
2. Filters:
   - Category (Furniture, Home Fix, Decor, etc.).
   - Difficulty (Beginner, Intermediate, Advanced).
3. Tap project → Project details screen with:
   - Title, hero image.
   - Estimated time, difficulty, summary.
   - Required tools and materials (from backend).
   - "Start Project" button.

### 4.3 Start Session

When user taps "Start Project":
1. App calls `POST /api/v1/sessions` with project ID.
2. Backend returns session ID and initial step info.
3. App navigates to AR Session screen.

### 4.4 AR Session Flow

**Goal:** Guide user step‑by‑step using AR overlays plus text.

Layout (AR Session screen):
- Top: Step indicator ("Step 2 of 8"), project name.
- Center: AR view.
- Bottom sheet:
  - Step title.
  - Step description.
  - Buttons: Back, Next, Help.

Interaction:
1. Initial calibration:
   - Instruction overlay: "Move your phone to scan the surface."
   - Once a plane is detected, show a placeholder overlay (e.g., ghosted object or arrow) to confirm alignment.
2. For each step:
   - Render step‑specific overlay (arrow, highlight, simple ghost model) based on metadata in `project_steps` (exact schema defined in CMS PRD).
   - User reads instructions, performs step, then taps "Next".
   - App sends `PATCH /api/v1/sessions/:id` with new step index and optional telemetry (time spent).
3. Help:
   - Tap "Help" → open AI assistant drawer (see section 4.5).

Fallback for non‑AR devices:
- Use static images or 3D previews instead of live AR feed, but keep the same step flow.

### 4.5 AI Assistant (MVP)

**Goal:** Provide context‑aware Q&A during a project.

Flow:
1. User taps "Help" in AR Session.
2. Bottom drawer opens with a chat UI.
3. User types a question (e.g., "Which screw is A4?").
4. App sends `POST /api/v1/orchestrator/plan` (or dedicated `/assist`) with:
   - `sessionId`.
   - `projectId`.
   - `currentStepIndex`.
   - `userMessage`.
5. Backend orchestrator calls Claude or relevant agents and returns plain‑text answer + optional structured hints.
6. App displays answer in chat UI.

Requirements:
- For MVP, use **text only**; voice can be added later.
- Handle latency gracefully (loading indicator, error message on failure).

### 4.6 Completion and Summary

Flow:
1. On final step, "Next" becomes "Complete".
2. When user taps "Complete":
   - App calls `PATCH /api/v1/sessions/:id` with `status=completed`.
   - Prompt user to optionally take a photo of the finished project.
3. Show completion screen with:
   - Confetti / celebratory animation.
   - Summary of time, steps completed, and any tips for next projects.

---

## 5. Screens and Components

### 5.1 Screens

1. **Splash / Intro**
2. **Sign‑In / Sign‑Up** (username/email + Supabase Auth flows)
3. **Home / Project List**
4. **Project Details**
5. **AR Session**
6. **Completion Summary**
7. **Settings / Profile** (basic, MVP)

### 5.2 Key Reusable Components

- `ProjectCard` – summary card for project list.
- `StepIndicator` – shows current step / total.
- `ARView` – abstraction over underlying AR module.
- `BottomSheet` – step details and controls.
- `ChatDrawer` – AI assistant UI.

Lovable agents should create these as composable, typed components.

---

## 6. Data Contracts (Client ↔ Backend)

### 6.1 Project Entity (simplified)

```ts
// packages/core-types/src/project.ts

export interface Project {
  id: string;
  title: string;
  slug: string;
  category: string; // e.g., "furniture", "home_fix"
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedMinutes: number;
  heroImageUrl: string | null;
  toolsSummary: string[];   // simple labels for MVP
  materialsSummary: string[];
}
```

### 6.2 ProjectStep Entity (simplified)

```ts
export interface ProjectStep {
  id: string;
  projectId: string;
  index: number; // 0‑based or 1‑based, but consistent
  title: string;
  description: string;
  // AR overlay metadata (structure defined in CMS PRD)
  overlayType: 'arrow' | 'ghost_model' | 'highlight';
  overlayData: Record<string, any>;
}
```

### 6.3 Session Entity (client view)

```ts
export interface Session {
  id: string;
  projectId: string;
  userId: string;
  status: 'active' | 'completed' | 'abandoned';
  currentStepIndex: number;
  startedAt: string;
  updatedAt: string;
}
```

Endpoints should return these shapes (or extensions) to the client.

---

## 7. Telemetry and Analytics (MVP)

The mobile client must emit telemetry events via a simple helper that calls a backend endpoint or writes to `events` table indirectly.

Minimum events:
- `session_started` – user and project IDs, timestamp.
- `step_viewed` – session, step index, timestamps.
- `step_completed` – same as above.
- `session_completed` – total duration, steps completed.
- `assistant_invoked` – step index, question length.

Lovable agents implementing new features should always consider whether a new user action is worth tracking.

---

## 8. Non‑Functional Requirements (Mobile)

- **Performance:** AR view should target 30+ FPS on supported devices.
- **Offline behavior:**
  - If connection drops mid‑session, user should still see current step details; updates can be queued and synced when online.
- **Error handling:**
  - Show user‑friendly errors for network issues, AR initialization failures, and missing data.
- **Accessibility:**
  - Support Dynamic Type / font scaling.
  - Ensure important instructions are also readable as text, not only via AR visuals.

---

## 9. Implementation Guidance for AI Agents

1. **Respect abstractions:**
   - Wrap AR SDK in `ARView` so it can be swapped or extended.
   - Use `/packages/core-types` for all domain types.
2. **Keep screens focused:**
   - Avoid feature creep; additional modes (e.g., advanced settings) must be separate tickets.
3. **Coordinate with backend:**
   - Do not hard‑code API URLs; use environment configuration.
   - Treat server responses as source of truth for project and session state.
4. **Testing:**
   - Add basic unit tests where possible (e.g., reducers, hooks).
   - Run app on at least one iOS simulator and one Android emulator in CI (or via Lovable defaults).

---

## 10. Acceptance Criteria

MVP is considered complete when:

1. A user can:
   - Sign up / sign in.
   - Browse projects.
   - Start a project, complete all steps in AR mode or fallback.
   - Ask at least one question to the AI assistant during a session.
   - Reach a completion screen.
2. Session progress is persisted in Supabase and can be resumed.
3. Core telemetry events are recorded in the backend.
4. The app runs on a representative set of iOS and Android devices without critical crashes in AR sessions.
