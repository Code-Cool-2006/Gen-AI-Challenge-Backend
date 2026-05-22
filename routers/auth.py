import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import (
    UserCreate, UserSchema, Token, UserRole,
    StudentRegister, InstitutionRegister, CompanyRegister, StartupRegister,
    StudentProfileCreate, InstitutionProfileCreate, CompanyProfileCreate, StartupProfileCreate
)
from database import get_db
from models import User, StudentProfile, InstitutionProfile, CompanyProfile, StartupProfile
from utils.security import (


    hash_password, verify_password, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, get_client_ip,
    auth_limiter, brute_force, log_login_attempt, log_security_event,
    sanitize_input
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# ============================================================
# REGISTER — Universal endpoint with role-based profile creation
# ============================================================

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)

    # Rate limit registration (max 5 per minute per IP)
    if auth_limiter.is_rate_limited(client_ip, max_requests=5, window_seconds=60):
        log_security_event(db, "rate_limit_register", "medium", client_ip,
                           details="Registration rate limit exceeded")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )

    # Check existing email
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Sanitize inputs
    clean_name = sanitize_input(user_data.full_name, max_length=100)

    # Create user
    new_user = User(
        full_name=clean_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role.value if isinstance(user_data.role, UserRole) else user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"✅ New user registered: {new_user.email} as {new_user.role}")
    return new_user


# ============================================================
# REGISTER — Role-specific endpoints
# ============================================================

@router.post("/register/student", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_student(data: StudentRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)

    if auth_limiter.is_rate_limited(client_ip, max_requests=5, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=sanitize_input(data.full_name),
        email=data.email,
        password_hash=hash_password(data.password),
        role="student"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create student profile if provided
    if data.profile:
        profile = StudentProfile(
            user_id=new_user.user_id,
            college=data.profile.college,
            degree=data.profile.degree,
            branch=data.profile.branch,
            year_of_study=data.profile.year_of_study,
            cgpa=data.profile.cgpa,
            phone=data.profile.phone,
            github_url=data.profile.github_url,
            linkedin_url=data.profile.linkedin_url,
            portfolio_url=data.profile.portfolio_url,
            bio=data.profile.bio,
            location=data.profile.location,
            preferred_job_type=data.profile.preferred_job_type.value if data.profile.preferred_job_type else None,
        )
        db.add(profile)
        db.commit()
        db.refresh(new_user)

    logger.info(f"✅ Student registered: {new_user.email}")
    return new_user


@router.post("/register/institution", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_institution(data: InstitutionRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)

    if auth_limiter.is_rate_limited(client_ip, max_requests=5, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=sanitize_input(data.full_name),
        email=data.email,
        password_hash=hash_password(data.password),
        role="institution"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if data.profile:
        profile = InstitutionProfile(
            user_id=new_user.user_id,
            institution_name=data.profile.institution_name,
            institution_type=data.profile.institution_type.value if data.profile.institution_type else "college",
            address=data.profile.address,
            city=data.profile.city,
            state=data.profile.state,
            website=data.profile.website,
            phone=data.profile.phone,
            accreditation=data.profile.accreditation,
            established_year=data.profile.established_year,
            total_students=data.profile.total_students,
            description=data.profile.description,
        )
        db.add(profile)
        db.commit()
        db.refresh(new_user)

    logger.info(f"✅ Institution registered: {new_user.email}")
    return new_user


@router.post("/register/company", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_company(data: CompanyRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)

    if auth_limiter.is_rate_limited(client_ip, max_requests=5, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=sanitize_input(data.full_name),
        email=data.email,
        password_hash=hash_password(data.password),
        role="company"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if data.profile:
        profile = CompanyProfile(
            user_id=new_user.user_id,
            company_name=data.profile.company_name,
            industry=data.profile.industry,
            company_size=data.profile.company_size.value if data.profile.company_size else None,
            website=data.profile.website,
            phone=data.profile.phone,
            headquarters=data.profile.headquarters,
            founded_year=data.profile.founded_year,
            description=data.profile.description,
            linkedin_url=data.profile.linkedin_url,
            tech_stack=data.profile.tech_stack,
        )
        db.add(profile)
        db.commit()
        db.refresh(new_user)

    logger.info(f"✅ Company registered: {new_user.email}")
    return new_user


@router.post("/register/startup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_startup(data: StartupRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)

    if auth_limiter.is_rate_limited(client_ip, max_requests=5, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=sanitize_input(data.full_name),
        email=data.email,
        password_hash=hash_password(data.password),
        role="startup"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if data.profile:
        profile = StartupProfile(
            user_id=new_user.user_id,
            startup_name=data.profile.startup_name,
            tagline=data.profile.tagline,
            sector=data.profile.sector,
            stage=data.profile.stage.value if data.profile.stage else "idea",
            founded_year=data.profile.founded_year,
            team_size=data.profile.team_size,
            website=data.profile.website,
            pitch_deck_url=data.profile.pitch_deck_url,
            video_url=data.profile.video_url,
            description=data.profile.description,
        )
        db.add(profile)
        db.commit()
        db.refresh(new_user)

    logger.info(f"✅ Startup registered: {new_user.email}")
    return new_user


# ============================================================
# LOGIN — with brute force protection and audit logging
# ============================================================

@router.post("/login", response_model=Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")

    # Rate limit login (max 10 per minute per IP)
    if auth_limiter.is_rate_limited(client_ip, max_requests=10, window_seconds=60):
        log_security_event(db, "rate_limit_login", "medium", client_ip,
                           details="Login rate limit exceeded")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )

    # Check brute force lockout
    lockout_key = f"login:{client_ip}:{form_data.username}"
    if brute_force.is_locked(lockout_key):
        log_security_event(db, "brute_force_blocked", "high", client_ip,
                           details=f"Blocked login for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed attempts. Try again in 15 minutes."
        )

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        brute_force.record_failure(lockout_key)
        log_login_attempt(db, user.user_id if user else None, client_ip,
                          user_agent, "email", "failed", "Invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Contact support."
        )

    # Clear brute force on successful login
    brute_force.clear(lockout_key)

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Log successful login
    log_login_attempt(db, user.user_id, client_ip, user_agent, "email", "success")

    # Create token with role
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.user_id},
        expires_delta=token_expires
    )

    logger.info(f"✅ Login successful: {user.email} ({user.role})")

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.user_id,
        "full_name": user.full_name
    }


# ============================================================
# GET CURRENT USER PROFILE
# ============================================================

@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ============================================================
# FIREBASE AUTH BRIDGE — validates Firebase token, creates/returns JWT
# ============================================================

@router.post("/firebase-login", response_model=Token)
def firebase_login(request: Request, db: Session = Depends(get_db)):
    """
    Bridge endpoint: Frontend sends Firebase ID token,
    backend validates and returns a FastAPI JWT with role info.
    This keeps both auth systems in sync.
    """
    # For now, this is a placeholder — Firebase token validation
    # requires firebase-admin SDK which can be added as needed
    raise HTTPException(
        status_code=501,
        detail="Firebase bridge login not yet implemented. Use email/password login."
    )
