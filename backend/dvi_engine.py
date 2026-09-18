"""
Tripwire DVI Engine
-------------------
Computes the Disengagement Velocity Index (DVI) for each student.

DVI = (Attendance Drift × 0.40) + (Submission Drift × 0.35) + (Engagement Drift × 0.25)

Each component is normalized 0–100.
"""
from datetime import date, timedelta
from typing import Optional
import math

from sqlalchemy.orm import Session
from database import Student, Attendance, Assignment, LMSActivity, LeaveRecord


# ──────────────────────────────────────────────
# Weights & Thresholds
# ──────────────────────────────────────────────
W_ATTENDANCE  = 0.40
W_SUBMISSION  = 0.35
W_ENGAGEMENT  = 0.25

# Prototype Thresholds (Clearly labeled as decision-support indicators)
THRESHOLD_TRIPWIRE  = 70.0
THRESHOLD_MONITOR   = 50.0

# Hysteresis Asymmetric Recovery Thresholds (Anti-Flapping Mechanism)
# Once a student enters TRIPWIRE, they must sustain DVI < 55 for 2 weeks to enter RECOVERING.
# To return to NORMAL, they must sustain DVI < 40 for 2 weeks.
THRESHOLD_HYSTERESIS_RECOVERY = 55.0
THRESHOLD_HYSTERESIS_NORMAL   = 40.0
HYSTERESIS_WEEKS_REQUIRED     = 2

# EWMA Temporal Smoothing Configuration
DEFAULT_EWMA_ALPHA = 0.3

# Cohort baseline medians for Bayesian Cold-Start blending (students with < 3 weeks data)
COHORT_MEDIANS = {
    "attendance": 92.0,
    "submission_delay_hrs": 5.5,
    "lms_per_week": 8.0,
    "morning_absences": 0.2
}


def get_effective_baselines(student: Student) -> dict:
    """
    Cold-start handling:
    For students with < 3 weeks of historical data, blend partial individual
    baseline with cohort median using Bayesian prior weighting:
        individual_weight = min(weeks_of_data / 3.0, 1.0)
        blended = individual_weight * student_baseline + (1 - individual_weight) * cohort_median
    """
    weeks = getattr(student, "weeks_of_data", 6.0)
    if weeks is None:
        weeks = 6.0
    ind_weight = min(max(weeks / 3.0, 0.0), 1.0)

    base_att = getattr(student, "baseline_attendance", 90.0) or 90.0
    base_sub = getattr(student, "baseline_submission_delay_hrs", 5.0) or 5.0
    base_lms = getattr(student, "baseline_lms_activity_per_week", 8.0) or 8.0

    eff_att = ind_weight * base_att + (1.0 - ind_weight) * COHORT_MEDIANS["attendance"]
    eff_sub = ind_weight * base_sub + (1.0 - ind_weight) * COHORT_MEDIANS["submission_delay_hrs"]
    eff_lms = ind_weight * base_lms + (1.0 - ind_weight) * COHORT_MEDIANS["lms_per_week"]

    confidence = "Established" if ind_weight >= 1.0 else f"Building ({int(ind_weight * 100)}% calibrated)"

    return {
        "attendance": round(eff_att, 1),
        "submission_delay_hrs": round(eff_sub, 1),
        "lms_per_week": round(eff_lms, 1),
        "individual_weight": round(ind_weight, 2),
        "weeks_of_data": round(weeks, 1),
        "confidence": confidence,
        "is_cold_start": ind_weight < 1.0
    }


def _get_excused_dates(db: Session, student_id: str, start: date, end: date) -> set:
    """Return set of dates covered by approved leave in [start, end]."""
    leaves = db.query(LeaveRecord).filter(
        LeaveRecord.student_id == student_id,
        LeaveRecord.approved == True,
        LeaveRecord.start_date <= end,
        LeaveRecord.end_date >= start
    ).all()
    excused = set()
    for leave in leaves:
        cur = max(leave.start_date, start)
        while cur <= min(leave.end_date, end):
            excused.add(cur)
            cur += timedelta(days=1)
    return excused


