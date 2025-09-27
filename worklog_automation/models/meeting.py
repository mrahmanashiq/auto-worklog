"""
Meeting model for tracking meeting time and details.

This module defines the Meeting model for recording meetings,
their duration, attendees, and related information.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON
from sqlmodel import Field, Relationship

from worklog_automation.models.base import BaseModel


class MeetingType(str, Enum):
    """Types of meetings for categorization."""
    
    STANDUP = "standup"
    PLANNING = "planning"
    REVIEW = "review"
    RETROSPECTIVE = "retrospective"
    ONE_ON_ONE = "one_on_one"
    CLIENT_CALL = "client_call"
    TRAINING = "training"
    INTERVIEW = "interview"
    BRAINSTORMING = "brainstorming"
    DEMO = "demo"
    OTHER = "other"


class MeetingStatus(str, Enum):
    """Meeting status for tracking."""
    
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Meeting(BaseModel, table=True):
    """
    Meeting model for tracking meeting time and details.
    
    Records meetings with duration, attendees, and optional
    links to calendar events or external meeting platforms.
    """
    
    __tablename__ = "meetings"
    
    # Basic information
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Meeting title"
    )
    
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Meeting description or agenda"
    )
    
    meeting_type: MeetingType = Field(
        default=MeetingType.OTHER,
        description="Type of meeting"
    )
    
    status: MeetingStatus = Field(
        default=MeetingStatus.SCHEDULED,
        description="Current meeting status"
    )
    
    # Timing
    scheduled_start: Optional[datetime] = Field(
        default=None,
        description="Scheduled start time"
    )
    
    scheduled_end: Optional[datetime] = Field(
        default=None,
        description="Scheduled end time"
    )
    
    actual_start: Optional[datetime] = Field(
        default=None,
        description="Actual start time"
    )
    
    actual_end: Optional[datetime] = Field(
        default=None,
        description="Actual end time"
    )
    
    duration_minutes: int = Field(
        default=0,
        ge=0,
        description="Actual duration in minutes"
    )
    
    # Relationships
    user_id: UUID = Field(
        foreign_key="users.id",
        description="User who created/attended this meeting"
    )
    
    project_id: Optional[UUID] = Field(
        default=None,
        foreign_key="projects.id",
        description="Associated project (optional)"
    )
    
    # Meeting details
    location: Optional[str] = Field(
        default=None,
        description="Meeting location or platform (Zoom, Teams, etc.)"
    )
    
    meeting_url: Optional[str] = Field(
        default=None,
        description="URL for online meeting"
    )
    
    attendees: Optional[list[str]] = Field(
        default=None,
        sa_type=JSON,
        description="List of attendee email addresses"
    )
    
    attendee_count: int = Field(
        default=1,
        ge=1,
        description="Number of attendees"
    )
    
    # External references
    calendar_event_id: Optional[str] = Field(
        default=None,
        description="Calendar event ID (Google, Outlook, etc.)"
    )
    
    external_meeting_id: Optional[str] = Field(
        default=None,
        description="External meeting platform ID"
    )
    
    recording_url: Optional[str] = Field(
        default=None,
        description="URL to meeting recording"
    )
    
    # Meeting outcomes
    notes: Optional[str] = Field(
        default=None,
        description="Meeting notes or summary"
    )
    
    action_items: Optional[list[str]] = Field(
        default=None,
        sa_type=JSON,
        description="List of action items from the meeting"
    )
    
    decisions_made: Optional[list[str]] = Field(
        default=None,
        sa_type=JSON,
        description="List of decisions made in the meeting"
    )
    
    # Productivity metrics
    was_productive: Optional[bool] = Field(
        default=None,
        description="Self-assessment of meeting productivity"
    )
    
    could_have_been_email: bool = Field(
        default=False,
        description="Whether this meeting could have been an email"
    )
    
    preparation_time_minutes: int = Field(
        default=0,
        ge=0,
        description="Time spent preparing for the meeting"
    )
    
    # Auto-tracking
    auto_detected: bool = Field(
        default=False,
        description="Whether this meeting was auto-detected from calendar"
    )
    
    detection_confidence: Optional[float] = Field(
        default=None,
        description="Confidence score for auto-detection (0.0-1.0)"
    )
    
    # Sync status
    synced_to_calendar: bool = Field(
        default=False,
        description="Whether synced back to calendar"
    )
    
    included_in_reports: bool = Field(
        default=True,
        description="Whether to include in time reports"
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="meetings")
    project: Optional["Project"] = Relationship(back_populates="meetings")
    
    class Config:
        """Model configuration."""
        
        json_schema_extra = {
            "example": {
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
                "could_have_been_email": False
            }
        }
    
    def start_meeting(self) -> None:
        """Start the meeting timer."""
        self.actual_start = datetime.utcnow()
        self.status = MeetingStatus.IN_PROGRESS
        self.mark_updated()
    
    def end_meeting(self) -> None:
        """End the meeting and calculate duration."""
        if not self.actual_start:
            raise ValueError("Cannot end meeting - no start time recorded")
        
        self.actual_end = datetime.utcnow()
        self.status = MeetingStatus.COMPLETED
        self.calculate_duration()
        self.mark_updated()
    
    def calculate_duration(self) -> None:
        """Calculate actual duration from start and end times."""
        if not self.actual_start or not self.actual_end:
            return
        
        delta = self.actual_end - self.actual_start
        self.duration_minutes = int(delta.total_seconds() / 60)
    
    def add_attendee(self, email: str) -> None:
        """Add an attendee to the meeting."""
        if self.attendees is None:
            self.attendees = []
        
        if email not in self.attendees:
            self.attendees.append(email)
            self.attendee_count = len(self.attendees)
            self.mark_updated()
    
    def remove_attendee(self, email: str) -> None:
        """Remove an attendee from the meeting."""
        if self.attendees and email in self.attendees:
            self.attendees.remove(email)
            self.attendee_count = len(self.attendees) if self.attendees else 1
            self.mark_updated()
    
    def add_action_item(self, item: str) -> None:
        """Add an action item to the meeting."""
        if self.action_items is None:
            self.action_items = []
        
        if item not in self.action_items:
            self.action_items.append(item)
            self.mark_updated()
    
    def add_decision(self, decision: str) -> None:
        """Add a decision made in the meeting."""
        if self.decisions_made is None:
            self.decisions_made = []
        
        if decision not in self.decisions_made:
            self.decisions_made.append(decision)
            self.mark_updated()
    
    def mark_as_productive(self, productive: bool) -> None:
        """Mark meeting productivity assessment."""
        self.was_productive = productive
        self.mark_updated()
    
    def cancel_meeting(self, reason: Optional[str] = None) -> None:
        """Cancel the meeting."""
        self.status = MeetingStatus.CANCELLED
        if reason:
            self.set_metadata("cancellation_reason", reason)
        self.mark_updated()
    
    @property
    def is_ongoing(self) -> bool:
        """Check if meeting is currently in progress."""
        return self.status == MeetingStatus.IN_PROGRESS
    
    @property
    def is_overdue(self) -> bool:
        """Check if meeting is running over scheduled time."""
        if not self.scheduled_end or not self.actual_start:
            return False
        
        if self.status == MeetingStatus.COMPLETED:
            return False
        
        return datetime.utcnow() > self.scheduled_end
    
    @property
    def duration_hours(self) -> float:
        """Get duration in hours."""
        return self.duration_minutes / 60.0
    
    @property
    def scheduled_duration_minutes(self) -> Optional[int]:
        """Get scheduled duration in minutes."""
        if not self.scheduled_start or not self.scheduled_end:
            return None
        
        delta = self.scheduled_end - self.scheduled_start
        return int(delta.total_seconds() / 60)
    
    @property
    def time_variance_minutes(self) -> Optional[int]:
        """Get variance between scheduled and actual duration."""
        scheduled = self.scheduled_duration_minutes
        if scheduled is None or self.duration_minutes == 0:
            return None
        
        return self.duration_minutes - scheduled
    
    @property
    def formatted_duration(self) -> str:
        """Get formatted duration string (e.g., '1h 30m')."""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"

