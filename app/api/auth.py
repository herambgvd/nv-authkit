"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    ChangePasswordRequest,
    MessageResponse
)
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_user
from app.core.exceptions import (
    UserManagementException,
    create_http_exception
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account. An email verification will be sent."
)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    try:
        auth_service = AuthService(db)
        user = await auth_service.register_user(user_data)

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


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return access and refresh tokens."
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """User login."""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.login_user(login_data)
        return tokens
    except UserManagementException as e:
        raise create_http_exception(e)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get a new access token using refresh token."
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.refresh_access_token(refresh_data.refresh_token)
        return tokens
    except UserManagementException as e:
        raise create_http_exception(e)


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address",
    description="Verify user email address using verification token."
)
async def verify_email(
    verification_data: EmailVerificationConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Verify email address."""
    try:
        auth_service = AuthService(db)
        success = await auth_service.verify_email(verification_data.token)

        if success:
            return MessageResponse(message="Email verified successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
    summary="Resend verification email",
    description="Resend email verification to user."
)
async def resend_verification(
    email_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Resend verification email."""
    try:
        auth_service = AuthService(db)
        await auth_service.resend_verification_email(email_data.email)
        return MessageResponse(message="Verification email sent successfully")
    except UserManagementException as e:
        raise create_http_exception(e)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Request a password reset email."
)
async def forgot_password(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset."""
    try:
        auth_service = AuthService(db)
        await auth_service.request_password_reset(reset_data.email)
        return MessageResponse(message="Password reset email sent successfully")
    except UserManagementException as e:
        raise create_http_exception(e)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
    description="Reset password using reset token."
)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Reset password."""
    try:
        auth_service = AuthService(db)
        success = await auth_service.reset_password(
            reset_data.token,
            reset_data.new_password
        )

        if success:
            return MessageResponse(message="Password reset successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change user password (requires authentication)."
)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change password."""
    try:
        auth_service = AuthService(db)
        success = await auth_service.change_password(
            str(current_user.id),
            password_data.current_password,
            password_data.new_password
        )

        if success:
            return MessageResponse(message="Password changed successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information."
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        bio=current_user.bio,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login,
        full_name=current_user.full_name,
        display_name=current_user.display_name,
        roles=current_user.role_names,
        permissions=current_user.permission_codenames
    )