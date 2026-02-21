"""
Unit tests for task utility functions
"""

import pytest
from datetime import datetime, timedelta
from backend.library.task_utils import (
    parse_due_date,
    is_overdue,
    days_until_due,
    get_priority_score,
    sort_tasks_by_priority,
    sort_tasks_by_due_date,
    get_tasks_by_tag,
    get_overdue_tasks,
    calculate_completion_percentage,
    get_daily_summary,
)


class TestDateUtilities:
    """Test date parsing and validation utilities"""

    def test_parse_due_date_valid(self):
        """Test parsing valid date string"""
        date = parse_due_date("2026-02-28")
        assert date.year == 2026
        assert date.month == 2
        assert date.day == 28

    def test_parse_due_date_invalid_format(self):
        """Test that invalid format raises error"""
        with pytest.raises(ValueError):
            parse_due_date("02/28/2026")

    def test_parse_due_date_invalid_date(self):
        """Test that invalid date raises error"""
        with pytest.raises(ValueError):
            parse_due_date("2026-13-45")

    def test_is_overdue_past_date(self):
        """Test that past dates are detected as overdue"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        assert is_overdue(yesterday) is True

    def test_is_overdue_future_date(self):
        """Test that future dates are not overdue"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert is_overdue(tomorrow) is False

    def test_is_overdue_today(self):
        """Test that today's date is not overdue"""
        today = datetime.now().strftime("%Y-%m-%d")
        assert is_overdue(today) is False

    def test_is_overdue_none(self):
        """Test that None date is not overdue"""
        assert is_overdue(None) is False

    def test_is_overdue_empty_string(self):
        """Test that empty string returns False"""
        assert is_overdue("") is False

    def test_days_until_due_future(self):
        """Test calculating days until future date"""
        future_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        days = days_until_due(future_date)
        assert days == 5

    def test_days_until_due_past(self):
        """Test calculating days for past date (negative)"""
        past_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        days = days_until_due(past_date)
        assert days == -3

    def test_days_until_due_none(self):
        """Test that None returns None"""
        assert days_until_due(None) is None

    def test_days_until_due_today(self):
        """Test calculating days for today (should be 0)"""
        today = datetime.now().strftime("%Y-%m-%d")
        days = days_until_due(today)
        assert days == 0


class TestPriorityUtilities:
    """Test priority-related utilities"""

    def test_get_priority_score_urgent(self):
        """Test priority score for urgent"""
        assert get_priority_score("urgent") == 4

    def test_get_priority_score_high(self):
        """Test priority score for high"""
        assert get_priority_score("high") == 3

    def test_get_priority_score_medium(self):
        """Test priority score for medium"""
        assert get_priority_score("medium") == 2

    def test_get_priority_score_low(self):
        """Test priority score for low"""
        assert get_priority_score("low") == 1

    def test_get_priority_score_invalid(self):
        """Test invalid priority returns 0"""
        assert get_priority_score("invalid") == 0

    def test_get_priority_score_case_insensitive(self):
        """Test priority scoring is case-insensitive"""
        assert get_priority_score("URGENT") == 4
        assert get_priority_score("High") == 3

    def test_sort_tasks_by_priority(self):
        """Test sorting tasks by priority"""
        tasks = [
            {"title": "Low", "priority": "low"},
            {"title": "Urgent", "priority": "urgent"},
            {"title": "Medium", "priority": "medium"},
            {"title": "High", "priority": "high"},
        ]

        sorted_tasks = sort_tasks_by_priority(tasks)

        assert sorted_tasks[0]["priority"] == "urgent"
        assert sorted_tasks[1]["priority"] == "high"
        assert sorted_tasks[2]["priority"] == "medium"
        assert sorted_tasks[3]["priority"] == "low"

    def test_sort_tasks_by_priority_missing(self):
        """Test sorting when priority is missing (defaults to medium)"""
        tasks = [
            {"title": "No priority"},
            {"title": "Urgent", "priority": "urgent"},
        ]

        sorted_tasks = sort_tasks_by_priority(tasks)
        assert sorted_tasks[0]["priority"] == "urgent"


class TestSortingUtilities:
    """Test task sorting functionality"""

    def test_sort_tasks_by_due_date(self):
        """Test sorting tasks by due date"""
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        tasks = [
            {"title": "Next week", "due_date": next_week},
            {"title": "Today", "due_date": today},
            {"title": "Tomorrow", "due_date": tomorrow},
        ]

        sorted_tasks = sort_tasks_by_due_date(tasks)

        assert sorted_tasks[0]["title"] == "Today"
        assert sorted_tasks[1]["title"] == "Tomorrow"
        assert sorted_tasks[2]["title"] == "Next week"

    def test_sort_tasks_by_due_date_no_date(self):
        """Test that tasks without due date go to end"""
        today = datetime.now().strftime("%Y-%m-%d")

        tasks = [
            {"title": "No date"},
            {"title": "Today", "due_date": today},
        ]

        sorted_tasks = sort_tasks_by_due_date(tasks)

        assert sorted_tasks[0]["title"] == "Today"
        assert sorted_tasks[1]["title"] == "No date"

    def test_sort_tasks_by_due_date_invalid_format(self):
        """Test sorting with invalid date format"""
        today = datetime.now().strftime("%Y-%m-%d")

        tasks = [
            {"title": "Invalid", "due_date": "invalid-date"},
            {"title": "Today", "due_date": today},
        ]

        sorted_tasks = sort_tasks_by_due_date(tasks)

        # Invalid date should go to end
        assert sorted_tasks[0]["title"] == "Today"
        assert sorted_tasks[1]["title"] == "Invalid"


