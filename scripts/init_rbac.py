#!/usr/bin/env python3
"""
Script to initialize RBAC system with default roles and permissions.
"""
import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import database_manager
from app.services.role_service import RoleService
from app.schemas.role import PermissionCreate, RoleCreate
from app.core.config import settings

# Default permissions for the system
DEFAULT_PERMISSIONS = [
    # User permissions
    PermissionCreate(
        name="Create User",
        codename="user.create",
        description="Permission to create new users",
        resource="user",
        action="create"
    ),
    PermissionCreate(
        name="Read User",
        codename="user.read",
        description="Permission to read user information",
        resource="user",
        action="read"
    ),
    PermissionCreate(
        name="Update User",
        codename="user.update",
        description="Permission to update user information",
        resource="user",
        action="update"
    ),
    PermissionCreate(
        name="Delete User",
        codename="user.delete",
        description="Permission to delete users",
        resource="user",
        action="delete"
    ),
    PermissionCreate(
        name="List Users",
        codename="user.list",
        description="Permission to list all users",
        resource="user",
        action="list"
    ),

    # Role permissions
    PermissionCreate(
        name="Create Role",
        codename="role.create",
        description="Permission to create new roles",
        resource="role",
        action="create"
    ),
    PermissionCreate(
        name="Read Role",
        codename="role.read",
        description="Permission to read role information",
        resource="role",
        action="read"
    ),
    PermissionCreate(
        name="Update Role",
        codename="role.update",
        description="Permission to update role information",
        resource="role",
        action="update"
    ),
    PermissionCreate(
        name="Delete Role",
        codename="role.delete",
        description="Permission to delete roles",
        resource="role",
        action="delete"
    ),
    PermissionCreate(
        name="Assign Role",
        codename="role.assign",
        description="Permission to assign roles to users",
        resource="role",
        action="assign"
    ),

    # Permission permissions
    PermissionCreate(
        name="Create Permission",
        codename="permission.create",
        description="Permission to create new permissions",
        resource="permission",
        action="create"
    ),
    PermissionCreate(
        name="Read Permission",
        codename="permission.read",
        description="Permission to read permission information",
        resource="permission",
        action="read"
    ),
    PermissionCreate(
        name="Update Permission",
        codename="permission.update",
        description="Permission to update permission information",
        resource="permission",
        action="update"
    ),
    PermissionCreate(
        name="Delete Permission",
        codename="permission.delete",
        description="Permission to delete permissions",
        resource="permission",
        action="delete"
    ),

    # Profile permissions
    PermissionCreate(
        name="View Own Profile",
        codename="profile.view_own",
        description="Permission to view own profile",
        resource="profile",
        action="view_own"
    ),
    PermissionCreate(
        name="Update Own Profile",
        codename="profile.update_own",
        description="Permission to update own profile",
        resource="profile",
        action="update_own"
    ),
    PermissionCreate(
        name="View Any Profile",
        codename="profile.view_any",
        description="Permission to view any user's profile",
        resource="profile",
        action="view_any"
    ),

    # System permissions
    PermissionCreate(
        name="View System Stats",
        codename="system.stats",
        description="Permission to view system statistics",
        resource="system",
        action="stats"
    ),
    PermissionCreate(
        name="System Admin",
        codename="system.admin",
        description="Full system administration access",
        resource="system",
        action="admin"
    ),

    # Example microservice permissions
    PermissionCreate(
        name="Order Service Read",
        codename="order_service.read",
        description="Permission to read from order service",
        resource="order_service",
        action="read"
    ),
    PermissionCreate(
        name="Order Service Write",
        codename="order_service.write",
        description="Permission to write to order service",
        resource="order_service",
        action="write"
    ),
    PermissionCreate(
        name="Payment Service Read",
        codename="payment_service.read",
        description="Permission to read from payment service",
        resource="payment_service",
        action="read"
    ),
    PermissionCreate(
        name="Payment Service Write",
        codename="payment_service.write",
        description="Permission to write to payment service",
        resource="payment_service",
        action="write"
    ),
]


async def create_permissions(role_service: RoleService) -> dict:
    """Create default permissions and return their IDs."""
    permission_ids = {}

    print("Creating default permissions...")
    for perm_data in DEFAULT_PERMISSIONS:
        try:
            # Check if permission already exists
            existing = await role_service.get_permission_by_codename(perm_data.codename)
            if existing:
                print(f"  ✓ Permission '{perm_data.codename}' already exists")
                permission_ids[perm_data.codename] = existing.id
            else:
                permission = await role_service.create_permission(perm_data)
                print(f"  ✓ Created permission: {perm_data.codename}")
                permission_ids[perm_data.codename] = permission.id
        except Exception as e:
            print(f"  ❌ Failed to create permission '{perm_data.codename}': {e}")

    return permission_ids


