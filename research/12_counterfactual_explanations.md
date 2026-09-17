# Research Topic: Counterfactual Explanations in Educational Decision Support

## Why it Matters to Tripwire
Explaining *why* an alert occurred is only half the battle. To empower faculty mentors and advisors, a decision-support system should also answer: **"What would need to change for this student to no longer trigger the alert?"**

This is the domain of **counterfactual explanations**. In learning analytics, counterfactual reasoning shifts the paradigm from deterministic condemnation ("Student is high risk") to actionable, hopeful intervention pathways ("If assignment submission latency returns to baseline, the alert threshold would clear").

---

## Key Concepts to Investigate
1. **Definition of Counterfactual Explanation (Wachter et al., 2017)**:
   - A counterfactual explanation describes the minimal change to input features that would change the model's decision from the adverse outcome (TRIPWIRE) to the desired outcome (NORMAL/MONITORING):
     $$\mathbf{x}^* = \arg\min_{\mathbf{x}'} d(\mathbf{x}, \mathbf{x}') \quad \text{s.t.} \quad f(\mathbf{x}') = y^*$$
   - Where $\mathbf{x}$ is the student's current behavioral state, $\mathbf{x}^*$ is the counterfactual state, $d(\cdot)$ is a distance function (e.g., Manhattan distance normalized by median absolute deviation), and $y^*$ is the sub-threshold state.

2. **Actionability and Feasibility**:
   - In contrast to immutable static features (e.g., prior high school GPA or demographic background, which can never be altered by the student), behavioral signals in Tripwire are inherently **actionable**:
     - Submission latency can be reduced.
     - LMS logins can be resumed.
     - Attendance in upcoming sessions can be restored.
   - Counterfactual statements must only perturb actionable behavioral levers.

3. **Explanatory vs. Causal Disclaimers**:
   - A counterfactual calculation demonstrates how the algorithm's scoring function responds to hypothetical inputs; it does *not* constitute a guaranteed medical or psychological causal proof.
   - Tripwire must explicitly disclaim:
     *"Explanatory / Counterfactual Analysis — not a guaranteed causal statement."*

---

## Example Counterfactual Formulation in Tripwire
For student **Rahul** with current metrics:
- Attendance: $78\%$ (Baseline: $92\%$, Drift Contribution: $28.0\text{ pts}$)
- Submission Delay: $22\text{ hrs}$ (Baseline: $4\text{ hrs}$, Drift Contribution: $29.8\text{ pts}$)
- LMS Activity: $7/\text{wk}$ (Baseline: $18/\text{wk}$, Drift Contribution: $18.8\text{ pts}$)
- Total DVI: $76.6 \approx 77$ (Threshold $\ge 70 \rightarrow \text{TRIPWIRE}$)

**Counterfactual Computation**:
1. If Submission Delay returned to baseline ($4\text{ hrs}$), Submission Drift contribution drops from $29.8$ to $0$.
   - New DVI: $76.6 - 29.8 = 46.8$ (Below the Monitoring threshold of 50 $\rightarrow$ **NORMAL**).
2. If LMS Activity returned to baseline ($18/\text{wk}$), LMS Drift contribution drops from $18.8$ to $0$.
   - New DVI: $76.6 - 18.8 = 57.8$ (Leaves student in **MONITORING**, clearing TRIPWIRE).

**Generated Explanation**:
> *"The Tripwire alert would likely not have triggered if assignment submission latency and LMS activity had remained near Rahul's normal historical baseline."*

---

## Relevant Literature & Citations
- **Key Reference**: *"Counterfactual Explanations Without Opening the Black Box: Automated Decisions and the GDPR"* (Wachter, Mittelstadt, & Russell, 2017).
  - Foundational legal and technical formulation establishing counterfactuals as the premier ethical vehicle for actionable consumer and citizen recourse.
- **Key Reference**: *"Actionable Recourse in Learning Analytics: Guiding Students Toward Success with Counterfactual Recommendations"* (2024).
  - Demonstrates that providing advisors with counterfactual intervention targets improves the clarity and efficacy of student advising sessions.

---

## Relevant Search Terms
- `counterfactual explanations machine learning learning analytics`
- `Wachter Mittelstadt counterfactual explanations recourse`
- `actionable recourse educational decision support`
- `what if analysis learning analytics dashboards`
- `counterfactual vs SHAP feature attribution education`

---

## How It Influences Tripwire's Implementation
1. **Interactive Counterfactual Panel**: The student profile and alert inspection views feature a prominent "What Changed & Counterfactual Analysis" card.
2. **Dynamic "What If" Computation**: The backend calculates the counterfactual impact of restoring each single signal to baseline, ranking which behavioral recovery would most effectively lower the DVI.
3. **Transparent Disclaimer**: Clearly labels the analysis as decision-support reasoning rather than determinism.

---

## Limitations & Open Questions to Verify
- **Past Cannot Be Undone**: Past missed classes cannot retroactively be attended. Counterfactuals must be framed forward-looking: *"If attendance across the next two weeks returns to normal..."*
