from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from ..models.auth_models import (
    UserSignUpRequest, UserSignInRequest, UserResponse, AuthResponse,
    RefreshTokenRequest, PasswordResetRequest, PasswordUpdateRequest,
    UserProfileUpdateRequest
)
from services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme for Bearer token
security = HTTPBearer()

# Initialize auth service
auth_service = AuthService()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    try:
        token = credentials.credentials
        return auth_service.get_current_user(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/signup", response_model=AuthResponse)
async def sign_up(user_data: UserSignUpRequest):
    """Register a new user account"""
    try:
        result = await auth_service.sign_up(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )
        
        return AuthResponse(
            user=UserResponse(**result["user"]),
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign up error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/signin", response_model=AuthResponse)
async def sign_in(user_data: UserSignInRequest):
    """Sign in with existing user account"""
    try:
        result = await auth_service.sign_in(
            email=user_data.email,
            password=user_data.password
        )
        
        return AuthResponse(
            user=UserResponse(**result["user"]),
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign in error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/signout")
async def sign_out(current_user: dict = Depends(get_current_user)):
    """Sign out the current user"""
    return {"message": "Successfully signed out"}

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        result = await auth_service.refresh_token(refresh_data.refresh_token)
        
        return AuthResponse(
            user=UserResponse(**result["user"]),
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refresh token error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/reset-password")
async def reset_password(reset_data: PasswordResetRequest):
    """Send password reset email"""
    try:
        await auth_service.reset_password(reset_data.email)
        return {"message": "Password reset email sent successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/update-password")
async def update_password(
    password_data: PasswordUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update user password"""
    try:
        await auth_service.update_password("", password_data.password)
        return {"message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update password error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile information"""
    try:
        result = await auth_service.update_profile(
            "",
            first_name=profile_data.first_name,
            last_name=profile_data.last_name
        )
        
        return UserResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

@router.get("/health")
async def auth_health_check():
    """Check authentication service health"""
    return {"status": "healthy", "service": "authentication"}