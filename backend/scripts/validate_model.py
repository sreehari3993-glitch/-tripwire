"""
Tripwire DVI Model Validation — validate_model.py
--------------------------------------------------
Computes per-archetype precision, recall, and F1 score for the DVI alert system
using the 50-student synthetic cohort across 7 behavioral archetypes from seed_data.py.

Archetypes:
  POSITIVE (should trigger DVI >= 70):
    - rapid_decline   : Rapid multi-signal collapse — must be caught
    - monitoring      : Drifting into alert zone — proactive detection
  BORDERLINE (should appear in MONITORING 50-69 or catch a subset):
    - slow_decline    : Gradual drift; early catch is the goal
    - improver        : Improving, but may still have residual DVI
    - recovery        : Post-intervention; gradual stabilization
  NEGATIVE (should NOT trigger DVI >= 70):
    - normal          : Stable student — zero false positives expected
    - excused         : Approved medical/official leave — should not be flagged

Outputs:
  - JSON: backend/scripts/model_validation_results.json
  - Markdown section for README inclusion
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Student
from dvi_engine import compute_dvi, W_ATTENDANCE, W_SUBMISSION, W_ENGAGEMENT

ALERT_THRESHOLD = 70.0
MONITORING_THRESHOLD = 50.0

# Ground-truth label per archetype
# positive   = should trigger DVI >= 70 (true positives)
# borderline = in monitoring zone 50-69; alerting = early catch (still good)
# negative   = should NOT trigger DVI >= 70 (false positives if flagged)
ARCHETYPE_LABELS = {
    "rapid_decline":  "positive",    # Multi-signal collapse — must be caught
    "monitoring":     "positive",    # Already drifting into alert zone
    "recovery":       "borderline",  # Post-intervention; some may still alert
    "slow_decline":   "borderline",  # Gradual drift; early catch is the goal
    "improver":       "borderline",  # Improving, but may still have residual DVI
    "normal":         "negative",    # Stable student — zero false positives expected
    "excused":        "negative",    # Approved leave — should not be flagged
}

CURRENT_WEIGHTS = {"attendance": W_ATTENDANCE, "submission": W_SUBMISSION, "engagement": W_ENGAGEMENT}


def run_model_validation() -> dict:
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        if not students:
            return {"error": "No students found. Please seed the database first."}

        # Per-archetype buckets
        archetype_data = {}
        for s in students:
            arch = (getattr(s, "archetype", None) or "normal").strip()
            if arch not in archetype_data:
                archetype_data[arch] = {"scores": [], "tp": 0, "fp": 0, "fn": 0, "tn": 0}

            res = compute_dvi(db, s)
            dvi = res["dvi"]
            archetype_data[arch]["scores"].append(dvi)

            label = ARCHETYPE_LABELS.get(arch, "negative")
            predicted_alert = dvi >= ALERT_THRESHOLD

            if label == "positive":
                if predicted_alert:
                    archetype_data[arch]["tp"] += 1
                else:
                    archetype_data[arch]["fn"] += 1
            elif label == "negative":
                if predicted_alert:
                    archetype_data[arch]["fp"] += 1
                else:
                    archetype_data[arch]["tn"] += 1
            # borderline: count as true_positive if alert triggered (catching drift is good)
            else:
                if predicted_alert:
                    archetype_data[arch]["tp"] += 1
                else:
                    archetype_data[arch]["tn"] += 1

        # Build per-archetype stats
        per_archetype = []
        total_tp = total_fp = total_fn = total_tn = 0

        for arch, data in sorted(archetype_data.items()):
            scores = data["scores"]
            mean_dvi = round(sum(scores) / len(scores), 1) if scores else 0.0
            min_dvi = round(min(scores), 1) if scores else 0.0
            max_dvi = round(max(scores), 1) if scores else 0.0
            n = len(scores)
            tp, fp, fn, tn = data["tp"], data["fp"], data["fn"], data["tn"]

            label = ARCHETYPE_LABELS.get(arch, "negative")
            precision = round((tp / (tp + fp)) * 100, 1) if (tp + fp) > 0 else (100.0 if label == "negative" else 0.0)
            recall = round((tp / (tp + fn)) * 100, 1) if (tp + fn) > 0 else (100.0 if label == "negative" else 0.0)
            f1 = round((2 * precision * recall / (precision + recall)), 1) if (precision + recall) > 0 else 0.0
            alert_rate = round((tp + fp) / n * 100, 1) if n > 0 else 0.0

            per_archetype.append({
                "archetype": arch,
                "ground_truth": label,
                "count": n,
                "mean_dvi": mean_dvi,
                "min_dvi": min_dvi,
                "max_dvi": max_dvi,
                "alert_rate_pct": alert_rate,
                "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
            })

            if label in ("positive", "borderline"):
                total_tp += tp
                total_fn += fn
            else:
                total_fp += fp
                total_tn += tn

        # Micro-averaged overall metrics
        overall_precision = round((total_tp / (total_tp + total_fp)) * 100, 1) if (total_tp + total_fp) > 0 else 0.0
        overall_recall = round((total_tp / (total_tp + total_fn)) * 100, 1) if (total_tp + total_fn) > 0 else 0.0
        overall_f1 = round((2 * overall_precision * overall_recall / (overall_precision + overall_recall)), 1) if (overall_precision + overall_recall) > 0 else 0.0
        fp_rate = round((total_fp / (total_fp + total_tn)) * 100, 1) if (total_fp + total_tn) > 0 else 0.0

        result = {
            "title": "Tripwire DVI Model Validation — Per-Archetype Precision/Recall Analysis",
            "cohort_size": len(students),
            "alert_threshold": ALERT_THRESHOLD,
            "weights_used": CURRENT_WEIGHTS,
            "per_archetype": per_archetype,
            "overall": {
                "precision": overall_precision,
                "recall": overall_recall,
                "f1_score": overall_f1,
                "false_positive_rate": fp_rate,
                "tp": total_tp,
                "fp": total_fp,
                "fn": total_fn,
                "tn": total_tn,
            },
            "note": (
                "Prototype classification thresholds are decision-support indicators, not "
                "clinical diagnoses. Borderline archetypes (slow_decline, improver) are intentionally "
                "caught mid-drift to enable early mentorship before full disengagement."
            )
        }

        # Save JSON
        out_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(out_dir, "model_validation_results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"[OK] Model validation complete. JSON saved to: {json_path}")
        print(f"     Overall — Precision: {overall_precision}%  Recall: {overall_recall}%  F1: {overall_f1}%")
        return result

    finally:
        db.close()


if __name__ == "__main__":
    run_model_validation()