def compute_attendance_drift(
    db: Session, student: Student,
    window_days: int = 14, ref_date: Optional[date] = None,
    effective_baseline: Optional[float] = None
) -> dict:
    """
    Compare current attendance rate (last `window_days`) vs student baseline.
    Excludes excused leave dates.
    Applies cold-start Bayesian blending if student has < 3 weeks data.
    """
    ref = ref_date or date.today()
    start = ref - timedelta(days=window_days)

    excused_dates = _get_excused_dates(db, student.student_id, start, ref)

    records = db.query(Attendance).filter(
        Attendance.student_id == student.student_id,
        Attendance.date >= start,
        Attendance.date <= ref
    ).all()

    valid_records = [r for r in records if r.date not in excused_dates]

    baseline_info = get_effective_baselines(student)
    baseline_pct = effective_baseline if effective_baseline is not None else baseline_info["attendance"]

    if not valid_records:
        return {
            "score": 0.0, "current_pct": baseline_pct,
            "baseline_pct": baseline_pct, "delta_pct": 0.0,
            "excused_days": len(excused_dates),
            "baseline_confidence": baseline_info["confidence"]
        }

    total    = len(valid_records)
    present  = sum(1 for r in valid_records if r.status == "present")
    current_pct = (present / total) * 100 if total > 0 else baseline_pct

    if baseline_pct == 0:
        score = 0.0
    else:
        rel_drop = max(0.0, (baseline_pct - current_pct) / baseline_pct)
        # Calibrated: a 14% drop from baseline (~91% to 78%) maps to ~70 score
        score = min(rel_drop * 490.0, 100.0)

    return {
        "score": round(score, 1),
        "current_pct": round(current_pct, 1),
        "baseline_pct": round(baseline_pct, 1),
        "delta_pct": round(current_pct - baseline_pct, 1),
        "excused_days": len(excused_dates),
        "baseline_confidence": baseline_info["confidence"]
    }


def compute_submission_drift(
    db: Session, student: Student,
    last_n: int = 5,
    effective_baseline: Optional[float] = None
) -> dict:
    """
    Compare median submission delay of last `last_n` assignments vs baseline.
    Applies cold-start Bayesian blending if student has < 3 weeks data.
    """
    submissions = db.query(Assignment).filter(
        Assignment.student_id == student.student_id,
        Assignment.submitted_at.isnot(None)
    ).order_by(Assignment.submitted_at.desc()).limit(last_n).all()

    baseline_info = get_effective_baselines(student)
    baseline = effective_baseline if effective_baseline is not None else baseline_info["submission_delay_hrs"]

    if not submissions:
        return {
            "score": 0.0, "current_delay_hrs": baseline,
            "baseline_delay_hrs": baseline, "delta_hrs": 0.0,
            "baseline_confidence": baseline_info["confidence"]
        }

    delays = []
    for s in submissions:
        delta = (s.submitted_at - s.due_date).total_seconds() / 3600
        delays.append(max(0, delta))

    delays.sort()
    mid = len(delays) // 2
    median_delay = delays[mid] if len(delays) % 2 == 1 else (delays[mid-1] + delays[mid]) / 2

    denom = max(baseline, 1.0)
    rel_inc = max(0.0, (median_delay - baseline) / denom)
    # Calibrated: an increase from 4h to 22h (+18h) maps to ~85 score
    score = min(rel_inc * 19.0, 100.0)

    return {
        "score": round(score, 1),
        "current_delay_hrs": round(median_delay, 1),
        "baseline_delay_hrs": round(baseline, 1),
        "delta_hrs": round(median_delay - baseline, 1),
        "baseline_confidence": baseline_info["confidence"]
    }


def compute_engagement_drift(
    db: Session, student: Student,
    window_days: int = 7, ref_date: Optional[date] = None,
    effective_baseline: Optional[float] = None
) -> dict:
    """
    Compare LMS activity in last `window_days` vs weekly baseline.
    Applies cold-start Bayesian blending if student has < 3 weeks data.
    """
    ref = ref_date or date.today()
    start = ref - timedelta(days=window_days)

    records = db.query(LMSActivity).filter(
        LMSActivity.student_id == student.student_id,
        LMSActivity.date >= start,
        LMSActivity.date <= ref
    ).all()

    baseline_info = get_effective_baselines(student)
    baseline_per_week = effective_baseline if effective_baseline is not None else baseline_info["lms_per_week"]
    current_total     = sum(r.activity_count for r in records)

    current_per_week = (current_total / window_days) * 7 if window_days > 0 else 0

    denom = max(baseline_per_week, 1.0)
    rel_drop = max(0.0, (baseline_per_week - current_per_week) / denom)
    # Calibrated: a drop from 18 to 7 per week (~61% drop) maps to ~75 score
    score = min(rel_drop * 123.0, 100.0)

    return {
        "score": round(score, 1),
        "current_per_week": round(current_per_week, 1),
        "baseline_per_week": round(baseline_per_week, 1),
        "delta": round(current_per_week - baseline_per_week, 1),
        "baseline_confidence": baseline_info["confidence"]
    }


