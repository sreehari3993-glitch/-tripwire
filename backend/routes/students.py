"""Student routes — list, profile, timeline, DVI history, and dynamic data ingestion."""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import csv
import io
import json

from database import (
    get_db, Student, Attendance, LMSActivity, Assignment,
    TripwireAlert, WeeklyPulse, LeaveRecord, Intervention, FlagFeedback
)
from routes.auth import get_current_mentor
from routes.access import get_owned_student
from dvi_engine import (
    compute_dvi, compute_dvi_history, compute_counterfactual,
    W_ATTENDANCE, W_SUBMISSION, W_ENGAGEMENT, W_SERIES_EXAM, THRESHOLD_SERIES_EXAM
)

from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(prefix="/students", tags=["students"])


class StudentCreateRequest(BaseModel):
    student_id: Optional[str] = None
    name: str
    roll_no: str
    section: str
    archetype: Optional[str] = "normal"
    baseline_attendance: Optional[float] = 85.0
    baseline_submission_delay_hrs: Optional[float] = 6.0
    baseline_lms_activity_per_week: Optional[float] = 7.0
    baseline_series_exam_mark: Optional[float] = 75.0
    series_exam_mark: Optional[float] = 70.0


class SeriesExamLogRequest(BaseModel):
    series_exam_mark: float
    baseline_series_exam_mark: Optional[float] = None


class AttendanceLogRequest(BaseModel):
    date: Optional[str] = None  # YYYY-MM-DD, defaults to today
    period: Optional[int] = 1
    status: str = "present"  # present, absent, late, excused


class AssignmentLogRequest(BaseModel):
    assignment_id: Optional[str] = None
    due_date: Optional[str] = None
    submitted_at: Optional[str] = None  # None = missing


class LMSLogRequest(BaseModel):
    date: Optional[str] = None
    activity_count: int = 1


class BatchAttendanceItem(BaseModel):
    student_id: str
    status: str = "present"  # present, absent, late, excused


class BatchAttendanceRequest(BaseModel):
    date: Optional[str] = None
    period: Optional[int] = 1
    records: List[BatchAttendanceItem]


class CSVImportRequest(BaseModel):
    csv_text: str


class ResetCohortRequest(BaseModel):
    mode: str = "empty"  # "empty" or "seed"


class ExcuseRequest(BaseModel):
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    reason: str = "medical"  # medical / official / personal
    notes: Optional[str] = ""


class PulseSubmitRequest(BaseModel):
    rating: int  # 1 to 5
    stuck_on: Optional[str] = None


