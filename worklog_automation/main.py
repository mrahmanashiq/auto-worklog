"""
FastAPI application factory and main entry point.

This module creates and configures the FastAPI application with all necessary
middleware, routers, and startup/shutdown handlers.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from worklog_automation.api.v1.router import api_router
from worklog_automation.core.config import get_settings
from worklog_automation.core.database import create_database_tables
from worklog_automation.core.exceptions import setup_exception_handlers
from worklog_automation.core.logging import setup_logging
from worklog_automation.core.middleware import setup_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    settings = get_settings()
    
    # Startup
    logger.info("🚀 Starting Worklog Automation System")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Version: {settings.APP_VERSION}")
    
    # Create database tables
    await create_database_tables()
    logger.info("✅ Database tables created/verified")
    
    # Setup monitoring if enabled (moved to application factory)
    # Note: Prometheus instrumentator is set up in create_application()
    
    logger.info("🎉 Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Worklog Automation System")


def create_application() -> FastAPI:
    """
    Application factory function.
    
    Creates and configures the FastAPI application with all necessary
    components including middleware, routers, and error handlers.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    settings = get_settings()
    
    # Setup logging first
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-friendly worklog management and automation system",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware for production
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
        )
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Setup monitoring if enabled (before routes)
    if settings.ENABLE_METRICS:
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app)
        logger.info("📊 Prometheus metrics enabled")
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> JSONResponse:
        """
        Health check endpoint for monitoring and load balancers.
        """
        return JSONResponse(
            content={
                "status": "healthy",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
            }
        )
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> JSONResponse:
        """
        Root endpoint with basic application information.
        """
        return JSONResponse(
            content={
                "message": f"Welcome to {settings.APP_NAME}",
                "version": settings.APP_VERSION,
                "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
                "health": "/health",
            }
        )
    
    logger.info("🏗️ FastAPI application created successfully")
    return app


# Create the application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "worklog_automation.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        access_log=settings.ACCESS_LOG,
        log_level=settings.LOG_LEVEL.lower(),
    )

