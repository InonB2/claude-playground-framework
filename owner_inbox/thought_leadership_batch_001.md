# Thought Leadership Batch 001
**Author:** Inon Baasov (written in first person)
**Prepared for:** Portfolio website — Journal section
**Date:** 2026-05-01
**Posts:** 3
**Status:** Ready to publish

---

## Post 1 — Why I Stopped Building Features

**Publish date:** 2026-05-02
**Meta description:** The hardest skill in product isn't shipping — it's knowing when to stop. What TouchE taught me about the discipline of subtraction.
**Hashtags:** #ProductManagement #ProductLeadership #StartupLife #CPO #AIProduct

---

### The discipline nobody teaches you

Most product managers learn how to build.
Nobody teaches you how to stop.

I spent the first few years of my career measuring my value by output. Features shipped. Roadmap items closed. Velocity. It looked productive. It felt productive. And it was slowly making the product worse.

At TouchE — the AI interactive video platform I co-founded and led as CPO — we raised $2.5M and onboarded Paramount, JVP, and Lionsgate. For most of that run, I was adding. More overlays. More social mechanics. More ways for viewers to interact. More reasons the product was interesting.

The inflection point came from a feature we never shipped.

We had a co-watch experience deep in development: shared playlists, synchronized playback, live reactions. Engineering was energized. The concept tested well. It made every pitch deck look more interesting.

Three weeks before launch, I killed it.

Not because it was broken. Because I stopped reading surveys and started watching actual behavior. Users who engaged with the interactive video overlays — our core product — watched 34% longer. Users who watched content "socially" were gone in under eight minutes. Consistently. The feature was solving the problem people said they had. Not the one they actually had.

That distinction — between the problem users describe and the problem they demonstrate — is the whole job.

Here's what I've learned since: every feature you ship is a tax. It taxes engineering, QA, support, onboarding, and future changes. Most of the time, adding is easy. Saying no is the hard part. Removing something you've already built, something the team believed in, something that looks right on every slide — that's where real product judgment lives.

The best product decisions I've made are the ones that don't appear in any release note. The scope cuts that kept the core tight. The pivots away from things that users asked for but didn't need.

Subtraction is a skill. It doesn't come naturally. But it's the one that separates the PMs who ship clean, compounding products from the ones who ship complicated, slowing ones.

Build less. Obsess over what stays.

---

## Post 2 — The AI Stack That Actually Runs My Work in 2026

**Publish date:** 2026-05-03
**Meta description:** Not a tool list — a real workflow. How I use Claude, Cursor, Supabase, and automation to build a system that remembers what it knows.
**Hashtags:** #AIProductivity #BuildInPublic #AgentAI #FutureOfWork #ProductLeadership

---

### The stack I actually use (not the one that sounds good in a tweet)

I was skeptical of the "AI workflow" genre for a long time. Most of it is a tool list dressed up as a system. ChatGPT for this. Notion AI for that. A dozen disconnected experiments that don't compound into anything.

What changed my mind wasn't a new tool. It was building a workflow with memory.

Here is what I actually run, and why each layer matters.

**The core: Claude as the orchestrator.** I don't use Claude as a chatbot. I've built a team of persistent AI agents — each with a defined role, a file of context, and a clear scope. A researcher, a coder, a copywriter, a security auditor. They don't start from zero. They read their own files, reference prior decisions, and pass structured handoffs to each other. The orchestrator role — which I call Andy — reads active tasks and delegates. Every session starts with a status, not a blank screen.

**The coding layer: Cursor.** When code needs to happen, it happens in Cursor, where the model has full codebase context. The agent writes, I review, Cursor executes. The loop is tight enough that I'm not switching contexts constantly. What used to take an afternoon takes a focused hour.

**The memory layer: Supabase + SQLite.** This is the one most people skip — and it's the most important. Every significant decision, every agent output, every pattern we've observed gets logged. Not in a chat thread that disappears. In a structured database that persists. When I start a new session, the agents query what they already know. The "context tax" — the 10 minutes you spend re-briefing a tool that should remember you — shrinks every week.

**The sync layer: GitHub + automation scripts.** Everything is version-controlled. Daily syncs, auto-commits, session logs pushed to the repo. The system self-documents. Six months from now, I can open any session log and see exactly what was decided and why.

The insight that ties this together isn't about any individual tool. It's about the difference between using AI and building with AI. Tools are point solutions. Systems compound.

A system that remembers what it knows is fundamentally different from a capable assistant that resets every morning. The first one gets more useful over time. The second one stays flat.

That's the architecture I'm optimizing for: continuity, not just capability.

---

## Post 3 — What the Best PMs I've Met Have in Common

**Publish date:** 2026-05-04
**Meta description:** After 10+ years in product, four traits separate the great PMs from the competent ones. None of them are on any framework list.
**Hashtags:** #ProductManagement #ProductLeadership #Leadership #CPO #CareerGrowth

---

### Four things I've noticed after ten years

After more than a decade in product — as a builder, a co-founder, and someone who has interviewed, worked alongside, and hired PMs across multiple domains — I've stopped believing that great product management comes from frameworks.

The best PMs I've worked with share four things. None of them appear in any certification syllabus.

**1. They slow down when everyone else speeds up.**

The most dangerous moment in a product cycle is when the team reaches consensus fast. It usually means something important wasn't said. The best PMs I know are the ones who call a pause at that exact moment. "We all just agreed very quickly. What are we not looking at?" I've seen that question save two launches. I've seen what happens when no one asks it.

**2. They protect the team's attention like it's a scarce resource — because it is.**

There's a certain kind of PM who is constantly responsive. Always in the thread. Always in the room. Always adding a comment. It looks like engagement. It's actually noise. The standout PMs I've worked with understand that their team's attention is the product's most finite input. They kill unnecessary meetings. They batch feedback. They create quiet. The teams around them ship faster — not because they're pushed harder, but because they're interrupted less.

**3. They know exactly what they're not building — and they'll tell you why.**

Every great PM I've met can articulate, clearly and without hesitation, the things they've decided not to do and why. Not as a list of constraints. As a strategic position. "We're not building X because our user does Y, and if we built X we'd be optimizing for the wrong moment." That level of clarity is rare. Most roadmaps are a prioritized list of what people asked for. The best ones reflect a deliberate theory of what the product should not become.

**4. They have a point of view under pressure.**

Stakeholders push. Engineers push back. Timelines compress. In those moments, some PMs get diplomatic to the point of losing the thread entirely. The ones I'd work with again are the ones who get clearer under pressure, not blurrier. They don't become inflexible. But they don't abandon their read of the situation to make the room comfortable. That combination — confident in the insight, open on the implementation — is what I've come to think of as genuine product leadership.

None of these are teachable through frameworks. They come from reps, from watching decisions land and fail, from building enough product that you start to recognize the patterns before they fully emerge.

The most important thing I've learned: great PMs aren't born with better instincts. They've just made more mistakes in high-stakes situations and stayed curious enough to learn from them.

---

*End of Batch 001 — 3 posts, ready for website journal section.*
