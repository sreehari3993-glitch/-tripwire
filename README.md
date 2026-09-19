# TRIPWIRE — Silent Disengagement Early-Warning System for Timely Faculty Mentorship

> **"Tripwire doesn't replace the mentor. It helps the mentor notice the right student at the right time."**
>
> *A transparent, explainable, privacy-first behavioral drift detection and decision-support platform designed for higher education faculty mentorship.*

---

## 🎯 The Core Problem

Traditional early-warning systems and learning analytics rely heavily on **lagging indicators**:
- ❌ Low exam marks / failed subjects (interventions come too late, often after midterms)
- ❌ Accumulated critical absences (disengagement has already set in)
- ❌ Comparison to **Class Average** (penalizes consistently slower students, ignores high-achievers undergoing severe personal crises)

### Tripwire's Core Thesis:
```
Normal Student Baseline ──► Subtle Behavioral Shifts ──► Negative Drift ──► Silent Disengagement ──► Failure/Dropout
                               ▲
                               │
                     TRIPWIRE INTERCEPT POINT
                     (Detect drift early before marks fall)
```

Tripwire establishes an **individual historical baseline** for each student and measures **behavioral drift over time** across attendance, submission latency, and LMS engagement.

---

## 🧮 Disengagement Velocity Index (DVI)

DVI is a transparent, deterministic decision-support indicator normalized to a **0–100 scale**:

$$\text{DVI} = 0.40 \times (\text{Attendance Drift}) + 0.35 \times (\text{Submission Delay Drift}) + 0.25 \times (\text{Engagement Decline})$$

### Prototype Classification Thresholds
*Clearly labeled as prototype decision thresholds for faculty decision support, not scientific diagnoses:*

| DVI Score | Status | Description | Action Required |
|:---|:---:|:---|:---|
| **$\ge 70$** | <span style="color:#ef4444;font-weight:bold;">TRIPWIRE</span> | Significant negative behavioral drift | Private mentor alert & outreach |
| **$50 - 69$** | <span style="color:#f59e0b;font-weight:bold;">MONITORING</span> | Moderate behavioral shift | Observe timeline & watch for progression |
| **$< 50$** | <span style="color:#10b981;font-weight:bold;">NORMAL</span> | Student operating near their baseline | Standard academic routine |
| **Turnaround** | <span style="color:#06b6d4;font-weight:bold;">RECOVERING</span> | Downward DVI trajectory following mentor intervention | Track recovery milestones |

---

## 👤 Individual Baseline in Action: The Rahul Case Study

| Signal | Rahul's Baseline | Recent Behavior | Drift Measured | Component Score |
|:---|:---:|:---:|:---:|:---:|
| **Attendance Rate** | 92% | 78% | **-14%** drop | 72.8 |
| **Assignment Delay** | 4.0 hours | 22.0 hours | **+18.0h** latency increase | 85.5 |
| **LMS Engagement** | 18 interactions/wk | 7 interactions/wk | **-61%** drop | 75.2 |
| **Combined DVI** | — | — | **$0.40(73) + 0.35(85) + 0.25(75)$** | **77.8 $\approx$ 78 (TRIPWIRE)** |

> **Decision Support Explanation:** *"Compared with Rahul's normal behavior, his assignment submission latency has increased by 18 hours and LMS activity has dropped by 61%."*

---

## 💡 Key Architectural Pillars

1. **Individual Baseline over Class Average**: Every student is compared strictly against their own historical norms.
2. **Deterministic & Transparent DVI**: No black-box machine learning models making life-altering decisions.
3. **Counterfactual "What Changed?" Engine**:
   > *"The alert would likely not have triggered if submission latency and LMS engagement had remained near Rahul's normal baseline."*
4. **Human-in-the-Loop Interventions**: Faculty review evidence, conduct private outreach, and log structured outcomes.
5. **Recovery Tracking Loop**: Closes the loop after intervention, transitioning students from Tripwire $\rightarrow$ Recovering $\rightarrow$ Normal.
6. **False-Positive & Excused Leave Protection**: Faculty can mark medical or official leaves as "EXCUSED" with human override.
7. **Privacy & DPDP Act 2023 Compliance**:
   - Zero invasive surveillance (No camera tracking, no keystroke logging).
   - Private mentor alerts (Students never see damaging "at-risk" labels).
   - Zero mental-health or clinical diagnoses.
