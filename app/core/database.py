"""
Database configuration and session management.
"""
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


class DatabaseManager:
    """Database connection manager."""

    def __init__(self, database_url: str, echo: bool = False):
        self.engine = create_async_engine(
            database_url,
            echo=echo,
            future=True,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=20,
            max_overflow=30
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    async def create_tables(self) -> None:
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self) -> None:
        """Close database connection."""
        await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database manager instance
database_manager = DatabaseManager(
    database_url=settings.database.url,
    echo=settings.database.echo
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async for session in database_manager.get_session():
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    await database_manager.create_tables()


async def close_db() -> None:
    """Close database connections."""
    await database_manager.close()


# Health check function
async def check_db_health() -> bool:
    """Check database connectivity."""
    try:
        async with database_manager.session_factory() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False