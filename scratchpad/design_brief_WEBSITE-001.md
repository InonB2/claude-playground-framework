# Design Brief: Inon Baasov Portfolio — Awwwards-Level Redesign
**By:** Lena (UI/UX Designer)  
**Date:** 2026-04-24  
**Task ID:** WEBSITE-001-DESIGN-01  
**Inspired by:** awwwards.com inspiration links provided by Owner  
**Status:** Ready for Rex (Web Developer)

---

## Design Vision

Transform the current flat, static dark-navy portfolio into a **cinematic, interaction-rich product portfolio** that feels like it belongs to a top-1% CPO — not just a professional website. Every scroll should feel intentional. Every hover should respond. The site should open doors before a word is read.

**Design direction:** *Premium tech minimalism with editorial motion* — think Stripe meets Apple meets a GSAP-powered awwwards site.

---

## 1. Color System

```
Background (deep):  #080E1A  — near-black navy base
Background (mid):   #0D1F3C  — navy for sections
Surface:            #111827  — elevated cards
Surface highlight:  #1E293B  — hover states
Accent primary:     #00B4D8  — electric cyan (keep — it works)
Accent glow:        #0EA5E9  — lighter cyan for glow effects
Text primary:       #F0F6FC  — near-white
Text secondary:     #94A3B8  — muted slate
Text accent:        #00B4D8  — cyan for roles/labels
Border subtle:      rgba(255,255,255,0.06)
Gradient A:         linear from #080E1A → #0D1F3C → #080E1A (vertical)
Gradient B:         radial from rgba(0,180,216,0.15) at hero center
```

All text/background pairs pass WCAG AA (contrast ≥ 4.5:1).

---

## 2. Typography Scale

**Primary font:** `Inter` (Google Fonts) — system-level clarity  
**Display font:** `Syne` (Google Fonts, Bold 700/800) — architectural impact

```
Display:  Syne ExtraBold 800,  72–96px,  tracking -0.03em,  line-height 1.0
H1:       Syne Bold 700,       48–64px,  tracking -0.02em,  line-height 1.1
H2:       Syne Bold 700,       32–40px,  tracking -0.015em, line-height 1.2
H3:       Inter SemiBold 600,  20–24px,  tracking 0,        line-height 1.3
Body:     Inter Regular 400,   15–16px,  tracking 0,        line-height 1.7
Body sm:  Inter Regular 400,   13–14px,  tracking 0.01em,   line-height 1.6
Label:    Inter Medium 500,    11–12px,  tracking 0.12em,   uppercase
Caption:  Inter Regular 400,   12px,     tracking 0.02em,   color: text-secondary
```

---

## 3. Layout Architecture

### Section 1: Hero (Cinematic Opener)
- **Full viewport** height
- **Centered composition** — name as a display-size typographic statement
- Ambient glow: radial cyan gradient behind the name (not a circle, a soft halo)
- Background: subtle animated particle field (50 tiny points, slow drift — Three.js or CSS)
- Left: Name + role + bio + CTAs
- Right: Profile photo with **glowing ring** + floating stat cards (appear on scroll or after 1.5s delay)
- **Remove:** The "CHOOSE YOUR PHOTO" dev widget
- **Add:** Animated badge "● OPEN TO SENIOR PM / CPO ROLES" with pulsing dot
- Stats animate as **number counters** on enter (0 → final value, 800ms ease-out)
- Photo frame: subtle continuous rotation of the glow ring (keyframe, 8s loop)
- CTAs: "View Portfolio" stays cyan; add subtle shimmer hover effect

### Section 2: About / Story (NEW)
- Short 2-paragraph narrative about Inon's approach to product
- Right side: horizontal scrolling skill chips (GSAP horizontal marquee, infinite loop)
- Background shift: slightly lighter navy to signal section change

### Section 3: Product Portfolio
- **Grid → Horizontal scroll** inspired by Lufte product gallery
- Cards are **tall (3:4 ratio)** with product screenshot/visual at top, details below
- **On hover:** Card scales up (1.05), background shifts to surface highlight, stats fade in
- Tags and "Deep Dive" CTA appear on hover (fade in from bottom)
- **Cards should feel like magazine covers**, not bullet points
- Filter bar at top: All / Flagship / Live / Consulting (smooth filter transition)

