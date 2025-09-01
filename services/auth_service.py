import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from fastapi import HTTPException, status
import logging
from dotenv import load_dotenv

# Import ORM models for local database integration
from db.orms.profiles import ProfileCRUD, Profile

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AuthService:
    """Supabase authentication service with local database integration"""
    
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
    
    async def sign_up(self, email: str, password: str, first_name: Optional[str] = None, last_name: Optional[str] = None, role: str = "student") -> Dict[str, Any]:
        """Register a new user with both Supabase and local database"""
        self._check_initialization()
        
        try:
            # Step 1: Create user with Supabase Auth
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": role
                    }
                }
            })
            
            if response.user:
                # Step 2: Create profile in local database
                profile_data = {
                    "user_id": response.user.id,
                    "role": role,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email
                }
                
                try:
                    # Create local user profile
                    local_profile = ProfileCRUD.create_profile(profile_data)
                    logger.info(f"Created local profile for user {response.user.id} with role {role}")
                except Exception as e:
                    logger.error(f"Failed to create local profile: {e}")
                    # Continue with Supabase user creation but log the error
                    # In production, you might want to rollback the Supabase user creation
                
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": role,
                        "created_at": str(response.user.created_at) if response.user.created_at else None,
                        "updated_at": str(response.user.updated_at) if response.user.updated_at else None
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
        """Sign in user and sync with local database"""
        self._check_initialization()
        
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                # Sync user data with local database
                try:
                    local_profile = ProfileCRUD.get_profile_by_user_id(response.user.id)
                    role = local_profile.role if local_profile else "student"
                except Exception as e:
                    logger.error(f"Failed to get local profile: {e}")
                    role = "student"
                
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "first_name": response.user.user_metadata.get("first_name"),
                        "last_name": response.user.user_metadata.get("last_name"),
                        "role": role,
                        "created_at": str(response.user.created_at) if response.user.created_at else None,
                        "updated_at": str(response.user.updated_at) if response.user.updated_at else None
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
                # Get role from local database
                try:
                    local_profile = ProfileCRUD.get_profile_by_user_id(response.user.id)
                    role = local_profile.role if local_profile else "student"
                except Exception as e:
                    logger.error(f"Failed to get local profile: {e}")
                    role = "student"
                
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "first_name": response.user.user_metadata.get("first_name"),
                        "last_name": response.user.user_metadata.get("last_name"),
                        "role": role,
                        "created_at": str(response.user.created_at) if response.user.created_at else None,
                        "updated_at": str(response.user.updated_at) if response.user.updated_at else None
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
        """Update user profile in both Supabase and local database"""
        self._check_initialization()
        
        try:
            # Set the access token for the session
            self.supabase.auth.set_session(access_token, None)
            
            # Get current user
            user = self.supabase.auth.get_user()
            if not user.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token"
                )
            
            # Update user metadata in Supabase
            user_data = {}
            if first_name is not None:
                user_data["first_name"] = first_name
            if last_name is not None:
                user_data["last_name"] = last_name
            
            response = self.supabase.auth.update_user({
                "data": user_data
            })
            
            if response.user:
                # Update local database profile
                try:
                    update_data = {}
                    if first_name is not None:
                        update_data["first_name"] = first_name
                    if last_name is not None:
                        update_data["last_name"] = last_name
                    
                    if update_data:
                        ProfileCRUD.update_profile(response.user.id, update_data)
                        logger.info(f"Updated local profile for user {response.user.id}")
                except Exception as e:
                    logger.error(f"Failed to update local profile: {e}")
                
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "first_name": response.user.user_metadata.get("first_name"),
                    "last_name": response.user.user_metadata.get("last_name"),
                    "created_at": str(response.user.created_at) if response.user.created_at else None,
                    "updated_at": str(response.user.updated_at) if response.user.updated_at else None
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
        """Get current user information from both Supabase and local database"""
        self._check_initialization()
        
        try:
            # Set the access token for the session
            self.supabase.auth.set_session(access_token, None)
            
            # Get user from Supabase
            user = self.supabase.auth.get_user()
            
            if user.user:
                # Get additional data from local database
                try:
                    local_profile = ProfileCRUD.get_profile_by_user_id(user.user.id)
                    role = local_profile.role if local_profile else "student"
                except Exception as e:
                    logger.error(f"Failed to get local profile: {e}")
                    role = "student"
                
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "first_name": user.user.user_metadata.get("first_name"),
                    "last_name": user.user.user_metadata.get("last_name"),
                    "role": role,
                    "created_at": str(user.user.created_at) if user.user.created_at else None,
                    "updated_at": str(user.user.updated_at) if user.user.updated_at else None
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