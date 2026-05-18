# Yoni — BuildAR Pro S1-015: type-parity assertions (last Wave 1 carry-forward)

**From:** Andy
**Dispatched:** 2026-05-18
**Task:** BUILDAR-S1-015 — closes Jasmin's other S1-006 MINOR (#2 of 2)
**Branch:** continue on `feat/orchestrator-mvp` (same as S1-013/S1-014, extend with 1 commit)
**Tester:** Jasmin

---

## Why this matters

Jasmin's original S1-006 QA found two MINORs:
1. ✅ PostgREST error sanitization — closed in S1-013/S1-014
2. ❌ **Type-parity assertion missing for ProjectStep, Asset, Event, ProjectWithSteps, UpdateSessionBody** ← this task

Without compile-time type-parity assertions, the DB schema (and PostgREST's runtime row shape) can drift from the TypeScript domain types in `packages/core-types/`. The drift would only surface at runtime when a request fails or — worse — silently corrupts data.

The fix is a small set of compile-time assertions that confirm each domain type maps cleanly to its DB-row equivalent.

---

## Success criteria

### Code
1. **Create** `packages/core-types/src/__tests__/type_parity.test.ts` (or `.test-d.ts` if you're using `tsd`; otherwise `.ts` with compile-time `expectType` shape).
2. **Add assertions for 5 types** that Jasmin called out:
   - `ProjectStep`
   - `Asset`
   - `Event`
   - `ProjectWithSteps`
   - `UpdateSessionBody`
3. **Mechanism — pick the lightest workable approach.** Three options in order of preference:
   - **(A) `expectType` helper.** Tiny TS helper that asserts type equality at compile time:
     ```ts
     type Assert<T, U> = [T] extends [U] ? ([U] extends [T] ? true : never) : never;
     const _ProjectStepParity: Assert<ProjectStep, DBProjectStepRow> = true;
     ```
     If `Assert<T,U>` ever evaluates to `never`, the line fails to compile — your CI catches the drift.
   - **(B) `tsd` package.** External library that wraps the above pattern. Only add if (A) feels too DIY.
   - **(C) Runtime Zod schema parity.** Heaviest — pair each domain type with a Zod schema and assert `z.infer<typeof schema>` matches the type. Skip unless you have a reason.
   
   Pick (A) unless something blocks.
4. **Reference the canonical DB row shape.** Either:
   - Generate types from Supabase (if there's already a generation step), OR
   - Hand-write a `DB{Type}Row` type that mirrors the schema migration column-for-column, with a short comment pointing to the migration file that defines it.
   
   Document which approach you picked at the top of the test file.

### Tests
5. The parity file is itself the test — it either compiles (PASS) or fails (FAIL). Add a single `it('type parity holds at compile time', () => expect(true).toBe(true))` so the test runner registers it.
6. Existing 19/19 tests must still pass.
7. New total target: ≥20 tests passing.

---

## What NOT to do

- Do NOT regenerate `packages/core-types` from scratch.
- Do NOT add Zod runtime validation at API boundaries that don't already have it — that's a separate Phase B task.
- Do NOT touch the S1-013/S1-014 logger or sanitizer.
- Do NOT touch the mobile-shell or other branches.
- Do NOT push to GitHub.
- Do NOT modify `tasks/active_tasks.json`.

---

## Infrastructure vs Design (per CLAUDE.md Rubric)

**Infrastructure:** If there's already a Supabase type generation step (codegen) in the monorepo, lean on it. If there isn't and adding one would be a big lift, hand-write the DB row types instead and note in the report that codegen is a Phase 2 follow-up.

**Design:** Document at the top of the parity test file: which mechanism you picked (A/B/C), why, and how to update it when the schema changes. This is a "drift detector" — its value depends on someone updating it when the schema moves. Make that obvious.

---

## Commit strategy

1 commit on `feat/orchestrar-mvp`:
```
test(core-types): compile-time type-parity assertions

- new packages/core-types/src/__tests__/type_parity.test.ts
- asserts ProjectStep, Asset, Event, ProjectWithSteps, UpdateSessionBody
  match their DB row shapes column-for-column
- closes Jasmin S1-006 MINOR-2 (Wave 1 QA carry-forward)
```

NOT pushed.

---

## Reporting

Write to `D:\Claude Playground\agents\andy\inbox\yoni_s1_015_done.md`:
- Commit SHA + git log --oneline (since branch tip)
- Files touched
- Test count (target ≥20; was 19)
- Mechanism chosen + reasoning
- How to update parity when schema changes (1 sentence)
- Status: DONE or BLOCKED

Telegram when done:
```
python "D:/Claude Playground/scripts/buildar_notify.py" done "BUILDAR-S1-015" "Type-parity assertions shipped. <test counts>. Report at agents/andy/inbox/yoni_s1_015_done.md."
```

---

## Constraints

- **Repo:** `D:\BuildAR\` on `feat/orchestrator-mvp` branch.
- **You are the ONLY agent in `D:\BuildAR\` right now.** Sequential.
- **Token discipline:** target ≤150 tool uses. This is small.

After you: Jasmin quick QA — confirms parity assertions cover the 5 types AND would fail to compile if the schema drifted.

— Andy
