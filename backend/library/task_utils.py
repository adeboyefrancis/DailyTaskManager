"""Utility functions for task management"""

from datetime import datetime
from typing import List, Dict


def parse_due_date(date_str: str) -> datetime:
    """Parse due date string to datetime object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD") from exc


def is_overdue(due_date_str: str) -> bool:
    """Check if task is overdue (past due date)"""
    if not due_date_str:
        return False
    due_date = parse_due_date(due_date_str).date()
    today = datetime.now().date()
    return due_date < today


def days_until_due(due_date_str: str) -> int:
    """Calculate days until due date (0 = today, positive = future, negative = past)"""
    if not due_date_str:
        return None
    due_date = parse_due_date(due_date_str).date()
    today = datetime.now().date()
    delta = (due_date - today).days
    return delta


def get_priority_score(priority: str) -> int:
    """Convert priority to numeric score for sorting"""
    priority_map = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
    return priority_map.get(priority.lower(), 0)


def sort_tasks_by_priority(tasks: List[Dict]) -> List[Dict]:
    """Sort tasks by priority (urgent to low)"""
    return sorted(
        tasks,
        key=lambda x: get_priority_score(x.get("priority", "medium")),
        reverse=True,
    )


def sort_tasks_by_due_date(tasks: List[Dict]) -> List[Dict]:
    """Sort tasks by due date (earliest first)"""

    def due_date_key(task):
        if task.get("due_date"):
            try:
                return parse_due_date(task["due_date"])
            except ValueError:
                return datetime.max
        return datetime.max

    return sorted(tasks, key=due_date_key)


def get_tasks_by_tag(tasks: List[Dict], tag: str) -> List[Dict]:
    """Filter tasks by tag"""
    return [t for t in tasks if tag.lower() in [tg.lower() for tg in t.get("tags", [])]]


def get_overdue_tasks(tasks: List[Dict]) -> List[Dict]:
    """Get all overdue tasks"""
    overdue = []
    for task in tasks:
        if task.get("due_date") and task.get("status") != "completed":
            try:
                if is_overdue(task["due_date"]):
                    overdue.append(task)
            except ValueError:
                pass
    return overdue


def calculate_completion_percentage(tasks: List[Dict]) -> float:
    """Calculate task completion percentage"""
    if not tasks:
        return 0.0
    completed = len([t for t in tasks if t.get("status") == "completed"])
    return (completed / len(tasks)) * 100


def get_daily_summary(tasks: List[Dict]) -> Dict:
    """Generate a daily summary of tasks"""
    today = datetime.now().date()

    today_tasks = []
    for task in tasks:
        if task.get("due_date"):
            try:
                due_date = parse_due_date(task["due_date"]).date()
                if due_date == today:
                    today_tasks.append(task)
            except ValueError:
                pass

    return {
        "date": str(today),
        "total_today": len(today_tasks),
        "completed_today": len(
            [t for t in today_tasks if t.get("status") == "completed"]
        ),
        "pending_today": len([t for t in today_tasks if t.get("status") == "pending"]),
        "in_progress_today": len(
            [t for t in today_tasks if t.get("status") == "in_progress"]
        ),
        "tasks": today_tasks,
    }