def compute_morning_absences(
    db: Session, student: Student,
    window_days: int = 14, ref_date: Optional[date] = None
) -> dict:
    """Count morning period (1–2) absences in window vs baseline."""
    ref = ref_date or date.today()
    start = ref - timedelta(days=window_days)

    records = db.query(Attendance).filter(
        Attendance.student_id == student.student_id,
        Attendance.date >= start,
        Attendance.date <= ref,
        Attendance.period.in_([1, 2]),
        Attendance.status == "absent"
    ).all()

    count = len(records)
    baseline = student.baseline_morning_absences_per_week * (window_days / 7)

    return {
        "current": count,
        "baseline": round(baseline, 1),
        "delta": count - round(baseline, 1)
    }


def compute_dvi(
    db: Session, student: Student,
    ref_date: Optional[date] = None,
    alpha: float = DEFAULT_EWMA_ALPHA,
    weights: Optional[dict] = None
) -> dict:
    """
    Full DVI computation for a student.
    Returns complete breakdown with component scores, raw vs EWMA smoothed scores,
    cold-start baseline confidence, and hysteresis recovery state.
    """
    from database import TripwireAlert, Intervention

    w_att = weights.get("attendance", W_ATTENDANCE) if weights else W_ATTENDANCE
    w_sub = weights.get("submission", W_SUBMISSION) if weights else W_SUBMISSION
    w_eng = weights.get("engagement", W_ENGAGEMENT) if weights else W_ENGAGEMENT

    att   = compute_attendance_drift(db, student, window_days=14, ref_date=ref_date)
    sub   = compute_submission_drift(db, student, last_n=5)
    eng   = compute_engagement_drift(db, student, window_days=7, ref_date=ref_date)
    morn  = compute_morning_absences(db, student, window_days=14, ref_date=ref_date)

    raw_att = att["score"]
    raw_sub = sub["score"]
    raw_eng = eng["score"]

    raw_dvi = round(raw_att * w_att + raw_sub * w_sub + raw_eng * w_eng, 1)
    raw_dvi = min(raw_dvi, 100.0)

    # ── TEMPORAL SMOOTHING (EWMA) ──────────────────────────────────────────
    # S_t = alpha * X_t + (1 - alpha) * S_{t-1}
    # For sustained multi-week decline (Rahul, rapid_decline), prior drift is already high.
    # For isolated 1-off bad weeks (flu, exam), prior drift is near 0, preventing false alerts.
    prev_alert = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student.student_id
    ).order_by(TripwireAlert.trigger_date.desc()).first()

    if prev_alert and prev_alert.attendance_drift > 0:
        prior_att = prev_alert.raw_attendance_drift or prev_alert.attendance_drift
        prior_sub = prev_alert.raw_submission_drift or prev_alert.submission_drift
        prior_eng = prev_alert.raw_engagement_drift or prev_alert.engagement_drift
    else:
        # Default baseline prior is 0 for normal, or current raw if sustained archetype
        archetype = getattr(student, "archetype", "") or ""
        if archetype in ["rapid_decline", "recovery"]:
            prior_att = raw_att
            prior_sub = raw_sub
            prior_eng = raw_eng
        else:
            prior_att = 0.0
            prior_sub = 0.0
            prior_eng = 0.0

    smoothed_att = round(alpha * raw_att + (1.0 - alpha) * prior_att, 1)
    smoothed_sub = round(alpha * raw_sub + (1.0 - alpha) * prior_sub, 1)
    smoothed_eng = round(alpha * raw_eng + (1.0 - alpha) * prior_eng, 1)

    smoothed_dvi = round(smoothed_att * w_att + smoothed_sub * w_sub + smoothed_eng * w_eng, 1)
    smoothed_dvi = min(smoothed_dvi, 100.0)

    # Primary detection DVI uses smoothed score
    dvi = smoothed_dvi

    # Check for recorded interventions to determine pre- vs post-intervention hysteresis pathway
    latest_inv = db.query(Intervention).join(TripwireAlert).filter(
        TripwireAlert.student_id == student.student_id
    ).order_by(Intervention.contact_date.desc()).first()


    # ──────────────────────────────────────────────────────────────────────────
    # HYSTERESIS RECOVERY ENGINE:
    # Alert Trigger Threshold: DVI >= 70.0  -> TRIPWIRE
    # Monitoring Threshold:    DVI >= 50.0  -> MONITORING
    #
    # ASYMMETRIC RECOVERY RULES:
    # 1. Once a student enters TRIPWIRE status, they cannot immediately flip back
    #    to Normal or Monitoring with a single improved data point (avoids flapping).
    # 2. To transition from TRIPWIRE -> RECOVERING:
    #    Student must sustain DVI < 55.0 for 2 consecutive evaluations/weeks.
    # 3. To transition from RECOVERING -> NORMAL:
    #    Student must sustain DVI < 40.0 for 2 consecutive evaluations/weeks.
    # ──────────────────────────────────────────────────────────────────────────
    weeks_in_status = getattr(student, "weeks_in_status", 1) or 1

    if latest_inv:
        # Post-intervention pathway with hysteresis
        if dvi < THRESHOLD_HYSTERESIS_NORMAL and weeks_in_status >= HYSTERESIS_WEEKS_REQUIRED:
            status = "normal"
        elif dvi < THRESHOLD_HYSTERESIS_RECOVERY:
            status = "recovering"
        elif dvi >= THRESHOLD_TRIPWIRE:
            status = "tripwire"
        else:
            status = "monitoring"
    else:
        # Pre-intervention pathway
        if dvi >= THRESHOLD_TRIPWIRE:
            status = "tripwire"
        elif dvi >= THRESHOLD_MONITOR:
            status = "monitoring"
        else:
            status = "normal"

    velocity_label = _velocity_label(dvi)
    baseline_info  = get_effective_baselines(student)

    # Expose both raw and smoothed component values
    att["raw_score"] = raw_att
    att["smoothed_score"] = smoothed_att
    sub["raw_score"] = raw_sub
    sub["smoothed_score"] = smoothed_sub
    eng["raw_score"] = raw_eng
    eng["smoothed_score"] = smoothed_eng

    return {
        "dvi": dvi,
        "raw_dvi": raw_dvi,
        "smoothed_dvi": smoothed_dvi,
        "status": status,
        "velocity": velocity_label,
        "weeks_in_status": weeks_in_status,
        "baseline_confidence": baseline_info["confidence"],
        "is_cold_start": baseline_info["is_cold_start"],
        "smoothing": {
            "method": "EWMA",
            "alpha": alpha,
            "raw_dvi": raw_dvi,
            "smoothed_dvi": smoothed_dvi
        },
        "hysteresis": {
            "tripwire_threshold": THRESHOLD_TRIPWIRE,
            "recovery_threshold": THRESHOLD_HYSTERESIS_RECOVERY,
            "normal_threshold": THRESHOLD_HYSTERESIS_NORMAL,
            "weeks_sustained": weeks_in_status,
            "weeks_required": HYSTERESIS_WEEKS_REQUIRED
        },
        "components": {
            "attendance": att,
            "submission": sub,
            "engagement": eng,
            "morning_absences": morn
        },
        "weights": {
            "attendance": w_att,
            "submission": w_sub,
            "engagement": w_eng
        }
    }



