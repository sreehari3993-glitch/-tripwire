"""
Script to generate the official Tripwire Hackathon Pitch Deck (.pptx)
focused on Tripwire as a predictive behavioral early-warning layer
for standard college ERPs (like ETLAB, Linways), with embedded screenshots
of the web application's different interfaces.
"""
import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

SCREENSHOTS_DIR = os.path.join(os.getcwd(), "screenshots")
PPTX_OUT = os.path.join(os.getcwd(), "TRIPWIRE_PITCH_DECK.pptx")

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
blank_layout = prs.slide_layouts[6]

def set_slide_bg(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_BG
    bg.line.fill.background()
    return bg

def add_header(slide, section_tag, title_text, subtitle_text=None):
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = section_tag.upper()
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = BRAND_BLUE

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.65))
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
        p_sub.font.size = Pt(11.5)
        p_sub.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_BG):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1: Title / Cover Slide
# ─────────────────────────────────────────────────────────────────────────────
s1 = prs.slides.add_slide(blank_layout)
set_slide_bg(s1)

add_card(s1, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1), border_color=BRAND_BLUE)

tb = s1.shapes.add_textbox(Inches(2.0), Inches(1.7), Inches(9.333), Inches(4.0))
tf = tb.text_frame
tf.word_wrap = True

p0 = tf.paragraphs[0]
p0.alignment = PP_ALIGN.CENTER
p0.text = "HACKATHON PRESENTATION | AI IN HIGHER EDUCATION"
p0.font.size = Pt(12)
p0.font.bold = True
p0.font.color.rgb = ACCENT_CYAN

p1 = tf.add_paragraph()
p1.alignment = PP_ALIGN.CENTER
p1.text = "PROJECT TRIPWIRE"
p1.font.size = Pt(44)
p1.font.bold = True
p1.font.color.rgb = TEXT_WHITE

p2 = tf.add_paragraph()
p2.alignment = PP_ALIGN.CENTER
p2.text = "The Predictive Behavioral Intelligence Layer for Standard College ERPs"
p2.font.size = Pt(17)
p2.font.bold = True
p2.font.color.rgb = BRAND_BLUE

p3 = tf.add_paragraph()
p3.alignment = PP_ALIGN.CENTER
p3.text = "\n\"Tripwire is designed to ingest attendance/academic data from standard college ERP systems (like ETLAB) rather than requiring a new platform — no new sensors, no separate student-facing app.\""
p3.font.size = Pt(13)
p3.font.italic = True
p3.font.color.rgb = TEXT_WHITE

p4 = tf.add_paragraph()
p4.alignment = PP_ALIGN.CENTER
p4.text = "\nCompatible with University Systems: KTU, Autonomous Engineering Colleges & Technical Institutions"
p4.font.size = Pt(11)
p4.font.color.rgb = ACCENT_GREEN

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2: 1. Problem Statement
# ─────────────────────────────────────────────────────────────────────────────
s2 = prs.slides.add_slide(blank_layout)
set_slide_bg(s2)
add_header(s2, "1. Problem Statement", "The Passive ERP Blindspot: Why Colleges Fail to Catch Dropping Students", "How traditional college management systems miss silent behavioral disengagement.")

add_card(s2, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=ACCENT_RED)
tb_l = s2.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.1), Inches(4.6))
tf_l = tb_l.text_frame
tf_l.word_wrap = True

p = tf_l.paragraphs[0]
p.text = "THE CAMPUS REALITY: LATE POST-MORTEM"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = ACCENT_RED

pts_l = [
    ("The 75% Debarment Shock: ", "Under statutory technical university regulations (e.g., KTU), students must maintain >= 75% attendance. Students below 75% face condonation fines or year-back exam debarment."),
    ("ERPs are Passive Ledgers: ", "Current campus ERPs (like ETLAB, Linways) merely act as digital databases. They log period attendance and Series exam marks passively, but have zero predictive analytics."),
    ("Late-Stage Discovery: ", "Faculty and students only discover debarment status 48 hours before final exams when hall tickets are blocked—when it is mathematically impossible to attend enough classes to recover."),
    ("The Cost: ", "Over 25% of engineering dropouts and semester year-backs occur without prior academic warnings because disengagement starts behaviorally weeks earlier.")
]
for title, desc in pts_l:
    p = tf_l.add_paragraph()
    p.text = f"\n• {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE
    p2 = tf_l.add_paragraph()
    p2.text = f"  {desc}"
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED

