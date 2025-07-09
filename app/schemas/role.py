"""
Role and Permission Pydantic schemas for RBAC system.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import uuid


# Permission Schemas
class PermissionBase(BaseModel):
    """Base permission schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Permission name")
    codename: str = Field(..., min_length=1, max_length=100, description="Permission codename")
    description: Optional[str] = Field(None, max_length=500, description="Permission description")
    resource: str = Field(..., min_length=1, max_length=50, description="Resource name")
    action: str = Field(..., min_length=1, max_length=50, description="Action name")
    is_active: bool = Field(True, description="Permission active status")

    @validator('codename')
    def codename_format(cls, v):
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError('Codename must contain only alphanumeric characters, dots, and underscores')
        return v.lower()

    @validator('resource', 'action')
    def resource_action_format(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Resource and action must contain only alphanumeric characters and underscores')
        return v.lower()


class PermissionCreate(PermissionBase):
    """Permission creation schema."""

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Create User",
                "codename": "user.create",
                "description": "Permission to create new users",
                "resource": "user",
                "action": "create",
                "is_active": True
            }
        }


class PermissionUpdate(BaseModel):
    """Permission update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Permission name")
    description: Optional[str] = Field(None, max_length=500, description="Permission description")
    is_active: Optional[bool] = Field(None, description="Permission active status")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Permission Name",
                "description": "Updated permission description",
                "is_active": True
            }
        }


class PermissionResponse(PermissionBase):
    """Permission response schema."""
    id: uuid.UUID = Field(..., description="Permission ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Create User",
                "codename": "user.create",
                "description": "Permission to create new users",
                "resource": "user",
                "action": "create",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z"
            }
        }


# Role Schemas
class RoleBase(BaseModel):
    """Base role schema."""
    name: str = Field(..., min_length=1, max_length=50, description="Role name")
    description: Optional[str] = Field(None, max_length=500, description="Role description")
    is_default: bool = Field(False, description="Default role for new users")
    is_active: bool = Field(True, description="Role active status")
    priority: int = Field(0, ge=0, le=100, description="Role priority (0-100)")

    @validator('name')
    def name_format(cls, v):
        if not v.replace(' ', '').replace('_', '').replace('-', '').isalnum():
            raise ValueError('Role name must contain only alphanumeric characters, spaces, hyphens, and underscores')
        return v


class RoleCreate(RoleBase):
    """Role creation schema."""
    permission_ids: List[uuid.UUID] = Field(default=[], description="List of permission IDs")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Editor",
                "description": "Can edit content but not manage users",
                "is_default": False,
                "is_active": True,
                "priority": 20,
                "permission_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "456e7890-e89b-12d3-a456-426614174001"
                ]
            }
        }


class RoleUpdate(BaseModel):
    """Role update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Role name")
    description: Optional[str] = Field(None, max_length=500, description="Role description")
    is_default: Optional[bool] = Field(None, description="Default role for new users")
    is_active: Optional[bool] = Field(None, description="Role active status")
    priority: Optional[int] = Field(None, ge=0, le=100, description="Role priority (0-100)")
    permission_ids: Optional[List[uuid.UUID]] = Field(None, description="List of permission IDs")

    @validator('name')
    def name_format(cls, v):
        if v and not v.replace(' ', '').replace('_', '').replace('-', '').isalnum():
            raise ValueError('Role name must contain only alphanumeric characters, spaces, hyphens, and underscores')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Senior Editor",
                "description": "Updated role description",
                "priority": 25
            }
        }


class RoleResponse(RoleBase):
    """Role response schema."""
    id: uuid.UUID = Field(..., description="Role ID")
    is_system: bool = Field(..., description="System role (cannot be deleted)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    permissions: List[PermissionResponse] = Field(default=[], description="Role permissions")
    user_count: Optional[int] = Field(None, description="Number of users with this role")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Editor",
                "description": "Can edit content but not manage users",
                "is_default": False,
                "is_system": False,
                "is_active": True,
                "priority": 20,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
                "permissions": [],
                "user_count": 5
            }
        }


class RoleListResponse(BaseModel):
    """Role list response schema."""
    roles: List[RoleResponse] = Field(..., description="List of roles")
    total: int = Field(..., description="Total number of roles")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of roles per page")
    pages: int = Field(..., description="Total number of pages")


class PermissionListResponse(BaseModel):
    """Permission list response schema."""
    permissions: List[PermissionResponse] = Field(..., description="List of permissions")
    total: int = Field(..., description="Total number of permissions")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of permissions per page")
    pages: int = Field(..., description="Total number of pages")


# User Role Assignment Schemas
class UserRoleAssignment(BaseModel):
    """User role assignment schema."""
    user_id: uuid.UUID = Field(..., description="User ID")
    role_ids: List[uuid.UUID] = Field(..., description="List of role IDs to assign")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "role_ids": [
                    "456e7890-e89b-12d3-a456-426614174001",
                    "789e0123-e89b-12d3-a456-426614174002"
                ]
            }
        }


class UserPermissionCheck(BaseModel):
    """User permission check schema."""
    user_id: uuid.UUID = Field(..., description="User ID")
    permission_codename: str = Field(..., description="Permission codename to check")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "permission_codename": "user.create"
            }
        }


class UserPermissionResponse(BaseModel):
    """User permission check response schema."""
    has_permission: bool = Field(..., description="Whether user has the permission")
    user_id: uuid.UUID = Field(..., description="User ID")
    permission_codename: str = Field(..., description="Permission codename")
    granted_by_roles: List[str] = Field(default=[], description="Roles that grant this permission")

    class Config:
        json_schema_extra = {
            "example": {
                "has_permission": True,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "permission_codename": "user.create",
                "granted_by_roles": ["admin", "user_manager"]
            }
        }


# Bulk operations
class BulkRoleAssignment(BaseModel):
    """Bulk role assignment schema."""
    user_ids: List[uuid.UUID] = Field(..., min_items=1, description="List of user IDs")
    role_ids: List[uuid.UUID] = Field(..., min_items=1, description="List of role IDs to assign")
    operation: str = Field(..., pattern="^(add|remove|replace)$", description="Operation type: add, remove, or replace")

    class Config:
        json_schema_extra = {
            "example": {
                "user_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "456e7890-e89b-12d3-a456-426614174001"
                ],
                "role_ids": [
                    "789e0123-e89b-12d3-a456-426614174002"
                ],
                "operation": "add"
            }
        }