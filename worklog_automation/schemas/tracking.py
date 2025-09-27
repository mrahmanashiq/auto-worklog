"""
Pydantic schemas for tracking endpoints.

This module defines request and response models for time tracking operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from worklog_automation.models.time_entry import TimeEntry, TimeEntryType
from worklog_automation.models.user import WorkDayStatus


class TrackingStartRequest(BaseModel):
    """Request model for starting work day tracking."""
    
    initial_activity: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional initial activity description"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "initial_activity": "Starting work on user authentication module"
            }
        }


class ActivityUpdateRequest(BaseModel):
    """Request model for updating current activity."""
    
    activity: str = Field(
        min_length=1,
        max_length=500,
        description="Current activity description"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "activity": "Implementing JWT token validation"
            }
        }


class ManualEntryRequest(BaseModel):
    """Request model for adding manual time entries."""
    
    description: str = Field(
        min_length=1,
        max_length=1000,
        description="Description of the work performed"
    )
    
    duration_minutes: int = Field(
        gt=0,
        le=1440,  # Max 24 hours
        description="Duration in minutes"
    )
    
    start_time: Optional[datetime] = Field(
        default=None,
        description="Start time (defaults to current time)"
    )
    
    entry_type: Optional[TimeEntryType] = Field(
        default=TimeEntryType.WORK,
        description="Type of time entry"
    )
    
    project_id: Optional[UUID] = Field(
        default=None,
        description="Associated project ID"
    )
    
    commit_hash: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Git commit hash"
    )
    
    jira_ticket: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Jira ticket ID"
    )
    
    tags: Optional[list[str]] = Field(
        default=None,
        description="Tags for categorization"
    )
    
    billable: bool = Field(
        default=True,
        description="Whether time is billable"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Implemented user authentication with JWT tokens",
                "duration_minutes": 120,
                "start_time": "2024-01-15T10:00:00Z",
                "entry_type": "work",
                "commit_hash": "a1b2c3d4",
                "jira_ticket": "AUTH-123",
                "tags": ["backend", "security"],
                "billable": True
            }
        }


class TrackingStatusResponse(BaseModel):
    """Response model for tracking status operations."""
    
    status: str = Field(description="Operation status")
    message: str = Field(description="Status message")
    work_day_status: WorkDayStatus = Field(description="Current work day status")
    started_at: Optional[datetime] = Field(description="Work day start time")
    ended_at: Optional[datetime] = Field(default=None, description="Work day end time")
    current_activity: Optional[str] = Field(default=None, description="Current activity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "started",
                "message": "Work day started successfully",
                "work_day_status": "active",
                "started_at": "2024-01-15T08:00:00Z",
                "ended_at": None,
                "current_activity": "Starting work on authentication module"
            }
        }


class CurrentTrackingResponse(BaseModel):
    """Response model for current tracking status."""
    
    work_day_status: WorkDayStatus = Field(description="Current work day status")
    started_at: Optional[datetime] = Field(description="Work day start time")
    ended_at: Optional[datetime] = Field(default=None, description="Work day end time")
    current_activity: Optional[str] = Field(default=None, description="Current activity")
    ongoing_entries: list[TimeEntry] = Field(description="Currently ongoing time entries")
    total_minutes_today: int = Field(description="Total minutes logged today")
    entries_count_today: int = Field(description="Number of entries today")
    
    class Config:
        json_schema_extra = {
            "example": {
                "work_day_status": "active",
                "started_at": "2024-01-15T08:00:00Z",
                "ended_at": None,
                "current_activity": "Code review",
                "ongoing_entries": [],
                "total_minutes_today": 240,
                "entries_count_today": 3
            }
        }

