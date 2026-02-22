"""
Daily Task Manager - FastAPI Backend
A modern task management microservice with full CRUD operations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module
from typing import List, Optional
from datetime import datetime
from enum import Enum
import json
import os

# Initialize FastAPI app
app = FastAPI(
    title="Daily Task Manager API",
    description="A RESTful API for managing daily tasks",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
DATA_FILE = "tasks.json"


# Enums
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Pydantic Models
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[str] = None
    tags: Optional[List[str]] = None


class Task(TaskBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Complete project report",
                "description": "Finalize and submit quarterly report",
                "priority": "high",
                "status": "in_progress",
                "due_date": "2026-02-28",
                "tags": ["work", "urgent"],
                "created_at": "2026-02-21T10:30:00",
                "updated_at": "2026-02-21T11:00:00",
            }
        }


# Task Management
class TaskManager:
    def __init__(self, file_path: str = DATA_FILE):
        self.file_path = file_path
        self.tasks: List[dict] = self.load_tasks()
        self.next_id = self._get_next_id()

    def load_tasks(self) -> List[dict]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_tasks(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2)

    def _get_next_id(self) -> int:
        return max([t["id"] for t in self.tasks], default=0) + 1

    def create_task(self, task_data: TaskCreate) -> Task:
        new_task = {
            "id": self.next_id,
            "title": task_data.title,
            "description": task_data.description,
            "priority": task_data.priority,
            "status": task_data.status,
            "due_date": task_data.due_date,
            "tags": task_data.tags,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self.tasks.append(new_task)
        self.next_id += 1
        self.save_tasks()
        return Task(**new_task)

    def get_all_tasks(
        self, status: Optional[str] = None, priority: Optional[str] = None
    ) -> List[Task]:
        filtered_tasks = self.tasks
        if status:
            filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]
        return [Task(**t) for t in filtered_tasks]

    def get_task(self, task_id: int) -> Task:
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return Task(**task)

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Task:
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        update_data = task_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            task[field] = value
        task["updated_at"] = datetime.now().isoformat()
        self.save_tasks()
        return Task(**task)

    def delete_task(self, task_id: int) -> dict:
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self.save_tasks()
        return {"message": f"Task {task_id} deleted successfully"}

    def get_statistics(self) -> dict:
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t["status"] == TaskStatus.COMPLETED])
        pending = len([t for t in self.tasks if t["status"] == TaskStatus.PENDING])
        in_progress = len(
            [t for t in self.tasks if t["status"] == TaskStatus.IN_PROGRESS]
        )

        return {
            "total_tasks": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
        }


# Initialize task manager
task_manager = TaskManager()


# Routes
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Daily Task Manager API", "version": "1.0.0"}


@app.post("/tasks", response_model=Task, tags=["Tasks"], status_code=201)
async def create_task(task: TaskCreate):
    """Create a new task"""
    return task_manager.create_task(task)


@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
async def get_tasks(status: Optional[str] = None, priority: Optional[str] = None):
    """Get all tasks with optional filtering"""
    return task_manager.get_all_tasks(status, priority)


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def get_task(task_id: int):
    """Get a specific task by ID"""
    return task_manager.get_task(task_id)


@app.patch("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update a task"""
    return task_manager.update_task(task_id, task_update)


@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(task_id: int):
    """Delete a task"""
    return task_manager.delete_task(task_id)


@app.get("/statistics", tags=["Analytics"])
async def get_statistics():
    """Get task statistics"""
    return task_manager.get_statistics()


@app.delete("/tasks", tags=["Tasks"])
async def clear_all_tasks():
    """Clear all tasks"""
    task_manager.tasks = []
    task_manager.save_tasks()
    return {"message": "All tasks cleared"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
