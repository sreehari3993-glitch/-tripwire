# Research Topic: Predictive Learning Analytics (PLA) in Higher Education

## Why it Matters to Tripwire
Predictive Learning Analytics (PLA) leverages machine learning and statistical modeling to identify students at risk of academic failure or course dropout. However, a major critique of conventional PLA is that models operate as opaque predictive black boxes that emphasize probability scores (e.g., "78% risk of course failure") rather than actionable operational levers.

For Tripwire, evaluating the past decade of PLA literature reveals why simple, transparent drift detection coupled with decision support outperforms complex, opaque dropout models in actual institutional deployments.

---

## Key Concepts to Investigate
1. **Predictive Analytics vs. Decision Support**:
   - Predictive models aim for statistical accuracy ($AUC$, $F_1$-score) at predicting an end-of-semester outcome.
   - Decision support systems focus on *timeliness*, *interpretability*, and *intervention efficacy* during the semester while the trajectory can still be altered.

2. **Common Input Features in PLA**:
   - Demographics / Prior academic performance (GPA, high school percentiles).
   - In-course behaviors (LMS logins, forum posts, quiz attempts).
   - Temporal features (weekly cadence, recency of login, latency to complete tasks).

3. **The "Too Late to Intervene" Paradox**:
   - Many predictive models achieve high predictive accuracy late in the term (Week 10–12) when grade variance is already wide, but faculty intervention at that stage yields minimal salvage value.
   - True early-warning systems must function effectively in Weeks 3–6.

---

## Relevant Literature & Citations
- **Key Reference**: *"Recent advances in Predictive Learning Analytics: A decade systematic review (2012–2022)"*.
  - Reviews over 100 PLA implementations across institutions worldwide.
  - Documents recurring deficiencies: heavy reliance on historical static features (prior GPA) which biases against non-traditional students; low faculty adoption due to lack of explainability; lack of closed-loop post-intervention evaluation.
- **Key Reference**: *"Machine Learning and Deep Learning for Dropout Prediction in Higher Education: A Review"* (2026).
  - Analyzes the transition from Logistic Regression and Decision Trees to Deep Neural Networks (LSTMs, GRUs, Transformers).
  - Concludes that while Deep Learning captures complex sequential dependencies, it suffers from a "trust deficit" among educators who cannot explain *why* the model flagged a particular student.

---

## Relevant Search Terms
- `predictive learning analytics systematic review 2012 2022`
- `dropout prediction higher education machine learning deep learning review`
- `actionable learning analytics intervention timing`
- `explainable predictive modeling student retention`
- `early warning intervention window higher education`

---

## How It Influences Tripwire's Implementation
1. **Prioritizing Actionable Levers over Static Attributes**: Tripwire explicitly excludes static demographic and prior socio-economic variables from its risk engine to eliminate structural bias.
2. **Transparent Scoring**: Rather than generating a mysterious probability score, Tripwire calculates the transparent Disengagement Velocity Index (DVI), where each point is directly traced to attendance, submission delay, or LMS activity.
3. **Early Window Detection**: Tripwire evaluates 14-day rolling windows relative to an early-term baseline, flagging shifts during Weeks 2–6 before irreversible grade deficits accumulate.

---

## Limitations & Open Questions to Verify
- **Label Definition**: What constitutes "true at-risk"? Is it binary course failure, or is it suboptimal engagement that hinders deeper conceptual mastery?
- **Intervention Fatigue**: If alerts trigger too frequently for minor variations, faculty may experience alert fatigue. Calibrating prototype thresholds (e.g., DVI $\ge 70$) is critical.
