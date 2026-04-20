"""
Tests for the Task Manager FastAPI app.
Uses starlette.testclient.TestClient for synchronous test execution.
Each test gets a fresh in-memory state via the module-level fixture.
"""
import pytest
from starlette.testclient import TestClient

# ── Ensure a clean state before every test ───────────────────────────────────
import main as app_module


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task list and ID counter before each test."""
    app_module.tasks.clear()
    app_module._next_id = 1
    yield
    app_module.tasks.clear()
    app_module._next_id = 1


# Create a single TestClient reused across all tests
client = TestClient(app_module.app)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_list_tasks_empty():
    """GET /tasks should return an empty list when no tasks exist."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task():
    """POST /tasks should create a task and return it with an id field."""
    response = client.post("/tasks", json={"title": "Buy groceries"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["title"] == "Buy groceries"


def test_delete_task():
    """POST then DELETE should remove the task; subsequent GET returns empty list."""
    # Create a task
    create_resp = client.post("/tasks", json={"title": "Write tests"})
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    # Delete it
    delete_resp = client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"deleted": task_id}

    # Confirm it's gone
    list_resp = client.get("/tasks")
    assert list_resp.status_code == 200
    assert list_resp.json() == []
