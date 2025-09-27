"""
Meeting endpoints.

This module provides meeting management functionality including
one-click meeting timers, meeting creation, and meeting tracking.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from worklog_automation.core.database import get_session
from worklog_automation.models.meeting import Meeting, MeetingStatus, MeetingType
from worklog_automation.schemas.meetings import (
    MeetingCreateRequest,
    MeetingResponse,
    MeetingStartRequest,
    MeetingUpdateRequest,
)

router = APIRouter()


@router.post("/start", response_model=MeetingResponse)
async def start_meeting_timer(
    request: MeetingStartRequest,
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> MeetingResponse:
    """
    Start a meeting timer.
    
    One-click meeting start functionality - creates a new meeting
    and immediately starts timing it.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Create new meeting
    meeting = Meeting(
        user_id=user_id,
        title=request.title,
        description=request.description,
        meeting_type=request.meeting_type,
        project_id=request.project_id,
        location=request.location,
        attendee_count=request.attendee_count or 1,
    )
    
    # Start the meeting
    meeting.start_meeting()
    
    # Save meeting
    session.add(meeting)
    await session.commit()
    await session.refresh(meeting)
    
    return MeetingResponse.from_orm(meeting)


@router.post("/{meeting_id}/stop", response_model=MeetingResponse)
async def stop_meeting_timer(
    meeting_id: UUID,
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> MeetingResponse:
    """
    Stop a meeting timer.
    
    Stops the meeting timer and calculates the final duration.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get meeting
    result = await session.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.user_id == user_id,
            Meeting.is_deleted == False,
        )
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    if meeting.status != MeetingStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting is not currently in progress"
        )
    
    # Stop the meeting
    meeting.end_meeting()
    
    # Save changes
    session.add(meeting)
    await session.commit()
    await session.refresh(meeting)
    
    return MeetingResponse.from_orm(meeting)


@router.post("/", response_model=MeetingResponse)
async def create_meeting(
    request: MeetingCreateRequest,
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> MeetingResponse:
    """
    Create a scheduled meeting.
    
    Creates a meeting with scheduled times but doesn't start it immediately.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Create meeting
    meeting = Meeting(
        user_id=user_id,
        title=request.title,
        description=request.description,
        meeting_type=request.meeting_type,
        project_id=request.project_id,
        scheduled_start=request.scheduled_start,
        scheduled_end=request.scheduled_end,
        location=request.location,
        meeting_url=request.meeting_url,
        attendees=request.attendees,
        attendee_count=len(request.attendees) if request.attendees else 1,
        status=MeetingStatus.SCHEDULED,
    )
    
    # Save meeting
    session.add(meeting)
    await session.commit()
    await session.refresh(meeting)
    
    return MeetingResponse.from_orm(meeting)


@router.get("/ongoing", response_model=list[MeetingResponse])
async def get_ongoing_meetings(
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> list[MeetingResponse]:
    """
    Get currently ongoing meetings.
    
    Returns all meetings that are currently in progress.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get ongoing meetings
    result = await session.execute(
        select(Meeting).where(
            Meeting.user_id == user_id,
            Meeting.status == MeetingStatus.IN_PROGRESS,
            Meeting.is_deleted == False,
        )
    )
    meetings = result.scalars().all()
    
    return [MeetingResponse.from_orm(meeting) for meeting in meetings]


@router.get("/today", response_model=list[MeetingResponse])
async def get_todays_meetings(
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> list[MeetingResponse]:
    """
    Get today's meetings.
    
    Returns all meetings for the current day.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get today's date range
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Get today's meetings
    result = await session.execute(
        select(Meeting).where(
            Meeting.user_id == user_id,
            Meeting.created_at >= today_start,
            Meeting.created_at <= today_end,
            Meeting.is_deleted == False,
        ).order_by(Meeting.created_at)
    )
    meetings = result.scalars().all()
    
    return [MeetingResponse.from_orm(meeting) for meeting in meetings]


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: UUID,
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> MeetingResponse:
    """
    Get a specific meeting by ID.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get meeting
    result = await session.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.user_id == user_id,
            Meeting.is_deleted == False,
        )
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    return MeetingResponse.from_orm(meeting)


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: UUID,
    request: MeetingUpdateRequest,
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> MeetingResponse:
    """
    Update a meeting.
    
    Allows updating meeting details, notes, productivity assessment, etc.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get meeting
    result = await session.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.user_id == user_id,
            Meeting.is_deleted == False,
        )
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(meeting, field):
            setattr(meeting, field, value)
    
    # Handle special updates
    if request.notes is not None:
        meeting.notes = request.notes
    
    if request.was_productive is not None:
        meeting.mark_as_productive(request.was_productive)
    
    if request.action_items:
        for item in request.action_items:
            meeting.add_action_item(item)
    
    meeting.mark_updated()
    
    # Save changes
    session.add(meeting)
    await session.commit()
    await session.refresh(meeting)
    
    return MeetingResponse.from_orm(meeting)


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: UUID,
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> dict:
    """
    Delete a meeting (soft delete).
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get meeting
    result = await session.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.user_id == user_id,
            Meeting.is_deleted == False,
        )
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    # Soft delete
    meeting.soft_delete()
    
    # Save changes
    session.add(meeting)
    await session.commit()
    
    return {"message": "Meeting deleted successfully"}

