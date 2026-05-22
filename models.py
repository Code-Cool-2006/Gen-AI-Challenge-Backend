from sqlalchemy import (Column, Integer, String, Text, Date, DateTime,
                        ForeignKey, Enum, DECIMAL, JSON, Boolean, Float)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base



# ============================================================
# CORE USER MODEL — Supports 4 Portal Roles
# ============================================================

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    firebase_uid = Column(String(128), unique=True, nullable=True, index=True)
    role = Column(Enum('student', 'institution', 'company', 'startup'), default='student')
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
    join_date = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)

    # --- Relationships ---
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    career_score = relationship("CareerScore", back_populates="user", uselist=False, cascade="all, delete-orphan")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")

    # Portal-specific profile relationships (one-to-one)
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    institution_profile = relationship("InstitutionProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    company_profile = relationship("CompanyProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    startup_profile = relationship("StartupProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


# ============================================================
# PORTAL-SPECIFIC PROFILE MODELS
# ============================================================

class StudentProfile(Base):
    __tablename__ = 'student_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    college = Column(String(200))
    degree = Column(String(100))
    branch = Column(String(100))
    year_of_study = Column(String(10))
    cgpa = Column(DECIMAL(4, 2), nullable=True)
    phone = Column(String(20), nullable=True)
    github_url = Column(String(300), nullable=True)
    linkedin_url = Column(String(300), nullable=True)
    portfolio_url = Column(String(300), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    preferred_job_type = Column(Enum('full-time', 'internship', 'freelance', 'remote'), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="student_profile")


class InstitutionProfile(Base):
    __tablename__ = 'institution_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    institution_name = Column(String(200), nullable=False)
    institution_type = Column(Enum('university', 'college', 'training_center', 'bootcamp'), default='college')
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    website = Column(String(300), nullable=True)
    phone = Column(String(20), nullable=True)
    accreditation = Column(String(200), nullable=True)
    established_year = Column(Integer, nullable=True)
    total_students = Column(Integer, nullable=True)
    logo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="institution_profile")
    mentors = relationship("Mentor", back_populates="institution", cascade="all, delete-orphan")
    teachers = relationship("TeacherProfile", back_populates="institution", cascade="all, delete-orphan")


class CompanyProfile(Base):
    __tablename__ = 'company_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100), nullable=True)
    company_size = Column(Enum('1-10', '11-50', '51-200', '201-500', '500+'), nullable=True)
    website = Column(String(300), nullable=True)
    phone = Column(String(20), nullable=True)
    headquarters = Column(String(200), nullable=True)
    founded_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(300), nullable=True)
    tech_stack = Column(Text, nullable=True)
    open_positions = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="company_profile")
    internships = relationship("Internship", back_populates="company", cascade="all, delete-orphan")
    job_postings = relationship("JobPosting", back_populates="company", cascade="all, delete-orphan")


class StartupProfile(Base):
    __tablename__ = 'startup_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    startup_name = Column(String(200), nullable=False)
    tagline = Column(String(300), nullable=True)
    sector = Column(String(100), nullable=True)
    stage = Column(Enum('idea', 'mvp', 'seed', 'series_a', 'series_b', 'growth'), default='idea')
    founded_year = Column(Integer, nullable=True)
    team_size = Column(Integer, nullable=True)
    website = Column(String(300), nullable=True)
    pitch_deck_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    funding_raised = Column(DECIMAL(15, 2), default=0)
    funding_goal = Column(DECIMAL(15, 2), nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="startup_profile")
    pitches = relationship("Pitch", back_populates="startup", cascade="all, delete-orphan")


# ============================================================
# EXISTING MODELS (preserved from original)
# ============================================================

class Skill(Base):
    __tablename__ = 'skills'

    skill_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    skill_name = Column(String(100), nullable=False)
    proficiency = Column(Enum('Beginner', 'Intermediate', 'Advanced', 'Expert'))

    user = relationship("User", back_populates="skills")


class Project(Base):
    __tablename__ = 'projects'

    project_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    title = Column(String(150), nullable=False)
    description = Column(Text)
    tech_stack = Column(String(200))
    project_link = Column(String(200))

    user = relationship("User", back_populates="projects")


class Experience(Base):
    __tablename__ = 'experience'

    exp_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    company = Column(String(150), nullable=False)
    role = Column(String(100), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    achievements = Column(Text)

    user = relationship("User", back_populates="experience")


class Education(Base):
    __tablename__ = 'education'

    edu_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    degree = Column(String(100), nullable=False)
    university = Column(String(150), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    gpa = Column(DECIMAL(3, 2))

    user = relationship("User", back_populates="education")


class InterviewSession(Base):
    __tablename__ = 'interview_sessions'

    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    job_title = Column(String(100))
    experience_level = Column(String(50))
    current_question = Column(Text)
    status = Column(String(20), default='active')
    question = Column(Text)
    user_answer = Column(Text)
    ai_feedback = Column(Text)
    score = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="interview_sessions")


class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    activity_type = Column(String(50))
    details = Column(Text)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="activity_logs")


