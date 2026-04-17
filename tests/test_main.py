import pytest
from starlette.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_tasks_empty():
    """Test that GET /tasks returns empty list initially"""
    # Reset tasks for clean test
    from main import tasks
    tasks.clear()
    
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_create_task():
    """Test that POST /tasks creates a new task and returns it with an id"""
    # Reset tasks for clean test
    from main import tasks, next_id
    tasks.clear()
    
    task_data = {"title": "Test Task"}
    response = client.post("/tasks", json=task_data)
    
    assert response.status_code == 200
    created_task = response.json()
    assert "id" in created_task
    assert created_task["title"] == "Test Task"
    assert isinstance(created_task["id"], int)

def test_delete_task():
    """Test POST then DELETE workflow"""
    # Reset tasks for clean test
    from main import tasks
    tasks.clear()
    
    # First create a task
    task_data = {"title": "Task to Delete"}
    create_response = client.post("/tasks", json=task_data)
    assert create_response.status_code == 200
    created_task = create_response.json()
    task_id = created_task["id"]
    
    # Then delete it
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": task_id}
    
    # Verify it's gone
    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert list_response.json() == []