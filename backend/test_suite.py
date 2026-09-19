"""
Tripwire Comprehensive Test Suite
---------------------------------
Executes unit tests, integration tests, and edge case validations for:
1. DVI Drift Engine (formulas, weights, bounds, cold-start, counterfactuals, velocity)
2. Database Models & Schema Integrity
3. Authentication & Security (JWT, Password Hashing, Route Guards)
4. AI Layer (Fallback heuristics & prompt structuring)
5. FastAPI Endpoints (TestClient integration tests for all routes)
6. Error & Edge Case Handling (401, 404, invalid credentials)
"""

import os
import sys
import unittest
from datetime import date, timedelta

# Reconfigure stdout/stderr for Unicode characters on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure backend root is on sys.path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, Student, Mentor, TripwireAlert, Attendance, Assignment, LMSActivity, LeaveRecord
import dvi_engine
from routes.auth import pwd_context, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt


class TestDVIEngine(unittest.TestCase):
    """Unit tests for the Disengagement Velocity Index (DVI) Engine."""

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_weights_sum_to_one(self):
        """Weights must sum exactly to 1.0 (40% attendance + 35% submission + 25% engagement)."""
        total = dvi_engine.W_ATTENDANCE + dvi_engine.W_SUBMISSION + dvi_engine.W_ENGAGEMENT
        self.assertAlmostEqual(total, 1.0, places=5)

    def test_threshold_constants(self):
        """Verify standard prototype thresholds."""
        self.assertEqual(dvi_engine.THRESHOLD_TRIPWIRE, 70.0)
        self.assertEqual(dvi_engine.THRESHOLD_MONITOR, 50.0)
        self.assertEqual(dvi_engine.THRESHOLD_WATCH, 35.0)
        self.assertEqual(dvi_engine.THRESHOLD_HYSTERESIS_RECOVERY, 55.0)
        self.assertEqual(dvi_engine.THRESHOLD_HYSTERESIS_NORMAL, 40.0)

    def test_bayesian_cold_start_blending_zero_weeks(self):
        """Student with 0 weeks of data should fully blend with cohort medians."""
        mock_student = Student(
            student_id="TEST_001",
            baseline_attendance=90.0,
            baseline_submission_delay_hrs=4.0,
            baseline_lms_activity_per_week=10.0,
            weeks_of_data=0.0
        )
        baselines = dvi_engine.get_effective_baselines(mock_student)
        self.assertEqual(baselines["individual_weight"], 0.0)
        self.assertTrue(baselines["is_cold_start"])
        self.assertEqual(baselines["attendance"], dvi_engine.COHORT_MEDIANS["attendance"])

    def test_bayesian_cold_start_blending_full_data(self):
        """Student with >= 3 weeks of data should use 100% individual baseline."""
        mock_student = Student(
            student_id="TEST_002",
            baseline_attendance=85.0,
            baseline_submission_delay_hrs=6.0,
            baseline_lms_activity_per_week=9.0,
            weeks_of_data=4.0
        )
        baselines = dvi_engine.get_effective_baselines(mock_student)
        self.assertEqual(baselines["individual_weight"], 1.0)
        self.assertFalse(baselines["is_cold_start"])
        self.assertEqual(baselines["attendance"], 85.0)
        self.assertEqual(baselines["submission_delay_hrs"], 6.0)
        self.assertEqual(baselines["lms_per_week"], 9.0)

    def test_bayesian_cold_start_partial(self):
        """Student with 1.5 weeks should blend 50/50 with cohort medians."""
        mock_student = Student(
            student_id="TEST_003",
            baseline_attendance=80.0,
            weeks_of_data=1.5
        )
        baselines = dvi_engine.get_effective_baselines(mock_student)
        self.assertEqual(baselines["individual_weight"], 0.5)
        self.assertEqual(baselines["attendance"], 86.0)

    def test_velocity_labels(self):
        """Verify velocity label mapping returns strings."""
        for val in [95.0, 75.0, 55.0, 35.0, 10.0]:
            label = dvi_engine._velocity_label(val)
            self.assertIsInstance(label, str)
            self.assertGreater(len(label), 0)

    def test_compute_dvi_structure_and_bounds(self):
        """compute_dvi should return valid bounds [0.0, 100.0] and complete breakdown."""
        student = self.db.query(Student).first()
        self.assertIsNotNone(student)
        result = dvi_engine.compute_dvi(self.db, student)

        self.assertIn("dvi", result)
        self.assertIn("status", result)
        self.assertIn("components", result)
        self.assertIn("weights", result)
        self.assertIn("smoothing", result)
        self.assertIn("hysteresis", result)

        self.assertGreaterEqual(result["dvi"], 0.0)
        self.assertLessEqual(result["dvi"], 100.0)
        self.assertIn(result["status"], ["tripwire", "monitoring", "recovering", "normal"])

    def test_counterfactual_engine(self):
        """compute_counterfactual should compute actionable recovery steps."""
        student = self.db.query(Student).first()
        self.assertIsNotNone(student)
        cf = dvi_engine.compute_counterfactual(self.db, student)

        self.assertIn("current_dvi", cf)
        self.assertIn("scenarios", cf)
        self.assertIn("summary", cf)
        self.assertIn("disclaimer", cf)
        self.assertIn("threshold", cf)

    def test_dvi_not_frozen_post_intervention(self):
        """DVI must not freeze to post_dvi; it must continue to dynamically compute from telemetry."""
        from database import Intervention, TripwireAlert
        student = self.db.query(Student).first()
        self.assertIsNotNone(student)

        # Retrieve or create an intervention for this student with an artificial post_dvi value
        alert = self.db.query(TripwireAlert).filter(TripwireAlert.student_id == student.student_id).first()
        if not alert:
            alert = TripwireAlert(
                student_id=student.student_id,
                dvi_score=75.0,
                status="active"
            )
            self.db.add(alert)
            self.db.commit()

        from datetime import datetime
        inv = Intervention(
            alert_id=alert.alert_id,
            mentor_id="FAC001",
            contact_date=datetime.now(),
            outcome="Contacted",
            notes="Test intervention",
            post_dvi=12.3  # distinct artificial value
        )
        self.db.add(inv)
        self.db.commit()

        try:
            result = dvi_engine.compute_dvi(self.db, student)
            # DVI must be computed from smoothed component telemetry, NOT frozen to 12.3
            self.assertEqual(result["dvi"], result["smoothed_dvi"])
            self.assertNotEqual(result["dvi"], 12.3)
        finally:
            self.db.delete(inv)
            self.db.commit()



