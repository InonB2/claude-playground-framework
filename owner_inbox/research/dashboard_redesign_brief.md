# Andy C&C Dashboard — Full Redesign Brief
**Author:** Lena (Senior UI/UX Designer)  
**For:** Rex (Frontend Developer)  
**Date:** 2026-05-08  
**Scope:** Full visual redesign + 4 new feature areas

---

## 1. Design Direction

### Concept: "Mission Control, Refined"

The current dashboard is functional but reads as a first draft. This redesign pushes it into the territory of a premium internal tool — the kind of thing you'd see at a well-funded startup's war room. The aesthetic direction:

- **Dark command center** — keep the `#0A0A0B` black base, but add depth through micro-layering
- **Typographic precision** — replace Inter with **JetBrains Mono** (monospace) for IDs, metadata, and numeric data; **Syne** for tab labels and headings; keep **Inter** only for body copy and long-form text
- **Intentional glow system** — status colors (orange, cyan, green) used as *light sources*, not flat badges. The glows communicate urgency at a glance
- **Spatial rhythm** — tighter baseline grid (4px unit), more generous section separation (32px vs 20px), deliberate asymmetry in the notification layer
- **Motion as information** — the pulse animation on blockers should communicate *category* (owner-caused vs external), not just "something is happening"

---

## 2. Color Palette — Revisions

Keep the existing CSS variable structure. Extend with:

```css
:root {
  /* Existing — keep as-is */
  --bg:           #0A0A0B;
  --surface:      #131316;
  --surface2:     #1C1C21;
  --surface3:     #24242B;
  --border:       #2C2C35;
  --border-hover: #3E3E4D;
  --text:         #E4E4EF;
  --text-secondary: #9494A8;
  --muted:        #6B6B7E;
  --cyan:         #22D3EE;
  --cyan-dim:     rgba(34,211,238,0.12);
  --green:        #34D399;
  --green-dim:    rgba(52,211,153,0.12);
  --yellow:       #FACC15;
  --yellow-dim:   rgba(250,204,21,0.12);
  --red:          #F87171;
  --red-dim:      rgba(239,68,68,0.15);
  --orange:       #F97316;
  --orange-dim:   rgba(249,115,22,0.15);
  --purple:       #A78BFA;

  /* NEW — Owner-blocker accent (brighter, warmer orange) */
  --owner-block:         #FF6B00;          /* hotter than --orange */
  --owner-block-dim:     rgba(255,107,0,0.18);
  --owner-block-border:  rgba(255,107,0,0.45);
  --owner-block-glow:    0 0 16px rgba(255,107,0,0.35);

  /* NEW — LinkedIn brand blue (for CMS tab indicator) */
  --linkedin:      #0A66C2;
  --linkedin-bright: #2D8CF0;
  --linkedin-dim:  rgba(10,102,194,0.2);

  /* NEW — Hebrew rule indicator (flame amber) */
  --hebrew-flag:   #F59E0B;
  --hebrew-flag-dim: rgba(245,158,11,0.15);

  /* NEW — Notification bell */
  --bell-badge:    #EF4444;
  --bell-badge-glow: 0 0 10px rgba(239,68,68,0.5);

  /* NEW — Surface shimmer (for card hover enhancement) */
  --shimmer-start: rgba(255,255,255,0.02);
  --shimmer-end:   rgba(255,255,255,0.0);
}
```

