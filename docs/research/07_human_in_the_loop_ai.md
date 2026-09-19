# Research Topic: Human-in-the-Loop (HITL) AI and Mentorship Workflows

## Why it Matters to Tripwire
A fundamental architectural commitment of Tripwire is that AI must **never** independently label, judge, or enact automated sanctions upon a student. Disengagement is a human experience with diverse, multifaceted causes—some academic, some health-related, some personal.

Tripwire operationalizes **Human-in-the-Loop (HITL)** architecture: algorithms serve purely as an observational radar, presenting decision-support telemetry to qualified faculty mentors who exercise empathy, professional judgment, and verified action.

---

## Key Concepts to Investigate
1. **Decision Support vs. Automated Adjudication**:
   - *Automated Adjudication*: AI flags student $\rightarrow$ system automatically downgrades grade, sends disciplinary warning, or locks portal access. *(Strictly rejected by Tripwire)*.
   - *Decision Support*: AI detects drift $\rightarrow$ alerts faculty mentor privately $\rightarrow$ mentor reviews context $\rightarrow$ mentor conducts private check-in $\rightarrow$ mentor records outcome $\rightarrow$ system tracks recovery.

2. **The Risk of Algorithmic Paternalism**:
   - Automated outreach (e.g., canned bot emails stating "We noticed you missed class") often alienates students, leading to defiance or disengagement.
   - Human mentors can frame conversations supportively ("I noticed things have been hectic lately, wanted to see if I can help connect you with resources").

3. **Closing the Telemetry Loop**:
   - Most early-warning tools are "open loop"—they send an alert and have no concept of whether someone intervened or whether the student improved.
   - Tripwire is a "closed loop" system: intervention recording and subsequent recovery tracking are primary entities within the state machine.

---

## Relevant Literature & Citations
- **Key Reference**: *"Human-in-the-Loop Decision-Making in Education: Navigating the Balance Between Algorithmic Efficiency and Pedagogical Discretion"* (2024).
  - Demonstrates that faculty agency and discretionary override are vital to institutional ethics and legal compliance in higher education.
  - Highlights that faculty must have the ability to annotate, override, and dismiss algorithmic alerts based on offline context.
- **Key Reference**: *"Mentorship and Student Retention: The Transformative Role of Faculty Outreach Following Early Warning Signals"* (2023).
  - Shows that proactive, empathetic mentor contact within 48 hours of an early disengagement flag increases course completion rates by 34%.

---

## Relevant Search Terms
- `human in the loop AI higher education decision support`
- `pedagogical discretion algorithmic decision making`
- `faculty mentorship learning analytics intervention`
- `closed loop intervention tracking early warning system`
- `preventing automated punitive actions AI education`

---

## How It Influences Tripwire's Implementation
1. **Mentor-Centric User Interface**: The UI is optimized for faculty mentors, placing case history, contact forms, and conversation starters in one integrated workspace.
2. **Mandatory Intervention Step**: Tripwire does not allow an alert to transition from "Active" to "Resolved" without an explicit mentor action recording the contact date, contact method, and outcome.
3. **Structured Intervention Log**: Mentors record specific outcomes (e.g., *Academic issue identified*, *Personal difficulty reported*, *Referred to support service*, *Monitoring*), building institutional memory.

---

## Limitations & Open Questions to Verify
- **Faculty Accountability**: How to ensure mentors follow up promptly without creating bureaucratic reporting burdens?
- **Intervention Quality**: While Tripwire records that an intervention occurred, assessing the qualitative depth of the conversation remains a human leadership responsibility.
