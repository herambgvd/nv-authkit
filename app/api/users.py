"""
User management API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserAdminUpdate,
    UserListResponse,
    UserProfileResponse
)
from app.schemas.auth import MessageResponse
from app.dependencies.auth import get_current_user, get_current_superuser
from app.core.exceptions import (
    UserManagementException,
    create_http_exception
)
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    summary="Get user profile",
    description="Get current user's profile information."
)
async def get_profile(
        current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        bio=current_user.bio,
        avatar_url=current_user.avatar_url,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        full_name=current_user.full_name,
        display_name=current_user.display_name
    )


@router.put(
    "/profile",
    response_model=UserProfileResponse,
    summary="Update user profile",
    description="Update current user's profile information."
)
async def update_profile(
        user_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    try:
        user_service = UserService(db)
        updated_user = await user_service.update_user(current_user.id, user_data)

        return UserProfileResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            phone=updated_user.phone,
            bio=updated_user.bio,
            avatar_url=updated_user.avatar_url,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login,
            full_name=updated_user.full_name,
            display_name=updated_user.display_name
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.delete(
    "/profile",
    response_model=MessageResponse,
    summary="Delete user account",
    description="Delete current user's account."
)
async def delete_account(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Delete current user account."""
    try:
        user_service = UserService(db)
        await user_service.delete_user(current_user.id)
        return MessageResponse(message="Account deleted successfully")
    except UserManagementException as e:
        raise create_http_exception(e)


# Admin endpoints
@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users (Admin)",
    description="Get a list of users with filtering and pagination. Requires superuser privileges."
)
async def list_users(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        search: Optional[str] = Query(None, description="Search in email, username, first name, or last name"),
        is_active: Optional[bool] = Query(None, description="Filter by active status"),
        is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
        is_superuser: Optional[bool] = Query(None, description="Filter by superuser status"),
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """List users with filtering and pagination."""
    try:
        user_service = UserService(db)
        result = await user_service.get_users(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            is_verified=is_verified,
            is_superuser=is_superuser
        )

        users_response = [
            UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                bio=user.bio,
                avatar_url=user.avatar_url,
                is_active=user.is_active,
                is_verified=user.is_verified,
                is_superuser=user.is_superuser,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login,
                full_name=user.full_name,
                display_name=user.display_name
            )
            for user in result["users"]
        ]

        return UserListResponse(
            users=users_response,
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"],
            pages=result["pages"]
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID (Admin)",
    description="Get a specific user by ID. Requires superuser privileges."
)
async def get_user(
        user_id: uuid.UUID,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Get user by ID."""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            bio=user.bio,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            full_name=user.full_name,
            display_name=user.display_name
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user (Admin)",
    description="Update a specific user. Requires superuser privileges."
)
async def update_user(
        user_id: uuid.UUID,
        user_data: UserAdminUpdate,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Update user."""
    try:
        user_service = UserService(db)
        updated_user = await user_service.admin_update_user(user_id, user_data)

        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            phone=updated_user.phone,
            bio=updated_user.bio,
            avatar_url=updated_user.avatar_url,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            is_superuser=updated_user.is_superuser,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            last_login=updated_user.last_login,
            full_name=updated_user.full_name,
            display_name=updated_user.display_name
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete user (Admin)",
    description="Delete a specific user. Requires superuser privileges."
)
async def delete_user(
        user_id: uuid.UUID,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Delete user."""
    try:
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        user_service = UserService(db)
        await user_service.delete_user(user_id)
        return MessageResponse(message="User deleted successfully")
    except UserManagementException as e:
        raise create_http_exception(e)


@router.get(
    "/stats/overview",
    summary="Get user statistics (Admin)",
    description="Get user statistics overview. Requires superuser privileges."
)
async def get_user_stats(
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Get user statistics."""
    try:
        user_service = UserService(db)
        stats = await user_service.get_user_stats()
        return stats
    except UserManagementException as e:
        raise create_http_exception(e)