"""
Tripwire DVI Weight Validation & Sensitivity Analysis
------------------------------------------------------
Validates the current DVI weights (0.40 Attendance, 0.35 Submission, 0.25 Engagement)
against alternative weight sets across the 50-student synthetic cohort.

Evaluates how effectively each weight configuration separates:
  - Positive Class: "Rapid Decline" archetype (should trigger Tripwire >= 70)
  - Negative Class: "Normal" and "Excused Leave" archetypes (should remain low < 50)

Outputs:
  - Markdown Report: backend/scripts/weight_validation_report.md
  - JSON Data:       backend/scripts/weight_validation_results.json
"""

import os
import sys
import json
from typing import Dict, List

# Add parent directory to path so database and dvi_engine can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Student
from dvi_engine import compute_dvi

WEIGHT_CANDIDATES = [
    {
        "id": "current",
        "name": "Current Config (Calibrated)",
        "weights": {"attendance": 0.40, "submission": 0.35, "engagement": 0.25},
        "rationale": "High priority on early lecture presence + assignment completion latency."
    },
    {
        "id": "equal",
        "name": "Equal Weights (33/33/34)",
        "weights": {"attendance": 0.33, "submission": 0.33, "engagement": 0.34},
        "rationale": "Uniform agnostic distribution across all 3 telemetry streams."
    },
    {
        "id": "attendance_heavy",
        "name": "Attendance-Heavy (50/30/20)",
        "weights": {"attendance": 0.50, "submission": 0.30, "engagement": 0.20},
        "rationale": "Emphasizes classroom physical presence over portal interactions."
    },
    {
        "id": "submission_heavy",
        "name": "Submission-Latency Heavy (25/50/25)",
        "weights": {"attendance": 0.25, "submission": 0.50, "engagement": 0.25},
        "rationale": "Focuses primarily on homework/project procrastination velocity."
    },
    {
        "id": "engagement_heavy",
        "name": "LMS Engagement-Heavy (25/25/50)",
        "weights": {"attendance": 0.25, "submission": 0.25, "engagement": 0.50},
        "rationale": "Prioritizes online learning platform clickstream interactions."
    }
]

THRESHOLD_ALERT = 70.0