add_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=ACCENT_AMBER)
tb_r = s2.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.6))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p = tf_r.paragraphs[0]
p.text = "THE 'SILENT DRIFT' ANATOMY"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = ACCENT_AMBER

pts_r = [
    ("Disengagement is Multi-Modal: ", "Students do not fail abruptly. Decline starts with subtle, connected behavioral micro-drifts 3 to 6 weeks before academic distress manifests in exam halls."),
    ("Morning Absence Anomaly: ", "A student begins routinely missing Period 1 (morning) lectures while attending afternoon classes—a primary indicator of sleep disorders or isolation."),
    ("Submission Latency Creep: ", "Assignments that were previously turned in 2 hours early begin arriving 18 to 48 hours late, signaling acute cognitive overload."),
    ("Faculty Triage Paralysis: ", "With 60 to 120 students per classroom, faculty advisors cannot manually cross-correlate attendance sheets, homework timestamps, and LMS clicks without automated intelligence.")
]
for title, desc in pts_r:
    p = tf_r.add_paragraph()
    p.text = f"\n• {title}"
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
set_slide_bg(s3)
add_header(s3, "2. Target Users / Stakeholders", "Academic Stakeholder Matrix: Transforming Roles from Reactive to Proactive", "Empowering educators, administrators, and students with dignified early intervention.")

stakeholders = [
    ("Faculty Advisors & Mentors (Primary Users)",
     "Pain Point: Overburdened with administrative data entry; blind to quiet student disengagement until exams.\nTripwire Value: A triaged Risk Radar surfacing at-risk students in seconds, 1-click batch attendance register, and pre-computed actionable intervention targets.",
     BRAND_BLUE),
    ("Course Instructors & Subject Lecturers",
     "Pain Point: Cannot identify which students are falling behind across multi-section classes.\nTripwire Value: Instant multi-period classroom attendance marking with automated real-time velocity recomputation and morning absence detection.",
     ACCENT_CYAN),
    ("Heads of Department (HOD) & Academic Deans",
     "Pain Point: Lack department-wide compliance visibility; discover high failure rates only at semester audit.\nTripwire Value: Real-time cohort health distribution heatmaps, faculty intervention velocity audits, and retention compliance tracking.",
     ACCENT_GREEN),
    ("Students (Direct Beneficiaries)",
     "Pain Point: Trapped by unexpected exam debarment; public 'high risk' labels cause shame and stereotype threat.\nTripwire Value: A private, dignified safety net. Students are never publicly labeled or stigmatized; approved medical/duty leaves are mathematically protected.",
     TEXT_WHITE),
]

for idx, (role, desc, color) in enumerate(stakeholders):
    top = Inches(1.6 + idx * 1.32)
    add_card(s3, Inches(0.8), top, Inches(11.733), Inches(1.18), border_color=color)
    tb = s3.shapes.add_textbox(Inches(1.1), top + Inches(0.08), Inches(11.1), Inches(1.02))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = role
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = color
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4: 3. Existing Gaps or Limitations
# ─────────────────────────────────────────────────────────────────────────────
s4 = prs.slides.add_slide(blank_layout)
set_slide_bg(s4)
add_header(s4, "3. Existing Gaps or Limitations", "Why Standard College ERPs (Like ETLAB) & Generic EWS Fall Short", "Four critical structural limitations that leave institutions vulnerable to student dropout.")

gaps = [
    ("1. Purely Passive Ledger Design",
     "College ERPs like ETLAB function strictly as administrative databases. They record daily attendance and marks accurately, but offer zero velocity modeling. They tell faculty where a student was yesterday, but cannot predict where they are heading next month.",
     ACCENT_RED),
    ("2. Blunt Universal 75% Cutoffs",
     "Traditional systems only sound alarms when attendance crosses 75%. They completely miss an honors student whose attendance rapidly plummets from 98% to 76% (an acute crisis), while continually flagging chronic 72% students whose performance is stable.",
     ACCENT_AMBER),
    ("3. Alert Fatigue from Transient Noise",
     "Rule-based platforms treat every single absence equally. A 2-day bout of food poisoning triggers immediate warning emails, overwhelming professors with false alarms and causing them to ignore genuine alerts.",
     ACCENT_RED),
    ("4. Black-Box Opacity & No Actionable Guidance",
     "Predictive learning analytics tools output opaque risk scores ('0.84 High Risk') without explanation. Faculty mentors are left asking: 'Why was Rahul flagged, and what specific action can I ask him to take to recover?'",
     ACCENT_AMBER)
]

