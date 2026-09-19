"""
Tripwire Synthetic Data Seeder
-------------------------------
Generates 50 students across 7 behavioral archetypes.
Baseline: Aug 1 – Aug 31
Active window: Sep 1 – Sep 15

Student patterns:
  Normal (15): Consistent, healthy
  Gradual Improver (5): Started shaky, now better
  Slow Decline (8): Gentle negative drift
  Rapid Decline (5): Sharp 2-week deterioration (RAHUL is student 1)
  Excused Leave (5): Attendance drop but leave approved
  Early Recovery (5): Was Tripwire, intervention done, recovering
  Monitoring Zone (7): DVI 35–60, borderline
"""

import random
import math
from datetime import date, datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import (
    init_db, SessionLocal, Mentor, Student,
    Attendance, Assignment, LMSActivity,
    TripwireAlert, Intervention, LeaveRecord, FlagFeedback
)

random.seed(42)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Date ranges ────────────────────────────────────────────
BASELINE_START = date(2026, 8, 1)
BASELINE_END   = date(2026, 8, 31)
ACTIVE_START   = date(2026, 9, 1)
ACTIVE_END     = date(2026, 9, 15)

ASSIGNMENTS_PER_MONTH = 8
PERIODS_PER_DAY = 6

# ── Student archetypes ──────────────────────────────────────
ARCHETYPES = {
    "normal":        {"count": 15, "label": "Normal"},
    "improver":      {"count": 5,  "label": "Gradual Improver"},
    "slow_decline":  {"count": 8,  "label": "Slow Decline"},
    "rapid_decline": {"count": 5,  "label": "Rapid Decline"},
    "excused":       {"count": 5,  "label": "Excused Leave"},
    "recovery":      {"count": 5,  "label": "Early Recovery"},
    "monitoring":    {"count": 7,  "label": "Monitoring"},
}

SOUTH_INDIAN_NAMES = [
    "Rajan Menon", "Arjun Nair", "Anjali Krishnan", "Akhil Raj", "Priya Suresh",
    "Vishnu Kumar", "Sneha Pillai", "Arun Varma", "Kavya Mohan", "Deepak Iyer",
    "Lakshmi Das", "Sanjay Nambiar", "Divya Rajan", "Vivek Babu", "Meera Pillai",
    "Rohit Menon", "Nithya Krishnan", "Kiran Suresh", "Shreya Nair", "Anand Kumar",
    "Pooja Varma", "Ravi Pillai", "Geetha Raj", "Suresh Babu", "Amrita Mohan",
    "Vinod Iyer", "Rekha Das", "Manoj Nambiar", "Sindhu Rajan", "Ashwin Babu",
    "Haritha Pillai", "Rajesh Nair", "Suma Krishnan", "Naveen Suresh", "Chithra Kumar",
    "Ajith Varma", "Radha Menon", "Pramod Raj", "Vidya Pillai", "Sreekanth Mohan",
    "Bindhu Iyer", "Anil Das", "Resmi Nambiar", "Sunil Rajan", "Jaya Babu",
    "Harikrishna Pillai", "Nisha Nair", "Rajeev Krishnan", "Parvathy Suresh", "Sreejith Kumar"
]

SECTIONS = ["CSE S1", "CSE S2", "CSE S3", "ECE S1", "ECE S2"]


def daterange(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def is_weekday(d: date) -> bool:
    return d.weekday() < 5  # Monday–Friday


def generate_attendance(
    db: Session, student_id: str,
    period_date: date, prob_present: float, excused_dates: set = None
):
    """Insert attendance records for all periods on a given date."""
    excused_dates = excused_dates or set()
    for period in range(1, PERIODS_PER_DAY + 1):
        if period_date in excused_dates:
            status = "excused"
        elif random.random() < prob_present:
            status = "present"
        else:
            status = "absent"
        db.add(Attendance(
            student_id=student_id,
            date=period_date,
            period=period,
            status=status
        ))


def generate_lms(db: Session, student_id: str, d: date, avg_activity: float):
    """Insert LMS activity for a day."""
    # Poisson-ish: activity count with some noise
    count = max(0, int(random.gauss(avg_activity, avg_activity * 0.4)))
    db.add(LMSActivity(student_id=student_id, date=d, activity_count=count))


def generate_assignment(
    db: Session, student_id: str, assignment_id: str,
    due_date: datetime, baseline_delay_hrs: float, delay_multiplier: float = 1.0
):
    """Insert an assignment with realistic submission time."""
    noise = random.gauss(0, baseline_delay_hrs * 0.3)
    delay_hrs = max(0, baseline_delay_hrs * delay_multiplier + noise)
    submitted_at = due_date + timedelta(hours=delay_hrs)
    db.add(Assignment(
        student_id=student_id,
        assignment_id=assignment_id,
        due_date=due_date,
        submitted_at=submitted_at
    ))


def compute_baselines(
    db: Session, student_id: str
) -> tuple[float, float, float, float]:
    """Compute actual baseline stats from Aug data."""
    # Attendance
    att_records = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date >= BASELINE_START,
        Attendance.date <= BASELINE_END,
        Attendance.status != "excused"
    ).all()
    total = len(att_records)
    present = sum(1 for r in att_records if r.status == "present")
    att_pct = (present / total * 100) if total > 0 else 85.0

    # Submission delay
    subs = db.query(Assignment).filter(
        Assignment.student_id == student_id,
        Assignment.submitted_at.isnot(None)
    ).all()
    delays = []
    for s in subs:
        delta = (s.submitted_at - s.due_date).total_seconds() / 3600
        delays.append(max(0, delta))
    delays.sort()
    mid = len(delays) // 2
    median_delay = delays[mid] if delays else 6.0

    # LMS
    lms_recs = db.query(LMSActivity).filter(
        LMSActivity.student_id == student_id,
        LMSActivity.date >= BASELINE_START,
        LMSActivity.date <= BASELINE_END
    ).all()
    total_lms = sum(r.activity_count for r in lms_recs)
    days_count = (BASELINE_END - BASELINE_START).days + 1
    lms_per_week = (total_lms / days_count) * 7

    # Morning absences per week (periods 1-2)
    morn_abs = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date >= BASELINE_START,
        Attendance.date <= BASELINE_END,
        Attendance.period.in_([1, 2]),
        Attendance.status == "absent"
    ).count()
    weeks = days_count / 7
    morn_per_week = morn_abs / weeks if weeks > 0 else 0.2

    return round(att_pct, 1), round(median_delay, 1), round(lms_per_week, 1), round(morn_per_week, 2)


