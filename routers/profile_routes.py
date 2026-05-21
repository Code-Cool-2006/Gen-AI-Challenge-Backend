from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from typing import List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import SkillBase, SkillSchema, ProjectBase, ProjectSchema, ExperienceBase, ExperienceSchema, EducationBase, EducationSchema
from database import get_db
from models import User, Skill, Project, Experience, Education
from utils.security import get_current_user

# ------------------------------------------------------------
# Router Setup
# ------------------------------------------------------------

router = APIRouter(
    prefix="/api/profile",
    tags=["Profile Management"]
)


# ------------------------------------------------------------
# Helper – Detect primary key automatically (fixed version)
# ------------------------------------------------------------

def get_profile_item(db: Session, model, item_id: int, user_id: int):
    """
    Automatically detects the primary key field of the model.
    Works for Skill, Project, Experience, Education, etc.
    """
    pk_column = inspect(model).primary_key[0]

    item = db.query(model).filter(
        model.user_id == user_id,
        pk_column == item_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found"
        )

    return item


# ------------------------------------------------------------
# SKILLS — CRUD
# ------------------------------------------------------------

@router.post("/skills", response_model=SkillSchema, status_code=status.HTTP_201_CREATED)
def add_skill(skill_data: SkillBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_skill = Skill(**skill_data.model_dump(), user_id=current_user.user_id)
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill


@router.put("/skills/{skill_id}", response_model=SkillSchema)
def update_skill(skill_id: int, skill_data: SkillBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    skill = get_profile_item(db, Skill, skill_id, current_user.user_id)
    skill.skill_name = skill_data.skill_name
    skill.proficiency = skill_data.proficiency

    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    skill = get_profile_item(db, Skill, skill_id, current_user.user_id)
    db.delete(skill)
    db.commit()
    return


# ------------------------------------------------------------
# PROJECTS — CRUD
# ------------------------------------------------------------

@router.post("/projects", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
def add_project(project_data: ProjectBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_project = Project(**project_data.model_dump(), user_id=current_user.user_id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.put("/projects/{project_id}", response_model=ProjectSchema)
def update_project(project_id: int, project_data: ProjectBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_profile_item(db, Project, project_id, current_user.user_id)

    for field, value in project_data.model_dump().items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_profile_item(db, Project, project_id, current_user.user_id)
    db.delete(project)
    db.commit()
    return


# ------------------------------------------------------------
# EXPERIENCE — CRUD
# ------------------------------------------------------------

@router.post("/experience", response_model=ExperienceSchema, status_code=status.HTTP_201_CREATED)
def add_experience(exp_data: ExperienceBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_exp = Experience(**exp_data.model_dump(), user_id=current_user.user_id)
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return new_exp


@router.put("/experience/{exp_id}", response_model=ExperienceSchema)
def update_experience(exp_id: int, exp_data: ExperienceBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exp = get_profile_item(db, Experience, exp_id, current_user.user_id)

    for field, value in exp_data.model_dump().items():
        setattr(exp, field, value)

    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/experience/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(exp_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exp = get_profile_item(db, Experience, exp_id, current_user.user_id)
    db.delete(exp)
    db.commit()
    return


# ------------------------------------------------------------
# EDUCATION — CRUD
# ------------------------------------------------------------

@router.post("/education", response_model=EducationSchema, status_code=status.HTTP_201_CREATED)
def add_education(edu_data: EducationBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_edu = Education(**edu_data.model_dump(), user_id=current_user.user_id)
    db.add(new_edu)
    db.commit()
    db.refresh(new_edu)
    return new_edu


@router.put("/education/{edu_id}", response_model=EducationSchema)
def update_education(edu_id: int, edu_data: EducationBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    edu = get_profile_item(db, Education, edu_id, current_user.user_id)

    for field, value in edu_data.model_dump().items():
        setattr(edu, field, value)

    db.commit()
    db.refresh(edu)
    return edu


@router.delete("/education/{edu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(edu_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    edu = get_profile_item(db, Education, edu_id, current_user.user_id)
    db.delete(edu)
    db.commit()
    return