**Key changes from current palette:**
- Owner-caused blockers get `--owner-block` (#FF6B00) — visually distinct from the regular `--orange` used for the "Needs You" column
- LinkedIn CMS gets its own brand blue — never confused with cyan task actions
- Hebrew rule indicator uses amber (`#F59E0B`) — warm enough to be unmissable, different enough from orange to read as a "rule" rather than a "status"

---

## 3. Typography

| Context | Font | Weight | Size | Notes |
|---|---|---|---|---|
| Tab labels, section headings | **Syne** | 700 | 13–15px | Google Fonts, geometric sans |
| Topbar title "Andy" | **Syne** | 800 | 16px | All-caps optional |
| Body text, card titles | **Inter** | 400–600 | 13–14px | Keep as-is |
| IDs, timestamps, badges | **JetBrains Mono** | 500 | 10–11px | Monospaced, tabular-nums feel |
| LinkedIn post body textarea | **Inter** | 400 | 14px | Direction: RTL for Hebrew |
| Hebrew rule banner text | **Syne** | 700 | 12px | All-caps |

**Google Fonts import to update:**
```html
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
```

---

## 4. Layout & Chrome Changes

### 4.1 Top Bar — Elevated

The topbar grows from 58px to **64px** to accommodate a notification bell and breathe more.

```
[ A ] Andy // Command Center  |  [ 🔔 3 ]  [ ⚡ Waiting on you  2 ]  [ Last updated 09:01 ]
```

**Left side:** Logo + title (unchanged)  
**Right side (new order, left to right):**
1. Notification bell with red badge count
2. "Waiting on you" owner-blocker badge (orange, pulsing) — *only appears when count > 0*
3. Last-updated timestamp

**Remove:** The existing `needs-you-badge` in the topbar (it becomes redundant once the bell exists). The "Waiting on you" badge is specifically for owner-caused blockers — separate from "Needs You" Kanban column.

### 4.2 Tab Bar — Redesigned

Current tabs: `Tasks | Job Applications | CV Versions`  
New tabs: `Tasks | Job Applications | CV Versions | LinkedIn`

Tab bar height: keep 44px  
Tab typography: switch to **Syne 600**  
Active tab indicator: keep the cyan underline, but make it 2.5px and extend with a subtle glow:
```css
.tab-btn.active {
  color: var(--cyan);
  border-bottom: 2.5px solid var(--cyan);
  text-shadow: 0 0 12px rgba(34,211,238,0.4);
}
```

**LinkedIn tab visual treatment:** When the LinkedIn tab is active, the active indicator becomes the LinkedIn blue (`--linkedin-bright`) instead of cyan. This reinforces the context shift.

### 4.3 Filter Bar — Polish Only

No structural changes. Typography update: use **JetBrains Mono** for the "All" count badge in the top-right.

---

## 5. Kanban Board (Tasks Tab) — Blocker Differentiation

This is the most important UX change in the Tasks tab.

### 5.1 Current problem

The "Blocked" column and the "Needs You" column both use orange-adjacent colors. Owner-caused blockers (items where *Inon* hasn't responded) are visually indistinct from external blockers (third-party dependency, agent waiting on tool output, etc.).

### 5.2 Solution: Two-tier blocker system

**Tier A — External Blocked** (current col-blocked, grey): Agent is waiting on something outside Inon's control. Remains grey. No change.

**Tier B — Owner Blocked** ("Waiting on You"): Inon specifically needs to act. Visually treated as the hottest item on the board — hotter than the existing "Needs You" column.

#### Owner-Blocked column spec

The `col-blocked` column is split. The Blocked column now has two visual sub-sections:

**Option A (Recommended): Sub-header inside Blocked column**

```
┌─────────────────────────────────┐
│ ●  BLOCKED               [4]    │  ← grey header, existing style
├─────────────────────────────────┤
│ ┌ WAITING ON YOU ──────────── ┐ │  ← amber/orange section divider
│ │ [card] card with --owner-   │ │
│ │ block border + glow         │ │
│ └─────────────────────────────┘ │
│ [regular blocked cards below]   │
└─────────────────────────────────┘
```

**Owner-blocked card visual spec:**
```css
.card.owner-blocked {
  border-left-color: var(--owner-block);
  background: linear-gradient(135deg, rgba(255,107,0,0.06) 0%, var(--surface2) 60%);
  box-shadow: var(--owner-block-glow);
}

.card.owner-blocked .card-note::before {
  content: 'WAITING ON YOU · ';
  color: var(--owner-block);
  font-family: 'JetBrains Mono', monospace;
}
```

**Owner-blocked section divider (inside Blocked column):**
```css
.owner-blocked-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--owner-block);
  text-transform: uppercase;
  border-bottom: 1px solid var(--owner-block-border);
  background: var(--owner-block-dim);
}
```

**If there are no owner-blocked tasks:** hide the sub-header entirely. No empty states.

### 5.3 Card hover upgrade (all cards)

Add a subtle radial shimmer on hover:
```css
.card:hover::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(ellipse at 50% 0%, var(--shimmer-start), var(--shimmer-end));
  pointer-events: none;
}
```

### 5.4 Column headers — elevation

Add a faint gradient to column headers that reinforces the accent color:
```css
.col-needs-you .col-header  { background: linear-gradient(90deg, rgba(249,115,22,0.08), transparent); }
.col-inprogress .col-header { background: linear-gradient(90deg, rgba(34,211,238,0.06), transparent); }
.col-done .col-header       { background: linear-gradient(90deg, rgba(52,211,153,0.06), transparent); }
```

---

## 6. Notification Bell — Component Spec

### Placement

Right side of topbar, before the "Waiting on you" badge.

### Visual spec

```
[🔔]   ← icon, 20px
  [3]  ← red badge, 16px circle, top-right corner of bell
```

```css
.notif-bell {
  position: relative;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--surface2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
  color: var(--text-secondary);
  font-size: 16px; /* or SVG icon */
}

.notif-bell:hover {
  border-color: var(--border-hover);
  background: var(--surface3);
  color: var(--text);
}

.notif-bell-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 16px;
  height: 16px;
  background: var(--bell-badge);
  box-shadow: var(--bell-badge-glow);
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 1.5px solid var(--bg);
}
```

### Behavior

On click: opens a dropdown panel anchored below the bell (not a modal). Max height: 320px, scrollable.

**Notification panel:**
```
┌──────────────────────────────────┐
│  NOTIFICATIONS             [×]   │
├──────────────────────────────────┤
│  🔴  Task ABC needs your input   │
│      Tasks · 2 minutes ago       │
├──────────────────────────────────┤
│  🟡  LinkedIn post in Draft      │
│      LinkedIn · 1 hour ago       │
├──────────────────────────────────┤
│  🔴  Job App: Microsoft aging    │
│      Jobs · 3 days ago           │
└──────────────────────────────────┘
```

Panel CSS: `background: var(--surface2); border: 1px solid var(--border-hover); border-radius: 10px; min-width: 300px; box-shadow: 0 16px 48px rgba(0,0,0,0.5);`

Each notification item:
- Left: colored dot (red = needs action, yellow = informational)
- Primary text: 13px Inter 500
- Secondary text: 11px JetBrains Mono, `--muted` color, "Source · time ago"
- Hover: `background: var(--surface3)`
- Click: navigates to the relevant tab and scrolls to item

**Badge logic:** Count = tasks in "Needs You" column + tasks in owner-blocked section + LinkedIn posts needing approval. Badge hidden when count is 0. When count > 9, display "9+".

---

## 7. LinkedIn CMS Tab — Full Spec

### 7.1 Tab-level persistent Hebrew rule indicator

This is a mandatory design requirement. It must be **unmissable** while the LinkedIn tab is active.

**Implementation: Sticky banner below the tab bar**

```
┌──────────────────────────────────────────────────────────────────┐
│  🔤  RULE: All LinkedIn posts must be written in Hebrew only.     │
│         Posts in English will not be published.                   │
└──────────────────────────────────────────────────────────────────┘
```

```css
.linkedin-hebrew-banner {
  background: var(--hebrew-flag-dim);
  border-bottom: 2px solid var(--hebrew-flag);
  padding: 10px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--hebrew-flag);
  position: sticky;
  top: 102px; /* 64 topbar + 44 tabbar */
  z-index: 180;
}

.linkedin-hebrew-icon {
  font-size: 16px;
  flex-shrink: 0;
}
```

The banner is sticky — it stays visible as the user scrolls through posts. It does NOT appear on any other tab.

### 7.2 Layout

The LinkedIn tab uses a **two-column master-detail layout** on wide screens (> 900px), single column on mobile.

```
┌─────────────────┬────────────────────────────────────────────────┐
│                 │                                                  │
│  LEFT PANEL     │  RIGHT PANEL (post detail / editor)             │
│  (pipeline      │                                                  │
│   list)         │  [ No post selected — click a post to view ]    │
│                 │                                                  │
│  340px wide     │  flex: 1                                         │
└─────────────────┴────────────────────────────────────────────────┘
```

On mobile (< 900px): left panel becomes a full-width scrollable list; tapping a post opens a slide-up panel (same pattern as the existing modal).

### 7.3 Left panel — Pipeline list

**Section headers per pipeline stage:**

| Stage | Accent color | Icon |
|---|---|---|
| Idea | `--muted` / grey | 💡 |
| Draft | `--yellow` | ✏️ |
| Approved | `--cyan` | ✓ |
| Posted | `--green` | 🌐 |

Each stage section is collapsible (click to toggle). Default: all open.

**Post list item (in left panel):**
```
┌────────────────────────────────────┐
│ ●  [STATUS BADGE]  May 15          │
│    Post title / first line preview │
│    [tag: Career] [tag: Personal]   │
└────────────────────────────────────┘
```

```css
.li-post-item {
  padding: 11px 14px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.12s;
  border-left: 3px solid transparent;
}

.li-post-item.selected,
.li-post-item:hover {
  background: var(--surface3);
}

.li-post-item.selected {
  border-left-color: var(--linkedin-bright);
}

/* Status-specific left border when selected */
.li-post-item[data-status="Idea"]     { border-left-color: var(--muted); }
.li-post-item[data-status="Draft"]    { border-left-color: var(--yellow); }
.li-post-item[data-status="Approved"] { border-left-color: var(--cyan); }
.li-post-item[data-status="Posted"]   { border-left-color: var(--green); }
```

**Backlog / Ideas queue**: The "Idea" stage section has a "+ Add Idea" button in its header. Ideas show only title + date — no body preview.

**Toolbar above left panel:**
```
[ + New Post ]     [Search posts...]    [Filter: All stages ▼]
```

### 7.4 Right panel — Post editor / viewer

**View mode (post already selected):**

```
┌──────────────────────────────────────────────────────┐
│  [DRAFT]  · Created May 5  · Scheduled May 15         │
│                                                        │
│  Post Title ────────────────── [Edit] [Move stage ▼]  │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Post body text (Hebrew, RTL)                    │ │
│  │  ...                                             │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  SCHEDULED DATE     POSTED DATE          POSTED URL    │
│  2026-05-15         —                    —             │
│                                                        │
│  PERFORMANCE NOTES                                     │
│  (empty)                                               │
│                                                        │
│  VERSION HISTORY ──────────────────────────────────    │
│  v3 · May 8, 09:01  "Revised tone, added hashtags"    │
│  v2 · May 7, 18:30  "First draft after review"        │
│  v1 · May 5, 12:00  "Initial idea"                    │
└──────────────────────────────────────────────────────┘
```

**Edit mode (inline, no separate modal):**

- Title becomes a text input
- Body becomes a `<textarea dir="rtl" lang="he">` with RTL alignment enforced via CSS. Background: slightly lighter than `--surface3` to signal editable state
- All fields (scheduled date, notes, performance URL) become inline inputs
- Save button: `--cyan` style (consistent with rest of dashboard)
- "Move Stage" dropdown uses LinkedIn blue accent when stage = Approved or Posted

**Post body textarea spec:**
```css
.li-post-body-edit {
  width: 100%;
  min-height: 220px;
  background: var(--surface3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text);
  direction: rtl;
  text-align: right;
  resize: vertical;
  transition: border-color 0.15s;
}

.li-post-body-edit:focus {
  outline: none;
  border-color: var(--linkedin-bright);
  box-shadow: 0 0 0 3px rgba(45,140,240,0.12);
}
```

**RTL note for Rex:** The post body textarea must have `dir="rtl"` attribute set in HTML. The browser handles bidirectional text — no JS needed. The Hebrew rule banner above reinforces this at all times.

### 7.5 Version history component

Each version is stored as `{ version: 3, timestamp: "...", note: "..." }`.

```css
.li-version-history {
  display: flex;
  flex-direction: column;
  gap: 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.li-version-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 14px;
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  transition: background 0.1s;
  cursor: default;
}

.li-version-item:last-child { border-bottom: none; }
.li-version-item:hover { background: var(--surface3); }

.li-version-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  color: var(--muted);
  min-width: 24px;
  text-transform: uppercase;
}

.li-version-note { flex: 1; color: var(--text-secondary); }

.li-version-time {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--muted);
  white-space: nowrap;
}
```

### 7.6 LinkedIn status badge palette

```css
.li-status-badge { border-radius: 5px; padding: 2px 8px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }

.li-status-badge.idea     { background: rgba(107,114,128,0.15); color: var(--muted);   border: 1px solid rgba(107,114,128,0.3); }
.li-status-badge.draft    { background: var(--yellow-dim);       color: var(--yellow);  border: 1px solid rgba(250,204,21,0.35); }
.li-status-badge.approved { background: var(--cyan-dim);         color: var(--cyan);    border: 1px solid rgba(34,211,238,0.35); }
.li-status-badge.posted   { background: var(--green-dim);        color: var(--green);   border: 1px solid rgba(52,211,153,0.35); }
```

### 7.7 Data schema (for Rex's JS/JSON data layer)

```json
{
  "posts": [
    {
      "id": "LI-001",
      "title": "What I learned shipping AR features in 3 months",
      "body": "...(Hebrew text)...",
      "status": "Draft",
      "scheduledDate": "2026-05-15",
      "postedDate": null,
      "postedUrl": null,
      "performanceNotes": "",
      "tags": ["Career", "Product"],
      "versions": [
        { "version": 1, "timestamp": "2026-05-05T12:00:00Z", "note": "Initial idea" },
        { "version": 2, "timestamp": "2026-05-07T18:30:00Z", "note": "First draft after review" }
      ]
    }
  ]
}
```

Persist to a local JSON file (`dashboard/linkedin_posts.json`) using the same pattern as `tasks.json` and `jobs.json`. Rex should use the existing serve.py / file-read pattern already in the codebase.

---

## 8. Component Upgrade Specs (Cross-Cutting)

### 8.1 Cards — visual weight hierarchy

Current cards are all the same visual weight. Introduce size tiering:

| Card type | Treatment |
|---|---|
| Critical priority | Add `box-shadow: 0 0 0 1px rgba(239,68,68,0.25), 0 4px 16px rgba(0,0,0,0.4)` at rest (not just hover) |
| Owner-blocked | Permanent left-glow via `box-shadow` on `--owner-block` |
| High priority | Current hover glow, but also faint at rest: `box-shadow: 0 0 0 1px rgba(249,115,22,0.15)` |

### 8.2 Modal — micro-upgrade

The modal priority bar (3px line at top) should animate in:
```css
.modal-priority-bar {
  transform-origin: left;
  animation: expandBar 0.3s ease 0.1s both;
}

@keyframes expandBar {
  from { transform: scaleX(0); opacity: 0; }
  to   { transform: scaleX(1); opacity: 1; }
}
```

### 8.3 Empty states — more character

Replace plain `<div class="empty-state">` text with a structured empty state:

```
[ icon ]
  No tasks here
  Tasks in this column will appear when the team updates their status.
```

Font: the "No tasks here" line in **Syne 600 14px**; description in Inter 12px `--muted`.

### 8.4 Scrollbars — upgrade

```css
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: linear-gradient(to bottom, var(--border-hover), var(--muted)); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan); }
```

### 8.5 Focus rings — accessible + on-brand

```css
*:focus-visible {
  outline: 2px solid var(--cyan);
  outline-offset: 2px;
  border-radius: 4px;
}
```

---

## 9. Interaction Patterns & Animations

### 9.1 Page load stagger

Cards should stagger in on initial render (not every filter change):

```css
.card {
  animation: cardIn 0.2s ease both;
}

/* Apply via JS: card.style.animationDelay = `${index * 30}ms` */

@keyframes cardIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### 9.2 Tab switch animation

Content of each tab fades in when selected:

```css
.tab-content.active {
  animation: tabFadeIn 0.15s ease;
}

@keyframes tabFadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### 9.3 Notification panel

Open: slides down from topbar with `transform: translateY(-8px) → translateY(0)` + opacity fade. Close: reverse.

### 9.4 Owner-blocked pulse

The pulse animation on owner-blocked cards should differ from the regular "Needs You" pulse — use a **ring-expand** rather than a dot:

```css
@keyframes ownerPulse {
  0%   { box-shadow: 0 0 0 0 rgba(255,107,0,0.5); }
  70%  { box-shadow: 0 0 0 8px rgba(255,107,0,0); }
  100% { box-shadow: 0 0 0 0 rgba(255,107,0,0); }
}

.card.owner-blocked {
  animation: ownerPulse 2.5s ease-out infinite;
}
```

---

## 10. Tab Structure Summary

| Tab | Existing? | Changes |
|---|---|---|
| Tasks | Yes | Blocker differentiation, card upgrades, column header gradients |
| Job Applications | Yes | No structural changes. Typography upgrade only (Syne headers). |
| CV Versions | Yes | No structural changes. Typography upgrade only. |
| LinkedIn | **New** | Full CMS spec — see Section 7 |

---

## 11. Responsive Breakpoints

| Breakpoint | Behavior |
|---|---|
| > 1280px | Full 4-column Kanban; LinkedIn in 2-column split |
| 900–1280px | 2-column Kanban; LinkedIn in 2-column split (narrower left panel) |
| 640–900px | 2-column Kanban; LinkedIn in single column |
| < 640px | Single column Kanban; LinkedIn single column, post detail as slide-up modal |

---

## 12. Accessibility Notes

- All interactive elements (bell, tabs, filter buttons) must have `:focus-visible` rings
- LinkedIn post body textarea needs `lang="he"` and `dir="rtl"` attributes for screen reader / input method compatibility
- Notification panel must be dismissable via Escape key
- The Hebrew rule banner must not be dismissable — it should always be visible on the LinkedIn tab
- Color contrast: all text on dim backgrounds verified at minimum 4.5:1. The `--muted` text (`#6B6B7E`) on `--surface2` (`#1C1C21`) is borderline — Rex should check this pair and bump muted to `#757587` if needed

---

## 13. Files Rex Will Need to Create / Modify

| File | Action |
|---|---|
| `dashboard/index.html` | Full redesign — styles + HTML structure |
| `dashboard/linkedin_posts.json` | New — sample data, empty array is fine to start |
| `dashboard/serve.py` (or equivalent) | Add route to serve `linkedin_posts.json` via the same GET/POST pattern as `tasks.json` |

---

## 14. Design Tradeoffs & Decisions Made

### Tradeoff 1: Keep dark theme, don't change the brand

**Decision:** The dark theme is a strength. Switching to light or hybrid was considered and rejected. The "Mission Control" identity is intentional.

**Why:** Inon uses this as a working dashboard, likely in evening/night sessions. Dark is ergonomically correct. Polish within the dark theme is the right direction.

### Tradeoff 2: LinkedIn tab as separate tab vs. inline panel

**Decision:** Separate tab.

**Why:** LinkedIn content management is a distinct context from task management. Mixing them would clutter the Tasks board. A separate tab with its own sticky Hebrew banner avoids any ambiguity about the language rule.

### Tradeoff 3: Owner-blocked as sub-section vs. separate column

**Decision:** Sub-section inside the Blocked column.

**Why:** A fifth column would overflow on laptops (we already have 4). The Blocked column is underused — most boards have 1–3 blocked items. Adding a visual sub-header inside Blocked keeps the column count clean while making owner-caused blockers visually distinct.

### Tradeoff 4: Notification bell count logic

**Decision:** Bell count = Tasks (Needs You column count) + Owner-blocked count + LinkedIn posts needing action (Draft or Approved with past scheduled date).

**Rationale:** The bell should only fire for things where Inon's input is required — not for In Progress tasks or general activity. This keeps badge fatigue low.

### Tradeoff 5: Version history storage

**Decision:** Store versions as an array within each post object in `linkedin_posts.json`.

**Why:** Simple, consistent with the existing flat-JSON pattern. No need for a separate version table at this scale.

---

## 15. Rex Implementation Notes

1. **Font loading:** Add Syne and JetBrains Mono to the existing Google Fonts import. Syne is a display sans — excellent for section headers. JetBrains Mono adds technical precision to IDs and metadata without feeling cold.

2. **LinkedIn tab activation:** When tab switches to LinkedIn, the `--active-tab-accent` CSS variable should be overridden to `--linkedin-bright` via a class on `<body>` or the tab panel: `body.tab-linkedin .tab-btn.active { color: var(--linkedin-bright); border-bottom-color: var(--linkedin-bright); }`

3. **RTL textarea:** Use `<textarea dir="rtl" lang="he">` — this is a single HTML attribute change. No library needed. CSS `text-align: right` reinforces it visually.

4. **Owner-blocked classification:** This requires a new field in `active_tasks.json`: `"blockedBy": "owner"`. Rex should add this to the data model and filter cards tagged this way into the owner-blocked section header inside the Blocked column.

5. **Notification bell data source:** For MVP, the bell can derive its count from already-loaded in-memory data (tasks + LinkedIn posts). No separate API call needed.

6. **Animation performance:** All animations use `transform` and `opacity` only — these are GPU-composited and will not cause layout thrashing. Safe to use freely.

7. **Preserve existing JS logic:** The filter bar, modal system, edit panels, drag-and-drop on job cards — none of this changes. All redesign work is CSS + new HTML for new features. The existing event listeners should still work after the HTML/CSS update.
