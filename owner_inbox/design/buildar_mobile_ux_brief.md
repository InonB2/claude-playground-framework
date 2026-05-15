# BuildAR Pro — Mobile UX Brief
**Version:** 1.0  
**Author:** Lena (UI/UX Designer)  
**Date:** 2026-05-15  
**Audience:** Yoni (implementation), Andy (review)

---

## Overview

This brief defines the five core mobile screens for BuildAR Pro Phase 0–1. The app is a mobile-first, AR-guided DIY assistant. The interaction model is borrowed from IKEA instruction manuals: one thing at a time, visual-first, no ambiguity. The user should never wonder what to do next.

Tech stack: Bare React Native. Screens must degrade gracefully when AR is unavailable. All layout must use logical CSS properties (inline-start/inline-end, not left/right) so RTL support (Hebrew) requires only a stylesheet swap.

Touch targets: minimum 44 x 44 pt on all interactive elements.

---

## Screen 1 — Sign-in / Sign-up

### Purpose
Authenticate the user with minimum friction so they can get to their project quickly. This is a gateway, not a destination — keep it fast and invisible.

### Primary action
Enter email and password, then tap "Continue."

### Key components
- App logo mark (top center, small — not a hero)
- Screen title: "Sign in" or "Create account" (toggle link below the form)
- Email input field — label above, full-width, keyboard type `email-address`, autofocus on mount
- Password input field — label above, full-width, show/hide toggle icon (eye icon, 44pt)
- Primary CTA button: "Continue" — full-width, high-contrast fill, disabled until both fields have input
- Toggle link below CTA: "Don't have an account? Sign up" / "Already have an account? Sign in" — toggles the form between sign-in and sign-up mode without navigation
- Sign-up mode adds a "Confirm password" field between password and CTA
- Error message area: inline, below the field that failed (not a toast, not a modal)
- No social login, no OAuth, no magic links — email/password only in Phase 0–1

### Empty / loading state
- On mount: form fields are empty, CTA is disabled
- On submit: CTA shows a spinner inside the button (replaces label text); fields become read-only during request

### Error state
- Wrong credentials: red inline message below the password field — "Incorrect email or password."
- Network failure: red inline message below the CTA — "Could not connect. Check your connection and try again."
- Validation (sign-up, mismatched passwords): inline message below "Confirm password" — "Passwords don't match."
- No modal dialogs for errors on this screen.

### Navigation
- Entry point: app cold start (unauthenticated) or sign-out action
- On success: navigate to Screen 2 (Home / Project List)
- No back navigation from this screen — it is the root for unauthenticated users

---

## Screen 2 — Home / Project List

### Purpose
Let the user browse available projects and choose one to start or resume. This is the discovery surface — confidence that there is something worth doing here.

### Primary action
Tap a project card to view its detail.

### Key components
- Screen header: "Projects" (left-aligned title, no back arrow — this is the root authenticated screen)
- Session resume banner (conditional): shown only if the user has an active in-progress session. Single-line banner pinned below the header — "Resume: [Project Title] — Step 3 of 6." Full-width tap target navigates directly to Screen 4 (Session / Step View). Dismissible via a close icon (44pt).
- Project card list: vertical scroll, full-width cards with 8px gap between cards
  - Each card contains:
    - Thumbnail placeholder: 16:9 aspect ratio rectangle, neutral fill with a centered icon placeholder (no image in Phase 0–1)
    - Project title: bold, 17pt
    - Category label: small caps or muted body, e.g. "Furniture Assembly"
    - Difficulty indicator: a row of 5 icons (filled vs. outline circles or wrenches), 1–5 filled indicating difficulty — do not use stars (too generic)
    - Time estimate: "~45 min" — muted text, small
    - Card tap target: full card surface, minimum 80pt tall
- No filter or search in Phase 0–1 — the list is short (2 seed projects)

### Empty / loading state
- Loading: show 2–3 skeleton card placeholders (grey shimmer rectangles matching card dimensions) while data fetches
- Empty list: centered message with icon — "No projects yet. Check back soon." No CTA needed in Phase 0–1.

