# Job Search System Upgrade Plan
**Prepared by:** Andy  
**Date:** 2026-05-13  
**Source:** Analysis of 3 YouTube videos (transcripts fetched via new MCP tool)  
**Status:** Ready for Owner review → delegate to agents

---

## Source Videos Analyzed

| # | Title | Key Domain |
|---|-------|-----------|
| 1 | How to Track Your Job Applications (Teal Job Tracker) | Pipeline management & organization |
| 2 | I wish every Job Seeker would watch this | AI-powered prompts for every search step |
| 3 | Everything You Need to Know About ATS | ATS mechanics & CV optimization |

---

## Key Insights Extracted

### From Video 1 — Pipeline & Tracking
- Think of job search **like a sales funnel**: Bookmarked → Applying → Applied → Interviewing → Negotiating
- **Friction kills**: if saving a job takes effort, people stop doing it — the tool must be effortless
- **Contacts linked to jobs**: track who you know at each company inside the job card
- **Sub-task checklist per job**: "customized resume ✓", "identified recruiter ✓", "got referral ✓"
- **Follow-up reminders**: set a date, get notified — never let an application go cold silently
- **Excitement rating**: score each job 1–5, sort funnel by excitement to prioritize
- **Daily cadence**: 30 min/day adding new jobs — habit, not marathon sessions

### From Video 2 — AI Prompts at Every Step
- **77% of job seekers using AI still had to heavily edit** because prompts were too generic — **prompt quality is the differentiator**
- **Networking**: download LinkedIn PDF → feed to AI → extract 3 achievements → personalize outreach (never send generic "I like your content" messages)
- **Coffee chat prep**: feed the person's profile → get 10 tailored questions that prove you did homework
- **Interview questions to ask**: feed the JD → get 5 questions only *that* interviewer can answer (not Googleable)
- **Thank you emails**: include a specific thing from the interview + reiterate transferable skills
- **Salary negotiation roleplay**: simulate the full conversation before it happens — reduces fear, gives the right words
- Chain-of-thought ("let's think step by step") dramatically improves AI output quality

### From Video 3 — ATS Reality
- **98% of Fortune 500** and most SMBs use ATS — there is no bypassing it
- Recruiters filter by: **skills (76%)**, job title (55%), credentials (51%)
- **Target 75% keyword match** — not 100% (looks keyword-stuffed and inauthentic)
- **ATS-killing formatting**: tables, images, columns, fancy fonts, headers/footers in the document
- **Job title must match JD title** — if you're a "Social Media Specialist" applying for "Social Media Strategist," update your title
- AI scoring (auto-ranking) is growing — candidates get tiered automatically before a recruiter even looks
- **Knockout questions** auto-filter before human review — answer carefully

---

## Gap Analysis: What We Have vs. What We Need

| Area | Current State | Gap |
|------|--------------|-----|
| Job pipeline | Basic stage column in dashboard | No kanban view, no sub-task checklist, no excitement rating |
| Contact tracking | None | No contacts linked to job cards |
| Follow-up reminders | None | No reminder/follow-up date system |
| ATS scoring | Cole estimates score manually | No automated keyword match % |
| AI prompts | Ad-hoc, per request | No built-in prompt library for networking, interviews, negotiation |
| CV–JD keyword gap | None | No visual diff of CV keywords vs JD keywords |
| Salary negotiation | None | No AI roleplay tool |
| Job title matching | None | No check: does CV title match JD title? |
| Transcript capability | None (before today) | **Fixed — MCP server now registered** |

---

## Proposed Improvements — Prioritized

### TIER 1 — High Impact, Moderate Effort (Do First)

#### 1.1 Dashboard: Kanban Pipeline View
**Owner:** Rex  
**What:** Add a kanban board view alongside the existing table — columns: Bookmarked / Preparing / Applied / Interviewing / Offer  
**Why:** Visual pipeline = clearer sense of where you are in the funnel, faster triage  
**Success criteria:** Drag cards between stages, toggle between kanban and table view

#### 1.2 Dashboard: Excitement Rating per Job
**Owner:** Rex  
**What:** Add a 1–5 star rating field to each job card. Allow sorting by rating  
**Why:** Not all jobs are equal — prioritize excitement, not just recency  
**Success criteria:** Rating visible in both kanban and table view; sortable

#### 1.3 Dashboard: Sub-Task Checklist Within "Preparing" Stage
**Owner:** Rex  
**What:** When a job is in "Preparing/Applying" stage, show a mini-checklist:  
- [ ] Identified recruiter  
- [ ] Customized CV  
- [ ] Sent connection request  
- [ ] Got referral  
- [ ] Cover letter ready  
**Why:** Ensures nothing is skipped before hitting Apply  
**Success criteria:** Checklist persists per job; completion % visible on card

#### 1.4 Dashboard: Follow-Up Reminder Field
**Owner:** Rex + Mack  
**What:** Add a "Follow-up date" field per job. When the date arrives, surface the job at the top of the dashboard with a visual alert  
**Why:** Applications go cold because people forget to follow up — this eliminates that  
**Success criteria:** Jobs with overdue follow-up dates highlighted in red at dashboard top

---

