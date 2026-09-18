"""Dashboard summary route."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db, Student, TripwireAlert, Intervention
from routes.auth import get_current_mentor
from dvi_engine import compute_dvi

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db), mentor=Depends(get_current_mentor)):
    students = db.query(Student).filter(Student.mentor_id == mentor.mentor_id).all()

    normal_count     = 0
    monitoring_count = 0
    tripwire_count   = 0
    recovering_count = 0
    resolved_count   = db.query(Intervention).count()

    distribution = {
        "0_20": 0,
        "21_40": 0,
        "41_60": 0,
        "61_80": 0,
        "81_100": 0
    }

    student_summaries = []

    for student in students:
        result = compute_dvi(db, student)
        s = result["status"]
        dvi = result["dvi"]

        if s == "tripwire":
            tripwire_count += 1
        elif s == "recovering":
            recovering_count += 1
        elif s == "monitoring":
            monitoring_count += 1
        else:
            normal_count += 1

        if dvi <= 20:
            distribution["0_20"] += 1
        elif dvi <= 40:
            distribution["21_40"] += 1
        elif dvi <= 60:
            distribution["41_60"] += 1
        elif dvi <= 80:
            distribution["61_80"] += 1
        else:
            distribution["81_100"] += 1

        student_summaries.append({
            "student_id": student.student_id,
            "name": student.name,
            "dvi": dvi,
            "status": s
        })

    # Recent alerts
    recent_alerts = db.query(TripwireAlert).filter(
        TripwireAlert.status == "active"
    ).order_by(TripwireAlert.trigger_date.desc()).limit(5).all()

    return {
        "total_students": len(students),
        "normal": normal_count,
        "monitoring": monitoring_count,
        "tripwire": tripwire_count,
        "recovering": recovering_count,
        "resolved_interventions": resolved_count,
        "distribution": distribution,
        "recent_alerts_count": len(recent_alerts),
        "prototype_thresholds": {
            "tripwire": 70,
            "monitoring": 50,
            "normal": 0,
            "disclaimer": "Prototype threshold — decision-support indicator, not a diagnostic verdict."
        }
    }


from datetime import date, timedelta

@router.get("/cohort-heatmap")
def get_cohort_heatmap(
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """
    Returns a weekly DVI behavioral matrix for the entire cohort across the last 4 weeks.
    Enables instant visual detection of drift velocity across individual students.
    """
    students = db.query(Student).filter(Student.mentor_id == mentor.mentor_id).all()
    today = date.today()

    checkpoints = [
        ("Week -3", today - timedelta(days=21)),
        ("Week -2", today - timedelta(days=14)),
        ("Week -1", today - timedelta(days=7)),
        ("Current", today)
    ]

    heatmap_data = []

    for student in students:
        weekly = []
        for label, ref_date in checkpoints:
            res = compute_dvi(db, student, ref_date=ref_date)
            weekly.append({
                "week": label,
                "dvi": round(res["dvi"], 1),
                "status": res["status"]
            })

        cur_res = weekly[-1]
        heatmap_data.append({
            "student_id": student.student_id,
            "name": student.name,
            "roll_no": student.roll_no,
            "section": student.section,
            "archetype": getattr(student, "archetype", "normal") or "normal",
            "current_status": cur_res["status"],
            "current_dvi": cur_res["dvi"],
            "weekly_dvi": weekly
        })

    # Sort: Tripwire first, then monitoring, recovering, normal; then descending DVI
    order = {"tripwire": 0, "monitoring": 1, "recovering": 2, "normal": 3}
    heatmap_data.sort(key=lambda x: (order.get(x["current_status"], 4), -x["current_dvi"]))

    return {
        "columns": [c[0] for c in checkpoints],
        "total_students": len(heatmap_data),
        "students": heatmap_data
    }
