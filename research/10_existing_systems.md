# Research Topic: Comparative Evaluation of Existing Learning Analytics & Early-Warning Systems

## Why it Matters to Tripwire
To communicate the novelty of Tripwire during a competitive hackathon presentation and viva defense, it is essential to objectively contextualize how existing commercial, institutional, and research systems operate—and precisely where their limitations lie.

Tripwire does not claim to invent educational analytics. Rather, its competitive differentiation stems from the synergistic synthesis of **individual behavioral baselines**, **transparent multi-signal drift velocity (DVI)**, **counterfactual explanations**, **human override safeguards**, and **closed-loop recovery tracking**.

---

## Key Concepts to Investigate
1. **Traditional Academic Warning Systems**:
   - Institutional legacy processes where faculty submit midterm deficiency reports for students with failing grades ($<40\%$) or excessive cumulative unexcused absences.
   - *Failure Mode*: Operates entirely on lagging indicators after irrecoverable academic deficit has already set in.

2. **Standard LMS Analytics Dashboards (Canvas, Moodle, Blackboard)**:
   - Provide raw descriptive charts (page views, total minutes online, assignment submissions).
   - *Failure Mode*: Overwhelms instructors with uncontextualized charts; compares students to class averages; fails to highlight behavioral velocity or suggest empathetic outreach.

3. **Predictive Learning Analytics Platforms (e.g., Civitas Learning, Ellucian CRM Advance)**:
   - Utilize machine learning on institutional SIS and historical data to output persistent dropout/retention probabilities.
   - *Failure Mode*: Opaque black-box models; heavy weighting of static demographic attributes; lack of granular behavioral explanations for why a score changed this week.

4. **Purdue Course Signals**:
   - Landmark traffic light (Red/Yellow/Green) alert platform.
   - *Failure Mode*: Broadcast alerts directly to students (risk of stigma); static thresholds; lack of individual baseline customization.

---

## Systematic Comparison Matrix

| System / Approach | Telemetry Data | Prediction Paradigm | Intervention Workflow | Privacy & Stigma | Primary Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Traditional Academic Warning** | Midterm exam marks, aggregate attendance count | None (threshold rule on summative failure) | Disciplinary email or academic probation notice | Public/Formal academic record; high stigma | Triggered far too late (Weeks 8–10); purely punitive |
| **Standard LMS Analytics** | Clickstreams, pageviews, forum counts | None (purely descriptive dashboards) | None (passive instructor viewing) | Visible on faculty dashboards; unstandardized | Information overload without actionable signals; click-counting |
| **Predictive Analytics (Civitas, etc.)** | SIS records, demographics, historical GPA, LMS | Opaque ML (Random Forest, Neural Nets) | Automated student email or advisor alert | Moderate; risk of demographic/prejudice profiling | Opaque "Black Box" predictions; static bias; low faculty trust |
| **Purdue Course Signals** | Preparation, demographics, effort, grades | Regression / Threshold traffic light | Direct student traffic light notification | Direct red/yellow lights visible to student; potential stigma | Population-normed; lacks within-subject baseline; stigmatizing |
| **Modern Research EWS (2025–2026)** | Multimodal LMS + sensor/activity logs | Deep Sequential models (LSTM, GRU, Transformers) | Automated nudges or advisor ticketing | Varies; often high surveillance (cameras/keystrokes) | High deployment complexity; severe trust and explainability deficit |
| **TRIPWIRE (Our Approach)** | Non-invasive administrative logs: Attendance, Assignment latency, LMS frequency | **Transparent Disengagement Velocity Index (DVI)** | **Closed-loop faculty mentorship with recovery tracking** | **Zero surveillance; private mentor-only alerts; human override** | Prototype threshold requires institutional calibration |

---

## Relevant Literature & Citations
- **Key Reference**: *"Comparing Early Warning Systems in Higher Education: Architecture, Adoption, and Ethics"* (Siemens et al., 2021).
  - Categorizes the five generations of EWS and identifies the fifth generation as explainable, human-centered decision support.
- **Key Reference**: *"Course Signals at Purdue: Ten Years Later"* (2022).
  - Reflects on the lessons learned regarding student-facing vs. advisor-facing alerts.

---

## Relevant Search Terms
- `comparative study early warning systems higher education`
- `purdue course signals vs modern learning analytics`
- `commercial learning analytics platforms comparison`
- `actionable vs descriptive learning analytics dashboards`
- `closed loop intervention tracking educational analytics`

---

## How It Influences Tripwire's Implementation
1. **Comparison Matrix in UI**: A dedicated "System Comparison" modal in the frontend dashboard allows judges to view this rigorous comparison directly during demo.
2. **Clear Viva Articulation**: Establishes concise answers for why Tripwire is uniquely positioned as an explainable, non-invasive decision-support tool.
