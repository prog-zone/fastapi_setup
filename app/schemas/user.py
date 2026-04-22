from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class ProfileBaseSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None

class ProfileCreateSchema(ProfileBaseSchema):
    pass

class ProfileSchema(ProfileBaseSchema):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)


class UserBaseSchema(BaseModel):
    email: EmailStr

class UserCreateSchema(UserBaseSchema):
    password: str # Plain text from request, will be hashed before saving

class UserSchema(UserBaseSchema):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Schema for full dashboard view (includes all nested data)
class UserFullSchema(UserSchema):
    profile: Optional[ProfileSchema] = None


class VerifyEmailRequestSchema(BaseModel):
    email: EmailStr
    code: str


class TokenRequestSchema(BaseModel):
    refresh_token: str