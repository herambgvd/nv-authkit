"""
Role and Permission service for RBAC operations.
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    UserNotFoundException,
    ValidationException
)
from app.models.role import Role, Permission, user_roles
from app.models.user import User
from app.schemas.role import (
    RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate
)


class RoleService:
    """Service for role and permission management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Permission methods
    async def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        # Check if permission already exists
        existing = await self.get_permission_by_codename(permission_data.codename)
        if existing:
            raise ValidationException(f"Permission with codename '{permission_data.codename}' already exists")

        db_permission = Permission(
            name=permission_data.name,
            codename=permission_data.codename,
            description=permission_data.description,
            resource=permission_data.resource,
            action=permission_data.action,
            is_active=permission_data.is_active
        )

        self.db.add(db_permission)
        await self.db.commit()
        await self.db.refresh(db_permission)

        return db_permission

    async def get_permission_by_id(self, permission_id: uuid.UUID) -> Optional[Permission]:
        """Get permission by ID."""
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def get_permission_by_codename(self, codename: str) -> Optional[Permission]:
        """Get permission by codename."""
        result = await self.db.execute(
            select(Permission).where(Permission.codename == codename)
        )
        return result.scalar_one_or_none()

    async def get_permissions(self, skip: int = 0, limit: int = 100, search: Optional[str] = None,
                              resource: Optional[str] = None, action: Optional[str] = None,
                              is_active: Optional[bool] = None) -> Dict[str, Any]:
        """Get permissions with filters and pagination."""
        query = select(Permission)

        # Apply filters
        conditions = []

        if search:
            search_filter = or_(
                Permission.name.ilike(f"%{search}%"),
                Permission.codename.ilike(f"%{search}%"),
                Permission.description.ilike(f"%{search}%")
            )
            conditions.append(search_filter)

        if resource:
            conditions.append(Permission.resource == resource)

        if action:
            conditions.append(Permission.action == action)

        if is_active is not None:
            conditions.append(Permission.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count(Permission.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get permissions with pagination
        query = query.offset(skip).limit(limit).order_by(Permission.resource, Permission.action)
        result = await self.db.execute(query)
        permissions = result.scalars().all()

        return {
            "permissions": permissions,
            "total": total,
            "page": (skip // limit) + 1,
            "per_page": limit,
            "pages": (total + limit - 1) // limit
        }

    async def update_permission(self, permission_id: uuid.UUID, permission_data: PermissionUpdate) -> Permission:
        """Update permission."""
        permission = await self.get_permission_by_id(permission_id)
        if not permission:
            raise ValidationException("Permission not found")

        # Update fields
        update_data = permission_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)

        permission.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(permission)

        return permission

    async def delete_permission(self, permission_id: uuid.UUID) -> bool:
        """Delete permission."""
        permission = await self.get_permission_by_id(permission_id)
        if not permission:
            raise ValidationException("Permission not found")

        await self.db.delete(permission)
        await self.db.commit()

        return True

    # Role methods
    async def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role."""
        # Check if role already exists
        existing = await self.get_role_by_name(role_data.name)
        if existing:
            raise ValidationException(f"Role with name '{role_data.name}' already exists")

        db_role = Role(
            name=role_data.name,
            description=role_data.description,
            is_default=role_data.is_default,
            is_active=role_data.is_active,
            priority=role_data.priority
        )

        # Add permissions if provided
        if role_data.permission_ids:
            permissions = await self.db.execute(
                select(Permission).where(Permission.id.in_(role_data.permission_ids))
            )
            db_role.permissions = list(permissions.scalars().all())

        self.db.add(db_role)
        await self.db.commit()
        await self.db.refresh(db_role, ["permissions"])

        return db_role

    async def get_role_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        """Get role by ID with permissions."""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        result = await self.db.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()

    async def get_roles(self, skip: int = 0, limit: int = 100,
                        search: Optional[str] = None, is_active: Optional[bool] = None,
                        is_default: Optional[bool] = None,
                        is_system: Optional[bool] = None) -> Dict[str, Any]:
        """Get roles with filters and pagination."""
        query = select(Role).options(selectinload(Role.permissions))

        # Apply filters
        conditions = []

        if search:
            search_filter = or_(
                Role.name.ilike(f"%{search}%"),
                Role.description.ilike(f"%{search}%")
            )
            conditions.append(search_filter)

        if is_active is not None:
            conditions.append(Role.is_active == is_active)

        if is_default is not None:
            conditions.append(Role.is_default == is_default)

        if is_system is not None:
            conditions.append(Role.is_system == is_system)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count(Role.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get roles with pagination
        query = query.offset(skip).limit(limit).order_by(Role.priority.desc(), Role.name)
        result = await self.db.execute(query)
        roles = result.scalars().all()

        # Get user counts for each role
        role_user_counts = {}
        if roles:
            role_ids = [role.id for role in roles]
            user_count_query = select(
                user_roles.c.role_id,
                func.count(user_roles.c.user_id).label('user_count')
            ).where(
                user_roles.c.role_id.in_(role_ids)
            ).group_by(user_roles.c.role_id)

            user_count_result = await self.db.execute(user_count_query)
            role_user_counts = dict(user_count_result.fetchall())

        return {
            "roles": roles,
            "role_user_counts": role_user_counts,
            "total": total,
            "page": (skip // limit) + 1,
            "per_page": limit,
            "pages": (total + limit - 1) // limit
        }

    async def update_role(self, role_id: uuid.UUID, role_data: RoleUpdate) -> Role:
        """Update role."""
        role = await self.get_role_by_id(role_id)
        if not role:
            raise ValidationException("Role not found")

        if role.is_system:
            raise ValidationException("Cannot modify system roles")

        # Check name uniqueness if name is being changed
        if role_data.name and role_data.name != role.name:
            existing = await self.get_role_by_name(role_data.name)
            if existing:
                raise ValidationException(f"Role with name '{role_data.name}' already exists")

        # Update fields
        update_data = role_data.dict(exclude_unset=True, exclude={"permission_ids"})
        for field, value in update_data.items():
            setattr(role, field, value)

        # Update permissions if provided
        if role_data.permission_ids is not None:
            permissions = await self.db.execute(
                select(Permission).where(Permission.id.in_(role_data.permission_ids))
            )
            role.permissions = list(permissions.scalars().all())

        role.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(role, ["permissions"])

        return role

    async def delete_role(self, role_id: uuid.UUID) -> bool:
        """Delete role."""
        role = await self.get_role_by_id(role_id)
        if not role:
            raise ValidationException("Role not found")

        if role.is_system:
            raise ValidationException("Cannot delete system roles")

        await self.db.delete(role)
        await self.db.commit()

        return True

    # User-Role assignment methods
    async def assign_roles_to_user(self, user_id: uuid.UUID, role_ids: List[uuid.UUID]) -> User:
        """Assign roles to user."""
        user = await self.db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        user = user.scalar_one_or_none()

        if not user:
            raise UserNotFoundException()

        # Get roles
        roles = await self.db.execute(
            select(Role).where(Role.id.in_(role_ids))
        )
        roles_list = list(roles.scalars().all())

        # Assign roles
        user.roles = roles_list

        await self.db.commit()
        await self.db.refresh(user, ["roles"])

        return user

    async def add_roles_to_user(self, user_id: uuid.UUID, role_ids: List[uuid.UUID]) -> User:
        """Add roles to user (keeping existing ones)."""
        user = await self.db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        user = user.scalar_one_or_none()

        if not user:
            raise UserNotFoundException()

        # Get new roles
        new_roles = await self.db.execute(
            select(Role).where(Role.id.in_(role_ids))
        )
        new_roles_list = list(new_roles.scalars().all())

        # Add to existing roles
        existing_role_ids = {role.id for role in user.roles}
        for role in new_roles_list:
            if role.id not in existing_role_ids:
                user.roles.append(role)

        await self.db.commit()
        await self.db.refresh(user, ["roles"])

        return user

    async def remove_roles_from_user(self, user_id: uuid.UUID, role_ids: List[uuid.UUID]) -> User:
        """Remove roles from user."""
        user = await self.db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        user = user.scalar_one_or_none()

        if not user:
            raise UserNotFoundException()

        # Remove specified roles
        role_ids_set = set(role_ids)
        user.roles = [role for role in user.roles if role.id not in role_ids_set]

        await self.db.commit()
        await self.db.refresh(user, ["roles"])

        return user

    async def get_user_permissions(self, user_id: uuid.UUID) -> List[str]:
        """Get all permission codenames for a user."""
        user = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        user = user.scalar_one_or_none()

        if not user:
            raise UserNotFoundException()

        return user.permission_codenames

    async def check_user_permission(self, user_id: uuid.UUID, permission_codename: str) -> Dict[str, Any]:
        """Check if user has a specific permission."""
        user = await self.db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        user = user.scalar_one_or_none()

        if not user:
            raise UserNotFoundException()

        has_permission = user.has_permission(permission_codename)
        granted_by_roles = []

        if has_permission:
            for role in user.roles:
                if role.is_active and role.has_permission(permission_codename):
                    granted_by_roles.append(role.name)

        return {
            "has_permission": has_permission,
            "user_id": user_id,
            "permission_codename": permission_codename,
            "granted_by_roles": granted_by_roles
        }

    async def bulk_assign_roles(self, user_ids: List[uuid.UUID], role_ids: List[uuid.UUID],
                                operation: str) -> Dict[str, Any]:
        """Bulk assign/remove roles to/from multiple users."""
        results = {"success": [], "failed": []}

        for user_id in user_ids:
            try:
                if operation == "add":
                    user = await self.add_roles_to_user(user_id, role_ids)
                elif operation == "remove":
                    user = await self.remove_roles_from_user(user_id, role_ids)
                elif operation == "replace":
                    user = await self.assign_roles_to_user(user_id, role_ids)
                else:
                    raise ValidationException("Invalid operation. Must be 'add', 'remove', or 'replace'")

                results["success"].append(str(user_id))
            except Exception as e:
                results["failed"].append({"user_id": str(user_id), "error": str(e)})

        return results

    async def get_default_role(self) -> Optional[Role]:
        """Get the default role for new users."""
        result = await self.db.execute(
            select(Role).where(and_(Role.is_default == True, Role.is_active == True))
        )
        return result.scalar_one_or_none()

    async def get_role_stats(self) -> Dict[str, Any]:
        """Get role and permission statistics."""
        total_roles = await self.db.execute(select(func.count(Role.id)))
        active_roles = await self.db.execute(select(func.count(Role.id)).where(Role.is_active == True))
        system_roles = await self.db.execute(select(func.count(Role.id)).where(Role.is_system == True))

        total_permissions = await self.db.execute(select(func.count(Permission.id)))
        active_permissions = await self.db.execute(
            select(func.count(Permission.id)).where(Permission.is_active == True))

        return {
            "total_roles": total_roles.scalar(),
            "active_roles": active_roles.scalar(),
            "system_roles": system_roles.scalar(),
            "total_permissions": total_permissions.scalar(),
            "active_permissions": active_permissions.scalar()
        }
