"""Tests for Task CRUD operations, filtering, search, pagination, and multi-tenant security."""

from datetime import datetime, timezone, timedelta
from fastapi import status
from fastapi.testclient import TestClient


def test_create_task_success(client: TestClient, auth_headers_a: dict) -> None:
    """Test successful task creation with all valid attributes."""
    due = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    payload = {
        "title": "Design REST API schema",
        "description": "Create Pydantic v2 validation models",
        "priority": "high",
        "status": "pending",
        "due_date": due,
    }
    response = client.post("/api/v1/tasks", json=payload, headers=auth_headers_a)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["priority"] == "high"
    assert data["status"] == "pending"
    assert "id" in data
    assert "owner_id" in data


def test_create_task_empty_title(client: TestClient, auth_headers_a: dict) -> None:
    """Test task creation fails when title is empty."""
    response = client.post(
        "/api/v1/tasks",
        json={"title": ""},
        headers=auth_headers_a,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_task_invalid_priority(client: TestClient, auth_headers_a: dict) -> None:
    """Test task creation fails with invalid priority string."""
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Some task", "priority": "urgent_critical"},
        headers=auth_headers_a,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_task_invalid_status(client: TestClient, auth_headers_a: dict) -> None:
    """Test task creation fails with invalid status string."""
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Some task", "status": "finished_done"},
        headers=auth_headers_a,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_task_by_id(client: TestClient, auth_headers_a: dict) -> None:
    """Test fetching a task by ID."""
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "Fetchable Task"},
        headers=auth_headers_a,
    )
    task_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers_a)
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.json()["id"] == task_id


def test_get_nonexistent_task(client: TestClient, auth_headers_a: dict) -> None:
    """Test retrieving non-existent task returns 404."""
    response = client.get("/api/v1/tasks/99999", headers=auth_headers_a)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_task(client: TestClient, auth_headers_a: dict) -> None:
    """Test updating task fields."""
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "priority": "low"},
        headers=auth_headers_a,
    )
    task_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated Title", "priority": "high"},
        headers=auth_headers_a,
    )
    assert update_resp.status_code == status.HTTP_200_OK
    data = update_resp.json()
    assert data["title"] == "Updated Title"
    assert data["priority"] == "high"


def test_patch_task_status(client: TestClient, auth_headers_a: dict) -> None:
    """Test updating only task status via PATCH."""
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "Task for status update", "status": "pending"},
        headers=auth_headers_a,
    )
    task_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=auth_headers_a,
    )
    assert patch_resp.status_code == status.HTTP_200_OK
    assert patch_resp.json()["status"] == "in_progress"


def test_delete_task(client: TestClient, auth_headers_a: dict) -> None:
    """Test deleting a task."""
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "To be deleted"},
        headers=auth_headers_a,
    )
    task_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers_a)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

    # Verification: task must no longer exist
    get_resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers_a)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_cross_user_isolation(
    client: TestClient, auth_headers_a: dict, auth_headers_b: dict
) -> None:
    """Test strict data isolation: User B cannot access, modify, or delete User A's task."""
    # User A creates a task
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "User A Private Task"},
        headers=auth_headers_a,
    )
    task_id = create_resp.json()["id"]

    # User B attempts GET -> 404
    resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers_b)
    assert resp.status_code == status.HTTP_404_NOT_FOUND

    # User B attempts PUT -> 404
    resp = client.put(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Hacked Title"},
        headers=auth_headers_b,
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND

    # User B attempts PATCH -> 404
    resp = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "completed"},
        headers=auth_headers_b,
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND

    # User B attempts DELETE -> 404
    resp = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers_b)
    assert resp.status_code == status.HTTP_404_NOT_FOUND

    # Verify task still intact under User A
    verify_resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers_a)
    assert verify_resp.status_code == status.HTTP_200_OK
    assert verify_resp.json()["title"] == "User A Private Task"


def test_filter_and_search_tasks(client: TestClient, auth_headers_a: dict) -> None:
    """Test filtering by status, priority, and searching by title."""
    client.post(
        "/api/v1/tasks",
        json={"title": "Setup PostgreSQL Database", "status": "completed", "priority": "high"},
        headers=auth_headers_a,
    )
    client.post(
        "/api/v1/tasks",
        json={"title": "Setup Redis Cache", "status": "pending", "priority": "low"},
        headers=auth_headers_a,
    )
    client.post(
        "/api/v1/tasks",
        json={"title": "Write Unit Tests", "status": "in_progress", "priority": "high"},
        headers=auth_headers_a,
    )

    # Filter by status = pending
    resp = client.get("/api/v1/tasks?status=pending", headers=auth_headers_a)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Setup Redis Cache"

    # Filter by priority = high
    resp = client.get("/api/v1/tasks?priority=high", headers=auth_headers_a)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["total"] == 2

    # Search by title keyword 'Database'
    resp = client.get("/api/v1/tasks?search=Database", headers=auth_headers_a)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["total"] == 1
    assert "PostgreSQL" in resp.json()["items"][0]["title"]


def test_sorting_and_pagination(client: TestClient, auth_headers_a: dict) -> None:
    """Test pagination limit/offset and ordering."""
    for i in range(5):
        client.post(
            "/api/v1/tasks",
            json={"title": f"Task Number {i}"},
            headers=auth_headers_a,
        )

    # Paginate: limit 2, offset 0
    resp = client.get("/api/v1/tasks?limit=2&offset=0", headers=auth_headers_a)
    assert resp.status_code == status.HTTP_200_OK
    page1 = resp.json()
    assert page1["total"] == 5
    assert len(page1["items"]) == 2
    assert page1["limit"] == 2
    assert page1["offset"] == 0

    # Paginate: limit 2, offset 2
    resp = client.get("/api/v1/tasks?limit=2&offset=2", headers=auth_headers_a)
    assert resp.status_code == status.HTTP_200_OK
    page2 = resp.json()
    assert len(page2["items"]) == 2
    assert page1["items"][0]["id"] != page2["items"][0]["id"]
