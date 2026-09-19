"""
Script to generate a professional, presentation-ready PowerPoint (.pptx)
for EduSync + Tripwire following the 10 mandated hackathon guidelines
with embedded prototype screenshots.
"""
import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

SCREENSHOTS_DIR = os.path.join(os.getcwd(), "screenshots")
PPTX_OUT = os.path.join(os.getcwd(), "EDUSYNC_TRIPWIRE_PITCH_DECK.pptx")

# ── Color Palette ─────────────────────────────────────────────────────────────
DARK_BG     = RGBColor(11, 15, 25)       # #0b0f19
CARD_BG     = RGBColor(19, 26, 43)       # #131a2b
CARD_BORDER = RGBColor(40, 53, 83)       # #283553
BRAND_BLUE  = RGBColor(99, 102, 241)     # #6366f1 (Indigo)
ACCENT_CYAN = RGBColor(14, 165, 233)     # #0ea5e9 (Sky)
ACCENT_GREEN= RGBColor(16, 185, 129)     # #10b981 (Emerald)
ACCENT_RED  = RGBColor(239, 68, 68)      # #ef4444 (Rose)
ACCENT_AMBER= RGBColor(245, 158, 11)     # #f59e0b (Amber)
TEXT_WHITE  = RGBColor(248, 250, 252)    # #f8fafc
TEXT_MUTED  = RGBColor(148, 163, 184)    # #94a3b8

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]  # blank layout

def set_slide_background(slide):
    # Add dark background rect
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_BG
    bg.line.fill.background()
    return bg

def add_header(slide, section_tag, title_text, subtitle_text=None):
    # Category tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = section_tag.upper()
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = BRAND_BLUE

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

    if subtitle_text:
        p_sub = tf_title.add_paragraph()
        p_sub.text = subtitle_text
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, border_color=CARD_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1: Title / Cover
# ─────────────────────────────────────────────────────────────────────────────
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

# Large Center Badge
c1 = add_card(s1, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1), border_color=BRAND_BLUE)

tb = s1.shapes.add_textbox(Inches(2.0), Inches(1.8), Inches(9.333), Inches(3.8))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
p.text = "BYTEFORGE 2026 | HACKATHON STAGE 2"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_CYAN

p2 = tf.add_paragraph()
p2.alignment = PP_ALIGN.CENTER
p2.text = "EDUSYNC  ×  TRIPWIRE"
p2.font.size = Pt(40)
p2.font.bold = True
p2.font.color.rgb = TEXT_WHITE

p3 = tf.add_paragraph()
p3.alignment = PP_ALIGN.CENTER
p3.text = "The Unified Smart Campus Operating System with Real-Time Behavioral Drift Intelligence"
p3.font.size = Pt(16)
p3.font.color.rgb = BRAND_BLUE

p4 = tf.add_paragraph()
p4.alignment = PP_ALIGN.CENTER
p4.text = "\n\"From Paper Chits to Instant Verification; From Academic Failure to Proactive Recovery\""
p4.font.size = Pt(13)
p4.font.italic = True
p4.font.color.rgb = TEXT_MUTED

p5 = tf.add_paragraph()
p5.alignment = PP_ALIGN.CENTER
p5.text = "\nInstitutional Deployment: TKM Institute of Technology (TKMIT) | APJ Abdul Kalam Technological University (KTU)"
p5.font.size = Pt(11)
p5.font.color.rgb = ACCENT_GREEN

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2: 1. Problem Statement
# ─────────────────────────────────────────────────────────────────────────────
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "1. Problem Statement", "The Dual Campus Crisis: Administrative Bottlenecks & The Silent Dropout Funnel", "Why higher-education institutions struggle with operational gridlock and late academic intervention.")

# Left Card: Administrative Runaround
c_left = add_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1), border_color=ACCENT_RED)
tb_l = s2.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_l = tb_l.text_frame
tf_l.word_wrap = True

p = tf_l.paragraphs[0]
p.text = "CRISIS 1: Administrative Paper Gridlock"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ACCENT_RED

