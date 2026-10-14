"""Tests for Dashboard and Task Summary endpoint calculations."""

from datetime import datetime, timezone, timedelta
from fastapi import status
from fastapi.testclient import TestClient


def test_task_summary_metrics(client: TestClient, auth_headers_a: dict) -> None:
    """Test aggregated metrics: total, pending, in_progress, completed, and overdue."""
    now = datetime.now(timezone.utc)
    past_due = (now - timedelta(days=2)).isoformat()
    future_due = (now + timedelta(days=5)).isoformat()

    # 1. Pending task with future due date (not overdue)
    client.post(
        "/api/v1/tasks",
        json={"title": "Task 1", "status": "pending", "due_date": future_due},
        headers=auth_headers_a,
    )
    # 2. In-progress task with past due date (OVERDUE!)
    client.post(
        "/api/v1/tasks",
        json={"title": "Task 2", "status": "in_progress", "due_date": past_due},
        headers=auth_headers_a,
    )
    # 3. Pending task with past due date (OVERDUE!)
    client.post(
        "/api/v1/tasks",
        json={"title": "Task 3", "status": "pending", "due_date": past_due},
        headers=auth_headers_a,
    )
    # 4. Completed task with past due date (COMPLETED - must NOT count as overdue!)
    client.post(
        "/api/v1/tasks",
        json={"title": "Task 4", "status": "completed", "due_date": past_due},
        headers=auth_headers_a,
    )
    # 5. Completed task without due date
    client.post(
        "/api/v1/tasks",
        json={"title": "Task 5", "status": "completed"},
        headers=auth_headers_a,
    )

    response = client.get("/api/v1/tasks/summary", headers=auth_headers_a)
    assert response.status_code == status.HTTP_200_OK
    summary = response.json()

    assert summary["total_tasks"] == 5
    assert summary["pending_tasks"] == 2
    assert summary["in_progress_tasks"] == 1
    assert summary["completed_tasks"] == 2
    assert summary["overdue_tasks"] == 2  # Tasks 2 & 3