### TIER 2 — High Impact, Higher Effort (Do Next)

#### 2.1 ATS Keyword Match Score — Automated
**Owner:** Yoni + Jasmin QA  
**What:** Build a tool that compares the current CV text against a pasted JD and returns:
- Match % (target: 75%)
- Keywords present in JD but missing from CV (gap list)
- Keywords in CV not in JD (noise list)
- Job title match: Yes/No  
**Integration:** Expose as a panel in the dashboard — paste JD, get score instantly  
**Why:** 76% of recruiters filter by skills; Cole currently estimates this manually  
**Success criteria:** Score shown within 3 seconds of pasting JD; gap list is actionable

#### 2.2 Dashboard: Contacts Sub-Panel per Job
**Owner:** Rex  
**What:** Each job card gets a "Contacts" section — add name, LinkedIn URL, role, last contacted  
**Why:** Networking is the most effective channel; tracking contacts per opportunity prevents duplicates and dropped threads  
**Success criteria:** Contacts visible in job detail panel; sortable by date contacted

#### 2.3 AI Prompt Toolkit — Built Into Dashboard
**Owner:** Yoni + Cole  
**What:** A "Job Prep" tab in the dashboard with 6 pre-built prompt templates:
1. **Networking outreach** — paste LinkedIn profile PDF → get personalized connection message
2. **Coffee chat questions** — paste contact's profile → get 10 tailored questions
3. **Interview questions to ask** — paste JD → get 5 sharp questions for end of interview
4. **Thank you email** — paste interview notes → get personalized follow-up
5. **Salary negotiation roleplay** — input offer + target → simulate negotiation dialogue
6. **LinkedIn connection request** — paste person's top achievements → get standout message  
**Why:** 59% of job seekers using AI get offers; prompt quality is the differentiator  
**Success criteria:** Each template pre-fills with context from the active job card (company, JD, CV)

---

### TIER 3 — Good-to-Have (Do After Tier 1+2)

#### 3.1 ATS Format Checker for CVs
**Owner:** Jasmin + Cole  
**What:** Automated checklist on every generated CV:
- No tables ✓/✗
- No images ✓/✗
- No columns ✓/✗
- No headers/footers in document body ✓/✗
- Standard fonts only ✓/✗
- All dates in consistent format ✓/✗
**Why:** Bad formatting = invisible to ATS regardless of content quality  
**Success criteria:** Checklist generated with every CV; Cole cannot deliver a CV without passing this check

#### 3.2 Daily Job Search Dashboard Widget
**Owner:** Rex  
**What:** A "Today's Actions" widget at top of dashboard showing:
- Jobs added this week vs. target (target: 5/week)
- Applications sent this week
- Follow-ups overdue
- Next interview date  
**Why:** Builds daily habit; 30 min/day consistently beats marathon sessions  
**Success criteria:** Widget updates in real-time; targets configurable

#### 3.3 Job URL Auto-Parser
**Owner:** Mack  
**What:** Paste any job URL (LinkedIn, Indeed, Google Jobs, Glassdoor) → auto-parse job title, company, location, JD text into a new job card  
**Why:** Manual data entry is the #1 friction killer — same reason Teal's Chrome extension works  
**Success criteria:** Supports 4+ major job boards; parses in under 5 seconds

---

## Delegation Map

| Task ID | Title | Agent | Depends On |
|---------|-------|-------|-----------|
| JOBSEARCH-001 | Kanban pipeline view | Rex | — |
| JOBSEARCH-002 | Excitement rating | Rex | — |
| JOBSEARCH-003 | Sub-task checklist | Rex | JOBSEARCH-001 |
| JOBSEARCH-004 | Follow-up reminder | Rex + Mack | JOBSEARCH-001 |
| JOBSEARCH-005 | ATS keyword match score | Yoni → Jasmin QA | — |
| JOBSEARCH-006 | Contacts sub-panel | Rex | JOBSEARCH-001 |
| JOBSEARCH-007 | AI Prompt Toolkit | Yoni + Cole | JOBSEARCH-005 |
| JOBSEARCH-008 | ATS format checker | Jasmin + Cole | — |
| JOBSEARCH-009 | Daily widget | Rex | JOBSEARCH-001 |
| JOBSEARCH-010 | Job URL auto-parser | Mack | — |

---

## Recommended Execution Order

**Phase 1 (This week):** JOBSEARCH-001, 002, 008 — Rex builds kanban + rating; Jasmin adds ATS format check to Cole's workflow  
**Phase 2 (Next week):** JOBSEARCH-003, 004, 005 — sub-tasks, reminders, ATS score engine  
**Phase 3 (Following week):** JOBSEARCH-006, 007, 009, 010 — contacts, AI toolkit, daily widget, URL parser

---

## Infrastructure Note

**YouTube Transcript MCP server** is now registered and active (takes effect next session restart).  
Location: `D:\Claude Playground\scripts\mcp_youtube_transcript\server.py`  
Tools: `get_youtube_transcript(video_url_or_id, language)` and `list_available_languages(video_url_or_id)`  
Use: Any time Inon shares YouTube links for LinkedIn posts, planning, or research — transcript first, then analyze.