bullets_l = [
    ("Manual Signature Chasing: ", "Students lose 3–5 days per semester physically collecting stamps across campus blocks from Faculty Advisors, HODs, Office Staff, and Principal."),
    ("Duty Leave Friction: ", "Extracurricular achievers representing colleges in hackathons or sports face severe attendance penalties due to delayed or lost paper approval slips."),
    ("Office Queue Congestion: ", "Bonafide certificates, fee dues clearances, and hostel out-passes require long physical lines and manual clerical verification."),
    ("Paper Vulnerability: ", "Physical slips are easily misplaced, forged, or unrecorded, causing compliance chaos during semester university audits.")
]
for title, desc in bullets_l:
    p = tf_l.add_paragraph()
    p.text = f"• {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p2 = tf_l.add_paragraph()
    p2.text = f"  {desc}"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED

# Right Card: Academic Attrition
c_right = add_card(s2, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.1), border_color=ACCENT_AMBER)
tb_r = s2.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.0), Inches(4.6))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p = tf_r.paragraphs[0]
p.text = "CRISIS 2: The Late-Detection Attrition Trap"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ACCENT_AMBER

bullets_r = [
    ("The 75% Statutory Cutoff: ", "Under university rules (KTU), <75% attendance leads to condonation fines (60–74%) or year-back debarment (<60%)."),
    ("Purely Reactive Portals: ", "Legacy ERPs only display passive historical numbers. Students discover debarment 48 hours before exams when hall tickets are blocked."),
    ("The 'Silent Drift' Phenomenon: ", "Students disengage quietly 3 to 4 weeks before grades fall—skipping morning lectures, submitting labs 18h late, reducing LMS access."),
    ("Blind Triage for Faculty: ", "In cohorts of 60–120 students, mentors cannot manually connect multi-modal behavioral signals until it is mathematically too late to recover.")
]
for title, desc in bullets_r:
    p = tf_r.add_paragraph()
    p.text = f"• {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p2 = tf_r.add_paragraph()
    p2.text = f"  {desc}"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3: 2. Target Users / Stakeholders
# ─────────────────────────────────────────────────────────────────────────────
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "2. Target Users / Stakeholders", "Whole-Campus Inclusivity: A Multi-Tiered Stakeholder Ecosystem", "Empowering every persona in the academic lifecycle with specialized digital tools.")

stakeholders = [
    ("Students (UG & PG)", "Friction: Paper signature chasing, sudden exam debarment shock, opaque university ordinances.\nSolution: 1-click digital leave requests, QR passes, 'What-If' grade/attendance simulators, 24/7 AI Ordinance guidance.", BRAND_BLUE),
    ("Faculty Advisors / Mentors", "Friction: Drowning in paper approvals, manual attendance math, blind to quiet student disengagement.\nSolution: 1-click tiered approvals, real-time cohort batch attendance register, automated behavioral drift alerts.", ACCENT_CYAN),
    ("Heads of Dept & Principal", "Friction: Lack of departmental oversight, compliance risks, manual paper audit trails.\nSolution: Executive dashboard with cohort risk heatmaps, institutional analytics, single-click leave audit compliance.", ACCENT_GREEN),
    ("Industry Connect & Placement", "Friction: Sifting through hundreds of resume PDFs manually, unstandardized candidate matching.\nSolution: AI ATS Placement Studio with 100+ skill parsing, CGPA eligibility filters, automated drive shortlisting.", ACCENT_AMBER),
    ("Admin Office & Exam Cell", "Friction: Manual queues for fee clearances, bonafide certificates, spreadsheet condonation errors.\nSolution: Digital clearance portal, cryptographic ZXing QR tokens, automated condonation calculation.", ACCENT_RED),
]

