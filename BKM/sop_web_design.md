# SOP: Web Design & Visual Audit Procedure

**File Path:** `/BKM/sop_web_design.md`  
**Authority:** Andy (Orchestrator)  
**Agent:** Lena (UI/UX Designer)  
**Version:** 1.0 — 2026-04-24

---

## Scope
This SOP governs design reviews, redesign briefs, and visual QA for all web projects in the framework.

---

## Phase 1: Design Audit

### Visual Inventory Checklist
- [ ] Color palette — how many colors, contrast ratios, emotional tone
- [ ] Typography — families, weights, scale consistency
- [ ] Layout grid — alignment, whitespace, section differentiation
- [ ] Components — button states, card design, nav behavior
- [ ] Imagery — quality, consistency, alt text presence
- [ ] Icons — style consistency (emoji vs. vector, size, alignment)
- [ ] Animations — what's animated, what isn't, motion design quality
- [ ] Mobile layout — visible at 375px and 768px breakpoints

### UX Inventory Checklist
- [ ] Clear primary CTA above the fold
- [ ] Logical page flow (attention → interest → desire → action)
- [ ] Social proof presence (testimonials, logos, numbers with context)
- [ ] Thought leadership signals (blog, talks, press)
- [ ] Contact friction (is it easy to reach out?)
- [ ] Navigation clarity (can a new visitor find everything in 10 seconds?)

---

## Phase 2: Design Brief Structure

Every Design Brief must include these sections:

### 1. Color System
```
Primary:    #XXXXXX — [usage]
Secondary:  #XXXXXX — [usage]
Accent:     #XXXXXX — [usage]
Background: #XXXXXX — [usage]
Surface:    #XXXXXX — [usage]
Text:       #XXXXXX — [usage]
Muted:      #XXXXXX — [usage]
```
All pairs must pass WCAG AA. Verify at webaim.org/resources/contrastchecker.

### 2. Typography Scale
```
Display: [Font Family], [Weight], [Size]
H1:      [Font Family], [Weight], [Size]
H2:      [Font Family], [Weight], [Size]
H3:      [Font Family], [Weight], [Size]
Body:    [Font Family], [Weight], [Size], [Line Height]
Caption: [Font Family], [Weight], [Size]
Label:   [Font Family], [Weight], [Size], [Letter Spacing]
```

### 3. Section-by-Section Layout
For each section: current state → recommended change → rationale.

### 4. Animation Specifications
```
Element: [component name]
Trigger: [on load / on scroll / on hover]
Animation: [fade in / slide up / counter / etc.]
Duration: [Xms]
Easing: [ease-out / spring / linear]
Delay: [Xms after trigger]
```

### 5. New Sections
- Section name, purpose, content requirements, placement in page flow.

---

## Phase 3: Visual QA (Post-Implementation)

After Rex implements the design:
- [ ] All colors match the design brief hex values
- [ ] Typography scale is applied consistently
- [ ] Animations fire correctly at the right trigger points
- [ ] All new sections are present and correctly placed
- [ ] Mobile layout looks correct at 375px and 768px
- [ ] No design regressions in sections that weren't supposed to change

---

## Rules
1. Never start designing without Tomy's research brief.
2. Always cite WCAG compliance for color choices.
3. Design for mobile-first — desktop is an enhancement.
4. Every animation must have a `prefers-reduced-motion` fallback.
5. Specify fonts from Google Fonts unless Owner confirms custom fonts are available.
