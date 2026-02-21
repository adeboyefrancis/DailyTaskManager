/**
 * Daily Task Manager - Frontend Application
 * Manages task creation, editing, deletion, and filtering
 */

const API_BASE_URL = 'http://localhost:8000';

class TaskManager {
    constructor() {
        this.tasks = [];
        this.currentFilter = 'all';
        this.currentSort = 'created';
        this.editingTaskId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadTasks();
    }

    // ========================================================================
    // Event Listeners
    // ========================================================================

    setupEventListeners() {
        // Add Task Button
        document.getElementById('addTaskBtn').addEventListener('click', () => this.openAddTask());

        // Task Input - Allow Enter key
        document.getElementById('taskTitle').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.openAddTask();
        });

        // Filter Buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.setFilter(e.target.dataset.filter));
        });

        // Sort Select
        document.getElementById('sortBy').addEventListener('change', (e) => {
            this.currentSort = e.target.value;
            this.renderTasks();
        });

        // Modal Events
        document.getElementById('saveEditBtn').addEventListener('click', () => this.saveEditTask());
        document.getElementById('cancelEditBtn').addEventListener('click', () => this.closeModal());
        document.querySelector('.modal-close').addEventListener('click', () => this.closeModal());
        document.getElementById('editModal').addEventListener('click', (e) => {
            if (e.target.id === 'editModal') this.closeModal();
        });
    }

    // ========================================================================
    // API Calls
    // ========================================================================

    async fetchAPI(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP Error: ${response.status}`);
            }

            return response.status !== 204 ? await response.json() : null;
        } catch (error) {
            console.error('API Error:', error);
            this.showNotification(`Error: ${error.message}`, 'error');
            throw error;
        }
    }

    async loadTasks() {
        try {
            this.tasks = await this.fetchAPI('/tasks');
            this.updateStatistics();
            this.renderTasks();
        } catch (error) {
            console.error('Failed to load tasks:', error);
        }
    }

    async createTask(taskData) {
        try {
            const newTask = await this.fetchAPI('/tasks', {
                method: 'POST',
                body: JSON.stringify(taskData),
            });
            this.tasks.push(newTask);
            this.updateStatistics();
            this.renderTasks();
            this.clearInputs();
            this.showNotification('Task created successfully! ✅', 'success');
        } catch (error) {
            console.error('Failed to create task:', error);
        }
    }

    async updateTask(taskId, updates) {
        try {
            const updatedTask = await this.fetchAPI(`/tasks/${taskId}`, {
                method: 'PATCH',
                body: JSON.stringify(updates),
            });
            const index = this.tasks.findIndex(t => t.id === taskId);
            if (index !== -1) {
                this.tasks[index] = updatedTask;
            }
            this.updateStatistics();
            this.renderTasks();
            this.showNotification('Task updated successfully! ✅', 'success');
        } catch (error) {
            console.error('Failed to update task:', error);
        }
    }

    async deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) return;

        try {
            await this.fetchAPI(`/tasks/${taskId}`, { method: 'DELETE' });
            this.tasks = this.tasks.filter(t => t.id !== taskId);
            this.updateStatistics();
            this.renderTasks();
            this.showNotification('Task deleted successfully! 🗑️', 'success');
        } catch (error) {
            console.error('Failed to delete task:', error);
        }
    }

    async getStatistics() {
        try {
            return await this.fetchAPI('/statistics');
        } catch (error) {
            console.error('Failed to get statistics:', error);
            return null;
        }
    }

    // ========================================================================
    // Task Management
    // ========================================================================

    openAddTask() {
        const title = document.getElementById('taskTitle').value.trim();
        if (!title) {
            this.showNotification('Please enter a task title', 'warning');
            return;
        }

        const taskData = {
            title,
            description: document.getElementById('taskDescription').value.trim() || null,
            priority: document.getElementById('taskPriority').value,
            due_date: document.getElementById('taskDueDate').value || null,
            tags: document.getElementById('taskTags').value
                .split(',')
                .map(tag => tag.trim())
                .filter(tag => tag),
        };

        this.createTask(taskData);
    }

    clearInputs() {
        document.getElementById('taskTitle').value = '';
        document.getElementById('taskDescription').value = '';
        document.getElementById('taskPriority').value = 'medium';
        document.getElementById('taskDueDate').value = '';
        document.getElementById('taskTags').value = '';
    }

    openEditModal(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;

        this.editingTaskId = taskId;

        document.getElementById('editTaskTitle').value = task.title;
        document.getElementById('editTaskDescription').value = task.description || '';
        document.getElementById('editTaskPriority').value = task.priority;
        document.getElementById('editTaskStatus').value = task.status;
        document.getElementById('editTaskDueDate').value = task.due_date || '';
        document.getElementById('editTaskTags').value = (task.tags || []).join(', ');

        document.getElementById('editModal').classList.remove('hidden');
    }

    saveEditTask() {
        const updates = {
            title: document.getElementById('editTaskTitle').value.trim(),
            description: document.getElementById('editTaskDescription').value.trim() || null,
            priority: document.getElementById('editTaskPriority').value,
            status: document.getElementById('editTaskStatus').value,
            due_date: document.getElementById('editTaskDueDate').value || null,
            tags: document.getElementById('editTaskTags').value
                .split(',')
                .map(tag => tag.trim())
                .filter(tag => tag),
        };

        if (!updates.title) {
            this.showNotification('Task title cannot be empty', 'warning');
            return;
        }

        this.updateTask(this.editingTaskId, updates);
        this.closeModal();
    }

    closeModal() {
        document.getElementById('editModal').classList.add('hidden');
        this.editingTaskId = null;
    }

    // ========================================================================
    // Filtering & Sorting
    // ========================================================================

    setFilter(filter) {
        this.currentFilter = filter;

        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });

        this.renderTasks();
    }

    getFilteredTasks() {
        let filtered = this.tasks;

        // Apply filter
        if (this.currentFilter !== 'all') {
            filtered = filtered.filter(t => t.status === this.currentFilter);
        }

        // Apply sort
        filtered = this.sortTasks(filtered);

        return filtered;
    }

    sortTasks(tasks) {
        const sorted = [...tasks];

        switch (this.currentSort) {
            case 'priority':
                return sorted.sort((a, b) => {
                    const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
                    return (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
                });
            case 'due_date':
                return sorted.sort((a, b) => {
                    if (!a.due_date) return 1;
                    if (!b.due_date) return -1;
                    return new Date(a.due_date) - new Date(b.due_date);
                });
            case 'created':
            default:
                return sorted.reverse();
        }
    }

    // ========================================================================
    // Rendering
    // ========================================================================

    renderTasks() {
        const tasksList = document.getElementById('tasksList');
        const filtered = this.getFilteredTasks();

        if (filtered.length === 0) {
            tasksList.innerHTML = '<div class="empty-state"><p>No tasks yet. Add one to get started! 🚀</p></div>';
            return;
        }

        tasksList.innerHTML = filtered.map(task => this.createTaskElement(task)).join('');

        // Attach event listeners to task elements
        document.querySelectorAll('.task-card').forEach(card => {
            const taskId = parseInt(card.dataset.taskId);
            const task = this.tasks.find(t => t.id === taskId);

            // Complete checkbox
            card.querySelector('.task-complete-checkbox').addEventListener('change', () => {
                const newStatus = task.status === 'completed' ? 'pending' : 'completed';
                this.updateTask(taskId, { status: newStatus });
            });

            // Edit button
            card.querySelector('.btn-edit').addEventListener('click', () => this.openEditModal(taskId));

            // Delete button
            card.querySelector('.btn-delete').addEventListener('click', () => this.deleteTask(taskId));
        });
    }

    createTaskElement(task) {
        const isCompleted = task.status === 'completed';
        const isOverdue = this.isOverdue(task.due_date) && !isCompleted;
        const dueDateDisplay = this.formatDueDate(task.due_date);

        const tagsHTML = task.tags && task.tags.length > 0
            ? task.tags.map(tag => `<span class="task-tag">#${tag}</span>`).join('')
            : '';

        return `
        <div class="task-card ${isCompleted ? 'completed' : ''}" data-task-id="${task.id}">
            <div class="task-header">
                <div class="task-checkbox">
                    <input type="checkbox" class="task-complete-checkbox" ${isCompleted ? 'checked' : ''}>
                </div>
                <div class="task-info">
                    <h3 class="task-title">${this.escapeHtml(task.title)}</h3>
                    ${task.description ? `<p class="task-description">${this.escapeHtml(task.description)}</p>` : ''}
                </div>
                <div class="task-meta">
                    <span class="task-priority ${task.priority}">${this.capitalizeFirst(task.priority)}</span>
                </div>
            </div>
            <div class="task-footer">
                <div class="task-tags">${tagsHTML}</div>
                <div class="task-due-date ${isOverdue ? 'overdue' : ''}">${dueDateDisplay}</div>
                <div class="task-actions">
                    <button class="btn-icon btn-edit" title="Edit task">✏️</button>
                    <button class="btn-icon btn-delete" title="Delete task">🗑️</button>
                </div>
            </div>
        </div>
        `;
    }

    async updateStatistics() {
        try {
            const stats = await this.getStatistics();
            if (stats) {
                document.getElementById('statTotal').textContent = stats.total_tasks;
                document.getElementById('statCompleted').textContent = stats.completed;
                document.getElementById('statPending').textContent = stats.pending;
            }
        } catch (error) {
            console.error('Failed to update statistics:', error);
        }
    }

    // ========================================================================
    // Utilities
    // ========================================================================

    isOverdue(dueDate) {
        if (!dueDate) return false;
        return new Date(dueDate) < new Date();
    }

    formatDueDate(dueDate) {
        if (!dueDate) return '';

        const date = new Date(dueDate);
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        const dateStr = date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });

        if (date.toDateString() === today.toDateString()) {
            return `📅 Today`;
        } else if (date.toDateString() === tomorrow.toDateString()) {
            return `📅 Tomorrow`;
        } else if (this.isOverdue(dueDate)) {
            return `⚠️ Overdue: ${dateStr}`;
        } else {
            return `📅 ${dateStr}`;
        }
    }

    showNotification(message, type = 'info') {
        // Simple notification (can be enhanced with toast library)
        console.log(`[${type.toUpperCase()}] ${message}`);
        // You can replace this with a toast notification library
        alert(message);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TaskManager();
});
