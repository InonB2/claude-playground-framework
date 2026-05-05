// CV PowerPoint generator for Inon Baasov — Elbit 2026
// A4 portrait (7776 x 11006 EMUs = 27.3cm x 38.74cm)
// Run: node scripts/generate_cv_pptx.js

const pptx = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const prs = new pptx();

// A4 portrait in inches (1 inch = 914400 EMU)
// 27.3cm = 10.748in, 38.74cm = 15.252in
const W = 10.748;
const H = 15.252;
prs.defineLayout({ name: "A4_PORTRAIT", width: W, height: H });
prs.layout = "A4_PORTRAIT";

// Colors
const NAVY  = "0d1f3c";
const CYAN  = "00b4d8";
const GREY  = "64748b";
const BLACK = "1a1a2e";
const WHITE = "ffffff";

// Margins
const ML = 0.55;  // left margin (inches)
const MR = 0.55;  // right margin
const BODY_W = W - ML - MR;  // 9.648 inches

const slide = prs.addSlide();
slide.background = { color: WHITE };

let curY = 0;

// ─────────────────────────────────────────────
// 1. HEADER BLOCK
// ─────────────────────────────────────────────
const HEADER_H = 0.72;
slide.addShape(prs.ShapeType.rect, {
  x: 0, y: curY, w: W, h: HEADER_H,
  fill: { color: NAVY }, line: { color: NAVY }
});

slide.addText("INON BAASOV", {
  x: ML, y: curY + 0.07, w: BODY_W, h: 0.32,
  fontSize: 24, bold: true, color: WHITE,
  fontFace: "Calibri", align: "left", valign: "top",
  margin: 0
});

slide.addText("Product Leader  |  Co-Founder  |  CPO", {
  x: ML, y: curY + 0.38, w: BODY_W, h: 0.22,
  fontSize: 10, color: CYAN,
  fontFace: "Calibri", align: "left", valign: "top",
  margin: 0
});

curY += HEADER_H;

// ─────────────────────────────────────────────
// 2. CONTACT BAR
// ─────────────────────────────────────────────
const CONTACT_H = 0.26;
slide.addShape(prs.ShapeType.rect, {
  x: 0, y: curY, w: W, h: CONTACT_H,
  fill: { color: CYAN }, line: { color: CYAN }
});

const contactItems = [
  "✉  Inonbaasov@hotmail.com",
  "✆  +972-54-444-5856",
  "in  linkedin.com/in/inonbaasov",
  "⌂  inon-baasov-website.base44.app"
];
const colW = W / 4;
contactItems.forEach((txt, i) => {
  slide.addText(txt, {
    x: i * colW, y: curY + 0.02, w: colW, h: CONTACT_H - 0.04,
    fontSize: 7.5, color: WHITE,
    fontFace: "Calibri", align: "center", valign: "middle",
    margin: 0
  });
});

curY += CONTACT_H;

// ─────────────────────────────────────────────
// 3. KEY METRICS + CORE SKILLS
// ─────────────────────────────────────────────
const SEC_GAP = 0.09;   // gap before each section
const LINE_Y_OFFSET = 0.005;
curY += SEC_GAP;

const METRICS_W = BODY_W * 0.34;
const SKILLS_W  = BODY_W * 0.66;
const METRICS_X = ML;
const SKILLS_X  = ML + METRICS_W + 0.12;

// Section titles row
slide.addText("KEY METRICS", {
  x: METRICS_X, y: curY, w: METRICS_W, h: 0.16,
  fontSize: 9.5, bold: true, color: NAVY,
  fontFace: "Calibri", align: "left", valign: "middle", margin: 0
});
slide.addText("CORE SKILLS & COMPETENCIES", {
  x: SKILLS_X, y: curY, w: SKILLS_W, h: 0.16,
  fontSize: 9.5, bold: true, color: NAVY,
  fontFace: "Calibri", align: "left", valign: "middle", margin: 0
});
curY += 0.17;

