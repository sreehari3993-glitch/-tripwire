# Research Topic: Privacy, Ethics, and Student Protection in Learning Analytics

## Why it Matters to Tripwire
Modern student monitoring platforms often cross ethical boundaries into invasive surveillance—deploying webcam eye-tracking, background keystroke logging, device location monitoring, or speculative psychological profiling. These practices breach privacy norms, foster adversarial student-institution relationships, and run afoul of data protection regulations.

Tripwire is engineered on strict **privacy-by-design** principles: it relies solely on non-invasive, coarse-grained administrative telemetry already generated in academic routines, keeps alert labels private from students to prevent psychological harm, and incorporates explicit human override controls.

---

## Key Concepts to Investigate
1. **Regulatory Framework: Digital Personal Data Protection (DPDP) Act 2023 (India)**:
   - Mandates purpose limitation: data collected for academic administration cannot be repurposed for invasive automated profiling.
   - Enforces data minimization: only process data strictly necessary for fulfilling the specified educational objective.
   - Right to correction and human oversight: prohibits fully autonomous decisions that produce significant legal or personal consequences on individuals.

2. **The "Panopticon Effect" vs. Minimum Necessary Telemetry**:
   - Invasively monitored students alter their authentic learning behavior, disabling cameras or using proxy evasion.
   - Tripwire processes only 3 standard academic artifacts: attendance records (present/absent), assignment timestamps (due date vs. submitted date), and aggregate LMS interaction counts. No video feeds, keystroke telemetry, or browsing history are collected.

3. **Label Stigmatization & Stereotype Threat**:
   - Labeling a student as "High Risk" or "Dropout Candidate" in a student-visible portal can induce learned helplessness and accelerate the very disengagement it seeks to prevent.
   - Tripwire maintains strict confidentiality: alert states and DVI numbers are **private to authorized faculty mentors**.

4. **Prohibition of Medical & Mental Health Diagnosis**:
   - Academic systems must never diagnose depression, ADHD, anxiety, or cognitive disability. Tripwire models solely observable behavioral drift in academic tasks.

---

## Relevant Literature & Citations
- **Key Reference**: *"Ethics and Privacy in Learning Analytics: A Delphi Study on Institutional Principles and Practical Guidelines"* (Slade & Prinsloo, 2020).
  - Codifies foundational ethical guidelines: transparency of purpose, consent, student agency, and safeguarding against algorithmic discrimination.
- **Key Reference**: *"Algorithmic Harm and Student Surveillance: The Ethical Dilemmas of Automated Proctoring and Early Warning Systems"* (2023).
  - Documents how invasive telemetry damages student mental well-being and trust in educational institutions.
  - Recommends non-invasive, transparent administrative proxies.

---

## Relevant Search Terms
- `learning analytics ethics privacy principles DPDP Act 2023`
- `data minimization student surveillance higher education`
- `student label stigmatization stereotype threat early warning`
- `non invasive academic engagement telemetry`
- `ethical guidelines automated decision support education`

---

## How It Influences Tripwire's Implementation
1. **Privacy & Ethics Manifesto in UI**: A dedicated, prominent modal and dashboard section detailing Tripwire's ethical boundary guarantees.
2. **Strict RBAC (Role-Based Access Control)**: Student identities and DVI trajectories are accessible only to authenticated mentors assigned to that section.
3. **No Speculative Diagnostics**: AI prompts explicitly prohibit medical, psychological, or disciplinary labeling.
4. **Synthetic Data for Prototype**: Hackathon demo strictly uses anonymized, synthetic time-series data without real student PII.

---

## Limitations & Open Questions to Verify
- **Legitimate Excused Absences**: If a student is absent due to bereavement, illness, or sanctioned athletic representation, the system must allow a mentor to mark the records as "EXCUSED", recalculating or dampening the DVI.
