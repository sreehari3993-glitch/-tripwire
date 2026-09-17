"""Student routes — list, profile, timeline, DVI history."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta

from database import get_db, Student, Attendance, LMSActivity, Assignment, TripwireAlert, WeeklyPulse, LeaveRecord
from routes.auth import get_current_mentor
from dvi_engine import compute_dvi, compute_dvi_history, compute_counterfactual

from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/students", tags=["students"])


class ExcuseRequest(BaseModel):
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    reason: str = "medical"  # medical / official / personal
    notes: Optional[str] = ""


class PulseSubmitRequest(BaseModel):
    rating: int  # 1 to 5
    stuck_on: Optional[str] = None


def _student_summary(db: Session, student: Student) -> dict:
    result = compute_dvi(db, student)
    comps = result["components"]
    active_alert = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student.student_id,
        TripwireAlert.status.in_(["active", "monitoring"])
    ).first()

    # Get last activity date
    last_att = db.query(Attendance).filter(
        Attendance.student_id == student.student_id
    ).order_by(Attendance.date.desc()).first()

    last_act_str = last_att.date.strftime("%d %b") if last_att else "15 Sep"

    pulse_info = {
        "rating": student.weekly_pulse_score,
        "stuck_on": student.weekly_pulse_note,
        "date": student.weekly_pulse_date.isoformat() if student.weekly_pulse_date else None
    } if student.weekly_pulse_score else None

    return {
        "student_id": student.student_id,
        "name": student.name,
        "section": student.section,
        "roll_no": student.roll_no,
        "archetype": getattr(student, "archetype", "normal") or "normal",
        "attendance": f"{comps['attendance']['current_pct']:.0f}%",
        "assignment_delay": f"{comps['submission']['current_delay_hrs']:.0f}h",
        "lms_engagement": f"{comps['engagement']['current_per_week']:.0f}/wk",
        "dvi": result["dvi"],
        "raw_dvi": result.get("raw_dvi", result["dvi"]),
        "status": result["status"],
        "velocity": result["velocity"],
        "weeks_in_status": result.get("weeks_in_status", getattr(student, "weeks_in_status", 1)),
        "baseline_confidence": result.get("baseline_confidence", "Established"),
        "is_cold_start": result.get("is_cold_start", False),
        "pulse": pulse_info,
        "last_activity": last_act_str,
        "alert_id": active_alert.alert_id if active_alert else None
    }



@router.get("")
def list_students(
    status_filter: str = Query(default="all", alias="status"),
    search: str = Query(default=""),
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    students = db.query(Student).filter(Student.mentor_id == mentor.mentor_id).all()
    summaries = [_student_summary(db, s) for s in students]

    if status_filter != "all":
        summaries = [s for s in summaries if s["status"].lower() == status_filter.lower()]
    if search:
        q = search.lower()
        summaries = [s for s in summaries if q in s["name"].lower() or q in s["roll_no"].lower() or q in s["student_id"].lower()]

    # Sort order: tripwire first, monitoring, recovering, normal
    order = {"tripwire": 0, "monitoring": 1, "recovering": 2, "normal": 3}
    summaries.sort(key=lambda x: (order.get(x["status"], 4), -x["dvi"]))

    return {"students": summaries, "total": len(summaries)}


@router.get("/{student_id}")
def get_student_profile(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = compute_dvi(db, student)
    comps  = result["components"]

    active_alert = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student_id,
        TripwireAlert.status.in_(["active", "monitoring", "recovering"])
    ).first()

    # Counterfactual analysis
    cf_analysis = compute_counterfactual(db, student)

    # What Changed comparison block
    att_pct_change = round(comps["attendance"]["delta_pct"], 1)
    sub_hrs_change = round(comps["submission"]["delta_hrs"], 1)
    lms_pct_change = round(
        ((comps["engagement"]["current_per_week"] - student.baseline_lms_activity_per_week) /
         max(student.baseline_lms_activity_per_week, 1.0)) * 100, 1
    )

    what_changed = {
        "attendance": {
            "label": "Attendance Rate",
            "baseline": student.baseline_attendance,
            "current": comps["attendance"]["current_pct"],
            "change": att_pct_change,
            "formatted_change": f"{att_pct_change:+.1f}%",
            "unit": "%",
            "negative": att_pct_change < -5
        },
        "submission_delay": {
            "label": "Assignment Delay",
            "baseline": student.baseline_submission_delay_hrs,
            "current": comps["submission"]["current_delay_hrs"],
            "change": sub_hrs_change,
            "formatted_change": f"{sub_hrs_change:+.1f}h",
            "unit": "h",
            "negative": sub_hrs_change > 5
        },
        "lms_activity": {
            "label": "LMS Activity",
            "baseline": student.baseline_lms_activity_per_week,
            "current": comps["engagement"]["current_per_week"],
            "change": lms_pct_change,
            "formatted_change": f"{lms_pct_change:+.1f}%",
            "unit": "/wk",
            "negative": lms_pct_change < -20
        }
    }

    # Check leaves
    leaves = db.query(LeaveRecord).filter(
        LeaveRecord.student_id == student_id,
        LeaveRecord.approved == True
    ).all()
    excused_leaves = [{
        "id": l.id,
        "start": l.start_date.isoformat(),
        "end": l.end_date.isoformat(),
        "reason": l.reason
    } for l in leaves]

    pulse_info = {
        "rating": student.weekly_pulse_score,
        "stuck_on": student.weekly_pulse_note,
        "date": student.weekly_pulse_date.isoformat() if student.weekly_pulse_date else None
    } if student.weekly_pulse_score else None

    return {
        "student_id": student.student_id,
        "name": student.name,
        "section": student.section,
        "roll_no": student.roll_no,
        "mentor_id": student.mentor_id,
        "archetype": getattr(student, "archetype", "normal") or "normal",
        "dvi": result["dvi"],
        "raw_dvi": result.get("raw_dvi", result["dvi"]),
        "smoothed_dvi": result.get("smoothed_dvi", result["dvi"]),
        "status": result["status"],
        "velocity": result["velocity"],
        "weeks_in_status": result.get("weeks_in_status", getattr(student, "weeks_in_status", 1)),
        "baseline_confidence": result.get("baseline_confidence", "Established"),
        "is_cold_start": result.get("is_cold_start", False),
        "weeks_of_data": getattr(student, "weeks_of_data", 6.0),
        "smoothing": result.get("smoothing", {}),
        "hysteresis": result.get("hysteresis", {}),
        "pulse": pulse_info,
        "baselines": {
            "attendance_pct": student.baseline_attendance,
            "submission_delay_hrs": student.baseline_submission_delay_hrs,
            "lms_per_week": student.baseline_lms_activity_per_week,
            "morning_absences_per_week": student.baseline_morning_absences_per_week
        },
        "signals": {
            "attendance": comps["attendance"],
            "submission": comps["submission"],
            "engagement": comps["engagement"],
            "morning_absences": comps["morning_absences"]
        },
        "what_changed": what_changed,
        "counterfactual": cf_analysis,
        "dvi_breakdown": {
            "attendance_component": round(comps["attendance"]["score"] * 0.40, 1),
            "submission_component": round(comps["submission"]["score"] * 0.35, 1),
            "engagement_component": round(comps["engagement"]["score"] * 0.25, 1),
        },
        "excused_leaves": excused_leaves,
        "alert_id": active_alert.alert_id if active_alert else None
    }



@router.post("/{student_id}/excuse")
def mark_student_excuse(
    student_id: str,
    body: ExcuseRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """
    Human override endpoint: Allows faculty to mark a date range as excused leave,
    excluding those dates from DVI attendance penalty.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    try:
        s_date = date.fromisoformat(body.start_date)
        e_date = date.fromisoformat(body.end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    leave = LeaveRecord(
        student_id=student_id,
        start_date=s_date,
        end_date=e_date,
        reason=body.reason,
        approved=True
    )
    db.add(leave)

    # If student has an active alert, update excused_flag
    alert = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student_id,
        TripwireAlert.status == "active"
    ).first()
    if alert:
        alert.excused_flag = True

    db.commit()

    # Recalculate DVI
    new_dvi_data = compute_dvi(db, student)

    return {
        "success": True,
        "message": "Human override applied: Leave period marked as EXCUSED.",
        "note": "Tripwire supports human override because behavioral signals can have legitimate explanations.",
        "leave_id": leave.id,
        "new_dvi": new_dvi_data["dvi"],
        "new_status": new_dvi_data["status"]
    }