### Section 4: Experience Timeline
- Keep the vertical timeline but **make the active item sticky**
- As user scrolls through, the left-side dot + company name stays visible while the right card scrolls
- **Reveal animation:** Each card slides in from right with 300ms ease as it enters viewport

### Section 5: Core Capabilities
- 4 columns stay — but add **icon illustrations** (replace emoji with SVG icons or Lottie)
- Cards have subtle border glow on hover (box-shadow with cyan)

### Section 6: Testimonials (NEW — requires Owner to supply quotes)
- 3 cards side by side
- Each with: quote text, photo, name, title, company
- **Subtle background:** dark card with left-side cyan border accent
- If quotes not ready: section hidden until content is available

### Section 7: Education
- Clean minimal list — no changes needed

### Section 8: Contact CTA
- Keep the strong headline
- **Add a contact form** (Name, Email, Message, Send button)
- Replace direct email display with form (reduces PII exposure)
- Animated background: subtle gradient shift on scroll-enter

---

## 4. Scroll & Animation Specifications

### Global Scroll: Lenis (smooth scroll library)
```javascript
// Install: npm install @studio-freight/lenis
// Config:
new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smooth: true,
})
```

### GSAP ScrollTrigger (all reveal animations)
```javascript
// Inspired by: awwwards scroll-tracing and landing-page-scroll-project-o
// Pattern: elements enter from bottom with opacity
gsap.from(element, {
  y: 40,
  opacity: 0,
  duration: 0.8,
  ease: "power3.out",
  scrollTrigger: {
    trigger: element,
    start: "top 85%",
    toggleActions: "play none none none"
  }
})
```

### Hero Stats Counter (inspired by Rosehip scroll interaction)
```javascript
// Count up animation on viewport enter
gsap.to(counter, {
  innerText: targetValue,
  duration: 1.2,
  ease: "power2.out",
  snap: { innerText: 1 },
  scrollTrigger: { trigger: statsSection, start: "top 80%" }
})
```

### Portfolio Cards (inspired by Kettmeir product animation)
```javascript
// Card hover: scale + reveal details
card.addEventListener('mouseenter', () => {
  gsap.to(card, { scale: 1.04, duration: 0.3, ease: "power2.out" });
  gsap.to(cardDetails, { opacity: 1, y: 0, duration: 0.3 });
});
```

### Mouse Interaction (inspired by Rosehip mouse interaction)
```javascript
// Custom cursor: replace default cursor with a custom dot + ring
// Magnetic effect on buttons: element moves slightly toward cursor
const btn = document.querySelector('.cta-btn');
btn.addEventListener('mousemove', (e) => {
  const rect = btn.getBoundingClientRect();
  const x = (e.clientX - rect.left - rect.width/2) * 0.3;
  const y = (e.clientY - rect.top - rect.height/2) * 0.3;
  gsap.to(btn, { x, y, duration: 0.3 });
});
```

### Page Transition (inspired by VR/Aexlab animations)
```javascript
// On navigation between pages: curtain wipe with GSAP
// Overlay div slides across screen, new page loads, overlay slides out
```

### Scroll-traced SVG path (inspired by main-scroll-tracing-art)
```javascript
// Optional enhancement: an SVG path in the hero/about section
// that traces/draws itself as the user scrolls
const path = document.querySelector('.scroll-path');
const length = path.getTotalLength();
gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
gsap.to(path, {
  strokeDashoffset: 0,
  scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom center', scrub: 1 }
});
```

---

## 5. New Sections to Add

### "About" Section
**Placement:** Between Hero and Portfolio  
**Content needed from Owner:**
- 2–3 sentence personal philosophy / approach to product
- One "origin story" sentence (why you got into product)

### Testimonials Section
**Placement:** Between Portfolio and Experience  
**Content needed from Owner:**
- 2–3 quotes from: co-founders, investors, clients, or team leads at Elbit/TouchE
- Each: quote, name, title, company, optional headshot

### CV Download
**Placement:** Near hero CTAs  
**Implementation:** `<a href="/cv/Inon_Baasov_CV.pdf" download>Download CV</a>`

---

## 6. Component Redesigns

