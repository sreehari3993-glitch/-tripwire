"""
Tripwire AI Explanation Layer
------------------------------
Uses Google Gemini to generate:
1. Plain-language factual explanation of behavioral drift
2. Non-judgmental conversation starters
3. Suggested mentor exploratory questions
4. Summary of recent behavioral changes

Strict Ethical Boundaries:
- NO mental health or psychological diagnosis
- NO accusations or disciplinary framing
- NO automated punitive decisions
- NO certainty claims
- NO exposure of risk scores to students
Falls back seamlessly to deterministic rule-based generator when no API key or offline.
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def _rule_based_explanation(student_name: str, factors: dict, dvi: float = 77.0) -> dict:
    """Deterministic fallback when no Gemini key is available or offline."""
    att  = factors.get("attendance", {})
    sub  = factors.get("submission", {})
    eng  = factors.get("engagement", {})
    morn = factors.get("morning_absences", {})

    first_name = student_name.split()[0]

    behavioral_changes = []
    if att.get("delta_pct", 0) < -5:
        behavioral_changes.append(f"Attendance declined from {att.get('baseline_pct', 90)}% baseline to {att.get('current_pct', 78)}% ({att.get('delta_pct', -12):+.1f}%)")
    if sub.get("delta_hrs", 0) > 5:
        behavioral_changes.append(f"Assignment submission delay increased from {sub.get('baseline_delay_hrs', 4)}h to {sub.get('current_delay_hrs', 22)}h (+{sub.get('delta_hrs', 18):.0f}h late)")
    if eng.get("delta", 0) < -2:
        behavioral_changes.append(f"LMS activity dropped from {eng.get('baseline_per_week', 18)}/wk baseline to {eng.get('current_per_week', 7)}/wk")
    if morn.get("current", 0) > 1:
        behavioral_changes.append(f"Concentration of morning class absences ({int(morn.get('current', 0))} in last 14 days)")

    if not behavioral_changes:
        behavioral_changes = [
            "Subtle divergence across attendance and assignment timeliness detected relative to personal baseline."
        ]

    explanation = (
        f"{student_name}'s recent academic activity has changed significantly compared with their normal historical pattern. "
        f"Observable shifts include: {'; '.join(behavioral_changes)}. "
        f"Consider checking in privately to understand whether there are academic, personal, scheduling, or other factors affecting their participation."
    )

    talking_point = (
        f"Hey {first_name}, I've been reflecting on how the semester is progressing. "
        f"How are you finding the coursework and workload lately? I wanted to check in privately to see if there is "
        f"anything on your mind—academic or personal—that I might be able to support you with."
    )

    suggested_questions = [
        f"How are you finding the balance between lab assignments and theory classes this month, {first_name}?",
        "Have there been any unforeseen scheduling, commute, or health hurdles that have made morning sessions tricky?",
        "Are there any specific topics in recent modules where a quick review or tutoring session would help relieve pressure?"
    ]

    whatsapp_draft = (
        f"Hey {first_name}! Hope your week is going well. Just wanted to do a quick informal check-in — "
        f"noticed things have been pretty busy with classes and lab work lately. If you have a few minutes "
        f"sometime this week, feel free to drop by my office or let me know if there's anything I can help with. "
        f"No stress at all, just checking in!"
    )

    return {
        "explanation": explanation,
        "talking_point": talking_point,
        "suggested_questions": suggested_questions,
        "behavioral_summary": behavioral_changes,
        "whatsapp_draft": whatsapp_draft,
        "source": "rule_based",
        "ethics_note": "Decision-support guidance for authorized faculty mentors. Tripwire does not diagnose mental health or assess psychological traits."
    }


def generate_explanation(
    student_name: str,
    section: str,
    dvi: float,
    factors: dict
) -> dict:
    """
    Generate AI explanation for a tripwire alert.
    Uses Gemini if API key present, otherwise falls back to rule-based.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        return _rule_based_explanation(student_name, factors, dvi)

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        att  = factors.get("attendance", {})
        sub  = factors.get("submission", {})
        eng  = factors.get("engagement", {})
        morn = factors.get("morning_absences", {})

        prompt = f"""You are an empathetic educational decision-support assistant for a college faculty mentor.
Your task is to summarize recent behavioral drift for student {student_name} ({section}).

CRITICAL ETHICAL RULES:
1. Do NOT make any medical, psychological, or mental health diagnoses.
2. Do NOT accuse, criticize, or judge the student.
3. Focus ONLY on observable academic telemetry (attendance, submission timeliness, LMS activity).
4. Frame all shifts relative to THIS STUDENT'S PERSONAL BASELINE (not a class average).
5. Emphasize supportive, respectful, non-punitive mentorship.
6. The "whatsapp_draft" MUST be a warm, casual, non-judgmental message under 45 words. It MUST NEVER mention AI, Tripwire, DVI, risk scores, or attendance percentages. It must sound like a caring teacher checking in casually about coursework and general well-being.

Student Signals:
- DVI Score: {dvi}/100 (Prototype Threshold: 70)
- Attendance: Baseline {att.get('baseline_pct', 'N/A')}% → Current {att.get('current_pct', 'N/A')}% (Change: {att.get('delta_pct', 0):+.1f}%)
- Submission Latency: Baseline {sub.get('baseline_delay_hrs', 'N/A')} hrs → Current {sub.get('current_delay_hrs', 'N/A')} hrs (Change: {sub.get('delta_hrs', 0):+.1f} hrs)
- LMS Activity: Baseline {eng.get('baseline_per_week', 'N/A')}/week → Current {eng.get('current_per_week', 'N/A')}/week (Change: {eng.get('delta', 0):+.1f}/week)
- Morning Absences: {morn.get('current', 0)} in last 14 days

Respond ONLY with a valid JSON object containing exactly:
{{
  "explanation": "A 2-3 sentence respectful summary of how the student's recent pattern deviates from their baseline, recommending a private check-in.",
  "talking_point": "A gentle, warm, conversational opener for the faculty mentor (under 50 words).",
  "suggested_questions": ["Question 1", "Question 2", "Question 3"],
  "behavioral_summary": ["Bullet 1", "Bullet 2", "Bullet 3"],
  "whatsapp_draft": "A warm, natural WhatsApp check-in message under 45 words without any mention of AI or risk."
}}
No markdown fences, no preamble."""

        response = model.generate_content(prompt)
        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        parsed = json.loads(text)
        if "whatsapp_draft" not in parsed:
            first_name = student_name.split()[0]
            parsed["whatsapp_draft"] = (
                f"Hey {first_name}! Hope your week is going well. Just wanted to do a quick informal check-in — "
                f"noticed things have been pretty busy with classes and lab work lately. If you have a few minutes "
                f"sometime this week, feel free to drop by my office or let me know if there's anything I can help with. "
                f"No stress at all, just checking in!"
            )
        parsed["source"] = "gemini"
        parsed["ethics_note"] = "Decision-support guidance for authorized faculty mentors. Tripwire does not diagnose mental health or assess psychological traits."
        return parsed

    except Exception as e:
        result = _rule_based_explanation(student_name, factors, dvi)
        result["source"] = "rule_based_fallback"
        result["fallback_reason"] = str(e)
        return result
