#!/usr/bin/env python3
"""
Script to create a superuser for the FastAPI User Management System.
"""
import asyncio
import sys
import os
from getpass import getpass

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import database_manager, get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.core.config import settings


async def create_superuser():
    """Create a superuser interactively."""
    print("Creating superuser for FastAPI User Management System")
    print("=" * 50)

    # Get user input
    email = input("Email address: ").strip()
    if not email:
        print("Email is required!")
        return

    username = input("Username (optional): ").strip() or None
    first_name = input("First name (optional): ").strip() or None
    last_name = input("Last name (optional): ").strip() or None

    password = getpass("Password: ")
    if not password:
        print("Password is required!")
        return

    confirm_password = getpass("Password (again): ")
    if password != confirm_password:
        print("Error: Passwords don't match!")
        return

    # Create user data
    user_data = UserCreate(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        confirm_password=confirm_password,
        is_active=True,
        is_verified=True,  # Auto-verify superuser
        is_superuser=True
    )

    try:
        # Initialize database connection
        async for db in database_manager.get_session():
            user_service = UserService(db)

            # Check if user already exists
            existing_user = await user_service.get_user_by_email(email)
            if existing_user:
                print(f"Error: User with email '{email}' already exists!")
                return

            if username:
                existing_username = await user_service.get_user_by_username(username)
                if existing_username:
                    print(f"Error: User with username '{username}' already exists!")
                    return

            # Create superuser
            user = await user_service.create_user(user_data)
            print(f"\nSuperuser created successfully!")
            print(f"Email: {user.email}")
            print(f"Username: {user.username or 'N/A'}")
            print(f"ID: {user.id}")
            break

    except Exception as e:
        print(f"Error creating superuser: {e}")


async def main():
    """Main function."""
    try:
        await create_superuser()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await database_manager.close()


if __name__ == "__main__":
    asyncio.run(main())