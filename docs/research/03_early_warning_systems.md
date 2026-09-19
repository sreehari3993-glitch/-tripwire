# Research Topic: Early-Warning Systems (EWS) in Higher Education

## Why it Matters to Tripwire
Early-Warning Systems (EWS) are institutional mechanisms engineered to detect indicators of academic distress before they culminate in failure or withdrawal. The lineage of EWS extends from simple rule-based flaggers in the early 2000s to modern algorithmic platforms.

Studying landmark systems—such as **Purdue Course Signals** and subsequent institutional iterations—provides critical operational lessons regarding alert design, stakeholder communication, and the risk of stigmatization.

---

## Key Concepts to Investigate
1. **Purdue Course Signals (Purdue University, Arnold & Pistilli)**:
   - One of the pioneering higher-ed learning analytics deployments.
   - Utilized a predictive algorithm combining student preparation, LMS interaction, academic performance, and demographics to generate a traffic-light indicator (Red, Yellow, Green).
   - Showed positive correlation with retention, but later independent evaluations raised questions about self-selection bias and student communication methods.

2. **Traffic-Light Paradigms vs. Behavioral Velocity**:
   - Classic EWS models categorize students into static risk buckets (Red / Yellow / Green).
   - Tripwire extends this by computing *velocity* ($\frac{d}{dt}\text{Behavior}$) rather than static risk state, distinguishing between a student with stable low performance and a student rapidly destabilizing from an exemplary baseline.

3. **Communication Channels and Stigma**:
   - Systems that broadcast "At-Risk" or "Red Alert" notifications directly to students often induce stereotype threat, learned helplessness, or acute academic anxiety.
   - Best practices emphasize routing early behavioral signals privately to faculty mentors or advisors who can initiate personal, supportive outreach.

---

## Relevant Literature & Citations
- **Key Reference**: *"A Real-Time Early Warning Intervention System for At-Risk Students Using Predictive Modeling and Academic Engagement Metrics"* (2026).
  - Emphasizes real-time feedback loops between behavioral sensor streams and student advising workflows.
  - Demonstrates that the median time-to-contact from alert generation is the single highest predictor of intervention success.
- **Key Reference**: *"Course Signals at Purdue: Using Learning Analytics to Increase Student Success"* (Arnold & Pistilli, 2012).
  - Seminal work establishing the viability of automated early warnings derived from LMS telemetry.
- **Critical Retrospective**: *"Student success system: Why Purdue Course Signals worked and why it raised questions"* (Essalmi et al., 2020).
  - Warns against opaque predictive algorithms and highlights the necessity of faculty involvement in the decision loop.

---

## Relevant Search Terms
- `early warning systems higher education learning analytics`
- `purdue course signals implementation review`
- `student retention early warning intervention models`
- `traffic light early warning higher education critique`
- `academic advising early alert behavioral telemetry`

---

## How It Influences Tripwire's Implementation
1. **Private Mentor Alerts**: Tripwire alerts are strictly private to designated faculty mentors (`FAC001`). Students are never confronted with automated "HIGH RISK" labels.
2. **Behavioral Velocity Framing**: The DVI metric captures the *rate of change* over rolling 14-day and 7-day windows, surfacing destabilization before absolute grade boundaries are crossed.
3. **Closing the Intervention Loop**: Tripwire does not end at alert generation; it requires recording the mentor intervention and initiates a continuous recovery tracking monitor.

---

## Limitations & Open Questions to Verify
- **Advisor Bandwidth**: In large classes (100+ students per faculty), alert volume must be regulated so mentors are not overloaded.
- **Actionability**: An alert without contextual evidence leaves mentors guessing; Tripwire must explicitly show the "What Changed?" panel alongside suggested talking points.