def recalculate_and_check_alerts(db: Session, student: Student) -> dict:
    """Recalculates DVI score and automatically manages active tripwire alerts."""
    dvi_data = compute_dvi(db, student)
    new_dvi = dvi_data["dvi"]

    existing_alert = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student.student_id,
        TripwireAlert.status.in_(["active", "monitoring"])
    ).first()

    alert_created = False
    alert_id = None

    if new_dvi >= 70.0:
        exam_drift = dvi_data["components"].get("series_exam", {}).get("score", 0.0)
        raw_exam_drift = dvi_data["components"].get("series_exam", {}).get("raw_score", exam_drift)
        if not existing_alert:
            new_alert = TripwireAlert(
                student_id=student.student_id,
                dvi_score=new_dvi,
                trigger_date=datetime.now(),
                attendance_drift=dvi_data["components"]["attendance"]["score"],
                submission_drift=dvi_data["components"]["submission"]["score"],
                engagement_drift=dvi_data["components"]["engagement"]["score"],
                series_exam_drift=exam_drift,
                raw_attendance_drift=dvi_data["components"]["attendance"].get("raw_score", dvi_data["components"]["attendance"]["score"]),
                raw_submission_drift=dvi_data["components"]["submission"].get("raw_score", dvi_data["components"]["submission"]["score"]),
                raw_engagement_drift=dvi_data["components"]["engagement"].get("raw_score", dvi_data["components"]["engagement"]["score"]),
                raw_series_exam_drift=raw_exam_drift,
                raw_dvi_score=dvi_data.get("raw_dvi", new_dvi),
                reason_json=json.dumps({
                    "attendance_delta_pct": dvi_data["components"]["attendance"].get("delta_pct", 0.0),
                    "submission_delta_hrs": dvi_data["components"]["submission"].get("delta_hrs", 0.0),
                    "engagement_delta": dvi_data["components"]["engagement"].get("delta", 0.0),
                    "series_exam_delta": dvi_data["components"].get("series_exam", {}).get("delta", 0.0),
                    "series_exam_mark": dvi_data["components"].get("series_exam", {}).get("current_mark", 70.0),
                    "auto_generated": True
                }),
                status="active",
                is_read=False
            )
            db.add(new_alert)
            db.commit()
            db.refresh(new_alert)
            alert_created = True
            alert_id = new_alert.alert_id
        else:
            existing_alert.dvi_score = new_dvi
            existing_alert.attendance_drift = dvi_data["components"]["attendance"]["score"]
            existing_alert.submission_drift = dvi_data["components"]["submission"]["score"]
            existing_alert.engagement_drift = dvi_data["components"]["engagement"]["score"]
            existing_alert.series_exam_drift = exam_drift
            existing_alert.raw_attendance_drift = dvi_data["components"]["attendance"].get("raw_score", dvi_data["components"]["attendance"]["score"])
            existing_alert.raw_submission_drift = dvi_data["components"]["submission"].get("raw_score", dvi_data["components"]["submission"]["score"])
            existing_alert.raw_engagement_drift = dvi_data["components"]["engagement"].get("raw_score", dvi_data["components"]["engagement"]["score"])
            existing_alert.raw_series_exam_drift = raw_exam_drift
            existing_alert.raw_dvi_score = dvi_data.get("raw_dvi", new_dvi)
            db.commit()
            alert_id = existing_alert.alert_id
    elif existing_alert:
        alert_id = existing_alert.alert_id
        if new_dvi < 50.0:
            existing_alert.status = "recovering"
            db.commit()

    return {
        "dvi": new_dvi,
        "status": dvi_data["status"],
        "alert_created": alert_created,
        "alert_id": alert_id,
        "components": dvi_data["components"]
    }



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
        "series_exam": f"{comps.get('series_exam', {}).get('current_mark', getattr(student, 'series_exam_mark', 70.0) or 70.0):.0f}%",
        "dvi": result["dvi"],
        "raw_dvi": result.get("raw_dvi", result["dvi"]),
        "status": result["status"],
        "velocity": result["velocity"],
        "weeks_in_status": result.get("weeks_in_status", getattr(student, "weeks_in_status", 1)),
        "baseline_confidence": result.get("baseline_confidence", "Established"),
        "is_cold_start": result.get("is_cold_start", False),
        "pulse": pulse_info,
        "last_activity": last_act_str,
        "alert_id": active_alert.alert_id if active_alert else None,
        "exam_eligibility": result.get("exam_eligibility", {})
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

    # Sort order: tripwire first, monitoring, watch, recovering, normal
    order = {"tripwire": 0, "monitoring": 1, "watch": 2, "recovering": 3, "normal": 4}
    summaries.sort(key=lambda x: (order.get(x["status"], 5), -x["dvi"]))

    return {"students": summaries, "total": len(summaries)}


@router.get("/template-csv")
def get_template_csv():
    """Returns a downloadable CSV template with standard column headers for class rosters."""
    sample_csv = "name,roll_no,section,student_id\nAravind Krishnan,CSE24101,CSE S2,STU101\nDiya Menon,CSE24102,CSE S2,STU102\nKarthik Raj,CSE24103,CSE S2,STU103\n"
    return PlainTextResponse(
        content=sample_csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tripwire_roster_template.csv"}
    )


