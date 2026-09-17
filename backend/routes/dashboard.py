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
