"""
Main API router for version 1.

This module sets up the main API router and includes all sub-routers
for different endpoint groups.
"""

from fastapi import APIRouter

from worklog_automation.api.v1.endpoints import (
    auth,
    meetings,
    projects,
    reports,
    time_entries,
    users,
    tracking,
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"],
)

api_router.include_router(
    time_entries.router,
    prefix="/time-entries",
    tags=["time-entries"],
)

api_router.include_router(
    meetings.router,
    prefix="/meetings",
    tags=["meetings"],
)

api_router.include_router(
    tracking.router,
    prefix="/tracking",
    tags=["tracking"],
)

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["reports"],
)