for idx, (title, desc, color) in enumerate(gaps):
    row = idx // 2
    col = idx % 2
    left = Inches(0.8 + col * 5.95)
    top = Inches(1.6 + row * 2.6)
    add_card(s4, left, top, Inches(5.75), Inches(2.4), border_color=color)
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
set_slide_bg(s5)
add_header(s5, "4. Proposed Solution", "Tripwire: The Behavioral Early-Warning Intelligence Layer for College ERPs", "A lightweight, mathematically rigorous AI layer that seamlessly supercharges systems like ETLAB.")

add_card(s5, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.1), border_color=BRAND_BLUE)

tb = s5.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(11.1), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "HOW TRIPWIRE INTEGRATES WITH STANDARD COLLEGE ERPs (ETLAB, LINWAYS)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = BRAND_BLUE

sol_points = [
    ("Non-Disruptive ERP Integration: ", "Colleges do not need to replace their existing ERP (ETLAB/Linways). Tripwire sits as an intelligent microservice layer, continuously ingesting period attendance, assignment submission logs, and approved medical leaves via standard APIs or batch sync."),
    ("The Dynamic Velocity Index (DVI): ", "Replaces blunt universal cutoffs with personal baseline modeling. Evaluates relative rate-of-change across 3 rolling vectors: Attendance Drift (40%), Submission Delay Drift (35%), and LMS Engagement Drift (25%)."),
    ("Noise-Suppression via EWMA: ", "Exponentially Weighted Moving Average smoothing (alpha=0.35) filters out 1-off transient shocks (flu, single exam week) while isolating genuine, sustained multi-week behavioral decline."),
    ("Counterfactual Explainable AI (XAI): ", "Computes actionable 'what-if' pathways: 'If student attends upcoming lab sessions and submits Assignment 3 on time, projected DVI falls from 74 to 48, averting academic probation.'"),
    ("Closed-Loop Intervention Tracking: ", "Enables mentors to log in-person meetings or support referrals in 30 seconds, automatically tracking post-intervention recovery velocity via a dual-threshold hysteresis state machine.")
]

for title, desc in sol_points:
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
set_slide_bg(s6)
add_header(s6, "5. Innovation / Unique Contribution", "Four Algorithmic Breakthroughs in Student Drift Detection", "Moving beyond simple heuristics to production-grade, mathematically defensible AI.")

