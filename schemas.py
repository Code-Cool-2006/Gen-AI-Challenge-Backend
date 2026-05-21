from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

# --- Pydantic Schemas ---
# These models define the data shapes for API requests and responses.

# --- Base Schemas for Profile Items (for creation/update) ---

class SkillBase(BaseModel):
    skill_name: str = Field(..., max_length=100)
    proficiency: str = Field(..., pattern="^(Beginner|Intermediate|Advanced|Expert)$")

class ProjectBase(BaseModel):
    title: str = Field(..., max_length=150)
    description: Optional[str] = None
    tech_stack: Optional[str] = Field(None, max_length=200)
    project_link: Optional[str] = Field(None, max_length=200)

class ExperienceBase(BaseModel):
    company: str = Field(..., max_length=150)
    role: str = Field(..., max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    achievements: Optional[str] = None

class EducationBase(BaseModel):
    degree: str = Field(..., max_length=100)
    university: str = Field(..., max_length=150)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[Decimal] = Field(None, ge=0, le=4)

# --- Full Schemas (including IDs, for responses) ---

class SkillSchema(SkillBase):
    skill_id: int
    user_id: int

    class Config:
        from_attributes = True

class ProjectSchema(ProjectBase):
    project_id: int
    user_id: int

    class Config:
        from_attributes = True

class ExperienceSchema(ExperienceBase):
    exp_id: int
    user_id: int

    class Config:
        from_attributes = True

class EducationSchema(EducationBase):
    edu_id: int
    user_id: int

    class Config:
        from_attributes = True

class InterviewSessionSchema(BaseModel):
    session_id: int
    user_id: int
    question: Optional[str] = None
    user_answer: Optional[str] = None
    ai_feedback: Optional[str] = None
    score: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CareerScoreSchema(BaseModel):
    score_id: int
    user_id: int
    career_score: Optional[int] = None
    interview_success: Optional[Decimal] = None
    market_position: Optional[str] = None
    active_streak: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True

# --- User Schemas ---

class UserCreate(BaseModel):
    full_name: str = Field(..., max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field("free", pattern="^(free|pro)$")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# This is the main schema for returning user data.
# Notice how it includes lists of the other full schemas.
class UserSchema(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    role: str
    join_date: datetime
    last_login: Optional[datetime] = None
    skills: List[SkillSchema] = []
    projects: List[ProjectSchema] = []
    experience: List[ExperienceSchema] = []
    education: List[EducationSchema] = []
    interview_sessions: List[InterviewSessionSchema] = []
    career_score: Optional[CareerScoreSchema] = None

    class Config:
        from_attributes = True

# --- Token Schema ---

class Token(BaseModel):
    access_token: str
    token_type: str

# --- AI Feature Schemas ---

class CareerPathRequest(BaseModel):
    job_title: str

class CareerPathResponse(BaseModel):
    roadmap: str

class InterviewFeedbackRequest(BaseModel):
    question: str
    user_answer: str

class InterviewFeedbackResponse(BaseModel):
    session: InterviewSessionSchema

class MarketAnalysisResponse(BaseModel):
    salary_range: Optional[str] = None
    demand_level: Optional[str] = None
    growth_trend: Optional[str] = None
    key_skills: Optional[List[str]] = []
    recommendations: Optional[str] = None

