from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.user import Role


class UserBaseSchema(BaseModel):
    email: EmailStr

class UserCreateSchema(UserBaseSchema):
    password: str = Field(min_length=6) #TODO: add proper password validator later

class UserSchema(UserBaseSchema):
    id: UUID
    role: Role
    is_verified: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class VerifyEmailRequestSchema(BaseModel):
    email: EmailStr
    code: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(min_length=6) #TODO: add proper password validator later

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

class ProfileSchema(ProfileBaseSchema):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)

class ProfileCreateSchema(ProfileBaseSchema):
    pass

class ProfileUpdateSchema(ProfileBaseSchema):
    pass

# Schema for full dashboard view (includes all nested data)
class UserFullSchema(UserSchema):
    profile: Optional[ProfileSchema] = None
