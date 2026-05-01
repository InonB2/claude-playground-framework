# LinkedIn Posts — Refreshed & Ready for Review
**Prepared by:** Sage  
**Date:** 2026-04-30  
**Status:** Awaiting Owner sign-off before publishing

---

## Post 1 — The Feature We Killed

Most PMs ship features. I've spent 10 years learning to kill them.

At TouchE, we built an AI interactive video platform. Raised $2.5M. Onboarded Paramount, JVP, Lionsgate.

The product decision I'm most proud of? One we never shipped.

We had a social viewing feature in the works — co-watch with friends, live reactions, shared playlists. Engineering was excited. Early users said they wanted it. It looked great in every deck.

We killed it 3 weeks before launch.

Here's what changed my mind:

When I stopped reading surveys and started watching actual behavior, the pattern was unmistakable. Users who engaged with interactive overlays watched 34% longer. Users who watched "socially" left after 8 minutes. Every single time.

The feature was solving the problem people *said* they had. Not the one they *actually* had.

That's the discipline that's hardest to teach: killing something you've already built. Something the team believed in. Something that looked right on paper.

That moment — more than any feature we shipped — shaped how I think about product.

What's the hardest product decision you've ever had to make?

#ProductManagement #ProductLeadership #StartupLife #AIProduct

---

**Posting note:** Best on Tuesday–Thursday, 8–10am Israel time.

---

## Post 2 — When AI Starts Remembering

Every AI session, you start from zero.

No memory of why you chose that architecture. No recall of the decision you made last Tuesday. No context from three debugging sessions ago.

You spend the first 10 minutes of every conversation re-briefing a tool that should already know you.

I've been working on changing that. I built a persistent database layer into my AI workflow — so the assistant can read and write structured data that carries across sessions. Decisions get logged. Patterns accumulate. Agents can hand state to each other without a full briefing every time.

In practice, it means:
- Preferred patterns and constraints don't disappear overnight
- Project decisions build into queryable knowledge over time
- The "context tax" of every new session gets smaller, not larger

Here's the product take I keep coming back to:

Memory isn't a feature. It's the difference between a chatbot and a system you can actually trust with ongoing work.

We talk a lot about AI getting smarter. But the bigger unlock isn't intelligence — it's continuity. An AI that remembers what you decided last week is more useful than one that's slightly smarter but starts fresh every morning.

That's the shift I'm watching: from AI as a tool you pick up, to AI as a teammate that learns.

What would you build if your AI never forgot?

#AgentAI #ProductLeadership #AIEngineering #BuildInPublic #FutureOfWork

---

**Posting note:** Pairs well with a screenshot of your actual workflow or terminal interface.

---

## Post 3 — The Document Is Dead. Long Live Judgment.

For years, producing a polished document was a skill.

Formatting a financial model. Structuring a board deck. Getting the slides right. These were things that took time — real time — and signaled competence.

That's changing.

I've been experimenting with AI that doesn't just help draft content — it generates finished, formatted, exportable files directly. PDFs. Decks. Spreadsheets. Ready to send.

Not outlines. Not bullet points. The actual deliverable.

Brief it → get a stakeholder-ready document. "Analyze this and build the spreadsheet" becomes a single step. One prompt, multiple formats — send the exec the PDF, send the team the editable version.

Here's the product implication nobody's talking about: the document was never the point. It was always the thinking behind it.

When a finished file is a byproduct of a 30-second conversation, the real skill shifts. It's not formatting fluency anymore. It's knowing what to ask for, what good looks like, and whether the output actually holds up under pressure.

Judgment. Context. A high bar.

That's the new stack for knowledge workers. And most teams aren't ready for it.

What's the first thing you'd take off your plate?

#AIProductivity #FutureOfWork #ProductLeadership #Gemini #GoogleWorkspace

---

**Posting note:** Works well with a clean visual showing AI generating multiple file formats.

---

*All posts written in first person as Inon Baasov. No source or tool references. Ready for sign-off.*

---

## Post 4 — Gemini Files

I uploaded 6 receipts from a work trip.

One prompt: "Create an Excel file with all my expenses — date, amount, category — formatted for QuickBooks."

Gemini built it. I downloaded it. Done.

Then I went a step further. I had the same trip data in Google Sheets. New chat. I asked: "Find my expenses log in Drive and build me a PDF report with graphs — show where I spent the most."

It found the file. It read it. It generated a PDF with a pie chart and a bar chart. Most of my spend was food — three visits to the same breakfast spot.

I didn't move any files. I didn't format anything. I didn't even open Sheets.

Here's what I keep thinking about: the document was always a container for a decision. Now the container is a byproduct.

The interesting question isn't "what can it generate?"

It's: when producing a polished output takes 30 seconds, what does the human add?

The answer I've landed on — the thing that doesn't compress: knowing what's worth asking for, and knowing whether the result is actually right.

That judgment is the job now.

What would you point Gemini at first?

#AIProductivity #Gemini #ProductLeadership #FutureOfWork #GoogleWorkspace

---

**Posting note:** Best paired with a screenshot of a downloaded PDF or formatted spreadsheet. Tuesday–Thursday, 8–10am Israel time.

---

## Post 5 — Ghost.build

I just found a way to let an AI agent destroy a database without actually destroying anything.

The tool is Ghost.build. Free. One install command. Connect to Claude Code with `ghost mcp install` — that's the full setup.

Here's what changed for me:

I built a test database with 100,000 customers, 500,000 orders, and 1 million order items. Intentionally no indexes — I wanted it slow. Then I told the agent to fork it three times in parallel and try a different optimization strategy on each: targeted indexes, materialized view, denormalized summary table.

It benchmarked all three. Picked the fastest. Applied it to the main database. Discarded the forks.

The base database was never touched during the experiment.

Then I tried something messier. I created a user database with intentionally broken phone numbers — some null, some malformed, the rest in five different formats. I asked the agent to fork it 10 times simultaneously and run a different cleanup strategy on each: drop bad rows, backfill, regex normalization, quarantine tables, and six more.

All 10 forks ran in parallel. It compared the results. Combined the two best approaches. Applied to main.

10 experiments. Zero risk. Zero cost. About 3 minutes.

The mental shift this created: when databases are free and disposable, you stop treating them like they're precious. You just experiment.

That's exactly how I want to work with AI agents — not carefully, but freely.

Ghost.build is on the free tier: 100 compute hours a month, 1TB storage, unlimited databases and forks. I haven't paid for it once.

Worth trying if you're building anything with agents right now.

#AIAgents #DeveloperTools #ClaudeCode #BuildInPublic #AIEngineering

---

**Posting note:** Strong post for the technical/developer segment of Inon's audience. Works well with a terminal screenshot showing the fork commands or benchmark output.