class CareerScore(Base):
    __tablename__ = 'career_scores'

    score_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    career_score = Column(Integer)
    interview_success = Column(DECIMAL(5, 2))
    market_position = Column(String(50))
    active_streak = Column(Integer)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="career_score")


class MarketTrend(Base):
    __tablename__ = 'market_trends'

    trend_id = Column(Integer, primary_key=True, index=True)
    role = Column(String(100))
    avg_salary_range = Column(String(50))
    demand_score = Column(Integer)
    skills_required = Column(JSON)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ============================================================
# SECURITY & AUDIT MODELS
# ============================================================

class LoginHistory(Base):
    __tablename__ = 'login_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    ip_address = Column(String(45))
    user_agent = Column(String(500), nullable=True)
    login_method = Column(Enum('email', 'google', 'firebase'), default='email')
    status = Column(Enum('success', 'failed', 'blocked'), default='success')
    failure_reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="login_history")


class RateLimitRecord(Base):
    __tablename__ = 'rate_limit_records'

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), index=True)
    endpoint = Column(String(200))
    request_count = Column(Integer, default=1)
    window_start = Column(DateTime, server_default=func.now())
    blocked_until = Column(DateTime, nullable=True)


class SecurityEvent(Base):
    __tablename__ = 'security_events'

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50))  # brute_force, suspicious_login, data_breach_attempt
    severity = Column(Enum('low', 'medium', 'high', 'critical'), default='low')
    source_ip = Column(String(45), nullable=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    details = Column(Text)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


# ============================================================
# INSTITUTION-SPECIFIC MODELS
# ============================================================

class Mentor(Base):
    __tablename__ = 'mentors'

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey('institution_profiles.id'))
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    expertise = Column(String(200))
    bio = Column(Text, nullable=True)
    rate_per_hour = Column(DECIMAL(10, 2), nullable=True)
    rating = Column(DECIMAL(3, 2), default=0)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    institution = relationship("InstitutionProfile", back_populates="mentors")


class TeacherProfile(Base):
    __tablename__ = 'teacher_profiles'

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey('institution_profiles.id'))
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    specialization = Column(String(200))
    qualification = Column(String(200), nullable=True)
    experience_years = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    portfolio_data = Column(JSON, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    institution = relationship("InstitutionProfile", back_populates="teachers")


# ============================================================
# COMPANY-SPECIFIC MODELS
# ============================================================

class Internship(Base):
    __tablename__ = 'internships'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('company_profiles.id'))
    title = Column(String(150), nullable=False)
    description = Column(Text)
    duration = Column(String(50))
    stipend = Column(String(50), nullable=True)
    skills_required = Column(Text)
    location = Column(String(100), nullable=True)
    is_remote = Column(Boolean, default=False)
    positions = Column(Integer, default=1)
    status = Column(Enum('open', 'closed', 'filled'), default='open')
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("CompanyProfile", back_populates="internships")


class JobPosting(Base):
    __tablename__ = 'job_postings'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('company_profiles.id'))
    title = Column(String(150), nullable=False)
    description = Column(Text)
    job_type = Column(Enum('full-time', 'part-time', 'contract', 'internship'), default='full-time')
    experience_required = Column(String(50))
    salary_range = Column(String(100), nullable=True)
    skills_required = Column(Text)
    location = Column(String(100))
    is_remote = Column(Boolean, default=False)
    status = Column(Enum('active', 'closed', 'draft'), default='active')
    applications_count = Column(Integer, default=0)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("CompanyProfile", back_populates="job_postings")


# ============================================================
# PITCH GALLERY MODELS
# ============================================================

class Pitch(Base):
    __tablename__ = 'pitches'

    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey('startup_profiles.id'))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    video_url = Column(String(500), nullable=True)
    deck_url = Column(String(500), nullable=True)
    ask_amount = Column(DECIMAL(15, 2), nullable=True)
    equity_offered = Column(DECIMAL(5, 2), nullable=True)
    status = Column(Enum('draft', 'live', 'funded', 'closed'), default='draft')
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    startup = relationship("StartupProfile", back_populates="pitches")


class Competition(Base):
    __tablename__ = 'competitions'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    organizer = Column(String(200))
    description = Column(Text)
    prize = Column(String(200), nullable=True)
    eligibility = Column(Text, nullable=True)
    registration_url = Column(String(500), nullable=True)
    deadline = Column(Date, nullable=True)
    event_date = Column(Date, nullable=True)
    category = Column(String(100), nullable=True)
    status = Column(Enum('upcoming', 'ongoing', 'completed'), default='upcoming')
    created_at = Column(DateTime, server_default=func.now())


class FundingOpportunity(Base):
    __tablename__ = 'funding_opportunities'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    funding_type = Column(Enum('grant', 'angel', 'vc', 'crowdfunding', 'government'), default='grant')
    amount = Column(String(100), nullable=True)
    description = Column(Text)
    eligibility = Column(Text, nullable=True)
    source = Column(String(200), nullable=True)
    application_url = Column(String(500), nullable=True)
    deadline = Column(Date, nullable=True)
    status = Column(Enum('open', 'closed'), default='open')
    created_at = Column(DateTime, server_default=func.now())
