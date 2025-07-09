"""
Role and Permission models for RBAC system.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Text, Table, Column, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


# Association table for role-permission many-to-many relationship
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_role_permissions_role_id', 'role_id'),
    Index('idx_role_permissions_permission_id', 'permission_id'),
)

# Association table for user-role many-to-many relationship
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_user_roles_user_id', 'user_id'),
    Index('idx_user_roles_role_id', 'role_id'),
)


class Permission(Base):
    """Permission model for granular access control."""

    __tablename__ = "permissions"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Permission details
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    codename: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Resource and action
    resource: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        onupdate=func.now()
    )

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )

    # Indexes
    __table_args__ = (
        Index("idx_permission_resource_action", "resource", "action"),
        Index("idx_permission_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Permission(codename={self.codename}, resource={self.resource}, action={self.action})>"


class Role(Base):
    """Role model for grouping permissions."""

    __tablename__ = "roles"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Role details
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Role properties
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Priority for role hierarchy (higher number = higher priority)
    priority: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        onupdate=func.now()
    )

    # Relationships
    permissions: Mapped[List[Permission]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles"
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )

    # Indexes
    __table_args__ = (
        Index("idx_role_name", "name"),
        Index("idx_role_is_default", "is_default"),
        Index("idx_role_is_system", "is_system"),
        Index("idx_role_is_active", "is_active"),
        Index("idx_role_priority", "priority"),
    )

    def __repr__(self) -> str:
        return f"<Role(name={self.name}, priority={self.priority})>"

    @property
    def permission_codenames(self) -> List[str]:
        """Get list of permission codenames for this role."""
        return [perm.codename for perm in self.permissions if perm.is_active]

    def has_permission(self, permission_codename: str) -> bool:
        """Check if role has a specific permission."""
        return permission_codename in self.permission_codenames