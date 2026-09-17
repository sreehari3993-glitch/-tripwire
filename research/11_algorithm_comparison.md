# Research Topic: Algorithmic Architecture Trade-Offs in Student Disengagement Detection

## Why it Matters to Tripwire
A common pitfall in computer science hackathons is deploying complex, opaque deep-learning architectures (e.g., LSTMs, Transformers) to problems where transparent, rule-based or linear formulations yield superior explainability, lower operational complexity, and higher institutional trust.

This document presents a structured decision framework comparing algorithmic candidates across Explainability, Computational Complexity, Data Requirements, and Overall Suitability for Tripwire's core mission: early, actionable decision support for faculty mentors.

---

## Model Evaluation Matrix

| Model Family | Explainability | Computational Complexity | Data Requirement | Cold-Start Tolerance | Tripwire Suitability | Rationale & Trade-Offs |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Transparent Weighted DVI (Tripwire Prototype)** | **Very High** (Exact mathematical decomposition) | **Very Low** ($\mathcal{O}(N)$ arithmetic) | **Minimal** (14-day history + baseline) | **High** (Needs only baseline window) | **Very High (Chosen Engine)** | Fully transparent; zero black-box obscurity; easily verifiable by faculty; mathematically grounded in behavioral drift. |
| **Logistic Regression** | **High** (Direct odds ratios / feature weights) | **Low** ($\mathcal{O}(d \cdot N)$) | **Moderate** (Requires labeled historical training data) | **Moderate** | **High** | Highly explainable linear decision boundary; standard baseline in educational data mining. |
| **Decision Trees (CART / C4.5)** | **Very High** (Explicit if-then decision paths) | **Low** ($\mathcal{O}(N \cdot d \log N)$) | **Moderate** | **Moderate** | **High** | Intuitive visual branching, but can be unstable and prone to overfitting small cohort variations. |
| **Random Forest** | **Medium** (Ensemble of trees; requires SHAP/TreeSHAP) | **Medium** ($\mathcal{O}(M \cdot N \log N)$) | **High** (Needs multi-term institutional datasets) | **Low** | **High (Secondary)** | Strong predictive accuracy, handles non-linear interactions; requires secondary post-hoc XAI layer. |
| **Gradient Boosting (XGBoost / LightGBM)** | **Medium** (Requires SHAP values for local attribution) | **Medium** | **High** | **Low** | **High (Secondary)** | State-of-the-art for tabular tabular data; highly effective if multi-year institutional historical data is available. |
| **Recurrent Neural Networks (LSTM / GRU)** | **Low/Medium** (Requires attention maps or Integrated Gradients) | **High** (Backprop through time, GPU inference) | **Very High** (Dense sequential event traces) | **Very Low** (Requires long sequences) | **Medium/Low** | Excellent at sequential modeling, but opaque, computationally demanding, and lacks natural faculty auditability. |
| **Transformers (Attention-based Encoders)** | **Low/Medium** (Attention weights do not equal explanation) | **Very High** (Self-attention $\mathcal{O}(T^2)$, heavy training) | **Extremely High** (Massive tokenized log sequences) | **Extremely Low** | **Low** | Massive over-engineering for 3 core administrative signals; severe trust and explainability barriers. |

*Note: This matrix represents an engineering design and pedagogical tradeoff comparison for institutional decision support, not an empirical benchmark.*

---

## Architectural Decision for Hackathon Prototype
For the hackathon MVP, Tripwire deliberately prioritizes:
1. **Transparent Weighted DVI**:
   $$\text{DVI} = 0.40 \cdot \text{Drift}_{\text{Attendance}} + 0.35 \cdot \text{Drift}_{\text{SubmissionDelay}} + 0.25 \cdot \text{Drop}_{\text{Engagement}}$$
2. **Individual Baseline**: Drift measured against personal norms rather than cohort distribution.
3. **Additive Interpretability**: Faculty see the exact breakdown of points contributing to the alert.
4. **Decoupled AI Layer**: LLMs (Gemini) are utilized solely as a communication and translation layer to craft empathetic dialogue, leaving the analytical verdict strictly deterministic.

---

## Key Concepts to Investigate
1. **Occam's Razor in Applied AI**:
   - In high-stakes educational decision making, the simplest model that accomplishes the objective with full interpretability is ethically and practically superior to complex neural models.
2. **The "Clever Hans" Effect in Educational Deep Learning**:
   - Deep models frequently latch onto non-causal confounding features (e.g., student ID ranges, browser version strings) rather than true pedagogical signals. Transparent rule-based formulations eliminate this vulnerability.

---

## Relevant Literature & Citations
- **Key Reference**: *"Stop Explaining Black Box Machine Learning Models for High Stakes Decisions and Use Interpretable Models Instead"* (Rudin, Nature Machine Intelligence, 2019).
  - Seminal work proving that complex black-box models rarely outperform well-engineered interpretable models on structured tabular data, while creating severe safety and accountability risks.
- **Key Reference**: *"Interpretable Machine Learning in Education: A Comparative Study of White-Box vs. Black-Box Models"* (2024).

---

## Relevant Search Terms
- `interpretable models vs black box educational data mining`
- `Cynthia Rudin interpretable machine learning high stakes decisions`
- `algorithm comparison student retention prediction`
- `feature attribution SHAP vs transparent scorecards`
- `overfitting sequential deep learning educational logs`

---

## Limitations & Open Questions to Verify
- **Weight Calibration**: The prototype weights (40% / 35% / 25%) are intuitive and grounded in pedagogical literature. Future iterations could use ridge regression or Bayesian optimization on historical cohort data to fine-tune weights for specific academic disciplines.
