"""
Role and Permission management API endpoints.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.services.role_service import RoleService
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse,
    PermissionCreate, PermissionUpdate, PermissionResponse, PermissionListResponse,
    UserRoleAssignment, UserPermissionCheck, UserPermissionResponse,
    BulkRoleAssignment
)
from app.schemas.auth import MessageResponse
from app.dependencies.auth import get_current_superuser
from app.core.exceptions import (
    UserManagementException,
    create_http_exception
)
from app.models.user import User

router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])


# Permission endpoints
@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create permission (Admin)",
    description="Create a new permission. Requires superuser privileges."
)
async def create_permission(
        permission_data: PermissionCreate,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Create a new permission."""
    try:
        role_service = RoleService(db)
        permission = await role_service.create_permission(permission_data)

        return PermissionResponse(
            id=permission.id,
            name=permission.name,
            codename=permission.codename,
            description=permission.description,
            resource=permission.resource,
            action=permission.action,
            is_active=permission.is_active,
            created_at=permission.created_at,
            updated_at=permission.updated_at
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.get(
    "/permissions",
    response_model=PermissionListResponse,
    summary="List permissions (Admin)",
    description="Get a list of permissions with filtering and pagination. Requires superuser privileges."
)
async def list_permissions(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        search: Optional[str] = Query(None, description="Search in name, codename, or description"),
        resource: Optional[str] = Query(None, description="Filter by resource"),
        action: Optional[str] = Query(None, description="Filter by action"),
        is_active: Optional[bool] = Query(None, description="Filter by active status"),
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """List permissions with filtering and pagination."""
    try:
        role_service = RoleService(db)
        result = await role_service.get_permissions(
            skip=skip,
            limit=limit,
            search=search,
            resource=resource,
            action=action,
            is_active=is_active
        )

        permissions_response = [
            PermissionResponse(
                id=perm.id,
                name=perm.name,
                codename=perm.codename,
                description=perm.description,
                resource=perm.resource,
                action=perm.action,
                is_active=perm.is_active,
                created_at=perm.created_at,
                updated_at=perm.updated_at
            )
            for perm in result["permissions"]
        ]

        return PermissionListResponse(
            permissions=permissions_response,
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"],
            pages=result["pages"]
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.get(
    "/permissions/{permission_id}",
    response_model=PermissionResponse,
    summary="Get permission by ID (Admin)",
    description="Get a specific permission by ID. Requires superuser privileges."
)
async def get_permission(
        permission_id: uuid.UUID,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Get permission by ID."""
    try:
        role_service = RoleService(db)
        permission = await role_service.get_permission_by_id(permission_id)

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        return PermissionResponse(
            id=permission.id,
            name=permission.name,
            codename=permission.codename,
            description=permission.description,
            resource=permission.resource,
            action=permission.action,
            is_active=permission.is_active,
            created_at=permission.created_at,
            updated_at=permission.updated_at
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.put(
    "/permissions/{permission_id}",
    response_model=PermissionResponse,
    summary="Update permission (Admin)",
    description="Update a specific permission. Requires superuser privileges."
)
async def update_permission(
        permission_id: uuid.UUID,
        permission_data: PermissionUpdate,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Update permission."""
    try:
        role_service = RoleService(db)
        permission = await role_service.update_permission(permission_id, permission_data)

        return PermissionResponse(
            id=permission.id,
            name=permission.name,
            codename=permission.codename,
            description=permission.description,
            resource=permission.resource,
            action=permission.action,
            is_active=permission.is_active,
            created_at=permission.created_at,
            updated_at=permission.updated_at
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.delete(
    "/permissions/{permission_id}",
    response_model=MessageResponse,
    summary="Delete permission (Admin)",
    description="Delete a specific permission. Requires superuser privileges."
)
async def delete_permission(
        permission_id: uuid.UUID,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Delete permission."""
    try:
        role_service = RoleService(db)
        await role_service.delete_permission(permission_id)
        return MessageResponse(message="Permission deleted successfully")
    except UserManagementException as e:
        raise create_http_exception(e)


# Role endpoints
@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create role (Admin)",
    description="Create a new role with permissions. Requires superuser privileges."
)
async def create_role(
        role_data: RoleCreate,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Create a new role."""
    try:
        role_service = RoleService(db)
        role = await role_service.create_role(role_data)

        permissions_response = [
            PermissionResponse(
                id=perm.id,
                name=perm.name,
                codename=perm.codename,
                description=perm.description,
                resource=perm.resource,
                action=perm.action,
                is_active=perm.is_active,
                created_at=perm.created_at,
                updated_at=perm.updated_at
            )
            for perm in role.permissions
        ]

        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_default=role.is_default,
            is_system=role.is_system,
            is_active=role.is_active,
            priority=role.priority,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=permissions_response,
            user_count=0
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.get(
    "/",
    response_model=RoleListResponse,
    summary="List roles (Admin)",
    description="Get a list of roles with filtering and pagination. Requires superuser privileges."
)
async def list_roles(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        search: Optional[str] = Query(None, description="Search in name or description"),
        is_active: Optional[bool] = Query(None, description="Filter by active status"),
        is_default: Optional[bool] = Query(None, description="Filter by default status"),
        is_system: Optional[bool] = Query(None, description="Filter by system status"),
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """List roles with filtering and pagination."""
    try:
        role_service = RoleService(db)
        result = await role_service.get_roles(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            is_default=is_default,
            is_system=is_system
        )

        roles_response = []
        for role in result["roles"]:
            permissions_response = [
                PermissionResponse(
                    id=perm.id,
                    name=perm.name,
                    codename=perm.codename,
                    description=perm.description,
                    resource=perm.resource,
                    action=perm.action,
                    is_active=perm.is_active,
                    created_at=perm.created_at,
                    updated_at=perm.updated_at
                )
                for perm in role.permissions
            ]

            role_response = RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                is_default=role.is_default,
                is_system=role.is_system,
                is_active=role.is_active,
                priority=role.priority,
                created_at=role.created_at,
                updated_at=role.updated_at,
                permissions=permissions_response,
                user_count=result["role_user_counts"].get(role.id, 0)
            )
            roles_response.append(role_response)

        return RoleListResponse(
            roles=roles_response,
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"],
            pages=result["pages"]
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get role by ID (Admin)",
    description="Get a specific role by ID. Requires superuser privileges."
)
async def get_role(
        role_id: uuid.UUID,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Get role by ID."""
    try:
        role_service = RoleService(db)
        role = await role_service.get_role_by_id(role_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        permissions_response = [
            PermissionResponse(
                id=perm.id,
                name=perm.name,
                codename=perm.codename,
                description=perm.description,
                resource=perm.resource,
                action=perm.action,
                is_active=perm.is_active,
                created_at=perm.created_at,
                updated_at=perm.updated_at
            )
            for perm in role.permissions
        ]

        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_default=role.is_default,
            is_system=role.is_system,
            is_active=role.is_active,
            priority=role.priority,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=permissions_response
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update role (Admin)",
    description="Update a specific role. Requires superuser privileges."
)
async def update_role(
        role_id: uuid.UUID,
        role_data: RoleUpdate,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Update role."""
    try:
        role_service = RoleService(db)
        role = await role_service.update_role(role_id, role_data)

        permissions_response = [
            PermissionResponse(
                id=perm.id,
                name=perm.name,
                codename=perm.codename,
                description=perm.description,
                resource=perm.resource,
                action=perm.action,
                is_active=perm.is_active,
                created_at=perm.created_at,
                updated_at=perm.updated_at
            )
            for perm in role.permissions
        ]

        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_default=role.is_default,
            is_system=role.is_system,
            is_active=role.is_active,
            priority=role.priority,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=permissions_response
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.delete(
    "/{role_id}",
    response_model=MessageResponse,
    summary="Delete role (Admin)",
    description="Delete a specific role. Requires superuser privileges."
)
async def delete_role(
        role_id: uuid.UUID,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Delete role."""
    try:
        role_service = RoleService(db)
        await role_service.delete_role(role_id)
        return MessageResponse(message="Role deleted successfully")
    except UserManagementException as e:
        raise create_http_exception(e)


# User-Role assignment endpoints
@router.post(
    "/assign",
    response_model=MessageResponse,
    summary="Assign roles to user (Admin)",
    description="Assign roles to a user (replaces existing roles). Requires superuser privileges."
)
async def assign_user_roles(
        assignment_data: UserRoleAssignment,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Assign roles to user."""
    try:
        role_service = RoleService(db)
        await role_service.assign_roles_to_user(assignment_data.user_id, assignment_data.role_ids)
        return MessageResponse(message="Roles assigned successfully")
    except UserManagementException as e:
        raise create_http_exception(e)


@router.post(
    "/bulk-assign",
    summary="Bulk assign roles (Admin)",
    description="Bulk assign/remove roles to/from multiple users. Requires superuser privileges."
)
async def bulk_assign_roles(
        assignment_data: BulkRoleAssignment,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Bulk assign roles to multiple users."""
    try:
        role_service = RoleService(db)
        result = await role_service.bulk_assign_roles(
            assignment_data.user_ids,
            assignment_data.role_ids,
            assignment_data.operation
        )
        return result
    except UserManagementException as e:
        raise create_http_exception(e)


@router.post(
    "/check-permission",
    response_model=UserPermissionResponse,
    summary="Check user permission (Admin)",
    description="Check if a user has a specific permission. Requires superuser privileges."
)
async def check_user_permission(
        permission_check: UserPermissionCheck,
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Check if user has a specific permission."""
    try:
        role_service = RoleService(db)
        result = await role_service.check_user_permission(
            permission_check.user_id,
            permission_check.permission_codename
        )

        return UserPermissionResponse(
            has_permission=result["has_permission"],
            user_id=result["user_id"],
            permission_codename=result["permission_codename"],
            granted_by_roles=result["granted_by_roles"]
        )
    except UserManagementException as e:
        raise create_http_exception(e)


@router.get(
    "/stats/overview",
    summary="Get role statistics (Admin)",
    description="Get role and permission statistics overview. Requires superuser privileges."
)
async def get_role_stats(
        current_user: User = Depends(get_current_superuser),
        db: AsyncSession = Depends(get_db)
):
    """Get role and permission statistics."""
    try:
        role_service = RoleService(db)
        stats = await role_service.get_role_stats()
        return stats
    except UserManagementException as e:
        raise create_http_exception(e)