// Cyan separator — full width
slide.addShape(prs.ShapeType.rect, {
  x: ML, y: curY + LINE_Y_OFFSET, w: BODY_W, h: 0.018,
  fill: { color: CYAN }, line: { color: CYAN }
});
curY += 0.035;

// --- Metrics block ---
const M_COL = METRICS_W / 3;
const metricsRows = [
  { vals: ["10+", "$2.5M", "38%"], labels: ["Years PM", "Raised", "Efficiency"] },
  { vals: ["6",   "4",    "99.99%"], labels: ["Products", "Teams Led", "Uptime"] },
];

metricsRows.forEach((row, ri) => {
  // Values
  row.vals.forEach((v, ci) => {
    slide.addText(v, {
      x: METRICS_X + ci * M_COL, y: curY, w: M_COL, h: 0.22,
      fontSize: 13, bold: true, color: CYAN,
      fontFace: "Calibri", align: "center", valign: "middle", margin: 0
    });
  });
  curY += 0.21;
  // Labels
  row.labels.forEach((lb, ci) => {
    slide.addText(lb, {
      x: METRICS_X + ci * M_COL, y: curY, w: M_COL, h: 0.14,
      fontSize: 7, color: GREY,
      fontFace: "Calibri", align: "center", valign: "middle", margin: 0
    });
  });
  curY += 0.15;

  // Thin separator between rows
  if (ri === 0) {
    slide.addShape(prs.ShapeType.rect, {
      x: METRICS_X, y: curY + 0.01, w: METRICS_W, h: 0.01,
      fill: { color: "cccccc" }, line: { color: "cccccc" }
    });
    curY += 0.025;
  }
});

// --- Skills block (drawn at saved Y positions) ---
const skillPairs = [
  ["Product Lifecycle Mgmt (0-to-Scale)", "PRD / MRD / BRD Authorship"],
  ["Training & Learning Systems",          "AI / LLM Product Design"],
  ["V&V Processes & Testing",              "Cross-functional Leadership"],
  ["Strategic Roadmapping",                "Budget & P&L Management"],
  ["Supplier & Vendor Management",         "Market Research & Competitive Intel"],
  ["Global Project Management",            "Business Development & GTM"],
  ["Agile / Scrum / OKRs",                 "SaaS / PaaS Architecture"],
  ["Regulatory Environments (HL7, MoH)",   ""],
];

const SKILL_COL_W = SKILLS_W / 2;
const SKILL_ROW_H = 0.145;
// Skills block starts at CONTACT_H + SEC_GAP + title row + separator
const SKILLS_START_Y = HEADER_H + CONTACT_H + SEC_GAP + 0.17 + 0.035;

skillPairs.forEach((pair, ri) => {
  const sy = SKILLS_START_Y + ri * SKILL_ROW_H;
  pair.forEach((skill, ci) => {
    if (!skill) return;
    slide.addText("• " + skill, {
      x: SKILLS_X + ci * SKILL_COL_W, y: sy, w: SKILL_COL_W - 0.05, h: SKILL_ROW_H,
      fontSize: 7.5, color: BLACK,
      fontFace: "Calibri", align: "left", valign: "middle", margin: 0
    });
  });
});

// Move curY past the taller of the two blocks
const METRICS_BLOCK_H = 0.17 + 0.035 + (0.21 + 0.15 + 0.025) + (0.21 + 0.15);
const SKILLS_BLOCK_H  = skillPairs.length * SKILL_ROW_H;
curY = HEADER_H + CONTACT_H + SEC_GAP + Math.max(METRICS_BLOCK_H, SKILLS_BLOCK_H) + 0.05;

