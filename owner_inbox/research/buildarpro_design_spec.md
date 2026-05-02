# BuildARPro — Visual Design Specification

**Version:** 1.0  
**Created by:** Lena (Visual Designer)  
**Date:** 2026-05-02  
**Product:** BuildARPro — AR Maintenance Guides Platform

---

## 1. Brand Summary

BuildARPro is a B2B SaaS product for industrial maintenance teams. The visual identity is **industrial, dark, and precise** — borrowing from AR UI aesthetics (targeting reticles, HUD overlays, grid lines) and applying them in a professional SaaS context. The brand must feel both high-tech and trustworthy on a factory floor.

---

## 2. Color Palette

| Token | Hex | RGB | Usage |
|---|---|---|---|
| `color-orange-primary` | `#F97316` | 249, 115, 22 | Primary accent, CTAs, power words, borders |
| `color-orange-hover` | `#FF8C42` | 255, 140, 66 | Button hover state, secondary highlights |
| `color-orange-glow` | `rgba(249,115,22,0.35)` | — | Text shadow on power words, glow effects |
| `color-orange-subtle` | `rgba(249,115,22,0.10)` | — | Background tints, badge fills |
| `color-bg-deep` | `#0D0D0D` | 13, 13, 13 | Primary dark background (slides, hero) |
| `color-bg-card` | `#1A1A1A` | 26, 26, 26 | Card backgrounds, secondary sections |
| `color-bg-elevated` | `#242424` | 36, 36, 36 | Hover states, elevated surfaces |
| `color-text-primary` | `#FFFFFF` | 255, 255, 255 | Headlines, titles |
| `color-text-body` | `#E5E5E5` | 229, 229, 229 | Body copy, descriptions |
| `color-text-secondary` | `#A3A3A3` | 163, 163, 163 | Sub-copy, labels, captions |
| `color-text-muted` | `#6B7280` | 107, 114, 128 | Metadata, placeholder text |
| `color-border-subtle` | `rgba(249,115,22,0.20)` | — | Card borders, dividers |

### Python-pptx color values (copy-paste ready)
```python
DARK_BG    = RGBColor(0x0D, 0x0D, 0x0D)
ORANGE     = RGBColor(0xF9, 0x73, 0x16)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xE5, 0xE5, 0xE5)
MID_GRAY   = RGBColor(0xA3, 0xA3, 0xA3)
```

---

## 3. Typography

### Font Stack (web)
```css
font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
```
- **Inter** is the recommended primary typeface (Google Fonts, free). It has excellent legibility at both large display sizes and small body sizes.
- **Segoe UI** is an acceptable Windows fallback and is already present on all Windows systems.

### Type Scale

| Role | Size | Weight | Color | Notes |
|---|---|---|---|---|
| Hero headline | 52px (clamp 32–52) | 800 (ExtraBold) | White | Letter-spacing: -0.02em |
| Power words (VIDEOS / BETTER) | +12% of headline | 900 (Black) | Orange `#F97316` | Text-shadow glow |
| Section title | 36px | 700 (Bold) | White | |
| Sub-headline | 19px | 400 | `#A3A3A3` | Line-height 1.6 |
| Body copy | 16px | 400 | `#E5E5E5` | Line-height 1.7 |
| Label / badge | 11px | 700 | Orange | Letter-spacing 0.15em, all-caps |
| Caption / meta | 13px | 400 | `#6B7280` | |

### PowerPoint / PPTX Typography
- Slide titles: **white, bold**, font size per template (do not override size, just color + weight)
- Body text: `#E5E5E5`, regular weight
- Power words: `#F97316`, bold, +4pt above surrounding body size

---

## 4. Catchphrase Treatment

**Full text:** "Stop Pausing VIDEOS, Start building BETTER"

This is the brand's primary hook. Always apply:
- Base words ("Stop Pausing", "Start building") → white, standard weight
- **VIDEOS** and **BETTER** → orange `#F97316`, bold, font-size +8–12% larger than surrounding text, optional glow `text-shadow: 0 0 24px rgba(249,115,22,0.35)`
- Never change the casing of VIDEOS or BETTER — they must stay uppercase

```html
<!-- Example HTML treatment -->
<h1>Stop Pausing <span class="power">VIDEOS</span>, Start building <span class="power">BETTER</span></h1>
```

