"""
Unit and integration tests for Daily Task Manager API
Tests all CRUD operations and filtering functionality
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app, TaskManager
from backend.app.main import TaskCreate, TaskUpdate, TaskStatus, TaskPriority


class TestAPIEndpoints:
    """Test FastAPI endpoints"""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Daily Task Manager API"
        assert "version" in response.json()

    def test_create_task(self, client, sample_task):
        """Test creating a new task"""
        response = client.post("/tasks", json=sample_task)
        assert response.status_code == 201

        task = response.json()
        assert task["title"] == sample_task["title"]
        assert task["description"] == sample_task["description"]
        assert task["priority"] == sample_task["priority"]
        assert task["status"] == sample_task["status"]
        assert "id" in task
        assert "created_at" in task
        assert "updated_at" in task

    def test_create_task_minimal(self, client):
        """Test creating a task with minimal fields"""
        task_data = {"title": "Simple Task"}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201

        task = response.json()
        assert task["title"] == "Simple Task"
        assert task["priority"] == "medium"
        assert task["status"] == "pending"
        assert task["description"] is None

    def test_create_task_invalid_title(self, client):
        """Test that empty title returns error"""
        response = client.post("/tasks", json={"title": ""})
        assert response.status_code == 422

    def test_get_all_tasks(self, client, sample_tasks):
        """Test retrieving all tasks"""
        # Create multiple tasks
        for task_data in sample_tasks:
            client.post("/tasks", json=task_data)

        response = client.get("/tasks")
        assert response.status_code == 200

        tasks = response.json()
        assert len(tasks) == len(sample_tasks)

    def test_get_all_tasks_empty(self, client):
        """Test retrieving tasks when none exist"""
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_task_by_id(self, client, sample_task):
        """Test retrieving a specific task by ID"""
        # Create a task
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        # Get the task
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200

        task = response.json()
        assert task["id"] == task_id
        assert task["title"] == sample_task["title"]

    def test_get_nonexistent_task(self, client):
        """Test that getting a non-existent task returns 404"""
        response = client.get("/tasks/9999")
        assert response.status_code == 404

    def test_update_task(self, client, sample_task):
        """Test updating a task"""
        # Create a task
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        # Update the task
        updates = {"title": "Updated Title", "status": "completed", "priority": "high"}
        response = client.patch(f"/tasks/{task_id}", json=updates)
        assert response.status_code == 200

        task = response.json()
        assert task["title"] == "Updated Title"
        assert task["status"] == "completed"
        assert task["priority"] == "high"

    def test_update_task_partial(self, client, sample_task):
        """Test partial update of a task"""
        # Create a task
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        # Update only the status
        response = client.patch(f"/tasks/{task_id}", json={"status": "in_progress"})
        assert response.status_code == 200

        task = response.json()
        assert task["status"] == "in_progress"
        assert task["title"] == sample_task["title"]  # Should remain unchanged

    def test_update_nonexistent_task(self, client):
        """Test that updating a non-existent task returns 404"""
        response = client.patch("/tasks/9999", json={"title": "Updated"})
        assert response.status_code == 404

    def test_delete_task(self, client, sample_task):
        """Test deleting a task"""
        # Create a task
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        # Delete the task
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]

        # Verify task is deleted
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_task(self, client):
        """Test that deleting a non-existent task returns 404"""
        response = client.delete("/tasks/9999")
        assert response.status_code == 404

    def test_filter_tasks_by_status(self, client, sample_tasks):
        """Test filtering tasks by status"""
        # Create multiple tasks
        for task_data in sample_tasks:
            client.post("/tasks", json=task_data)

        # Filter by pending status
        response = client.get("/tasks?status=pending")
        assert response.status_code == 200

        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["status"] == "pending"

    def test_filter_tasks_by_priority(self, client, sample_tasks):
        """Test filtering tasks by priority"""
        # Create multiple tasks
        for task_data in sample_tasks:
            client.post("/tasks", json=task_data)

        # Filter by high priority
        response = client.get("/tasks?priority=high")
        assert response.status_code == 200

        tasks = response.json()
        assert len(tasks) >= 1
        assert all(t["priority"] == "high" for t in tasks)

    def test_filter_tasks_by_status_and_priority(self, client, sample_tasks):
        """Test filtering tasks by both status and priority"""
        # Create multiple tasks
        for task_data in sample_tasks:
            client.post("/tasks", json=task_data)

        # Filter by status and priority
        response = client.get("/tasks?status=in_progress&priority=high")
        assert response.status_code == 200

        tasks = response.json()
        assert all(
            t["status"] == "in_progress" and t["priority"] == "high" for t in tasks
        )

    def test_get_statistics(self, client, sample_tasks):
        """Test getting task statistics"""
        # Create multiple tasks
        for task_data in sample_tasks:
            client.post("/tasks", json=task_data)

        response = client.get("/statistics")
        assert response.status_code == 200

        stats = response.json()
        assert "total_tasks" in stats
        assert "completed" in stats
        assert "pending" in stats
        assert "in_progress" in stats
        assert "completion_rate" in stats

        assert stats["total_tasks"] == 3
        assert stats["completed"] == 1
        assert stats["pending"] == 1
        assert stats["in_progress"] == 1

    def test_clear_all_tasks(self, client, sample_tasks):
        """Test clearing all tasks"""
        # Create multiple tasks
        for task_data in sample_tasks:
            client.post("/tasks", json=task_data)

        # Clear all tasks
        response = client.delete("/tasks")
        assert response.status_code == 200

        # Verify all tasks are deleted
        get_response = client.get("/tasks")
        assert get_response.status_code == 200
        assert get_response.json() == []


class TestTaskManager:
    """Test TaskManager class directly"""

    def test_task_manager_create_task(self, task_manager, sample_task):
        """Test TaskManager creates tasks correctly"""
        from backend.app.main import TaskCreate

        task_create = TaskCreate(**sample_task)
        task = task_manager.create_task(task_create)

        assert task.id == 1
        assert task.title == sample_task["title"]

    def test_task_manager_load_tasks(self, task_manager, sample_task):
        """Test TaskManager loads persisted tasks"""
        from backend.app.main import TaskCreate

        task_create = TaskCreate(**sample_task)
        task_manager.create_task(task_create)

        # Create new manager to load from file
        new_manager = task_manager.__class__(task_manager.file_path)
        tasks = new_manager.get_all_tasks()

        assert len(tasks) == 1
        assert tasks[0].title == sample_task["title"]

    def test_task_manager_update_task(self, task_manager, sample_task):
        """Test TaskManager updates tasks correctly"""
        from backend.app.main import TaskCreate, TaskUpdate

        task_create = TaskCreate(**sample_task)
        created_task = task_manager.create_task(task_create)

        update = TaskUpdate(title="Updated Title", status="completed")
        updated_task = task_manager.update_task(created_task.id, update)

        assert updated_task.title == "Updated Title"
        assert updated_task.status == "completed"

    def test_task_manager_delete_task(self, task_manager, sample_task):
        """Test TaskManager deletes tasks correctly"""
        from backend.app.main import TaskCreate

        task_create = TaskCreate(**sample_task)
        task = task_manager.create_task(task_create)

        result = task_manager.delete_task(task.id)
        assert "deleted" in result["message"]

        tasks = task_manager.get_all_tasks()
        assert len(tasks) == 0

    def test_task_manager_filter_tasks(self, task_manager, sample_tasks):
        """Test TaskManager filters tasks correctly"""
        from backend.app.main import TaskCreate

        for task_data in sample_tasks:
            task_create = TaskCreate(**task_data)
            task_manager.create_task(task_create)

        # Filter by status
        pending_tasks = task_manager.get_all_tasks(status="pending")
        assert all(t.status == "pending" for t in pending_tasks)

        # Filter by priority
        high_priority_tasks = task_manager.get_all_tasks(priority="high")
        assert all(t.priority == "high" for t in high_priority_tasks)

    def test_task_manager_statistics(self, task_manager, sample_tasks):
        """Test TaskManager calculates statistics correctly"""
        from backend.app.main import TaskCreate

        for task_data in sample_tasks:
            task_create = TaskCreate(**task_data)
            task_manager.create_task(task_create)

        stats = task_manager.get_statistics()
        assert stats["total_tasks"] == 3
        assert stats["completed"] == 1
        assert stats["pending"] == 1
        assert stats["in_progress"] == 1
        assert stats["completion_rate"] == (1 / 3) * 100


class TestTaskValidation:
    """Test task data validation"""

    def test_task_title_required(self, client):
        """Test that task title is required"""
        response = client.post("/tasks", json={"description": "No title"})
        assert response.status_code == 422

    def test_task_title_max_length(self, client):
        """Test that task title respects max length"""
        long_title = "a" * 201
        response = client.post("/tasks", json={"title": long_title})
        assert response.status_code == 422

    def test_task_description_max_length(self, client):
        """Test that description respects max length"""
        long_description = "a" * 1001
        response = client.post(
            "/tasks", json={"title": "Test", "description": long_description}
        )
        assert response.status_code == 422

    def test_task_priority_enum(self, client):
        """Test that priority validates enum values"""
        response = client.post("/tasks", json={"title": "Test", "priority": "invalid"})
        assert response.status_code == 422

    def test_task_status_enum(self, client):
        """Test that status validates enum values before lookup"""
        response = client.patch("/tasks/1", json={"status": "invalid"})
        # Validation error occurs before task lookup
        assert response.status_code == 422


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_create_task_with_empty_tags(self, client):
        """Test creating task with empty tags list"""
        task_data = {"title": "Task with tags", "tags": []}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        assert response.json()["tags"] == []

    def test_create_task_with_duplicate_tags(self, client):
        """Test creating task with duplicate tags"""
        task_data = {"title": "Task", "tags": ["urgent", "urgent", "test"]}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        # API accepts duplicates, frontend can handle deduplication

    def test_update_task_preserves_other_fields(self, client, sample_task):
        """Test that updating one field preserves others"""
        create_response = client.post("/tasks", json=sample_task)
        task_id = create_response.json()["id"]

        # Update only title
        client.patch(f"/tasks/{task_id}", json={"title": "New Title"})

        # Verify other fields unchanged
        response = client.get(f"/tasks/{task_id}")
        task = response.json()
        assert task["title"] == "New Title"
        assert task["description"] == sample_task["description"]
        assert task["priority"] == sample_task["priority"]

    def test_task_timestamps_update(self, client, sample_task):
        """Test that updated_at timestamp changes on update"""
        import time

        create_response = client.post("/tasks", json=sample_task)
        created_task = create_response.json()
        created_at = created_task["created_at"]
        updated_at_1 = created_task["updated_at"]

        # Initially created_at and updated_at should be the same (within the same second)
        assert (
            created_at[:19] == updated_at_1[:19]
        )  # Compare up to seconds, not microseconds

        # Wait a moment then update
        time.sleep(1)  # Wait 1 second to ensure clear difference
        client.patch(f"/tasks/{created_task['id']}", json={"title": "Updated"})

        response = client.get(f"/tasks/{created_task['id']}")
        updated_task = response.json()
        updated_at_2 = updated_task["updated_at"]

        # After update, updated_at should be different
        assert updated_at_2 != updated_at_1