async def create_default_roles(role_service: RoleService, permission_ids: dict):
    """Create default roles with permissions."""
    print("\nCreating default roles...")

    # Super Admin Role (has all permissions)
    try:
        existing_admin = await role_service.get_role_by_name("admin")
        if not existing_admin:
            admin_role = RoleCreate(
                name="admin",
                description="Super administrator with full system access",
                is_default=False,
                is_active=True,
                priority=100,
                permission_ids=list(permission_ids.values())
            )
            await role_service.create_role(admin_role)
            print("  ✓ Created admin role")
        else:
            print("  ✓ Admin role already exists")
    except Exception as e:
        print(f"  ❌ Failed to create admin role: {e}")

    # User Manager Role
    try:
        existing_user_manager = await role_service.get_role_by_name("user_manager")
        if not existing_user_manager:
            user_manager_permissions = [
                permission_ids.get("user.create"),
                permission_ids.get("user.read"),
                permission_ids.get("user.update"),
                permission_ids.get("user.list"),
                permission_ids.get("profile.view_any"),
                permission_ids.get("role.read"),
                permission_ids.get("role.assign"),
            ]
            user_manager_permissions = [p for p in user_manager_permissions if p]

            user_manager_role = RoleCreate(
                name="user_manager",
                description="Can manage users but not system settings",
                is_default=False,
                is_active=True,
                priority=80,
                permission_ids=user_manager_permissions
            )
            await role_service.create_role(user_manager_role)
            print("  ✓ Created user_manager role")
        else:
            print("  ✓ User manager role already exists")
    except Exception as e:
        print(f"  ❌ Failed to create user_manager role: {e}")

    # Moderator Role
    try:
        existing_moderator = await role_service.get_role_by_name("moderator")
        if not existing_moderator:
            moderator_permissions = [
                permission_ids.get("user.read"),
                permission_ids.get("user.update"),
                permission_ids.get("user.list"),
                permission_ids.get("profile.view_any"),
                permission_ids.get("role.read"),
            ]
            moderator_permissions = [p for p in moderator_permissions if p]

            moderator_role = RoleCreate(
                name="moderator",
                description="Content moderator with limited user management",
                is_default=False,
                is_active=True,
                priority=60,
                permission_ids=moderator_permissions
            )
            await role_service.create_role(moderator_role)
            print("  ✓ Created moderator role")
        else:
            print("  ✓ Moderator role already exists")
    except Exception as e:
        print(f"  ❌ Failed to create moderator role: {e}")

    # Regular User Role (default for new users)
    try:
        existing_user = await role_service.get_role_by_name("user")
        if not existing_user:
            user_permissions = [
                permission_ids.get("profile.view_own"),
                permission_ids.get("profile.update_own"),
            ]
            user_permissions = [p for p in user_permissions if p]

            user_role = RoleCreate(
                name="user",
                description="Regular user with basic permissions",
                is_default=True,
                is_active=True,
                priority=10,
                permission_ids=user_permissions
            )
            await role_service.create_role(user_role)
            print("  ✓ Created user role (default)")
        else:
            print("  ✓ User role already exists")
    except Exception as e:
        print(f"  ❌ Failed to create user role: {e}")

    # Guest Role (minimal permissions)
    try:
        existing_guest = await role_service.get_role_by_name("guest")
        if not existing_guest:
            guest_permissions = [
                permission_ids.get("profile.view_own"),
            ]
            guest_permissions = [p for p in guest_permissions if p]

            guest_role = RoleCreate(
                name="guest",
                description="Guest user with minimal permissions",
                is_default=False,
                is_active=True,
                priority=1,
                permission_ids=guest_permissions
            )
            await role_service.create_role(guest_role)
            print("  ✓ Created guest role")
        else:
            print("  ✓ Guest role already exists")
    except Exception as e:
        print(f"  ❌ Failed to create guest role: {e}")


async def initialize_rbac():
    """Initialize RBAC system with default roles and permissions."""
    print("Initializing RBAC System for FastAPI User Management")
    print("=" * 55)

    try:
        async for db in database_manager.get_session():
            role_service = RoleService(db)

            # Create permissions
            permission_ids = await create_permissions(role_service)

            # Create roles
            await create_default_roles(role_service, permission_ids)

            print("\n🎉 RBAC initialization completed successfully!")
            print("\nDefault roles created:")
            print("  • admin - Super administrator (priority: 100)")
            print("  • user_manager - User management (priority: 80)")
            print("  • moderator - Content moderation (priority: 60)")
            print("  • user - Regular user (priority: 10) [DEFAULT]")
            print("  • guest - Guest user (priority: 1)")

            print(f"\nTotal permissions created: {len(permission_ids)}")
            print("\nNext steps:")
            print("1. Create a superuser: python scripts/create_superuser.py")
            print("2. Assign admin role to superuser")
            print("3. Start the application: uvicorn app.main:app --reload")

            break

    except Exception as e:
        print(f"❌ Error initializing RBAC: {e}")
        raise
    finally:
        await database_manager.close()


async def main():
    """Main function."""
    try:
        await initialize_rbac()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"RBAC initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())