def seed_mentor(db: Session):
    mentor = Mentor(
        mentor_id="FAC001",
        name="Dr. Pradeep Kumar",
        password_hash=pwd_context.hash("tripwire123"),
        department="Computer Science"
    )
    db.add(mentor)
    db.commit()
    return mentor


def seed_student(
    db: Session, idx: int, archetype: str, mentor_id: str
) -> Student:
    name = SOUTH_INDIAN_NAMES[idx]
    section = random.choice(SECTIONS)
    roll = f"24{idx+1:03d}"
    sid = f"CSE{roll}"

    # Cold start simulation: last 2 students have < 3 weeks of data (transfer / late enroll)
    is_cold = idx in [48, 49]
    weeks_data = 1.8 if is_cold else 6.0
    conf_label = "Building (60% calibrated)" if is_cold else "Established"
    
    # Weeks in status for hysteresis tracking
    status_weeks = 2 if archetype in ["rapid_decline", "recovery"] else (3 if archetype == "monitoring" else 5)

    student = Student(
        student_id=sid, name=name, section=section,
        roll_no=roll, mentor_id=mentor_id,
        archetype=archetype,
        weeks_of_data=weeks_data,
        baseline_confidence=conf_label,
        weeks_in_status=status_weeks,
        # Will be updated after seeding data
        baseline_attendance=85.0,
        baseline_submission_delay_hrs=6.0,
        baseline_lms_activity_per_week=7.0,
        baseline_morning_absences_per_week=0.2
    )
    db.add(student)
    db.commit()

    # ── Generate BASELINE data (Aug 1–31) ──────────────────
    _seed_baseline(db, sid, archetype)

    # ── Generate ACTIVE data (Sep 1–15) ────────────────────
    excused_dates = set()
    if archetype == "excused":
        # Add approved leave for Sep 3–8
        leave_start = date(2026, 9, 3)
        leave_end   = date(2026, 9, 8)
        db.add(LeaveRecord(
            student_id=sid, start_date=leave_start,
            end_date=leave_end, reason="medical", approved=True
        ))
        db.commit()
        excused_dates = {leave_start + timedelta(days=i)
                        for i in range((leave_end - leave_start).days + 1)}

    _seed_active(db, sid, archetype, excused_dates)

    # ── Compute actual baselines from seeded data ──────────
    att, delay, lms, morn = compute_baselines(db, sid)
    student.baseline_attendance               = att
    student.baseline_submission_delay_hrs     = delay
    student.baseline_lms_activity_per_week    = lms
    student.baseline_morning_absences_per_week = morn
    db.commit()

    return student



def _seed_baseline(db: Session, sid: str, archetype: str):
    """Seed healthy baseline data for all archetypes during August."""
    # All students are healthy in August (baseline period)
    base_prob = random.uniform(0.88, 0.96)
    base_lms  = random.uniform(6, 11)
    base_delay = random.uniform(2, 8)

    # Sequence of assignments in August
    assignment_dates_aug = [
        datetime(2026, 8, 5, 23, 59),
        datetime(2026, 8, 10, 23, 59),
        datetime(2026, 8, 15, 23, 59),
        datetime(2026, 8, 20, 23, 59),
        datetime(2026, 8, 25, 23, 59),
        datetime(2026, 8, 28, 23, 59),
        datetime(2026, 8, 30, 23, 59),
    ]

    for d in daterange(BASELINE_START, BASELINE_END):
        if not is_weekday(d):
            continue
        generate_attendance(db, sid, d, base_prob)
        generate_lms(db, sid, d, base_lms / 7)

    for i, due in enumerate(assignment_dates_aug):
        generate_assignment(db, sid, f"AUG{i+1:02d}", due, base_delay)

    db.commit()


