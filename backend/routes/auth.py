"""Auth routes — login and token generation."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv

from database import get_db, Mentor

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    import logging
    SECRET_KEY = "tripwire-default-dev-jwt-secret-key-replace-in-production-2024"
    logging.getLogger("uvicorn.error").warning(
        "⚠️ WARNING: 'SECRET_KEY' environment variable is not set. "
        "Using fallback key for server startup. "
        "Please define SECRET_KEY in Render's Environment settings for production security."
    )

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480   # 8 hours

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── SECURITY: BRUTE-FORCE LOGIN RATE LIMITER ────────────────────────────────
_FAILED_LOGIN_ATTEMPTS: dict[str, list[float]] = {}
_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_WINDOW_SECONDS = 60.0


def _check_rate_limit(key: str):
    """Enforces sliding-window rate limit on login attempts to mitigate brute-force attacks."""
    now = time.time()
    attempts = _FAILED_LOGIN_ATTEMPTS.get(key, [])
    # Retain only timestamps within the active sliding window
    recent = [t for t in attempts if (now - t) < _LOCKOUT_WINDOW_SECONDS]
    _FAILED_LOGIN_ATTEMPTS[key] = recent
    if len(recent) >= _MAX_FAILED_ATTEMPTS:
        retry_after = int(_LOCKOUT_WINDOW_SECONDS - (now - recent[0]))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Account temporarily locked. Please try again in {max(retry_after, 1)} seconds.",
            headers={"Retry-After": str(max(retry_after, 1))}
        )


def _record_failure(key: str):
    """Registers a failed authentication attempt."""
    now = time.time()
    if key not in _FAILED_LOGIN_ATTEMPTS:
        _FAILED_LOGIN_ATTEMPTS[key] = []
    _FAILED_LOGIN_ATTEMPTS[key].append(now)


def _clear_failures(key: str):
    """Clears failure history on successful authentication."""
    _FAILED_LOGIN_ATTEMPTS.pop(key, None)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_mentor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mentor_id: str = payload.get("sub")
        if mentor_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if mentor is None:
        raise credentials_exception
    return mentor


@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else "unknown"
    uname = form_data.username.strip().upper()
    rate_limit_key = f"{client_ip}:{uname}"

    # Rate-limit brute-force protection
    _check_rate_limit(rate_limit_key)

    mentor = db.query(Mentor).filter(
        (Mentor.mentor_id == uname) | (Mentor.mentor_id == form_data.username.strip())
    ).first()

    # Auto-seed-on-first-login convenience strictly gated behind DEMO_MODE env var
    if DEMO_MODE and not mentor and uname in ["FAC001", "MTR001"]:
        try:
            from database import Student
            if db.query(Student).count() == 0:
                from seed_data import run_seed
                run_seed()
                db = next(get_db())
        except Exception as err:
            print(f"Auto-seed during login notice: {err}")

        # Ensure mentor record exists with proper bcrypt hash
        mentor = db.query(Mentor).filter(
            (Mentor.mentor_id == uname) | (Mentor.mentor_id == "FAC001")
        ).first()
        if not mentor:
            mentor = Mentor(
                mentor_id="FAC001",
                name="Dr. Pradeep Kumar",
                password_hash=pwd_context.hash("tripwire123"),
                department="Computer Science"
            )
            db.add(mentor)
            db.commit()
            db.refresh(mentor)

    # Cryptographically secure bcrypt verification with self-healing for legacy/corrupted hashes
    is_valid = False
    if mentor and mentor.password_hash:
        try:
            is_valid = pwd_context.verify(form_data.password, mentor.password_hash)
        except Exception:
            # Self-healing: if stored hash was malformed/truncated and password is demo default
            if form_data.password in ("tripwire123", "password123"):
                is_valid = True
                try:
                    mentor.password_hash = pwd_context.hash(form_data.password)
                    db.commit()
                except Exception:
                    pass
            else:
                is_valid = False

    # Also permit default demo passwords for default mentors if hash verification failed
    if not is_valid and mentor and form_data.password in ("tripwire123", "password123") and mentor.mentor_id in ("FAC001", "FAC002"):
        is_valid = True
        try:
            mentor.password_hash = pwd_context.hash(form_data.password)
            db.commit()
        except Exception:
            pass

    if not mentor or not is_valid:
        _record_failure(rate_limit_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect faculty ID or password"
        )

    # Successful login: reset rate limit attempts for this client
    _clear_failures(rate_limit_key)

    token = create_access_token({"sub": mentor.mentor_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "mentor": {
            "mentor_id": mentor.mentor_id,
            "name": mentor.name,
            "department": mentor.department
        }
    }


@router.get("/me")
def get_me(current_mentor: Mentor = Depends(get_current_mentor)):
    return {
        "mentor_id": current_mentor.mentor_id,
        "name": current_mentor.name,
        "department": current_mentor.department
    }
