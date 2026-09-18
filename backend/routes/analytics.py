"""
Analytics & Model Validation Router — routes/analytics.py
"""
import os
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db, FlagFeedback, TripwireAlert
from routes.auth import get_current_mentor
from scripts.validate_weights import run_weight_validation
from scripts.validate_model import run_model_validation

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/weight-validation")
def get_weight_validation(db: Session = Depends(get_db)):
    """
    Returns empirical sensitivity & archetype separation analysis for DVI weights:
    Compares 0.40/0.35/0.25 vs Equal (33/33/34), Attendance-heavy, Submission-heavy, and LMS-heavy.
    """
    report_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "weight_validation_results.json")
    if os.path.exists(report_json_path):
        try:
            with open(report_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # If file doesn't exist yet, run validation dynamically
    return run_weight_validation()


@router.get("/model-validation")
def get_model_validation(db: Session = Depends(get_db)):
    """
    Per-archetype precision, recall, and F1 score for the DVI alert system.
    Evaluates the 7 behavioral archetypes across the 50-student synthetic cohort
    to prove the deterministic DVI outperforms random/equal baselines.
    """
    cache_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "scripts", "model_validation_results.json"
    )
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return run_model_validation()



@router.get("/trust-score")
def get_trust_score(db: Session = Depends(get_db)):
    """
    Closed-loop System Trust Score tracking endpoint.
    Directly operationalizes Bhattacherjee & Premkumar's (2004) expectation-disconfirmation
    model in early-warning systems (EWS), tracking post-usage trust evolution.
    """
    feedbacks = db.query(FlagFeedback).join(
        TripwireAlert, FlagFeedback.alert_id == TripwireAlert.alert_id
    ).all()

    total_count = len(feedbacks)

    if total_count == 0:
        return {
            "status": "no_feedback_yet",
            "overall_trust_score": None,
            "total_feedback_count": 0,
            "false_positive_rate": None,
            "accurate_rate": None,
            "avg_useful": None,
            "trust_score_trend": [],
            "breakdown_by_dvi_range": [],
            "ratings_distribution": {
                "5_star": 0, "4_star": 0, "3_star": 0, "2_star": 0, "1_star": 0
            },
            "accuracy_breakdown": {
                "accurate": 0, "false_positive": 0, "too_late": 0, "unclear": 0
            },
            "narrative": "Not enough feedback recorded yet. As faculty mentors review alerts and submit verification feedback, empirical trust metrics will populate here.",
            "recovery_diff": None,
            "theoretical_grounding": "Bhattacherjee & Premkumar (2004) Expectation-Disconfirmation Theory; UTAUT Technology Acceptance in EWS"
        }

    # 1. Overall Composite Trust Score from real data
    accurate_count = sum(1 for f in feedbacks if f.was_accurate == "accurate")
    false_pos_count = sum(1 for f in feedbacks if f.was_accurate == "false_positive")
    too_late_count = sum(1 for f in feedbacks if f.was_accurate == "too_late")
    unclear_count = sum(1 for f in feedbacks if f.was_accurate == "unclear")

    pct_accurate = (accurate_count / total_count) * 100.0
    false_pos_rate = (false_pos_count / total_count) * 100.0
    avg_useful = sum(f.was_useful for f in feedbacks) / total_count
    overall_score = round((pct_accurate * 0.5) + ((avg_useful / 5.0) * 100.0 * 0.5), 1)

    # 2. Semester Longitudinal Trend (Disconfirmation Curve)
    semester_weeks = [
        {"week": "Week 1", "label": "W1 (10–16 Aug)", "start": datetime(2026, 8, 10), "end": datetime(2026, 8, 16, 23, 59, 59)},
        {"week": "Week 2", "label": "W2 (17–23 Aug)", "start": datetime(2026, 8, 17), "end": datetime(2026, 8, 23, 23, 59, 59)},
        {"week": "Week 3", "label": "W3 (24–30 Aug)", "start": datetime(2026, 8, 24), "end": datetime(2026, 8, 30, 23, 59, 59)},
        {"week": "Week 4", "label": "W4 (31 Aug–6 Sep)", "start": datetime(2026, 8, 31), "end": datetime(2026, 9, 6, 23, 59, 59)},
        {"week": "Week 5", "label": "W5 (7–13 Sep)", "start": datetime(2026, 9, 7), "end": datetime(2026, 9, 13, 23, 59, 59)},
        {"week": "Week 6", "label": "W6 (Current)", "start": datetime(2026, 9, 14), "end": datetime(2026, 9, 21, 23, 59, 59)},
    ]

    trust_score_trend = []
    for w in semester_weeks:
        w_fbs = [f for f in feedbacks if w["start"] <= f.submitted_at <= w["end"]]
        if w_fbs:
            w_total = len(w_fbs)
            w_acc = sum(1 for f in w_fbs if f.was_accurate == "accurate")
            w_fp = sum(1 for f in w_fbs if f.was_accurate == "false_positive")
            w_useful = sum(f.was_useful for f in w_fbs) / w_total
            w_acc_pct = (w_acc / w_total) * 100.0
            w_score = round((w_acc_pct * 0.5) + ((w_useful / 5.0) * 100.0 * 0.5), 1)
            trust_score_trend.append({
                "week": w["week"],
                "label": w["label"],
                "trust_score": w_score,
                "accurate_pct": round(w_acc_pct, 1),
                "avg_useful": round(w_useful, 1),
                "sample_count": w_total,
                "false_positive_rate": round((w_fp / w_total) * 100.0, 1),
                "phase": "Disconfirmation Dip" if w["week"] in ["Week 2", "Week 3"] else ("Calibrated Recovery" if w["week"] in ["Week 4", "Week 5", "Week 6"] else "Initial Deployment")
            })

    # 3. Breakdown by DVI Severity Range
    dvi_ranges = [
        {"key": "70_79", "range_label": "DVI 70–79 (Moderate Drift)", "min": 70.0, "max": 79.9},
        {"key": "80_89", "range_label": "DVI 80–89 (Elevated Drift)", "min": 80.0, "max": 89.9},
        {"key": "90_100", "range_label": "DVI 90–100 (Critical Disengagement)", "min": 90.0, "max": 100.0},
    ]

    breakdown_by_dvi_range = []
    for dr in dvi_ranges:
        matching_fbs = [f for f in feedbacks if f.alert and dr["min"] <= f.alert.dvi_score <= dr["max"]]
        if matching_fbs:
            m_total = len(matching_fbs)
            m_acc = sum(1 for f in matching_fbs if f.was_accurate == "accurate")
            m_fp = sum(1 for f in matching_fbs if f.was_accurate == "false_positive")
            m_useful = sum(f.was_useful for f in matching_fbs) / m_total
            m_acc_pct = (m_acc / m_total) * 100.0
            m_score = round((m_acc_pct * 0.5) + ((m_useful / 5.0) * 100.0 * 0.5), 1)
            breakdown_by_dvi_range.append({
                "range": dr["range_label"],
                "count": m_total,
                "accurate_pct": round(m_acc_pct, 1),
                "false_positive_rate": round((m_fp / m_total) * 100.0, 1),
                "avg_useful": round(m_useful, 1),
                "trust_score": m_score
            })

    # 4. Compute Trust Improvement vs earliest available week
    recovery_diff = None
    if len(trust_score_trend) >= 2:
        recovery_diff = round(trust_score_trend[-1]["trust_score"] - trust_score_trend[0]["trust_score"], 1)

    narrative = (
        f"Based on {total_count} faculty review(s), overall trust is {overall_score:.1f}/100 "
        f"with {pct_accurate:.1f}% flag accuracy consensus and an average actionability score of {avg_useful:.1f}/5.0."
    )

    return {
        "status": "active",
        "overall_trust_score": overall_score,
        "trust_score_trend": trust_score_trend,
        "false_positive_rate": round(false_pos_rate, 1),
        "accurate_rate": round(pct_accurate, 1),
        "avg_useful": round(avg_useful, 1),
        "total_feedback_count": total_count,
        "breakdown_by_dvi_range": breakdown_by_dvi_range,
        "narrative": narrative,
        "recovery_diff": recovery_diff,
        "ratings_distribution": {
            "5_star": sum(1 for f in feedbacks if f.was_useful == 5),
            "4_star": sum(1 for f in feedbacks if f.was_useful == 4),
            "3_star": sum(1 for f in feedbacks if f.was_useful == 3),
            "2_star": sum(1 for f in feedbacks if f.was_useful == 2),
            "1_star": sum(1 for f in feedbacks if f.was_useful == 1),
        },
        "accuracy_breakdown": {
            "accurate": accurate_count,
            "false_positive": false_pos_count,
            "too_late": too_late_count,
            "unclear": unclear_count
        },
        "theoretical_grounding": "Bhattacherjee & Premkumar (2004) Expectation-Disconfirmation Theory; UTAUT Technology Acceptance in EWS"
    }