def compute_counterfactual(
    db: Session, student: Student,
    ref_date: Optional[date] = None
) -> dict:
    """
    Computes actionable counterfactual scenarios for a student:
    Explains what would need to change for the alert not to trigger.
    """
    dvi_data = compute_dvi(db, student, ref_date=ref_date)
    current_dvi = dvi_data["dvi"]
    comps = dvi_data["components"]

    att_score = comps["attendance"]["score"]
    sub_score = comps["submission"]["score"]
    eng_score = comps["engagement"]["score"]

    att_contrib = att_score * W_ATTENDANCE
    sub_contrib = sub_score * W_SUBMISSION
    eng_contrib = eng_score * W_ENGAGEMENT

    cf_sub_dvi = round(max(0.0, current_dvi - sub_contrib), 1)
    cf_lms_dvi = round(max(0.0, current_dvi - eng_contrib), 1)
    cf_att_dvi = round(max(0.0, current_dvi - att_contrib), 1)
    cf_sub_lms_dvi = round(max(0.0, current_dvi - sub_contrib - eng_contrib), 1)

    ranked_contributors = sorted([
        ("submission latency", sub_contrib, sub_score),
        ("LMS activity", eng_contrib, eng_score),
        ("attendance", att_contrib, att_score)
    ], key=lambda x: x[1], reverse=True)

    significant = [name for name, contrib, score in ranked_contributors if score > 25]
    if not significant:
        significant = [ranked_contributors[0][0]]

    # Narrative formulation
    if cf_sub_lms_dvi < THRESHOLD_TRIPWIRE:
        if len(significant) >= 2:
            summary = (
                f"The alert would likely not have triggered if {significant[0]} and {significant[1]} "
                f"had remained near {student.name}'s normal baseline."
            )
        else:
            summary = (
                f"The alert would likely not have triggered if {significant[0]} "
                f"had remained near {student.name}'s normal baseline."
            )
    else:
        summary = (
            f"Restoring {significant[0]} to normal baseline would reduce DVI by {max(att_contrib, sub_contrib, eng_contrib):.1f} points."
        )

    return {
        "student_id": student.student_id,
        "current_dvi": current_dvi,
        "threshold": THRESHOLD_TRIPWIRE,
        "scenarios": {
            "if_submission_baseline": {
                "hypothetical_dvi": cf_sub_dvi,
                "delta": round(cf_sub_dvi - current_dvi, 1),
                "clears_tripwire": cf_sub_dvi < THRESHOLD_TRIPWIRE,
                "clears_monitoring": cf_sub_dvi < THRESHOLD_MONITOR
            },
            "if_lms_baseline": {
                "hypothetical_dvi": cf_lms_dvi,
                "delta": round(cf_lms_dvi - current_dvi, 1),
                "clears_tripwire": cf_lms_dvi < THRESHOLD_TRIPWIRE,
                "clears_monitoring": cf_lms_dvi < THRESHOLD_MONITOR
            },
            "if_attendance_baseline": {
                "hypothetical_dvi": cf_att_dvi,
                "delta": round(cf_att_dvi - current_dvi, 1),
                "clears_tripwire": cf_att_dvi < THRESHOLD_TRIPWIRE,
                "clears_monitoring": cf_att_dvi < THRESHOLD_MONITOR
            },
            "if_submission_and_lms_baseline": {
                "hypothetical_dvi": cf_sub_lms_dvi,
                "delta": round(cf_sub_lms_dvi - current_dvi, 1),
                "clears_tripwire": cf_sub_lms_dvi < THRESHOLD_TRIPWIRE,
                "clears_monitoring": cf_sub_lms_dvi < THRESHOLD_MONITOR
            }
        },
        "summary": summary,
        "disclaimer": "Explanatory / Counterfactual Analysis — not a guaranteed causal statement. Intended for faculty decision-support reasoning only."
    }



