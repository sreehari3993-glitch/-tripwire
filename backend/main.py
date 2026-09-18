"""
Tripwire FastAPI Backend — main.py
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import init_db
from routes.auth import router as auth_router
from routes.dashboard import router as dashboard_router
from routes.students import router as students_router
from routes.alerts import router as alerts_router
from routes.interventions import router as interventions_router
from routes.demo import router as demo_router
from routes.analytics import router as analytics_router

app = FastAPI(
    title="Tripwire API",
    description="Faculty Early-Intervention Dashboard — Behavioral Drift Detection Engine",
    version="1.0.0"
)

# ── SECURITY: RESTRICTED CORS WHITELIST ─────────────────────────────────────
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]
env_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
allowed_origins = list(set(DEFAULT_ORIGINS + env_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|.*\.onrender\.com|.*\.vercel\.app|.*\.netlify\.app)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# ── SECURITY: HTTP RESPONSE HEADERS MIDDLEWARE ──────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Enforces essential OWASP security headers across all API responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    return response

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()
    try:
        from database import SessionLocal, Student, Mentor
        from routes.auth import pwd_context
        db = SessionLocal()
        if db.query(Student).count() == 0:
            print("[*] Database is empty. Seeding initial demo data...")
            from seed_data import run_seed
            run_seed()
        else:
            # Self-healing: verify mentor hashes and repair if legacy/corrupted
            for mid in ["FAC001", "FAC002"]:
                m = db.query(Mentor).filter(Mentor.mentor_id == mid).first()
                if m:
                    try:
                        if not pwd_context.identify(m.password_hash):
                            m.password_hash = pwd_context.hash("tripwire123")
                    except Exception:
                        m.password_hash = pwd_context.hash("tripwire123")
            db.commit()
        db.close()
    except Exception as e:
        print(f"Startup seed notice: {e}")

# Routers (mounted directly and under /api for full compatibility)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(students_router)
app.include_router(alerts_router)
app.include_router(interventions_router)
app.include_router(demo_router)
app.include_router(analytics_router)

app.include_router(auth_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(interventions_router, prefix="/api")
app.include_router(demo_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")



@app.get("/")
def root():
    return {
        "system": "Tripwire",
        "version": "1.0.0",
        "status": "operational",
        "description": "Early-intervention behavioral drift detection system"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import sys
    import uvicorn
    # Ensure current directory is on Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    print("\n=======================================================")
    print("  TRIPWIRE FastAPI Backend Starting...")
    print("  URL:           http://127.0.0.1:8000 (or http://localhost:8000)")
    print("  API Docs:      http://127.0.0.1:8000/docs")
    print("  Frontend UI:   http://127.0.0.1:5173")
    print("=======================================================\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)

