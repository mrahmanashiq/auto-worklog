"""
Project model for organizing work activities.

This module defines the Project model for categorizing time entries
and managing project-specific settings and integrations.
"""

from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from worklog_automation.models.base import BaseModel


class ProjectStatus(str, Enum):
    """Project status for tracking lifecycle."""
    
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, Enum):
    """Project priority levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Project(BaseModel, table=True):
    """
    Project model for organizing work activities.
    
    Projects are used to categorize time entries, meetings, and tasks.
    They can be linked to external systems like Jira or GitHub.
    """
    
    __tablename__ = "projects"
    
    # Basic information
    name: str = Field(
        min_length=1,
        max_length=200,
        description="Project name"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Project description"
    )
    
    code: Optional[str] = Field(
        default=None,
        unique=True,
        max_length=20,
        description="Short project code (e.g., 'PROJ-001')"
    )
    
    # Status and priority
    status: ProjectStatus = Field(
        default=ProjectStatus.ACTIVE,
        description="Current project status"
    )
    
    priority: ProjectPriority = Field(
        default=ProjectPriority.MEDIUM,
        description="Project priority level"
    )
    
    # Ownership
    owner_id: UUID = Field(
        foreign_key="users.id",
        description="Project owner user ID"
    )
    
    # External integrations
    jira_project_key: Optional[str] = Field(
        default=None,
        description="Jira project key for integration"
    )
    
    github_repo_url: Optional[str] = Field(
        default=None,
        description="GitHub repository URL"
    )
    
    teams_channel_webhook: Optional[str] = Field(
        default=None,
        description="Teams channel webhook for notifications"
    )
    
    # Time tracking settings
    default_hourly_rate: Optional[float] = Field(
        default=None,
        description="Default hourly rate for billing"
    )
    
    requires_time_tracking: bool = Field(
        default=True,
        description="Whether time tracking is required for this project"
    )
    
    auto_create_jira_worklogs: bool = Field(
        default=False,
        description="Auto-create Jira worklogs for time entries"
    )
    
    # Budget and deadlines
    estimated_hours: Optional[float] = Field(
        default=None,
        description="Estimated total hours for the project"
    )
    
    budget_amount: Optional[float] = Field(
        default=None,
        description="Project budget amount"
    )
    
    start_date: Optional[date] = Field(
        default=None,
        description="Project start date"
    )
    
    end_date: Optional[date] = Field(
        default=None,
        description="Project end date"
    )
    
    # Display settings
    color: str = Field(
        default="#3498db",
        description="Hex color code for UI display"
    )
    
    icon: Optional[str] = Field(
        default=None,
        description="Icon name or emoji for UI display"
    )
    
    # Relationships
    owner: "User" = Relationship(back_populates="projects")
    time_entries: list["TimeEntry"] = Relationship(back_populates="project")
    meetings: list["Meeting"] = Relationship(back_populates="project")
    
    class Config:
        """Model configuration."""
        
        json_schema_extra = {
            "example": {
                "name": "Website Redesign",
                "description": "Complete redesign of company website",
                "code": "WEB-2024",
                "status": "active",
                "priority": "high",
                "jira_project_key": "WEB",
                "github_repo_url": "https://github.com/company/website",
                "estimated_hours": 160.0,
                "budget_amount": 25000.0,
                "start_date": "2024-01-15",
                "end_date": "2024-03-15",
                "color": "#e74c3c",
                "icon": "🌐"
            }
        }
    
    @property
    def is_active(self) -> bool:
        """Check if project is currently active."""
        return self.status == ProjectStatus.ACTIVE
    
    @property
    def is_overdue(self) -> bool:
        """Check if project is past its end date."""
        if not self.end_date:
            return False
        
        from datetime import date
        return date.today() > self.end_date
    
    def calculate_total_logged_hours(self) -> float:
        """Calculate total hours logged for this project."""
        return sum(entry.duration_minutes / 60.0 for entry in self.time_entries if not entry.is_deleted)
    
    def calculate_remaining_budget(self) -> Optional[float]:
        """Calculate remaining budget based on logged hours and hourly rate."""
        if not self.budget_amount or not self.default_hourly_rate:
            return None
        
        logged_hours = self.calculate_total_logged_hours()
        spent_amount = logged_hours * self.default_hourly_rate
        return max(0, self.budget_amount - spent_amount)
    
    def get_progress_percentage(self) -> Optional[float]:
        """Get project progress as percentage of estimated hours."""
        if not self.estimated_hours:
            return None
        
        logged_hours = self.calculate_total_logged_hours()
        return min(100.0, (logged_hours / self.estimated_hours) * 100.0)
