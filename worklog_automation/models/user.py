"""
User model for authentication and profile management.

This module defines the User model with authentication capabilities,
work preferences, and integration settings.
"""

from datetime import datetime, time
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship

from worklog_automation.models.base import BaseModel


class UserRole(str, Enum):
    """User roles for role-based access control."""
    
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


class WorkDayStatus(str, Enum):
    """Current work day status for tracking."""
    
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class User(BaseModel, table=True):
    """
    User model for authentication and profile management.
    
    Stores user credentials, preferences, and current work session state.
    """
    
    __tablename__ = "users"
    
    # Authentication fields
    email: str = Field(
        unique=True,
        index=True,
        description="User's email address (used for login)"
    )
    
    username: str = Field(
        unique=True,
        index=True,
        description="Unique username"
    )
    
    hashed_password: str = Field(
        description="Bcrypt hashed password"
    )
    
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active"
    )
    
    role: UserRole = Field(
        default=UserRole.USER,
        description="User role for permissions"
    )
    
    # Profile information
    full_name: Optional[str] = Field(
        default=None,
        description="User's full name"
    )
    
    avatar_url: Optional[str] = Field(
        default=None,
        description="URL to user's avatar image"
    )
    
    timezone: str = Field(
        default="UTC",
        description="User's timezone"
    )
    
    # Work preferences
    work_start_time: time = Field(
        default=time(8, 0),
        description="Preferred work start time"
    )
    
    work_end_time: time = Field(
        default=time(18, 0),
        description="Preferred work end time"
    )
    
    auto_start_tracking: bool = Field(
        default=True,
        description="Auto-start time tracking at work_start_time"
    )
    
    auto_stop_tracking: bool = Field(
        default=True,
        description="Auto-stop time tracking at work_end_time"
    )
    
    # Current work session state
    current_day_status: WorkDayStatus = Field(
        default=WorkDayStatus.NOT_STARTED,
        description="Current work day status"
    )
    
    daily_work_started_at: Optional[datetime] = Field(
        default=None,
        description="When today's work session started"
    )
    
    daily_work_ended_at: Optional[datetime] = Field(
        default=None,
        description="When today's work session ended"
    )
    
    current_activity: Optional[str] = Field(
        default=None,
        description="Current activity description"
    )
    
    # Integration settings
    teams_webhook_url: Optional[str] = Field(
        default=None,
        description="Personal Teams webhook URL"
    )
    
    jira_username: Optional[str] = Field(
        default=None,
        description="Jira username for worklog integration"
    )
    
    jira_api_token: Optional[str] = Field(
        default=None,
        description="Encrypted Jira API token"
    )
    
    git_username: Optional[str] = Field(
        default=None,
        description="Git username for commit tracking"
    )
    
    git_email: Optional[str] = Field(
        default=None,
        description="Git email for commit tracking"
    )
    
    # Notification preferences
    enable_email_notifications: bool = Field(
        default=True,
        description="Enable email notifications"
    )
    
    enable_teams_notifications: bool = Field(
        default=False,
        description="Enable Teams notifications"
    )
    
    daily_report_time: time = Field(
        default=time(18, 0),
        description="Time to send daily report"
    )
    
    weekly_report_day: int = Field(
        default=5,  # Friday
        description="Day of week for weekly report (0=Monday)"
    )
    
    # Relationships
    projects: list["Project"] = Relationship(back_populates="owner")
    time_entries: list["TimeEntry"] = Relationship(back_populates="user")
    meetings: list["Meeting"] = Relationship(back_populates="user")
    
    class Config:
        """Model configuration."""
        
        json_schema_extra = {
            "example": {
                "email": "john.doe@company.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "timezone": "America/New_York",
                "work_start_time": "09:00:00",
                "work_end_time": "17:30:00",
                "role": "user",
                "is_active": True,
                "auto_start_tracking": True,
                "current_day_status": "not_started"
            }
        }
    
    def start_work_day(self) -> None:
        """Start the work day tracking."""
        from datetime import datetime
        
        self.current_day_status = WorkDayStatus.ACTIVE
        self.daily_work_started_at = datetime.utcnow()
        self.daily_work_ended_at = None
        self.mark_updated()
    
    def end_work_day(self) -> None:
        """End the work day tracking."""
        from datetime import datetime
        
        self.current_day_status = WorkDayStatus.COMPLETED
        self.daily_work_ended_at = datetime.utcnow()
        self.current_activity = None
        self.mark_updated()
    
    def pause_work_day(self) -> None:
        """Pause the work day tracking."""
        if self.current_day_status == WorkDayStatus.ACTIVE:
            self.current_day_status = WorkDayStatus.PAUSED
            self.mark_updated()
    
    def resume_work_day(self) -> None:
        """Resume the work day tracking."""
        if self.current_day_status == WorkDayStatus.PAUSED:
            self.current_day_status = WorkDayStatus.ACTIVE
            self.mark_updated()
    
    def set_current_activity(self, activity: str) -> None:
        """Set the current activity description."""
        self.current_activity = activity
        self.mark_updated()
    
    @property
    def is_work_day_active(self) -> bool:
        """Check if work day is currently active."""
        return self.current_day_status in [WorkDayStatus.ACTIVE, WorkDayStatus.PAUSED]
    
    @property
    def has_teams_integration(self) -> bool:
        """Check if Teams integration is configured."""
        return bool(self.teams_webhook_url and self.enable_teams_notifications)
    
    @property
    def has_jira_integration(self) -> bool:
        """Check if Jira integration is configured."""
        return bool(self.jira_username and self.jira_api_token)
