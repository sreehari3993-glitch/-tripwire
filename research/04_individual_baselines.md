# Research Topic: Individual Behavioral Baselines vs. Class Averages

## Why it Matters to Tripwire
The single most distinctive algorithmic innovation of Tripwire is its rejection of population-level normative grading (class averages) as the reference point for early warning detection.

In standard systems, a student whose attendance drops from 95% to 80% is still labeled "Normal" because the class average is 75%. Conversely, a student whose historical attendance has always hovered around 72% but who consistently excels on projects might be perpetually flagged as "At-Risk". By establishing an **individual behavioral baseline** for each student, Tripwire detects personal negative drift regardless of where the class median lies.

---

## Key Concepts to Investigate
1. **Within-Subject vs. Between-Subject Change Detection**:
   - *Between-Subject (Normative)*: Compares student $i$ against cohort mean $\mu_{\text{class}}$ and standard deviation $\sigma_{\text{class}}$. Fails to detect personalized declines in high achievers; creates false alarms for steady low-intensity participants.
   - *Within-Subject (Idiographic)*: Compares student $i$'s current window $t$ against their own baseline period $T_{\text{base}}$:
     $$\Delta \text{Behavior}_i(t) = \text{Behavior}_i(t) - \text{Baseline}_i$$

2. **The "Quietly Sinking High-Achiever" Problem**:
   - High-performing students who experience severe emotional distress or burnout often drop substantially before falling below generic class alert thresholds.
   - Individual baseline analysis flags a drop from 95% to 80% attendance and a 20-hour delay increase as an acute warning, granting mentors early intervention opportunities.

3. **Baseline Calibration Window (Cold-Start Problem)**:
   - Defining the duration needed to establish a stable behavioral fingerprint (e.g., initial 3–4 weeks of term, or previous semester records).
   - Managing transitional variance during the initial baseline formation phase.

---

## Relevant Literature & Citations
- **Key Reference**: *"Personalized Learning Analytics: From Norm-Referenced Dashboards to Self-Referenced Progress Indicators"* (2023).
  - Demonstrates that students and advisors respond significantly better to self-referenced progress comparisons than peer-normed rankings, reducing competitive anxiety and surfacing genuine behavioral drift.
- **Key Reference**: *"Within-Person Behavioral Variability in Digital Learning Environments"* (Baker et al., 2021).
  - Establishes that variance from personal behavioral norms correlates strongly with cognitive friction, procrastination, and eventual drop-off.

---

## Relevant Search Terms
- `within-subject change detection learning analytics`
- `idiographic vs nomothetic models student retention`
- `personalized baseline behavioral drift higher education`
- `self-referenced learning analytics indicators`
- `cold start baseline calibration student telemetry`

---

## How It Influences Tripwire's Implementation
1. **Personalized Feature Extraction**: For each student, August 1–31 data is compiled to calculate individual baseline parameters:
   - Baseline Attendance % ($\text{Base}_{\text{att}}$)
   - Baseline Submission Delay Hours ($\text{Base}_{\text{sub}}$)
   - Baseline LMS Weekly Activity count ($\text{Base}_{\text{lms}}$)
   - Baseline Morning Absences ($\text{Base}_{\text{morn}}$)
2. **Relative Drift Normalization**: All drift metrics calculate percentage departure from the student's *own* baseline:
   $$\text{Drift}_{\text{att}} = \max\left(0, \frac{\text{Base}_{\text{att}} - \text{Current}_{\text{att}}}{\text{Base}_{\text{att}}}\right) \times 100$$
3. **Dashboard Narrative**: Every view explicitly frames data as *"Compared with Rahul's normal behavior..."* rather than *"Rahul is below class average"*.

---

## Limitations & Open Questions to Verify
- **Students with Low Baselines**: If a student enters the institution already disengaged during the baseline window, their baseline may reflect sub-par performance. Tripwire must combine relative drift with absolute safety floors for minimum statutory compliance (e.g., mandatory 75% university attendance regulations).
- **Temporal Baseline Drift**: Baselines may naturally shift across exam weeks or holidays; systems should distinguish between global cohort shocks (e.g., festival week) and isolated student drift.
