"""
Command-line interface for worklog automation system.

This module provides CLI commands for managing the application,
database operations, and development tasks.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich import print
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="worklog",
    help="🚀 Worklog Automation System CLI",
    add_completion=False,
)

console = Console()


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to bind"),
    reload: bool = typer.Option(True, help="Enable auto-reload"),
    workers: int = typer.Option(1, help="Number of workers"),
) -> None:
    """Start the FastAPI development server."""
    import uvicorn
    
    from worklog_automation.core.config import get_settings
    
    settings = get_settings()
    
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    
    uvicorn.run(
        "worklog_automation.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        access_log=settings.ACCESS_LOG,
        log_level=settings.LOG_LEVEL.lower(),
    )


@app.command()
def db_create() -> None:
    """Create database tables."""
    async def _create_tables():
        from worklog_automation.core.database import create_database_tables
        await create_database_tables()
        print("✅ Database tables created successfully")
    
    asyncio.run(_create_tables())


@app.command()
def db_reset() -> None:
    """Reset database (WARNING: This will delete all data!)."""
    confirm = typer.confirm("⚠️  This will delete ALL data. Are you sure?")
    if not confirm:
        print("❌ Database reset cancelled")
        return
    
    async def _reset_db():
        from sqlmodel import SQLModel
        from worklog_automation.core.database import engine, init_database
        
        # Import all models to ensure they're registered
        from worklog_automation.models import Meeting, Project, TimeEntry, User  # noqa: F401
        
        if engine is None:
            init_database()
        
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
        
        print("✅ Database reset successfully")
    
    asyncio.run(_reset_db())


@app.command()
def db_status() -> None:
    """Check database connection status."""
    async def _check_status():
        from worklog_automation.core.database import DatabaseManager
        
        health = await DatabaseManager.health_check()
        connection_info = await DatabaseManager.get_connection_info()
        
        table = Table(title="📊 Database Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", health["status"])
        table.add_row("Message", health["message"])
        table.add_row("Connection", connection_info.get("status", "unknown"))
        table.add_row("URL", connection_info.get("url", "unknown"))
        
        console.print(table)
    
    asyncio.run(_check_status())


@app.command()
def create_user(
    email: str = typer.Option(..., help="User email"),
    username: str = typer.Option(..., help="Username"),
    password: str = typer.Option(..., help="Password"),
    full_name: Optional[str] = typer.Option(None, help="Full name"),
) -> None:
    """Create a new user."""
    async def _create_user():
        from worklog_automation.core.database import get_async_session
        from worklog_automation.core.security import hash_password
        from worklog_automation.models.user import User
        
        async with get_async_session() as session:
            # Check if user exists
            from sqlmodel import select
            result = await session.execute(
                select(User).where((User.email == email) | (User.username == username))
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ User with email '{email}' or username '{username}' already exists")
                return
            
            # Create user
            user = User(
                email=email,
                username=username,
                hashed_password=hash_password(password),
                full_name=full_name,
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"✅ User created successfully:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
    
    asyncio.run(_create_user())


@app.command()
def config() -> None:
    """Show current configuration."""
    from worklog_automation.core.config import get_settings
    
    settings = get_settings()
    
    table = Table(title="⚙️  Application Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    # Core settings
    table.add_row("App Name", settings.APP_NAME)
    table.add_row("Version", settings.APP_VERSION)
    table.add_row("Environment", settings.ENVIRONMENT)
    table.add_row("Debug", str(settings.DEBUG))
    table.add_row("Host", settings.HOST)
    table.add_row("Port", str(settings.PORT))
    
    # Database
    db_url = settings.DATABASE_URL
    if "://" in db_url:
        db_type = db_url.split("://")[0]
        table.add_row("Database", db_type)
    
    # Features
    table.add_row("Teams Enabled", str(settings.TEAMS_ENABLED))
    table.add_row("Jira Enabled", str(settings.JIRA_ENABLED))
    table.add_row("Git Enabled", str(settings.GIT_ENABLED))
    table.add_row("Rate Limiting", str(settings.RATE_LIMIT_ENABLED))
    table.add_row("Metrics", str(settings.ENABLE_METRICS))
    
    console.print(table)


@app.command()
def validate() -> None:
    """Validate application setup and configuration."""
    from worklog_automation.core.config import get_settings
    
    settings = get_settings()
    issues = []
    
    # Check critical settings
    if settings.SECRET_KEY == "your-super-secret-key-change-this-in-production":
        issues.append("⚠️  SECRET_KEY is using default value - change this!")
    
    if settings.is_production and settings.DEBUG:
        issues.append("⚠️  DEBUG is enabled in production environment")
    
    # Check integrations
    if settings.TEAMS_ENABLED and not settings.TEAMS_WEBHOOK_URL:
        issues.append("⚠️  Teams integration enabled but no webhook URL configured")
    
    if settings.JIRA_ENABLED and (not settings.JIRA_BASE_URL or not settings.JIRA_USERNAME):
        issues.append("⚠️  Jira integration enabled but configuration incomplete")
    
    # Check directories
    upload_dir = Path(settings.UPLOAD_DIR)
    if not upload_dir.exists():
        try:
            upload_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created upload directory: {upload_dir}")
        except Exception as e:
            issues.append(f"❌ Cannot create upload directory: {e}")
    
    # Report results
    if issues:
        print("🔍 Validation Issues Found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ All validations passed!")
    
    # Test database connection
    async def _test_db():
        try:
            from worklog_automation.core.database import DatabaseManager
            health = await DatabaseManager.health_check()
            if health["status"] == "healthy":
                print("✅ Database connection working")
            else:
                print(f"❌ Database connection failed: {health['message']}")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    asyncio.run(_test_db())


@app.command()
def dev_data() -> None:
    """Create development test data."""
    async def _create_dev_data():
        from worklog_automation.core.database import get_async_session
        from worklog_automation.core.security import hash_password
        from worklog_automation.models.user import User
        from worklog_automation.models.project import Project
        
        async with get_async_session() as session:
            # Create test user
            test_user = User(
                email="test@example.com",
                username="testuser",
                hashed_password=hash_password("password123"),
                full_name="Test User",
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            
            # Create test project
            test_project = Project(
                name="Test Project",
                description="A test project for development",
                code="TEST-001",
                owner_id=test_user.id,
                color="#3498db",
            )
            session.add(test_project)
            await session.commit()
            
            print("✅ Development data created:")
            print(f"   User: test@example.com / password123")
            print(f"   Project: {test_project.name}")
    
    asyncio.run(_create_dev_data())


if __name__ == "__main__":
    app()

