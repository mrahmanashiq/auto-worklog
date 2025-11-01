"""
Time tracking endpoints.

This module provides the core time tracking functionality including
starting/stopping work days, managing current activities, and real-time tracking.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from worklog_automation.api.v1.endpoints.auth import get_current_user
from worklog_automation.core.database import get_session
from worklog_automation.models.time_entry import TimeEntry, TimeEntryType
from worklog_automation.models.user import User, WorkDayStatus
from worklog_automation.schemas.tracking import (
    ActivityUpdateRequest,
    CurrentTrackingResponse,
    ManualEntryRequest,
    TrackingStartRequest,
    TrackingStatusResponse,
)

router = APIRouter()


@router.post("/start", response_model=TrackingStatusResponse)
async def start_work_day(
    request: TrackingStartRequest = TrackingStartRequest(),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TrackingStatusResponse:
    """
    Start work day tracking.
    
    Marks the beginning of the work day and optionally sets an initial activity.
    If work day is already started, returns current status.
    """
    user = current_user
    
    # Check if work day already started
    if user.current_day_status == WorkDayStatus.ACTIVE:
        return TrackingStatusResponse(
            status="already_started",
            message="Work day already started",
            work_day_status=user.current_day_status,
            started_at=user.daily_work_started_at,
            current_activity=user.current_activity,
        )
    
    # Start work day
    user.start_work_day()
    
    if request.initial_activity:
        user.set_current_activity(request.initial_activity)
    
    # Save changes
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return TrackingStatusResponse(
        status="started",
        message="Work day started successfully",
        work_day_status=user.current_day_status,
        started_at=user.daily_work_started_at,
        current_activity=user.current_activity,
    )


@router.post("/stop", response_model=TrackingStatusResponse)
async def stop_work_day(
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> TrackingStatusResponse:
    """
    Stop work day tracking.
    
    Marks the end of the work day and finalizes all tracking.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if work day is active
    if user.current_day_status not in [WorkDayStatus.ACTIVE, WorkDayStatus.PAUSED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Work day is not currently active"
        )
    
    # Stop work day
    user.end_work_day()
    
    # Save changes
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return TrackingStatusResponse(
        status="stopped",
        message="Work day stopped successfully",
        work_day_status=user.current_day_status,
        started_at=user.daily_work_started_at,
        ended_at=user.daily_work_ended_at,
        current_activity=None,
    )


@router.post("/pause", response_model=TrackingStatusResponse)
async def pause_work_day(
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> TrackingStatusResponse:
    """
    Pause work day tracking.
    
    Temporarily pauses tracking without ending the work day.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Pause work day
    user.pause_work_day()
    
    # Save changes
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return TrackingStatusResponse(
        status="paused",
        message="Work day paused successfully",
        work_day_status=user.current_day_status,
        started_at=user.daily_work_started_at,
        current_activity=user.current_activity,
    )


@router.post("/resume", response_model=TrackingStatusResponse)
async def resume_work_day(
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> TrackingStatusResponse:
    """
    Resume work day tracking.
    
    Resumes tracking after a pause.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Resume work day
    user.resume_work_day()
    
    # Save changes
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return TrackingStatusResponse(
        status="resumed",
        message="Work day resumed successfully",
        work_day_status=user.current_day_status,
        started_at=user.daily_work_started_at,
        current_activity=user.current_activity,
    )


@router.get("/status", response_model=CurrentTrackingResponse)
async def get_tracking_status(
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> CurrentTrackingResponse:
    """
    Get current tracking status.
    
    Returns the current work day status, active time entries, and other tracking info.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get ongoing time entries for today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    ongoing_entries_result = await session.execute(
        select(TimeEntry)
        .where(
            TimeEntry.user_id == user_id,
            TimeEntry.start_time >= today_start,
            TimeEntry.end_time.is_(None),
            TimeEntry.is_deleted == False,
        )
    )
    ongoing_entries = ongoing_entries_result.scalars().all()
    
    # Get today's completed entries
    completed_entries_result = await session.execute(
        select(TimeEntry)
        .where(
            TimeEntry.user_id == user_id,
            TimeEntry.start_time >= today_start,
            TimeEntry.end_time.is_not(None),
            TimeEntry.is_deleted == False,
        )
    )
    completed_entries = completed_entries_result.scalars().all()
    
    # Calculate total time today
    total_minutes_today = sum(entry.duration_minutes for entry in completed_entries)
    
    return CurrentTrackingResponse(
        work_day_status=user.current_day_status,
        started_at=user.daily_work_started_at,
        ended_at=user.daily_work_ended_at,
        current_activity=user.current_activity,
        ongoing_entries=ongoing_entries,
        total_minutes_today=total_minutes_today,
        entries_count_today=len(completed_entries) + len(ongoing_entries),
    )


@router.put("/activity", response_model=TrackingStatusResponse)
async def update_current_activity(
    request: ActivityUpdateRequest,
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> TrackingStatusResponse:
    """
    Update current activity description.
    
    Updates what the user is currently working on.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Get user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update activity
    user.set_current_activity(request.activity)
    
    # Save changes
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return TrackingStatusResponse(
        status="updated",
        message="Current activity updated successfully",
        work_day_status=user.current_day_status,
        started_at=user.daily_work_started_at,
        current_activity=user.current_activity,
    )


@router.post("/entry", response_model=dict)
async def add_manual_entry(
    request: ManualEntryRequest,
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user),  # Will implement auth later
) -> dict:
    """
    Add a manual time entry.
    
    Allows users to manually log time for activities with descriptions,
    duration, and optional project/commit associations.
    """
    # TODO: Replace with actual current user from auth
    user_id = UUID("12345678-1234-5678-9012-123456789012")  # Placeholder
    
    # Create time entry
    time_entry = TimeEntry(
        user_id=user_id,
        description=request.description,
        start_time=request.start_time or datetime.utcnow(),
        duration_minutes=request.duration_minutes,
        entry_type=request.entry_type or TimeEntryType.WORK,
        project_id=request.project_id,
        commit_hash=request.commit_hash,
        jira_ticket=request.jira_ticket,
        tags=request.tags,
        billable=request.billable,
    )
    
    # Set end time based on duration
    if request.start_time and request.duration_minutes:
        from datetime import timedelta
        time_entry.end_time = request.start_time + timedelta(minutes=request.duration_minutes)
    
    # Save entry
    session.add(time_entry)
    await session.commit()
    await session.refresh(time_entry)
    
    return {
        "status": "created",
        "message": "Manual time entry added successfully",
        "entry_id": str(time_entry.id),
        "duration_formatted": time_entry.formatted_duration,
    }