class TestFilteringUtilities:
    """Test task filtering functionality"""

    def test_get_tasks_by_tag(self):
        """Test filtering tasks by tag"""
        tasks = [
            {"title": "Task 1", "tags": ["urgent", "work"]},
            {"title": "Task 2", "tags": ["personal"]},
            {"title": "Task 3", "tags": ["urgent", "home"]},
        ]

        urgent_tasks = get_tasks_by_tag(tasks, "urgent")

        assert len(urgent_tasks) == 2
        assert all("urgent" in t["tags"] for t in urgent_tasks)

    def test_get_tasks_by_tag_case_insensitive(self):
        """Test tag filtering is case-insensitive"""
        tasks = [
            {"title": "Task 1", "tags": ["Urgent"]},
            {"title": "Task 2", "tags": ["personal"]},
        ]

        urgent_tasks = get_tasks_by_tag(tasks, "URGENT")

        assert len(urgent_tasks) == 1

    def test_get_tasks_by_tag_no_matches(self):
        """Test tag filtering with no matches"""
        tasks = [
            {"title": "Task 1", "tags": ["work"]},
        ]

        results = get_tasks_by_tag(tasks, "personal")

        assert len(results) == 0

    def test_get_tasks_by_tag_empty_tags(self):
        """Test filtering tasks with empty tags list"""
        tasks = [
            {"title": "Task 1", "tags": []},
            {"title": "Task 2", "tags": ["work"]},
        ]

        results = get_tasks_by_tag(tasks, "work")

        assert len(results) == 1

    def test_get_overdue_tasks(self):
        """Test getting overdue tasks"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        tasks = [
            {"title": "Overdue", "due_date": yesterday, "status": "pending"},
            {"title": "Future", "due_date": tomorrow, "status": "pending"},
            {
                "title": "Completed overdue",
                "due_date": yesterday,
                "status": "completed",
            },
        ]

        overdue = get_overdue_tasks(tasks)

        assert len(overdue) == 1
        assert overdue[0]["title"] == "Overdue"

    def test_get_overdue_tasks_skips_completed(self):
        """Test that completed tasks are not included in overdue"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        tasks = [
            {"title": "Completed", "due_date": yesterday, "status": "completed"},
        ]

        overdue = get_overdue_tasks(tasks)

        assert len(overdue) == 0

    def test_get_overdue_tasks_no_date(self):
        """Test that tasks without due date are ignored"""
        tasks = [
            {"title": "No date", "status": "pending"},
        ]

        overdue = get_overdue_tasks(tasks)

        assert len(overdue) == 0


class TestStatisticsUtilities:
    """Test statistics calculation utilities"""

    def test_calculate_completion_percentage_all_completed(self):
        """Test completion percentage when all are completed"""
        tasks = [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "completed"},
        ]

        percentage = calculate_completion_percentage(tasks)

        assert percentage == 100.0

    def test_calculate_completion_percentage_none_completed(self):
        """Test completion percentage when none are completed"""
        tasks = [
            {"status": "pending"},
            {"status": "pending"},
            {"status": "in_progress"},
        ]

        percentage = calculate_completion_percentage(tasks)

        assert percentage == 0.0

    def test_calculate_completion_percentage_partial(self):
        """Test completion percentage with partial completion"""
        tasks = [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "pending"},
            {"status": "in_progress"},
        ]

        percentage = calculate_completion_percentage(tasks)

        assert percentage == 50.0

    def test_calculate_completion_percentage_empty(self):
        """Test completion percentage with empty list"""
        tasks = []

        percentage = calculate_completion_percentage(tasks)

        assert percentage == 0.0

    def test_get_daily_summary(self):
        """Test generating daily summary"""
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        tasks = [
            {"title": "Today 1", "due_date": today, "status": "pending"},
            {"title": "Today 2", "due_date": today, "status": "completed"},
            {"title": "Tomorrow", "due_date": tomorrow, "status": "pending"},
        ]

        summary = get_daily_summary(tasks)

        assert summary["total_today"] == 2
        assert summary["completed_today"] == 1
        assert summary["pending_today"] == 1
        assert summary["in_progress_today"] == 0
        assert summary["date"] == today

    def test_get_daily_summary_no_tasks_today(self):
        """Test daily summary with no tasks today"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        tasks = [
            {"title": "Tomorrow", "due_date": tomorrow, "status": "pending"},
        ]

        summary = get_daily_summary(tasks)

        assert summary["total_today"] == 0
        assert summary["completed_today"] == 0
        assert summary["pending_today"] == 0
