"""
RBAC (Role-Based Access Control) dependencies for FastAPI endpoints.
"""
from typing import List, Callable
from functools import wraps
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.services.role_service import RoleService
from app.models.user import User
from app.models.role import Role


def require_permissions(required_permissions: List[str]):
    """
    Decorator to require specific permissions for endpoint access.

    Args:
        required_permissions: List of permission codenames required

    Returns:
        Dependency function that checks user permissions
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Check if current user has required permissions."""
        if current_user.is_superuser:
            return current_user

        role_service = RoleService(db)
        user_permissions = await role_service.get_user_permissions(current_user.id)

        missing_permissions = []
        for permission in required_permissions:
            if permission not in user_permissions:
                missing_permissions.append(permission)

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing_permissions)}"
            )

        return current_user

    return permission_checker


def require_any_permission(required_permissions: List[str]):
    """
    Decorator to require at least one of the specified permissions.

    Args:
        required_permissions: List of permission codenames (user needs at least one)

    Returns:
        Dependency function that checks user permissions
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Check if current user has at least one required permission."""
        if current_user.is_superuser:
            return current_user

        role_service = RoleService(db)
        user_permissions = await role_service.get_user_permissions(current_user.id)

        has_permission = False
        for permission in required_permissions:
            if permission in user_permissions:
                has_permission = True
                break

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions. Need at least one of: {', '.join(required_permissions)}"
            )

        return current_user

    return permission_checker


def require_roles(required_roles: List[str]):
    """
    Decorator to require specific roles for endpoint access.

    Args:
        required_roles: List of role names required

    Returns:
        Dependency function that checks user roles
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Check if current user has required roles."""
        if current_user.is_superuser:
            return current_user

        user_roles = current_user.role_names
        missing_roles = []

        for role in required_roles:
            if role not in user_roles:
                missing_roles.append(role)

        if missing_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required roles: {', '.join(missing_roles)}"
            )

        return current_user

    return role_checker


def require_any_role(required_roles: List[str]):
    """
    Decorator to require at least one of the specified roles.

    Args:
        required_roles: List of role names (user needs at least one)

    Returns:
        Dependency function that checks user roles
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Check if current user has at least one required role."""
        if current_user.is_superuser:
            return current_user

        user_roles = current_user.role_names
        has_role = any(role in user_roles for role in required_roles)

        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required roles. Need at least one of: {', '.join(required_roles)}"
            )

        return current_user

    return role_checker


def check_resource_permission(resource: str, action: str):
    """
    Check permission for a specific resource and action.

    Args:
        resource: Resource name (e.g., 'user', 'post', 'order')
        action: Action name (e.g., 'create', 'read', 'update', 'delete')

    Returns:
        Dependency function that checks the specific permission
    """
    permission_codename = f"{resource}.{action}"
    return require_permissions([permission_codename])


# Predefined permission dependencies for common operations
def require_user_create():
    """Require user creation permission."""
    return require_permissions(["user.create"])


def require_user_read():
    """Require user read permission."""
    return require_permissions(["user.read"])


def require_user_update():
    """Require user update permission."""
    return require_permissions(["user.update"])


def require_user_delete():
    """Require user delete permission."""
    return require_permissions(["user.delete"])


def require_role_manage():
    """Require role management permissions."""
    return require_permissions(["role.create", "role.update", "role.delete"])


def require_permission_manage():
    """Require permission management permissions."""
    return require_permissions(["permission.create", "permission.update", "permission.delete"])


# Convenience functions for common role checks
def require_admin():
    """Require admin role."""
    return require_roles(["admin"])


def require_moderator():
    """Require moderator role."""
    return require_roles(["moderator"])


def require_admin_or_moderator():
    """Require admin or moderator role."""
    return require_any_role(["admin", "moderator"])


# Custom permission checker that can be used in endpoints
async def get_user_with_permission(
    permission_codename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user and check if they have a specific permission.

    Args:
        permission_codename: Permission codename to check
        current_user: Current authenticated user
        db: Database session

    Returns:
        User object if permission check passes

    Raises:
        HTTPException: If user doesn't have the required permission
    """
    if current_user.is_superuser:
        return current_user

    role_service = RoleService(db)
    result = await role_service.check_user_permission(current_user.id, permission_codename)

    if not result["has_permission"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing required permission: {permission_codename}"
        )

    return current_user


# Resource-based permission decorators for microservices
def require_microservice_permission(service_name: str, action: str):
    """
    Check permission for microservice operations.

    Args:
        service_name: Name of the microservice
        action: Action being performed

    Example:
        @app.get("/orders", dependencies=[Depends(require_microservice_permission("order_service", "read"))])
    """
    permission_codename = f"{service_name}.{action}"
    return require_permissions([permission_codename])


# Role hierarchy checker
async def check_role_hierarchy(
    target_user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Check if current user can perform actions on target user based on role hierarchy.
    Users can only manage users with lower priority roles.

    Args:
        target_user_id: ID of the user being managed
        current_user: Current authenticated user
        db: Database session

    Returns:
        User object if hierarchy check passes

    Raises:
        HTTPException: If user doesn't have sufficient role priority
    """
    if current_user.is_superuser:
        return current_user

    from app.services.user_service import UserService
    user_service = UserService(db)
    target_user = await user_service.get_user_by_id(target_user_id)

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )

    # Get highest priority roles
    current_user_role = current_user.get_highest_priority_role()
    target_user_role = target_user.get_highest_priority_role()

    current_priority = current_user_role.priority if current_user_role else 0
    target_priority = target_user_role.priority if target_user_role else 0

    if current_priority <= target_priority:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role priority to manage this user"
        )

    return current_user