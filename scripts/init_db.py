#!/usr/bin/env python3
"""
Script to initialize the database for the FastAPI User Management System.
"""
import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import database_manager, init_db
from app.core.config import settings


async def initialize_database():
    """Initialize the database."""
    print("Initializing FastAPI User Management System Database")
    print("=" * 55)
    print(f"Database URL: {settings.database.url}")
    print()

    try:
        # Create all tables
        await init_db()
        print("✅ Database tables created successfully!")

        # Test database connection
        async for db in database_manager.get_session():
            print("✅ Database connection test successful!")
            break

        print("\n🎉 Database initialization completed!")
        print("\nNext steps:")
        print("1. Run migrations: alembic upgrade head")
        print("2. Create a superuser: python scripts/create_superuser.py")
        print("3. Start the application: uvicorn app.main:app --reload")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        await database_manager.close()


async def main():
    """Main function."""
    try:
        await initialize_database()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())