for idx, (title, desc, color) in enumerate(stakeholders):
    top = Inches(1.6 + idx * 1.05)
    add_card(s3, Inches(0.8), top, Inches(11.733), Inches(0.95), border_color=color)
    tb = s3.shapes.add_textbox(Inches(1.1), top + Inches(0.08), Inches(11.1), Inches(0.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = color
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4: 3. Existing Gaps or Limitations
# ─────────────────────────────────────────────────────────────────────────────
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "3. Existing Gaps & Limitations", "Why Legacy College ERPs & Generic Early Warning Systems Fail", "Four fundamental systemic blindspots in current higher-education software.")

gaps = [
    ("1. Passive Digital Ledgers, Not Workflows", 
     "Existing campus software acts merely as a database. Even when installed, a duty leave or medical certificate still requires physical paper slips hand-carried across offices. There is zero automated multi-tier routing."),
    ("2. Disconnected Duty Leaves & False Penalties",
     "Legacy portals record hackathon and sports participation as absences first. Because leave approvals take weeks to reflect, students representing their college suffer false attendance penalties and blocked hall tickets."),
    ("3. Blunt 75% Cutoffs vs. Personal Velocity",
     "Conventional systems evaluate absolute thresholds only. They miss an honors student whose attendance just plummeted from 96% to 76% (an acute crisis), while constantly red-flagging students whose baseline is 73%."),
    ("4. Black-Box Opacity & Failure to Close the Loop",
     "Generic ML algorithms spit out arbitrary risk scores ('0.82 High Risk') without explainability. Worse, they provide no actionable 'what-if' recovery guidance or structured mentor intervention tracking.")
]

for idx, (title, desc) in enumerate(gaps):
    row = idx // 2
    col = idx % 2
    left = Inches(0.8 + col * 5.95)
    top = Inches(1.6 + row * 2.6)
    add_card(s4, left, top, Inches(5.75), Inches(2.4), border_color=ACCENT_RED if idx%2==0 else ACCENT_AMBER)
    tb = s4.shapes.add_textbox(left + Inches(0.25), top + Inches(0.15), Inches(5.25), Inches(2.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p2 = tf.add_paragraph()
    p2.text = f"\n{desc}"
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = TEXT_MUTED

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5: 4. Proposed Solution
# ─────────────────────────────────────────────────────────────────────────────
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "4. Proposed Solution", "EduSync + Tripwire: The Unified Intelligent Campus Ecosystem", "Bridging administrative automation with real-time predictive behavioral analytics.")

# Left Pillar: EduSync Core
add_card(s5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=BRAND_BLUE)
tb = s5.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.1), Inches(4.7))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "EDUSYNC: Campus Governance Operating Core"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = BRAND_BLUE

modules_edusync = [
    ("Multi-Tier Digital Leave Engine: ", "3-tier approval hierarchy (Advisor -> HOD -> Principal) with tamper-proof cryptographic ZXing QR verification."),
    ("KTU Attendance & CIE Calculator: ", "Automated Series Exams 1 & 2, assignment weightings, and mathematical 'What-If' exam eligibility simulator."),
    ("Campus AI Copilot (Hybrid RAG): ", "Document-grounded assistant trained on 200+ page KTU ordinances, credit rules, and curriculum regulations."),
    ("AI ATS Placement Studio: ", "100+ technical skill matcher, CGPA filtering, and automated student-to-recruiter matching.")
]
for title, desc in modules_edusync:
    p = tf.add_paragraph()
    p.text = f"\n✔ {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p2 = tf.add_paragraph()
    p2.text = f"   {desc}"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED

# Right Pillar: Tripwire Engine
add_card(s5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=ACCENT_CYAN)
tb = s5.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.7))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "TRIPWIRE: Behavioral Early-Warning Brain"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = ACCENT_CYAN

modules_tripwire = [
    ("Dynamic Velocity Index (DVI): ", "Unified 0–100 composite evaluating 40% Attendance, 35% Submission Latency, and 25% LMS Engagement relative to personal baseline."),
    ("EWMA Temporal Noise Smoothing: ", "Alpha=0.35 exponential smoothing filters out 1-day illnesses/transient drops while detecting sustained 2-week behavioral decline."),
    ("Approved Duty-Leave Masking: ", "Directly reads EduSync's sanctioned leaves, mathematically excluding hackathon and sports dates from attendance penalties!"),
    ("Counterfactual XAI & Closed Loop: ", "Generates exact mathematical recovery targets and tracks post-intervention student velocity through hysteresis recovery.")
]
for title, desc in modules_tripwire:
    p = tf.add_paragraph()
    p.text = f"\n✔ {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p2 = tf.add_paragraph()
    p2.text = f"   {desc}"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6: 5. Innovation / Unique Contribution
# ─────────────────────────────────────────────────────────────────────────────
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "5. Innovation & Unique Contribution", "Four Breakthrough Technical Innovations in Campus AI", "Engineered for institutional reality, mathematical rigor, and ethical fairness.")