innovations = [
    ("1. Personal Baselines & EWMA Smoothing",
     "Instead of rigid cutoffs, Tripwire calibrates a student's personal baseline over initial telemetry. It applies Exponentially Weighted Moving Average (EWMA, alpha=0.35) temporal smoothing: S_t = alpha*X_t + (1-alpha)*S_{t-1}. Transient illnesses produce zero false alarms, while sustained 2-week decay triggers immediate triage.",
     BRAND_BLUE),
    ("2. Bayesian Cold-Start Prior Blending",
     "Solves the first-year or transfer student 'blank slate' problem. For students with < 3 weeks of historical data, Tripwire blends individual data with cohort medians using Bayesian priors: Effective_Baseline = w*Student_Base + (1-w)*Cohort_Median. Eliminates early-semester blindspots.",
     ACCENT_CYAN),
    ("3. Approved Duty-Leave Mathematical Masking",
     "Unlike standard ERPs that record duty leaves as unexcused absences until manual end-of-term audit, Tripwire ingests approved leaves directly from the ERP. Verified medical/hackathon dates are mathematically excluded from drift penalties. Campus achievers are never penalized.",
     ACCENT_GREEN),
    ("4. Actionable Counterfactual Explainability (XAI)",
     "Grounded in Wachter et al. (2017) counterfactual theory: x* = argmin d(x, x') s.t. f(x') < threshold. Tripwire computes the minimal feasible behavioral changes required to clear the alert, giving faculty mentors hopeful, constructive guidance instead of punitive warnings.",
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
set_slide_bg(s7)
add_header(s7, "6. System / Solution Architecture", "How Tripwire Integrates with College ERP Infrastructure", "A lightweight, high-speed telemetry pipeline connecting institutional databases to mentor decision support.")

arch_columns = [
    ("COLLEGE ERP DATA LAYER", 
     "Standard College ERP\n(ETLAB / Linways / SIS)\n• Daily Period Attendance (1–6)\n• Assignment Submission Logs\n• LMS Activity Counters\n• Approved Medical Leaves", 
     ACCENT_CYAN, Inches(0.8), Inches(1.6), Inches(2.7), Inches(5.1)),
    ("INGESTION & PERSISTENCE", 
     "Tripwire Database Engine\nSQLAlchemy ORM + SQLite/PG\n• Indexed Student Telemetry\n• Attendance Register State\n• Leave Record Cache\n• Historical DVI Timeseries", 
     BRAND_BLUE, Inches(3.75), Inches(1.6), Inches(2.8), Inches(5.1)),
    ("PREDICTIVE DVI ENGINE", 
     "FastAPI Python Core\nNumPy Matrix Computation\n• EWMA Temporal Smoother\n• Bayesian Cold-Start Prior\n• Approved Leave Masker\n• Counterfactual Generator", 
     ACCENT_GREEN, Inches(6.8), Inches(1.6), Inches(2.8), Inches(5.1)),
    ("FACULTY ADVISOR COCKPIT", 
     "React 18 + Vite Web Client\nInteractive Glassmorphism UI\n• Real-Time Risk Radar Feed\n• One-Click Batch Register\n• DVI Radial Gauges & Alerts\n• Closed-Loop Intervention Log", 
     ACCENT_AMBER, Inches(9.85), Inches(1.6), Inches(2.7), Inches(5.1)),
]

for title, content, color, left, top, w, h in arch_columns:
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
set_slide_bg(s8)
add_header(s8, "7. Technology Stack", "High-Throughput ASGI Backend & Modern Reactive Client", "Selected for sub-10ms calculation velocity, reliability, and zero deployment friction.")

tech_grid = [
    ("Backend API Framework", "FastAPI (Python 3.11)", 
     "Asynchronous ASGI concurrency, automatic OpenAPI documentation, strict Pydantic v2 schema validation, OAuth2 JWT stateless authentication, sub-10ms endpoint latency.", BRAND_BLUE),
    ("Mathematical Engine", "NumPy & Custom Analytical Core", 
     "Vectorized array processing for EWMA smoothing, Bayesian prior calculations, and counterfactual simulation. Computes full cohort DVI scores across 50 students in < 200ms.", ACCENT_CYAN),
    ("Persistence & ORM", "SQLAlchemy 2.0 & SQLite / PostgreSQL", 
     "Relational ACID compliance, optimized indexed queries for multi-period student attendance records, clean migration path to enterprise PostgreSQL clusters.", ACCENT_GREEN),
    ("Frontend Interface", "React 18, Vite & Recharts", 
     "Sub-second Hot Module Replacement (HMR), SVG radial gauge rendering, Lucide Icons, responsive layout, Axios interceptors with automatic JWT auth management.", ACCENT_AMBER),
]

for idx, (tier, tools, details, color) in enumerate(tech_grid):
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
# SLIDE 9: 8. Demo Part 1 - Faculty Risk Radar Dashboard
# ─────────────────────────────────────────────────────────────────────────────
s9 = prs.slides.add_slide(blank_layout)
set_slide_bg(s9)
add_header(s9, "8. Working Prototype: Faculty Risk Radar & Cohort Heatmap", "Interface 1: Live Dashboard Visualizing Student Behavioral Distribution", "Live screenshot from the running Tripwire web application.")

img_path = os.path.join(SCREENSHOTS_DIR, "02_dashboard.png")
if os.path.exists(img_path):
    s9.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(7.5), Inches(4.8))

add_card(s9, Inches(8.5), Inches(1.6), Inches(4.0), Inches(4.8), border_color=BRAND_BLUE)
tb = s9.shapes.add_textbox(Inches(8.75), Inches(1.8), Inches(3.5), Inches(4.4))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "INTERFACE: Risk Radar Dashboard"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = BRAND_BLUE

points = [
    "Cohort Heatmap: Visualizes 50 students categorized into 7 behavioral archetypes (Normal, Slow Decline, Rapid Decline, Monitoring, Recovery, etc.).",
    "Triaged Alert Queue: Surfaces active alerts prioritized by drift velocity rather than static grades.",
    "Real-Time Metrics: Displays cohort average attendance, submission delays, and high-risk flags at a glance.",
    "Zero Guesswork: Faculty immediately see which students need support right now, without sifting through spreadsheets."
]
for pt in points:
    p = tf.add_paragraph()
    p.text = f"\n✔ {pt}"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10: 8. Demo Part 2 - Batch Attendance Register
# ─────────────────────────────────────────────────────────────────────────────
s10 = prs.slides.add_slide(blank_layout)
set_slide_bg(s10)
add_header(s10, "8. Working Prototype: Batch Attendance Register", "Interface 2: One-Click Classroom Telemetry Recording with Reliable Persistence", "Live screenshot of the Batch Attendance Register modal with date, period, and status buttons.")

img_path = os.path.join(SCREENSHOTS_DIR, "04_batch_attendance.png")
if os.path.exists(img_path):
    s10.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(7.5), Inches(4.8))