def _seed_active(db: Session, sid: str, archetype: str, excused_dates: set):
    """Seed Sep 1–15 data based on archetype."""
    # Assignment due dates in Sep
    assignment_dates_sep = [
        datetime(2026, 9, 3, 23, 59),
        datetime(2026, 9, 7, 23, 59),
        datetime(2026, 9, 10, 23, 59),
        datetime(2026, 9, 14, 23, 59),
    ]

    if archetype == "normal":
        prob   = random.uniform(0.88, 0.96)
        lms    = random.uniform(6, 11)
        d_mult = random.uniform(0.8, 1.2)

    elif archetype == "improver":
        # Starts bad early Sep, gets better
        day_of_active = 0
        for d in daterange(ACTIVE_START, ACTIVE_END):
            if not is_weekday(d): continue
            t = day_of_active / 14
            prob = 0.55 + 0.35 * t   # 0.55 → 0.90
            lms_avg = 2 + 8 * t
            generate_attendance(db, sid, d, prob, excused_dates)
            generate_lms(db, sid, d, lms_avg / 7)
            day_of_active += 1
        for i, due in enumerate(assignment_dates_sep):
            t = i / len(assignment_dates_sep)
            d_mult = 3.0 - 2.5 * t
            generate_assignment(db, sid, f"SEP{i+1:02d}", due, 6.0, d_mult)
        db.commit()
        return

    elif archetype == "slow_decline":
        day_of_active = 0
        for d in daterange(ACTIVE_START, ACTIVE_END):
            if not is_weekday(d): continue
            t = day_of_active / 14
            prob = 0.90 - 0.25 * t   # 0.90 → 0.65
            lms_avg = 9 - 5 * t
            generate_attendance(db, sid, d, prob, excused_dates)
            generate_lms(db, sid, d, lms_avg / 7)
            day_of_active += 1
        for i, due in enumerate(assignment_dates_sep):
            t = i / len(assignment_dates_sep)
            d_mult = 1.0 + 2.5 * t
            generate_assignment(db, sid, f"SEP{i+1:02d}", due, 5.0, d_mult)
        db.commit()
        return

    elif archetype == "rapid_decline":
        # Sharp drop from Sep 7 onwards
        for d in daterange(ACTIVE_START, ACTIVE_END):
            if not is_weekday(d): continue
            if d < date(2026, 9, 7):
                prob = random.uniform(0.80, 0.90)
                lms_avg = random.uniform(5, 8)
            else:
                prob = random.uniform(0.35, 0.55)
                lms_avg = random.uniform(0.5, 2)
            generate_attendance(db, sid, d, prob, excused_dates)
            generate_lms(db, sid, d, lms_avg / 7)
        for i, due in enumerate(assignment_dates_sep):
            d_mult = 1.0 if i < 2 else random.uniform(4.0, 7.0)
            generate_assignment(db, sid, f"SEP{i+1:02d}", due, 6.0, d_mult)
        db.commit()
        return

    elif archetype == "excused":
        # Overall attendance drop due to leave, but not disengaged
        for d in daterange(ACTIVE_START, ACTIVE_END):
            if not is_weekday(d): continue
            if d in excused_dates:
                generate_attendance(db, sid, d, 0.0, excused_dates)  # mark excused
            else:
                prob = random.uniform(0.90, 0.98)  # Normal when not on leave
                generate_attendance(db, sid, d, prob)
            generate_lms(db, sid, d, random.uniform(1, 3) / 7)  # Less during leave
        for i, due in enumerate(assignment_dates_sep):
            generate_assignment(db, sid, f"SEP{i+1:02d}", due, 6.0, 1.1)
        db.commit()
        return

    elif archetype == "recovery":
        # Sep 1–7: high DVI (bad), Sep 8+: recovering
        for d in daterange(ACTIVE_START, ACTIVE_END):
            if not is_weekday(d): continue
            if d <= date(2026, 9, 7):
                prob = random.uniform(0.40, 0.60)
                lms_avg = random.uniform(0.5, 2)
            else:
                t = (d - date(2026, 9, 7)).days / 8
                prob = 0.50 + 0.40 * t
                lms_avg = 1.5 + 7 * t
            generate_attendance(db, sid, d, prob, excused_dates)
            generate_lms(db, sid, d, lms_avg / 7)
        for i, due in enumerate(assignment_dates_sep):
            d_mult = 5.0 if i < 2 else 1.2
            generate_assignment(db, sid, f"SEP{i+1:02d}", due, 5.0, d_mult)
        db.commit()
        return

    elif archetype == "monitoring":
        prob   = random.uniform(0.70, 0.82)
        lms    = random.uniform(3, 6)
        d_mult = random.uniform(1.5, 2.5)

    else:
        prob   = 0.90
        lms    = 8.0
        d_mult = 1.0

    # For archetypes handled uniformly
    for d in daterange(ACTIVE_START, ACTIVE_END):
        if not is_weekday(d): continue
        generate_attendance(db, sid, d, prob, excused_dates)
        generate_lms(db, sid, d, lms / 7)
    for i, due in enumerate(assignment_dates_sep):
        generate_assignment(db, sid, f"SEP{i+1:02d}", due, 6.0, d_mult)
    db.commit()


