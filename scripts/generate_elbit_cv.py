"""
Inon Baasov — Elbit Systems CV (Learning Dept PM)
Strict one-page layout. Override output/cv_archive/Inon_Baasov_CV_Elbit_2026.pdf
Run: python scripts/generate_elbit_cv.py

Owner fixes applied:
  1. Removed "Applying for" line
  2. Contact bar: all icons same line, same white colour, LinkedIn added
  3. Removed "Why Elbit?" box
  4. Key Metrics kept at top — tightened
  5. Professional Experience alignment fixed (full INNER width)
  6. Periods at end of every bullet
  7. Core Skills moved up next to Key Metrics
  8. One-page — all spacing reduced
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

os.makedirs("output/cv_archive", exist_ok=True)
OUTPUT = "output/cv_archive/Inon_Baasov_CV_Elbit_2026.pdf"

W, H = A4
M = 14 * mm          # page margin
INNER = W - 2 * M   # usable width

# ── Colours ────────────────────────────────────────────────────────────────
NAVY  = colors.HexColor("#0d1f3c")
CYAN  = colors.HexColor("#00b4d8")
GREY  = colors.HexColor("#64748b")
BLACK = colors.HexColor("#1a1a2e")
WHITE = colors.white

# ── Style helpers ──────────────────────────────────────────────────────────
def PS(name, **kw):
    return ParagraphStyle(name, **kw)

# Header styles
sNAME  = PS("N",  fontName="Helvetica-Bold",    fontSize=22, textColor=WHITE,  leading=26)
sTITLE = PS("T",  fontName="Helvetica",         fontSize=10, textColor=CYAN,   leading=14)
sCON   = PS("C",  fontName="Helvetica",         fontSize=8,  textColor=WHITE,  leading=11)

# Body styles
sSEC   = PS("S",  fontName="Helvetica-Bold",    fontSize=9.5,textColor=NAVY,   leading=13, spaceBefore=2)
sBODY  = PS("B",  fontName="Helvetica",         fontSize=8,  textColor=BLACK,  leading=11, alignment=TA_JUSTIFY)
sBUL   = PS("BU", fontName="Helvetica",         fontSize=8,  textColor=BLACK,  leading=11,
            leftIndent=9, firstLineIndent=-8, spaceBefore=0.5)
sORG   = PS("O",  fontName="Helvetica-Bold",    fontSize=9,  textColor=NAVY,   leading=12)
sROLE  = PS("R",  fontName="Helvetica-Bold",    fontSize=8.5,textColor=CYAN,   leading=11)
sDATE  = PS("D",  fontName="Helvetica",         fontSize=7.5,textColor=GREY,   leading=11, alignment=TA_RIGHT)
sTAG   = PS("TG", fontName="Helvetica-Oblique", fontSize=7,  textColor=GREY,   leading=10, spaceAfter=1)
sMV    = PS("MV", fontName="Helvetica-Bold",    fontSize=13, textColor=CYAN,   leading=16, alignment=TA_CENTER)
sML    = PS("ML", fontName="Helvetica",         fontSize=7,  textColor=GREY,   leading=9,  alignment=TA_CENTER)
sSK    = PS("SK", fontName="Helvetica",         fontSize=7.5,textColor=BLACK,  leading=10)

def hr():
    return HRFlowable(width=INNER, thickness=1, color=CYAN, spaceAfter=2, spaceBefore=1)

def sec(t):
    return [Paragraph(t.upper(), sSEC), hr()]

def bul(t):
    # Ensure period at end
    t = t.rstrip()
    if t and t[-1] not in ".!?":
        t += "."
    return Paragraph("• " + t, sBUL)

# ── Story ──────────────────────────────────────────────────────────────────
story = []

# ══ HEADER ══════════════════════════════════════════════════════════════════
hdr = Table([[
    Paragraph("INON BAASOV", sNAME),
    ""
],[
    Paragraph("Product Leader  |  Co-Founder  |  CPO", sTITLE),
    ""
]], colWidths=[INNER + 2*M, 0])
hdr.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), NAVY),
    ("TOPPADDING",    (0,0),(-1,-1), 8),
    ("BOTTOMPADDING", (0,0),(-1,-1), 8),
    ("LEFTPADDING",   (0,0),(-1,-1), M),
    ("RIGHTPADDING",  (0,0),(-1,-1), M),
]))
story.append(hdr)

# ══ CONTACT BAR (single row, all white, consistent) ══════════════════════
# Using plain text labels — avoids any icon colour drift
con_items = [
    Paragraph("Email: Inonbaasov@hotmail.com", sCON),
    Paragraph("Tel: +972-54-444-5856", sCON),
    Paragraph("LinkedIn: linkedin.com/in/inonbaasov", sCON),
    Paragraph("Location: Israel  |  Available Now", sCON),
]
con = Table([con_items], colWidths=[INNER/4 + M/2]*4)
con.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), CYAN),
    ("TOPPADDING",    (0,0),(-1,-1), 3),
    ("BOTTOMPADDING", (0,0),(-1,-1), 3),
    ("LEFTPADDING",   (0,0),(0,-1),  M),
    ("LEFTPADDING",   (1,0),(-1,-1), 6),
    ("RIGHTPADDING",  (0,0),(-1,-1), 4),
]))
story.append(con)
story.append(Spacer(1, 3*mm))

# ══ KEY METRICS + CORE SKILLS (side by side) ════════════════════════════
metrics = [
    ("10+",    "Years PM"),
    ("$2.5M",  "Raised"),
    ("38%",    "Efficiency"),
    ("6",      "Products"),
    ("4",      "Teams Led"),
    ("99.99%", "Uptime"),
]
skills = [
    "Product Lifecycle Mgmt (0-to-Scale)",  "PRD / MRD / BRD Authorship",
    "Training & Learning Systems",           "AI / LLM Product Design",
    "V&V Processes & Testing",              "Cross-functional Leadership",
    "Strategic Roadmapping",                "Budget & P&L Management",
    "Supplier & Vendor Management",         "Market Research & Competitive Intel",
    "Global Project Management",            "Business Development & GTM",
    "Agile / Scrum / OKRs",                "SaaS / PaaS Architecture",
    "Regulatory Environments (HL7, MoH)",   "",
]

# Metrics block (3 col x 2 row)
met_rows = [
    [Paragraph(v, sMV) for v,_ in metrics[:3]],
    [Paragraph(l, sML) for _,l in metrics[:3]],
    [Paragraph(v, sMV) for v,_ in metrics[3:]],
    [Paragraph(l, sML) for _,l in metrics[3:]],
]
met_tbl = Table(met_rows, colWidths=[INNER*0.35/3]*3)
met_tbl.setStyle(TableStyle([
    ("TOPPADDING",    (0,0),(-1,-1), 1),
    ("BOTTOMPADDING", (0,0),(-1,-1), 1),
    ("LEFTPADDING",   (0,0),(-1,-1), 2),
    ("RIGHTPADDING",  (0,0),(-1,-1), 2),
    ("LINEBELOW",     (0,1),(-1,1), 0.3, GREY),
]))

# Skills block (2 col)
sk_pairs = [(skills[i], skills[i+1]) for i in range(0, len(skills)-1, 2)]
sk_rows = [[Paragraph("- " + a, sSK), Paragraph("- " + b if b else "", sSK)] for a,b in sk_pairs]
sk_tbl = Table(sk_rows, colWidths=[INNER*0.65/2]*2)
sk_tbl.setStyle(TableStyle([
    ("TOPPADDING",    (0,0),(-1,-1), 0.5),
    ("BOTTOMPADDING", (0,0),(-1,-1), 0.5),
    ("LEFTPADDING",   (0,0),(-1,-1), 0),
    ("RIGHTPADDING",  (0,0),(-1,-1), 2),
]))

# Combined metrics + skills row
MET_W  = INNER * 0.35
SK_W   = INNER * 0.65
sec_titles_row = Table([[
    Paragraph("KEY METRICS", sSEC),
    Paragraph("CORE SKILLS & COMPETENCIES", sSEC),
]], colWidths=[MET_W, SK_W])
sec_titles_row.setStyle(TableStyle([
    ("TOPPADDING",    (0,0),(-1,-1), 0),
    ("BOTTOMPADDING", (0,0),(-1,-1), 1),
    ("LEFTPADDING",   (0,0),(-1,-1), 0),
    ("RIGHTPADDING",  (0,0),(-1,-1), 0),
]))
story.append(sec_titles_row)
story.append(HRFlowable(width=INNER, thickness=1, color=CYAN, spaceAfter=2))

content_row = Table([[met_tbl, sk_tbl]], colWidths=[MET_W, SK_W])
content_row.setStyle(TableStyle([
    ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ("TOPPADDING",    (0,0),(-1,-1), 0),
    ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ("LEFTPADDING",   (0,0),(-1,-1), 0),
    ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ("LINEAFTER",     (0,0),(0,-1), 0.5, GREY),
    ("LEFTPADDING",   (1,0),(1,-1), 6),
]))
story.append(content_row)
story.append(Spacer(1, 3*mm))

# ══ PROFESSIONAL SUMMARY ═════════════════════════════════════════════════
story += sec("Professional Summary")
story.append(Paragraph(
    "Product Leader with 10+ years delivering technology products from zero to scale in AI, SaaS, "
    "and learning-adjacent systems. Raised <b>$2.5M</b>, led teams of 20+, and drove <b>38% efficiency gains</b>. "
    "Experienced in full product lifecycle (PRD/MRD/V&amp;V), supplier management, global projects, and Agile "
    "in regulated industries. Technion-educated (BSc + Executive MBA). Passionate about AI-driven "
    "<b>training, simulation, and enterprise learning systems</b>.",
    sBODY))
story.append(Spacer(1, 3*mm))

# ══ PROFESSIONAL EXPERIENCE ══════════════════════════════════════════════
story += sec("Professional Experience")

def exp_entry(org, role, dates, tags, bullets):
    # Org + date row — full INNER width
    row = Table(
        [[Paragraph(f"<b>{org}</b>", sORG), Paragraph(dates, sDATE)]],
        colWidths=[INNER * 0.72, INNER * 0.28]
    )
    row.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
        ("TOPPADDING",   (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
    ]))
    story.append(row)
    story.append(Paragraph(role, sROLE))
    story.append(Paragraph(tags, sTAG))
    for b in bullets:
        story.append(bul(b))
    story.append(Spacer(1, 2.5*mm))

exp_entry(
    "Inon Baasov Ltd", "Product Strategy Consultant", "2024 – Present",
    "GenAI  |  AI Strategy  |  GTM  |  Consulting",
    [
        "Advising 3 early-stage AI startups on product strategy, GTM, and 12-month roadmap execution",
        "AiRakoon — Enterprise AI: LLM architecture, API design, enterprise GTM delivery",
        "Medicrowd — MedTech AI: Full MVP spec in regulated HL7 environment; dual UX for clinicians and investors",
        "Smash+ — Wellness App: B2C behavioral design, cohort analysis, D7/D30 KPI framework",
    ]
)
exp_entry(
    "TouchE TV", "Co-Founder & Chief Product Officer", "2018 – 2024",
    "CPO  |  SaaS/PaaS  |  AWS  |  AI/ML  |  Android/iOS/Smart TV",
    [
        "Built AI-powered interactive video learning platform from 0 to scale; raised $2.5M seed funding",
        "Led 4 cross-functional teams across full 6-year product lifecycle; authored all PRD/MRD documentation",
        "Achieved 99.99% uptime on AWS serving millions of concurrent users; drove 38% operational efficiency gains",
        "Managed supplier relationships, external dev vendors, and international partnership programs",
    ]
)
exp_entry(
    "Arena Plus Financial Services", "Senior Product Manager", "2013 – 2018",
    "FinTech  |  B2B  |  Agile  |  Regulated  |  Global",
    [
        "Promoted PM to Senior PM in 18 months; managed global cross-functional teams across FinTech platforms",
        "Delivered +22% user adoption, +15% revenue growth, and -20% TTM via Agile methodology",
    ]
)
exp_entry(
    "Blau Pharmaceuticals", "Regulatory Affairs Consultant", "2009 – 2011",
    "Regulatory  |  Pharma  |  MoH  |  V&V  |  Team Lead",
    [
        "Led Israeli MoH regulatory submissions and headed Pharmacovigilance department with 6-person team",
    ]
)

# ══ EDUCATION ══════════════════════════════════════════════════════════════
story += sec("Education")
edu = [
    ("Executive MBA — Entrepreneurship & High-Tech Management", "Technion – IIT", "2016–2018"),
    ("B.Sc. — Biotechnology & Food Engineering",               "Technion – IIT", "2005–2008"),
    ("Faculty Studies — Chemical Engineering",                  "McGill University, Canada", "2004–2005"),
]
for deg, school, yr in edu:
    row = Table([[Paragraph(f"<b>{deg}</b>  |  {school}", sBODY), Paragraph(yr, sDATE)]],
                colWidths=[INNER * 0.78, INNER * 0.22])
    row.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
        ("TOPPADDING",   (0,0),(-1,-1), 0.5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0.5),
    ]))
    story.append(row)

story.append(Spacer(1, 2.5*mm))

# ══ LANGUAGES ══════════════════════════════════════════════════════════════
story += sec("Languages & Availability")
story.append(Paragraph(
    "Hebrew — Native  |  English — Fluent (C2)  |  Location: Israel  |  Available Now  |  Open to travel",
    sBODY))

# ══ BUILD ═══════════════════════════════════════════════════════════════════
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    topMargin=0,
    bottomMargin=8*mm,
    leftMargin=M,
    rightMargin=M,
)
doc.build(story)
print("CV generated: " + OUTPUT)
