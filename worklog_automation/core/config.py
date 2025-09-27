"""
Application configuration management.

This module handles all application configuration using Pydantic settings
with environment variable support and validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden using environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = Field(default="Worklog Automation", description="Application name")
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development", description="Environment name"
    )
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # Security
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-this-in-production",
        description="Secret key for JWT encoding",
        min_length=32,
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration in days"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./worklog.db",
        description="Database connection URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Work Schedule
    WORK_START_TIME: str = Field(
        default="08:00", description="Default work start time (HH:MM)"
    )
    WORK_END_TIME: str = Field(
        default="18:00", description="Default work end time (HH:MM)"
    )
    DEFAULT_TIMEZONE: str = Field(
        default="UTC", description="Default timezone"
    )
    
    # External Integrations
    TEAMS_WEBHOOK_URL: str = Field(default="", description="Microsoft Teams webhook URL")
    TEAMS_ENABLED: bool = Field(default=False, description="Enable Teams integration")
    
    JIRA_BASE_URL: str = Field(default="", description="Jira base URL")
    JIRA_USERNAME: str = Field(default="", description="Jira username")
    JIRA_API_TOKEN: str = Field(default="", description="Jira API token")
    JIRA_ENABLED: bool = Field(default=False, description="Enable Jira integration")
    
    GIT_ENABLED: bool = Field(default=True, description="Enable Git integration")
    DEFAULT_GIT_REMOTE: str = Field(default="origin", description="Default Git remote")
    
    # Email Configuration
    SMTP_HOST: str = Field(default="", description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    SMTP_USE_TLS: bool = Field(default=True, description="Use TLS for SMTP")
    EMAIL_FROM: str = Field(default="", description="From email address")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="./uploads", description="Upload directory")
    MAX_UPLOAD_SIZE: int = Field(default=10485760, description="Max upload size in bytes")  # 10MB
    ALLOWED_EXTENSIONS: str = Field(
        default=".txt,.pdf,.doc,.docx,.png,.jpg,.jpeg",
        description="Allowed file extensions"
    )
    
    # Monitoring & Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    SENTRY_DSN: str = Field(default="", description="Sentry DSN for error tracking")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # Background Tasks
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL"
    )
    
    # Development
    RELOAD: bool = Field(default=True, description="Enable auto-reload")
    ACCESS_LOG: bool = Field(default=True, description="Enable access logging")
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key length."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @computed_field
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return self.DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "")
    
    @computed_field
    @property
    def allowed_extensions_list(self) -> list[str]:
        """Get list of allowed file extensions."""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    This function uses LRU cache to ensure settings are loaded only once
    and reused throughout the application lifecycle.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()

