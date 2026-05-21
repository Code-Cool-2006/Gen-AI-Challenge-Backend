from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import *
from services import gemini_service
from database import get_db
from models import User
from utils.security import get_current_user

router = APIRouter(
    prefix="/api/career",
    tags=["Career Path"]
)

@router.post("/generate-roadmap", response_model=CareerPathResponse)
async def generate_user_career_roadmap(
    request: CareerPathRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates a step-by-step career roadmap for a given job title.
    Protected endpoint: requires JWT authentication.
    """

    # Validate input
    job_title = request.job_title.strip()
    if not job_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job title cannot be empty."
        )

    try:
        # AI call (async recommended)
        roadmap_text = await gemini_service.generate_career_path(job_title)

        # Validate AI response
        if not roadmap_text or roadmap_text.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI did not return a valid response."
            )

        if "error" in roadmap_text.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=roadmap_text
            )

        return CareerPathResponse(roadmap=roadmap_text)

    except HTTPException:
        # Pass FastAPI errors
        raise

    except Exception as e:
        print(f"Unexpected error while generating career roadmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while generating the career roadmap."
        )
