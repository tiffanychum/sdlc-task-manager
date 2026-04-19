"""
Pytest tests for the Task Manager FastAPI app.
Uses starlette.testclient.TestClient for synchronous testing.
Each test resets the in-memory state to ensure isolation.
"""
import pytest
from starlette.testclient import TestClient

import sys
import os

# Ensure the project root is on the path so `main` can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main as app_module
from main import app


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset in-memory task list and ID counter before every test."""
    app_module.tasks.clear()
    app_module._next_id = 1
    yield
    app_module.tasks.clear()
    app_module._next_id = 1


client = TestClient(app)


def test_list_tasks_empty():
    """GET /tasks on a fresh store should return an empty list."""
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
    """POST then DELETE should remove the task; subsequent GET should not include it."""
    # Create a task
    create_resp = client.post("/tasks", json={"title": "Write tests"})
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    # Delete the task
    delete_resp = client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"deleted": task_id}

    # Confirm it's gone
    list_resp = client.get("/tasks")
    assert list_resp.status_code == 200
    ids = [t["id"] for t in list_resp.json()]
    assert task_id not in ids
