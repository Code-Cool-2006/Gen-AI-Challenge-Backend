from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import InterviewSession
from services import gemini_service
from utils.security import get_current_user

router = APIRouter(
    prefix="/api/interview",
    tags=["Mock Interview"]
)

class InterviewRequest(BaseModel):
    job_title: str
    experience_level: str

class InterviewResponse(BaseModel):
    question: str
    session_id: str

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

class AnswerResponse(BaseModel):
    feedback: str
    next_question: str
    session_id: str

@router.post("/start", response_model=InterviewResponse)
async def start_interview(
    request: InterviewRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Starts a new mock interview session.
    Protected endpoint: requires JWT authentication.
    """

    # Validate input
    job_title = request.job_title.strip()
    experience_level = request.experience_level.strip()

    if not job_title or not experience_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job title and experience level cannot be empty."
        )

    try:
        # Generate first question using AI
        first_question = await gemini_service.generate_interview_question(job_title, experience_level)

        # Validate AI response
        if not first_question or first_question.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI did not return a valid question."
            )

        # Create new interview session
        new_session = InterviewSession(
            user_id=current_user.user_id,
            job_title=job_title,
            experience_level=experience_level,
            current_question=first_question,
            status="active"
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return InterviewResponse(
            question=first_question,
            session_id=str(new_session.session_id)
        )

    except HTTPException:
        # Pass FastAPI errors
        raise

    except Exception as e:
        print(f"Unexpected error while starting interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while starting the interview."
        )

@router.post("/answer", response_model=AnswerResponse)
async def answer_question(
    request: AnswerRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Processes the user's answer and provides feedback + next question.
    Protected endpoint: requires JWT authentication.
    """

    # Validate input
    session_id = request.session_id.strip()
    answer = request.answer.strip()

    if not session_id or not answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID and answer cannot be empty."
        )

    try:
        # Load session
        session = db.query(InterviewSession).filter(InterviewSession.session_id == int(session_id)).first()

        if not session or session.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found."
            )

        if session.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session is not active."
            )

        # Generate feedback and next question using AI
        feedback, next_question = await gemini_service.process_interview_answer(
            session.current_question, answer, session.job_title, session.experience_level
        )

        # Validate AI response
        if not feedback or not next_question:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI did not return valid feedback or next question."
            )

        # Update session
        session.current_question = next_question
        db.commit()

        return AnswerResponse(
            feedback=feedback,
            next_question=next_question,
            session_id=session_id
        )

    except HTTPException:
        # Pass FastAPI errors
        raise

    except Exception as e:
        print(f"Unexpected error while processing answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing the answer."
        )

@router.post("/end")
async def end_interview(
    request: AnswerRequest,  # Reusing for session_id
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Ends the interview session.
    Protected endpoint: requires JWT authentication.
    """

    # Validate input
    session_id = request.session_id.strip()

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID cannot be empty."
        )

    try:
        # Load session
        session = db.query(InterviewSession).filter(InterviewSession.session_id == int(session_id)).first()

        if not session or session.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found."
            )

        # End session
        session.status = "completed"
        db.commit()

        return {"message": "Interview session ended successfully."}

    except HTTPException:
        # Pass FastAPI errors
        raise

    except Exception as e:
        print(f"Unexpected error while ending interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while ending the interview."
        )
