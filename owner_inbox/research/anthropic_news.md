# Anthropic / Claude — Latest News (2026-05-09)

## Key Updates

- **Claude Opus 4.7 launched (April 16, 2026)** — Most capable generally available model, priced same as Opus 4.6 ($5/$25 per MTok input/output). Available on API, Bedrock, Vertex AI, and Microsoft Foundry. Notable gains in advanced software engineering, especially complex multi-step tasks.
- **Vision resolution 3x upgrade** — Opus 4.7 accepts images up to 2,576px on the long edge (was ~800px), enabling real work with dense screenshots, technical diagrams, and design specs.
- **New `xhigh` reasoning effort level** — Finer control between reasoning depth and latency, sitting above the previous `high` setting.
- **`/ultrareview` command** — Launched as public research preview in Claude Code; detailed non-interactive code review via `claude ultrareview [target]` subcommand.
- **Auto Mode for Claude Code** — Safer long-running permissions option that lets Claude make decisions with fewer interruptions; research preview for Team users, Enterprise/API rollout coming soon.
- **SpaceX Colossus 1 compute deal** — 300+ MW capacity, 220,000+ NVIDIA GPUs. Enabled Anthropic to double Claude Code rate limits for Pro/Max/Team/Enterprise plans and remove peak-hour throttling.
- **API rate limits massively expanded** — Tier 1: 1500% increase to max input tokens/min, 900% increase to max output tokens/min. Pro/Max five-hour limits doubled.
- **Enhanced file system memory** — Multi-session persistence for Opus 4.7, allowing continuity across long-running agentic tasks.
- **Cyber safeguards** — Security-sensitive applications can request verified professional access to Opus 4.7 for offensive security use cases.
- **Claude Code 2.1.x changelog (April 23 – May 7):** Vim visual mode, `/usage` command (merges `/cost` + `/stats`), custom named themes, MCP tool hooks, `claude project purge`, OAuth code paste in terminal, PowerShell fallback on Windows, plugin URL fetch, Ctrl+R history search across all projects.

## Angles for LinkedIn Posts

- **"Your AI just got a 3x zoom."** Opus 4.7's vision resolution jump is underrated — PMs reviewing dense wireframes, dashboards, or spreadsheet screenshots can now actually hand those to Claude. Angle: what work tasks become viable that weren't before?
- **"Anthropic just 10x'd their rate limits overnight."** The SpaceX compute deal isn't just infrastructure news — it's a signal about who wins the AI infrastructure race and what happens when model companies own their compute stack. Angle: forces the question of whether AWS/Google partnerships are sustainable long-term.
- **"Auto Mode is the feature that will make most PMs nervous."** Claude Code can now run long jobs with fewer human approvals. The real PM question isn't "is it safe?" — it's "what happens to my review process when AI is autonomous by default?" Angle: the governance gap nobody is talking about.

## Raw Notes

- Opus 4.7 shows "better instruction-following" and "more professional outputs for creative professional tasks" — relevant for writing/brand use cases Sage handles.
- Finance, legal, and technical benchmarks called out specifically — enterprise angle for LinkedIn.
- SpaceX deal gives Anthropic independence from hyperscaler throttling — strategic inflection point worth noting.
- `/ultrareview` is available now in Claude Code if Inon wants to test it directly.
- "Code with Claude 2026" event ran May 6 (Simon Willison live blog) — may be worth fetching full recap for deeper detail.
- Advisor tool now in beta on Claude Platform (separate from Claude Code).

---
*Sources: [Anthropic News](https://www.anthropic.com/news/claude-opus-4-7) · [Let's Data Science — rate limits](https://letsdatascience.com/news/anthropic-increases-claude-code-and-api-usage-limits-735fd0ac) · [Releasebot Claude Code](https://releasebot.io/updates/anthropic/claude-code) · [Releasebot Anthropic](https://releasebot.io/updates/anthropic)*