def seed_rahul_special(db: Session, student: Student):
    """
    Override Rahul (first rapid_decline student) with a dramatic, specific arc
    perfect for the demo narrative.
    DVI progression: 28 → 41 → 55 → 77

    Timeline of events:
    Aug: Healthy baseline (90% attendance, 4hr delay, 10 LMS/week)
    Sep 1–6: Still OK (82% attendance)
    Sep 7: First missed morning class
    Sep 8–10: LMS activity drops significantly
    Sep 11: Assignment submitted 18hrs late
    Sep 12–14: Further decline
    Sep 15: Tripwire triggers
    """
    sid = student.student_id

    # Delete any existing active-period data for Rahul
    db.query(Attendance).filter(
        Attendance.student_id == sid,
        Attendance.date >= ACTIVE_START
    ).delete()
    db.query(LMSActivity).filter(
        LMSActivity.student_id == sid,
        LMSActivity.date >= ACTIVE_START
    ).delete()
    db.query(Assignment).filter(
        Assignment.student_id == sid,
        Assignment.assignment_id.like("SEP%")
    ).delete()
    db.commit()

    # Active data (Sep 2 to Sep 15): 10 weekdays * 6 periods = 60 periods
    # To get 78% attendance: 47 present, 13 absent out of 60 periods (47/60 = 78.3% -> 78%)
    daily_schedule = {
        date(2026, 9, 1):  {"att": [1,1,1,1,1,1], "lms": 3},
        date(2026, 9, 2):  {"att": [1,1,1,1,1,1], "lms": 2}, # 6 present
        date(2026, 9, 3):  {"att": [1,1,1,1,1,1], "lms": 2}, # 6 present
        date(2026, 9, 4):  {"att": [1,1,1,1,1,0], "lms": 2}, # 5 present, 1 absent
        date(2026, 9, 7):  {"att": [0,0,1,1,1,1], "lms": 1}, # 4 present, 2 morning absent
        date(2026, 9, 8):  {"att": [1,1,1,1,1,0], "lms": 1}, # 5 present, 1 absent
        date(2026, 9, 9):  {"att": [0,1,1,1,1,1], "lms": 1}, # 5 present, 1 absent
        date(2026, 9, 10): {"att": [0,0,1,1,1,1], "lms": 1}, # 4 present, 2 morning absent
        date(2026, 9, 11): {"att": [0,0,1,1,1,1], "lms": 1}, # 4 present, 2 morning absent
        date(2026, 9, 12): {"att": [1,1,1,1,1,1], "lms": 1}, # Saturday LMS check
        date(2026, 9, 13): {"att": [1,1,1,1,1,1], "lms": 1}, # Sunday LMS check
        date(2026, 9, 14): {"att": [0,0,1,1,1,1], "lms": 1}, # 4 present, 2 morning absent
        date(2026, 9, 15): {"att": [0,0,1,1,1,1], "lms": 1}, # 4 present, 2 morning absent
    }
    # LMS in last 7 days (Sep 9 to 15): exactly 7 logins -> 7.0/wk!

    for d, info in daily_schedule.items():
        if d.weekday() < 5:  # Only count weekday attendance
            for period, present in enumerate(info["att"], 1):
                db.add(Attendance(
                    student_id=sid, date=d, period=period,
                    status="present" if present else "absent"
                ))
        db.add(LMSActivity(student_id=sid, date=d, activity_count=info["lms"]))

    # Assignments with submission delay sequence: [8h, 14h, 22h, 31h, 35h]
    # Median is exactly 22.0h
    db.add(Assignment(
        student_id=sid, assignment_id="SEP01",
        due_date=datetime(2026, 9, 2, 23, 59),
        submitted_at=datetime(2026, 9, 3, 7, 59)  # 8h delay
    ))
    db.add(Assignment(
        student_id=sid, assignment_id="SEP02",
        due_date=datetime(2026, 9, 5, 23, 59),
        submitted_at=datetime(2026, 9, 6, 13, 59) # 14h delay
    ))
    db.add(Assignment(
        student_id=sid, assignment_id="SEP03",
        due_date=datetime(2026, 9, 8, 23, 59),
        submitted_at=datetime(2026, 9, 9, 21, 59) # 22h delay (median)
    ))
    db.add(Assignment(
        student_id=sid, assignment_id="SEP04",
        due_date=datetime(2026, 9, 11, 23, 59),
        submitted_at=datetime(2026, 9, 13, 6, 59) # 31h delay
    ))
    db.add(Assignment(
        student_id=sid, assignment_id="SEP05",
        due_date=datetime(2026, 9, 14, 23, 59),
        submitted_at=datetime(2026, 9, 16, 10, 59) # 35h delay
    ))

    # Set Rahul's identity and exact prompt baselines
    student.name = "Rahul"
    student.section = "S5 CSE"
    student.roll_no = "24001"



    # Exact prompt baseline: 92% attendance, 4 hours delay, 18 LMS activity/week
    student.baseline_attendance = 92.0
    student.baseline_submission_delay_hrs = 4.0
    student.baseline_lms_activity_per_week = 18.0
    student.baseline_morning_absences_per_week = 0.1

    db.commit()


