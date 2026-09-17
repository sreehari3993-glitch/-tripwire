"""
Tripwire Database Models — SQLAlchemy ORM
"""
from sqlalchemy import (
    create_engine, Column, String, Integer, Float,
    Boolean, DateTime, Date, Text, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tripwire.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────

class Mentor(Base):
    __tablename__ = "mentors"
    mentor_id  = Column(String, primary_key=True)
    name       = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    department = Column(String, default="Computer Science")
    students   = relationship("Student", back_populates="mentor")
    interventions = relationship("Intervention", back_populates="mentor")
    feedbacks  = relationship("FlagFeedback", back_populates="mentor")


class Student(Base):
    __tablename__ = "students"
    student_id   = Column(String, primary_key=True)   # e.g. "CSE24001"
    name         = Column(String, nullable=False)
    section      = Column(String, nullable=False)      # "CSE S2"
    roll_no      = Column(String, nullable=False)
    mentor_id    = Column(String, ForeignKey("mentors.mentor_id"))
    archetype    = Column(String, default="normal")
    weeks_in_status = Column(Integer, default=2)
    weeks_of_data   = Column(Float, default=6.0)
    baseline_confidence = Column(String, default="Established")  # Established vs Building (Cold-Start)
    
    # Lightweight self-report pulse signal (corroborating qualitative evidence)
    weekly_pulse_score = Column(Integer, nullable=True)  # 1-5 emoji scale
    weekly_pulse_note  = Column(String, nullable=True)   # "stuck_on" free text
    weekly_pulse_date  = Column(Date, nullable=True)

    # Baseline metrics (computed from Aug 1–31 seed data)
    baseline_attendance               = Column(Float, default=85.0)   # %
    baseline_submission_delay_hrs     = Column(Float, default=6.0)    # median hours
    baseline_lms_activity_per_week    = Column(Float, default=7.0)    # avg logins/week
    baseline_morning_absences_per_week = Column(Float, default=0.2)   # avg per week

    mentor       = relationship("Mentor", back_populates="students")
    attendance   = relationship("Attendance", back_populates="student")
    assignments  = relationship("Assignment", back_populates="student")
    lms_activity = relationship("LMSActivity", back_populates="student")
    alerts       = relationship("TripwireAlert", back_populates="student")
    leaves       = relationship("LeaveRecord", back_populates="student")
    pulses       = relationship("WeeklyPulse", back_populates="student")


class Attendance(Base):
    __tablename__ = "attendance"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    date       = Column(Date, nullable=False)
    period     = Column(Integer, nullable=False)   # 1–6
    status     = Column(String, nullable=False)    # present / absent / excused
    student    = relationship("Student", back_populates="attendance")


class Assignment(Base):
    __tablename__ = "assignments"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    student_id     = Column(String, ForeignKey("students.student_id"), nullable=False)
    assignment_id  = Column(String, nullable=False)
    due_date       = Column(DateTime, nullable=False)
    submitted_at   = Column(DateTime, nullable=True)   # null = not submitted
    student        = relationship("Student", back_populates="assignments")


class LMSActivity(Base):
    __tablename__ = "lms_activity"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    student_id     = Column(String, ForeignKey("students.student_id"), nullable=False)
    date           = Column(Date, nullable=False)
    activity_count = Column(Integer, default=0)
    student        = relationship("Student", back_populates="lms_activity")


class TripwireAlert(Base):
    __tablename__ = "tripwire_alerts"
    alert_id          = Column(Integer, primary_key=True, autoincrement=True)
    student_id        = Column(String, ForeignKey("students.student_id"), nullable=False)
    dvi_score         = Column(Float, nullable=False)
    trigger_date      = Column(DateTime, nullable=False)
    attendance_drift  = Column(Float, default=0.0)   # smoothed component 0–100
    submission_drift  = Column(Float, default=0.0)
    engagement_drift  = Column(Float, default=0.0)
    raw_attendance_drift = Column(Float, default=0.0) # raw un-smoothed drift
    raw_submission_drift = Column(Float, default=0.0)
    raw_engagement_drift = Column(Float, default=0.0)
    raw_dvi_score        = Column(Float, default=0.0)
    reason_json       = Column(Text, default="{}")   # JSON details
    status            = Column(String, default="active")  # active / resolved / monitoring
    excused_flag      = Column(Boolean, default=False)

    student       = relationship("Student", back_populates="alerts")
    interventions = relationship("Intervention", back_populates="alert")
    feedbacks     = relationship("FlagFeedback", back_populates="alert", cascade="all, delete-orphan")


class Intervention(Base):
    __tablename__ = "interventions"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    alert_id     = Column(Integer, ForeignKey("tripwire_alerts.alert_id"), nullable=False)
    mentor_id    = Column(String, ForeignKey("mentors.mentor_id"), nullable=False)
    contact_date = Column(DateTime, nullable=False)
    contact_method = Column(String, default="In-Person")  # In-Person, Video Call, Email, Phone, LMS Message
    outcome      = Column(String, nullable=False)  # Contacted, Student requested support, Academic issue identified, Personal difficulty reported, No response, Referred to support service, Monitoring, Improved
    notes        = Column(Text, default="")
    follow_up_date = Column(Date, nullable=True)
    post_dvi     = Column(Float, nullable=True)

    alert  = relationship("TripwireAlert", back_populates="interventions")
    mentor = relationship("Mentor", back_populates="interventions")


class LeaveRecord(Base):
    __tablename__ = "leave_records"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date   = Column(Date, nullable=False)
    reason     = Column(String, default="personal")  # medical / official / personal
    approved   = Column(Boolean, default=True)
    student    = relationship("Student", back_populates="leaves")


class WeeklyPulse(Base):
    __tablename__ = "weekly_pulses"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    week_date  = Column(Date, nullable=False)
    rating     = Column(Integer, nullable=False)  # 1 (Struggling) to 5 (Thriving)
    stuck_on   = Column(String, nullable=True)    # optional free text explanation
    student    = relationship("Student", back_populates="pulses")


class FlagFeedback(Base):
    __tablename__ = "flag_feedback"
    id                = Column(Integer, primary_key=True, autoincrement=True)
    alert_id          = Column(Integer, ForeignKey("tripwire_alerts.alert_id"), nullable=False)
    faculty_id        = Column(String, ForeignKey("mentors.mentor_id"), nullable=False)
    was_accurate      = Column(String, nullable=False)  # "accurate", "false_positive", "too_late", "unclear"
    was_useful        = Column(Integer, nullable=False)  # 1 to 5 Likert scale
    free_text_comment = Column(Text, nullable=True)
    submitted_at      = Column(DateTime, default=datetime.utcnow)

    alert   = relationship("TripwireAlert", back_populates="feedbacks")
    mentor  = relationship("Mentor", back_populates="feedbacks")


def init_db():
    Base.metadata.create_all(bind=engine)

