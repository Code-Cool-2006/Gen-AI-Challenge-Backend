from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import User
from schemas import UserSchema
from utils.security import verify_token

# -----------------------------------------------------------
# Router Setup
# -----------------------------------------------------------

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

# OAuth2 dependency (expects: Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# -----------------------------------------------------------
# Get Current User (JWT Auth)
# -----------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Verify token and extract email
    email = verify_token(token, credentials_exception)

    # 2. Load user
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise credentials_exception

    return user


# -----------------------------------------------------------
# Routes
# -----------------------------------------------------------

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Returns the profile of the currently logged-in user.

    - Protected endpoint
    - Returns UserSchema (safe, without password)
    """
    return current_user
