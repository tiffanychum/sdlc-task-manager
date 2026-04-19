from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Task Manager")

# In-memory storage
tasks: List[dict] = []
_next_id: int = 1


class TaskCreate(BaseModel):
    title: str


@app.get("/tasks", response_model=List[dict])
def list_tasks():
    """Return all tasks."""
    return tasks


@app.post("/tasks", response_model=dict, status_code=201)
def create_task(body: TaskCreate):
    """Create a new task and return it."""
    global _next_id
    task = {"id": _next_id, "title": body.title}
    tasks.append(task)
    _next_id += 1
    return task


@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int):
    """Delete a task by id and return {"deleted": id}."""
    global tasks
    for task in tasks:
        if task["id"] == task_id:
            tasks = [t for t in tasks if t["id"] != task_id]
            return {"deleted": task_id}
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.get("/")
def index():
    return FileResponse("index.html")