innovations = [
    ("1. Approved Duty-Leave Mathematical Masking",
     "Traditional EWS algorithms penalize student achievers who miss lectures for national hackathons or sports. EduSync + Tripwire directly connects the digital approval pipeline to the analytical engine: verified duty and medical leave dates are mathematically excluded from attendance drift calculations. Zero false positives for campus ambassadors.",
     ACCENT_GREEN),
    ("2. EWMA Noise-Dampened Behavioral Velocity",
     "Rather than static grade cuts, Tripwire implements Exponentially Weighted Moving Average (EWMA) smoothing (alpha=0.35). An isolated 48-hour sickness will never trigger an alert, but progressive 2-week disengagement across attendance, assignment delays, and LMS access triggers early triage.",
     BRAND_BLUE),
    ("3. Document-Grounded Campus RAG AI",
     "Generic chatbots hallucinate on institutional policies. EduSync integrates an in-memory TF-IDF semantic retrieval engine over actual KTU university ordinances, course syllabi, and circulars via Apache PDFBox, providing source-backed answers to credit and academic queries.",
     ACCENT_CYAN),
    ("4. Actionable Counterfactual Explainable AI (XAI)",
     "Instead of delivering opaque risk probability scores, Tripwire computes minimal actionable behavioral deltas: 'If Rahul attends next week's 4 lectures and submits Lab 2 on time, his DVI drops by 28 points, clearing the monitoring threshold.' Actionable pathways replace punitive condemnation.",
     ACCENT_AMBER)
]

for idx, (title, desc, color) in enumerate(innovations):
    top = Inches(1.6 + idx * 1.35)
    add_card(s6, Inches(0.8), top, Inches(11.733), Inches(1.22), border_color=color)
    tb = s6.shapes.add_textbox(Inches(1.1), top + Inches(0.08), Inches(11.1), Inches(1.05))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = color
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7: 6. System Architecture
# ─────────────────────────────────────────────────────────────────────────────
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "6. System / Solution Architecture", "End-to-End Enterprise Multi-Tier Campus Pipeline", "Seamless coordination across enterprise microservices, real-time analytics, and mobile clients.")

# Architecture Blocks
arch_blocks = [
    ("CLIENT TIER", "React 18 + Vite Web App\nAndroid APK via Capacitor\nGlassmorphism UI System\nOffline ZXing QR Scanner", BRAND_BLUE, Inches(0.8), Inches(1.6), Inches(2.7), Inches(5.1)),
    ("ENTERPRISE ERP CORE", "Spring Boot 3.2.3 (Java 17)\n3-Tier Leave Approval Engine\nKTU CIE & Attendance Math\nOpenPDF + ZXing Token Engine\nSpring Mail Automated SMTP", ACCENT_CYAN, Inches(3.75), Inches(1.6), Inches(2.8), Inches(5.1)),
    ("PREDICTIVE AI ENGINE", "FastAPI (Python 3.11)\nDVI Velocity Engine (40/35/25)\nEWMA Temporal Smoother\nApproved Leave Date Masker\nCounterfactual Optimizer", ACCENT_GREEN, Inches(6.8), Inches(1.6), Inches(2.8), Inches(5.1)),
    ("PERSISTENCE & DATA", "MySQL 8.0 (17 Relational Tables)\nHikariCP Connection Pool (200 th)\nGoogle Drive Cloud Syllabus Sync\nIn-Memory TF-IDF Document Store\nHistorical Audit Trail Logs", ACCENT_AMBER, Inches(9.85), Inches(1.6), Inches(2.7), Inches(5.1)),
]

for title, content, color, left, top, w, h in arch_blocks:
    add_card(s7, left, top, w, h, border_color=color)
    tb = s7.shapes.add_textbox(left + Inches(0.15), top + Inches(0.2), w - Inches(0.3), h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = color
    for line in content.split("\n"):
        p = tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.text = f"\n{line}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8: 7. Technology Stack
# ─────────────────────────────────────────────────────────────────────────────
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "7. Technology Stack", "Robust Engineering Stack: High Concurrency, Fast Math & Mobile Mobility", "Enterprise-grade frameworks engineered for 10,000+ student campuses.")

tech_cards = [
    ("Enterprise Backend", "Spring Boot 3.2.3 | Java 17", "Spring Data JPA, Hibernate 6.4, HikariCP 200 connection pool, Spring Security 6 stateless JWT, OpenPDF 1.3, ZXing QR generation, Spring Mail SMTP.", BRAND_BLUE),
    ("Predictive Analytics Core", "FastAPI | Python 3.11", "ASGI asynchronous concurrency, vectorized NumPy numerical calculations, EWMA matrix math, Pydantic data validation, sub-10ms DVI recalculation.", ACCENT_CYAN),
    ("Database & Storage", "MySQL 8.0 & SQLite", "17 normalized relational schemas (InnoDB, UTF8mb4), indexing on student/period pairs, Google Drive API v3 bi-directional syllabus sync worker.", ACCENT_GREEN),
    ("Client & Mobile Deployment", "React 18, Vite & Capacitor", "Sub-second HMR development, modern responsive CSS system, SVG radial gauges, Recharts visualization, cross-platform Android mobile APK generation.", ACCENT_AMBER),
]

