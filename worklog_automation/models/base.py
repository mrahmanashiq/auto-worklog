"""
Base model with common fields and functionality.

This module provides the base model class that all other models inherit from,
ensuring consistent ID, timestamp, and metadata fields across all entities.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """
    Base model with common fields for all database entities.
    
    Provides:
    - UUID primary key
    - Created/updated timestamps
    - Soft delete functionality
    - Common utility methods
    """
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the record"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the record was created"
    )
    
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the record was last updated"
    )
    
    is_deleted: bool = Field(
        default=False,
        description="Soft delete flag"
    )
    
    extra_metadata: Optional[dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="Additional metadata for the record"
    )
    
    class Config:
        """SQLModel configuration."""
        
        # Enable arbitrary types for complex fields
        arbitrary_types_allowed = True
        
        # JSON schema configuration
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2024-01-15T08:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "is_deleted": False,
                "extra_metadata": {}
            }
        }
    
    def mark_updated(self) -> None:
        """Mark the record as updated with current timestamp."""
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self) -> None:
        """Soft delete the record."""
        self.is_deleted = True
        self.mark_updated()
    
    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.mark_updated()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set a metadata field."""
        if self.extra_metadata is None:
            self.extra_metadata = {}
        self.extra_metadata[key] = value
        self.mark_updated()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata field value."""
        if self.extra_metadata is None:
            return default
        return self.extra_metadata.get(key, default)

