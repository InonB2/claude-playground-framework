# QA Audit — Cole Skill Edits
**Auditor:** Jasmin (Security & Logic Auditor)
**Date:** 2026-05-08
**Files reviewed:**
- `.claude/commands/session-handoff.md`
- `.claude/commands/start.md`

---

## File 1: session-handoff.md

**Result: FLAG**

### Issues

- **FLAG — Scope ban inconsistency (lines 1 vs 3)**
  Line 1 bans *reading* "any files outside this conversation." Line 3 bans *using content* from prior sessions or external files. These are logically different constraints. An AI could read a file and then claim it only incorporated in-conversation content, satisfying line 3 while violating line 1. The two statements should be collapsed into one consistent rule.
  **Fix:** Replace both with a single sentence: "Do NOT read any files during this command. Use only what is already in this conversation's context."

- **FLAG — `$CURRENT_DATE` is an unresolved placeholder (line 10)**
  The format header uses the literal string `$CURRENT_DATE`. An AI following the template mechanically may write that exact string instead of the actual date. There is no instruction to substitute it.
  **Fix:** Replace `$CURRENT_DATE` with: `[today's date — write the actual date here, e.g. 2026-05-08]` or add an explicit instruction: "Replace $CURRENT_DATE with today's date before writing."

- **FLAG — "Next Session: Pick Up Here" has no None-fallback (lines 29–32)**
  Every other section has an explicit `None.` fallback for the empty case. This section mandates "minimum 3 items" with no escape hatch for sessions where fewer than 3 meaningful next-steps exist. This can force fabricated or padded items.
  **Fix:** Add: "If fewer than 3 genuine next-steps exist, list only what is real. Do not pad. Write 'None.' if there is truly nothing."

- **ADVISORY — 150-line hard cap is not structurally enforceable (line 1)**
  "Hard cap 150 lines" is an instruction, not a mechanism. There is nothing stopping an AI from producing more lines. The cap is advisory in practice.
  **Fix (optional):** Add a note: "If you are approaching 150 lines, truncate 'Next Session' and 'Decisions Made' first — those are lower priority than 'What Shipped' and 'Left Unfinished'." This at least gives a truncation strategy.

### Sections with correct None-fallback
- Decisions Made: PASS
- What Shipped: PASS
- Left Unfinished: PASS
- New Owner Blockers: PASS

---

## File 2: start.md

**Result: FLAG**

### Issues

- **FLAG — No fallback if PowerShell clock-check fails (step 5)**
  The instruction says "ALWAYS check the system clock... run PowerShell: `(Get-Date).Hour`" and "Never guess." If the tool call fails (unavailable tool, permission error, unsupported environment), the AI has no valid path forward — it cannot guess and cannot proceed without a greeting. This is a dead end.
  **Fix:** Add a fallback: "If the PowerShell call fails or returns no result, omit the time greeting entirely and proceed with a neutral 'Hello, Inon.'"

- **FLAG — Greeting line format is underspecified (step 6)**
  Step 6 says "bullet points (not a prose paragraph)" and lists four bullet items, but does not clarify whether the greeting line itself (e.g., "Good morning, Inon.") is a bullet or a standalone header line. Models will produce inconsistent output — some will bullet the greeting, others will not.
  **Fix:** Specify explicitly: "Output the greeting as a standalone line (not a bullet), then list the four bullets below it."

- **FLAG — "Active agent count (14)" is hardcoded in the instruction (step 6)**
  The parenthetical `(14)` locks the output value. If the roster changes, this produces stale output without any signal to the AI that it should verify the count.
  **Fix:** Replace `(14)` with: "(read from roster.md or use current count)" — or remove the parenthetical entirely and let the AI derive the count from the data it already read.

- **ADVISORY — "if space" is ambiguous (step 6)**
  "Task queue count (with IDs if space)" does not define what "space" means. Space in the bullet? Space in the terminal? This produces variable output across sessions.
  **Fix:** Replace with: "(include up to 5 task IDs; omit IDs if there are more than 5)" or any concrete threshold.

- **ADVISORY — "unprocessed drops" undefined (step 3)**
  Step 3 says "note any unprocessed drops" without defining what makes a file processed vs. unprocessed. This is low-risk but could cause a new agent instance to over-flag or under-flag items.
  **Fix:** Add: "(a file is unprocessed if it has not been referenced in QUICK_STATUS.md or the active task list)"

### What works well
- The PowerShell command `(Get-Date).Hour` is correct and valid on Windows 11 — returns an integer 0–23, maps cleanly to the defined greeting bands.
- The short-circuit at the top (skip re-reading files if handoff already in context) is a good efficiency guard with no logical flaws.
- Step 6 correctly names the four required bullet items, providing structure without over-constraining the output.

---

## Summary

| File | Result | Issues |
|------|--------|--------|
| session-handoff.md | FLAG | 3 flags, 1 advisory |
| start.md | FLAG | 3 flags, 2 advisories |

Neither file is a FAIL — they are functional as-is and their core logic is sound. The flags are precision gaps that would produce inconsistent or incorrect output in edge cases. Recommend Cole apply the fixes above before these files are treated as stable.