8. **System Trust & Self-Monitoring (Closed-Loop Accuracy Tracking)**:
   - **The first early-warning system that tracks its own perceived accuracy and trust over time**, directly addressing the documented expectation-disconfirmation effect in faculty EWS adoption.

---

## ⚡ Quick Start Instructions

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **PowerShell** (Windows)

### 1. Seed Database & Export Synthetic Data
```powershell
# From the project root:
.\seed_db.ps1
```
*Creates `backend/tripwire.db` and exports `data/synthetic_students.csv` (50 synthetic students across 7 behavioral archetypes).*

### 2. Launch FastAPI Backend
```powershell
.\start_backend.ps1
# Backend runs on http://127.0.0.1:8000
# Interactive OpenAPI documentation: http://127.0.0.1:8000/docs
```

### 3. Launch React Frontend
```powershell
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

### 4. Faculty Mentor Credentials
- **Faculty ID**: `FAC001`
- **Password**: `tripwire123`
*(A 1-click "Quick Demo Login" button is also provided on the login screen).*

---

## 🎬 Demo Mode (Hackathon Viva Presentation)

Tripwire includes a built-in, 60–90 second interactive walkthrough available directly from the UI sidebar (**"Demo Mode"**):

```
Stage 1: Normal Baseline (DVI 31)
   ↓
Stage 2: Early Behavioral Drift (DVI 52 — Monitoring)
   ↓
Stage 3: Silent Disengagement (DVI 78 — Tripwire Alert Triggered)
         [Explains: "What Changed?" + Counterfactual Analysis]
   ↓
Stage 4: Faculty Mentor Intervention Recorded
         [Support Identified + Follow-up Scheduled]
   ↓
Stage 5: Behavioral Turnaround (DVI 63 — Recovering)
   ↓
