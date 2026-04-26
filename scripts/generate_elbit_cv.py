"""
Generate Inon Baasov CV – tailored for Elbit Systems Product Manager (Learning Dept.)
Output: output/cv_archive/Inon_Baasov_CV_Elbit_2026.pdf
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
import os

os.makedirs("output/cv_archive", exist_ok=True)
OUTPUT = "output/cv_archive/Inon_Baasov_CV_Elbit_2026.pdf"

W, H = A4
MARGIN = 16 * mm
INNER  = W - 2 * MARGIN

# ── Colours ───────────────────────────────────────────────────────────────────
NAVY  = colors.HexColor("#0d1f3c")
CYAN  = colors.HexColor("#00b4d8")
GREY  = colors.HexColor("#5a6272")
LGREY = colors.HexColor("#f0f4f8")
BLACK = colors.HexColor("#1a1a2e")
WHITE = colors.white

# ── Style factory ─────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

# ── Styles ────────────────────────────────────────────────────────────────────
sNAME  = S("sNAME",  fontName="Helvetica-Bold", fontSize=24, textColor=WHITE,  leading=28, alignment=TA_LEFT)
sTITLE = S("sTITLE", fontName="Helvetica",      fontSize=11, textColor=CYAN,   leading=15, alignment=TA_LEFT)
sAPPLY = S("sAPPLY", fontName="Helvetica-Bold", fontSize=8.5,textColor=LGREY,  leading=12, alignment=TA_LEFT)
sCON   = S("sCON",   fontName="Helvetica",      fontSize=8,  textColor=WHITE,  leading=11, alignment=TA_LEFT)

sSEC   = S("sSEC",   fontName="Helvetica-Bold", fontSize=10, textColor=NAVY,   leading=14, spaceBefore=4, spaceAfter=1)
sBODY  = S("sBODY",  fontName="Helvetica",      fontSize=8.5,textColor=BLACK,  leading=12, alignment=TA_JUSTIFY)
sBUL   = S("sBUL",   fontName="Helvetica",      fontSize=8.5,textColor=BLACK,  leading=12, leftIndent=10, firstLineIndent=-8, spaceBefore=1)
sORG   = S("sORG",   fontName="Helvetica-Bold", fontSize=9.5,textColor=NAVY,   leading=13)
sROLE  = S("sROLE",  fontName="Helvetica-Bold", fontSize=9,  textColor=CYAN,   leading=12)
sDATE  = S("sDATE",  fontName="Helvetica",      fontSize=8,  textColor=GREY,   leading=12, alignment=TA_RIGHT)
sTAG   = S("sTAG",   fontName="Helvetica-Oblique",fontSize=7.5,textColor=GREY, leading=11, spaceAfter=2)
sMET   = S("sMET",   fontName="Helvetica-Bold", fontSize=10.5,textColor=CYAN,  leading=14)
sMEL   = S("sMEL",   fontName="Helvetica",      fontSize=7.5, textColor=GREY,  leading=11)
sNOTE  = S("sNOTE",  fontName="Helvetica-Oblique",fontSize=8.5,textColor=NAVY, leading=12, alignment=TA_JUSTIFY)

def hr():
    return HRFlowable(width=INNER, thickness=1.2, color=CYAN, spaceAfter=3, spaceBefore=1)

def section_title(t):
    return [Paragraph(t.upper(), sSEC), hr()]

def bullet(t):
    return Paragraph(f"• {t}", sBUL)

# ── Build story ───────────────────────────────────────────────────────────────
story = []

# ── HEADER ────────────────────────────────────────────────────────────────────
hdr = Table([[
    [
        Paragraph("INON BAASOV", sNAME),
        Spacer(1, 2),
        Paragraph("Product Leader  ·  Co-Founder  ·  CPO", sTITLE),
        Spacer(1, 3),
        Paragraph("Applying for: Product Manager – Learning Department, Elbit Systems", sAPPLY),
    ]
]], colWidths=[INNER + 2*MARGIN])
hdr.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), NAVY),
    ("TOPPADDING",    (0,0),(-1,-1), 10),
    ("BOTTOMPADDING", (0,0),(-1,-1), 10),
    ("LEFTPADDING",   (0,0),(-1,-1), MARGIN),
    ("RIGHTPADDING",  (0,0),(-1,-1), MARGIN),
]))
story.append(hdr)

# Contact bar
con = Table([[
    Paragraph("✉ Inonbaasov@hotmail.com", sCON),
    Paragraph("✆ +972-54-444-5856", sCON),
    Paragraph("⚑ Israel  ·  Available Now", sCON),
    Paragraph("linkedin.com/in/inonbaasov", sCON),
]], colWidths=[(INNER+2*MARGIN)/4]*4)
con.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), CYAN),
    ("TOPPADDING",    (0,0),(-1,-1), 4),
    ("BOTTOMPADDING", (0,0),(-1,-1), 4),
    ("LEFTPADDING",   (0,0),(-1,-1), MARGIN),
    ("RIGHTPADDING",  (0,0),(-1,-1), 4),
]))
story.append(con)
story.append(Spacer(1, 4*mm))

# ── BODY wrapper ──────────────────────────────────────────────────────────────
def body(*items):
    for i in items:
        story.append(i)

# ── RELEVANCE NOTE ────────────────────────────────────────────────────────────
note_tbl = Table([[Paragraph(
    "<b>Why Elbit Learning Systems?</b>  Inon's combination of AI product leadership, "
    "cross-functional team management in regulated tech environments, and a Technion engineering "
    "foundation (BSc + Executive MBA) positions him uniquely to lead TPSS, simulation, "
    "and AI-assisted learning platforms.",
    sNOTE
)]], colWidths=[INNER])
note_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), LGREY),
    ("TOPPADDING",    (0,0),(-1,-1), 6),
    ("BOTTOMPADDING", (0,0),(-1,-1), 6),
    ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ("RIGHTPADDING",  (0,0),(-1,-1), 8),
    ("BOX",           (0,0),(-1,-1), 1.5, CYAN),
]))
body(Spacer(1,2*mm), note_tbl, Spacer(1,4*mm))

# ── KEY METRICS (horizontal bar) ──────────────────────────────────────────────
body(*section_title("Key Metrics"))
metrics = [
    ("10+",    "Years PM Leadership"),
    ("$2.5M",  "Seed Capital Raised"),
    ("38%",    "Efficiency Gains"),
    ("6",      "Products Shipped"),
    ("4",      "Cross-Func. Teams"),
    ("99.99%", "Platform Uptime"),
]
m_data = [[Paragraph(v, sMET) for v,_ in metrics]]
m_labels = [[Paragraph(l, sMEL) for _,l in metrics]]
m_tbl = Table(m_data + m_labels, colWidths=[INNER/6]*6)
m_tbl.setStyle(TableStyle([
    ("ALIGN",         (0,0),(-1,-1), "CENTER"),
    ("TOPPADDING",    (0,0),(-1,-1), 2),
    ("BOTTOMPADDING", (0,0),(-1,-1), 2),
    ("LEFTPADDING",   (0,0),(-1,-1), 2),
    ("RIGHTPADDING",  (0,0),(-1,-1), 2),
]))
body(m_tbl, Spacer(1,4*mm))

# ── PROFESSIONAL SUMMARY ──────────────────────────────────────────────────────
body(*section_title("Professional Summary"))
body(Paragraph(
    "Product Leader with 10+ years delivering technology products from zero to scale in AI, "
    "SaaS, and learning-adjacent systems. Raised <b>$2.5M</b>, led teams of 20+, and drove "
    "<b>38% efficiency gains</b> across complex cross-functional environments. Experienced in "
    "full product lifecycle management (PRD/MRD/V&amp;V), supplier oversight, global project "
    "leadership, and Agile delivery in regulated industries. Technion-educated engineer (BSc + "
    "Executive MBA) with a track record of translating operational requirements into scalable, "
    "user-centric products. Excited to apply AI and interactive technology to <b>training "
    "simulation, defence learning systems, and enterprise EdTech</b> at Elbit.",
    sBODY
), Spacer(1,4*mm))

# ── PROFESSIONAL EXPERIENCE ───────────────────────────────────────────────────
body(*section_title("Professional Experience"))

exp = [
    {
        "org": "Inon Baasov Ltd",
        "role": "Product Strategy Consultant",
        "dates": "2024 – Present",
        "tags": "GenAI · AI Strategy · GTM · Consulting",
        "bullets": [
            "Advising 3 early-stage AI startups on product strategy, GTM, and 12-month roadmap execution",
            "AiRakoon — Enterprise AI Model Platform: LLM architecture, API design, enterprise GTM delivery",
            "Medicrowd — Medical AI Funding Platform: Full MVP specification in regulated HL7 environment; dual UX for clinicians and investors",
            "Smash+ — Fitness App: B2C behavioral design, cohort analysis, D7/D30 KPI framework, 18% estimated churn reduction",
        ]
    },
    {
        "org": "TouchE TV",
        "role": "Co-Founder & Chief Product Officer",
        "dates": "2018 – 2024",
        "tags": "CPO · SaaS/PaaS · AWS · AI/ML · Android/iOS/Smart TV",
        "bullets": [
            "Built AI-powered interactive video learning platform from 0→scale; raised $2.5M seed funding",
            "Led 4 cross-functional teams (engineering, product, design, data) across complete 6-year product lifecycle",
            "Authored all PRD/MRD documentation; drove full V&V cycles, supplier management, and global launch programs",
            "Achieved 99.99% uptime on AWS serving millions of concurrent users; 38% operational efficiency gains",
            "Managed international partner relationships and external development vendors across multiple time zones",
        ]
    },
    {
        "org": "Arena Plus Financial Services",
        "role": "Senior Product Manager",
        "dates": "2013 – 2018",
        "tags": "FinTech · B2B · Agile · Regulated · Global",
        "bullets": [
            "Promoted PM → Senior PM in 18 months; managed global cross-functional teams across FinTech platforms",
            "Delivered +22% user adoption, +15% revenue growth, −20% TTM through Agile transformation",
            "Managed complex B2B product lifecycle in multiple regulated financial markets",
        ]
    },
    {
        "org": "Blau Pharmaceuticals",
        "role": "Regulatory Affairs Consultant",
        "dates": "2009 – 2011",
        "tags": "Regulatory · Pharma · MoH · V&V · Team Lead",
        "bullets": [
            "Led Israeli Ministry of Health regulatory submissions and headed Pharmacovigilance department",
            "Managed 6-person team supporting global pharmaceutical clients in regulated documentation workflows",
        ]
    },
]

for e in exp:
    row = Table([[Paragraph(f"<b>{e['org']}</b>", sORG), Paragraph(e['dates'], sDATE)]],
                colWidths=[INNER*0.72, INNER*0.28])
    row.setStyle(TableStyle([
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    body(row, Paragraph(e['role'], sROLE), Paragraph(e['tags'], sTAG))
    for b in e['bullets']:
        body(bullet(b))
    body(Spacer(1, 4*mm))

# ── CORE SKILLS ───────────────────────────────────────────────────────────────
body(*section_title("Core Skills & Competencies"))
skills = [
    ["Product Lifecycle Mgmt (0→Scale)",   "PRD / MRD / BRD Authorship",    "Training & Learning Systems"],
    ["AI / LLM Product Design",            "V&V Processes & Testing",        "Strategic Roadmapping"],
    ["Cross-functional Team Leadership",   "Budget & P&L Management",        "Supplier & Vendor Management"],
    ["Market Research & Competitive Intel","Global Project Management",       "Agile / Scrum / OKRs"],
    ["Business Development & GTM",         "SaaS / PaaS Architecture",       "Regulatory Environments (HL7, MoH)"],
]
sk_tbl = Table(
    [[Paragraph(f"• {a}", sBUL), Paragraph(f"• {b}", sBUL), Paragraph(f"• {c}", sBUL)] for a,b,c in skills],
    colWidths=[INNER/3]*3
)
sk_tbl.setStyle(TableStyle([
    ("TOPPADDING",    (0,0),(-1,-1), 1),
    ("BOTTOMPADDING", (0,0),(-1,-1), 1),
    ("LEFTPADDING",   (0,0),(-1,-1), 0),
    ("RIGHTPADDING",  (0,0),(-1,-1), 0),
]))
body(sk_tbl, Spacer(1,4*mm))

# ── EDUCATION ─────────────────────────────────────────────────────────────────
body(*section_title("Education"))
edu = [
    ("Executive MBA", "Entrepreneurship & High-Tech Management", "Technion – Israel Institute of Technology", "2016–2018"),
    ("B.Sc.", "Biotechnology & Food Engineering", "Technion – Israel Institute of Technology", "2005–2008"),
    ("Faculty Studies", "Chemical Engineering", "McGill University, Montreal, Canada", "2004–2005"),
]
for deg, field, school, yr in edu:
    row = Table([[
        Paragraph(f"<b>{deg}</b> — {field}", sBODY),
        Paragraph(yr, sDATE)
    ]], colWidths=[INNER*0.75, INNER*0.25])
    row.setStyle(TableStyle([
        ("LEFTPADDING",   (0,0),(-1,-1), 0),("RIGHTPADDING",(0,0),(-1,-1), 0),
        ("TOPPADDING",    (0,0),(-1,-1), 0),("BOTTOMPADDING",(0,0),(-1,-1), 0),
    ]))
    body(row, Paragraph(school, sTAG))

body(Spacer(1,3*mm))

# ── LANGUAGES & PERSONAL ──────────────────────────────────────────────────────
lang_tbl = Table([[
    [*section_title("Languages"), bullet("Hebrew — Native"), bullet("English — Fluent (C2)"), Spacer(1,1)],
    [*section_title("Personal"), bullet("Location: Israel  ·  Available Now"), bullet("Open to: Senior PM / CPO Roles"), bullet("Willing to travel internationally")]
]], colWidths=[INNER*0.45, INNER*0.55])
lang_tbl.setStyle(TableStyle([
    ("VALIGN",       (0,0),(-1,-1), "TOP"),
    ("LEFTPADDING",  (0,0),(0,-1), 0),
    ("RIGHTPADDING", (0,0),(0,-1), 10),
    ("LEFTPADDING",  (1,0),(1,-1), 10),
    ("RIGHTPADDING", (1,0),(1,-1), 0),
    ("TOPPADDING",   (0,0),(-1,-1), 0),
    ("BOTTOMPADDING",(0,0),(-1,-1), 0),
]))
body(lang_tbl)

# ── DOCUMENT ──────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    topMargin=0,
    bottomMargin=10*mm,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
)
doc.build(story)
print(f"CV generated: {OUTPUT}")