### Error state
- Full-page error state (not inline): centered icon + message — "Couldn't load projects." + a "Try again" button (retry fetch). Log the error silently.

### Navigation
- Entry from: Sign-in success, or "Back to Projects" from Screen 5 (Completion)
- Tap card: navigate to Screen 3 (Project Detail), passing project ID
- Tap resume banner: navigate to Screen 4 (Session / Step View), passing active session ID

---

## Screen 3 — Project Detail

### Purpose
Give the user enough information to decide to start (or resume) the project. This is the commitment screen — address hesitation before the session begins.

### Primary action
Tap "Start Session" (or "Resume Session" if a session exists for this project).

### Key components
- Back arrow (inline-start, 44pt) leading back to Screen 2
- Thumbnail placeholder: full-width 16:9 block at top of scroll area
- Project title: large, bold, below thumbnail
- Category + difficulty row: horizontal, same format as card (category label + difficulty icons)
- Time estimate: "~45 min" next to a clock icon
- Summary text: 2–4 lines of prose description (from CMS `summary` field). Body text, not a heading.
- Steps preview section: labeled "What you'll do" — numbered list of step titles (no descriptions). If more than 5 steps, show first 5 then "...and 3 more steps." Non-interactive list.
- Materials / Tools callout (conditional): shown only if the project has this data seeded. Small card or indented block labeled "You'll need" — bullet list of tools/materials. If not seeded, omit the section entirely — do not show an empty block or "N/A."
- Primary CTA: "Start Session" (or "Resume Session") — full-width, fixed to bottom of screen above safe area inset, always visible without scrolling. If a session exists: change label to "Resume Session" and add a secondary link "Start over" beneath the button (smaller, destructive text style).

### Empty / loading state
- Loading: show skeleton blocks for the thumbnail, title, and two text-line placeholders. CTA button skeleton at bottom.
- If project fails to load (bad ID): navigate back to Screen 2 automatically and show a brief bottom toast — "Project not found."

### Error state
- Session creation failure: bottom toast — "Couldn't start session. Try again." CTA re-enables immediately.

### Navigation
- Entry from: Screen 2 (project card tap), passing project ID
- CTA tap: POST to create/resume session, then navigate to Screen 4 with session ID
- Back: Screen 2

---

## Screen 4 — Session / Step View

### Purpose
Guide the user through one step at a time. This is the product's core loop — everything else exists to get the user here. Clarity, focus, and zero distraction.

### Primary action
Read (or view via AR) the current step, complete the physical action, then tap "Next."

### Key components
- Header bar (minimal): project title truncated to one line (inline-start), "Exit" text button (inline-end, 44pt). Exit triggers a confirmation bottom sheet: "Your progress is saved. Exit?" with "Exit" and "Keep going" options.
- Step progress indicator: "Step 2 of 6" — single text line, muted, directly below header. Do not use a progress bar in Phase 0–1 (add in Phase 2 with animation).
- AR view area: a full-width rectangle with a 4:3 aspect ratio (approximately). When AR is available and active: live camera feed with overlay. When AR is unavailable or loading: neutral dark rectangle with a centered icon (camera/AR icon) and label "AR unavailable — follow the instructions below." The fallback state must look intentional, not broken.
- Step title: bold, 20pt, below the AR area
- Step description: body text, up to ~4 lines before overflow scroll — keep CMS content concise. Below the title.
- If step has an image asset attached: show it below the description, full-width, in a 16:9 container. Do not show an empty container if no image.
- Navigation row (bottom, above safe area inset): two buttons side by side.
  - "Previous" (inline-start, secondary style, ghost/outline): disabled on step 1 — do not hide it, disable it (preserve layout stability).
  - "Next" (inline-end, primary fill): on the last step changes label to "Complete."