def run_weight_validation() -> Dict:
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        if not students:
            print("[!] No students found. Please seed the database first.")
            return {}

        results = []

        for candidate in WEIGHT_CANDIDATES:
            weights = candidate["weights"]
            rapid_scores = []
            normal_scores = []
            excused_scores = []
            all_scores = []

            tp, fp, fn, tn = 0, 0, 0, 0
            fp_normal, fp_excused = 0, 0

            for s in students:
                archetype = getattr(s, "archetype", "normal") or "normal"
                # Compute DVI under candidate weights
                res = compute_dvi(db, s, weights=weights)
                dvi = res["dvi"]
                all_scores.append({"id": s.student_id, "name": s.name, "archetype": archetype, "dvi": dvi})

                if archetype == "rapid_decline":
                    rapid_scores.append(dvi)
                    if dvi >= THRESHOLD_ALERT:
                        tp += 1
                    else:
                        fn += 1
                elif archetype in ["normal", "excused"]:
                    if archetype == "normal":
                        normal_scores.append(dvi)
                        if dvi >= THRESHOLD_ALERT:
                            fp_normal += 1
                            fp += 1
                        else:
                            tn += 1
                    else:
                        excused_scores.append(dvi)
                        if dvi >= THRESHOLD_ALERT:
                            fp_excused += 1
                            fp += 1
                        else:
                            tn += 1

            negative_scores = normal_scores + excused_scores

            mean_rapid = sum(rapid_scores) / len(rapid_scores) if rapid_scores else 0.0
            mean_normal = sum(normal_scores) / len(normal_scores) if normal_scores else 0.0
            mean_excused = sum(excused_scores) / len(excused_scores) if excused_scores else 0.0
            mean_negative = sum(negative_scores) / len(negative_scores) if negative_scores else 0.0

            # Separation gap = how far rapid decline students are from healthy students
            separation_gap = mean_rapid - mean_negative

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            results.append({
                "id": candidate["id"],
                "name": candidate["name"],
                "weights": weights,
                "rationale": candidate["rationale"],
                "mean_rapid_decline": round(mean_rapid, 1),
                "mean_normal": round(mean_normal, 1),
                "mean_excused": round(mean_excused, 1),
                "mean_negative": round(mean_negative, 1),
                "separation_gap": round(separation_gap, 1),
                "tp": tp,
                "fp": fp,
                "fp_normal": fp_normal,
                "fp_excused": fp_excused,
                "fn": fn,
                "tn": tn,
                "precision": round(precision * 100, 1),
                "recall": round(recall * 100, 1),
                "f1_score": round(f1 * 100, 1)
            })

        # Rank candidates by separation gap & F1 score
        results.sort(key=lambda x: (x["f1_score"], x["separation_gap"]), reverse=True)
        best_candidate = results[0]

        excused_fp_text = (
            "zero false positives on excused leaves"
            if best_candidate["fp_excused"] == 0
            else f"{best_candidate['fp_excused']} false positive(s) on excused leaves (mean DVI {best_candidate['mean_excused']})"
        )

        summary_payload = {
            "title": "DVI Weight Sensitivity & Separation Analysis",
            "threshold_used": THRESHOLD_ALERT,
            "cohort_size": len(students),
            "best_candidate": best_candidate["id"],
            "candidates": results,
            "recommendation": (
                f"The '{best_candidate['name']}' ({best_candidate['weights']['attendance']*100:.0f}% Att, "
                f"{best_candidate['weights']['submission']*100:.0f}% Sub, {best_candidate['weights']['engagement']*100:.0f}% LMS) "
                f"achieves the optimal separation gap ({best_candidate['separation_gap']} pts) with "
                f"{best_candidate['f1_score']}% F1 score and {excused_fp_text}."
            )
        }

        # Save JSON output
        out_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(out_dir, "weight_validation_results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary_payload, f, indent=2)

        # Generate Markdown Report
        md_path = os.path.join(out_dir, "weight_validation_report.md")
        generate_markdown_report(md_path, summary_payload)

        print(f"[OK] Weight validation complete!")
        print(f"     Report saved to: {md_path}")
        print(f"     JSON saved to:   {json_path}")
        print(f"     Top Config:      {best_candidate['name']} (Gap: {best_candidate['separation_gap']} pts, F1: {best_candidate['f1_score']}%)")

        return summary_payload

    finally:
        db.close()


def generate_markdown_report(filepath: str, data: Dict):
    best_id = data["best_candidate"]
    candidates = data["candidates"]
    best = next(c for c in candidates if c["id"] == best_id)
    other_candidates = [c for c in candidates if c["id"] != best_id]

    lines = [
        "# TRIPWIRE — DVI Weight Validation & Sensitivity Report",
        "",
        "> **Objective**: Mathematically validate the DVI weighting scheme against alternative configurations to identify optimal separation between disengaged students and healthy cohorts.",
        "",
        f"**Evaluation Cohort**: {data['cohort_size']} students | **Alert Threshold**: DVI $\\ge {data['threshold_used']}$",
        "",
        "## 📊 Model Comparison & Separation Metrics",
        "",
        "| Weight Configuration | Weights (Att / Sub / LMS) | Mean Rapid Decline | Mean Normal | Mean Excused | Separation Gap | Precision | Recall | F1 Score | Excused FP |",
        "|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    ]

    for c in candidates:
        w = c["weights"]
        w_str = f"{int(w['attendance']*100)} / {int(w['submission']*100)} / {int(w['engagement']*100)}"
        badge = " **(Top Ranked)**" if c["id"] == best_id else ""
        lines.append(
            f"| **{c['name']}**{badge} | `{w_str}` | **{c['mean_rapid_decline']}** | {c['mean_normal']} | {c['mean_excused']} | **+{c['separation_gap']} pts** | {c['precision']}% | {c['recall']}% | **{c['f1_score']}%** | {c.get('fp_excused', c['fp'])} |"
        )

    lines.extend([
        "",
        "## 🔍 Key Findings & Empirical Analysis",
        "",
        f"1. **Winning Configuration — {best['name']}**:",
        f"   - Achieves top separation performance with an F1 score of **{best['f1_score']}%** and a separation gap of **+{best['separation_gap']} points** between rapid decline and healthy cohorts.",
        f"   - Empirical design rationale: {best['rationale']}",
        "",
        "2. **Comparison with Alternative Configurations**:"
    ])

    for oc in other_candidates:
        gap_diff = round(best["separation_gap"] - oc["separation_gap"], 1)
        f1_diff = round(best["f1_score"] - oc["f1_score"], 1)
        lines.append(
            f"   - **{oc['name']}**: Yielded a separation gap of +{oc['separation_gap']} pts "
            f"({gap_diff:+.1f} pts vs top) and F1 score of {oc['f1_score']}% ({f1_diff:+.1f}% vs top). "
            f"Config focus: {oc['rationale']}"
        )

    excused_fp = best.get("fp_excused", 0)
    excused_claim = (
        f"Under '{best['name']}', students on approved excused leaves maintain an average DVI of `{best['mean_excused']}`, safely generating zero false positives."
        if excused_fp == 0 else
        f"Under '{best['name']}', students on approved excused leaves have an average DVI of `{best['mean_excused']}`, with {excused_fp} student(s) crossing the threshold due to concurrent assignment/LMS drift."
    )

    lines.extend([
        "",
        "3. **Behavior on Excused Leaves Subgroup**:",
        f"   - {excused_claim}",
        "",
        f"**Conclusion**: {data['recommendation']}"
    ])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    run_weight_validation()
