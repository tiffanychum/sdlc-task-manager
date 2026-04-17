from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task storage
tasks = []
next_id = 1

class TaskCreate(BaseModel):
    title: str

class Task(BaseModel):
    id: int
    title: str

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return tasks

@app.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    global next_id
    new_task = Task(id=next_id, title=task.title)
    tasks.append(new_task)
    next_id += 1
    return new_task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    global tasks
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return {"deleted": task_id}
    raise HTTPException(status_code=404, detail="Task not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)