# JOBSEARCH-007 — AI Prompt Toolkit — DONE (Yoni)

**Date:** 2026-05-14
**Status:** Ready for Vera QA
**File touched (only one):** `D:\Claude Playground\dashboard\index.html`
**Do NOT commit yet — Andy commits after Vera signs off.**

---

## Tab name chosen

**"AI Toolkit"** — short, sits in the tab bar between **ATS Match** and **LinkedIn**.
Follows the existing `data-tab` / `switchTab` / `#tab-XXX` convention exactly — `switchTab()` was **not** modified and needs no special-casing. The only tab-specific branch in `switchTab` (`body.classList.toggle('tab-linkedin', ...)`) correctly stays LinkedIn-only.

## Architecture — prompt generator, no AI call

As specified: the dashboard is a static HTML file with no backend and no API key. The toolkit **does not call an AI**. It is a pure prompt assembler:
1. User picks 1 of 6 scenarios from a left-rail list.
2. User fills the variable fields (or auto-fills from a saved job / CV).
3. "Generate prompt" assembles a high-quality prompt string into a **`<textarea readonly>`**.
4. "Copy to clipboard" puts it on the clipboard to paste into ChatGPT/Claude.

All toolkit code is namespaced `tk*` / `.tk-*` / `#tk*` and `TK_TEMPLATES` — self-contained to the new tab + its CSS + its JS, so Mack's upcoming job-URL parser won't collide.

## How auto-fill works

Two pickers in the tab (`#tkJobPicker`, `#tkCvPicker`):

- **Auto-fill from job** (`tkAutofillJob`) — picks a saved job and populates any field tagged `autofill:'company'` or `autofill:'role'` in the active template. Pickers are kept live: `renderJobs()` now calls `tkPopulateJobPicker()` and `renderCvs()` calls `tkPopulateCvPicker()` (both guarded with `try/catch` + `typeof` checks, same belt-and-suspenders pattern as my ATS `populateAtsCvPicker` hook).
- **Auto-fill background from CV** (`tkAutofillCv`) — reuses the exact ATS approach: for an HTML CV it `fetch()`es the file and strips to plain text via the existing `_atsStripHtml()`; for a PDF CV (no fetchable text) it falls back to the CV's name/role/industry/notes metadata and tells the user to expand it. Populates any field tagged `autofill:'background'`.

