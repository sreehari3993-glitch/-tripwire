"""
Access control helpers to enforce ownership and mitigate IDOR vulnerabilities.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database import Student, TripwireAlert, Mentor


def get_owned_student(db: Session, student_id: str, mentor: Mentor) -> Student:
    """
    Retrieve student ensuring they belong to the requesting mentor.
    Raises 404 (not 403) to prevent leaking the existence of other mentors' students.
    """
    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.mentor_id == mentor.mentor_id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student


def get_owned_alert(db: Session, alert_id: int, mentor: Mentor) -> TripwireAlert:
    """
    Retrieve alert ensuring the underlying student belongs to the requesting mentor.
    Raises 404 (not 403) to prevent leaking the existence of other mentors' alerts.
    """
    alert = db.query(TripwireAlert).join(
        Student, TripwireAlert.student_id == Student.student_id
    ).filter(
        TripwireAlert.alert_id == alert_id,
        Student.mentor_id == mentor.mentor_id
    ).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return alert
