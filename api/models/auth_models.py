from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSignUpRequest(BaseModel):
    """User registration request model"""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "student"  # Default role is student

class UserSignInRequest(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    created_at: str
    updated_at: str

class AuthResponse(BaseModel):
    """Authentication response model"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr

class PasswordUpdateRequest(BaseModel):
    """Password update request model"""
    password: str

class UserProfileUpdateRequest(BaseModel):
    """User profile update request model"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None 