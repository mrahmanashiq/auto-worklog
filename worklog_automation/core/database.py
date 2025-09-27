"""
Database configuration and connection management.

This module handles database connections, session management,
and table creation using SQLModel with async support.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from worklog_automation.core.config import get_settings


# Global database engine and session maker
engine = None
async_session_maker = None


def get_database_url() -> str:
    """Get the database URL from settings."""
    settings = get_settings()
    return settings.DATABASE_URL


def init_database() -> None:
    """
    Initialize the database engine and session maker.
    
    This function sets up the global database connection objects
    that will be used throughout the application.
    """
    global engine, async_session_maker
    
    settings = get_settings()
    database_url = settings.DATABASE_URL
    
    # Create async engine with appropriate settings
    engine_kwargs = {
        "echo": settings.DEBUG,  # Log SQL queries in debug mode
        "future": True,  # Use SQLAlchemy 2.0 style
    }
    
    # SQLite specific configuration
    if "sqlite" in database_url:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    
    # PostgreSQL specific configuration
    elif "postgresql" in database_url:
        engine_kwargs.update({
            "pool_size": 20,
            "max_overflow": 0,
            "pool_recycle": 3600,
            "pool_pre_ping": True,
        })
    
    engine = create_async_engine(database_url, **engine_kwargs)
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    logger.info(f"🗄️  Database initialized: {database_url.split('://')[0]}")


async def create_database_tables() -> None:
    """
    Create all database tables.
    
    This function creates all tables defined in the SQLModel models.
    It's safe to call multiple times - existing tables won't be affected.
    """
    if engine is None:
        init_database()
    
    # Import all models to ensure they're registered with SQLModel
    from worklog_automation.models import Meeting, Project, TimeEntry, User  # noqa: F401
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("✅ Database tables created/verified")


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    
    This is an async context manager that provides a database session
    and ensures proper cleanup and transaction handling.
    
    Usage:
        async with get_async_session() as session:
            # Use session for database operations
            result = await session.execute(select(User))
    
    Yields:
        AsyncSession: Database session
    """
    if async_session_maker is None:
        init_database()
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function for FastAPI to get database session.
    
    This function is used as a FastAPI dependency to inject
    database sessions into route handlers.
    
    Usage:
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            # Use session for database operations
    
    Yields:
        AsyncSession: Database session
    """
    async with get_async_session() as session:
        yield session


class DatabaseManager:
    """
    Database manager for handling advanced database operations.
    
    This class provides methods for database health checks,
    connection pooling management, and maintenance operations.
    """
    
    @staticmethod
    async def health_check() -> dict[str, str]:
        """
        Perform a database health check.
        
        Returns:
            dict: Health check results
        """
        try:
            async with get_async_session() as session:
                # Simple query to test connection
                result = await session.execute("SELECT 1")
                await result.fetchone()
                
                return {
                    "status": "healthy",
                    "database": "connected",
                    "message": "Database connection is working"
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "message": f"Database connection failed: {str(e)}"
            }
    
    @staticmethod
    async def get_connection_info() -> dict[str, any]:
        """
        Get database connection information.
        
        Returns:
            dict: Connection information
        """
        if engine is None:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "url": get_database_url().split("://")[0] + "://***",
            "pool_size": getattr(engine.pool, "size", "N/A"),
            "checked_out": getattr(engine.pool, "checkedout", "N/A"),
            "overflow": getattr(engine.pool, "overflow", "N/A"),
        }
    
    @staticmethod
    async def close_connections() -> None:
        """Close all database connections."""
        if engine is not None:
            await engine.dispose()
            logger.info("🔌 Database connections closed")


# Initialize database on module import
try:
    init_database()
except Exception as e:
    logger.warning(f"Failed to initialize database on import: {e}")
    logger.info("Database will be initialized on first use")