// ─────────────────────────────────────────────
// Helper: section header + cyan line
// ─────────────────────────────────────────────
function addSectionTitle(label, y) {
  slide.addText(label, {
    x: ML, y: y, w: BODY_W, h: 0.16,
    fontSize: 9.5, bold: true, color: NAVY,
    fontFace: "Calibri", align: "left", valign: "middle", margin: 0
  });
  const lineY = y + 0.17;
  slide.addShape(prs.ShapeType.rect, {
    x: ML, y: lineY + LINE_Y_OFFSET, w: BODY_W, h: 0.018,
    fill: { color: CYAN }, line: { color: CYAN }
  });
  return lineY + 0.025 + 0.04; // return next content Y
}

// ─────────────────────────────────────────────
// 4. PROFESSIONAL SUMMARY
// ─────────────────────────────────────────────
curY += SEC_GAP;
let nextY = addSectionTitle("PROFESSIONAL SUMMARY", curY);

const summaryText = "Product Leader with 10+ years delivering complex technology products from zero to scale in AI, SaaS, and interactive media systems. Raised $2.5M, led teams of 20+, and drove 38% efficiency gains. Experienced in full product lifecycle management (PRD/MRD/V&V), supplier management, global cross-functional projects, and Agile in regulated industries. Technion-educated (BSc + Executive MBA). Passionate about technically complex, multi-platform products that combine AI, simulation, and scalable content delivery.";

slide.addText(summaryText, {
  x: ML, y: nextY, w: BODY_W, h: 0.52,
  fontSize: 8, color: BLACK,
  fontFace: "Calibri", align: "justify", valign: "top",
  margin: 0, paraSpaceAfter: 0
});
curY = nextY + 0.53;

// ─────────────────────────────────────────────
// 5. PROFESSIONAL EXPERIENCE
// ─────────────────────────────────────────────
curY += SEC_GAP * 0.8;
nextY = addSectionTitle("PROFESSIONAL EXPERIENCE", curY);
curY = nextY;

const jobs = [
  {
    org: "Inon Baasov Ltd",
    role: "Product Strategy Consultant",
    dates: "2024 – Present",
    tags: "GenAI  |  AI Strategy  |  GTM  |  Consulting",
    bullets: [
      "Advising 3 early-stage AI startups on product strategy, GTM, and 12-month roadmap execution.",
      "AiRakoon — Enterprise AI: LLM architecture, API design, enterprise GTM delivery.",
      "Medicrowd — MedTech AI: Full MVP spec in regulated HL7 environment; dual UX for clinicians and investors.",
      "Smash+ — Wellness App: B2C behavioral design, cohort analysis, D7/D30 KPI framework.",
    ]
  },
  {
    org: "TouchE TV",
    role: "Co-Founder & Chief Product Officer",
    dates: "2018 – 2024",
    tags: "CPO  |  SaaS/PaaS  |  AWS  |  AI/ML  |  Android/iOS/Smart TV",
    bullets: [
      "Built AI-powered interactive video platform (content, e-commerce, advertising) from 0 to scale; raised $2.5M seed funding.",
      "Led 4 cross-functional teams across full 6-year product lifecycle; authored all PRD/MRD documentation.",
      "Achieved 99.99% uptime on AWS serving millions of concurrent users; drove 38% operational efficiency gains.",
      "Managed supplier relationships, external dev vendors, and international studio partnerships (Paramount, Lionsgate).",
    ]
  },
  {
    org: "Arena Plus Financial Services",
    role: "Senior Product Manager",
    dates: "2013 – 2018",
    tags: "FinTech  |  B2B  |  Agile  |  Regulated  |  Global",
    bullets: [
      "Promoted PM to Senior PM in 18 months; managed global cross-functional teams across FinTech platforms.",
      "Delivered +22% user adoption, +15% revenue growth, and -20% TTM via Agile methodology.",
    ]
  },
  {
    org: "Blau Pharmaceuticals",
    role: "Regulatory Affairs Consultant",
    dates: "2009 – 2011",
    tags: "Regulatory  |  Pharma  |  MoH  |  V&V  |  Team Lead",
    bullets: [
      "Led Israeli MoH regulatory submissions and headed Pharmacovigilance department with 6-person team.",
    ]
  },
];