class TestDatabaseIntegrity(unittest.TestCase):
    """Tests for database connectivity and data consistency."""

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_students_loaded(self):
        """Database should have seeded cohort students."""
        count = self.db.query(Student).count()
        self.assertGreater(count, 0, "Database has 0 students! Needs seeding.")

    def test_mentors_loaded(self):
        """Mentor table should contain default faculty account FAC001."""
        mentor = self.db.query(Mentor).filter(Mentor.mentor_id == "FAC001").first()
        self.assertIsNotNone(mentor, "Default mentor FAC001 missing in DB.")

    def test_tripwire_alerts_exist(self):
        """Alerts should exist in database."""
        alerts = self.db.query(TripwireAlert).all()
        self.assertGreater(len(alerts), 0, "No alerts found in database.")

    def test_student_archetypes_valid(self):
        """Archetypes must match the 7 archetypes produced by seed_data.py."""
        valid_archetypes = {
            "normal", "improver", "slow_decline", "rapid_decline",
            "excused", "recovery", "monitoring"
        }
        students = self.db.query(Student).all()
        for s in students:
            if s.archetype:
                self.assertIn(s.archetype, valid_archetypes, f"Unknown archetype: {s.archetype}")

    def test_attendance_records_valid(self):
        """Attendance records should have valid status."""
        records = self.db.query(Attendance).limit(100).all()
        self.assertGreater(len(records), 0)
        for r in records:
            self.assertIn(r.status, ["present", "absent", "late", "excused"])


