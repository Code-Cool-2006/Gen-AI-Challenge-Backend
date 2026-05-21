from sqlalchemy import (Column, Integer, String, Text, Date, DateTime, 
                        ForeignKey, Enum, DECIMAL, JSON)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

# --- Database Models ---
# Each class represents a table in the database.

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(Enum('free', 'pro'), default='free')
    join_date = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)

    # --- Relationships ---
    # These attributes allow you to easily access related data.
    # For example, `user.skills` will give you a list of all skills for that user.
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    # A user can have only one career score record (one-to-one relationship)
    career_score = relationship("CareerScore", back_populates="user", uselist=False, cascade="all, delete-orphan")


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

