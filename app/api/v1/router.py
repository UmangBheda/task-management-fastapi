"""Aggregated API v1 Router."""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, summary, tasks

api_router = APIRouter()

# Include authentication endpoints
api_router.include_router(auth.router)

# IMPORTANT: summary.router is included BEFORE tasks.router
# to ensure /tasks/summary is evaluated before /tasks/{task_id}
api_router.include_router(summary.router)
api_router.include_router(tasks.router)
