# Ralph Loop — Guardrails

Ralph Loop is an iterative AI development technique where the same prompt is fed to Claude repeatedly until a completion signal is detected. Each iteration reads its own previous work from disk, enabling progressive self-correction over multiple passes.

Reference: https://ghuntley.com/ralph/

---

## When to use Ralph Loop vs. direct agent dispatch

**Use Ralph Loop when:**
- The task has a clear, measurable definition of done that Claude can evaluate itself
- The output benefits from self-correction (e.g., writing, code generation, structured data)
- The task is well-scoped and does not require owner judgment mid-stream
- Early drafts are expected to be imperfect and iteration adds real value

**Use direct agent dispatch when:**
- The task requires a single, fast, deterministic response (no benefit to iteration)
- The task involves live system actions (API calls, deployments, data writes to production)
- The task requires owner decision-making at intermediate steps
- Success criteria cannot be evaluated autonomously by the agent

---

## Max iteration guidelines

| Task type | Recommended max iterations |
|---|---|
| Short writing tasks (posts, summaries) | 5–10 |
| Structured document generation | 10–15 |
| Complex code or multi-file output | Up to 20 |
| Research synthesis | 10–15 |

Never set max iterations above 20 without explicit owner approval. If the task is not converging by iteration 10, stop and reassess the prompt.

---

## Completion promise conventions

Every Ralph Loop prompt MUST instruct the agent to emit one of two signals when finished:

- `<promise>DONE</promise>` — all success criteria have been met; loop should terminate
- `<promise>BLOCKED</promise>` — a blocker requiring human judgment has been encountered; loop must pause

The loop runner (skill: `/ralph-loop`) detects these signals in the agent's output to determine whether to continue or halt.

Do NOT use any other signal format. Consistency is required for reliable detection.

---

## Tasks Ralph Loop MUST NOT be used for

1. **Tasks requiring owner judgment** — anything that depends on Inon's personal preference, approval, or a decision that only the owner can make
2. **Tasks touching production data** — any write operation to a live database, live API, or published content (Supabase production, Base44 live app, published LinkedIn posts, live website)
3. **Tasks with unclear success criteria** — if you cannot write a measurable definition of done before starting, do not use Ralph Loop; use `/plan` first
4. **Multi-agent coordination tasks** — Ralph Loop runs one agent in a tight loop; tasks requiring handoffs between agents should use standard delegation
5. **Irreversible actions** — file deletions, git force-pushes, credential rotations, billing changes

---

## Prompt template guidance

Every Ralph Loop prompt must include:

1. **Explicit task description** — what needs to be produced, not how to produce it
2. **Key files to read at iteration start** — so the agent always has current context
3. **Measurable success criteria** — specific, checkable conditions the agent can evaluate itself
4. **Completion promise instruction** — always the exact `<promise>DONE</promise>` / `<promise>BLOCKED</promise>` convention
5. **Max iterations** — set before starting; do not increase mid-loop without owner approval

Use `D:\Claude Playground\.ralph\PROMPT_TEMPLATE.md` as the canonical starting point for every Ralph Loop delegation.
