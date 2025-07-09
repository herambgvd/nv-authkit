"""
User Pydantic schemas for the FastAPI User Management System.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
import uuid


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")

    @validator('username')
    def username_alphanumeric(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, hyphens, and underscores')
        return v


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8, description="User password")
    confirm_password: str = Field(..., min_length=8, description="Password confirmation")
    is_active: bool = Field(True, description="User active status")
    is_verified: bool = Field(False, description="User verification status")
    is_superuser: bool = Field(False, description="Superuser status")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "bio": "Software developer",
                "password": "securepassword123",
                "confirm_password": "securepassword123",
                "is_active": True,
                "is_verified": False,
                "is_superuser": False
            }
        }


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")

    @validator('username')
    def username_alphanumeric(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, hyphens, and underscores')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "bio": "Senior software developer",
                "avatar_url": "https://example.com/avatar.jpg"
            }
        }


class UserAdminUpdate(UserUpdate):
    """Admin user update schema."""
    is_active: Optional[bool] = Field(None, description="User active status")
    is_verified: Optional[bool] = Field(None, description="User verification status")
    is_superuser: Optional[bool] = Field(None, description="Superuser status")

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": True,
                "is_superuser": False
            }
        }


class UserInDB(UserBase):
    """User schema for database operations."""
    id: uuid.UUID = Field(..., description="User ID")
    is_active: bool = Field(..., description="User active status")
    is_verified: bool = Field(..., description="User verification status")
    is_superuser: bool = Field(..., description="Superuser status")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="User update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """User response schema."""
    full_name: str = Field(..., description="User full name")
    display_name: str = Field(..., description="User display name")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "bio": "Software developer",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_active": True,
                "is_verified": True,
                "is_superuser": False,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
                "last_login": "2023-01-02T10:30:00Z",
                "full_name": "John Doe",
                "display_name": "johndoe"
            }
        }


class UserListResponse(BaseModel):
    """User list response schema."""
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of users per page")
    pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "username": "johndoe",
                        "first_name": "John",
                        "last_name": "Doe",
                        "full_name": "John Doe",
                        "display_name": "johndoe",
                        "is_active": True,
                        "is_verified": True,
                        "is_superuser": False,
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 10,
                "pages": 1
            }
        }


class UserProfileResponse(BaseModel):
    """User profile response schema."""
    id: uuid.UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    username: Optional[str] = Field(None, description="Username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    bio: Optional[str] = Field(None, description="User bio")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    full_name: str = Field(..., description="Full name")
    display_name: str = Field(..., description="Display name")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "bio": "Software developer",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_verified": True,
                "created_at": "2023-01-01T00:00:00Z",
                "last_login": "2023-01-02T10:30:00Z",
                "full_name": "John Doe",
                "display_name": "johndoe"
            }
        }