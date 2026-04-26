# SOP: Web Development Procedure

**File Path:** `/BKM/sop_web_development.md`  
**Authority:** Andy (Orchestrator)  
**Agent:** Rex (Web Developer)  
**Version:** 1.0 — 2026-04-24

---

## Scope
This SOP governs all frontend web development tasks in the framework, from initial implementation to production deployment.

---

## Pre-Implementation Checklist (Do before writing a single line)
- [ ] Read Tomy's Knowledge Brief
- [ ] Read Lena's Design Brief (if applicable)
- [ ] Read Maya's Security Report (if applicable)
- [ ] Understand the target platform constraints (Base44, Next.js, etc.)
- [ ] Confirm what files/components you are allowed to modify
- [ ] Create task draft directory in `/scratchpad/code_[task_id]/`

---

## Development Standards

### Code Quality
- TypeScript strict mode — no `any`, no `@ts-ignore` without documented reason
- ESLint clean — zero warnings in production code
- DRY — extract reusable logic into named functions or hooks
- No magic numbers — use named constants
- One responsibility per function/component

### Testing
- Unit test for every new function containing logic
- Integration test for any form submission or async operation
- Test file alongside source file: `Component.test.tsx` next to `Component.tsx`

### Security in Code
- Never hardcode secrets, API keys, or credentials
- Sanitize all user inputs before rendering or submitting
- Use `rel="noopener noreferrer"` on all external `<a target="_blank">` links
- Never store sensitive data in localStorage — use httpOnly cookies

### Accessibility
- All images must have meaningful `alt` attributes
- All interactive elements must be keyboard-accessible
- Color contrast must pass WCAG AA (use linting or manual check)
- Respect `prefers-reduced-motion` for all animations:
  ```css
  @media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
  }
  ```

### Performance
- Lazy load images below the fold
- Avoid importing entire libraries when only a utility is needed
- Use `loading="lazy"` on non-critical images
- Minimize layout shifts (CLS) — define image dimensions in HTML/CSS

---

## Deployment Gate

Before tagging Jasmin for review:
- [ ] No TypeScript errors (`tsc --noEmit`)
- [ ] No ESLint errors (`eslint . --ext .ts,.tsx`)
- [ ] All tests pass
- [ ] No console errors in browser
- [ ] Works on Chrome, Firefox, and Safari (latest)
- [ ] Works at 375px, 768px, and 1280px viewport widths
- [ ] All links are functional (no 404s)

After Jasmin writes "READY FOR DEPLOY":
- [ ] Move code to production paths
- [ ] Log deployment in `/memory/session_log.db`
- [ ] Update task status in `/tasks/active_tasks.json` to `completed`
- [ ] Notify Andy in session log

---

## Base44-Specific Notes
- All application code lives in the project's component files — do not touch platform scaffold files
- If a design change is impossible within Base44 constraints, document the exact limitation and escalate to Andy
- Test every change in the Base44 preview before marking as ready for review
