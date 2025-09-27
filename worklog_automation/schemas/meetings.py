"""
Pydantic schemas for meeting endpoints.

This module defines request and response models for meeting operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from worklog_automation.models.meeting import Meeting, MeetingStatus, MeetingType


class MeetingStartRequest(BaseModel):
    """Request model for starting a meeting timer."""
    
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Meeting title"
    )
    
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Meeting description"
    )
    
    meeting_type: MeetingType = Field(
        default=MeetingType.OTHER,
        description="Type of meeting"
    )
    
    project_id: Optional[UUID] = Field(
        default=None,
        description="Associated project ID"
    )
    
    location: Optional[str] = Field(
        default=None,
        description="Meeting location or platform"
    )
    
    attendee_count: Optional[int] = Field(
        default=1,
        ge=1,
        description="Number of attendees"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Daily Standup",
                "description": "Team daily standup meeting",
                "meeting_type": "standup",
                "location": "Microsoft Teams",
                "attendee_count": 5
            }
        }


class MeetingCreateRequest(BaseModel):
    """Request model for creating a scheduled meeting."""
    
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Meeting title"
    )
    
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Meeting description"
    )
    
    meeting_type: MeetingType = Field(
        default=MeetingType.OTHER,
        description="Type of meeting"
    )
    
    project_id: Optional[UUID] = Field(
        default=None,
        description="Associated project ID"
    )
    
    scheduled_start: Optional[datetime] = Field(
        default=None,
        description="Scheduled start time"
    )
    
    scheduled_end: Optional[datetime] = Field(
        default=None,
        description="Scheduled end time"
    )
    
    location: Optional[str] = Field(
        default=None,
        description="Meeting location or platform"
    )
    
    meeting_url: Optional[str] = Field(
        default=None,
        description="URL for online meeting"
    )
    
    attendees: Optional[list[str]] = Field(
        default=None,
        description="List of attendee email addresses"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sprint Planning",
                "description": "Planning for upcoming sprint",
                "meeting_type": "planning",
                "scheduled_start": "2024-01-15T14:00:00Z",
                "scheduled_end": "2024-01-15T16:00:00Z",
                "location": "Conference Room A",
                "attendees": ["john@company.com", "jane@company.com"]
            }
        }


class MeetingUpdateRequest(BaseModel):
    """Request model for updating a meeting."""
    
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Meeting title"
    )
    
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Meeting description"
    )
    
    notes: Optional[str] = Field(
        default=None,
        description="Meeting notes or summary"
    )
    
    was_productive: Optional[bool] = Field(
        default=None,
        description="Whether the meeting was productive"
    )
    
    could_have_been_email: Optional[bool] = Field(
        default=None,
        description="Whether this could have been an email"
    )
    
    action_items: Optional[list[str]] = Field(
        default=None,
        description="Action items from the meeting"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "notes": "Discussed upcoming features and timeline",
                "was_productive": True,
                "could_have_been_email": False,
                "action_items": [
                    "John to implement authentication",
                    "Jane to design user interface"
                ]
            }
        }


class MeetingResponse(BaseModel):
    """Response model for meeting operations."""
    
    id: UUID
    title: str
    description: Optional[str] = None
    meeting_type: MeetingType
    status: MeetingStatus
    
    # Timing
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    duration_minutes: int
    
    # Meeting details
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    attendee_count: int
    
    # Outcomes
    notes: Optional[str] = None
    action_items: Optional[list[str]] = None
    was_productive: Optional[bool] = None
    could_have_been_email: bool
    
    # Metadata
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def formatted_duration(self) -> str:
        """Get formatted duration string."""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"
    
    @property
    def is_ongoing(self) -> bool:
        """Check if meeting is currently ongoing."""
        return self.status == MeetingStatus.IN_PROGRESS
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Daily Standup",
                "description": "Team daily standup meeting",
                "meeting_type": "standup",
                "status": "completed",
                "scheduled_start": "2024-01-15T09:00:00Z",
                "scheduled_end": "2024-01-15T09:30:00Z",
                "actual_start": "2024-01-15T09:02:00Z",
                "actual_end": "2024-01-15T09:28:00Z",
                "duration_minutes": 26,
                "location": "Microsoft Teams",
                "attendee_count": 5,
                "was_productive": True,
                "could_have_been_email": False,
                "created_at": "2024-01-15T09:02:00Z"
            }
        }

