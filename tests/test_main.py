"""
Pytest tests for the Task Manager FastAPI app.
Uses starlette.testclient.TestClient for synchronous testing.
"""
import pytest
from starlette.testclient import TestClient

# Adjust path so the test runner can find main.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main as app_module
from main import app


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset in-memory task list and id counter before every test."""
    app_module.tasks.clear()
    app_module._next_id = 1
    yield
    app_module.tasks.clear()
    app_module._next_id = 1


client = TestClient(app)


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
    assert data["title"] == "Buy groceries"
    assert isinstance(data["id"], int)


def test_delete_task():
    """POST a task then DELETE it; confirm the task is removed."""
    # Create a task
    create_resp = client.post("/tasks", json={"title": "Task to delete"})
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    # Delete the task
    delete_resp = client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"deleted": task_id}

    # Confirm it no longer appears in the list
    list_resp = client.get("/tasks")
    assert list_resp.status_code == 200
    ids = [t["id"] for t in list_resp.json()]
    assert task_id not in ids