jobs.forEach(job => {
  // Org + dates on same line
  slide.addText([
    { text: job.org, options: { bold: true, color: NAVY, fontSize: 9 } },
  ], {
    x: ML, y: curY, w: BODY_W * 0.72, h: 0.175,
    fontFace: "Calibri", align: "left", valign: "middle", margin: 0
  });
  slide.addText(job.dates, {
    x: ML + BODY_W * 0.72, y: curY, w: BODY_W * 0.28, h: 0.175,
    fontSize: 7.5, color: GREY,
    fontFace: "Calibri", align: "right", valign: "middle", margin: 0
  });
  curY += 0.165;

  // Role title
  slide.addText(job.role, {
    x: ML, y: curY, w: BODY_W, h: 0.155,
    fontSize: 8.5, bold: true, color: CYAN,
    fontFace: "Calibri", align: "left", valign: "middle", margin: 0
  });
  curY += 0.15;

  // Tags
  slide.addText(job.tags, {
    x: ML, y: curY, w: BODY_W, h: 0.13,
    fontSize: 7, italic: true, color: GREY,
    fontFace: "Calibri", align: "left", valign: "middle", margin: 0
  });
  curY += 0.125;

  // Bullets
  job.bullets.forEach(b => {
    slide.addText("•  " + b, {
      x: ML + 0.1, y: curY, w: BODY_W - 0.1, h: 0.135,
      fontSize: 8, color: BLACK,
      fontFace: "Calibri", align: "left", valign: "top", margin: 0
    });
    curY += 0.13;
  });
  curY += 0.04; // gap after entry
});

// ─────────────────────────────────────────────
// 6. EDUCATION
// ─────────────────────────────────────────────
curY += SEC_GAP * 0.5;
nextY = addSectionTitle("EDUCATION", curY);
curY = nextY;

const educRows = [
  { deg: "Executive MBA — Entrepreneurship & High-Tech Management  |  Technion – IIT", yr: "2016–2018" },
  { deg: "B.Sc. — Biotechnology & Food Engineering  |  Technion – IIT", yr: "2005–2008" },
  { deg: "Faculty Studies — Chemical Engineering  |  McGill University, Canada", yr: "2004–2005" },
];
educRows.forEach(row => {
  slide.addText(row.deg, {
    x: ML, y: curY, w: BODY_W * 0.82, h: 0.135,
    fontSize: 8, color: BLACK,
    fontFace: "Calibri", align: "left", valign: "middle", margin: 0
  });
  slide.addText(row.yr, {
    x: ML + BODY_W * 0.82, y: curY, w: BODY_W * 0.18, h: 0.135,
    fontSize: 7.5, color: GREY,
    fontFace: "Calibri", align: "right", valign: "middle", margin: 0
  });
  curY += 0.13;
});

// ─────────────────────────────────────────────
// 7. LANGUAGES & AVAILABILITY
// ─────────────────────────────────────────────
curY += SEC_GAP * 0.8;
nextY = addSectionTitle("LANGUAGES & AVAILABILITY", curY);
curY = nextY;

slide.addText("Hebrew — Native  |  English — Fluent (C2)  |  Location: Israel  |  Available Now  |  Open to travel", {
  x: ML, y: curY, w: BODY_W, h: 0.16,
  fontSize: 8, color: BLACK,
  fontFace: "Calibri", align: "left", valign: "middle", margin: 0
});

// ─────────────────────────────────────────────
// Output
// ─────────────────────────────────────────────
const outDir = "D:\\Claude Playground\\output\\cv_archive";
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
const outFile = path.join(outDir, "Inon_Baasov_CV_Elbit_2026.pptx");

prs.writeFile({ fileName: outFile }).then(() => {
  console.log("Created:", outFile);
}).catch(err => {
  console.error("Error:", err.message);
  process.exit(1);
});