@router.get("/{student_id}/dvi-history")
def get_dvi_history(
    student_id: str,
    days: int = Query(default=28, ge=7, le=90),
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    history = compute_dvi_history(db, student, days=days)
    return {"student_id": student_id, "history": history}


@router.get("/{student_id}/timeline")
def get_student_timeline(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Return a chronological list of behavioral events for the What Changed? view."""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    events = []

    # Attendance events (absences only)
    absences = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date >= date(2026, 9, 1),
        Attendance.status == "absent"
    ).order_by(Attendance.date).all()

    absence_by_date: dict[date, int] = {}
    for a in absences:
        absence_by_date[a.date] = absence_by_date.get(a.date, 0) + 1

    for d, count in absence_by_date.items():
        morning = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.date == d,
            Attendance.period.in_([1, 2]),
            Attendance.status == "absent"
        ).count()
        label = f"Missed {count} period(s)"
        if morning > 0:
            label += f" (incl. {morning} morning)"
        events.append({
            "date": d.isoformat(),
            "type": "attendance",
            "severity": "high" if count >= 4 else "medium" if count >= 2 else "low",
            "label": label
        })

    # Assignment events
    assignments = db.query(Assignment).filter(
        Assignment.student_id == student_id,
        Assignment.assignment_id.like("SEP%")
    ).order_by(Assignment.due_date).all()

    for a in assignments:
        if a.submitted_at is None:
            events.append({
                "date": (a.due_date + timedelta(days=1)).date().isoformat(),
                "type": "assignment",
                "severity": "high",
                "label": f"{a.assignment_id}: Not submitted"
            })
        else:
            delay = (a.submitted_at - a.due_date).total_seconds() / 3600
            baseline = student.baseline_submission_delay_hrs
            if delay > baseline * 2:
                sev = "high" if delay > baseline * 4 else "medium"
                events.append({
                    "date": a.submitted_at.date().isoformat(),
                    "type": "assignment",
                    "severity": sev,
                    "label": f"{a.assignment_id}: Submitted {delay:.0f} hrs late (baseline: {baseline:.0f} hrs)"
                })

    # LMS events (low activity days)
    lms_records = db.query(LMSActivity).filter(
        LMSActivity.student_id == student_id,
        LMSActivity.date >= date(2026, 9, 1)
    ).order_by(LMSActivity.date).all()

    baseline_daily = student.baseline_lms_activity_per_week / 7
    for lms in lms_records:
        if lms.activity_count == 0 and baseline_daily > 0.5:
            events.append({
                "date": lms.date.isoformat(),
                "type": "lms",
                "severity": "medium",
                "label": "No LMS activity recorded"
            })

    # Tripwire event
    alert = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student_id,
        TripwireAlert.status == "active"
    ).first()
    if alert:
        events.append({
            "date": alert.trigger_date.date().isoformat(),
            "type": "tripwire",
            "severity": "critical",
            "label": f"🚨 TRIPWIRE triggered (DVI: {alert.dvi_score:.0f})"
        })

    # Sort by date
    events.sort(key=lambda x: x["date"])
    return {"student_id": student_id, "events": events}


@router.post("/{student_id}/pulse")
def submit_student_pulse(
    student_id: str,
    body: PulseSubmitRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """
    Records lightweight weekly self-reported pulse (1-5 emoji scale + optional free text).
    Exposed separately to mentors as corroborating/contradicting qualitative evidence.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    today = date.today()
    pulse = WeeklyPulse(
        student_id=student_id,
        week_date=today,
        rating=body.rating,
        stuck_on=body.stuck_on
    )
    db.add(pulse)

    student.weekly_pulse_score = body.rating
    student.weekly_pulse_note = body.stuck_on
    student.weekly_pulse_date = today
    db.commit()

    return {
        "success": True,
        "message": "Weekly self-reported pulse logged successfully.",
        "rating": body.rating,
        "stuck_on": body.stuck_on,
        "date": today.isoformat()
    }


@router.get("/{student_id}/pulse")
def get_student_pulses(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    pulses = db.query(WeeklyPulse).filter(
        WeeklyPulse.student_id == student_id
    ).order_by(WeeklyPulse.week_date.desc()).all()

    return {
        "student_id": student_id,
        "pulses": [
            {
                "id": p.id,
                "date": p.week_date.isoformat(),
                "rating": p.rating,
                "stuck_on": p.stuck_on
            } for p in pulses
        ]
    }

