import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from fastapi import HTTPException, status
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AuthService:
    """Supabase authentication service"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        # Initialize Supabase client only if credentials are available
        if self.supabase_url and self.supabase_key:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            self._initialized = True
        else:
            logger.warning("SUPABASE_URL and SUPABASE_ANON_KEY not set. Authentication features will be disabled.")
            self.supabase = None
            self._initialized = False
    
    def _check_initialization(self):
        """Check if the service is properly initialized"""
        if not self._initialized:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )
    
    async def sign_up(self, email: str, password: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user"""
        self._check_initialization()
        
        try:
            # Create user with Supabase
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name
                    }
                }
            })
            
            if response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "created_at": response.user.created_at,
                        "updated_at": response.user.updated_at
                    },
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
                )
                
        except Exception as e:
            logger.error(f"Sign up error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user"""
        self._check_initialization()
        
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "first_name": response.user.user_metadata.get("first_name"),
                        "last_name": response.user.user_metadata.get("last_name"),
                        "created_at": response.user.created_at,
                        "updated_at": response.user.updated_at
                    },
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
                
        except Exception as e:
            logger.error(f"Sign in error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out user"""
        self._check_initialization()
        
        try:
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"Sign out error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to sign out"
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        self._check_initialization()
        
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.user and response.session:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "first_name": response.user.user_metadata.get("first_name"),
                        "last_name": response.user.user_metadata.get("last_name"),
                        "created_at": response.user.created_at,
                        "updated_at": response.user.updated_at
                    },
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
                
        except Exception as e:
            logger.error(f"Refresh token error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        self._check_initialization()
        
        try:
            self.supabase.auth.reset_password_email(email)
            return True
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send password reset email"
            )
    
    async def update_password(self, access_token: str, new_password: str) -> bool:
        """Update user password"""
        self._check_initialization()
        
        try:
            # Set the access token for the session
            self.supabase.auth.set_session(access_token, None)
            
            # Update password
            response = self.supabase.auth.update_user({
                "password": new_password
            })
            
            return response.user is not None
            
        except Exception as e:
            logger.error(f"Update password error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update password"
            )
    
    async def update_profile(self, access_token: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict[str, Any]:
        """Update user profile"""
        self._check_initialization()
        
        try:
            # Set the access token for the session
            self.supabase.auth.set_session(access_token, None)
            
            # Update user metadata
            user_data = {}
            if first_name is not None:
                user_data["first_name"] = first_name
            if last_name is not None:
                user_data["last_name"] = last_name
            
            response = self.supabase.auth.update_user({
                "data": user_data
            })
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "first_name": response.user.user_metadata.get("first_name"),
                    "last_name": response.user.user_metadata.get("last_name"),
                    "created_at": response.user.created_at,
                    "updated_at": response.user.updated_at
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update profile"
                )
                
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
    
    async def get_current_user(self, access_token: str) -> Dict[str, Any]:
        """Get current user information"""
        self._check_initialization()
        
        try:
            # Set the access token for the session
            self.supabase.auth.set_session(access_token, None)
            
            # Get user
            user = self.supabase.auth.get_user()
            
            if user.user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "first_name": user.user.user_metadata.get("first_name"),
                    "last_name": user.user.user_metadata.get("last_name"),
                    "created_at": user.user.created_at,
                    "updated_at": user.user.updated_at
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token"
                )
                
        except Exception as e:
            logger.error(f"Get current user error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            ) 