class TestAuthAndSecurity(unittest.TestCase):
    """Tests for password hashing, JWT creation, and validation."""

    def test_password_hash_and_verify(self):
        """Verify bcrypt password hashing."""
        password = "tripwire_secure_pass"
        hashed = pwd_context.hash(password)
        self.assertTrue(pwd_context.verify(password, hashed))
        self.assertFalse(pwd_context.verify("wrong_password", hashed))

    def test_jwt_token_generation_and_decode(self):
        """JWT access token should encode and decode subject correctly."""
        token = create_access_token({"sub": "FAC001", "role": "faculty"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(payload["sub"], "FAC001")
        self.assertEqual(payload["role"], "faculty")
        self.assertIn("exp", payload)

    def test_security_headers_present(self):
        """Verify OWASP recommended security headers on responses."""
        client = TestClient(app)
        res = client.get("/health")
        self.assertEqual(res.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(res.headers.get("x-frame-options"), "DENY")
        self.assertEqual(res.headers.get("x-xss-protection"), "1; mode=block")
        self.assertEqual(res.headers.get("referrer-policy"), "strict-origin-when-cross-origin")
        self.assertIn("geolocation=()", res.headers.get("permissions-policy", ""))

    def test_brute_force_login_rate_limiting(self):
        """After 5 consecutive failed login attempts, 6th attempt is throttled with HTTP 429."""
        client = TestClient(app)
        dummy_user = "BRUTE_FORCE_TEST_USER"
        for _ in range(5):
            client.post("/auth/login", data={"username": dummy_user, "password": "wrong_password_123"})
        blocked = client.post("/auth/login", data={"username": dummy_user, "password": "wrong_password_123"})
        self.assertEqual(blocked.status_code, 429)
        self.assertIn("Retry-After", blocked.headers)

    def test_no_hardcoded_password_backdoor(self):
        """Even for default faculty accounts, an incorrect password must always be rejected."""
        client = TestClient(app)
        res = client.post("/auth/login", data={"username": "FAC001", "password": "wrongpassword"})
        self.assertEqual(res.status_code, 401)

    def test_unregistered_account_without_demo_mode_rejected(self):
        """Unregistered mentor login attempt must fail with 401 when DEMO_MODE is false."""
        client = TestClient(app)
        res = client.post("/auth/login", data={"username": "UNREGISTERED_FACULTY", "password": "tripwire123"})
        self.assertEqual(res.status_code, 401)


class TestAPIEndpoints(unittest.TestCase):
    """Integration tests across all FastAPI endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Obtain auth token for FAC001
        login_res = cls.client.post("/auth/login", data={"username": "FAC001", "password": "tripwire123"})
        if login_res.status_code == 200:
            cls.token = login_res.json().get("access_token")
            cls.auth_headers = {"Authorization": f"Bearer {cls.token}"}
        else:
            cls.token = None
            cls.auth_headers = {}

    def test_root_endpoint(self):
        """GET / returns system operational status."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["system"], "Tripwire")
        self.assertEqual(data["status"], "operational")

    def test_health_endpoint(self):
        """GET /health returns 200 healthy."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "healthy"})

    def test_login_success(self):
        """POST /auth/login with valid credentials returns access token."""
        res = self.client.post("/auth/login", data={"username": "FAC001", "password": "tripwire123"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

    def test_login_invalid_password(self):
        """POST /auth/login with invalid password returns 401."""
        res = self.client.post("/auth/login", data={"username": "FAC001", "password": "wrong_password"})
        self.assertEqual(res.status_code, 401)

    def test_unauthorized_access_rejected(self):
        """Accessing protected endpoint without token returns 401."""
        res = self.client.get("/students")
        self.assertEqual(res.status_code, 401)

    def test_get_current_mentor(self):
        """GET /auth/me returns authenticated faculty profile."""
        res = self.client.get("/auth/me", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["mentor_id"], "FAC001")

    def test_dashboard_summary(self):
        """GET /dashboard/summary returns student and alert distribution."""
        res = self.client.get("/dashboard/summary", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_students", data)
        self.assertIn("tripwire", data)
        self.assertIn("monitoring", data)
        self.assertGreater(data["total_students"], 0)

    def test_get_all_students(self):
        """GET /students returns student roster."""
        res = self.client.get("/students", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("students", data)
        self.assertIsInstance(data["students"], list)
        self.assertGreater(len(data["students"]), 0)

    def test_get_student_detail(self):
        """GET /students/{id} returns comprehensive profile data."""
        students_res = self.client.get("/students", headers=self.auth_headers)
        first_stu = students_res.json()["students"][0]
        stu_id = first_stu["student_id"]

        res = self.client.get(f"/students/{stu_id}", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["student_id"], stu_id)
        self.assertIn("dvi", data)
        self.assertIn("signals", data)

    def test_get_student_timeline(self):
        """GET /students/{id}/timeline returns event timeline."""
        students_res = self.client.get("/students", headers=self.auth_headers)
        stu_id = students_res.json()["students"][0]["student_id"]
        res = self.client.get(f"/students/{stu_id}/timeline", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("events", data)
        self.assertIsInstance(data["events"], list)

    def test_get_student_dvi_history(self):
        """GET /students/{id}/dvi-history returns time series data."""
        students_res = self.client.get("/students", headers=self.auth_headers)
        stu_id = students_res.json()["students"][0]["student_id"]
        res = self.client.get(f"/students/{stu_id}/dvi-history", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("history", data)
        self.assertIsInstance(data["history"], list)

    def test_get_student_not_found(self):
        """GET /students/NON_EXISTENT returns 404."""
        res = self.client.get("/students/DOES_NOT_EXIST_999", headers=self.auth_headers)
        self.assertEqual(res.status_code, 404)

    def test_get_alerts_list(self):
        """GET /alerts returns list of alerts."""
        res = self.client.get("/alerts", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("alerts", data)
        self.assertIsInstance(data["alerts"], list)
        self.assertGreater(len(data["alerts"]), 0)

    def test_get_alert_detail(self):
        """GET /alerts/{id} returns single alert detail."""
        alerts_res = self.client.get("/alerts", headers=self.auth_headers)
        alert_id = alerts_res.json()["alerts"][0]["alert_id"]

        res = self.client.get(f"/alerts/{alert_id}", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["alert_id"], alert_id)
        self.assertIn("components", data)

    def test_submit_alert_feedback(self):
        """POST /alerts/{id}/feedback saves faculty verification."""
        alerts_res = self.client.get("/alerts", headers=self.auth_headers)
        alert_id = alerts_res.json()["alerts"][0]["alert_id"]

        payload = {
            "was_accurate": "accurate",
            "was_useful": 5,
            "free_text_comment": "Automated test feedback: Alert accurately detected drift."
        }
        res = self.client.post(f"/alerts/{alert_id}/feedback", json=payload, headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success") or data.get("succes"))
        self.assertIn("feedback", data)

    def test_get_alert_feedback(self):
        """GET /alerts/{id}/feedback returns recorded feedback."""
        alerts_res = self.client.get("/alerts", headers=self.auth_headers)
        alert_id = alerts_res.json()["alerts"][0]["alert_id"]

        res = self.client.get(f"/alerts/{alert_id}/feedback", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)

    def test_ai_explain_endpoint(self):
        """POST /alerts/{id}/ai-explain returns generated explanation."""
        alerts_res = self.client.get("/alerts", headers=self.auth_headers)
        alert_id = alerts_res.json()["alerts"][0]["alert_id"]

        res = self.client.post(f"/alerts/{alert_id}/ai-explain", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("explanation", data)

    def test_interventions_by_student(self):
        """GET /interventions/student/{id} returns interventions for student."""
        students_res = self.client.get("/students", headers=self.auth_headers)
        stu_id = students_res.json()["students"][0]["student_id"]
        res = self.client.get(f"/interventions/student/{stu_id}", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("interventions", data)

    def test_demo_stages_endpoint(self):
        """GET /demo/stages returns the 6-stage demo progression."""
        res = self.client.get("/demo/stages")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("total_stages"), 6)
        self.assertEqual(len(data.get("stages", [])), 6)
        self.assertEqual(data.get("data_source"), "scripted_demo")

    def test_analytics_endpoints(self):
        """GET /analytics/model-validation, weight-validation, trust-score return reports."""
        res_model = self.client.get("/analytics/model-validation")
        self.assertEqual(res_model.status_code, 200)
        data_model = res_model.json()
        self.assertIn("overall", data_model)
        self.assertIn("f1_score", data_model["overall"])

        res_weight = self.client.get("/analytics/weight-validation")
        self.assertEqual(res_weight.status_code, 200)

        res_trust = self.client.get("/analytics/trust-score")
        self.assertEqual(res_trust.status_code, 200)
        data_trust = res_trust.json()
        self.assertIn("status", data_trust)
        self.assertIn("overall_trust_score", data_trust)

    def test_trust_score_empty_state(self):
        """When no feedback is recorded, GET /analytics/trust-score returns honest empty state without fake defaults."""
        from unittest.mock import MagicMock
        from database import get_db
        from main import app

        def override_empty_db():
            mock_db = MagicMock()
            mock_query = MagicMock()
            mock_db.query.return_value = mock_query
            mock_query.join.return_value.all.return_value = []
            yield mock_db

        app.dependency_overrides[get_db] = override_empty_db
        try:
            res = self.client.get("/analytics/trust-score")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "no_feedback_yet")
            self.assertIsNone(data["overall_trust_score"])
            self.assertEqual(data["total_feedback_count"], 0)
            self.assertEqual(data["trust_score_trend"], [])
            self.assertIsNone(data["false_positive_rate"])
            self.assertIsNone(data["accurate_rate"])
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_simulation_pitch_endpoints(self):
        """P1: Live simulation endpoints test drift trigger, alert creation, recovery, and reset."""
        res = self.client.get("/students", headers=self.auth_headers)
        students = res.json()["students"]
        # Pick any normal student
        test_student = next(s for s in students if s["status"] in ["normal", "monitoring"])
        stu_id = test_student["student_id"]

        # 1. Simulate drift
        drift_res = self.client.post(f"/students/{stu_id}/simulate-drift", headers=self.auth_headers)
        self.assertEqual(drift_res.status_code, 200)
        d_data = drift_res.json()
        self.assertTrue(d_data["success"])
        self.assertGreaterEqual(d_data["dvi"], 70.0)
        self.assertTrue(d_data["alert_id"] is not None)

        # 2. Simulate recovery
        rec_res = self.client.post(f"/students/{stu_id}/simulate-recovery", headers=self.auth_headers)
        self.assertEqual(rec_res.status_code, 200)
        r_data = rec_res.json()
        self.assertTrue(r_data["success"])
        self.assertLess(r_data["dvi"], 65.0)

        # 3. Simulate reset
        reset_res = self.client.post(f"/students/{stu_id}/simulate-reset", headers=self.auth_headers)
        self.assertEqual(reset_res.status_code, 200)
        rst_data = reset_res.json()
        self.assertTrue(rst_data["success"])


class TestAccessControlIDOR(unittest.TestCase):
    """Verifies that mentors cannot access or modify students/alerts belonging to other mentors (mitigating IDOR)."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        db = SessionLocal()
        try:
            # Ensure FAC002 exists
            m2 = db.query(Mentor).filter(Mentor.mentor_id == "FAC002").first()
            if not m2:
                m2 = Mentor(
                    mentor_id="FAC002",
                    name="Dr. Sarah Thomas",
                    password_hash=pwd_context.hash("tripwire123"),
                    department="Information Technology"
                )
                db.add(m2)
                db.commit()

            # Ensure a student exists belonging to FAC002
            s_other = db.query(Student).filter(Student.student_id == "TEST_FAC2_001").first()
            if not s_other:
                s_other = Student(
                    student_id="TEST_FAC2_001",
                    name="Other Student",
                    section="IT S1",
                    roll_no="IT24099",
                    mentor_id="FAC002",
                    archetype="normal"
                )
                db.add(s_other)
                db.commit()

            # Ensure an alert exists belonging to FAC002's student
            alt_other = db.query(TripwireAlert).filter(TripwireAlert.student_id == "TEST_FAC2_001").first()
            if not alt_other:
                from datetime import datetime
                alt_other = TripwireAlert(
                    student_id="TEST_FAC2_001",
                    dvi_score=75.0,
                    trigger_date=datetime.utcnow(),
                    status="active"
                )
                db.add(alt_other)
                db.commit()
                db.refresh(alt_other)

            cls.other_student_id = "TEST_FAC2_001"
            cls.other_alert_id = alt_other.alert_id
        finally:
            db.close()

        # FAC001 token
        token1 = create_access_token({"sub": "FAC001", "role": "faculty"})
        cls.fac1_headers = {"Authorization": f"Bearer {token1}"}

    def test_cross_mentor_student_profile_404(self):
        res = self.client.get(f"/students/{self.other_student_id}", headers=self.fac1_headers)
        self.assertEqual(res.status_code, 404)

    def test_cross_mentor_student_timeline_404(self):
        res = self.client.get(f"/students/{self.other_student_id}/timeline", headers=self.fac1_headers)
        self.assertEqual(res.status_code, 404)

    def test_cross_mentor_student_dvi_history_404(self):
        res = self.client.get(f"/students/{self.other_student_id}/dvi-history", headers=self.fac1_headers)
        self.assertEqual(res.status_code, 404)

    def test_cross_mentor_alert_detail_404(self):
        res = self.client.get(f"/alerts/{self.other_alert_id}", headers=self.fac1_headers)
        self.assertEqual(res.status_code, 404)

    def test_cross_mentor_alert_feedback_404(self):
        res = self.client.get(f"/alerts/{self.other_alert_id}/feedback", headers=self.fac1_headers)
        self.assertEqual(res.status_code, 404)

    def test_cross_mentor_alert_excuse_404(self):
        res = self.client.post(f"/alerts/{self.other_alert_id}/excuse", headers=self.fac1_headers)
        self.assertEqual(res.status_code, 404)

    def test_cross_mentor_interventions_by_student_404(self):
        res = self.client.get(f"/interventions/student/{self.other_student_id}", headers=self.fac1_headers)
        self.assertEqual(res.status_code, 404)


def run_all_tests():
    """Run all tests with a verbose runner."""
    print("=" * 70)
    print("           TRIPWIRE SYSTEM TEST SUITE RUNNER")
    print("=" * 70)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestDVIEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthAndSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestAccessControlIDOR))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    test_result = run_all_tests()
    if not test_result.wasSuccessful():
        sys.exit(1)
