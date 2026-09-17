"""Auth routes — login and token generation."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

from database import get_db, Mentor

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "tripwire-super-secret-key")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480   # 8 hours for hackathon

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    uname = form_data.username.strip().upper()
    mentor = db.query(Mentor).filter((Mentor.mentor_id == uname) | (Mentor.mentor_id == form_data.username.strip())).first()

    # If demo mentor doesn't exist yet on fresh cloud DB, auto-provision and seed!
    if not mentor and uname in ["FAC001", "MTR001"] and form_data.password == "tripwire123":
        try:
            from database import Student
            if db.query(Student).count() == 0:
                from seed_data import run_seed
                run_seed()
                db = next(get_db())
        except Exception as err:
            print(f"Auto-seed during login notice: {err}")

        # Ensure mentor record exists
        mentor = db.query(Mentor).filter((Mentor.mentor_id == uname) | (Mentor.mentor_id == "FAC001")).first()
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

    # Validate password (support direct demo match or bcrypt hash)
    is_valid = False
    if form_data.password == "tripwire123" and uname in ["FAC001", "MTR001"]:
        is_valid = True
    elif mentor:
        try:
            is_valid = pwd_context.verify(form_data.password, mentor.password_hash)
        except Exception:
            is_valid = (form_data.password == "tripwire123")

    if not mentor or not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect faculty ID or password"
        )

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
