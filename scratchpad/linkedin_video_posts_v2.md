# LinkedIn Video Posts v2
**Author:** Sage  
**Date:** 2026-05-01  
**Status:** Draft — awaiting review

---

## Ralph Loop — Extraction Notes

### Gemini video (AtTLckneAQU) — key specifics:
1. One prompt creates a finished Google Doc saved directly into Drive — preview via card, open via link
2. Upload 6–7 receipts → "create an Excel file with all expenses, dates, amounts, for QuickBooks" — downloads ready
3. New chat: "find my Las Vegas trip expenses log in Google Sheets and create a PDF with graphs" — it accessed Drive, built pie + bar charts, exported a PDF ($179 trip, most spent at The Egg Shop)
4. Canvas mode: click "create canvas" → interactive dashboard view of the same data, toggle back to raw data
5. Current limitation: editing an existing Drive file creates a V2 duplicate instead of editing in-place

### Ghost.build video (vJBAzdOACD8) — key specifics:
1. Install: one command, `ghost login` (GitHub auth only — no separate signup), then `ghost mcp install` — choose Claude Code, Cursor, or Codex
2. Verify in Claude Code with `/mcp` — Ghost server visible with tools: create database, execute SQL, fork, delete, list
3. Fork experiment: "shop analytics" DB with 100k customers / 500k orders / 1M order items — forked 3 in parallel, tested targeted indexes vs. materialized view vs. denormalized summary table, benchmarked all three, applied winner to base DB
4. 10 parallel forks for data cleanup: intentionally messy phone column (3% null, 2% malformed, rest mixed formats), 10 strategies ran simultaneously — drop bad rows / backfill / regex normalization / quarantine tables — combined the two best, applied to base DB
5. Free tier: 100 compute hours/month, 1TB storage, unlimited databases and forks — zero cost anxiety

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

---

*Posts written in first person as Inon Baasov. No video, creator, or source references. Ready for sign-off.*
