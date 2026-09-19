# Research Topic: Time-Series Behavioral Change Detection

## Why it Matters to Tripwire
Disengagement is a temporal process, not a static state. A student does not become disengaged overnight; the phenomenon unfolds as a series of micro-decisions—a missed morning lab, a late homework upload, three days without logging into the course portal.

To detect this silent drift in real time, Tripwire must apply time-series change-point and anomaly detection concepts that balance sensitivity to genuine downward drift with robustness against single-day anomalies.

---

## Key Concepts to Investigate
1. **Statistical Change-Point Detection (CPD)**:
   - Identifies points in time where the probability distribution of a time-series stochastic process changes.
   - Offline vs. Online/Sequential CPD: Online algorithms (such as CUSUM or Page-Hinkley test) update drift statistics sequentially with each new observation.

2. **Exponential Moving Averages (EMA) vs. Simple Moving Windows**:
   - Simple Moving Average (SMA) weights all days in the window equally (e.g., 14 days).
   - Exponential Moving Average (EMA) applies exponentially decreasing weights over time:
     $$\text{EMA}_t = \alpha \cdot X_t + (1 - \alpha) \cdot \text{EMA}_{t-1}$$
   - Gives higher sensitivity to sudden recent drop-offs while smoothing out high-frequency noise.

3. **Rate of Change & Temporal Velocity**:
   - Velocity ($\frac{\Delta \text{Metric}}{\Delta t}$) and Acceleration ($\frac{\Delta^2 \text{Metric}}{\Delta t^2}$) capture whether a student is slowly drifting or rapidly deteriorating.
   - For Tripwire, distinguishing between steady drift and sudden freefall informs the urgency of the faculty notification.

4. **Z-Score Normalization of Residuals**:
   - Standardizing the deviation of current window behavior relative to the mean and standard deviation of the student's historical baseline:
     $$Z_i(t) = \frac{x_i(t) - \mu_{\text{baseline}, i}}{\sigma_{\text{baseline}, i}}$$

---

## Relevant Literature & Citations
- **Key Reference**: *"Online Change-Point Detection in Educational Data Mining: A Review of Methods and Applications"* (2022).
  - Evaluates cumulative sum (CUSUM), Bayesian change-point algorithms, and moving-window variance tests on learning trace data.
  - Finds that moving-window deviation with explicit baseline subtraction provides optimal interpretability and latency for classroom deployment.
- **Key Reference**: *"Sequential Analysis of Time-Series LMS Data for Early Detection of Academic Disengagement"* (2025).
  - Shows that sudden spikes in submission delay variance often precede attendance drops by 7 to 10 days.

---

## Relevant Search Terms
- `time series change point detection learning analytics`
- `exponential moving average behavioral drift detection`
- `CUSUM anomaly detection student engagement`
- `submission latency time series trajectory modeling`
- `rolling window statistical process control education`

---

## How It Influences Tripwire's Implementation
1. **Multi-Horizon Rolling Windows**:
   - Attendance drift evaluated over a **14-day rolling window** to account for bi-weekly lecture cycles and avoid overreacting to an isolated absent period.
   - LMS activity evaluated over a **7-day window** (normalized to weekly frequency) to capture weekly study rhythms.
   - Submission delay evaluated across the **last $N=5$ assignments**, computing median latency to insulate against a single non-representative late assignment.
2. **Velocity Indicators**: Tripwire computes behavioral trend arrows (`↘↘`, `↘`, `→`, `↗`, `↗↗`) alongside raw DVI to visualize directional momentum.
3. **Temporal Alignment**: Daily time-series computation enables the 28-day historical DVI graph in the faculty dashboard.

---

## Limitations & Open Questions to Verify
- **Irregular Sampling Intervals**: Unlike automated network telemetry, academic events (assignments, classes) occur on scheduled calendar dates with gaps during weekends and holidays.
- **Sensitivity vs. Specificity Trade-Off**: Excessively narrow windows (e.g., 3 days) trigger false alarms from minor schedule conflicts; excessively wide windows (e.g., 30 days) delay intervention until failure is imminent. The 14-day window provides an optimal empirical compromise.
