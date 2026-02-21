"""
Pytest configuration and fixtures for Daily Task Manager tests
"""

import pytest
import json
import os
from fastapi.testclient import TestClient
from backend.app.main import app, TaskManager


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    app_client = TestClient(app)
    # Clear all tasks before each test
    app_client.delete("/tasks")
    yield app_client
    # Cleanup after test
    app_client.delete("/tasks")


@pytest.fixture
def test_db_file(tmp_path):
    """Create a temporary database file for testing"""
    db_file = tmp_path / "test_tasks.json"
    return str(db_file)


@pytest.fixture
def task_manager(test_db_file):
    """Create a TaskManager instance with a test database"""
    manager = TaskManager(test_db_file)
    yield manager
    # Cleanup after test
    if os.path.exists(test_db_file):
        os.remove(test_db_file)


@pytest.fixture
def sample_task():
    """Create a sample task for testing"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "medium",
        "status": "pending",
        "due_date": "2026-02-28",
        "tags": ["test", "urgent"],
    }


@pytest.fixture
def sample_tasks():
    """Create multiple sample tasks for testing"""
    return [
        {
            "title": "Task 1",
            "description": "First task",
            "priority": "low",
            "status": "pending",
            "due_date": "2026-03-01",
            "tags": ["task1"],
        },
        {
            "title": "Task 2",
            "description": "Second task",
            "priority": "high",
            "status": "in_progress",
            "due_date": "2026-02-25",
            "tags": ["task2", "urgent"],
        },
        {
            "title": "Task 3",
            "description": "Third task",
            "priority": "urgent",
            "status": "completed",
            "due_date": "2026-02-20",
            "tags": ["task3"],
        },
    ]
