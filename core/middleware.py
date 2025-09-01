from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from services.auth_service import AuthService

logger = logging.getLogger(__name__)

security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(request: Request) -> Optional[dict]:
    """
    Middleware to get current authenticated user from request headers
    """
    try:
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        # Extract token
        token = auth_header.split(" ")[1]
        if not token:
            return None
        
        # Get user from token
        user = await auth_service.get_current_user(token)
        return user
        
    except Exception as e:
        logger.error(f"Auth middleware error: {e}")
        return None

def require_auth(func):
    """
    Decorator to require authentication for endpoints
    """
    async def wrapper(*args, **kwargs):
        # This is a simplified decorator - in practice you'd want to pass the request
        # For now, we'll handle auth in the route dependencies
        return await func(*args, **kwargs)
    return wrapper 