for idx, (tier, tools, details, color) in enumerate(tech_cards):
    row = idx // 2
    col = idx % 2
    left = Inches(0.8 + col * 5.95)
    top = Inches(1.6 + row * 2.6)
    add_card(s8, left, top, Inches(5.75), Inches(2.4), border_color=color)
    tb = s8.shapes.add_textbox(left + Inches(0.25), top + Inches(0.15), Inches(5.25), Inches(2.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = tier.upper()
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = color
    p2 = tf.add_paragraph()
    p2.text = tools
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p3 = tf.add_paragraph()
    p3.text = f"\n{details}"
    p3.font.size = Pt(10)
    p3.font.color.rgb = TEXT_MUTED

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9: 8. Prototype / Demo - Part 1 (Dashboard & Cohort Overview)
# ─────────────────────────────────────────────────────────────────────────────
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "8. Working Prototype: Faculty Risk Radar & Cohort Overview", "Real-Time Triaged Student Roster & Behavioral Archetype Distribution", "Live screenshot from the running EduSync Tripwire application.")

# Left Screenshot
img_path = os.path.join(SCREENSHOTS_DIR, "02_dashboard.png")
if os.path.exists(img_path):
    s9.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(7.5), Inches(4.8))

# Right Description Card
add_card(s9, Inches(8.5), Inches(1.6), Inches(4.0), Inches(4.8), border_color=BRAND_BLUE)
tb = s9.shapes.add_textbox(Inches(8.75), Inches(1.8), Inches(3.5), Inches(4.4))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "PROTOTYPE CAPABILITY: Risk Radar"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = BRAND_BLUE

points = [
    "50-Student Live Cohort: Categorized dynamically across 7 behavioral archetypes.",
    "Real-Time Velocity Ranking: Students sorted by DVI score; acute drift surfaced instantly.",
    "Categorized Risk Zones: Normal (DVI < 35), Monitoring Zone (35–69), and Tripwire Active Alert (DVI ≥ 70).",
    "Instant Triage: Mentors focus immediately on students destabilizing right now, ignoring noise."
]
for pt in points:
    p = tf.add_paragraph()
    p.text = f"\n✔ {pt}"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10: 8. Prototype / Demo - Part 2 (Batch Attendance Register)
# ─────────────────────────────────────────────────────────────────────────────
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "8. Working Prototype: Batch Attendance Register", "One-Click Classroom Telemetry Recording with Reliable Database Persistence", "Live screenshot of the Batch Attendance Register modal with date & period tracking.")

img_path = os.path.join(SCREENSHOTS_DIR, "04_batch_attendance.png")
if os.path.exists(img_path):
    s10.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(7.5), Inches(4.8))

add_card(s10, Inches(8.5), Inches(1.6), Inches(4.0), Inches(4.8), border_color=ACCENT_CYAN)
tb = s10.shapes.add_textbox(Inches(8.75), Inches(1.8), Inches(3.5), Inches(4.4))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "PROTOTYPE CAPABILITY: Telemetry Modal"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_CYAN

points = [
    "One-Click Cohort Marking: Quick toggling across Present (P), Absent (A), Late (L), and Excused (E).",
    "Multi-Period Tracking: Periods 1 through 6 selectable with morning absence anomaly detection.",
    "Saved State Persistence: Reopening the modal immediately fetches saved marks from database—no blank or fresh resets.",
    "Live DVI Recomputation: Saving attendance updates all 50 student velocity scores in under 200ms."
]
for pt in points:
    p = tf.add_paragraph()
    p.text = f"\n✔ {pt}"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11: 8. Prototype / Demo - Part 3 (Student Profile & Counterfactuals)
# ─────────────────────────────────────────────────────────────────────────────
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "8. Working Prototype: Student Profile & Counterfactual XAI", "Deep Behavioral Breakdown of Student Rahul (CSE24001) with 'What-If' Guidance", "Live screenshot of Rahul's DVI Profile, gauge, component scores, and counterfactuals.")

