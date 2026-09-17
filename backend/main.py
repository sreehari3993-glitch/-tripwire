"""
Tripwire FastAPI Backend — main.py
"""
from fastapi import FastAPI
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

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()
    try:
        from database import SessionLocal, Student
        db = SessionLocal()
        if db.query(Student).count() == 0:
            print("[*] Database is empty. Seeding initial demo data...")
            from seed_data import run_seed
            run_seed()
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