**Documented tradeoff — the JD is not auto-filled.** Job cards in the data model store `company`, `role`, `url`, `notes` but **no JD text field** (confirmed in `seedDefaultJobs`). So for the two templates with a JD field (Interview questions, Thank-you indirectly), the JD must be pasted manually — the field hint says so, and `tkAutofillJob` shows a hint message explaining it. Adding a `jdText` field to the job model was out of scope (it'd need migration + touches Rex's/Mack's area). Company/role still auto-fill; JD is the only paste-it-yourself field. If Andy wants full JD auto-fill later, the clean fix is a `jdText` field on the job model — a small separate task, ideally bundled with Mack's URL parser since that's where JD text would get captured anyway.

Auto-fill never silently clobbers a field the user already typed into (`_tkSetByAutofill` skips non-empty fields; the CV background fill asks via `confirm()` before replacing).

## XSS handling

- The assembled prompt is written **only** via `textarea.value` — never `innerHTML`. User-pasted text (including `<script>alert(1)</script>`) appears as **literal inert text** inside the readonly textarea, which is exactly correct for a prompt the user copies.
- Rail items and picker `<option>`s are built with `document.createElement` + `textContent` / `createTextNode` — no `innerHTML` with user data.
- Verified: pasting `<script>alert(1)</script><img src=x onerror=alert(1)>` into inputs produces **zero** `<img>`/`<script>` nodes in `#tab-toolkit`, the payload survives as literal text in the result, and no `onerror`/`alert` fires.

## localStorage

Optional persistence implemented under its **own key** `andy_toolkit_inputs` (shape: `{templateId: {fieldKey: value}}`). Last-used inputs per template are restored when you reopen a template. Uses the existing `_safeJsonParse` helper; all writes are `try/catch`-wrapped so persistence can never break the UI. **No existing localStorage keys touched** — verified `andy_jobs` / `andy_cvs` still intact after toolkit use.

---

## The 6 prompt templates (actual prompt text — for Cole/Andy wording review)

Each prompt embeds chain-of-thought ("let's think step by step") and, where the research showed it helps, an "unorthodox / lesser-known" framing. `{{...}}` below marks where the user's field values are injected.

### 1. Networking outreach
Fields: target person's LinkedIn profile text (req), your background (req, autofill from CV), what you want from the connection (optional).

```
You are an expert networking coach. Help me write a personalized LinkedIn outreach message.

Let's think step by step:
1. Read the target person's profile below and identify their top 3 concrete achievements or distinctive experiences — be specific (numbers, projects, roles), not generic.
2. Read my background and find ONE genuine, specific point of overlap or relevance between us.
3. Draft a short outreach message (90-130 words) that: opens by referencing ONE specific achievement from step 1 (not flattery, not "I love your content"), states the honest reason I'm reaching out, and ends with a low-friction ask.
4. Then list the 2 other achievements you found, so I can use them in follow-ups.

Constraints: warm but professional, no buzzwords, no "I hope this finds you well", no exclamation marks. Sound like a real person. Prioritize specific, lesser-known details from their profile over obvious headline facts — specificity is what gets a reply.

=== TARGET PERSON'S PROFILE ===
{{profile}}

=== MY BACKGROUND ===
{{background}}

=== WHAT I WANT FROM THE CONNECTION ===
{{goal | "(not specified — keep it relationship-first, no hard ask)"}}
```

### 2. Coffee chat questions
Fields: the contact — profile/role/company (req), the field/role you're targeting (req, autofill from job role), what you most want to learn (optional).

```
You are a career coach preparing me for a coffee chat / informational interview.

Let's think step by step:
1. Study the contact's background below and note what is distinctive about their path, their company, and their current role.
2. Consider the field I'm targeting and what I most want to learn.
3. Generate exactly 10 questions I should ask in the conversation.

The questions must:
- Be specific to THIS person's experience — referencing their actual path, company, or decisions — so it's obvious I did my homework.
- Be open-ended (not yes/no), and impossible to answer with a generic Google search.
- Mix categories: their career decisions, the day-to-day reality of the role, the team/company, industry shifts, and advice for someone in my position.
- Avoid questions that are really disguised asks for a job. This is relationship-building.

Prioritize unorthodox, lesser-known angles over the obvious "what does a typical day look like" questions. Order them from easy-rapport to more reflective. For each question, add a one-line note on why it works.

=== THE CONTACT ===
{{contact}}

=== FIELD / ROLE I AM TARGETING ===
{{field}}

=== WHAT I MOST WANT TO LEARN ===
{{focus | "(not specified — cover a balanced spread)"}}
```

### 3. Interview questions to ask
Fields: role title (req, autofill from job), company (optional, autofill from job), job description (req — paste manually), who is interviewing me (optional).

```
You are an interview strategist. Help me prepare questions to ask at the END of an interview.

Let's think step by step:
1. Read the job description below and identify the parts that are ambiguous, unusually demanding, or hint at an underlying challenge the team is facing.
2. Consider who is interviewing me and what they would uniquely know.
3. Generate exactly 5 questions I should ask when the interviewer says "do you have any questions for us?"

The questions must:
- Only be answerable by someone who works there — not findable on the company website, Glassdoor, or via Google.
- Show that I read the JD closely and am thinking about the actual work, not just trying to get hired.
- Surface real signal for me: what success looks like in 6 months, why the role is open, what the hardest part of the job is, how decisions actually get made, what would make them NOT hire someone.
- Be confident but not presumptuous.

Favor sharp, slightly unorthodox questions over safe ones — the goal is to be memorable and to actually learn whether I want this job. For each question, add a one-line note on what a good vs. concerning answer would sound like.

=== ROLE ===
{{role}}

=== COMPANY ===
{{company | "(not specified)"}}

=== JOB DESCRIPTION ===
{{jd}}

=== WHO IS INTERVIEWING ME ===
{{interviewer | "(not specified)"}}
```

### 4. Thank-you email
Fields: a specific thing from the interview (req), your transferable skills/background (req, autofill from CV), role title (optional, autofill from job), interviewer name (optional).

```
You are a professional communication coach. Help me write a post-interview thank-you email.

Let's think step by step:
1. Read the specific thing from the interview below — this is the anchor of the email.
2. Read my transferable skills and find the ONE that most directly connects to that specific thing.
3. Draft a thank-you email under 200 words.

The email must:
- Reference the specific moment from the interview concretely, so it is obviously not a template.
- Use that moment as a natural bridge to reiterate ONE concrete reason I am a strong fit (tied to my background).
- Be genuine and confident. Do NOT flatter or suck up to the interviewer. Do not over-thank. No "I would be honored". No exclamation marks.
- Close simply, signalling continued interest without desperation.

Give me the email, then a one-line note on the single most important word or phrase to personalize before sending.

=== SPECIFIC THING FROM THE INTERVIEW ===
{{specific}}

=== MY TRANSFERABLE SKILLS / BACKGROUND ===
{{background}}

=== ROLE ===
{{role | "(not specified)"}}

=== INTERVIEWER NAME ===
{{name | "(not specified — use a neutral greeting)"}}
```

### 5. Salary negotiation roleplay
Fields: role title (req, autofill from job), company (optional, autofill from job), the offer amount (req), your target amount (req), your leverage/context (optional). **Includes a follow-up prompt** the user pastes after the first roleplay.

```
You are an experienced compensation negotiation coach. Role-play a salary negotiation with me so I can rehearse before the real call.

Let's think step by step:
1. First, briefly assess my situation: the gap between the offer and my target, and how realistic my target is given the leverage I described.
2. Then role-play the full negotiation as a back-and-forth dialogue. You play the hiring manager / recruiter; I play the job seeker. Make the hiring manager realistic — they push back, cite budget, ask why I deserve more. Cover the whole arc: my counter, their response, the back-and-forth, and a landing point.
3. Throughout, write the job seeker's lines the way I should actually deliver them: polite but firm, never apologetic, anchored on value not need, comfortable with silence.
4. After the dialogue, list the 3 highest-leverage phrases I should memorize, and the 2 most common mistakes to avoid.

Prioritize practical, slightly unorthodox negotiation tactics that most candidates don't know over generic advice. Be realistic — do not let me "win" too easily.

When you finish, end with this line exactly: "Reply 'push harder' and I will run a second round where you aim for the top of your range."

=== ROLE ===
{{role}}

=== COMPANY ===
{{company | "(not specified)"}}

=== THE OFFER ===
{{offer}}

=== MY TARGET ===
{{target}}

=== MY LEVERAGE / CONTEXT ===
{{leverage | "(not specified — assume modest leverage and play it realistically)"}}

--- FOLLOW-UP PROMPT (paste this after the first roleplay) ---
Push harder. Run the negotiation again, but this time the job seeker aims for the very top of the range ({{target}} or above). Show how to hold firm when the hiring manager resists, how to use silence, and how to get there without burning the relationship. End by telling me the single moment in the conversation where the negotiation was actually won or lost.
```

### 6. LinkedIn connection request
Fields: the person's top achievements or profile (req), what makes you relevant to them (req, autofill from CV), how you came across them (optional).

```
You are a networking expert. Write me a LinkedIn connection-request note.

Let's think step by step:
1. From the person's achievements/profile below, pick the ONE detail most worth referencing.
2. From what makes me relevant, pick the ONE thread that makes connecting make sense for THEM, not just me.
3. Write a connection-request note.

Hard constraints:
- Maximum 300 characters (LinkedIn's limit). Aim for 200-280. Count the characters and tell me the count.
- Reference the one specific detail from step 1 — no generic flattery, no "I'd like to add you to my network".
- Give a real, honest reason for connecting.
- Warm, human, confident. No buzzwords. No exclamation marks.

Give me 3 variations at different tones (warm / direct / curious), each under 300 characters with its character count. Favor a memorable, slightly unorthodox opening line over a safe one.

=== THE PERSON'S TOP ACHIEVEMENTS / PROFILE ===
{{achievements}}

=== WHAT MAKES ME RELEVANT TO THEM ===
{{relevance}}

=== HOW I CAME ACROSS THEM ===
{{context | "(not specified)"}}
```

---

## Success criteria — status

| Criterion | Status |
|---|---|
| New tab loads, no console errors | OK — jsdom loads the page, runs `init()`/`tkInit()` clean, no errors thrown |
| All 6 templates selectable | OK — left-rail with 6 items; clicking each renders its fields + sets exactly one `.active` |
| Each template generates a clean, complete, copy-pasteable prompt | OK — all 6 builders produce 200+ char prompts; verified the prompt text by hand (above) |
| Copy-to-clipboard works | OK — `navigator.clipboard.writeText` with an `execCommand` fallback for non-secure contexts; clipboard content === result textarea |
| Auto-fill from a job works | OK — company/role auto-fill from a picked job; JD is the documented paste-it-yourself field (not in the data model) |
| No regression in other tabs | OK — all 5 existing tabs present + activatable; `switchTab` unchanged & generic; LinkedIn special-case still fires; `andy_jobs`/`andy_cvs` localStorage intact |
| No XSS | OK — `<script>`/`<img onerror>` payload stays literal inert text in the readonly textarea; zero injected nodes; no `alert`/`onerror` fired |

## How I tested

1. **Static parse check** — extracted the inline `<script>` (~120 KB), `new Function(js)` parses with no syntax errors.
2. **Sandbox builder test (Node `vm`)** — 25 checks: all 6 templates defined with correct ids, every builder produces a string prompt, prompts embed chain-of-thought + the injected field values, salary follow-up + linkedin 300-char rule present.
3. **Full DOM integration test (jsdom)** — 62 checks, all pass: tab structure, `switchTab` generic behavior + no regression on other tabs, rail renders 6 items, every template renders fields + generates a prompt, required-field validation (`.tk-missing`), **XSS inert** (literal text, zero injected nodes, no execution), copy-to-clipboard, auto-fill job populates company/role and correctly leaves JD empty, both pickers populate, localStorage persistence under its own key, existing keys untouched.
   Test files were worktree-local scratch and removed after passing (not committed).

---

## Findings (Team Quality Rubric — infrastructure vs design)

### Infrastructure
- **None.** Single static HTML file, no backend, no deps, no CI/CD. Inline JS still parses clean after the additions. No infrastructure changes required.
- One environment note: `navigator.clipboard` requires a secure context (https or `localhost`). The dashboard is opened via `file://` or `localhost` static server — I added an `execCommand('copy')` fallback so copy still works under `file://` and older browsers. Not a defect, just defensive.

### Design
- **JD is not in the job data model** — see "Documented tradeoff" above. Company/role auto-fill; JD is paste-it-yourself with a clear hint. Recommend a `jdText` field on the job model as a future small task, bundled with Mack's JOBSEARCH-010 URL parser (that's the natural capture point for JD text).
- **Left-rail selector (not 6 cards / not a dropdown)** — UX call: a rail keeps all 6 scenarios visible at once (discoverability) without the vertical cost of 6 cards, and is faster than a dropdown for switching while comparing. Matches the dashboard's dense, info-first aesthetic.
- **Result lives in a readonly `<textarea>`** — deliberate, and it doubles as the XSS guard: user text can only ever land in `.value`, never `innerHTML`. The user can also hand-edit the prompt before copying, which is a nice side benefit.
- **Auto-fill is non-destructive** — never silently overwrites typed content; CV background fill asks via `confirm()` first. Avoids the frustration of a picker nuking work.
- **Persistence is opt-in-shaped** — last inputs per template restore automatically but under an isolated key with fully guarded writes; worst case the feature silently no-ops, the UI never breaks.