@router.post("")
def create_student(
    body: StudentCreateRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Adds an individual student to the current mentor's roster."""
    name = body.name.strip()
    roll_no = body.roll_no.strip()
    section = body.section.strip()

    if not name or not roll_no or not section:
        raise HTTPException(status_code=400, detail="Name, Roll Number, and Section are required")

    # Generate unique ID if none provided
    if body.student_id and body.student_id.strip():
        student_id = body.student_id.strip()
    else:
        seq = int(datetime.now().timestamp() * 1000) % 1000000
        student_id = f"STU{seq:06d}"

    existing = db.query(Student).filter(Student.student_id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Student ID '{student_id}' already exists")

    student = Student(
        student_id=student_id,
        name=name,
        roll_no=roll_no,
        section=section,
        mentor_id=mentor.mentor_id,
        archetype=body.archetype or "normal",
        baseline_attendance=body.baseline_attendance or 85.0,
        baseline_submission_delay_hrs=body.baseline_submission_delay_hrs or 6.0,
        baseline_lms_activity_per_week=body.baseline_lms_activity_per_week or 7.0,
        baseline_series_exam_mark=body.baseline_series_exam_mark or 75.0,
        series_exam_mark=body.series_exam_mark or 70.0,
        baseline_confidence="Established"
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return {
        "success": True,
        "message": f"Student '{name}' added successfully.",
        "student": _student_summary(db, student)
    }


@router.post("/import-csv")
def import_students_csv(
    body: CSVImportRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Bulk imports a roster of students from CSV text."""
    csv_text = body.csv_text.strip()
    if not csv_text:
        raise HTTPException(status_code=400, detail="CSV content cannot be empty")

    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV does not contain valid headers")

    # Normalize header mapping
    header_map = {k.strip().lower(): k for k in reader.fieldnames if k}
    name_key = header_map.get("name") or header_map.get("student_name")
    roll_key = header_map.get("roll_no") or header_map.get("rollno") or header_map.get("roll")
    sec_key = header_map.get("section") or header_map.get("class") or header_map.get("batch")
    id_key = header_map.get("student_id") or header_map.get("id")

    if not name_key or not roll_key or not sec_key:
        raise HTTPException(
            status_code=400,
            detail="CSV must contain 'name', 'roll_no', and 'section' columns."
        )

    imported_students = []
    skipped_count = 0

    for idx, row in enumerate(reader, start=1):
        name = (row.get(name_key) or "").strip()
        roll = (row.get(roll_key) or "").strip()
        sec = (row.get(sec_key) or "").strip()

        if not name or not roll or not sec:
            skipped_count += 1
            continue

        raw_id = (row.get(id_key) or "").strip() if id_key else ""
        if raw_id:
            stu_id = raw_id
        else:
            seq = (int(datetime.now().timestamp() * 1000) + idx) % 1000000
            stu_id = f"STU{seq:06d}"

        # Avoid duplicate IDs
        if db.query(Student).filter(Student.student_id == stu_id).first():
            stu_id = f"{stu_id}_{idx}"

        student = Student(
            student_id=stu_id,
            name=name,
            roll_no=roll,
            section=sec,
            mentor_id=mentor.mentor_id,
            archetype="normal",
            baseline_attendance=85.0,
            baseline_submission_delay_hrs=6.0,
            baseline_lms_activity_per_week=7.0,
            baseline_series_exam_mark=75.0,
            series_exam_mark=70.0,
            baseline_confidence="Established"
        )
        db.add(student)
        imported_students.append(student)

    db.commit()

    return {
        "success": True,
        "imported_count": len(imported_students),
        "skipped_count": skipped_count,
        "message": f"Successfully imported {len(imported_students)} students."
    }


@router.get("/batch-attendance")
def get_batch_attendance(
    target_date_str: Optional[str] = Query(None, alias="date"),
    period: Optional[int] = Query(1),
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Fetches saved batch attendance records for mentor students on a specific date and period."""
    if target_date_str:
        try:
            target_date = date.fromisoformat(target_date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")
    else:
        target_date = date.today()

    period = period or 1

    mentor_students = db.query(Student).filter(
        Student.mentor_id == mentor.mentor_id
    ).all()
    student_ids = [s.student_id for s in mentor_students]

    records = {}
    if student_ids:
        att_rows = db.query(Attendance).filter(
            Attendance.student_id.in_(student_ids),
            Attendance.date == target_date,
            Attendance.period == period
        ).all()
        for r in att_rows:
            records[r.student_id] = r.status.lower()

    return {
        "success": True,
        "date": target_date.isoformat(),
        "period": period,
        "records": records,
        "total_marked": len(records)
    }


@router.post("/batch-attendance")
def batch_mark_attendance(
    body: BatchAttendanceRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Batch-marks attendance for multiple students on a specific date and updates DVIs."""
    if body.date:
        try:
            target_date = date.fromisoformat(body.date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")
    else:
        target_date = date.today()

    period = body.period or 1

    updated_count = 0
    alerts_triggered = 0

    for record in body.records:
        student = db.query(Student).filter(
            Student.student_id == record.student_id,
            Student.mentor_id == mentor.mentor_id
        ).first()
        if not student:
            continue

        # Check existing attendance for period (and clean any duplicate rows)
        existing_list = db.query(Attendance).filter(
            Attendance.student_id == student.student_id,
            Attendance.date == target_date,
            Attendance.period == period
        ).all()

        if existing_list:
            existing_list[0].status = record.status.lower()
            for dup in existing_list[1:]:
                db.delete(dup)
        else:
            att = Attendance(
                student_id=student.student_id,
                date=target_date,
                period=period,
                status=record.status.lower()
            )
            db.add(att)

        db.commit()
        updated_count += 1

        # Check real-time DVI delta
        res = recalculate_and_check_alerts(db, student)
        if res.get("alert_created"):
            alerts_triggered += 1

    return {
        "success": True,
        "updated_count": updated_count,
        "alerts_triggered": alerts_triggered,
        "date": target_date.isoformat(),
        "period": period
    }


@router.post("/reset-cohort")
def reset_cohort(
    body: ResetCohortRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Allows mentor to clear student roster or re-seed standard demonstration cohort."""
    students = db.query(Student).filter(Student.mentor_id == mentor.mentor_id).all()
    for s in students:
        alerts = db.query(TripwireAlert).filter(TripwireAlert.student_id == s.student_id).all()
        for a in alerts:
            db.query(Intervention).filter(Intervention.alert_id == a.alert_id).delete()
            db.query(FlagFeedback).filter(FlagFeedback.alert_id == a.alert_id).delete()
            db.delete(a)

        db.query(Attendance).filter(Attendance.student_id == s.student_id).delete()
        db.query(Assignment).filter(Assignment.student_id == s.student_id).delete()
        db.query(LMSActivity).filter(LMSActivity.student_id == s.student_id).delete()
        db.query(LeaveRecord).filter(LeaveRecord.student_id == s.student_id).delete()
        db.query(WeeklyPulse).filter(WeeklyPulse.student_id == s.student_id).delete()
        db.delete(s)

    db.commit()

    if body.mode == "seed":
        from seed_data import run_seed
        run_seed()
        return {"success": True, "message": "Demo cohort re-seeded successfully."}

    return {"success": True, "message": "Cohort cleared. Workspace is ready for custom students."}


@router.get("/{student_id}")
def get_student_profile(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    student = get_owned_student(db, student_id, mentor)

    result = compute_dvi(db, student)
    comps  = result["components"]
    weights = result.get("weights", {"series_exam": W_SERIES_EXAM, "attendance": W_ATTENDANCE, "submission": W_SUBMISSION, "engagement": W_ENGAGEMENT})

    active_alert = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student_id,
        TripwireAlert.status.in_(["active", "monitoring", "recovering"])
    ).first()

    # Counterfactual analysis
    cf_analysis = compute_counterfactual(db, student)

    # What Changed comparison block
    current_series = comps.get("series_exam", {}).get("current_mark", getattr(student, "series_exam_mark", 70.0) or 70.0)
    baseline_series = getattr(student, "baseline_series_exam_mark", 75.0) or 75.0
    series_delta = round(current_series - baseline_series, 1)

    att_pct_change = round(comps["attendance"]["delta_pct"], 1)
    sub_hrs_change = round(comps["submission"]["delta_hrs"], 1)
    lms_pct_change = round(
        ((comps["engagement"]["current_per_week"] - student.baseline_lms_activity_per_week) /
         max(student.baseline_lms_activity_per_week, 1.0)) * 100, 1
    )

    what_changed = {
        "series_exam": {
            "label": "Series Exam Mark",
            "baseline": baseline_series,
            "current": current_series,
            "change": series_delta,
            "formatted_change": f"{series_delta:+.1f}%",
            "unit": "%",
            "threshold": THRESHOLD_SERIES_EXAM,
            "below_threshold": current_series < THRESHOLD_SERIES_EXAM,
            "negative": series_delta < -5 or current_series < THRESHOLD_SERIES_EXAM
        },
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
            "series_exam_mark": getattr(student, "baseline_series_exam_mark", 75.0) or 75.0,
            "attendance_pct": student.baseline_attendance,
            "submission_delay_hrs": student.baseline_submission_delay_hrs,
            "lms_per_week": student.baseline_lms_activity_per_week,
            "morning_absences_per_week": student.baseline_morning_absences_per_week
        },
        "signals": {
            "series_exam": comps.get("series_exam", {}),
            "attendance": comps["attendance"],
            "submission": comps["submission"],
            "engagement": comps["engagement"],
            "morning_absences": comps["morning_absences"]
        },
        "what_changed": what_changed,
        "counterfactual": cf_analysis,
        "weights": weights,
        "dvi_breakdown": {
            "series_exam_component": round(comps.get("series_exam", {}).get("score", 0.0) * weights.get("series_exam", W_SERIES_EXAM), 1),
            "attendance_component": round(comps["attendance"]["score"] * weights.get("attendance", W_ATTENDANCE), 1),
            "submission_component": round(comps["submission"]["score"] * weights.get("submission", W_SUBMISSION), 1),
            "engagement_component": round(comps["engagement"]["score"] * weights.get("engagement", W_ENGAGEMENT), 1),
        },
        "exam_eligibility": result.get("exam_eligibility", {}),
        "academic_thresholds": result.get("academic_thresholds", {}),
        "excused_leaves": excused_leaves,
        "alert_id": active_alert.alert_id if active_alert else None
    }


@router.delete("/{student_id}")
def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Deletes an individual student and cascades removal of associated telemetry and alerts."""
    student = get_owned_student(db, student_id, mentor)
    name = student.name

    alerts = db.query(TripwireAlert).filter(TripwireAlert.student_id == student_id).all()
    for a in alerts:
        db.query(Intervention).filter(Intervention.alert_id == a.alert_id).delete()
        db.query(FlagFeedback).filter(FlagFeedback.alert_id == a.alert_id).delete()
        db.delete(a)

    db.query(Attendance).filter(Attendance.student_id == student_id).delete()
    db.query(Assignment).filter(Assignment.student_id == student_id).delete()
    db.query(LMSActivity).filter(LMSActivity.student_id == student_id).delete()
    db.query(LeaveRecord).filter(LeaveRecord.student_id == student_id).delete()
    db.query(WeeklyPulse).filter(WeeklyPulse.student_id == student_id).delete()

    db.delete(student)
    db.commit()

    return {"success": True, "message": f"Student '{name}' ({student_id}) deleted successfully."}


@router.post("/{student_id}/attendance")
def log_student_attendance(
    student_id: str,
    body: AttendanceLogRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Logs an attendance record for a student and instantly recalculates their DVI."""
    student = get_owned_student(db, student_id, mentor)
    target_date = date.fromisoformat(body.date) if body.date else date.today()
    period = body.period or 1
    status = body.status.lower()

    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == target_date,
        Attendance.period == period
    ).first()

    if existing:
        existing.status = status
    else:
        att = Attendance(
            student_id=student_id,
            date=target_date,
            period=period,
            status=status
        )
        db.add(att)

    db.commit()

    recalc = recalculate_and_check_alerts(db, student)
    return {
        "success": True,
        "message": f"Attendance recorded as '{status}'.",
        "dvi": recalc["dvi"],
        "status": recalc["status"],
        "alert_created": recalc["alert_created"],
        "alert_id": recalc["alert_id"]
    }


@router.post("/{student_id}/assignments")
def log_student_assignment(
    student_id: str,
    body: AssignmentLogRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Logs assignment submission timing and instantly recalculates DVI."""
    student = get_owned_student(db, student_id, mentor)

    due_dt = datetime.fromisoformat(body.due_date) if body.due_date else datetime.now() - timedelta(hours=12)
    submitted_dt = datetime.fromisoformat(body.submitted_at) if body.submitted_at else None
    asg_id = body.assignment_id or f"ASG_{int(datetime.now().timestamp()) % 10000}"

    asg = Assignment(
        student_id=student_id,
        assignment_id=asg_id,
        due_date=due_dt,
        submitted_at=submitted_dt
    )
    db.add(asg)
    db.commit()

    recalc = recalculate_and_check_alerts(db, student)
    return {
        "success": True,
        "message": "Assignment submission logged.",
        "dvi": recalc["dvi"],
        "status": recalc["status"],
        "alert_created": recalc["alert_created"],
        "alert_id": recalc["alert_id"]
    }


@router.post("/{student_id}/lms")
def log_student_lms(
    student_id: str,
    body: LMSLogRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Logs LMS login/access count for a date and updates DVI."""
    student = get_owned_student(db, student_id, mentor)
    target_date = date.fromisoformat(body.date) if body.date else date.today()

    existing = db.query(LMSActivity).filter(
        LMSActivity.student_id == student_id,
        LMSActivity.date == target_date
    ).first()

    if existing:
        existing.activity_count = max(0, body.activity_count)
    else:
        lms = LMSActivity(
            student_id=student_id,
            date=target_date,
            activity_count=max(0, body.activity_count)
        )
        db.add(lms)

    db.commit()

    recalc = recalculate_and_check_alerts(db, student)
    return {
        "success": True,
        "message": "LMS activity logged.",
        "dvi": recalc["dvi"],
        "status": recalc["status"],
        "alert_created": recalc["alert_created"],
        "alert_id": recalc["alert_id"]
    }


@router.post("/{student_id}/series-exam")
def log_student_series_exam(
    student_id: str,
    body: SeriesExamLogRequest,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Updates student series exam mark and recalculates DVI."""
    student = get_owned_student(db, student_id, mentor)
    student.series_exam_mark = max(0.0, min(100.0, body.series_exam_mark))
    if body.baseline_series_exam_mark is not None:
        student.baseline_series_exam_mark = max(0.0, min(100.0, body.baseline_series_exam_mark))
    db.commit()
    recalc = recalculate_and_check_alerts(db, student)
    return {
        "success": True,
        "message": f"Series exam mark updated to {student.series_exam_mark}%.",
        "dvi": recalc["dvi"],
        "status": recalc["status"],
        "alert_created": recalc["alert_created"],
        "alert_id": recalc["alert_id"],
        "series_exam_mark": student.series_exam_mark
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
    student = get_owned_student(db, student_id, mentor)

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
    student = get_owned_student(db, student_id, mentor)

    history = compute_dvi_history(db, student, days=days)
    return {"student_id": student_id, "history": history}


@router.get("/{student_id}/timeline")
def get_student_timeline(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Return a chronological list of behavioral events for the What Changed? view."""
    student = get_owned_student(db, student_id, mentor)

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
    student = get_owned_student(db, student_id, mentor)

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
    student = get_owned_student(db, student_id, mentor)
    pulses = db.query(WeeklyPulse).filter(
        WeeklyPulse.student_id == student.student_id
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


@router.post("/{student_id}/simulate-drift")
def simulate_student_drift(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """
    P1 Pitch Simulator: Injects realistic behavioral drift telemetry.
    - Adds multiple missed lectures and morning absences over recent days
    - Injects delayed assignment submission (44h late)
    - Drops LMS activity
    - Sets qualitative pulse to 2/5
    - Recalculates DVI and automatically triggers a live TripwireAlert in tripwire.db
    """
    student = get_owned_student(db, student_id, mentor)
    today = date.today()

    # 1. Inject absences for last 7 days (all 6 periods to ensure attendance collapses)
    for i in range(1, 8):
        d = today - timedelta(days=i)
        for p in range(1, 7):
            existing_att = db.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.date == d,
                Attendance.period == p
            ).first()
            if existing_att:
                existing_att.status = "absent"
            else:
                db.add(Attendance(
                    student_id=student_id,
                    date=d,
                    period=p,
                    status="absent"
                ))

    # 2. Inject 3 delayed assignments so median delay of last 5 is heavily delayed (48h, 54h, 64h late)
    for idx, hrs in enumerate([48, 54, 64]):
        sim_asg_id = f"SIM_ASG_{idx}_{student_id}"
        existing_asg = db.query(Assignment).filter(
            Assignment.student_id == student_id,
            Assignment.assignment_id == sim_asg_id
        ).first()
        due_time = datetime.combine(today - timedelta(days=idx + 2), datetime.min.time()) + timedelta(hours=17)
        sub_time = due_time + timedelta(hours=hrs)
        if existing_asg:
            existing_asg.due_date = due_time
            existing_asg.submitted_at = sub_time
        else:
            db.add(Assignment(
                student_id=student_id,
                assignment_id=sim_asg_id,
                due_date=due_time,
                submitted_at=sub_time
            ))

    # 3. Drop LMS activity
    for i in range(7):
        d = today - timedelta(days=i)
        existing_lms = db.query(LMSActivity).filter(
            LMSActivity.student_id == student_id,
            LMSActivity.date == d
        ).first()
        if existing_lms:
            existing_lms.activity_count = 0
        else:
            db.add(LMSActivity(
                student_id=student_id,
                date=d,
                activity_count=0
            ))

    # 4. Self-reported pulse drop
    student.weekly_pulse_score = 2
    student.weekly_pulse_note = "Simulated: Struggling with concurrent lab deadlines and morning commute"
    student.weekly_pulse_date = today

    # 4b. Drop series exam mark below 45% threshold
    student.series_exam_mark = 34.0

    # Ensure prior drift anchor exists so EWMA models a sustained multi-week crisis for any student
    prev_alert = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student.student_id
    ).order_by(TripwireAlert.trigger_date.desc()).first()

    if not prev_alert or prev_alert.attendance_drift == 0:
        if not prev_alert:
            anchor = TripwireAlert(
                student_id=student_id,
                dvi_score=74.0,
                trigger_date=datetime.now() - timedelta(days=7),
                attendance_drift=75.0,
                submission_drift=75.0,
                engagement_drift=70.0,
                series_exam_drift=75.0,
                raw_attendance_drift=75.0,
                raw_submission_drift=75.0,
                raw_engagement_drift=70.0,
                raw_series_exam_drift=75.0,
                raw_dvi_score=74.0,
                reason_json=json.dumps({"sim_anchor": True, "auto_generated": True}),
                status="active"
            )
            db.add(anchor)
        else:
            prev_alert.attendance_drift = 75.0
            prev_alert.submission_drift = 75.0
            prev_alert.engagement_drift = 70.0
            prev_alert.series_exam_drift = 75.0
            prev_alert.raw_attendance_drift = 75.0
            prev_alert.raw_submission_drift = 75.0
            prev_alert.raw_engagement_drift = 70.0
            prev_alert.raw_series_exam_drift = 75.0
            prev_alert.status = "active"

    db.commit()

    # 5. Live recalculation and alert trigger
    recalc = recalculate_and_check_alerts(db, student)

    return {
        "success": True,
        "message": f"Simulated behavioral drift for {student.name}.",
        "dvi": recalc["dvi"],
        "status": recalc["status"],
        "alert_created": recalc["alert_created"],
        "alert_id": recalc["alert_id"],
        "summary": f"Injected 7 days of missed lectures, 3 delayed assignments, and 0 LMS logins. DVI reached {recalc['dvi']}."
    }


@router.post("/{student_id}/simulate-recovery")
def simulate_student_recovery(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """
    P1 Pitch Simulator: Simulates faculty check-in intervention and behavioral rebound.
    - Records an in-person mentorship session with action points
    - Restores attendance to 100% present for recent 14 days
    - Sets assignment submissions on-time
    - Increases LMS activity
    - Recalculates DVI down into recovery/normal range and resolves active alert
    """
    student = get_owned_student(db, student_id, mentor)
    today = date.today()

    # 1. Record an intervention
    active_alert = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student_id,
        TripwireAlert.status.in_(["active", "monitoring"])
    ).order_by(TripwireAlert.trigger_date.desc()).first()

    if not active_alert:
        active_alert = db.query(TripwireAlert).filter(
            TripwireAlert.student_id == student_id
        ).order_by(TripwireAlert.trigger_date.desc()).first()

    alert_id = active_alert.alert_id if active_alert else None
    if alert_id:
        intervention = Intervention(
            alert_id=alert_id,
            mentor_id=mentor.mentor_id,
            contact_date=datetime.now(),
            contact_method="In-Person Check-in (Office)",
            outcome="Improved",
            notes="Met with student. Provided 48hr extension on lab report and connected with S7 peer tutor. Student re-engaged.",
            follow_up_date=today + timedelta(days=7),
            post_dvi=45.0
        )
        db.add(intervention)
        active_alert.status = "resolved"
        active_alert.attendance_drift = 0.0
        active_alert.submission_drift = 0.0
        active_alert.engagement_drift = 0.0
        active_alert.series_exam_drift = 0.0
        active_alert.raw_attendance_drift = 0.0
        active_alert.raw_submission_drift = 0.0
        active_alert.raw_engagement_drift = 0.0
        active_alert.raw_series_exam_drift = 0.0
        active_alert.dvi_score = 45.0

    student.series_exam_mark = 74.0

    # 2. Inject positive attendance rebound (all present for last 14 days)
    for i in range(1, 15):
        d = today - timedelta(days=i)
        for p in range(1, 7):
            existing_att = db.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.date == d,
                Attendance.period == p
            ).first()
            if existing_att:
                existing_att.status = "present"
            else:
                db.add(Attendance(
                    student_id=student_id,
                    date=d,
                    period=p,
                    status="present"
                ))

    # 3. Simulated assignments submitted on time
    sim_asgs = db.query(Assignment).filter(
        Assignment.student_id == student_id,
        Assignment.assignment_id.like("SIM_%")
    ).all()
    for asg in sim_asgs:
        asg.submitted_at = asg.due_date - timedelta(hours=2)

    # 4. Boost LMS activity
    for i in range(7):
        d = today - timedelta(days=i)
        existing_lms = db.query(LMSActivity).filter(
            LMSActivity.student_id == student_id,
            LMSActivity.date == d
        ).first()
        if existing_lms:
            existing_lms.activity_count = 6
        else:
            db.add(LMSActivity(
                student_id=student_id,
                date=d,
                activity_count=6
            ))

    # 5. Pulse improvement
    student.weekly_pulse_score = 4
    student.weekly_pulse_note = "Peer tutor session was very helpful, feeling back on track"
    student.weekly_pulse_date = today

    db.commit()

    # 6. Recalculate DVI
    recalc = recalculate_and_check_alerts(db, student)

    if active_alert and recalc["dvi"] < 55.0:
        active_alert.status = "recovering"
        db.commit()

    return {
        "success": True,
        "message": f"Simulated mentorship intervention and recovery for {student.name}.",
        "dvi": recalc["dvi"],
        "status": "recovering" if recalc["dvi"] < 60.0 else recalc["status"],
        "alert_id": alert_id,
        "summary": f"Recorded faculty intervention and attendance rebound. DVI decreased to {recalc['dvi']}."
    }


@router.post("/{student_id}/simulate-reset")
def simulate_student_reset(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """
    P1 Pitch Simulator: Cleans up simulation records and restores baseline standing.
    """
    student = get_owned_student(db, student_id, mentor)

    # Remove simulated assignments
    db.query(Assignment).filter(
        Assignment.student_id == student_id,
        Assignment.assignment_id.like("SIM_%")
    ).delete()

    # Remove simulated alerts
    auto_alerts = db.query(TripwireAlert).filter(
        TripwireAlert.student_id == student_id,
        TripwireAlert.reason_json.like('%"auto_generated": true%')
    ).all()
    for a in auto_alerts:
        db.query(Intervention).filter(Intervention.alert_id == a.alert_id).delete()
        db.query(FlagFeedback).filter(FlagFeedback.alert_id == a.alert_id).delete()
        db.delete(a)

    # Reset attendance for last 14 days to present
    today = date.today()
    for i in range(15):
        d = today - timedelta(days=i)
        for att in db.query(Attendance).filter(Attendance.student_id == student_id, Attendance.date == d).all():
            att.status = "present"

    # Reset LMS
    for i in range(7):
        d = today - timedelta(days=i)
        for lms in db.query(LMSActivity).filter(LMSActivity.student_id == student_id, LMSActivity.date == d).all():
            lms.activity_count = max(1, int(student.baseline_lms_activity_per_week / 7))

    # Reset pulse
    student.weekly_pulse_score = 4
    student.weekly_pulse_note = "Regular coursework pace"
    student.weekly_pulse_date = today

    db.commit()

    recalc = recalculate_and_check_alerts(db, student)

    return {
        "success": True,
        "message": f"Simulation reset. {student.name} restored to baseline standing.",
        "dvi": recalc["dvi"],
        "status": recalc["status"]
    }


