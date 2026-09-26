import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.infrastructure.db.models.user import UserRole


class UserSignupRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Unique and valid email address of the user",
        examples=["developer@company.com", "developer@gmail.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Unique alphanumeric username (letters, numbers, underscores, hyphens)",
        examples=["dev_gorge"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plaintext password with a minimum length of 8 characters",
        examples=["SecretPass123!"],
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Full display name of the user",
        examples=["Gorge Martin"],
    )
    role: UserRole = Field(
        default=UserRole.DEV,
        description="Role assigned to the user within the organization",
    )

class UserLoginRequest(BaseModel):
    username_or_email: str = Field(
        min_length=3,
        description="Username or email address of the user attempting to authenticate",
        examples=["dev_gorge"],
    )
    password: str = Field(
        min_length=1,
        description="User plaintext password",
        examples=["SecretPass123!"],
    )
    
class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Signed JWT Bearer access token")
    token_type: str = Field(default="bearer", description="Token authentication scheme")
    expires_in: int = Field(..., description="Access token expiration lifespan in seconds")

class UserResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique user identifier (UUID)")
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Unique username")
    full_name: Optional[str] = Field(None, description="Full display name")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    role: UserRole = Field(..., description="User role (CTO, PM, DEV, LEAD)")
    is_active: bool = Field(..., description="Account active status flag")
    is_verified: bool = Field(..., description="Email verification status flag")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = ConfigDict(from_attributes=True)
    