## Malfunctions found / prevention
None during implementation. **Process note for prevention:** I initially ran my smoke test against the worktree copy of `dashboard/index.html` and saw every check fail — the edits had (correctly) gone to the main-repo path the brief specified (`D:\Claude Playground\dashboard\index.html`), not the worktree copy. Caught it immediately via a `grep -c`. Prevention: when working from a git worktree but editing a file by absolute path outside it, always confirm with a quick `grep` which file actually received the edit before testing. No code impact — the right file was edited all along.

## Files
- Modified: `D:\Claude Playground\dashboard\index.html` — one file. Additions: 1 tab button, 1 `#tab-toolkit` panel, ~85 lines CSS (`.tk-*`), ~1 JS module (`TK_TEMPLATES` + ~15 `tk*` functions), 1 `tkInit()` call in `init()`, 2 guarded picker-sync hooks in `renderJobs`/`renderCvs`. No edits to engine, ATS code, or other tabs.

## Not committed
Per the brief, I did **not** run git commit. Andy commits after Vera QA signs off.

## Recommended next step for Andy
1. Route to Vera for UI QA — she should open the dashboard, click the AI Toolkit tab, generate all 6 prompts, test copy + auto-fill, and paste the XSS payload to confirm it's inert.
2. Optionally route the 6 prompt texts above to Cole for a wording pass (career-coach voice review) — the prompts are field-tested for structure but Cole owns CV/writing voice.
3. After sign-off: commit, update `tasks/active_tasks.json` (JOBSEARCH-007 → done).

— Yoni
