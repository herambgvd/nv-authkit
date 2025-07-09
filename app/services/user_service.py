"""
User service for business logic operations.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)
from app.core.security import security_manager
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserAdminUpdate


class UserService:
    """Service for user-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsException("User with this email already exists")

        if user_data.username:
            existing_username = await self.get_user_by_username(user_data.username)
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
            phone=user_data.phone,
            bio=user_data.bio,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            is_verified=user_data.is_verified,
            is_superuser=user_data.is_superuser,
            verification_token=verification_token
        )

        # Assign default role to new users (unless they're superusers)
        if not user_data.is_superuser:
            from app.services.role_service import RoleService
            role_service = RoleService(self.db)
            default_role = await role_service.get_default_role()
            if default_role:
                db_user.roles = [default_role]

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        return db_user

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None

        if not security_manager.verify_password(password, user.hashed_password):
            return None

        return user

    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> User:
        """Update user information."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        # Check if email is being changed and if new email already exists
        if user_data.email and user_data.email != user.email:
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise UserAlreadyExistsException("User with this email already exists")

        # Check if username is being changed and if new username already exists
        if user_data.username and user_data.username != user.username:
            existing_user = await self.get_user_by_username(user_data.username)
            if existing_user:
                raise UserAlreadyExistsException("User with this username already exists")

        # Update user fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def admin_update_user(self, user_id: uuid.UUID, user_data: UserAdminUpdate) -> User:
        """Update user information (admin only)."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        # Check if email is being changed and if new email already exists
        if user_data.email and user_data.email != user.email:
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise UserAlreadyExistsException("User with this email already exists")

        # Check if username is being changed and if new username already exists
        if user_data.username and user_data.username != user.username:
            existing_user = await self.get_user_by_username(user_data.username)
            if existing_user:
                raise UserAlreadyExistsException("User with this username already exists")

        # Update user fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        await self.db.delete(user)
        await self.db.commit()

        return True

    async def get_users(
            self,
            skip: int = 0,
            limit: int = 100,
            search: Optional[str] = None,
            is_active: Optional[bool] = None,
            is_verified: Optional[bool] = None,
            is_superuser: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get users with filters and pagination."""
        query = select(User)

        # Apply filters
        conditions = []

        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
            conditions.append(search_filter)

        if is_active is not None:
            conditions.append(User.is_active == is_active)

        if is_verified is not None:
            conditions.append(User.is_verified == is_verified)

        if is_superuser is not None:
            conditions.append(User.is_superuser == is_superuser)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count(User.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get users with pagination
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        users = result.scalars().all()

        return {
            "users": users,
            "total": total,
            "page": (skip // limit) + 1,
            "per_page": limit,
            "pages": (total + limit - 1) // limit
        }

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Update user's last login timestamp."""
        user = await self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            await self.db.commit()

    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
        """Change user password."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        if not security_manager.verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsException("Current password is incorrect")

        user.hashed_password = security_manager.hash_password(new_password)
        user.updated_at = datetime.utcnow()

        await self.db.commit()

        return True

    async def set_verification_token(self, user_id: uuid.UUID, token: str) -> None:
        """Set email verification token for user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        user.verification_token = token
        user.updated_at = datetime.utcnow()

        await self.db.commit()

    async def verify_email(self, token: str) -> bool:
        """Verify user email with token."""
        email = security_manager.verify_token(token, "email_verification")
        if not email:
            return False

        user = await self.get_user_by_email(email)
        if not user:
            return False

        user.is_verified = True
        user.verification_token = None
        user.updated_at = datetime.utcnow()

        await self.db.commit()

        return True

    async def set_password_reset_token(self, user_id: uuid.UUID, token: str) -> None:
        """Set password reset token for user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        user.password_reset_token = token
        user.updated_at = datetime.utcnow()

        await self.db.commit()

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password with token."""
        email = security_manager.verify_token(token, "password_reset")
        if not email:
            return False

        user = await self.get_user_by_email(email)
        if not user:
            return False

        user.hashed_password = security_manager.hash_password(new_password)
        user.password_reset_token = None
        user.updated_at = datetime.utcnow()

        await self.db.commit()

        return True

    async def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics."""
        total_users = await self.db.execute(select(func.count(User.id)))
        active_users = await self.db.execute(select(func.count(User.id)).where(User.is_active == True))
        verified_users = await self.db.execute(select(func.count(User.id)).where(User.is_verified == True))
        superusers = await self.db.execute(select(func.count(User.id)).where(User.is_superuser == True))

        return {
            "total_users": total_users.scalar(),
            "active_users": active_users.scalar(),
            "verified_users": verified_users.scalar(),
            "superusers": superusers.scalar()
        }
