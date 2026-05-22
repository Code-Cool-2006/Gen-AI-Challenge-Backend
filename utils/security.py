import os
import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from collections import defaultdict

from dotenv import load_dotenv
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import User, LoginHistory, SecurityEvent, RateLimitRecord




# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# ============================================================
# JWT CONFIG
# ============================================================

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("❌ JWT_SECRET_KEY is missing in environment variables.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ============================================================
# PASSWORD HASHING — bcrypt with auto-upgrade
# ============================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# OAUTH2 TOKEN EXTRACTOR
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============================================================
# JWT TOKEN CREATION — includes role in payload
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ============================================================
# JWT VERIFICATION
# ============================================================

def verify_token(token: str, credentials_exception: HTTPException) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")

        if email is None:
            raise credentials_exception

        return {"email": email, "role": role}

    except JWTError:
        raise credentials_exception


# ============================================================
# DEPENDENCY: Get Current User
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.email == token_data["email"]).first()

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated"
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensures user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ============================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================

def require_role(*allowed_roles: str):
    """
    Dependency factory that checks if the current user has the required role.
    Usage: Depends(require_role("student", "company"))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}. Your role: {current_user.role}"
            )
        return current_user
    return role_checker


def require_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access only")
    return current_user


def require_institution(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "institution":
        raise HTTPException(status_code=403, detail="Institution access only")
    return current_user


def require_company(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "company":
        raise HTTPException(status_code=403, detail="Company access only")
    return current_user


def require_startup(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "startup":
        raise HTTPException(status_code=403, detail="Startup access only")
    return current_user


# ============================================================
# RATE LIMITING — In-memory + DB backed
# ============================================================

class RateLimiter:
    """In-memory rate limiter with configurable windows."""

    def __init__(self):
        self._requests = defaultdict(list)  # ip -> [timestamps]

    def is_rate_limited(self, ip: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        """Check if an IP has exceeded the rate limit."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)

        # Clean old entries
        self._requests[ip] = [
            ts for ts in self._requests[ip] if ts > window_start
        ]

        if len(self._requests[ip]) >= max_requests:
            return True

        self._requests[ip].append(now)
        return False

    def get_remaining(self, ip: str, max_requests: int = 60, window_seconds: int = 60) -> int:
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)
        self._requests[ip] = [
            ts for ts in self._requests[ip] if ts > window_start
        ]
        return max(0, max_requests - len(self._requests[ip]))


# Global rate limiter instances
general_limiter = RateLimiter()
auth_limiter = RateLimiter()  # Stricter for auth endpoints


# ============================================================
# BRUTE FORCE PROTECTION
# ============================================================

class BruteForceProtection:
    """Tracks failed login attempts per IP/email."""

    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 15):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self._attempts = defaultdict(list)  # key -> [timestamps]
        self._lockouts = {}  # key -> lockout_until

    def record_failure(self, key: str):
        now = datetime.now(timezone.utc)
        self._attempts[key].append(now)

        # Clean old entries (only keep last hour)
        cutoff = now - timedelta(hours=1)
        self._attempts[key] = [ts for ts in self._attempts[key] if ts > cutoff]

        if len(self._attempts[key]) >= self.max_attempts:
            self._lockouts[key] = now + timedelta(minutes=self.lockout_minutes)
            logger.warning(f"🔒 Brute force lockout triggered for: {key}")

    def is_locked(self, key: str) -> bool:
        if key in self._lockouts:
            if datetime.now(timezone.utc) < self._lockouts[key]:
                return True
            else:
                del self._lockouts[key]
                self._attempts.pop(key, None)
        return False

    def clear(self, key: str):
        self._attempts.pop(key, None)
        self._lockouts.pop(key, None)


brute_force = BruteForceProtection()


# ============================================================
# SECURITY AUDIT LOGGING
# ============================================================

def log_login_attempt(
    db: Session,
    user_id: Optional[int],
    ip_address: str,
    user_agent: str = "",
    login_method: str = "email",
    status_val: str = "success",
    failure_reason: str = None
):
    """Record a login attempt to the database."""
    try:
        record = LoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else "",
            login_method=login_method,
            status=status_val,
            failure_reason=failure_reason
        )
        db.add(record)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log login attempt: {e}")
        db.rollback()


def log_security_event(
    db: Session,
    event_type: str,
    severity: str = "low",
    source_ip: str = None,
    user_id: int = None,
    details: str = ""
):
    """Record a security event."""
    try:
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            details=details
        )
        db.add(event)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")
        db.rollback()


# ============================================================
# INPUT SANITIZATION
# ============================================================

def sanitize_input(value: str, max_length: int = 500) -> str:
    """Basic input sanitization against XSS and injection."""
    if not value:
        return value

    # Truncate
    value = value[:max_length]

    # Strip dangerous characters for basic XSS protection
    dangerous_patterns = ['<script', '</script', 'javascript:', 'onerror=', 'onload=', 'eval(']
    for pattern in dangerous_patterns:
        value = value.replace(pattern, '')
        value = value.replace(pattern.upper(), '')

    return value.strip()


# ============================================================
# CSRF TOKEN GENERATION
# ============================================================

def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a token for secure comparison."""
    return hashlib.sha256(token.encode()).hexdigest()


# ============================================================
# REQUEST HELPERS
# ============================================================

def get_client_ip(request: Request) -> str:
    """Extract real client IP, considering reverse proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
