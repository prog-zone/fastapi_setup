from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class SkillBase(BaseModel):
    name: str
    proficiency: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)


class ApplicationPreferencesBase(BaseModel):
    gender: Optional[str] = None
    race_ethnicity: Optional[str] = None
    veteran_status: Optional[str] = None
    disability_status: Optional[str] = None
    authorized_to_work: Optional[bool] = None
    requires_sponsorship: Optional[bool] = None
    notice_period: Optional[str] = None

class ApplicationPreferencesCreate(ApplicationPreferencesBase):
    pass

class ApplicationPreferences(ApplicationPreferencesBase):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)
    

class EducationBase(BaseModel):
    school: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class Education(EducationBase):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)


class ExperienceBase(BaseModel):
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class ExperienceCreate(ExperienceBase):
    pass

class Experience(ExperienceBase):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    title: str
    link: Optional[str] = None
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)


class ProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None
    resume_path: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str # Plain text from request, will be hashed before saving

class User(UserBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Schema for full dashboard view (includes all nested data)
class UserFull(User):
    profile: Optional[Profile] = None
    experience: List[Experience] = []
    projects: List[Project] = []
    skills: List[Skill] = []
    preferences: Optional[ApplicationPreferences] = None


class TokenRequest(BaseModel):
    refresh_token: str