def seed_alerts_and_interventions(db: Session, students: list, mentor: Mentor):
    """Create pre-seeded alerts for rapid_decline and recovery archetypes."""
    for student in students:
        from dvi_engine import compute_dvi
        result = compute_dvi(db, student)
        dvi = result["dvi"]

        if dvi >= 70.0 or student.name == "Rahul":
            import json as jsonmod
            components = result["components"]
            att_s = components["attendance"].get("smoothed_score", components["attendance"]["score"])
            sub_s = components["submission"].get("smoothed_score", components["submission"]["score"])
            eng_s = components["engagement"].get("smoothed_score", components["engagement"]["score"])
            att_r = components["attendance"].get("raw_score", components["attendance"]["score"])
            sub_r = components["submission"].get("raw_score", components["submission"]["score"])
            eng_r = components["engagement"].get("raw_score", components["engagement"]["score"])

            alert = TripwireAlert(
                student_id=student.student_id,
                dvi_score=dvi,
                trigger_date=datetime(2026, 9, 15, 9, 0),
                attendance_drift=att_s,
                submission_drift=sub_s,
                engagement_drift=eng_s,
                raw_attendance_drift=att_r,
                raw_submission_drift=sub_r,
                raw_engagement_drift=eng_r,
                raw_dvi_score=result["raw_dvi"],
                reason_json=jsonmod.dumps({
                    "attendance_delta_pct": components["attendance"]["delta_pct"],
                    "submission_delta_hrs": components["submission"]["delta_hrs"],
                    "engagement_delta": components["engagement"]["delta"],
                    "morning_absences": components["morning_absences"]["current"]
                }),
                status="active"
            )
            db.add(alert)
            db.commit()


def seed_pulses(db: Session, students: list):
    """Seed qualitative weekly pulse signal (1-5 emoji scale + optional stuck_on text)."""
    from database import WeeklyPulse
    pulse_samples = {
        "CSE24001": (2, "Feeling overwhelmed by Operating Systems lab assignments and long commuting hours."),
        "CSE24002": (4, "Doing well with coursework. Study group is helping."),
        "CSE24004": (5, "Prepared for midterms. Enjoying the cloud computing module."),
        "CSE24018": (1, "Medical issues last week put me behind on two deadlines."),
        "CSE24022": (2, "Struggling to keep up with lecture speed in algorithms.")
    }
    for s in students:
        if s.student_id in pulse_samples:
            score, note = pulse_samples[s.student_id]
            p = WeeklyPulse(
                student_id=s.student_id,
                week_date=date(2026, 9, 11),
                rating=score,
                stuck_on=note
            )
            db.add(p)
            s.weekly_pulse_score = score
            s.weekly_pulse_note = note
            s.weekly_pulse_date = date(2026, 9, 11)
        elif getattr(s, "archetype", "") == "rapid_decline":
            score, note = 2, "Experiencing heavy fatigue and struggling with project milestones."
            p = WeeklyPulse(student_id=s.student_id, week_date=date(2026, 9, 11), rating=score, stuck_on=note)
            db.add(p)
            s.weekly_pulse_score = score
            s.weekly_pulse_note = note
            s.weekly_pulse_date = date(2026, 9, 11)
        elif getattr(s, "archetype", "") == "normal":
            score, note = 4, "Course load is manageable."
            p = WeeklyPulse(student_id=s.student_id, week_date=date(2026, 9, 11), rating=score, stuck_on=note)
            db.add(p)
            s.weekly_pulse_score = score
            s.weekly_pulse_note = note
            s.weekly_pulse_date = date(2026, 9, 11)
    db.commit()


def export_synthetic_csv(db: Session):
    """Export synthetic students to data/synthetic_students.csv."""
    import os
    import csv
    from dvi_engine import compute_dvi

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "synthetic_students.csv")

    students = db.query(Student).all()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "student_id", "name", "class", "archetype", "attendance", "assignment_delay",
            "lms_activity", "dvi", "raw_dvi", "status", "baseline_confidence",
            "baseline_attendance", "baseline_submission_delay", "baseline_lms_activity"
        ])
        for s in students:
            dvi_info = compute_dvi(db, s)
            comps = dvi_info["components"]
            writer.writerow([
                s.student_id,
                s.name,
                s.section,
                getattr(s, "archetype", "normal"),
                f"{comps['attendance']['current_pct']:.1f}%",
                f"{comps['submission']['current_delay_hrs']:.1f}h",
                f"{comps['engagement']['current_per_week']:.1f}/wk",
                round(dvi_info["dvi"], 1),
                round(dvi_info.get("raw_dvi", dvi_info["dvi"]), 1),
                dvi_info["status"].upper(),
                dvi_info.get("baseline_confidence", "Established"),
                f"{s.baseline_attendance:.1f}%",
                f"{s.baseline_submission_delay_hrs:.1f}h",
                f"{s.baseline_lms_activity_per_week:.1f}/wk"
            ])
    print(f"[*] Exported synthetic dataset to {csv_path}")


