"""
User model for the FastAPI User Management System.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base
from app.models.role import user_roles


class User(Base):
    """User model."""

    __tablename__ = "users"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    username: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Profile fields
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Status fields
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Verification tokens
    verification_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    verification_token_expires: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Password reset tokens
    password_reset_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    password_reset_token_expires: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # OAuth fields (for future social login)
    oauth_provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    oauth_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )

    # Indexes
    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_username", "username"),
        Index("idx_user_is_active", "is_active"),
        Index("idx_user_is_verified", "is_verified"),
        Index("idx_user_verification_token", "verification_token"),
        Index("idx_user_password_reset_token", "password_reset_token"),
        Index("idx_user_oauth_provider_id", "oauth_provider", "oauth_id"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email

    @property
    def display_name(self) -> str:
        """Get user's display name."""
        if self.username:
            return self.username
        return self.full_name

    @property
    def role_names(self) -> List[str]:
        """Get list of role names for this user."""
        return [role.name for role in self.roles if role.is_active]

    @property
    def permission_codenames(self) -> List[str]:
        """Get list of all permission codenames for this user."""
        permissions = set()
        for role in self.roles:
            if role.is_active:
                permissions.update(role.permission_codenames)
        return list(permissions)

    def has_permission(self, permission_codename: str) -> bool:
        """Check if user has a specific permission."""
        return permission_codename in self.permission_codenames

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return role_name in self.role_names

    def has_any_role(self, role_names: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        user_roles = set(self.role_names)
        required_roles = set(role_names)
        return bool(user_roles.intersection(required_roles))

    def get_highest_priority_role(self) -> Optional["Role"]:
        """Get the role with highest priority for this user."""
        if not self.roles:
            return None
        return max(self.roles, key=lambda role: role.priority if role.is_active else -1)