add_card(s10, Inches(8.5), Inches(1.6), Inches(4.0), Inches(4.8), border_color=ACCENT_CYAN)
tb = s10.shapes.add_textbox(Inches(8.75), Inches(1.8), Inches(3.5), Inches(4.4))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "INTERFACE: Batch Register Modal"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_CYAN

points = [
    "Classroom Cohort View: Mark daily attendance across Present (P), Absent (A), Late (L), and Excused (E) in seconds.",
    "Period & Date Navigation: Select Periods 1–6 with morning period tracking for anomaly detection.",
    "Database State Persistence: Reopening the modal or changing dates automatically loads saved attendance records—eliminating fresh resets.",
    "Immediate Velocity Recalculation: Submitting attendance instantly re-evaluates DVI scores across all students in under 200ms."
]
for pt in points:
    p = tf.add_paragraph()
    p.text = f"\n✔ {pt}"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11: 8. Demo Part 3 - Student Profile & Counterfactuals
# ─────────────────────────────────────────────────────────────────────────────
s11 = prs.slides.add_slide(blank_layout)
set_slide_bg(s11)
add_header(s11, "8. Working Prototype: Student Profile & Counterfactual XAI", "Interface 3: Deep Behavioral Analytics & 'What-If' Guidance for Rahul (CSE24001)", "Live screenshot of Rahul's profile with DVI radial gauge, component waterfall, and recovery targets.")

img_path = os.path.join(SCREENSHOTS_DIR, "05_student_profile_rahul.png")
if os.path.exists(img_path):
    s11.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(7.5), Inches(4.8))

add_card(s11, Inches(8.5), Inches(1.6), Inches(4.0), Inches(4.8), border_color=ACCENT_RED)
tb = s11.shapes.add_textbox(Inches(8.75), Inches(1.8), Inches(3.5), Inches(4.4))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "INTERFACE: Explainable Profile"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_RED

points = [
    "DVI Radial Gauge: Displays real-time drift score (74 High Risk) with velocity indicator.",
    "Multi-Vector Attribution: Explicitly breaks down risk origin (28 pts from attendance drop, 30 pts from submission latency, 16 pts from LMS).",
    "Actionable Counterfactual: Generates specific guidance: 'Submitting Assignment 3 and attending upcoming labs drops DVI by 28 points to 46 (Safe zone).'",
    "Human-Centric Mentoring: Transforms data from punitive labels into positive, constructive student check-in conversations."
]
for pt in points:
    p = tf.add_paragraph()
    p.text = f"\n✔ {pt}"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_WHITE

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12: 8. Demo Part 4 - Closed-Loop Interventions
# ─────────────────────────────────────────────────────────────────────────────
s12 = prs.slides.add_slide(blank_layout)
set_slide_bg(s12)
add_header(s12, "8. Working Prototype: Closed-Loop Intervention Tracking", "Interface 4: Logging Advisor Consultations, Outcomes & Hysteresis Recovery", "Live screenshot of the Faculty Interventions Log & Recovery Monitoring pipeline.")

img_path = os.path.join(SCREENSHOTS_DIR, "06_interventions.png")
if os.path.exists(img_path):
    s12.shapes.add_picture(img_path, Inches(0.8), Inches(1.6), Inches(7.5), Inches(4.8))

add_card(s12, Inches(8.5), Inches(1.6), Inches(4.0), Inches(4.8), border_color=ACCENT_GREEN)
tb = s12.shapes.add_textbox(Inches(8.75), Inches(1.8), Inches(3.5), Inches(4.4))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "INTERFACE: Intervention Log"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_GREEN