def seed_flag_feedbacks(db: Session, students: list, mentor: Mentor):
    """
    Seeds historical flag feedbacks demonstrating the Expectation-Disconfirmation Curve
    (Bhattacherjee & Premkumar, 2004; UTAUT EWS acceptance literature).
    - Weeks 1-2: Moderate initial trust (68% -> 61%)
    - Week 3: Disconfirmation Dip (trough at ~53.8%) due to early edge cases and unexcused leaves
    - Weeks 4-6: Post-tuning calibrated recovery (73% -> 82% -> 88.5%)
    """
    import json as jsonmod

    historical_data = [
        # --- WEEK 1 (10-16 Aug) --- Initial Deployment
        {
            "week_idx": 1, "student_idx": 3, "dt": datetime(2026, 8, 12, 11, 30),
            "dvi": 74.5, "att": 72.0, "sub": 65.0, "eng": 80.0,
            "accurate": "accurate", "useful": 4,
            "comment": "Early flag on Akhil Raj. Good reminder, caught assignment latency before it accumulated."
        },
        {
            "week_idx": 1, "student_idx": 7, "dt": datetime(2026, 8, 14, 15, 0),
            "dvi": 76.0, "att": 78.0, "sub": 70.0, "eng": 75.0,
            "accurate": "accurate", "useful": 3,
            "comment": "Accurate on submission delay, but LMS login drop seemed minor."
        },
        {
            "week_idx": 1, "student_idx": 12, "dt": datetime(2026, 8, 15, 10, 15),
            "dvi": 71.5, "att": 69.0, "sub": 72.0, "eng": 68.0,
            "accurate": "accurate", "useful": 4,
            "comment": "Helpful early warning before midterm assignment was due."
        },
        {
            "week_idx": 1, "student_idx": 15, "dt": datetime(2026, 8, 16, 16, 45),
            "dvi": 72.0, "att": 68.0, "sub": 74.0, "eng": 70.0,
            "accurate": "false_positive", "useful": 2,
            "comment": "Student had a minor 1-day absence; flagged a bit too quickly."
        },

        # --- WEEK 2 (17-23 Aug) --- Pre-Tuning Friction
        {
            "week_idx": 2, "student_idx": 18, "dt": datetime(2026, 8, 18, 9, 30),
            "dvi": 78.0, "att": 75.0, "sub": 80.0, "eng": 76.0,
            "accurate": "accurate", "useful": 3,
            "comment": "Flagged for 2 missed lectures, but student had informed class rep."
        },
        {
            "week_idx": 2, "student_idx": 20, "dt": datetime(2026, 8, 20, 14, 20),
            "dvi": 73.5, "att": 70.0, "sub": 75.0, "eng": 72.0,
            "accurate": "false_positive", "useful": 2,
            "comment": "Student was active on external GitHub repository instead of campus LMS."
        },
        {
            "week_idx": 2, "student_idx": 22, "dt": datetime(2026, 8, 21, 11, 0),
            "dvi": 81.0, "att": 82.0, "sub": 85.0, "eng": 74.0,
            "accurate": "accurate", "useful": 4,
            "comment": "Confirmed academic difficulty in data structures. Intervention logged."
        },
        {
            "week_idx": 2, "student_idx": 24, "dt": datetime(2026, 8, 23, 17, 10),
            "dvi": 70.5, "att": 68.0, "sub": 71.0, "eng": 69.0,
            "accurate": "unclear", "useful": 3,
            "comment": "Unclear whether submission delay was due to portal glitch or actual delay."
        },

        # --- WEEK 3 (24-30 Aug) — DISCONFIRMATION TROUGH ---
        {
            "week_idx": 3, "student_idx": 25, "dt": datetime(2026, 8, 25, 10, 0),
            "dvi": 75.0, "att": 80.0, "sub": 72.0, "eng": 70.0,
            "accurate": "false_positive", "useful": 2,
            "comment": "False positive on Priya — student had approved sick leave that the system didn't account for!"
        },
        {
            "week_idx": 3, "student_idx": 27, "dt": datetime(2026, 8, 26, 16, 0),
            "dvi": 77.0, "att": 74.0, "sub": 82.0, "eng": 71.0,
            "accurate": "too_late", "useful": 2,
            "comment": "Alert triggered after midterm results were already published. A bit too late."
        },
        {
            "week_idx": 3, "student_idx": 29, "dt": datetime(2026, 8, 27, 13, 15),
            "dvi": 82.0, "att": 85.0, "sub": 80.0, "eng": 80.0,
            "accurate": "accurate", "useful": 3,
            "comment": "Genuine disengagement, but faculty trust is low after the two false alarms this week."
        },
        {
            "week_idx": 3, "student_idx": 31, "dt": datetime(2026, 8, 28, 15, 30),
            "dvi": 73.0, "att": 76.0, "sub": 70.0, "eng": 71.0,
            "accurate": "false_positive", "useful": 2,
            "comment": "Student attended alternative workshop; uncoordinated attendance data caused false flag."
        },
        {
            "week_idx": 3, "student_idx": 33, "dt": datetime(2026, 8, 30, 11, 45),
            "dvi": 79.5, "att": 80.0, "sub": 82.0, "eng": 74.0,
            "accurate": "accurate", "useful": 3,
            "comment": "Accurate, but faculty frustration high regarding static threshold sensitivity."
        },

        # --- WEEK 4 (31 Aug-6 Sep) — POST-TUNING RECOVERY BEGINS ---
        {
            "week_idx": 4, "student_idx": 34, "dt": datetime(2026, 9, 1, 10, 30),
            "dvi": 84.0, "att": 82.0, "sub": 88.0, "eng": 80.0,
            "accurate": "accurate", "useful": 4,
            "comment": "Much better now that the human override allows marking medical leaves as EXCUSED."
        },
        {
            "week_idx": 4, "student_idx": 36, "dt": datetime(2026, 9, 2, 14, 0),
            "dvi": 79.0, "att": 76.0, "sub": 84.0, "eng": 74.0,
            "accurate": "accurate", "useful": 4,
            "comment": "EWMA temporal smoothing reduced noisy spikes from a single tough quiz."
        },
        {
            "week_idx": 4, "student_idx": 38, "dt": datetime(2026, 9, 3, 11, 20),
            "dvi": 72.0, "att": 70.0, "sub": 75.0, "eng": 70.0,
            "accurate": "false_positive", "useful": 3,
            "comment": "Borderline drift. Quickly resolved with student check-in."
        },
        {
            "week_idx": 4, "student_idx": 40, "dt": datetime(2026, 9, 4, 16, 10),
            "dvi": 86.0, "att": 88.0, "sub": 86.0, "eng": 82.0,
            "accurate": "accurate", "useful": 5,
            "comment": "Caught Rohan's silent decline 2 weeks before project submission. Very timely."
        },
        {
            "week_idx": 4, "student_idx": 42, "dt": datetime(2026, 9, 6, 12, 0),
            "dvi": 77.5, "att": 75.0, "sub": 81.0, "eng": 74.0,
            "accurate": "accurate", "useful": 4,
            "comment": "Threshold calibration from sensitivity analysis is clearly showing improved precision."
        },

        # --- WEEK 5 (7-13 Sep) --- Sustained Trust
        {
            "week_idx": 5, "student_idx": 43, "dt": datetime(2026, 9, 8, 9, 45),
            "dvi": 88.0, "att": 85.0, "sub": 90.0, "eng": 88.0,
            "accurate": "accurate", "useful": 5,
            "comment": "Identified disengagement in LMS access before attendance even slipped. Great catch."
        },
        {
            "week_idx": 5, "student_idx": 44, "dt": datetime(2026, 9, 9, 14, 30),
            "dvi": 82.0, "att": 80.0, "sub": 85.0, "eng": 79.0,
            "accurate": "accurate", "useful": 4,
            "comment": "The 'What Changed' breakdown gave concrete talking points for our 1-on-1 meeting."
        },
        {
            "week_idx": 5, "student_idx": 45, "dt": datetime(2026, 9, 10, 11, 15),
            "dvi": 75.0, "att": 73.0, "sub": 78.0, "eng": 72.0,
            "accurate": "false_positive", "useful": 3,
            "comment": "Student had network trouble at home; marked excused quickly via override."
        },
        {
            "week_idx": 5, "student_idx": 46, "dt": datetime(2026, 9, 11, 16, 0),
            "dvi": 91.0, "att": 90.0, "sub": 94.0, "eng": 87.0,
            "accurate": "accurate", "useful": 5,
            "comment": "Critical alert — student had stopped attending morning sessions entirely. Support provided."
        },
        {
            "week_idx": 5, "student_idx": 47, "dt": datetime(2026, 9, 12, 13, 0),
            "dvi": 83.5, "att": 82.0, "sub": 86.0, "eng": 80.0,
            "accurate": "accurate", "useful": 4,
            "comment": "Student appreciated early mentor outreach; coursework back on track."
        },
        {
            "week_idx": 5, "student_idx": 48, "dt": datetime(2026, 9, 13, 10, 30),
            "dvi": 78.0, "att": 76.0, "sub": 82.0, "eng": 74.0,
            "accurate": "accurate", "useful": 5,
            "comment": "Cold-start Bayesian blending worked nicely for newly transferred student."
        },

        # --- WEEK 6 (14-16 Sep - CURRENT) --- High Trust Maturity
        {
            "week_idx": 6, "student_idx": 0, "dt": datetime(2026, 9, 15, 14, 0), # RAHUL
            "dvi": 77.8, "att": 72.8, "sub": 85.5, "eng": 75.2,
            "accurate": "accurate", "useful": 5,
            "comment": "Accurate flag on Rahul Sharma (CSE24001). Latency shift (+18h) was the smoking gun. Supportive extension granted."
        },
        {
            "week_idx": 6, "student_idx": 1, "dt": datetime(2026, 9, 15, 16, 30),
            "dvi": 85.0, "att": 84.0, "sub": 88.0, "eng": 82.0,
            "accurate": "accurate", "useful": 5,
            "comment": "Excellent alert timing. Actionable counterfactual explanation provided immediate clarity."
        },
        {
            "week_idx": 6, "student_idx": 2, "dt": datetime(2026, 9, 16, 9, 15),
            "dvi": 80.0, "att": 79.0, "sub": 82.0, "eng": 78.0,
            "accurate": "accurate", "useful": 4,
            "comment": "Faculty trust firmly restored. The system is demonstrably calibrating to personal baselines."
        },
        {
            "week_idx": 6, "student_idx": 4, "dt": datetime(2026, 9, 16, 11, 45),
            "dvi": 76.0, "att": 74.0, "sub": 79.0, "eng": 74.0,
            "accurate": "accurate", "useful": 5,
            "comment": "The asymmetric hysteresis recovery prevents status flapping. Great design."
        }
    ]

    for item in historical_data:
        stu = students[item["student_idx"]] if item["student_idx"] < len(students) else students[0]

        # Check if alert already exists for this student (e.g. Rahul CSE24001)
        existing_alert = db.query(TripwireAlert).filter(
            TripwireAlert.student_id == stu.student_id
        ).first()

        if existing_alert and item["student_idx"] == 0:
            target_alert = existing_alert
        else:
            # Create historical alert record
            target_alert = TripwireAlert(
                student_id=stu.student_id,
                dvi_score=item["dvi"],
                trigger_date=item["dt"],
                attendance_drift=item["att"],
                submission_drift=item["sub"],
                engagement_drift=item["eng"],
                raw_attendance_drift=item["att"] + random.uniform(-2, 2),
                raw_submission_drift=item["sub"] + random.uniform(-3, 3),
                raw_engagement_drift=item["eng"] + random.uniform(-2, 2),
                raw_dvi_score=item["dvi"],
                reason_json=jsonmod.dumps({
                    "attendance_delta_pct": -12.0,
                    "submission_delta_hrs": 14.5,
                    "engagement_delta": -5.0
                }),
                status="resolved" if item["week_idx"] < 5 else "active"
            )
            db.add(target_alert)
            db.commit()
            db.refresh(target_alert)

        # Create flag feedback
        fb = FlagFeedback(
            alert_id=target_alert.alert_id,
            faculty_id=mentor.mentor_id,
            was_accurate=item["accurate"],
            was_useful=item["useful"],
            free_text_comment=item["comment"],
            submitted_at=item["dt"] + timedelta(hours=random.randint(1, 12))
        )
        db.add(fb)

    db.commit()
    print(f"[*] Seeded {len(historical_data)} historical flag feedback records across Weeks 1-6.")


