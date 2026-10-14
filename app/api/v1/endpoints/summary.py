"""Dashboard and Summary endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.task import TaskSummaryResponse
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["Dashboard & Summary"])


@router.get(
    "/summary",
    response_model=TaskSummaryResponse,
    summary="Get task dashboard summary",
    description="Calculates total, pending, in-progress, completed, and overdue task metrics for the authenticated user.",
)
def get_task_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TaskSummaryResponse:
    """Return task metrics for the current user's dashboard."""
    return task_service.get_summary(db, owner_id=current_user.id)