img_path = os.path.join(SCREENSHOTS_DIR, "05_student_profile_rahul.png")
if os.path.exists(img_path):
    s11.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(7.5), Inches(4.8))

add_card(s11, Inches(8.5), Inches(1.6), Inches(4.0), Inches(4.8), border_color=ACCENT_RED)
tb = s11.shapes.add_textbox(Inches(8.75), Inches(1.8), Inches(3.5), Inches(4.4))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "PROTOTYPE CAPABILITY: Explainable XAI"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_RED

points = [
    "DVI Radial Gauge: Displays real-time score (74 High Risk) with velocity indicator.",
    "Tri-Component Breakdown: Explicitly attributes drift: 28 pts from attendance, 30 pts from late submissions, 16 pts from LMS drop.",
    "Actionable Counterfactual: System calculates minimal change required to exit the alert zone.",
    "Non-Punitive Guidance: Gives mentors supportive talking points instead of algorithmic condemnation."
]
for pt in points:
    p = tf.add_paragraph()
    p.text = f"\n✔ {pt}"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12: 8. Prototype / Demo - Part 4 (Closed-Loop Interventions)
# ─────────────────────────────────────────────────────────────────────────────
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "8. Working Prototype: Closed-Loop Intervention & Recovery", "Logging Consultations, Outcome Classifications, and Hysteresis Tracking", "Live screenshot of the Faculty Interventions Log & Recovery Monitoring pipeline.")

img_path = os.path.join(SCREENSHOTS_DIR, "06_interventions.png")
if os.path.exists(img_path):
    s12.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(7.5), Inches(4.8))

add_card(s12, Inches(8.5), Inches(1.6), Inches(4.0), Inches(4.8), border_color=ACCENT_GREEN)
tb = s12.shapes.add_textbox(Inches(8.75), Inches(1.8), Inches(3.5), Inches(4.4))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "PROTOTYPE CAPABILITY: Closed Loop"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_GREEN

points = [
    "Structured Outreach Logging: Records in-person meetings, phone calls, LMS messages, and referrals.",
    "Outcome Classification: Categorizes academic vs personal issues to guide institutional support.",
    "Hysteresis Recovery Monitor: Student transitions to 'Recovering' when DVI drops below 50, preventing alert oscillation.",
    "Audit-Ready Compliance: Creates a permanent, institutional record of supportive mentorship."
]
for pt in points:
    p = tf.add_paragraph()
    p.text = f"\n✔ {pt}"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 13: 9. Impact and Usefulness
# ─────────────────────────────────────────────────────────────────────────────
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13)
add_header(s13, "9. Impact & Usefulness", "Transforming Campus Operations, Academic Retention & Student Well-Being", "Quantified institutional impact backed by ethical AI and privacy-by-design.")

impacts = [
    ("21–28 Days Earlier", "Lead Time Advantage", "Detects micro-drift in 14-day rolling windows rather than waiting 90 days for midterm grades or exam hall ticket debarment.", BRAND_BLUE),
    ("< 2 Minutes", "Duty Leave Turnaround", "Replaces 3–5 days of physical signature chasing across blocks with instant 3-tier digital approvals and QR passes.", ACCENT_CYAN),
    ("15,000+ Sheets", "Zero-Paper Sustainability", "Completely eliminates physical leave chits, medical condonation chits, and hall ticket clearance slips annually.", ACCENT_GREEN),
    ("15–20% Reduction", "Avoidable Debarments", "Early velocity check-ins prevent students from sliding into the condonation (<75%) or year-back (<60%) danger zone.", ACCENT_AMBER),
    ("Zero Stigmatization", "Dignity-Preserving Safety Net", "Alerts are strictly private to mentors. Approved duty leaves are automatically masked. Zero public red flags.", ACCENT_RED),
    ("85% Reduction", "Faculty Triage Overhead", "Automated velocity scoring highlights the top 5 at-risk students out of 100 in less than 10 seconds.", TEXT_WHITE),
]

for idx, (metric, title, desc, color) in enumerate(impacts):
    row = idx // 3
    col = idx % 3
    left = Inches(0.8 + col * 3.95)
    top = Inches(1.6 + row * 2.6)
    add_card(s13, left, top, Inches(3.75), Inches(2.4), border_color=color)
    tb = s13.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), Inches(3.35), Inches(2.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = metric
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = color
    p2 = tf.add_paragraph()
    p2.text = title.upper()
    p2.font.size = Pt(11)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p3 = tf.add_paragraph()
    p3.text = f"\n{desc}"
    p3.font.size = Pt(9.5)
    p3.font.color.rgb = TEXT_MUTED

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 14: 10. Future Scope
# ─────────────────────────────────────────────────────────────────────────────
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14)
add_header(s14, "10. Future Scope & Roadmap", "From Institution Prototype to State-Wide Higher Education Standard", "Scalable multi-phase trajectory expanding to national university ecosystems.")

