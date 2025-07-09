"""
Authentication service for handling user authentication and authorization.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.user_service import UserService
from app.services.email_service import email_service
from app.core.security import security_manager
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    EmailNotVerifiedException,
    InvalidTokenException
)

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

    async def register_user(self, user_data: RegisterRequest) -> User:
        """Register a new user."""
        # Check if user already exists
        existing_user = await self.user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsException("User with this email already exists")

        if user_data.username:
            existing_username = await self.user_service.get_user_by_username(user_data.username)
            if existing_username:
                raise UserAlreadyExistsException("User with this username already exists")

        # Create user
        hashed_password = security_manager.hash_password(user_data.password)
        verification_token = security_manager.generate_email_verification_token(user_data.email)

        db_user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
            is_superuser=False,
            verification_token=verification_token
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        # Send verification email
        email_sent = False
        try:
            await email_service.send_verification_email(
                email=db_user.email,
                name=db_user.display_name,
                token=verification_token
            )
            email_sent = True
            logger.info(f"Verification email sent successfully to {db_user.email}")
        except Exception as e:
            # Log detailed error but don't fail registration
            logger.error(f"Failed to send verification email to {db_user.email}: {e}")
            logger.error(f"Email service error details: {type(e).__name__}: {str(e)}")
            # Email failure should not prevent user registration

        # Add email status to user object for debugging
        if hasattr(db_user, '__dict__'):
            db_user.__dict__['_email_sent'] = email_sent

        return db_user

    async def login_user(self, login_data: LoginRequest) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self.user_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )

        if not user:
            raise InvalidCredentialsException("Invalid email or password")

        if not user.is_active:
            raise AuthenticationException("Account is deactivated")

        # Update last login
        await self.user_service.update_last_login(user.id)

        # Generate tokens
        access_token = security_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        refresh_token = security_manager.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.security.access_token_expire_minutes * 60
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        payload = security_manager.decode_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise InvalidTokenException("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenException("Invalid refresh token")

        # Get user to ensure they still exist and are active
        user = await self.user_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive")

        # Generate new tokens
        access_token = security_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        new_refresh_token = security_manager.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.security.access_token_expire_minutes * 60
        )

    async def verify_email(self, token: str) -> bool:
        """Verify user email address."""
        email = security_manager.verify_token(token, "email_verification")
        if not email:
            raise InvalidTokenException("Invalid or expired verification token")

        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise InvalidTokenException("User not found")

        if user.is_verified:
            return True  # Already verified

        # Mark as verified
        user.is_verified = True
        user.verification_token = None
        user.updated_at = datetime.utcnow()

        await self.db.commit()

        # Send welcome email
        try:
            await email_service.send_welcome_email(
                email=user.email,
                name=user.display_name
            )
        except Exception:
            # Log error but don't fail verification
            pass

        return True

    async def resend_verification_email(self, email: str) -> bool:
        """Resend verification email."""
        user = await self.user_service.get_user_by_email(email)
        if not user:
            # Don't reveal if user exists
            return True

        if user.is_verified:
            return True  # Already verified

        # Generate new verification token
        verification_token = security_manager.generate_email_verification_token(email)
        user.verification_token = verification_token
        user.updated_at = datetime.utcnow()

        await self.db.commit()

        # Send verification email
        await email_service.send_verification_email(
            email=user.email,
            name=user.display_name,
            token=verification_token
        )

        return True

    async def request_password_reset(self, email: str) -> bool:
        """Request password reset."""
        user = await self.user_service.get_user_by_email(email)
        if not user:
            # Don't reveal if user exists
            return True

        # Generate password reset token
        reset_token = security_manager.generate_password_reset_token(email)
        user.password_reset_token = reset_token
        user.password_reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        user.updated_at = datetime.utcnow()

        await self.db.commit()

        # Send password reset email
        await email_service.send_password_reset_email(
            email=user.email,
            name=user.display_name,
            token=reset_token
        )

        return True

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token."""
        email = security_manager.verify_token(token, "password_reset")
        if not email:
            raise InvalidTokenException("Invalid or expired reset token")

        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise InvalidTokenException("User not found")

        # Check if token is still valid
        if (user.password_reset_token != token or
            not user.password_reset_token_expires or
            user.password_reset_token_expires < datetime.utcnow()):
            raise InvalidTokenException("Invalid or expired reset token")

        # Update password
        user.hashed_password = security_manager.hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_token_expires = None
        user.updated_at = datetime.utcnow()

        await self.db.commit()

        # Send password changed confirmation email
        try:
            await email_service.send_password_changed_email(
                email=user.email,
                name=user.display_name
            )
        except Exception:
            # Log error but don't fail password reset
            pass

        return True

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password."""
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")

        if not security_manager.verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsException("Current password is incorrect")

        # Update password
        user.hashed_password = security_manager.hash_password(new_password)
        user.updated_at = datetime.utcnow()

        await self.db.commit()

        # Send password changed confirmation email
        try:
            await email_service.send_password_changed_email(
                email=user.email,
                name=user.display_name
            )
        except Exception:
            # Log error but don't fail password change
            pass

        return True

    async def validate_token(self, token: str) -> Optional[User]:
        """Validate access token and return user."""
        payload = security_manager.decode_token(token)

        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await self.user_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None

        return user