from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path

app = FastAPI(title="Task Manager")

# In-memory storage
tasks: list[dict] = []
_next_id: int = 1


class TaskCreate(BaseModel):
    title: str


@app.get("/tasks", response_model=list[dict])
def list_tasks():
    """Return all tasks."""
    return tasks


@app.post("/tasks", response_model=dict, status_code=201)
def create_task(payload: TaskCreate):
    """Create a new task and return it."""
    global _next_id
    task = {"id": _next_id, "title": payload.title}
    tasks.append(task)
    _next_id += 1
    return task


@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int):
    """Remove a task by id and return {"deleted": id}."""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return {"deleted": task_id}
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    """Serve the single-page frontend."""
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(content=html_path.read_text())