### Navigation
- Current: plain text links. New: add subtle frosted-glass background on scroll (backdrop-filter: blur)
- "Hire Me" button: add shimmer animation on hover (moving gradient overlay)

### Portfolio Cards (Major Upgrade)
- Current: dark card, emoji icon, text stats, "Deep Dive" link
- New: full-bleed product image/screenshot background (blurred, darkened), product name in large type overlay, tags as chips, hover to reveal full card
- Emoji → real product screenshots or SVG brand marks

### Footer
- Fix: © 2026 (already correct)
- Add: "Built with intention in Israel" tagline
- Add: Back-to-top arrow with smooth scroll

---

## 7. Technical Stack for Animations

```
Smooth scroll:      @studio-freight/lenis
Scroll animations:  gsap + @gsap/scrolltrigger
Particle field:     tsparticles or vanilla canvas
Custom cursor:      vanilla JS (no library needed)
Number counters:    gsap
Page transitions:   gsap
(Optional) 3D:      @react-three/fiber + three.js (only if heavy VR-style effects wanted)
```

---

## 8. Accessibility & Performance Notes
- All animations: add `prefers-reduced-motion` fallback (disable GSAP if user prefers no motion)
- Particle field: pause when tab is not visible (Page Visibility API)
- Lazy load all images below the fold
- Target Lighthouse Performance: 90+
- All motion must have CSS fallback for no-JS environments

---

## 9. awwwwards Reference Sites (April 2026)

Updated with latest SOTD research:

| Site | What to steal | Stack |
|------|--------------|-------|
| **Takuya Oshima** (takuya-oshima.com) | Clean dark/light toggle, smooth GSAP page transitions, minimal nav | Next.js + Tailwind + GSAP |
| **OHZI Interactive** | Full-page WebGL distortion on mouse move, custom GLSL shaders for glow | WebGL + OGL |
| **Dave Holloway** | Lottie + WebGL header combo, OGL for performance, GSAP transitions | OGL + Lottie + GSAP |
| **Jasmine Gunarto** | Editorial palette (pure black + warm off-white #EBEAE4), animated loading sequence, dynamic gallery, page transitions | GSAP + Vite |
| **Daniel Destefanis** | Spinning 3D App Icon, "daytime shadow" animation, WebGL hero video | WebGL + GSAP |
| **SAV1N Portfolio** (awwwwards nominee) | Dark minimal portfolio nominee — inspect for layout patterns | — |

**Key pattern across all winners:**
- One dominant motion technique (WebGL or GSAP), not both everywhere
- Dark background, high contrast text — NOT gray-on-dark
- Page transitions as a design signature (not just fade)
- Loading animation as first impression (300–800ms max)
- Editorial spacing — generous whitespace feels premium
- NO STOCK PHOTOS — either real screenshots, SVGs, or abstract WebGL backgrounds

**For Inon's site (practical picks):**
1. Use GSAP (already in brief) — no need for WebGL for a PM portfolio
2. Add a loading animation (200ms logo reveal or line wipe) — this alone earns credibility
3. Adopt the Jasmine Gunarto editorial spacing approach — generous gaps between sections
4. Replace cyan separator lines under sections with whitespace (awwwwards winning sites use space, not lines)
5. Consider a color-mode toggle (dark default, light option) — Takuya Oshima does this well

---

## Hand-off to Rex
1. Install Lenis and GSAP (+ ScrollTrigger plugin)
2. Implement in priority order: (a) Remove dev widget → (b) Fix title → (c) Add animations → (d) New sections
3. Reference sites: takuya-oshima.com, ohzi.fr, dave-holloway.com
4. Test at 375px, 768px, 1280px before handing to Vera for QA

---

## DEPLOYMENT NOTE (critical)
The live site runs on Base44 at inonbaasov-website.base44.app. Base44 is NOT auto-synced with GitHub (unlike Lovable/ProMaker AR). Two paths to deploy:
- **Option A:** Edit directly in Base44's web editor (fastest for small fixes)
- **Option B:** Confirm if Base44 has GitHub sync in project Settings → if yes, pushes to the repo deploy automatically
- **Option C (recommended for full redesign):** Migrate hosting to Vercel (free) connected to the GitHub repo — then all pushes from GitHub deploy instantly. Owner decides hosting platform.
