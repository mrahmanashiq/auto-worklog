"""
Time entry model for tracking work activities.

This module defines the TimeEntry model for recording work activities,
their duration, and associated metadata like commits and descriptions.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON
from sqlmodel import Field, Relationship

from worklog_automation.models.base import BaseModel


class TimeEntryType(str, Enum):
    """Types of time entries for categorization."""
    
    WORK = "work"
    MEETING = "meeting"
    BREAK = "break"
    TRAINING = "training"
    ADMIN = "admin"
    RESEARCH = "research"
    DEBUGGING = "debugging"
    REVIEW = "review"
    DOCUMENTATION = "documentation"


class TimeEntryStatus(str, Enum):
    """Time entry status for workflow management."""
    
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    SYNCED = "synced"  # Synced to external systems


class TimeEntry(BaseModel, table=True):
    """
    Time entry model for tracking work activities.
    
    Records work activities with duration, description, and optional
    links to commits, tickets, or other external references.
    """
    
    __tablename__ = "time_entries"
    
    # Basic information
    description: str = Field(
        min_length=1,
        max_length=1000,
        description="Description of the work performed"
    )
    
    start_time: datetime = Field(
        description="When the activity started"
    )
    
    end_time: Optional[datetime] = Field(
        default=None,
        description="When the activity ended (null for ongoing)"
    )
    
    duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Duration in minutes"
    )
    
    # Categorization
    entry_type: TimeEntryType = Field(
        default=TimeEntryType.WORK,
        description="Type of time entry"
    )
    
    status: TimeEntryStatus = Field(
        default=TimeEntryStatus.DRAFT,
        description="Current status of the time entry"
    )
    
    # Relationships
    user_id: UUID = Field(
        foreign_key="users.id",
        description="User who created this time entry"
    )
    
    project_id: Optional[UUID] = Field(
        default=None,
        foreign_key="projects.id",
        description="Associated project (optional)"
    )
    
    # External references
    commit_hash: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Git commit hash associated with this work"
    )
    
    commit_url: Optional[str] = Field(
        default=None,
        description="URL to the commit in version control"
    )
    
    jira_ticket: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Jira ticket ID (e.g., 'PROJ-123')"
    )
    
    jira_worklog_id: Optional[str] = Field(
        default=None,
        description="Jira worklog ID after sync"
    )
    
    pull_request_url: Optional[str] = Field(
        default=None,
        description="URL to related pull request"
    )
    
    # Additional details
    tags: Optional[list[str]] = Field(
        default=None,
        sa_type=JSON,
        description="Tags for categorization and filtering"
    )
    
    billable: bool = Field(
        default=True,
        description="Whether this time is billable"
    )
    
    hourly_rate: Optional[float] = Field(
        default=None,
        description="Hourly rate for this specific entry"
    )
    
    # Automation metadata
    auto_tracked: bool = Field(
        default=False,
        description="Whether this entry was automatically tracked"
    )
    
    tracking_source: Optional[str] = Field(
        default=None,
        description="Source of automatic tracking (IDE, calendar, etc.)"
    )
    
    # Sync status
    synced_to_jira: bool = Field(
        default=False,
        description="Whether synced to Jira"
    )
    
    synced_to_teams: bool = Field(
        default=False,
        description="Whether included in Teams report"
    )
    
    last_sync_at: Optional[datetime] = Field(
        default=None,
        description="When last synced to external systems"
    )
    
    sync_error: Optional[str] = Field(
        default=None,
        description="Error message from last sync attempt"
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="time_entries")
    project: Optional["Project"] = Relationship(back_populates="time_entries")
    
    class Config:
        """Model configuration."""
        
        json_schema_extra = {
            "example": {
                "description": "Implemented user authentication with JWT tokens",
                "start_time": "2024-01-15T10:00:00Z",
                "end_time": "2024-01-15T12:30:00Z",
                "duration_minutes": 150,
                "entry_type": "work",
                "status": "submitted",
                "commit_hash": "a1b2c3d4e5f6",
                "jira_ticket": "AUTH-123",
                "tags": ["backend", "security", "authentication"],
                "billable": True,
                "auto_tracked": False
            }
        }
    
    def start_tracking(self) -> None:
        """Start time tracking for this entry."""
        if not self.start_time:
            self.start_time = datetime.utcnow()
        self.end_time = None
        self.mark_updated()
    
    def stop_tracking(self) -> None:
        """Stop time tracking and calculate duration."""
        if not self.start_time:
            raise ValueError("Cannot stop tracking - no start time set")
        
        self.end_time = datetime.utcnow()
        self.calculate_duration()
        self.mark_updated()
    
    def calculate_duration(self) -> None:
        """Calculate duration in minutes from start and end times."""
        if not self.start_time or not self.end_time:
            return
        
        delta = self.end_time - self.start_time
        self.duration_minutes = int(delta.total_seconds() / 60)
    
    def set_manual_duration(self, minutes: int) -> None:
        """Set duration manually (for manual entries)."""
        if minutes < 0:
            raise ValueError("Duration cannot be negative")
        
        self.duration_minutes = minutes
        if self.start_time and not self.end_time:
            from datetime import timedelta
            self.end_time = self.start_time + timedelta(minutes=minutes)
        self.mark_updated()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to this time entry."""
        if self.tags is None:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            self.mark_updated()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this time entry."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.mark_updated()
    
    def mark_synced_to_jira(self, worklog_id: str) -> None:
        """Mark as synced to Jira with worklog ID."""
        self.synced_to_jira = True
        self.jira_worklog_id = worklog_id
        self.last_sync_at = datetime.utcnow()
        self.sync_error = None
        self.mark_updated()
    
    def mark_sync_error(self, error_message: str) -> None:
        """Mark sync error with error message."""
        self.sync_error = error_message
        self.last_sync_at = datetime.utcnow()
        self.mark_updated()
    
    @property
    def is_ongoing(self) -> bool:
        """Check if time tracking is currently ongoing."""
        return self.start_time is not None and self.end_time is None
    
    @property
    def duration_hours(self) -> float:
        """Get duration in hours."""
        return self.duration_minutes / 60.0
    
    @property
    def billable_amount(self) -> Optional[float]:
        """Calculate billable amount if hourly rate is set."""
        if not self.billable or not self.hourly_rate:
            return None
        
        return self.duration_hours * self.hourly_rate
    
    @property
    def formatted_duration(self) -> str:
        """Get formatted duration string (e.g., '2h 30m')."""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"