```css
.power {
  color: #F97316;
  font-size: 1.1em;
  font-weight: 900;
  text-shadow: 0 0 24px rgba(249, 115, 22, 0.35);
}
```

---

## 5. Spacing System

Based on an 8px base unit. All spacing should be multiples of 8.

| Token | Value | Use |
|---|---|---|
| `space-xs` | 4px | Micro gaps (between icon + label) |
| `space-sm` | 8px | Inline gaps |
| `space-md` | 16px | Component internal padding |
| `space-lg` | 24px | Between related elements |
| `space-xl` | 32px | Between sections within a card |
| `space-2xl` | 48px | Section padding (horizontal) |
| `space-3xl` | 64px | Page section gaps |

---

## 6. Component Patterns

### Primary CTA Button
```css
background: #F97316;
color: #0D0D0D;           /* Dark text on orange — high contrast */
font-weight: 700;
letter-spacing: 0.04em;
text-transform: uppercase;
padding: 14px 32px;
border-radius: 4px;
box-shadow: 0 4px 20px rgba(249, 115, 22, 0.40);

/* Hover */
background: #FF8C42;
box-shadow: 0 6px 28px rgba(249, 115, 22, 0.60);
transform: translateY(-1px);
```

### Card / Surface
```css
background: #1A1A1A;
border: 1px solid rgba(249, 115, 22, 0.20);
border-radius: 6px;
padding: 24px;
```

### Accent Divider
```css
width: 56px;
height: 3px;
background: #F97316;
border-radius: 2px;
```

### Industrial Grid Background
```css
background-image:
  linear-gradient(rgba(249, 115, 22, 0.04) 1px, transparent 1px),
  linear-gradient(90deg, rgba(249, 115, 22, 0.04) 1px, transparent 1px);
background-size: 60px 60px;
```

### Orange Glow Bar (vertical)
```css
width: 3px;
background: linear-gradient(180deg, transparent 0%, #F97316 40%, #F97316 60%, transparent 100%);
border-radius: 0 2px 2px 0;
```

---

## 7. Logo Usage

- **File:** `BuildAR PRO - logo image.png` (orange hexagon with hammer/wrench icon)
- Minimum size: 40px height
- Always use `filter: drop-shadow(0 0 12px rgba(249, 115, 22, 0.40))` on dark backgrounds to enhance presence
- Never place logo on a white or light background without a dark container
- Always preserve the orange hex color — do not recolor the logo

---

## 8. Slide / Presentation Design Rules

For PowerPoint and slide decks:

1. **Background:** Always `#0D0D0D` — use python-pptx `fill.solid()` with `fore_color.rgb`
2. **Title slides:** Large white headline, orange accent line below, logo top-left
3. **Content slides:** Title in white bold, body in `#E5E5E5`, key figures in orange
4. **Data / metrics:** Numbers in orange `#F97316`, labels in `#A3A3A3`
5. **Images:** Use product images (`image 1.png` through `image 6.png`) in dark-framed containers
6. **Footer:** Consistent — "BuildARPro" wordmark + slide number in `#6B7280`

---

## 9. Social / Marketing Assets

| Format | Dimensions | File |
|---|---|---|
| LinkedIn / OG banner | 1200×628px | `scratchpad/buildarpro_social_banner.html` |
| Website hero | Full-width, ~600px tall | `scratchpad/buildarpro_banner.html` |
| Logo source | PNG with transparency | `team_inbox/BuildAR Pro/BuildAR PRO - logo image.png` |
| Social image | PNG | `team_inbox/BuildAR Pro/BuildAR PRO - social image.png` |

To export HTML banners as PNG: open in Chrome → DevTools → toggle device frame → screenshot, or use a headless tool such as `puppeteer` or `wkhtmltoimage`.

---

## 10. Do / Don't

| Do | Don't |
|---|---|
| Use dark backgrounds (#0D0D0D / #1A1A1A) | Use white or light backgrounds |
| Keep VIDEOS and BETTER uppercase and orange | Lowercase the power words |
| Use orange only for accents and CTAs | Make entire sections orange |
| Apply the 8px spacing grid | Use arbitrary padding values |
| Pair orange CTAs with dark text (#0D0D0D) | Use white text on orange buttons |
| Use Inter or Segoe UI | Use decorative or serif fonts |
| Keep border-radius at 4–6px | Use round pills (unless badges) |
