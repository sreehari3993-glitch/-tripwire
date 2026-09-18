"""Alert routes — list alerts, get detail, generate AI explanation."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from database import get_db, TripwireAlert, Student, FlagFeedback
from routes.auth import get_current_mentor
from routes.access import get_owned_alert
from ai_layer import generate_explanation
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

router = APIRouter(prefix="/alerts", tags=["alerts"])


class FeedbackSubmitRequest(BaseModel):
    was_accurate: str  # "accurate", "false_positive", "too_late", "unclear"
    was_useful: int = Field(..., ge=1, le=5)  # 1-5 Likert scale
    comment: Optional[str] = None
    free_text_comment: Optional[str] = None


@router.get("")
def list_alerts(
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    # Get alerts for mentor's students
    mentor_students = db.query(Student).filter(
        Student.mentor_id == mentor.mentor_id
    ).all()
    student_ids = [s.student_id for s in mentor_students]

    alerts = db.query(TripwireAlert).filter(
        TripwireAlert.student_id.in_(student_ids)
    ).order_by(TripwireAlert.trigger_date.desc()).all()

    result = []
    for alert in alerts:
        student = db.query(Student).filter(
            Student.student_id == alert.student_id
        ).first()
        reason = json.loads(alert.reason_json) if alert.reason_json else {}
        result.append({
            "alert_id": alert.alert_id,
            "student_id": alert.student_id,
            "student_name": student.name if student else "Unknown",
            "section": student.section if student else "",
            "dvi_score": alert.dvi_score,
            "trigger_date": alert.trigger_date.isoformat(),
            "status": alert.status,
            "excused_flag": alert.excused_flag,
            "is_read": getattr(alert, "is_read", False),
            "attendance_drift": alert.attendance_drift,
            "submission_drift": alert.submission_drift,
            "engagement_drift": alert.engagement_drift,
            "reason": reason
        })

    return {"alerts": result, "total": len(result)}


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    mentor_students = db.query(Student).filter(
        Student.mentor_id == mentor.mentor_id
    ).all()
    student_ids = [s.student_id for s in mentor_students]

    unread_alerts = db.query(TripwireAlert).filter(
        TripwireAlert.student_id.in_(student_ids),
        TripwireAlert.status == "active",
        TripwireAlert.is_read == False
    ).order_by(TripwireAlert.trigger_date.desc()).all()

    previews = []
    for alert in unread_alerts[:5]:
        student = db.query(Student).filter(Student.student_id == alert.student_id).first()
        previews.append({
            "alert_id": alert.alert_id,
            "student_id": alert.student_id,
            "student_name": student.name if student else "Unknown",
            "section": student.section if student else "",
            "dvi_score": round(alert.dvi_score, 1),
            "trigger_date": alert.trigger_date.isoformat(),
            "status": alert.status
        })

    return {
        "unread_count": len(unread_alerts),
        "recent_unread": previews
    }


@router.post("/mark-all-read")
def mark_all_alerts_read(
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    mentor_students = db.query(Student).filter(
        Student.mentor_id == mentor.mentor_id
    ).all()
    student_ids = [s.student_id for s in mentor_students]

    unread_alerts = db.query(TripwireAlert).filter(
        TripwireAlert.student_id.in_(student_ids),
        TripwireAlert.is_read == False
    ).all()

    for alert in unread_alerts:
        alert.is_read = True
    db.commit()

    return {"success": True, "marked_count": len(unread_alerts)}


@router.post("/{alert_id}/mark-read")
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    alert = get_owned_alert(db, alert_id, mentor)
    alert.is_read = True
    db.commit()
    return {"success": True, "alert_id": alert.alert_id, "is_read": True}


from dvi_engine import compute_counterfactual, compute_dvi

@router.get("/{alert_id}")
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    alert = get_owned_alert(db, alert_id, mentor)

    if not getattr(alert, "is_read", False):
        alert.is_read = True
        db.commit()

    student = db.query(Student).filter(
        Student.student_id == alert.student_id
    ).first()

    reason = json.loads(alert.reason_json) if alert.reason_json else {}

    # Calculate counterfactual analysis for this student
    counterfactual = compute_counterfactual(db, student) if student else None

    # Calculate exact point contributions
    att_contrib = round(alert.attendance_drift * 0.40, 1)
    sub_contrib = round(alert.submission_drift * 0.35, 1)
    eng_contrib = round(alert.engagement_drift * 0.25, 1)

    fb = db.query(FlagFeedback).filter(
        FlagFeedback.alert_id == alert_id
    ).order_by(FlagFeedback.submitted_at.desc()).first()

    feedback_data = {
        "id": fb.id,
        "alert_id": fb.alert_id,
        "faculty_id": fb.faculty_id,
        "was_accurate": fb.was_accurate,
        "was_useful": fb.was_useful,
        "comment": fb.free_text_comment,
        "submitted_at": fb.submitted_at.isoformat()
    } if fb else None

    return {
        "alert_id": alert.alert_id,
        "student_id": alert.student_id,
        "student_name": student.name if student else "Unknown",
        "section": student.section if student else "",
        "roll_no": student.roll_no if student else "",
        "dvi_score": round(alert.dvi_score, 1),
        "trigger_date": alert.trigger_date.isoformat(),
        "status": alert.status,
        "excused_flag": alert.excused_flag,
        "is_read": True,
        "prototype_threshold": 70,
        "components": {
            "attendance": {
                "score": round(alert.attendance_drift, 1),
                "weight": 0.40,
                "contribution": att_contrib
            },
            "submission": {
                "score": round(alert.submission_drift, 1),
                "weight": 0.35,
                "contribution": sub_contrib
            },
            "engagement": {
                "score": round(alert.engagement_drift, 1),
                "weight": 0.25,
                "contribution": eng_contrib
            }
        },
        "reason": reason,
        "counterfactual": counterfactual,
        "baselines": {
            "attendance_pct": student.baseline_attendance if student else None,
            "submission_delay_hrs": student.baseline_submission_delay_hrs if student else None,
            "lms_per_week": student.baseline_lms_activity_per_week if student else None
        },
        "raw_dvi_score": round(alert.raw_dvi_score or alert.dvi_score, 1),
        "pulse": {
            "rating": student.weekly_pulse_score,
            "stuck_on": student.weekly_pulse_note,
            "date": student.weekly_pulse_date.isoformat() if student.weekly_pulse_date else None
        } if (student and student.weekly_pulse_score) else None,
        "feedback": feedback_data,
        "threshold_label": "Prototype threshold: DVI >= 70 (TRIPWIRE)"
    }


@router.post("/{alert_id}/feedback")
def submit_alert_feedback(
    alert_id: int,
    payload: FeedbackSubmitRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """
    Submits or updates faculty feedback for a Tripwire alert.
    Feeds the closed-loop System Trust Score tracking engine.
    """
    alert = get_owned_alert(db, alert_id, mentor)

    valid_accurate = ["accurate", "false_positive", "too_late", "unclear"]
    if payload.was_accurate not in valid_accurate:
        raise HTTPException(status_code=400, detail=f"was_accurate must be one of {valid_accurate}")

    comment_text = payload.free_text_comment or payload.comment or ""

    # Check for existing feedback by this faculty member (upsert)
    existing_fb = db.query(FlagFeedback).filter(
        FlagFeedback.alert_id == alert_id,
        FlagFeedback.faculty_id == mentor.mentor_id
    ).first()

    if existing_fb:
        existing_fb.was_accurate = payload.was_accurate
        existing_fb.was_useful = payload.was_useful
        existing_fb.free_text_comment = comment_text
        existing_fb.submitted_at = datetime.utcnow()
        feedback_obj = existing_fb
    else:
        feedback_obj = FlagFeedback(
            alert_id=alert_id,
            faculty_id=mentor.mentor_id,
            was_accurate=payload.was_accurate,
            was_useful=payload.was_useful,
            free_text_comment=comment_text,
            submitted_at=datetime.utcnow()
        )
        db.add(feedback_obj)

    db.commit()
    db.refresh(feedback_obj)

    return {
        "succes": True,
        "message": "Faculty feedback recorded. System Trust metrics updated.",
        "feedback": {
            "id": feedback_obj.id,
            "alert_id": feedback_obj.alert_id,
            "faculty_id": feedback_obj.faculty_id,
            "was_accurate": feedback_obj.was_accurate,
            "was_useful": feedback_obj.was_useful,
            "comment": feedback_obj.free_text_comment,
            "submitted_at": feedback_obj.submitted_at.isoformat()
        }
    }


@router.get("/{alert_id}/feedback")
def get_alert_feedback(
    alert_id: int,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Retrieves faculty feedback for a specific alert."""
    alert = get_owned_alert(db, alert_id, mentor)

    fb = db.query(FlagFeedback).filter(
        FlagFeedback.alert_id == alert_id,
        FlagFeedback.faculty_id == mentor.mentor_id
    ).first()

    if not fb:
        return {"has_feedback": False, "feedback": None}

    return {
        "has_feedback": True,
        "feedback": {
            "id": fb.id,
            "alert_id": fb.alert_id,
            "faculty_id": fb.faculty_id,
            "was_accurate": fb.was_accurate,
            "was_useful": fb.was_useful,
            "comment": fb.free_text_comment,
            "submitted_at": fb.submitted_at.isoformat()
        }
    }



