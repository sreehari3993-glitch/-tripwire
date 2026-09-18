"""Intervention routes — record and retrieve intervention outcomes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional

from database import get_db, Intervention, TripwireAlert, Student
from routes.auth import get_current_mentor
from routes.access import get_owned_alert, get_owned_student
from dvi_engine import compute_dvi

router = APIRouter(prefix="/interventions", tags=["interventions"])


class InterventionCreate(BaseModel):
    alert_id: int
    contact_date: Optional[str] = None
    contact_method: Optional[str] = "In-Person"  # In-Person, Video Call, Email, Phone, LMS Message
    outcome: str       # Contacted, Student requested support, Academic issue identified, Personal difficulty reported, No response, Referred to support service, Monitoring, Improved
    notes: Optional[str] = ""
    follow_up_date: Optional[str] = None
    post_dvi: Optional[float] = None


@router.post("")
def create_intervention(
    body: InterventionCreate,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    alert = get_owned_alert(db, body.alert_id, mentor)

    contact_dt = datetime.utcnow()
    if body.contact_date:
        try:
            contact_dt = datetime.fromisoformat(body.contact_date)
        except Exception:
            pass

    fu_date = None
    if body.follow_up_date:
        try:
            fu_date = date.fromisoformat(body.follow_up_date)
        except Exception:
            pass

    # Post DVI calculation if not manually given:
    # If outcome is positive, simulate a 15-point recovery reduction
    calculated_post_dvi = body.post_dvi
    if calculated_post_dvi is None:
        if body.outcome in ["Improved", "Student requested support", "Academic issue identified", "resolving", "Contacted"]:
            calculated_post_dvi = max(35.0, round(alert.dvi_score - 18.0, 1))

    intervention = Intervention(
        alert_id=body.alert_id,
        mentor_id=mentor.mentor_id,
        contact_date=contact_dt,
        contact_method=body.contact_method or "In-Person",
        outcome=body.outcome,
        notes=body.notes or "",
        follow_up_date=fu_date,
        post_dvi=calculated_post_dvi
    )
    db.add(intervention)

    # Update alert status based on outcome
    if body.outcome in ["Improved", "resolving", "no_concern"]:
        alert.status = "resolved"
    else:
        alert.status = "monitoring"

    db.commit()
    db.refresh(intervention)

    return {
        "id": intervention.id,
        "alert_id": intervention.alert_id,
        "outcome": intervention.outcome,
        "contact_method": intervention.contact_method,
        "contact_date": intervention.contact_date.isoformat(),
        "notes": intervention.notes,
        "follow_up_date": intervention.follow_up_date.isoformat() if intervention.follow_up_date else None,
        "pre_dvi": alert.dvi_score,
        "post_dvi": intervention.post_dvi,
        "alert_status": alert.status
    }


@router.get("/{alert_id}")
def get_intervention(
    alert_id: int,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    alert = get_owned_alert(db, alert_id, mentor)

    intervention = db.query(Intervention).filter(
        Intervention.alert_id == alert_id
    ).order_by(Intervention.contact_date.desc()).first()

    if not intervention:
        return {"intervention": None}

    return {
        "intervention": {
            "id": intervention.id,
            "alert_id": intervention.alert_id,
            "mentor_id": intervention.mentor_id,
            "contact_method": intervention.contact_method or "In-Person",
            "outcome": intervention.outcome,
            "contact_date": intervention.contact_date.isoformat(),
            "notes": intervention.notes,
            "follow_up_date": intervention.follow_up_date.isoformat() if intervention.follow_up_date else None,
            "pre_dvi": alert.dvi_score if alert else None,
            "post_dvi": intervention.post_dvi
        }
    }


@router.get("/student/{student_id}")
def get_student_interventions(
    student_id: str,
    db: Session = Depends(get_db),
    mentor=Depends(get_current_mentor)
):
    """Retrieve all intervention history for a given student."""
    student = get_owned_student(db, student_id, mentor)

    interventions = db.query(Intervention).join(TripwireAlert).filter(
        TripwireAlert.student_id == student.student_id
    ).order_by(Intervention.contact_date.desc()).all()

    results = []
    for inv in interventions:
        alert = db.query(TripwireAlert).filter(TripwireAlert.alert_id == inv.alert_id).first()
        results.append({
            "id": inv.id,
            "alert_id": inv.alert_id,
            "mentor_id": inv.mentor_id,
            "contact_method": inv.contact_method or "In-Person",
            "outcome": inv.outcome,
            "contact_date": inv.contact_date.isoformat(),
            "notes": inv.notes,
            "follow_up_date": inv.follow_up_date.isoformat() if inv.follow_up_date else None,
            "pre_dvi": alert.dvi_score if alert else None,
            "post_dvi": inv.post_dvi
        })

    return {"student_id": student_id, "interventions": results, "total": len(results)}
