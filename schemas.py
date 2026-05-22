from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum

# ============================================================
# ENUMS
# ============================================================

class UserRole(str, PyEnum):
    student = "student"
    institution = "institution"
    company = "company"
    startup = "startup"

class JobType(str, PyEnum):
    full_time = "full-time"
    internship = "internship"
    freelance = "freelance"
    remote = "remote"

class InstitutionType(str, PyEnum):
    university = "university"
    college = "college"
    training_center = "training_center"
    bootcamp = "bootcamp"

class CompanySize(str, PyEnum):
    tiny = "1-10"
    small = "11-50"
    medium = "51-200"
    large = "201-500"
    enterprise = "500+"

class StartupStage(str, PyEnum):
    idea = "idea"
    mvp = "mvp"
    seed = "seed"
    series_a = "series_a"
    series_b = "series_b"
    growth = "growth"

# ============================================================
# AUTH SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    full_name: str = Field(..., max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.student

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class FirebaseAuthRequest(BaseModel):
    firebase_token: str
    role: Optional[UserRole] = UserRole.student

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# ============================================================
# PROFILE SCHEMAS — Student
# ============================================================

class StudentProfileCreate(BaseModel):
    college: Optional[str] = Field(None, max_length=200)
    degree: Optional[str] = Field(None, max_length=100)
    branch: Optional[str] = Field(None, max_length=100)
    year_of_study: Optional[str] = Field(None, max_length=10)
    cgpa: Optional[Decimal] = Field(None, ge=0, le=10)
    phone: Optional[str] = Field(None, max_length=20)
    github_url: Optional[str] = Field(None, max_length=300)
    linkedin_url: Optional[str] = Field(None, max_length=300)
    portfolio_url: Optional[str] = Field(None, max_length=300)
    bio: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    preferred_job_type: Optional[JobType] = None

class StudentProfileSchema(StudentProfileCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ============================================================
# PROFILE SCHEMAS — Institution
# ============================================================

class InstitutionProfileCreate(BaseModel):
    institution_name: str = Field(..., max_length=200)
    institution_type: Optional[InstitutionType] = InstitutionType.college
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=300)
    phone: Optional[str] = Field(None, max_length=20)
    accreditation: Optional[str] = Field(None, max_length=200)
    established_year: Optional[int] = None
    total_students: Optional[int] = None
    description: Optional[str] = None

class InstitutionProfileSchema(InstitutionProfileCreate):
    id: int
    user_id: int
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ============================================================
# PROFILE SCHEMAS — Company
# ============================================================

class CompanyProfileCreate(BaseModel):
    company_name: str = Field(..., max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[CompanySize] = None
    website: Optional[str] = Field(None, max_length=300)
    phone: Optional[str] = Field(None, max_length=20)
    headquarters: Optional[str] = Field(None, max_length=200)
    founded_year: Optional[int] = None
    description: Optional[str] = None
    linkedin_url: Optional[str] = Field(None, max_length=300)
    tech_stack: Optional[str] = None

class CompanyProfileSchema(CompanyProfileCreate):
    id: int
    user_id: int
    logo_url: Optional[str] = None
    open_positions: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ============================================================
# PROFILE SCHEMAS — Startup
# ============================================================

class StartupProfileCreate(BaseModel):
    startup_name: str = Field(..., max_length=200)
    tagline: Optional[str] = Field(None, max_length=300)
    sector: Optional[str] = Field(None, max_length=100)
    stage: Optional[StartupStage] = StartupStage.idea
    founded_year: Optional[int] = None
    team_size: Optional[int] = None
    website: Optional[str] = Field(None, max_length=300)
    pitch_deck_url: Optional[str] = Field(None, max_length=500)
    video_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None

class StartupProfileSchema(StartupProfileCreate):
    id: int
    user_id: int
    logo_url: Optional[str] = None
    funding_raised: Optional[Decimal] = 0
    funding_goal: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ============================================================
# REGISTRATION WITH PROFILE (combined)
# ============================================================

class StudentRegister(UserCreate):
    role: UserRole = UserRole.student
    profile: Optional[StudentProfileCreate] = None

class InstitutionRegister(UserCreate):
    role: UserRole = UserRole.institution
    profile: Optional[InstitutionProfileCreate] = None

class CompanyRegister(UserCreate):
    role: UserRole = UserRole.company
    profile: Optional[CompanyProfileCreate] = None

class StartupRegister(UserCreate):
    role: UserRole = UserRole.startup
    profile: Optional[StartupProfileCreate] = None

# ============================================================
# EXISTING SCHEMAS (preserved)
# ============================================================

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

# --- Full User Schema ---
class UserSchema(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool = True
    is_verified: bool = False
    avatar_url: Optional[str] = None
    join_date: datetime
    last_login: Optional[datetime] = None
    skills: List[SkillSchema] = []
    projects: List[ProjectSchema] = []
    experience: List[ExperienceSchema] = []
    education: List[EducationSchema] = []
    interview_sessions: List[InterviewSessionSchema] = []
    career_score: Optional[CareerScoreSchema] = None
    student_profile: Optional[StudentProfileSchema] = None
    institution_profile: Optional[InstitutionProfileSchema] = None
    company_profile: Optional[CompanyProfileSchema] = None
    startup_profile: Optional[StartupProfileSchema] = None

    class Config:
        from_attributes = True

# ============================================================
# AI FEATURE SCHEMAS
# ============================================================

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

# ============================================================
# DASHBOARD STAT SCHEMAS
# ============================================================

class DashboardStats(BaseModel):
    total_users: int = 0
    active_sessions: int = 0
    career_score: Optional[int] = None

class StudentDashboardStats(DashboardStats):
    resumes_analyzed: int = 0
    interviews_completed: int = 0
    jobs_matched: int = 0
    skills_count: int = 0
    projects_count: int = 0

class InstitutionDashboardStats(DashboardStats):
    total_mentors: int = 0
    total_teachers: int = 0
    total_students: int = 0
    placement_rate: Optional[float] = None

class CompanyDashboardStats(DashboardStats):
    open_positions: int = 0
    total_applicants: int = 0
    internships_active: int = 0
    resumes_scanned: int = 0

class StartupDashboardStats(DashboardStats):
    active_pitches: int = 0
    total_views: int = 0
    competitions_joined: int = 0
    funding_progress: Optional[float] = None
