"""
Authentication schemas for request/response validation.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    """Token response schema."""
    
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    
    username: str = Field(..., description="Username")
    password: str = Field(..., min_length=1, description="Password")


class RegisterRequest(BaseModel):
    """User registration request schema."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    full_name: Optional[str] = Field(None, description="Full name")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    
    refresh_token: str = Field(..., description="Refresh token")


class UserResponse(BaseModel):
    """User response schema."""
    
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    role: str

