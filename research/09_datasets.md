# Research Topic: Datasets in Learning Analytics and Synthetic Trajectory Modeling

## Why it Matters to Tripwire
Developing an effective prototype early-warning system requires high-fidelity time-series telemetry that reflects realistic academic workflows. While benchmark educational datasets exist, they rarely contain the exact combination of synchronous attendance, granular assignment submission latency, and daily LMS interaction counts mapped across distinct behavioral archetypes.

For Tripwire, synthesizing a mathematically grounded, 50-student time-series dataset allows us to rigorously simulate diverse trajectories (Normal, Improving, Slow Decline, Rapid Decline, Excused Leave, Recovered) without risking real student privacy.

---

## Key Concepts to Investigate
1. **Existing Benchmark Educational Datasets**:
   - **Open University Learning Analytics Dataset (OULAD)**:
     - Comprehensive public dataset containing student demographics, course modules, assessment scores, and daily VLE (Virtual Learning Environment) clickstream logs for 32,593 students.
     - *Limitation*: Captures distance learning with minimal synchronous class attendance data.
   - **Kaggle Higher Education Students Performance Dataset**:
     - Tabular survey data focused on static socio-demographic features; lacks time-series event resolution.
   - **ASSISTments & Canvas LMS Traces**:
     - Excellent micro-interaction logs, but sparse in terms of faculty mentor intervention recording and post-intervention recovery tracking.

2. **Synthetic Trajectory Generation Architecture**:
   - Creating synthetic cohorts requires realistic probabilistic distributions:
     - **Baseline Period (Month 1 - August)**: All students exhibit authentic, stable behaviors centered around personalized means ($\mu_{\text{att}} \sim \mathcal{U}(85, 95)\%$, $\mu_{\text{sub}} \sim \mathcal{U}(2, 8)\text{ hrs}$, $\mu_{\text{lms}} \sim \mathcal{U}(6, 12)/\text{wk}$).
     - **Active Monitoring Window (Month 2 - September)**: Controlled trajectory divergence across 6 distinct behavioral archetypes.

3. **Archetype Definitions**:
   1. *Consistent Normal*: Attendance $\sim 90\%$, sub delay $\le 6$ hrs, steady LMS activity.
   2. *Gradual Improver*: Starts low, progressively tightens submission times and improves attendance.
   3. *Slow Decline*: Subtle negative slope across multiple weeks, hovering in monitoring territory ($50 \le \text{DVI} < 70$).
   4. *Rapid Decline (Demo Archetype - Rahul)*: Sharp deterioration over 10 days; missed morning periods, compounding assignment delay ($42+$ hrs), collapsed LMS logins. Crosses $\text{DVI} \ge 70$.
   5. *Excused Leave*: Apparent attendance drop during Sep 3–8, but verified as medical leave; DVI calculation overrides unexcused penalty.
   6. *Recovered After Intervention*: Exhibits high initial DVI, triggers intervention record, and subsequently recovers baseline metrics ($DVI: 78 \rightarrow 63 \rightarrow 49$).

---

## Relevant Literature & Citations
- **Key Reference**: *"The Open University Learning Analytics Dataset (OULAD)"* (Kuzilek, Hlosta, & Zdrahal, 2017).
  - Benchmark standard for VLE clickstream and assessment timing telemetry.
- **Key Reference**: *"Generative Modeling of Synthetic Learner Behavior for Validating Educational Recommender Systems"* (2023).
  - Validates the utility of synthetic agent-based behavioral generation in testing early warning algorithms prior to live institutional trials.

---

## Relevant Search Terms
- `open university learning analytics dataset OULAD review`
- `synthetic student behavior time series generation`
- `educational data mining benchmark datasets`
- `simulating student dropout trajectories learning analytics`
- `realistic assignment submission latency distributions`

---

## How It Influences Tripwire's Implementation
1. **Dual-Phase Calendar**: Data structured with an August baseline period (31 calendar days) and a September monitoring period (15 calendar days).
2. **Deterministic Reproducibility**: Fixed random seed (`random.seed(42)`) ensures consistent, reproducible demonstration conditions for hackathon viva presentations.
3. **Data Export**: Exportable synthetic CSV (`data/synthetic_students.csv`) providing transparent inspection for judges.

---

## Limitations & Open Questions to Verify
- **Real-World Noise**: Synthetic datasets have smooth Gaussian noise; real classroom data features missing attendance scans, proxy swipes, and server downtime. The DVI engine must handle nulls and missing records gracefully.
