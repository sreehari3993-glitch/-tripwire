"""Demo Mode Route — Provides the full 6-stage interactive demonstration flow for Rahul Menon."""
from fastapi import APIRouter

router = APIRouter(prefix="/demo", tags=["demo"])

DEMO_STAGES = [
    {
        "stage": 1,
        "title": "Individual Baseline Established",
        "phase": "Baseline Normal",
        "timeframe": "August 1 – August 31",
        "dvi": 31,
        "status": "normal",
        "velocity": "↗↗",
        "metrics": {
            "attendance": {"current": 91.0, "baseline": 91.0, "delta": 0.0, "unit": "%"},
            "submission_delay": {"current": 4.5, "baseline": 4.5, "delta": 0.0, "unit": "h"},
            "lms_activity": {"current": 10.0, "baseline": 10.0, "delta": 0.0, "unit": "/wk"},
            "morning_absences": {"current": 0, "baseline": 0.1}
        },
        "dvi_components": {
            "attendance_contrib": 12.4,
            "submission_contrib": 10.8,
            "engagement_contrib": 7.8,
            "total_dvi": 31.0
        },
        "narrative": "Rahul starts the semester in strong standing. During August, Tripwire establishes his personal behavioral baseline: 91% attendance, 4.5-hour average assignment delay, and 10 LMS interactions per week. Crucially, Tripwire does not compare Rahul to the class average—his own normal pattern is the reference point.",
        "badge": "🟢 Normal Baseline",
        "key_takeaway": "Baseline established: Individual norm calibration active."
    },
    {
        "stage": 2,
        "title": "Early Behavioral Drift",
        "phase": "Monitoring Zone",
        "timeframe": "September 1 – September 8",
        "dvi": 52,
        "status": "monitoring",
        "velocity": "↘",
        "metrics": {
            "attendance": {"current": 84.0, "baseline": 91.0, "delta": -7.0, "unit": "%"},
            "submission_delay": {"current": 18.0, "baseline": 4.5, "delta": +13.5, "unit": "h"},
            "lms_activity": {"current": 6.0, "baseline": 10.0, "delta": -4.0, "unit": "/wk"},
            "morning_absences": {"current": 2, "baseline": 0.1}
        },
        "dvi_components": {
            "attendance_contrib": 18.2,
            "submission_contrib": 21.0,
            "engagement_contrib": 12.8,
            "total_dvi": 52.0
        },
        "narrative": "Early in September, small behavioral shifts emerge. Rahul misses two morning lectures and submits assignment SEP02 18 hours late. His LMS logins drop from 10 to 6 per week. DVI rises to 52, entering the MONITORING zone. Traditional systems fail to notice this because 84% attendance is well above the institutional failure bar.",
        "badge": "🟡 Behavioral Drift",
        "key_takeaway": "DVI rises to 52: Silent drift detected before any grades suffer."
    },
    {
        "stage": 3,
        "title": "Tripwire Alert Triggered",
        "phase": "Active Warning",
        "timeframe": "September 9 – September 15",
        "dvi": 78,
        "status": "tripwire",
        "velocity": "↘↘",
        "metrics": {
            "attendance": {"current": 78.0, "baseline": 91.0, "delta": -13.0, "unit": "%"},
            "submission_delay": {"current": 42.0, "baseline": 4.5, "delta": +37.5, "unit": "h"},
            "lms_activity": {"current": 2.0, "baseline": 10.0, "delta": -8.0, "unit": "/wk"},
            "morning_absences": {"current": 4, "baseline": 0.1}
        },
        "dvi_components": {
            "attendance_contrib": 28.0,
            "submission_contrib": 30.5,
            "engagement_contrib": 19.5,
            "total_dvi": 78.0
        },
        "what_changed": {
            "attendance": "Attendance declined 13% from baseline (91% → 78%)",
            "submission": "Assignment delay increased by 37.5 hours (4.5h → 42h)",
            "lms": "LMS engagement decreased by 80% (10/wk → 2/wk)",
            "patterns": "Repeated absences concentrated in morning lab blocks"
        },
        "counterfactual": "The alert would likely not have triggered if assignment submission latency and LMS activity had remained near Rahul's normal historical baseline.",
        "ai_explanation": "Rahul's recent academic activity has changed significantly compared with his normal pattern. Observable shifts include a 37.5-hour increase in submission delay and a drop in weekly LMS logins. Consider checking in privately to explore whether academic, scheduling, or personal factors are affecting his participation.",
        "talking_point": "Hey Rahul, I wanted to check in and see how the semester is going. How are you finding the coursework and lab pace lately? Is there anything on your mind—academic or personal—that I might be able to help with?",
        "suggested_questions": [
            "How are you finding the workload balance across theory and labs this month?",
            "Have commute or morning scheduling hurdles impacted your lab attendance?",
            "Would a quick review or tutoring session on recent topics help relieve pressure?"
        ],
        "narrative": "Decline accelerates: Assignment SEP03 is 42 hours late, SEP04 is missing, and morning attendance drops further. DVI crosses 70 to hit 78. A confidential TRIPWIRE alert is sent to Dr. Pradeep. Crucially, Rahul is NOT notified with an alarming 'High Risk' label. The alert empowers the human mentor to step in.",
        "badge": "🔴 TRIPWIRE DETECTED",
        "key_takeaway": "Confidential decision-support alert dispatched to faculty mentor."
    },
    {
        "stage": 4,
        "title": "Human-in-the-Loop Intervention",
        "phase": "Faculty Mentorship",
        "timeframe": "September 16",
        "dvi": 78,
        "status": "tripwire",
        "velocity": "→",
        "intervention": {
            "mentor": "Dr. Pradeep Kumar",
            "contact_method": "In-Person Check-in (Faculty Office)",
            "outcome": "Academic issue identified",
            "notes": "Met with Rahul for 20 minutes using Tripwire's suggested talking points. Rahul disclosed that he was overwhelmed by the concurrent data structures lab deadlines and had an unexpected family commute issue. Arranged a peer tutor from S7 and granted a 48-hour extension on SEP04 lab report.",
            "follow_up_date": "September 23",
            "status": "Recorded"
        },
        "narrative": "Dr. Pradeep invites Rahul for a relaxed check-in using Tripwire's non-stigmatizing talking points. Rahul opens up about feeling overwhelmed by difficult concurrency lab projects and difficult commute schedules. Dr. Pradeep connects Rahul with an S7 peer tutor and records the intervention outcome. AI did not punish the student; it facilitated human connection.",
        "badge": "🤝 Mentor Intervention Recorded",
        "key_takeaway": "AI assists the mentor; human judgment and empathy lead the intervention."
    },
    {
        "stage": 5,
        "title": "Behavioral Recovery Detected",
        "phase": "Early Recovery",
        "timeframe": "September 17 – September 20",
        "dvi": 63,
        "status": "recovering",
        "velocity": "↗",
        "metrics": {
            "attendance": {"current": 86.0, "baseline": 91.0, "delta": -5.0, "unit": "%"},
            "submission_delay": {"current": 12.0, "baseline": 4.5, "delta": +7.5, "unit": "h"},
            "lms_activity": {"current": 8.0, "baseline": 10.0, "delta": -2.0, "unit": "/wk"},
            "morning_absences": {"current": 1, "baseline": 0.1}
        },
        "dvi_components": {
            "attendance_contrib": 21.0,
            "submission_contrib": 23.5,
            "engagement_contrib": 18.5,
            "total_dvi": 63.0
        },
        "narrative": "Supported by the peer tutor, Rahul turns the corner. He attends all classes for the rest of the week and submits the updated lab report. DVI drops sharply from 78 down to 63. Tripwire detects the positive velocity and updates Rahul's status to RECOVERING (🟣). This proves Tripwire is an intervention-support loop, not just a warning siren.",
        "badge": "🟣 Behavioral Recovery Detected",
        "key_takeaway": "Post-intervention telemetry confirms the positive behavioral rebound."
    },
    {
        "stage": 6,
        "title": "Fully Recovered to Normal Baseline",
        "phase": "Full Resolution",
        "timeframe": "September 21 – September 25",
        "dvi": 49,
        "status": "normal",
        "velocity": "↗↗",
        "metrics": {
            "attendance": {"current": 90.0, "baseline": 91.0, "delta": -1.0, "unit": "%"},
            "submission_delay": {"current": 5.0, "baseline": 4.5, "delta": +0.5, "unit": "h"},
            "lms_activity": {"current": 9.5, "baseline": 10.0, "delta": -0.5, "unit": "/wk"},
            "morning_absences": {"current": 0, "baseline": 0.1}
        },
        "dvi_components": {
            "attendance_contrib": 16.5,
            "submission_contrib": 18.0,
            "engagement_contrib": 14.5,
            "total_dvi": 49.0
        },
        "narrative": "By the fourth week of September, Rahul's behavioral metrics have fully stabilized near his initial August baseline. DVI drops below 50 to 49, successfully clearing all warning flags. A potential semester failure was detected and reversed in early September—weeks before midterm exams.",
        "badge": "🟢 Good Standing Restored",
        "final_message": "Tripwire doesn't replace the mentor. It helps the mentor notice the right student at the right time.",
        "key_takeaway": "Disengagement was resolved silently and compassionately. Mission accomplished."
    }
]


@router.get("/stages")
def get_demo_stages():
    """Return all 6 sequential stages of Rahul's demo arc."""
    return {
        "data_source": "scripted_demo",
        "student_id": "CSE24001",
        "student_name": "Rahul Menon",
        "section": "CSE S2",
        "total_stages": len(DEMO_STAGES),
        "stages": DEMO_STAGES,
        "viva_takeaway": "Tripwire doesn't replace the mentor. It helps the mentor notice the right student at the right time."
    }