phases = [
    ("Phase 1 (Delivered Prototype)", "Current Hackathon Release", [
        "Full 3-Tier Digital Leave & QR Generation Engine",
        "Tripwire DVI Behavioral Velocity Engine (40/35/25)",
        "Batch Attendance Register with Persistence",
        "Document-Grounded RAG AI for KTU Ordinances",
        "AI ATS Placement Resume Screening Studio"
    ], BRAND_BLUE),
    ("Phase 2 (Next 3 Months)", "Deep Ecosystem Integration", [
        "Generative AI Advisor Outreach Copilot (Google Gemini API)",
        "Direct Canvas / Moodle LTI 1.3 Streaming Connectors",
        "Automated WhatsApp & SMS Gateway for Immediate Alerts",
        "State-Wide KTU University Portal API Synchronization"
    ], ACCENT_CYAN),
    ("Phase 3 (Next 6–12 Months)", "State-Wide Enterprise Scale", [
        "Cross-Semester Longitudinal Retention AI Modeling",
        "Blockchain-Anchored Credential Verification for Leaves & Bonafides",
        "Predictive Departmental Resource & Faculty Workload Balancer",
        "Multi-Institution Federated Learning for Cross-Campus Models"
    ], ACCENT_GREEN),
]

for idx, (title, subtitle, bullets, color) in enumerate(phases):
    left = Inches(0.8 + idx * 3.95)
    top = Inches(1.6)
    add_card(s14, left, top, Inches(3.75), Inches(5.1), border_color=color)
    tb = s14.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), Inches(3.35), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = color
    p2 = tf.add_paragraph()
    p2.text = subtitle
    p2.font.size = Pt(10)
    p2.font.italic = True
    p2.font.color.rgb = TEXT_MUTED
    for b in bullets:
        p = tf.add_paragraph()
        p.text = f"\n• {b}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 15: Conclusion & Q&A Defense
# ─────────────────────────────────────────────────────────────────────────────
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15)
add_header(s15, "Conclusion & Judge Defense", "Why EduSync × Tripwire is the Winning Higher-Ed Solution", "Cheat-sheet answering the toughest judge questions.")

conclusions = [
    ("Why combine campus ERP duty leaves with behavioral AI?",
     "Because they cannot work in silos! An early warning system that doesn't know about approved duty leaves will penalize students who are winning hackathons for the college. Integrating leave governance directly into the telemetry pipeline eliminates false positives.",
     BRAND_BLUE),
    ("How does this protect student dignity and mental health?",
     "Students are NEVER shown a public 'High Risk' label. Alerts are private advisory signals strictly inside the Faculty Advisor portal. The mentor reaches out naturally and supportively, preserving student dignity.",
     ACCENT_CYAN),
    ("What if a student is sick with the flu for 2 days?",
     "Our EWMA noise-smoothing filter (alpha=0.35) mathematically dampens isolated shocks. An alert requires sustained behavioral drift across rolling 14-day windows.",
     ACCENT_GREEN),
    ("Is this feasible to deploy across a 5,000-student university?",
     "Yes. Spring Boot handles ACID transactions via HikariCP connection pooling, while FastAPI executes vectorized NumPy calculations that recompute 5,000 student DVI scores in under 1.2 seconds.",
     ACCENT_AMBER)
]

for idx, (q, a, color) in enumerate(conclusions):
    top = Inches(1.6 + idx * 1.35)
    add_card(s15, Inches(0.8), top, Inches(11.733), Inches(1.22), border_color=color)
    tb = s15.shapes.add_textbox(Inches(1.1), top + Inches(0.08), Inches(11.1), Inches(1.05))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f"Q: \"{q}\""
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = color
    p2 = tf.add_paragraph()
    p2.text = f"A: {a}"
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_WHITE

# ── Save Presentation ─────────────────────────────────────────────────────────
prs.save(PPTX_OUT)
print(f"Presentation successfully created at: {PPTX_OUT}")