@router.post("/{alert_id}/excuse")
def mark_alert_excused(
    alert_id: int,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """
    Human override endpoint: Allows faculty to mark this alert as partially or fully excused
    due to approved medical leave, college event, or verified personal circumstance.
    """
    alert = get_owned_alert(db, alert_id, mentor)

    alert.excused_flag = True
    alert.status = "monitoring"  # De-escalate from active tripwire to monitoring
    db.commit()

    return {
        "success": True,
        "message": "Alert marked as EXCUSED by mentor. Status de-escalated to monitoring.",
        "note": "Tripwire supports human override because behavioral signals can have legitimate explanations.",
        "alert_id": alert.alert_id,
        "excused_flag": alert.excused_flag,
        "new_status": alert.status
    }


@router.post("/{alert_id}/ai-explain")
def ai_explain(
    alert_id: int,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    alert = get_owned_alert(db, alert_id, mentor)

    student = db.query(Student).filter(
        Student.student_id == alert.student_id
    ).first()

    reason = json.loads(alert.reason_json) if alert.reason_json else {}

    # Extract live factors if available from compute_dvi
    if student:
        live_data = compute_dvi(db, student)
        comps = live_data["components"]
        factors = {
            "attendance": {
                "baseline_pct": student.baseline_attendance,
                "current_pct": comps["attendance"]["current_pct"],
                "delta_pct": comps["attendance"]["delta_pct"]
            },
            "submission": {
                "baseline_delay_hrs": student.baseline_submission_delay_hrs,
                "current_delay_hrs": comps["submission"]["current_delay_hrs"],
                "delta_hrs": comps["submission"]["delta_hrs"]
            },
            "engagement": {
                "baseline_per_week": student.baseline_lms_activity_per_week,
                "current_per_week": comps["engagement"]["current_per_week"],
                "delta": comps["engagement"]["delta"]
            },
            "morning_absences": {
                "current": comps["morning_absences"]["current"],
                "baseline": comps["morning_absences"]["baseline"]
            }
        }
    else:
        factors = {}

    result = generate_explanation(
        student_name=student.name if student else "Student",
        section=student.section if student else "Unknown",
        dvi=alert.dvi_score,
        factors=factors
    )

    return result