- "Ask AI" floating action button: circular, 56pt, inline-end, positioned above the navigation row by 16px. Tap opens a bottom sheet (not a new screen) with a text input and submit button. The sheet shows the last AI response if one exists. Dismiss by swiping down or tapping outside. The AI button must remain visible and accessible at all times during an active step.

### Empty / loading state
- Session load: full-screen centered spinner while session and step data resolve. Avoid showing partial UI.
- Step transition (Next/Previous tap): brief 150ms opacity fade between step content — replace, do not slide (slide animation is disorienting mid-task).
- AI response loading: inside the bottom sheet, show a typing indicator (3-dot animation) while awaiting response.

### Error state
- Step data failure: inline error below step title area — "Couldn't load step details." + "Retry" link. Do not navigate away.
- AI failure: inside the bottom sheet, replace typing indicator with — "Couldn't get a response. Try again." with a retry button.
- Session save failure (step progression): bottom toast — "Progress may not have saved. Check your connection." Do not block navigation — let the user keep moving.

### Navigation
- Entry from: Screen 3 CTA (new session) or Screen 2 resume banner (existing session)
- "Next" on last step: POST session completion, navigate to Screen 5
- "Previous" / "Next": update current step index, reload step content in place
- "Exit": navigate to Screen 2 (session state preserved on server)

---

## Screen 5 — Session Completion

### Purpose
Confirm the user has finished. Deliver a clear, satisfying moment of completion before returning them to the project list. Keep it brief — they just did the work, don't make them read.

### Primary action
Tap "Back to Projects."

### Key components
- No header bar — this is a full-screen celebratory moment
- Checkmark icon: large (80pt), centered vertically in the upper half of the screen. Use a simple animated checkmark drawn with a stroke animation (SVG path or Lottie if available — fallback to static icon if Lottie is not in the bundle).
- Heading: "Done!" — large, bold, centered
- Subheading: "[Project Title]" — muted, slightly smaller, centered. Pulls from session data.
- Total time: "Completed in 38 min" — pulls from session timestamps (started_at to completed_at). If timestamps are missing, omit this line rather than show "0 min."
- CTA: "Back to Projects" — full-width, centered, standard primary button style. Positioned in the lower third of the screen.
- No sharing, no rating, no upsell — Phase 0–1 only.

### Empty / loading state
- Screen renders immediately from session data passed through navigation — no async load needed.
- If session data is missing (edge case from navigation error): show the checkmark and "Done!" but omit the project title and time lines.

### Error state
- No async operations on this screen. No error states needed.

### Navigation
- Entry from: Screen 4 "Next" on last step (session completion POST successful)
- "Back to Projects" CTA: navigate to Screen 2, clearing the session from navigation state
- No back gesture — add this screen to a non-back navigation stack (replace, not push)

---

## Design System Seeds

**Primary color:** `#FF6B2B` — a construction-orange with enough saturation to work as an AR overlay accent and a mobile UI primary. It reads "tool, work, build" without generic blue associations, and holds contrast against both white backgrounds and dark AR camera feeds. Pair with near-black `#1A1A1A` for text and `#F5F5F0` as an off-white page background (warmer than pure white, easier on the eye in bright environments).

**Font stack:** `System` — use React Native's default system font stack: San Francisco on iOS, Roboto on Android. No custom font loading in Phase 0–1. Both fonts support Hebrew characters natively, so RTL is font-safe with zero extra configuration. Suggested scale: 13pt (caption), 15pt (body), 17pt (body emphasis), 20pt (step title), 24pt (section heading), 32pt (completion heading).

**Spacing unit:** 8px grid. All margins, paddings, gaps, and component dimensions should be multiples of 8 (8, 16, 24, 32, 48, 64). This keeps layout consistent across screen sizes and makes developer handoff unambiguous.

**Icon set:** `react-native-vector-icons` with the `MaterialCommunityIcons` pack. It is open source (MIT), ships with icons relevant to construction/tools (wrench, hammer, home, camera, chevrons), supports tree-shaking, and works across iOS and Android without native module complications. For the difficulty indicator, use `wrench` (filled) and `wrench-outline` (empty) from this set.
