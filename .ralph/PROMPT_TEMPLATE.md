# Ralph Loop — Prompt Template

Copy this template when starting a Ralph Loop. Fill in all bracketed sections before dispatching.

---

## Task
[What needs to be done — be specific about the output format, scope, and any constraints]

## Files / Context
[List key files the agent should read at the start of each iteration to get current state. Example:]
- `tasks/active_tasks.json` — current task queue
- `agents/[name].md` — agent persona
- `[output_file_path]` — the file being produced (read to see previous iteration's work)

## Success Criteria
[Measurable definition of done. Each item should be a checkable boolean:]
- [ ] [Criterion 1 — specific and verifiable]
- [ ] [Criterion 2 — specific and verifiable]
- [ ] [Criterion 3 — specific and verifiable]

## Completion Signal
Output `<promise>DONE</promise>` when ALL success criteria above are met.
Output `<promise>BLOCKED</promise>` if you encounter a blocker requiring human judgment — and include a one-paragraph description of the blocker.

Do NOT output either signal until you have verified each criterion.

## Max Iterations
[n] — if not converged by iteration [n÷2], re-read the success criteria and adjust your approach.

---

## Usage notes for Andy

1. Before dispatching, confirm success criteria are measurable by the agent without owner input.
2. Set max iterations conservatively — you can always re-run if needed.
3. After loop completes, review the final output against success criteria before marking the task done.
4. If the loop emits `<promise>BLOCKED</promise>`, surface the blocker to Inon immediately.
5. See `.ralph/guardrails.md` for full rules on when to use (and not use) Ralph Loop.
