"""Pydantic schemas for Task validation, serialization, and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base fields shared across task schemas."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters).",
        examples=["Complete Backend System Architecture"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Detailed description of the task.",
        examples=["Implement JWT authentication and SQLAlchemy 2.0 models."],
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority level: low, medium, or high.",
        examples=["high"],
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Optional due date in ISO 8601 format (e.g. 2026-12-31T23:59:59Z).",
        examples=["2026-12-31T23:59:59Z"],
    )


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Initial status of the task.",
        examples=["pending"],
    )


class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields are optional."""
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Updated task title.",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Updated task description.",
    )
    status: Optional[TaskStatus] = Field(
        default=None,
        description="Updated task status.",
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="Updated task priority.",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Updated due date in ISO 8601 format.",
    )


class TaskStatusUpdate(BaseModel):
    """Schema for PATCH /tasks/{task_id}/status."""
    status: TaskStatus = Field(
        ...,
        description="New status for the task.",
        examples=["in_progress"],
    )


class TaskRead(TaskBase):
    """Schema for task response returned to clients."""
    id: int
    status: TaskStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Paginated list of tasks."""
    items: List[TaskRead]
    total: int
    limit: int
    offset: int


class TaskSummaryResponse(BaseModel):
    """Dashboard task statistics for the authenticated user."""
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
