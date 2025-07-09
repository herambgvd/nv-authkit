#!/usr/bin/env python3
"""
Script to fix datetime column issues in the database.
"""
import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import database_manager
from sqlalchemy import text


async def fix_datetime_columns():
    """Fix datetime column default values."""
    print("Fixing datetime column issues...")

    try:
        async with database_manager.engine.begin() as conn:
            # Fix users table datetime columns
            await conn.execute(text("""
                                    ALTER TABLE users
                                        ALTER COLUMN created_at SET DEFAULT now() ,
                                    ALTER
                                    COLUMN updated_at DROP
                                    DEFAULT;
                                    """))

            # Fix roles table datetime columns if it exists
            try:
                await conn.execute(text("""
                                        ALTER TABLE roles
                                            ALTER COLUMN created_at SET DEFAULT now() ,
                                        ALTER
                                        COLUMN updated_at DROP
                                        DEFAULT;
                                        """))
            except Exception:
                print("Roles table not found, skipping...")

            # Fix permissions table datetime columns if it exists
            try:
                await conn.execute(text("""
                                        ALTER TABLE permissions
                                            ALTER COLUMN created_at SET DEFAULT now() ,
                                        ALTER
                                        COLUMN updated_at DROP
                                        DEFAULT;
                                        """))
            except Exception:
                print("Permissions table not found, skipping...")

        print("✅ Datetime columns fixed successfully!")

    except Exception as e:
        print(f"❌ Error fixing datetime columns: {e}")
        raise
    finally:
        await database_manager.close()


async def main():
    """Main function."""
    try:
        await fix_datetime_columns()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Fix failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())