# Icon Audit — WEBSITE-001-UX-03
**Agent:** Lena (UI/UX Designer)  
**Date:** 2026-04-30  
**Status:** Draft — pending Inon approval before Rex implements

---

## 1. Icon Library Status

No `package.json` was found in the `sites/website-product-portfolio/` directory — the project appears to be deployed via Base44/Lovable without a traditional Node.js build pipeline. This means icon libraries cannot be imported as npm packages directly.

**Recommendation:** Use **Lucide React** (lightweight, tree-shakeable, MIT license) imported via CDN or as an npm dependency if the platform supports it. Alternatively, inline SVGs can be pasted directly into the JSX — zero dependency, zero build step, works on any platform.

**Decision tree:**
- If Base44 supports npm packages → install `lucide-react` (`npm install lucide-react`)
- If not → use inline SVG strings (provided below for each replacement)

---

## 2. Full Emoji Inventory

### File: `pages/Home.jsx`

#### 2.1 PRODUCTS Data Array (lines 57–124)
These emojis are stored in the `PRODUCTS` data array and rendered in both the Card component (line 265) and Modal header (line 342). They animate on hover (scale + rotate).

| Location | Current Emoji | Unicode | Semantic Meaning | Recommended Lucide Icon | Inline SVG Path |
|---|---|---|---|---|---|
| `PRODUCTS[0].emoji` — TouchE | 🎬 | U+1F3AC | Video / Film | `Clapperboard` | `<path d="M4 11v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8H4Z"/><path d="m4 11-.88-2.87a2 2 0 0 1 1.33-2.5l11.48-3.5a2 2 0 0 1 2.5 1.32l.87 2.87L4 11Z"/><path d="m6.6 4.99 3.38 4.2"/><path d="m11.86 3.38 3.38 4.2"/>` |
| `PRODUCTS[1].emoji` — TradePulse | 📈 | U+1F4C8 | Chart / Growth | `TrendingUp` | `<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>` |
| `PRODUCTS[2].emoji` — Family Flow | 👨‍👩‍👧 | U+1F468 ZWJ family | Family / People | `Users` | `<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>` |
| `PRODUCTS[3].emoji` — AiRakoon | 🤖 | U+1F916 | AI / Robot | `Bot` | `<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>` |

#### 2.2 CAREER Data Array (lines 127–137)
Rendered in the Timeline tab buttons (line 779) and Timeline preview in DesignOptions.jsx.

| Location | Current Emoji | Semantic Meaning | Recommended Lucide Icon |
|---|---|---|---|
| `CAREER[0].emoji` — The Engineer | 🔬 | Science / Lab | `FlaskConical` |
| `CAREER[1].emoji` — The Regulator | ⚗️ | Chemistry / Precision | `TestTube` |
| `CAREER[2].emoji` — The PM | 📊 | Analytics / Data | `BarChart3` |
| `CAREER[3].emoji` — The Founder | 🚀 | Launch / Startup | `Rocket` |
| `CAREER[4].emoji` — The Architect | 🎯 | Focus / Target | `Target` |

#### 2.3 Modal Step Icons (lines 320–327)
Rendered inside the step icon boxes in the Modal component. Small, 15px, inside colored rounded squares.

| Step | Current Emoji | Semantic Meaning | Recommended Lucide Icon |
|---|---|---|---|
| `steps[0].icon` — THE PROBLEM | ⚡ | Problem / Energy | `Zap` |
| `steps[1].icon` — MY PROCESS | 🔍 | Research / Search | `Search` |
| `steps[2].icon` — THE SOLUTION | 💡 | Idea / Solution | `Lightbulb` |
| `steps[3].icon` — MY ROLE | 👤 | Person / Self | `User` |
| `steps[4].icon` — IMPACT | 📊 | Metrics / Chart | `BarChart3` |
| `steps[5].icon` — WHAT I LEARNED | 🎓 | Learning / Education | `GraduationCap` |

#### 2.4 Contact Section — Download CV Link (line 834)
A single emoji used as a button prefix.

| Location | Current | Recommended |
|---|---|---|
| Download CV button prefix | `⬇` (U+2B07) | `Download` (Lucide) or inline `↓` styled text |

---

### File: `pages/DesignOptions.jsx`

This file is a design preview tool, not the production portfolio. However, it contains emojis in badge labels and in the TimelinePreview component (which mirrors CAREER data from Home.jsx).

