# Research Topic: Explainable AI (XAI) in Educational Early-Warning Systems

## Why it Matters to Tripwire
In educational decision-support systems, a model's prediction is useless if faculty mentors do not understand *why* it was made. If an automated system merely asserts "Student CSE24001 is at High Risk (Score: 0.82)", mentors cannot determine whether the underlying cause is attendance, missed coursework, lack of online study, or an algorithmic glitch.

Tripwire separates the deterministic, transparent calculation engine (the DVI) from the AI explanation layer. Every alert is accompanied by an itemized attribution of components and an explainable narrative.

---

## Key Concepts to Investigate
1. **Intrinsically Interpretable Models vs. Post-Hoc Explanations**:
   - *Intrinsically Interpretable*: Linear models, weighted scorecards (e.g., DVI), shallow decision trees, where every decision path and coefficient is visible.
   - *Post-Hoc Explanations*: Model-agnostic explainability methods (SHAP - Shapley Additive exPlanations, LIME - Local Interpretable Model-agnostic Explanations) applied to black-box models (Neural Networks, Gradient Boosted Trees).
   *Tripwire's primary detection engine is intrinsically interpretable by design, obviating the need to approximate decision boundaries with surrogate methods.*

2. **Feature Attribution & Contribution Decomposition**:
   - In Tripwire, total DVI is decomposed into exact additive contributions:
     $$\text{DVI} = \text{Att\_Score} \times 0.40 + \text{Sub\_Score} \times 0.35 + \text{Eng\_Score} \times 0.25$$
   - A score of 77 is clearly presented as $28.0 + 29.8 + 18.8 = 76.6 \approx 77$.

3. **Natural Language Explanations as a Bridge**:
   - Faculty members are busy educators, not data scientists. Translating numerical deviations into concise, respectful, non-judgmental prose bridges the cognitive gap between raw metrics and a human conversation.

---

## Relevant Literature & Citations
- **Key Reference**: *"Explainable AI in Education (XAI-ED): A Review of Applications and Future Directions"* (Khosravi et al., 2022).
  - Outlines the ethical necessity of explainability when algorithmic outputs affect learner trajectories.
  - Warns that instructors reject black-box educational predictions unless supported by clear, evidence-based feature attribution.
- **Key Reference**: *"Addressing the Black-Box Problem in Learning Analytics: A Study of Instructor Trust and Intervention Behavior"* (2024).
  - Finds that instructor willingness to reach out to students increases by over 60% when explanations clearly highlight specific behavioral shifts rather than probabilistic risk tiers.

---

## Relevant Search Terms
- `explainable AI in education learning analytics review`
- `feature attribution student early warning decision support`
- `SHAP LIME learning analytics interpretability`
- `instructor trust educational decision support systems`
- `transparent scoring models vs black box predictive models`

---

## How It Influences Tripwire's Implementation
1. **"What Changed?" Card**: The student profile and alert pages feature a dedicated "What Changed?" section that breaks down baseline vs. current values and percentage changes.
2. **Visual Contribution Bars**: Each of the 3 core signals displays its raw score (0–100), weighting factor (40%, 35%, 25%), and exact point contribution to the final DVI.
3. **AI Explanatory Layer**: Generative AI (Google Gemini) is utilized strictly as an explanatory translator—turning verified metric deltas into non-stigmatizing talking points and suggested questions for the mentor.

---

## Limitations & Open Questions to Verify
- **Hallucination Safeguards**: Generative AI layers must be strictly bound by prompts to never speculate on unmeasured attributes (mental health, domestic life, cognitive ability).
- **Rule-Based Fallback**: If an external LLM API is unavailable, the system must retain a 100% deterministic rule-based template explanation generator.