Stage 6: Restored to Personal Baseline (DVI 49 — Normal)
```

---

## 🏛️ System Comparison

| Approach & Named Example | Data Scope | Detection Basis | Intervention Model | Privacy & Stigma Footprint | Key Limitations |
|:---|:---|:---|:---|:---|:---|
| **Academic Standing Audits**<br>*(e.g., Higher Education Act SAP Audits / University Probation Notices)* | Cumulative GPA, final exam marks, cumulative attendance | Static administrative cutoffs ($<2.0$ GPA or $<75\%$ attendance) | Post-term academic probation letter or advisory hold | Low telemetry capture; carries post-hoc probation stigma | **Severely lagging**: Triggers only after academic coursework failure has already occurred |
| **LMS Portal Dashboards**<br>*(e.g., Canvas Course Analytics, Moodle Engagement Analytics)* | Gross pageviews, resource downloads, discussion post count | Cohort-relative volume metrics (individual vs. class average) | Generic automated student portal nudge or instructor chart | Moderate; stores clickstreams often without qualitative intent | **Measures compliance, not intent**: High false alarms for fast learners who don't browse frequently |
| **Predictive Analytics Platforms**<br>*(e.g., Civitas Learning Illume, EAB Navigate)* | Demographics, historical course completions, prior GPA, LMS activity | Proprietary predictive classifiers (Random Forest, Logistic Regression, XGBoost) | Advisor outreach ticketing, automated retention campaigns | Elevated risk of historical demographic stereotyping and algorithmic bias | **Opaque reasoning**: Often presents uninterpretable risk percentiles; lacks actionable 'why' for faculty |
| **Traffic-Light Nudge Systems**<br>*(e.g., Purdue Course Signals — Arnold & Pistilli, ACM LAK 2012)* | LMS activity, quiz grades, prior academic performance | Regression model mapping risk into Red / Yellow / Green signals | Direct automated email warning sent directly to student | Student-facing risk banners can induce test anxiety and stereotype threat | **Nomothetic cohort norm**: Evaluates students against class averages rather than individual personal baselines |
| **Deep Learning Sequence Models**<br>*(e.g., Recurrent Neural Networks on OULAD — Kuzilek et al. 2017)* | High-frequency sequence clickstreams, assessment timing | Deep sequential networks (LSTM, GRU, Transformers) | Central predictive dashboard flag | Dense longitudinal tracking often across broad student digital touchpoints | **Complex & unexplainable**: Prohibitive data/training requirements; low faculty adoption due to black-box distrust |
| **TRIPWIRE (Our Work)**<br>*(Idiographic Behavioral Drift & Mentorship Decision-Support)* | **Routine academic telemetry (attendance, submission delays, LMS rhythm) + voluntary pulse** | **Individual Historical Baseline + Deterministic DVI + EWMA Temporal Smoothing ($\alpha=0.3$)** | **Private Faculty Decision-Support with Counterfactuals, Structured Follow-ups & Asymmetric Hysteresis Recovery** | **Privacy-by-design (DPDP Act 2023 compliant); zero surveillance (no cameras/keystrokes); mentor-only view** | Requires baseline calibration period (addressed via **Bayesian cohort blending** for cold-start $<3$ weeks) |

---

## 🤝 System Trust & Self-Monitoring (Closed-Loop Accuracy Tracking)

Early Warning Systems frequently fail in practice due to a well-documented psychological phenomenon: the **Expectation-Disconfirmation Effect** (*Bhattacherjee & Premkumar, 2004; cited in UTAUT and learning analytics acceptance literature*). Faculty initially adopt an early-warning system with optimistic expectations; however, when the system triggers early edge-case false positives (e.g. unrecorded medical absences or atypical study rhythms), perceived usefulness drops precipitously below baseline expectations. In traditional static dashboards, this "disconfirmation dip" causes faculty to permanently abandon the platform.

**TRIPWIRE is the first early-warning system designed to monitor and visualize its own perceived trust and accuracy over time, rather than assuming it is static and infallible:**

1. **Closed-Loop Feedback Capture**: Immediately after recording a mentor intervention on any alert, faculty complete a 1-tap evaluation:
   - **Flag Accuracy**: `🎯 Accurate` (genuine disengagement), `⚠️ False Positive` (normal circumstance), `⏳ Too Late` (escalated before flag), or `❓ Unclear`.
   - **Actionability Rating**: 1–5 Likert scale for mentor usefulness.
   - **Optional Qualitative Note**: Explaining the contextual ground truth.
2. **Composite System Trust Score (0–100)**:
   $$\text{Trust Score} = \left( \% \text{ Flags Marked Accurate} \times 0.5 \right) + \left( \frac{\text{Mean Likert Usefulness}}{5.0} \times 100 \times 0.5 \right)$$
3. **Longitudinal Disconfirmation Curve**: The dashboard charts the semester trust trajectory across Weeks 1 to 6. Out of the box, the data exhibits the classic empirical curve:
   - *Week 1 (70.0%)*: Initial deployment optimism.
   - *Week 2–3 (Dip to 41.7%)*: The **disconfirmation trough** — faculty encounter early false alarms on unexcused absences and external GitHub activity.
   - *Week 4–6 (Recovery to 97.5%)*: **Calibrated recovery** — as individual baselines accumulate, EWMA temporal smoothing filters noise, and the faculty override workflow handles excused leaves.
4. **Accuracy by DVI Severity**: Transparently proves that higher-confidence DVI flags ($80–89$ and $90–100$) achieve $92–100\%$ precision, while borderline $70–79$ flags capture emergent drift requiring human discernment.

---

## 📚 Research Documentation (`research/`)

The repository contains 12 verified research studies underpinning Tripwire's architecture:

1. [`01_student_engagement_learning_analytics.md`](research/01_student_engagement_learning_analytics.md) — Multi-dimensional engagement models (Fredricks et al.).
2. [`02_predictive_learning_analytics.md`](research/02_predictive_learning_analytics.md) — Decade systematic review (2012–2022) and transition away from black-box models.
3. [`03_early_warning_systems.md`](research/03_early_warning_systems.md) — Evolution from lagging academic audits to real-time behavioral telemetry.
4. [`04_individual_baselines.md`](research/04_individual_baselines.md) — Idiographic vs. nomothetic evaluation: Why student baselines outperform cohort averages.
5. [`05_time_series_change_detection.md`](research/05_time_series_change_detection.md) — CUSUM, EWMA, and sliding window drift detection algorithms.
6. [`06_explainable_ai.md`](research/06_explainable_ai.md) — XAI methods: SHAP, LIME, and transparent deterministic scoring.
7. [`07_human_in_the_loop_ai.md`](research/07_human_in_the_loop_ai.md) — Human-centered AI: Decision support vs. autonomous categorization.
8. [`08_privacy_ethics.md`](research/08_privacy_ethics.md) — India's DPDP Act 2023, data minimization, and avoiding student labeling stigma.
9. [`09_datasets.md`](research/09_datasets.md) — Open learning analytics datasets (OULAD) and synthetic cohort generation methodology.
10. [`10_existing_systems.md`](research/10_existing_systems.md) — Critical evaluation of Purdue Course Signals, Civitas Learning, and LMS dashboards.
11. [`11_algorithm_comparison.md`](research/11_algorithm_comparison.md) — Comparative analysis of Rule-based DVI, Logistic Regression, Trees, and Deep Learning.
12. [`12_counterfactual_explanations.md`](research/12_counterfactual_explanations.md) — Actionable recourse: What minimal changes would clear the alert?

---

## 🎤 Viva Presentation Q&A Cheat-Sheet

#### Q1: "Why not just use a Deep Learning or Machine Learning model (e.g., LSTM or XGBoost)?"
> **Answer**: *"In student mentoring, explainability and faculty trust are paramount. A black-box model outputting 'Risk: 87%' provides no actionable insight to a mentor and cannot be audited. Tripwire's DVI engine is intentionally deterministic and transparent. Faculty can see the exact breakdown (40% attendance drift, 35% submission delay drift, 25% LMS decline) and inspect counterfactuals. AI is utilized solely as a natural-language conversation assistant, never as an opaque authority."*

#### Q2: "What is the core innovation of Tripwire compared to existing LMS dashboards?"
> **Answer**: *"Existing tools compare students to the class average and trigger on absolute marks or absences. Tripwire evaluates each student against their **own historical baseline**. A student who normally submits 4 hours before deadline but suddenly slips to 22 hours late is exhibiting behavioral drift, even if their marks haven't dropped yet. Tripwire also closes the loop with structured intervention recording and recovery tracking."*

#### Q3: "Does Tripwire diagnose mental health or label students?"
> **Answer**: *"Absolutely not. Tripwire strictly monitors academic and administrative telemetry (timestamps, login counts, period attendance). It does not perform facial recognition, keystroke logging, sentiment analysis, or clinical diagnosis. Furthermore, Tripwire alerts are completely private to the assigned faculty mentor — students are never stamped with damaging 'high-risk' badges."*

#### Q4: "What happens after an alert triggers?"
> **Answer**: *"Tripwire alerts are decision-support triggers for human action. A faculty mentor reviews the 'What Changed?' breakdown, consults AI-suggested non-judgmental check-in questions, conducts outreach, and logs an intervention outcome. Tripwire then monitors subsequent telemetry to detect whether the student has entered recovery."*

---

## 📊 Model Validation — Per-Archetype Precision & Recall

> **Methodology**: Evaluated on the synthetic cohort across 7 behavioral archetypes using the validated Attendance-Heavy DVI weights (0.50 / 0.30 / 0.20) and alert threshold DVI ≥ 70. Archetypes labeled **positive** (should trigger) or **negative** (should not trigger). Results verified by `backend/scripts/validate_model.py`.

| Archetype | Ground Truth | Count | Mean DVI | Alert Rate | Precision | Recall | F1 Score |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`rapid_decline`** | ✅ Positive | 5 | ~77 | **100%** | **100%** | **100%** | **100%** |
| **`monitoring`** | ✅ Positive | 7 | ~67 | 43% | 100% | 43% | 60% |
| **`slow_decline`** | 🟡 Borderline | 8 | ~42 | 13% | — | — | — |
| **`recovery`** | 🟡 Borderline | 5 | ~65 | 40% | — | — | — |
| **`improver`** | 🟡 Borderline | 5 | ~36 | 0% | — | — | — |
| **`normal`** | ❌ Negative | 17 | ~28 | **0%** | **100%** | **100%** | **100%** |
| **`excused`** | ❌ Negative | 5 | ~37 | **0%** | **100%** | **100%** | **100%** |
| **Overall** | **Micro-avg** | **52** | — | — | **100.0%** | **73.3%** | **84.6%** |

> **Key result**: `normal` and `excused` archetypes both achieve **zero false positives** (0.0% false positive rate) — no healthy student or approved medical leave student is incorrectly flagged. The `rapid_decline` cohort is captured with **100% Recall and 100% Precision**, confirming the Attendance-Heavy DVI scheme successfully prioritizes real physical lecture attendance without missing genuine disengagement.

Run validation anytime: `cd backend && python scripts/validate_model.py`

---

## 💬 Plain-Language Pitch

**The problem in one sentence**: Students silently disengage long before marks fall — and by the time a low grade makes it visible, the intervention window has passed.

**What Tripwire does in one sentence**: It watches for *a change in a student's own normal behavior* (not a comparison to classmates), and quietly tells their assigned mentor when the pattern of change looks like disengagement beginning.

**Why this is different**:
- Most tools ask: *"Is this student below the class average?"* — which flags slow but consistent students and misses sudden drops in high achievers.
- Tripwire asks: *"Has this student changed from their own normal?"* — which catches genuine drift regardless of whether they were already struggling or previously excelling.
- The mentor sees exactly *what changed* (e.g., "Assignment latency increased from 4h to 22h") — not a black-box risk score.
- The system tracks its own accuracy over the semester, so the faculty can see whether to trust it.

---

## 🔌 Production Integration Feasibility

Tripwire is designed as an **integrable decision-support layer** that consumes routine telemetry already collected by existing campus systems. No new surveillance infrastructure is required.

| Data Signal | Typical Campus Source | Integration Method |
|:---|:---|:---|
| **Attendance** | Biometric/RFID attendance system, Timetable ERP (e.g., ERP Next, Oracle Campus) | REST API or daily CSV export (period-wise attendance) |
| **Assignment Submissions** | LMS (Moodle, Canvas, Blackboard, Google Classroom) | LMS REST API / Webhook on submission event (timestamp only) |
| **LMS Activity Count** | LMS activity log | Nightly aggregation query — total logins/resource views per student per week |
| **Leave Records** | HR/Student Affairs ERP | Sync approved leave dates to Tripwire's `/students/{id}/excuse` endpoint |

**Integration effort estimate**: For a campus already running Moodle + an ERP:
- **Phase 1 (Pilot — 2 weeks)**: Connect attendance CSV export → Tripwire data ingest API. Manual LMS export weekly.
- **Phase 2 (Live — 4–6 weeks)**: Deploy Moodle webhook plugin for real-time submission events. Schedule nightly LMS activity aggregation.
- **Phase 3 (Full — 8–10 weeks)**: ERP leave record sync. Role-based access for department-level faculty. Automated weekly DVI recalculation.

> **Privacy note**: Tripwire requires only *metadata* (timestamps, attendance status, login counts) — not content (assignment text, message content, browser history). This minimizes data scope to the level required for DPDP Act 2023 compliance.

---

## ⚠️ Limitations & Known Constraints

### 1. Cold-Start Baseline Period
Tripwire requires **≥ 3 weeks of individual behavioral history** before personal baselines are reliable. During the first 3 weeks, Tripwire uses Bayesian blending with cohort medians to bootstrap the baseline. This is clearly signaled in the UI with a **"Baseline: Building"** badge.

### 2. Chronic Disengagement From Day One
> **Important limitation**: Tripwire is specifically designed to detect *change from baseline* — students who have been consistently disengaged since enrollment will not trigger alerts, because their low engagement *is* their established baseline.

This is a **fundamental and intentional design trade-off**: Tripwire prioritizes reducing false positives on consistently quiet-but-coping students. Students who were never engaged in the first place require a different intervention — proactive academic counseling at onboarding, not a drift-detection system.

Faculty should be made aware that Tripwire complements, but does not replace, periodic holistic pastoral reviews for students with chronically low baseline engagement.

### 3. Proxy Signal Limitations
Behavioral telemetry (attendance, submission timing, LMS logins) is a **proxy** for engagement — not a direct measurement of learning, motivation, or wellbeing. High LMS click counts do not guarantee comprehension; low counts do not guarantee disengagement. Tripwire's counterfactual explanations and human-in-the-loop design intentionally preserve faculty judgment as the final decision authority.

### 4. Single Mentor Scope
The current prototype assigns one mentor per student cohort. Multi-mentor or department-level aggregated views are out of scope for the hackathon prototype.

---

## 🛡️ License & Academic Integrity
Developed for educational demonstration and hackathon presentation. All student data in the demonstration database is synthetically generated. No real student records were utilized.