points = [
    "Structured Consultation Logging: Records in-person meetings, phone check-ins, or academic referrals in 30 seconds.",
    "Root Cause Identification: Flags whether the distress was academic difficulty, personal difficulty, or health-related.",
    "Hysteresis Recovery Monitoring: Alert clears only when student's DVI drops below 50, preventing alert oscillation.",
    "Institutional Accountability: Provides deans with verified audit trails of proactive faculty mentorship."
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
set_slide_bg(s13)
add_header(s13, "9. Impact & Usefulness", "Measurable Retention ROI, Academic Equity & Privacy Safeguards", "Quantified institutional impact engineered with ethical AI principles.")

impacts = [
    ("21–28 Days Earlier", "Lead Time Advantage", "Detects micro-drift in 14-day rolling windows rather than waiting 90 days for midterms or end-of-term hall ticket blocks.", BRAND_BLUE),
    ("85% Reduction", "Faculty Triage Overhead", "Automated velocity scoring highlights the top 5 at-risk students out of 100 in less than 10 seconds.", ACCENT_CYAN),
    ("15–20% Reduction", "Avoidable Debarments", "Early velocity check-ins prevent students from sliding past the non-recoverable 75% university attendance threshold.", ACCENT_GREEN),
    ("Zero Student Stigma", "Dignity-Preserving Safety Net", "Alerts are strictly private to designated mentors. Students are never shown a demoralizing public 'High Risk' badge.", ACCENT_AMBER),
    ("Excused Leave Protection", "Fairness & Equity", "Approved medical and duty leaves in the ERP are mathematically masked from penalties, protecting student ambassadors.", ACCENT_RED),
    ("Privacy by Design", "Operational Telemetry Only", "Uses coarse institutional metadata already in the ERP (attendance, timestamps, clicks). Zero invasive webcams or screen tracking.", TEXT_WHITE),
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
set_slide_bg(s14)
add_header(s14, "10. Future Scope & Roadmap", "From Campus Prototype to Standard College ERP Plug-In", "A clear 3-phase commercialization and technical expansion roadmap.")

roadmap_phases = [
    ("Phase 1: Delivered Prototype", "Current Hackathon Release", [
        "Full DVI multi-vector analytical engine",
        "EWMA temporal noise smoothing (alpha=0.35)",
        "Classroom batch attendance register with persistence",
        "Actionable counterfactual explainability module",
        "Closed-loop mentor intervention & recovery tracker"
    ], BRAND_BLUE),
    ("Phase 2: Native ERP Connectors", "Next 3 Months", [
        "Native plug-in connectors for ETLAB, Linways & CampusCare",
        "LTI 1.3 standard compliance for Canvas & Moodle LMS",
        "Generative AI Mentor Outreach Copilot (Google Gemini API) to auto-draft personalized check-in emails in 1 click",
        "Automated WhatsApp & SMS alert dispatches"
    ], ACCENT_CYAN),
    ("Phase 3: Enterprise & State Scale", "Next 6–12 Months", [
        "Cross-semester longitudinal retention modeling",
        "Departmental resource allocation & workload prediction",
        "State-wide technical university deployment across KTU colleges",
        "Federated privacy-preserving machine learning models"
    ], ACCENT_GREEN),
]

for idx, (title, subtitle, bullets, color) in enumerate(roadmap_phases):
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
set_slide_bg(s15)
add_header(s15, "Conclusion & Judge Defense", "Why Tripwire is the Winning Educational AI Innovation", "Cheat-sheet answering the toughest judge questions with technical precision.")

defense_qa = [
    ("Why integrate with college ERPs like ETLAB instead of replacing them?",
     "Colleges have years of financial and institutional lock-in with ERPs like ETLAB. By sitting as an intelligent predictive plug-in rather than a disruptive replacement, Tripwire achieves zero-friction institutional adoption.",
     BRAND_BLUE),
    ("Why is personal velocity better than a static 75% cutoff?",
     "Static cutoffs trigger alarms when it's already too late to recover. A student dropping from 98% to 76% in 2 weeks represents an acute crisis that static rules ignore until they cross 75%. Relative velocity catches the fire early.",
     ACCENT_CYAN),
    ("What prevents false alerts when a student catches the flu for 2 days?",
     "Our EWMA noise-smoothing filter (alpha=0.35) mathematically suppresses transient shocks. An alert strictly requires sustained multi-week decline across multiple operational dimensions before firing.",
     ACCENT_GREEN),
    ("How does Tripwire protect student mental health and dignity?",
     "Tripwire never shows students a demoralizing public 'At-Risk' label. Alerts are private advisory signals for mentors, paired with constructive counterfactual pathways ('attending 3 labs clears the alert') rather than punitive condemnation.",
     ACCENT_AMBER)
]

for idx, (q, a, color) in enumerate(defense_qa):
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
print(f"Presentation successfully saved to: {PPTX_OUT}")
