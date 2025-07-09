"""
Authentication dependencies for FastAPI endpoints.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.exceptions import CREDENTIALS_EXCEPTION, INSUFFICIENT_PERMISSIONS_EXCEPTION

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    if not credentials:
        raise CREDENTIALS_EXCEPTION

    try:
        auth_service = AuthService(db)
        user = await auth_service.validate_token(credentials.credentials)

        if not user:
            raise CREDENTIALS_EXCEPTION

        return user
    except Exception:
        raise CREDENTIALS_EXCEPTION


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
        current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user


async def get_current_superuser(
        current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise INSUFFICIENT_PERMISSIONS_EXCEPTION
    return current_user


async def get_optional_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None

    try:
        auth_service = AuthService(db)
        user = await auth_service.validate_token(credentials.credentials)
        return user
    except Exception:
        return None