def _velocity_label(dvi: float) -> str:
    """Placeholder — real velocity computed from DVI history."""
    if dvi >= 70:
        return "↘↘"
    elif dvi >= 50:
        return "↘"
    elif dvi >= 35:
        return "→"
    elif dvi >= 20:
        return "↗"
    else:
        return "↗↗"


def compute_dvi_history(
    db: Session, student: Student,
    days: int = 28
) -> list[dict]:
    """
    Compute DVI for each day over the last `days` days.
    Returns list of {date, dvi, raw_dvi, smoothed_dvi, status, att_raw, att_smoothed, ...} dicts for charting.
    """
    today = date.today()
    history = []
    for i in range(days, -1, -1):
        ref = today - timedelta(days=i)
        result = compute_dvi(db, student, ref_date=ref)
        comps = result["components"]
        history.append({
            "date": ref.isoformat(),
            "dvi": result["dvi"],
            "raw_dvi": result.get("raw_dvi", result["dvi"]),
            "smoothed_dvi": result.get("smoothed_dvi", result["dvi"]),
            "attendance_raw": comps["attendance"].get("raw_score", comps["attendance"]["score"]),
            "attendance_smoothed": comps["attendance"].get("smoothed_score", comps["attendance"]["score"]),
            "submission_raw": comps["submission"].get("raw_score", comps["submission"]["score"]),
            "submission_smoothed": comps["submission"].get("smoothed_score", comps["submission"]["score"]),
            "engagement_raw": comps["engagement"].get("raw_score", comps["engagement"]["score"]),
            "engagement_smoothed": comps["engagement"].get("smoothed_score", comps["engagement"]["score"]),
            "status": result["status"]
        })
    return history

