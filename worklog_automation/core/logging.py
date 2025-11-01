"""
Logging configuration for the application.

This module sets up structured logging using Loguru with
appropriate formatters, handlers, and log levels.
"""

import sys
from pathlib import Path

from loguru import logger

from worklog_automation.core.config import get_settings


def setup_logging() -> None:
    """
    Set up application logging configuration.
    
    Configures Loguru with appropriate handlers, formatters,
    and log levels based on environment settings.
    """
    settings = get_settings()
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colored output for development
    if settings.DEBUG:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            level=settings.LOG_LEVEL,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        # Production console handler - structured JSON
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            level=settings.LOG_LEVEL,
            serialize=True,  # JSON output
        )
    
    # File handler for persistent logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Main application log
    logger.add(
        log_dir / "worklog_automation.log",
        rotation="10 MB",
        retention="30 days",
        compression="gz",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG,
    )
    
    # Error log - only warnings and above
    logger.add(
        log_dir / "errors.log",
        rotation="10 MB",
        retention="90 days",
        compression="gz",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="WARNING",
        backtrace=True,
        diagnose=True,
    )
    
    # Access log for HTTP requests (if needed)
    if settings.ACCESS_LOG:
        logger.add(
            log_dir / "access.log",
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            level="INFO",
            filter=lambda record: "access" in record["extra"],
        )
    
    # Integration logs
    logger.add(
        log_dir / "integrations.log",
        rotation="10 MB",
        retention="30 days",
        compression="gz",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="INFO",
        filter=lambda record: "integration" in record["extra"],
    )
    
    # Set external library log levels
    import logging
    
    # Reduce noise from external libraries
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(
        logging.INFO if settings.ACCESS_LOG else logging.WARNING
    )
    
    # Integrate Loguru with Sentry (forward to Python logging for Sentry to capture)
    if settings.SENTRY_ENABLE_LOGS and settings.SENTRY_DSN:
        # Add a Loguru sink that forwards logs to Python logging for Sentry
        def send_to_sentry(record):
            """Forward logs to Sentry via Python logging module."""
            try:
                py_logger = logging.getLogger(record["name"])
                level_name = record["level"].name
                log_level = getattr(logging, level_name, logging.INFO)
                py_logger.log(log_level, record["message"])
            except Exception:
                # Don't break logging if Sentry integration fails
                pass
            return True
        
        # Forward WARNING, ERROR, and CRITICAL logs to Sentry
        logger.add(
            send_to_sentry,
            level="WARNING",
            filter=lambda r: settings.SENTRY_ENABLE_LOGS and settings.SENTRY_DSN
        )
    
    logger.info(f"📝 Logging configured - Level: {settings.LOG_LEVEL}")


def get_integration_logger(service_name: str):
    """
    Get a logger for integration services.
    
    Args:
        service_name: Name of the integration service (e.g., 'teams', 'jira')
    
    Returns:
        Logger instance with integration context
    """
    return logger.bind(integration=service_name)


def get_request_logger(request_id: str):
    """
    Get a logger with request context.
    
    Args:
        request_id: Unique request identifier
    
    Returns:
        Logger instance with request context
    """
    return logger.bind(request_id=request_id)


def log_function_call(func_name: str, **kwargs):
    """
    Log function call with parameters.
    
    Args:
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    params = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f"Calling {func_name}({params})")


class LoggingMiddleware:
    """
    Middleware for logging HTTP requests and responses.
    
    This middleware logs incoming requests, their processing time,
    and response status codes for monitoring and debugging.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        import time
        import uuid
        
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Log request
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()
        client = scope.get("client", ["unknown", 0])[0]
        
        request_logger = get_request_logger(request_id)
        request_logger.bind(access=True).info(
            f"Request started: {method} {path}{'?' + query_string if query_string else ''} "
            f"from {client}"
        )
        
        # Process request
        status_code = 500
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            request_logger.error(f"Request failed: {str(e)}")
            raise
        finally:
            # Log response
            process_time = time.time() - start_time
            request_logger.bind(access=True).info(
                f"Request completed: {method} {path} -> {status_code} "
                f"({process_time:.3f}s)"
            )


# Utility functions for structured logging
def log_user_action(user_id: str, action: str, **context):
    """Log user action with context."""
    logger.bind(user_id=user_id, action=action).info(f"User action: {action}", **context)


def log_integration_event(service: str, event: str, success: bool, **context):
    """Log integration event."""
    logger.bind(integration=service, event=event, success=success).info(
        f"Integration {service}: {event} - {'Success' if success else 'Failed'}",
        **context
    )


def log_performance_metric(metric_name: str, value: float, unit: str = "ms", **context):
    """Log performance metric."""
    logger.bind(metric=metric_name, value=value, unit=unit).info(
        f"Performance: {metric_name} = {value}{unit}",
        **context
    )

