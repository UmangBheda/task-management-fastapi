"""Task CRUD endpoints with filtering, pagination, sorting, and ownership checks."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskRead,
    TaskListResponse,
)
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a task for the authenticated user. Owner ID is automatically assigned from the user's token.",
)
def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Task:
    """Create a new task."""
    return task_service.create_task(db, task_in=task_in, owner_id=current_user.id)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List current user's tasks",
    description="Returns a paginated list of tasks belonging to the current user with filtering, search, and sorting options.",
)
def list_tasks(
    status: Optional[TaskStatus] = Query(
        default=None,
        description="Filter tasks by status (pending, in_progress, completed)",
    ),
    priority: Optional[TaskPriority] = Query(
        default=None,
        description="Filter tasks by priority (low, medium, high)",
    ),
    search: Optional[str] = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Search tasks containing text in their title",
    ),
    sort_by: str = Query(
        default="created_at",
        pattern="^(created_at|due_date|title|status|priority|updated_at)$",
        description="Column to sort tasks by",
    ),
    order: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort direction (asc or desc)",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of tasks to return (pagination limit)",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of tasks to skip (pagination offset)",
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TaskListResponse:
    """Retrieve filtered, sorted, and paginated tasks for the current user."""
    tasks, total = task_service.get_tasks(
        db,
        owner_id=current_user.id,
        status=status,
        priority=priority,
        search=search,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
    )
    return TaskListResponse(
        items=tasks,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Retrieve a specific task",
    description="Fetches a single task by its ID. Returns 404 if the task does not exist or does not belong to the user.",
)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Task:
    """Get single task by ID with ownership enforcement."""
    task = task_service.get_task_by_id(db, task_id=task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you do not have permission to access it.",
        )
    return task


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    description="Updates task properties. Only provided fields are updated; unprovided fields retain their previous values.",
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Task:
    """Update task details with ownership enforcement."""
    task = task_service.get_task_by_id(db, task_id=task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you do not have permission to access it.",
        )
    return task_service.update_task(db, task=task, task_in=task_in)


@router.patch(
    "/{task_id}/status",
    response_model=TaskRead,
    summary="Update task status",
    description="Lightweight endpoint specifically for updating the status of a task.",
)
def update_task_status(
    task_id: int,
    status_in: TaskStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Task:
    """Update task status only."""
    task = task_service.get_task_by_id(db, task_id=task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you do not have permission to access it.",
        )
    return task_service.update_status(db, task=task, new_status=status_in.status)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently deletes a task. Returns 404 if the task does not exist or does not belong to the user.",
)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Response:
    """Delete a task."""
    task = task_service.get_task_by_id(db, task_id=task_id, owner_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you do not have permission to access it.",
        )
    task_service.delete_task(db, task=task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