| Location | Current Emoji | Context | Action |
|---|---|---|---|
| `DESIGNS[0].badge` — "⭐ RECOMMENDED" | ⭐ | Badge label string | Replace with `Star` icon inline, or use a styled text pill — this is UI chrome, not user-facing |
| `DESIGNS[4].badge` — "🚀 ORIGINAL" | 🚀 | Badge label string | Replace with `Rocket` icon inline |
| `DESIGNS[5].badge` — "🎨 ORIGINAL" | 🎨 | Badge label string | Replace with `Palette` icon |
| `DesignBlock` selected state — "✓ SELECTED" | `✓` text | Checkmark (not emoji — Unicode U+2713) | Keep as-is or replace with `Check` icon |
| Sticky bar — "✅ Tell Andy to build this →" | ✅ | UI action label | Replace `✅` with `CheckCircle` icon |
| `TimelinePreview` chapter emojis | 🔬⚗️📊🚀🎯 | Same as CAREER data | Apply same replacements as Home.jsx |

---

## 3. Implementation Strategy

### Option A: Lucide React (Preferred — if platform allows npm)

```bash
npm install lucide-react
```

**Import pattern at top of Home.jsx:**
```jsx
import {
  Clapperboard, TrendingUp, Users, Bot,
  FlaskConical, TestTube, BarChart3, Rocket, Target,
  Zap, Search, Lightbulb, User, GraduationCap,
  Download, Star, Palette, Check, CheckCircle
} from 'lucide-react';
```

**Usage in PRODUCTS data — change `emoji` field to a component reference:**
```jsx
// Before:
{ id: "touche", emoji: "🎬", ... }

// After:
{ id: "touche", Icon: Clapperboard, iconColor: "#0ea5e9", ... }
```

**Usage in Card component (line 265) — change render:**
```jsx
// Before:
<span style={{
  fontSize: 26, transition: "transform .3s cubic-bezier(.34,1.56,.64,1)",
  transform: hov ? "scale(1.18) rotate(-4deg)" : "scale(1)", display: "inline-block",
}}>{p.emoji}</span>

// After:
<span style={{
  transition: "transform .3s cubic-bezier(.34,1.56,.64,1)",
  transform: hov ? "scale(1.18) rotate(-4deg)" : "scale(1)", display: "inline-block",
}}>
  <p.Icon size={26} color={p.color} strokeWidth={1.8} />
</span>
```

**Usage in Modal step icons (line 373) — steps array must also change:**
```jsx
// Before:
{ label: "THE PROBLEM", icon: "⚡", ... }

// After:
{ label: "THE PROBLEM", Icon: Zap, ... }

// Render:
<s.Icon size={15} color={s.color} strokeWidth={2} />
```

**CAREER timeline tabs (line 779):**
```jsx
// Before:
<div style={{ fontSize: 20, marginBottom: 3 }}>{c.emoji}</div>

// After:
<div style={{ marginBottom: 3 }}>
  <c.Icon size={20} color={chapter === i ? c.color : "rgba(255,255,255,0.25)"} strokeWidth={1.8} />
</div>
```

---

### Option B: Inline SVGs (No-dependency fallback)

Wrap each SVG in a helper component:

```jsx
function Icon({ paths, size = 16, color = "currentColor", strokeWidth = 2 }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size} height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ display: "inline-block", verticalAlign: "middle", flexShrink: 0 }}
    >
      {paths}
    </svg>
  );
}
```

Use the SVG path strings from the table in Section 2.1.

---

## 4. Accessibility Notes

- All icon replacements must have `aria-label` or a visually hidden text sibling for screen readers.
- The timeline tab buttons currently render emoji as visual labels with no text alternative. After replacement, add `aria-label={c.title}` to each tab button.
- Modal step icons are decorative (step label text is present beside them) — add `aria-hidden="true"` to each icon.

---

## 5. Scope Summary

| File | Emoji instances | Priority |
|---|---|---|
| `pages/Home.jsx` | 15 (4 product + 5 career + 6 modal steps + 1 download) | HIGH — production page |
| `pages/DesignOptions.jsx` | 8 (3 badges + 1 checkmark + 5 timeline) | LOW — internal design tool |

**Total replacements:** 23 emoji instances across 2 files.

---

## 6. Ralph Loop — Self-Review

- [x] All emoji instances catalogued from both JSX files
- [x] Icon library status confirmed (none installed)
- [x] Lucide recommended with rationale
- [x] Both implementation paths (npm + inline SVG) documented
- [x] Accessibility requirements called out
- [x] DesignOptions.jsx treated as lower priority (internal tool)
- [x] Production-ready: yes — Rex can implement directly from this spec
