"""Task service handling business logic, filtering, pagination, and metrics."""

from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskSummaryResponse


class TaskService:
    """Encapsulates business operations for Task items."""

    @staticmethod
    def get_task_by_id(db: Session, task_id: int, owner_id: int) -> Optional[Task]:
        """Fetch a specific task verifying ownership to prevent IDOR."""
        statement = select(Task).where(
            and_(Task.id == task_id, Task.owner_id == owner_id)
        )
        return db.scalars(statement).first()

    @staticmethod
    def create_task(db: Session, task_in: TaskCreate, owner_id: int) -> Task:
        """Create a new task assigned to the specified owner."""
        db_task = Task(
            title=task_in.title.strip(),
            description=task_in.description.strip() if task_in.description else None,
            status=task_in.status,
            priority=task_in.priority,
            due_date=task_in.due_date,
            owner_id=owner_id,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def get_tasks(
        db: Session,
        owner_id: int,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Task], int]:
        """Retrieve paginated, filtered, searched, and sorted tasks for a user."""
        statement = select(Task).where(Task.owner_id == owner_id)

        # Status filter
        if status is not None:
            statement = statement.where(Task.status == status)

        # Priority filter
        if priority is not None:
            statement = statement.where(Task.priority == priority)

        # Search by title
        if search:
            search_pattern = f"%{search.strip()}%"
            statement = statement.where(Task.title.ilike(search_pattern))

        # Calculate total matching count before pagination
        count_statement = select(func.count()).select_from(statement.order_by(None).subquery())
        total = db.scalar(count_statement) or 0

        # Dynamic sorting validation
        allowed_sort_fields = {
            "created_at": Task.created_at,
            "due_date": Task.due_date,
            "title": Task.title,
            "status": Task.status,
            "priority": Task.priority,
            "updated_at": Task.updated_at,
        }
        sort_column = allowed_sort_fields.get(sort_by, Task.created_at)

        if order.lower() == "asc":
            statement = statement.order_by(sort_column.asc())
        else:
            statement = statement.order_by(sort_column.desc())

        # Pagination
        statement = statement.offset(offset).limit(limit)
        tasks = list(db.scalars(statement).all())

        return tasks, total

    @staticmethod
    def update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
        """Update an existing task without overwriting unsupplied fields."""
        update_data = task_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "title" and value is not None:
                value = value.strip()
            elif field == "description" and value is not None:
                value = value.strip()
            setattr(task, field, value)

        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_status(db: Session, task: Task, new_status: TaskStatus) -> Task:
        """Update only the status of an existing task."""
        task.status = new_status
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task: Task) -> None:
        """Delete a task from the database."""
        db.delete(task)
        db.commit()

    @staticmethod
    def get_summary(db: Session, owner_id: int) -> TaskSummaryResponse:
        """Calculate task statistics for the user in a single optimized aggregation query."""
        now_expr = func.now()

        summary_stmt = select(
            func.count(Task.id).label("total"),
            func.count(case((Task.status == TaskStatus.PENDING, 1))).label("pending"),
            func.count(case((Task.status == TaskStatus.IN_PROGRESS, 1))).label("in_progress"),
            func.count(case((Task.status == TaskStatus.COMPLETED, 1))).label("completed"),
            func.count(
                case(
                    (
                        and_(
                            Task.due_date.is_not(None),
                            Task.due_date < now_expr,
                            Task.status != TaskStatus.COMPLETED,
                        ),
                        1,
                    )
                )
            ).label("overdue"),
        ).where(Task.owner_id == owner_id)

        row = db.execute(summary_stmt).one()

        return TaskSummaryResponse(
            total_tasks=row.total or 0,
            pending_tasks=row.pending or 0,
            in_progress_tasks=row.in_progress or 0,
            completed_tasks=row.completed or 0,
            overdue_tasks=row.overdue or 0,
        )


task_service = TaskService()