def run_seed():
    print("[*] Initialising Tripwire database...")
    init_db()
    db = SessionLocal()

    # Clear existing data
    from database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("[*] Seeding mentor...")
    mentor = seed_mentor(db)

    print("[*] Seeding 50 students...")
    students = []
    
    # Student 0 (CSE24001) is Rahul — primary demo persona
    print("  [demo_archetype] Rahul (CSE24001 - S5 CSE)")
    rahul_student = seed_student(db, 0, "rapid_decline", mentor.mentor_id)
    seed_rahul_special(db, rahul_student)
    students.append(rahul_student)

    # Remaining 49 students
    idx = 1
    for archetype, cfg in ARCHETYPES.items():
        count = cfg["count"] - 1 if archetype == "rapid_decline" else cfg["count"]
        for i in range(count):
            if idx >= 50:
                break
            student = seed_student(db, idx, archetype, mentor.mentor_id)
            students.append(student)
            idx += 1

    print("[*] Seeding qualitative weekly pulse signals...")
    seed_pulses(db, students)

    print("[*] Seeding alerts...")
    seed_alerts_and_interventions(db, students, mentor)

    # Seed interventions for recovery archetype students so they show as RECOVERING
    print("[*] Seeding sample resolved and recovering interventions...")
    alerts = db.query(TripwireAlert).all()
    if len(alerts) > 1:
        # Give second alert a resolved intervention
        sample_alert = alerts[1]
        sample_alert.status = "monitoring"
        intervention1 = Intervention(
            alert_id=sample_alert.alert_id,
            mentor_id=mentor.mentor_id,
            contact_date=datetime(2026, 9, 13, 14, 30),
            contact_method="In-Person",
            outcome="Academic issue identified",
            notes="Discussed lab scheduling conflicts. Arranged peer tutoring.",
            post_dvi=54.0
        )
        db.add(intervention1)

    if len(alerts) > 2:
        # Give third alert an improved outcome
        sample_alert2 = alerts[2]
        sample_alert2.status = "resolved"
        intervention2 = Intervention(
            alert_id=sample_alert2.alert_id,
            mentor_id=mentor.mentor_id,
            contact_date=datetime(2026, 9, 14, 11, 0),
            contact_method="In-Person",
            outcome="Improved",
            notes="Student attendance returned to normal after meeting. Catch-up completed.",
            post_dvi=42.0
        )
        db.add(intervention2)

    db.commit()

    print("[*] Seeding historical flag feedback records (Expectation-Disconfirmation Curve)...")
    seed_flag_feedbacks(db, students, mentor)

    db.commit()

    export_synthetic_csv(db)

    student_count = db.query(Student).count()
    alert_count   = db.query(TripwireAlert).count()
    print(f"\n[OK] Seed complete!")
    print(f"   Students: {student_count}")
    print(f"   Alerts:   {alert_count}")
    print(f"   Mentor:   {mentor.name} (ID: {mentor.mentor_id}, pass: tripwire123)")


if __name__ == "__main__":
    run_seed()

