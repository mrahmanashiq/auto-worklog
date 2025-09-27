"""
Exception handling for the application.

This module defines custom exceptions and sets up global
exception handlers for the FastAPI application.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


class WorklogException(Exception):
    """Base exception for worklog automation system."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(WorklogException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class AuthorizationError(WorklogException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class NotFoundError(WorklogException):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ValidationError(WorklogException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class ConflictError(WorklogException):
    """Raised when there's a conflict with existing data."""
    
    def __init__(self, message: str = "Conflict with existing data", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


class ExternalServiceError(WorklogException):
    """Raised when external service integration fails."""
    
    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, details)


class RateLimitError(WorklogException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS, details)


class DatabaseError(WorklogException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


async def worklog_exception_handler(request: Request, exc: WorklogException) -> JSONResponse:
    """
    Handler for custom worklog exceptions.
    
    Args:
        request: FastAPI request object
        exc: WorklogException instance
    
    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"WorklogException: {exc.message}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "details": exc.details,
            "url": str(request.url),
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "request_id": request_id,
            "timestamp": str(datetime.utcnow()),
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for Pydantic validation errors.
    
    Args:
        request: FastAPI request object
        exc: RequestValidationError instance
    
    Returns:
        JSONResponse with validation error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Format validation errors
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input"),
        })
    
    logger.warning(
        f"Validation error: {len(formatted_errors)} errors",
        extra={
            "request_id": request_id,
            "errors": formatted_errors,
            "url": str(request.url),
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "details": {
                "validation_errors": formatted_errors,
                "error_count": len(formatted_errors),
            },
            "request_id": request_id,
            "timestamp": str(datetime.utcnow()),
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler for SQLAlchemy database errors.
    
    Args:
        request: FastAPI request object
        exc: SQLAlchemyError instance
    
    Returns:
        JSONResponse with database error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "exception_type": type(exc).__name__,
        }
    )
    
    # Don't expose internal database errors in production
    from worklog_automation.core.config import get_settings
    settings = get_settings()
    
    if settings.DEBUG:
        message = f"Database error: {str(exc)}"
        details = {"exception_type": type(exc).__name__}
    else:
        message = "Internal database error occurred"
        details = {}
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": message,
            "details": details,
            "request_id": request_id,
            "timestamp": str(datetime.utcnow()),
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for general unhandled exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception instance
    
    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
        exc_info=True,
    )
    
    # Don't expose internal errors in production
    from worklog_automation.core.config import get_settings
    settings = get_settings()
    
    if settings.DEBUG:
        message = f"Internal error: {str(exc)}"
        details = {"exception_type": type(exc).__name__}
    else:
        message = "An internal error occurred"
        details = {}
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": message,
            "details": details,
            "request_id": request_id,
            "timestamp": str(datetime.utcnow()),
        }
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Set up exception handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    from datetime import datetime
    
    # Custom exception handlers
    app.add_exception_handler(WorklogException, worklog_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("🛡️  Exception handlers configured successfully")

