<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Todo App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .filters {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .input-section {
            display: grid;
            grid-template-columns: 1fr auto auto auto;
            gap: 10px;
            margin-bottom: 20px;
        }

        input, select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }

        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .todo-item {
            display: grid;
            grid-template-columns: auto 1fr auto auto auto auto;
            align-items: center;
            padding: 10px;
            margin-bottom: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
            gap: 10px;
        }

        .priority-high { border-left: 4px solid #ff4444; }
        .priority-medium { border-left: 4px solid #ffbb33; }
        .priority-low { border-left: 4px solid #00C851; }

        .completed { background-color: #e0e0e0; text-decoration: line-through; }

        .tag {
            padding: 2px 8px;
            background-color: #e0e0e0;
            border-radius: 12px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Enhanced Todo App</h1>
        
        <!-- Filters -->
        <div class="filters">
            <select id="filter-priority">
                <option value="all">All Priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
            <select id="filter-category">
                <option value="all">All Categories</option>
                <option value="work">Work</option>
                <option value="personal">Personal</option>
                <option value="shopping">Shopping</option>
            </select>
            <select id="sort-by">
                <option value="date">Sort by Date</option>
                <option value="priority">Sort by Priority</option>
                <option value="name">Sort by Name</option>
            </select>
        </div>

        <!-- Input Section -->
        <div class="input-section">
            <input type="text" id="todo-input" placeholder="Enter a new task">
            <input type="date" id="todo-date">
            <select id="todo-priority">
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
            <select id="todo-category">
                <option value="work">Work</option>
                <option value="personal">Personal</option>
                <option value="shopping">Shopping</option>
            </select>
            <button onclick="addTodo()">Add Todo</button>
        </div>

        <!-- Todo List -->
        <div id="todo-list"></div>
    </div>

    <script>
        let todos = [];

        // Load todos from localStorage
        document.addEventListener('DOMContentLoaded', () => {
            const savedTodos = localStorage.getItem('todos');
            if (savedTodos) {
                todos = JSON.parse(savedTodos);
                renderTodos();
            }
        });

        // Add event listeners for filters
        document.getElementById('filter-priority').addEventListener('change', renderTodos);
        document.getElementById('filter-category').addEventListener('change', renderTodos);
        document.getElementById('sort-by').addEventListener('change', renderTodos);

        function addTodo() {
            const text = document.getElementById('todo-input').value.trim();
            const date = document.getElementById('todo-date').value;
            const priority = document.getElementById('todo-priority').value;
            const category = document.getElementById('todo-category').value;

            if (text) {
                const todo = {
                    id: Date.now(),
                    text: text,
                    completed: false,
                    date: date,
                    priority: priority,
                    category: category,
                    createdAt: new Date().toISOString()
                };

                todos.push(todo);
                saveTodos();
                renderTodos();
                clearInputs();
            }
        }

        function clearInputs() {
            document.getElementById('todo-input').value = '';
            document.getElementById('todo-date').value = '';
            document.getElementById('todo-priority').value = 'high';
            document.getElementById('todo-category').value = 'work';
        }

        function deleteTodo(id) {
            todos = todos.filter(todo => todo.id !== id);
            saveTodos();
            renderTodos();
        }

        function toggleTodo(id) {
            todos = todos.map(todo => 
                todo.id === id ? {...todo, completed: !todo.completed} : todo
            );
            saveTodos();
            renderTodos();
        }

        function editTodo(id) {
            const todo = todos.find(t => t.id === id);
            const newText = prompt('Edit todo:', todo.text);
            
            if (newText !== null && newText.trim() !== '') {
                todos = todos.map(t => 
                    t.id === id ? {...t, text: newText.trim()} : t
                );
                saveTodos();
                renderTodos();
            }
        }

        function saveTodos() {
            localStorage.setItem('todos', JSON.stringify(todos));
        }

        function renderTodos() {
            let filteredTodos = [...todos];
            
            // Apply filters
            const priorityFilter = document.getElementById('filter-priority').value;
            const categoryFilter = document.getElementById('filter-category').value;
            const sortBy = document.getElementById('sort-by').value;

            if (priorityFilter !== 'all') {
                filteredTodos = filteredTodos.filter(todo => todo.priority === priorityFilter);
            }

            if (categoryFilter !== 'all') {
                filteredTodos = filteredTodos.filter(todo => todo.category === categoryFilter);
            }

            // Apply sorting
            switch(sortBy) {
                case 'date':
                    filteredTodos.sort((a, b) => new Date(a.date) - new Date(b.date));
                    break;
                case 'priority':
                    const priorityOrder = { high: 1, medium: 2, low: 3 };
                    filteredTodos.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
                    break;
                case 'name':
                    filteredTodos.sort((a, b) => a.text.localeCompare(b.text));
                    break;
            }

            const todoList = document.getElementById('todo-list');
            todoList.innerHTML = '';

            filteredTodos.forEach(todo => {
                const todoElement = document.createElement('div');
                todoElement.className = `todo-item priority-${todo.priority} ${todo.completed ? 'completed' : ''}`;

                todoElement.innerHTML = `
                    <input type="checkbox" 
                           ${todo.completed ? 'checked' : ''} 
                           onchange="toggleTodo(${todo.id})">
                    <span class="todo-text">${todo.text}</span>
                    <span class="tag">${todo.category}</span>
                    <span class="date">${formatDate(todo.date)}</span>
                    <button onclick="editTodo(${todo.id})" class="edit-btn">Edit</button>
                    <button onclick="deleteTodo(${todo.id})" class="delete-btn">Delete</button>
                `;

                todoList.appendChild(todoElement);
            });

            // Show total count
            const totalCount = document.createElement('div');
            totalCount.className = 'todo-count';
            totalCount.textContent = `Total: ${filteredTodos.length} todos`;
            todoList.appendChild(totalCount);
        }

        function formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString();
        }

        // Add keyboard shortcut for adding todos
        document.getElementById('todo-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                addTodo();
            }
        });

        // Add drag and drop functionality
        let draggedItem = null;

        document.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('todo-item')) {
                draggedItem = e.target;
                e.target.style.opacity = '0.5';
            }
        });

        document.addEventListener('dragend', (e) => {
            if (e.target.classList.contains('todo-item')) {
                e.target.style.opacity = '1';
            }
        });

        document.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
            if (draggedItem) {
                const todoList = document.getElementById('todo-list');
                const afterElement = getDragAfterElement(todoList, e.clientY);
                if (afterElement) {
                    todoList.insertBefore(draggedItem, afterElement);
                } else {
                    todoList.appendChild(draggedItem);
                }
                draggedItem = null;
            }
        });

        function getDragAfterElement(container, y) {
            const draggableElements = [...container.querySelectorAll('.todo-item:not(.dragging)')];
            
            return draggableElements.reduce((closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;
                if (offset < 0 && offset > closest.offset) {
                    return { offset: offset, element: child };
                } else {
                    return closest;
                }
            }, { offset: Number.NEGATIVE_INFINITY }).element;
        }

        // Add some sample todos if the list is empty
        if (todos.length === 0) {
            todos = [
                {
                    id: 1,
                    text: 'Welcome to Enhanced Todo App',
                    completed: false,
                    date: new Date().toISOString().split('T')[0],
                    priority: 'high',
                    category: 'work',
                    createdAt: new Date().toISOString()
                }
            ];
            saveTodos();
            renderTodos();
        }
    </script>

    <!-- Add these additional styles to the head section -->
    <style>
        /* Additional Styles */
        .todo-count {
            margin-top: 20px;
            text-align: right;
            color: #666;
            font-size: 14px;
        }

        .edit-btn {
            background-color: #2196F3;
        }

        .edit-btn:hover {
            background-color: #0b7dda;
        }

        .delete-btn {
            background-color: #f44336;
        }

        .delete-btn:hover {
            background-color: #da190b;
        }

        .date {
            color: #666;
            font-size: 14px;
        }

        .todo-item {
            transition: all 0.3s ease;
            cursor: move;
        }

        .todo-item:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Category Tags */
        .tag.work { background-color: #2196F3; color: white; }
        .tag.personal { background-color: #4CAF50; color: white; }
        .tag.shopping { background-color: #ff9800; color: white; }

        /* Responsive Design */
        @media (max-width: 768px) {
            .input-section {
                grid-template-columns: 1fr;
            }

            .todo-item {
                grid-template-columns: auto 1fr;
                grid-gap: 5px;
            }

            .filters {
                flex-direction: column;
            }

            button {
                width: 100%;
            }
        }

        /* Animation */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .todo-item {
            animation: slideIn 0.3s ease;
        }
    </style>

    <!-- Add this modal for editing todos -->
    <div id="edit-modal" class="modal" style="display: none;">
        <div class="modal-content">
            <h2>Edit Todo</h2>
            <input type="text" id="edit-input">
            <input type="date" id="edit-date">
            <select id="edit-priority">
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
            <select id="edit-category">
                <option value="work">Work</option>
                <option value="personal">Personal</option>
                <option value="shopping">Shopping</option>
            </select>
            <div class="modal-buttons">
                <button onclick="saveEdit()">Save</button>
                <button onclick="closeModal()">Cancel</button>
            </div>
        </div>
    </div>

    <style>
        /* Modal Styles */
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 500px;
        }

        .modal-buttons {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 20px;
        }
    </style>

    <script>
        // Modal functionality
        let currentEditId = null;

        function openModal(id) {
            currentEditId = id;
            const todo = todos.find(t => t.id === id);
            const modal = document.getElementById('edit-modal');
            
            document.getElementById('edit-input').value = todo.text;
            document.getElementById('edit-date').value = todo.date;
            document.getElementById('edit-priority').value = todo.priority;
            document.getElementById('edit-category').value = todo.category;
            
            modal.style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('edit-modal').style.display = 'none';
            currentEditId = null;
        }

        function saveEdit() {
            if (currentEditId) {
                const text = document.getElementById('edit-input').value.trim();
                const date = document.getElementById('edit-date').value;
                const priority = document.getElementById('edit-priority').value;
                const category = document.getElementById('edit-category').value;

                if (text) {
                    todos = todos.map(todo => {
                        if (todo.id === currentEditId) {
                            return {
                                ...todo,
                                text,
                                date,
                                priority,
                                category,
                                lastModified: new Date().toISOString()
                            };
                        }
                        return todo;
                    });

                    saveTodos();
                    renderTodos();
                    closeModal();
                }
            }
        }

        // Add search functionality
        function searchTodos(query) {
            const searchTerm = query.toLowerCase();
            return todos.filter(todo => 
                todo.text.toLowerCase().includes(searchTerm) ||
                todo.category.toLowerCase().includes(searchTerm)
            );
        }

        // Add statistics
        function getTodoStats() {
            const stats = {
                total: todos.length,
                completed: todos.filter(todo => todo.completed).length,
                high: todos.filter(todo => todo.priority === 'high').length,
                medium: todos.filter(todo => todo.priority === 'medium').length,
                low: todos.filter(todo => todo.priority === 'low').length,
                categories: {}
            };

            todos.forEach(todo => {
                stats.categories[todo.category] = (stats.categories[todo.category] || 0) + 1;
            });

            return stats;
        }

        // Add export functionality
        function exportTodos() {
            const dataStr = JSON.stringify(todos, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            
            const exportFileDefaultName = 'todos.json';
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
        }

        // Add import functionality
        function importTodos(event) {
            const file = event.target.files[0];
            const reader = new FileReader();
            
            reader.onload = function(e) {
                try {
                    const importedTodos = JSON.parse(e.target.result);
                    todos = [...todos, ...importedTodos];
                    saveTodos();
                    renderTodos();
                    alert('Todos imported successfully!');
                } catch (error) {
                    alert('Error importing todos. Please check the file format.');
                }
            };
            
            reader.readAsText(file);
        }

        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                exportTodos();
            }
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                document.getElementById('todo-input').focus();
            }
        });

        // Add notification for due dates
        function checkDueDates() {
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);

            todos.forEach(todo => {
                if (!todo.completed && todo.date) {
                    const dueDate = new Date(todo.date);
                    if (dueDate <= tomorrow) {
                        notifyUser(todo);
                    }
                }
            });
        }

        function notifyUser(todo) {
            if ("Notification" in window && Notification.permission === "granted") {
                new Notification("Todo Reminder", {
                    body: `Task "${todo.text}" is due ${todo.date}`,
                    icon: "path-to-your-icon.png"
                });
            } else if (Notification.permission !== "denied") {
                Notification.requestPermission().then(permission => {
                    if (permission === "granted") {
                        notifyUser(todo);
                    }
                });
            }
        }

        // Add local storage backup
        function backupTodos() {
            const backup = {
                todos: todos,
                timestamp: new Date().toISOString()
            };
            localStorage.setItem('todosBackup', JSON.stringify(backup));
        }

        function restoreFromBackup() {
            const backup = localStorage.getItem('todosBackup');
            if (backup) {
                const { todos: backupTodos, timestamp } = JSON.parse(backup);
                if (confirm(`Restore todos from backup created on ${new Date(timestamp).toLocaleString()}?`)) {
                    todos = backupTodos;
                    saveTodos();
                    renderTodos();
                }
            }
        }

        // Add data validation
        function validateTodo(todo) {
            const errors = [];

            if (!todo.text || todo.text.trim().length === 0) {
                errors.push('Todo text is required');
            }

            if (todo.text.length > 200) {
                errors.push('Todo text must be less than 200 characters');
            }

            if (todo.date && isNaN(new Date(todo.date).getTime())) {
                errors.push('Invalid date format');
            }

            if (!['high', 'medium', 'low'].includes(todo.priority)) {
                errors.push('Invalid priority level');
            }

            if (!['work', 'personal', 'shopping'].includes(todo.category)) {
                errors.push('Invalid category');
            }

            return errors;
        }

        // Add these buttons to the HTML
        document.querySelector('.container').insertAdjacentHTML('beforeend', `
            <div class="action-buttons">
                <button onclick="exportTodos()">Export Todos</button>
                <input type="file" id="import-file" style="display: none" onchange="importTodos(event)">
                <button onclick="document.getElementById('import-file').click()">Import Todos</button>
                <button onclick="backupTodos()">Backup</button>
                <button onclick="restoreFromBackup()">Restore</button>
            </div>
            <div class="stats-container"></div>
        `);

        // Initialize the app
        function initApp() {
            // Request notification permission
            if ("Notification" in window) {
                Notification.requestPermission();
            }

            // Check for due dates every minute
            setInterval(checkDueDates, 60000);

            // Auto backup every 5 minutes
            setInterval(backupTodos, 300000);

            // Update stats
            updateStats();
        }

        function updateStats() {
            const stats = getTodoStats();
            const statsContainer = document.querySelector('.stats-container');
            statsContainer.innerHTML = `
                <h3>Statistics</h3>
                <p>Total: ${stats.total}</p>
                <p>Completed: ${stats.completed}</p>
                <p>Priority: High (${stats.high}), Medium (${stats.medium}), Low (${stats.low})</p>
                <p>Categories: ${Object.entries(stats.categories)
                    .map(([category, count]) => `${category} (${count})`)
                    .join(', ')}
                </p>
            `;
        }

        // Add progress tracking
        function updateProgress() {
            const total = todos.length;
            const completed = todos.filter(todo => todo.completed).length;
            const percentage = total === 0 ? 0 : Math.round((completed / total) * 100);

            const progressBar = document.createElement('div');
            progressBar.className = 'progress-bar';
            progressBar.innerHTML = `
                <div class="progress" style="width: ${percentage}%"></div>
                <span>${percentage}% Complete</span>
            `;

            const existingProgress = document.querySelector('.progress-bar');
            if (existingProgress) {
                existingProgress.replaceWith(progressBar);
            } else {
                document.querySelector('.container').insertBefore(
                    progressBar,
                    document.querySelector('.todo-list')
                );
            }
        }

        // Add these additional styles
        const additionalStyles = `
            <style>
                .progress-bar {
                    width: 100%;
                    height: 20px;
                    background-color: #f0f0f0;
                    border-radius: 10px;
                    margin: 20px 0;
                    position: relative;
                    overflow: hidden;
                }

                .progress {
                    height: 100%;
                    background-color: #4CAF50;
                    transition: width 0.3s ease;
                }

                .progress-bar span {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    color: #333;
                    font-size: 12px;
                }

                .stats-container {
                    margin-top: 20px;
                    padding: 15px;
                    background-color: #f9f9f9;
                    border-radius: 8px;
                }

                .action-buttons {
                    display: flex;
                    gap: 10px;
                    margin: 20px 0;
                    flex-wrap: wrap;
                }

                .action-buttons button {
                    flex: 1;
                    min-width: 120px;
                }

                @media print {
                    .input-section,
                    .filters,
                    .action-buttons {
                        display: none;
                    }
                }

                .todo-item.dragging {
                    opacity: 0.5;
                    background-color: #e9e9e9;
                }

                .todo-item .actions {
                    display: flex;
                    gap: 5px;
                }

                .todo-item .due-date {
                    font-size: 12px;
                    color: #666;
                }

                .todo-item .overdue {
                    color: #f44336;
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', additionalStyles);

        // Override the original renderTodos function to include the new features
        const originalRenderTodos = renderTodos;
        renderTodos = function() {
            originalRenderTodos();
            updateProgress();
            updateStats();
        };

        // Add keyboard shortcuts help
        function showKeyboardShortcuts() {
            alert(`
                Keyboard Shortcuts:
                Ctrl + S: Export todos
                Ctrl + F: Focus search
                Ctrl + N: New todo
                Esc: Close modal
            `);
        }

        // Initialize the app
        document.addEventListener('DOMContentLoaded', () => {
            initApp();
            
            // Add help button
            document.querySelector('.container').insertAdjacentHTML('afterbegin', `
                <button onclick="showKeyboardShortcuts()" class="help-btn">
                    Keyboard Shortcuts
                </button>
            `);

            // Add search functionality
            document.querySelector('.filters').insertAdjacentHTML('afterbegin', `
                <input type="text" 
                       id="search-input" 
                       placeholder="Search todos..." 
                       class="search-input">
            `);

            // Add search event listener
            document.getElementById('search-input').addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                const filteredTodos = todos.filter(todo => 
                    todo.text.toLowerCase().includes(searchTerm) ||
                    todo.category.toLowerCase().includes(searchTerm)
                );
                renderFilteredTodos(filteredTodos);
            });
        });

        function renderFilteredTodos(filteredTodos) {
            const todoList = document.getElementById('todo-list');
            todoList.innerHTML = '';

            if (filteredTodos.length === 0) {
                todoList.innerHTML = `
                    <div class="no-results">
                        No todos found matching your search.
                    </div>
                `;
                return;
            }

            filteredTodos.forEach(todo => {
                const todoElement = createTodoElement(todo);
                todoList.appendChild(todoElement);
            });
        }

        function createTodoElement(todo) {
            const todoElement = document.createElement('div');
            todoElement.className = `todo-item priority-${todo.priority} ${todo.completed ? 'completed' : ''}`;
            todoElement.draggable = true;

            const dueDate = new Date(todo.date);
            const isOverdue = !todo.completed && dueDate < new Date();

            todoElement.innerHTML = `
                <input type="checkbox" 
                       ${todo.completed ? 'checked' : ''} 
                       onchange="toggleTodo(${todo.id})">
                <span class="todo-text">${todo.text}</span>
                <span class="tag ${todo.category}">${todo.category}</span>
                <span class="due-date ${isOverdue ? 'overdue' : ''}">
                    ${formatDate(todo.date)}
                </span>
                <div class="actions">
                    <button onclick="openModal(${todo.id})" class="edit-btn">Edit</button>
                    <button onclick="deleteTodo(${todo.id})" class="delete-btn">Delete</button>
                </div>
            `;

            return todoElement;
        }

        // Add additional styles
        const finalStyles = `
            <style>
                .help-btn {
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    background-color: #666;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                }

                .search-input {
                    width: 100%;
                    padding: 8px;
                    margin-bottom: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }

                .no-results {
                    text-align: center;
                    padding: 20px;
                    color: #666;
                }

                .overdue {
                    color: #f44336;
                    font-weight: bold;
                }

                @media (max-width: 600px) {
                    .help-btn {
                        position: static;
                        width: 100%;
                        margin-bottom: 10px;
                    }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', finalStyles);

        // Add auto-save feature
        let autoSaveTimeout;
        function autoSave() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                saveTodos();
                showNotification('Changes auto-saved');
            }, 2000);
        }

        function showNotification(message) {
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = message;
            document.body.appendChild(notification);

            setTimeout(() => {
                notification.classList.add('fade-out');
                setTimeout(() => notification.remove(), 500);
            }, 2000);
        }

        // Add categories management
        const categories = {
            list: ['work', 'personal', 'shopping'],
            add(category) {
                if (!this.list.includes(category)) {
                    this.list.push(category);
                    this.updateCategorySelects();
                }
            },
            remove(category) {
                const index = this.list.indexOf(category);
                if (index > -1) {
                    this.list.splice(index, 1);
                    this.updateCategorySelects();
                }
            },
            updateCategorySelects() {
                const selects = document.querySelectorAll('#todo-category, #edit-category, #filter-category');
                selects.forEach(select => {
                    const currentValue = select.value;
                    select.innerHTML = `
                        ${select.id === 'filter-category' ? '<option value="all">All Categories</option>' : ''}
                        ${this.list.map(category => `
                            <option value="${category}" ${currentValue === category ? 'selected' : ''}>
                                ${category.charAt(0).toUpperCase() + category.slice(1)}
                            </option>
                        `).join('')}
                    `;
                });
            }
        };

        // Add category management UI
        function addCategoryManagement() {
            const categoryManager = document.createElement('div');
            categoryManager.className = 'category-manager';
            categoryManager.innerHTML = `
                <h3>Manage Categories</h3>
                <div class="category-input">
                    <input type="text" id="new-category" placeholder="New category name">
                    <button onclick="addNewCategory()">Add Category</button>
                </div>
                <div class="category-list"></div>
            `;
            document.querySelector('.container').appendChild(categoryManager);
            updateCategoryList();
        }

        function addNewCategory() {
            const input = document.getElementById('new-category');
            const category = input.value.trim().toLowerCase();
            if (category && !categories.list.includes(category)) {
                categories.add(category);
                input.value = '';
                updateCategoryList();
                showNotification('Category added');
            }
        }

        function updateCategoryList() {
            const categoryList = document.querySelector('.category-list');
            categoryList.innerHTML = categories.list.map(category => `
                <div class="category-item">
                    <span>${category}</span>
                    <button onclick="removeCategory('${category}')" 
                            ${['work', 'personal', 'shopping'].includes(category) ? 'disabled' : ''}>
                        Remove
                    </button>
                </div>
            `).join('');
        }

        function removeCategory(category) {
            if (confirm(`Are you sure you want to remove the category "${category}"?`)) {
                // Update todos with this category to 'personal'
                todos = todos.map(todo => ({
                    ...todo,
                    category: todo.category === category ? 'personal' : todo.category
                }));
                categories.remove(category);
                updateCategoryList();
                renderTodos();
                showNotification('Category removed');
            }
        }

        // Add final styles
        const finalAdditionalStyles = `
            <style>
                .notification {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background-color: #333;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 4px;
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                }

                .notification.fade-out {
                    animation: fadeOut 0.5s ease forwards;
                }

                .category-manager {
                    margin-top: 30px;
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-radius: 8px;
                }

                .category-input {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 15px;
                }

                .category-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px;
                    background-color: white;
                    margin-bottom: 5px;
                    border-radius: 4px;
                }

                .category-item button {
                    padding: 4px 8px;
                    font-size: 12px;
                }

                .category-item button:disabled {
                    background-color: #ccc;
                    cursor: not-allowed;
                }

                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                @keyframes fadeOut {
                    to {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                }

                .todo-summary {
                    margin-top: 20px;
                    padding: 15px;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .priority-indicator {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    display: inline-block;
                    margin-right: 5px;
                }

                .priority-high .priority-indicator { background-color: #f44336; }
                .priority-medium .priority-indicator { background-color: #ffb300; }
                .priority-low .priority-indicator { background-color: #4caf50; }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', finalAdditionalStyles);

        // Add todo summary
        function updateTodoSummary() {
            const summary = document.createElement('div');
            summary.className = 'todo-summary';
            
            const stats = getTodoStats();
            const percentComplete = stats.total === 0 ? 0 : 
                Math.round((stats.completed / stats.total) * 100);

            summary.innerHTML = `
                <h3>Summary</h3>
                <p>Tasks Complete: ${percentComplete}% (${stats.completed}/${stats.total})</p>
                <p>Priority Distribution:</p>
                <ul>
                    <li><span class="priority-indicator"></span>High: ${stats.high}</li>
                    <li><span class="priority-indicator"></span>Medium: ${stats.medium}</li>
                    <li><span class="priority-indicator"></span>Low: ${stats.low}</li>
                </ul>
            `;

            const existingSummary = document.querySelector('.todo-summary');
            if (existingSummary) {
                existingSummary.replaceWith(summary);
            } else {
                document.querySelector('.container').appendChild(summary);
            }
        }

        // Update the renderTodos function to include summary
        const finalRenderTodos = renderTodos;
        renderTodos = function() {
            finalRenderTodos();
            updateTodoSummary();
            updateProgress();
            autoSave();
        };

        // Add data persistence with IndexedDB
        const dbName = 'TodoDB';
        const dbVersion = 1;
        let db;

        const initDB = () => {
            return new Promise((resolve, reject) => {
                const request = indexedDB.open(dbName, dbVersion);

                request.onerror = () => reject(request.error);
                request.onsuccess = () => {
                    db = request.result;
                    resolve(db);
                };

                request.onupgradeneeded = (event) => {
                    const db = event.target.result;
                    if (!db.objectStoreNames.contains('todos')) {
                        db.createObjectStore('todos', { keyPath: 'id' });
                    }
                };
            });
        };

        // Save todos to IndexedDB
        async function saveToIndexedDB() {
            const transaction = db.transaction(['todos'], 'readwrite');
            const store = transaction.objectStore('todos');
            
            // Clear existing todos
            await store.clear();
            
            // Add all todos
            todos.forEach(todo => store.add(todo));
            
            return new Promise((resolve, reject) => {
                transaction.oncomplete = resolve;
                transaction.onerror = () => reject(transaction.error);
            });
        }

        // Load todos from IndexedDB
        async function loadFromIndexedDB() {
            const transaction = db.transaction(['todos'], 'readonly');
            const store = transaction.objectStore('todos');
            const request = store.getAll();

            return new Promise((resolve, reject) => {
                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
            });
        }

        // Add undo/redo functionality
        const history = {
            past: [],
            future: [],
            push(state) {
                this.past.push(JSON.stringify(state));
                this.future = [];
            },
            undo() {
                if (this.past.length === 0) return;
                
                const current = JSON.stringify(todos);
                this.future.push(current);
                
                todos = JSON.parse(this.past.pop());
                renderTodos();
            },
            redo() {
                if (this.future.length === 0) return;
                
                const current = JSON.stringify(todos);
                this.past.push(current);
                
                todos = JSON.parse(this.future.pop());
                renderTodos();
            }
        };

        // Add keyboard shortcuts for undo/redo
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'z') {
                e.preventDefault();
                history.undo();
            }
            if (e.ctrlKey && e.key === 'y') {
                e.preventDefault();
                history.redo();
            }
        });

        // Initialize the application
        async function initializeApp() {
            try {
                await initDB();
                const savedTodos = await loadFromIndexedDB();
                if (savedTodos.length > 0) {
                    todos = savedTodos;
                }
                renderTodos();
                addCategoryManagement();
                
                // Add undo/redo buttons
                document.querySelector('.action-buttons').insertAdjacentHTML('beforeend', `
                    <button onclick="history.undo()" class="undo-btn">Undo</button>
                    <button onclick="history.redo()" class="redo-btn">Redo</button>
                `);

                // Set up auto-backup
                setInterval(() => {
                    saveToIndexedDB();
                    showNotification('Auto-backup completed');
                }, 300000);
        // Add final event listeners and initialization
                document.addEventListener('visibilitychange', () => {
                    if (document.visibilityState === 'hidden') {
                        saveToIndexedDB();
                    }
                });

                // Add drag and drop touch support
                document.addEventListener('touchstart', handleTouchStart, false);
                document.addEventListener('touchmove', handleTouchMove, false);
                document.addEventListener('touchend', handleTouchEnd, false);

            } catch (error) {
                console.error('Failed to initialize app:', error);
                showNotification('Error initializing app');
            }
        }

        // Touch handling for mobile drag and drop
        let touchStartY = 0;
        let touchedElement = null;

        function handleTouchStart(e) {
            if (e.target.closest('.todo-item')) {
                touchedElement = e.target.closest('.todo-item');
                touchStartY = e.touches[0].clientY;
                touchedElement.classList.add('dragging');
            }
        }

        function handleTouchMove(e) {
            if (!touchedElement) return;
            e.preventDefault();
            
            const touch = e.touches[0];
            const moveY = touch.clientY - touchStartY;
            touchedElement.style.transform = `translateY(${moveY}px)`;
        }

        function handleTouchEnd(e) {
            if (!touchedElement) return;
            
            touchedElement.classList.remove('dragging');
            touchedElement.style.transform = '';
            
            const todoList = document.getElementById('todo-list');
            const children = [...todoList.children];
            const touchEndY = e.changedTouches[0].clientY;
            
            const dropTarget = children.find(child => {
                const rect = child.getBoundingClientRect();
                return touchEndY >= rect.top && touchEndY <= rect.bottom;
            });

            if (dropTarget && dropTarget !== touchedElement) {
                const draggedIndex = children.indexOf(touchedElement);
                const dropIndex = children.indexOf(dropTarget);
                
                // Reorder todos array
                const [draggedTodo] = todos.splice(draggedIndex, 1);
                todos.splice(dropIndex, 0, draggedTodo);
                
                renderTodos();
                history.push([...todos]);
            }

            touchedElement = null;
        }

        // Add final styles for mobile support
        const mobileStyles = `
            <style>
                @media (max-width: 768px) {
                    .todo-item {
                        touch-action: none;
                        user-select: none;
                    }

                    .todo-item.dragging {
                        opacity: 0.8;
                        background-color: #f0f0f0;
                        z-index: 1000;
                    }

                    .action-buttons {
                        flex-direction: column;
                    }

                    .action-buttons button {
                        width: 100%;
                        margin: 5px 0;
                    }

                    .todo-item .actions {
                        flex-direction: column;
                        gap: 5px;
                    }

                    .todo-item .actions button {
                        width: 100%;
                    }
                }

                /* Dark mode support */
                @media (prefers-color-scheme: dark) {
                    body {
                        background-color: #1a1a1a;
                        color: #ffffff;
                    }

                    .container {
                        background-color: #2d2d2d;
                    }

                    .todo-item {
                        background-color: #3d3d3d;
                    }

                    input, select {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border-color: #4d4d4d;
                    }

                    .category-manager {
                        background-color: #3d3d3d;
                    }

                    .category-item {
                        background-color: #2d2d2d;
                        color: #ffffff;
                    }

                    .todo-summary {
                        background-color: #2d2d2d;
                        color: #ffffff;
                    }

                    .notification {
                        background-color: #4d4d4d;
                    }
                }

                /* Animations and transitions */
                .todo-item {
                    transition: all 0.3s ease;
                }

                .todo-item:hover {
                    transform: translateX(5px);
                }

                .notification {
                    transition: opacity 0.3s ease, transform 0.3s ease;
                }

                /* Accessibility improvements */
                button:focus, input:focus, select:focus {
                    outline: 2px solid #4CAF50;
                    outline-offset: 2px;
                }

                /* Print styles */
                @media print {
                    .action-buttons, 
                    .input-section,
                    .filters,
                    .category-manager {
                        display: none;
                    }

                    .container {
                        box-shadow: none;
                    }

                    .todo-item {
                        break-inside: avoid;
                    }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', mobileStyles);

        // Add final utility functions
        function exportAsCSV() {
            const headers = ['Task', 'Status', 'Priority', 'Category', 'Due Date'];
            const csvContent = [
                headers.join(','),
                ...todos.map(todo => [
                    `"${todo.text}"`,
                    todo.completed ? 'Completed' : 'Pending',
                    todo.priority,
                    todo.category,
                    todo.date
                ].join(','))
            ].join('\n');

            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'todos.csv';
            link.click();
            URL.revokeObjectURL(url);
        }

        // Add final event listeners
        window.addEventListener('load', initializeApp);
        window.addEventListener('beforeunload', (e) => {
            saveToIndexedDB();
        });

        // Add PWA support
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('service-worker.js')
                .then(registration => {
                    console.log('ServiceWorker registration successful');
                })
                .catch(err => {
                    console.log('ServiceWorker registration failed:', err);
                });
        }

        // Create service-worker.js file
        const serviceWorkerContent = `
            const CACHE_NAME = 'todo-app-v1';
            const urlsToCache = [
                '/',
                '/index.html',
                '/styles.css',
                '/script.js'
            ];

            self.addEventListener('install', event => {
                event.waitUntil(
                    caches.open(CACHE_NAME)
                        .then(cache => cache.addAll(urlsToCache))
                );
            });

            self.addEventListener('fetch', event => {
                event.respondWith(
                    caches.match(event.request)
                        .then(response => response || fetch(event.request))
                );
            });
        `;

        // Add manifest.json for PWA
        const manifestContent = {
            name: 'Enhanced Todo App',
            short_name: 'Todos',
            start_url: '/',
            display: 'standalone',
            background_color: '#ffffff',
            theme_color: '#4CAF50',
            icons: [
                {
                    {
                    src: 'icon-192x192.png',
                    sizes: '192x192',
                    type: 'image/png'
                },
                {
                    src: 'icon-512x512.png',
                    sizes: '512x512',
                    type: 'image/png'
                }
            ]
        };

        // Add final utility methods
        const utils = {
            // Format date for display
            formatDate(date) {
                if (!date) return '';
                return new Date(date).toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
            },

            // Generate unique ID
            generateId() {
                return Date.now().toString(36) + Math.random().toString(36).substr(2);
            },

            // Debounce function for performance
            debounce(func, wait) {
                let timeout;
                return function executedFunction(...args) {
                    const later = () => {
                        clearTimeout(timeout);
                        func(...args);
                    };
                    clearTimeout(timeout);
                    timeout = setTimeout(later, wait);
                };
            },

            // Save state to localStorage as backup
            saveStateToLocalStorage: utils.debounce(() => {
                localStorage.setItem('todosBackup', JSON.stringify(todos));
            }, 1000)
        };

        // Add final event handlers
        const eventHandlers = {
            // Handle theme toggle
            toggleTheme() {
                document.body.classList.toggle('dark-theme');
                localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
            },

            // Handle todo item double click for quick edit
            handleTodoDoubleClick(id) {
                const todo = todos.find(t => t.id === id);
                if (!todo) return;

                const text = prompt('Edit todo:', todo.text);
                if (text !== null && text.trim() !== '') {
                    todos = todos.map(t => 
                        t.id === id ? {...t, text: text.trim()} : t
                    );
                    history.push([...todos]);
                    renderTodos();
                }
            },

            // Handle keyboard shortcuts
            handleKeyboardShortcuts(e) {
                if (e.ctrlKey && e.key === 'b') {
                    e.preventDefault();
                    exportToIndexedDB();
                }
                if (e.ctrlKey && e.key === 'p') {
                    e.preventDefault();
                    window.print();
                }
            }
        };

        // Add final initialization
        function finalizeApp() {
            // Add theme toggle button
            document.querySelector('.container').insertAdjacentHTML('afterbegin', `
                <button onclick="eventHandlers.toggleTheme()" class="theme-toggle">
                    Toggle Theme
                </button>
            `);

            // Initialize theme
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                document.body.classList.toggle('dark-theme', savedTheme === 'dark');
            }

            // Add double click handlers
            document.getElementById('todo-list').addEventListener('dblclick', (e) => {
                const todoItem = e.target.closest('.todo-item');
                if (todoItem) {
                    const id = parseInt(todoItem.dataset.id);
                    eventHandlers.handleTodoDoubleClick(id);
                }
            });

            // Add keyboard shortcut handlers
            document.addEventListener('keydown', eventHandlers.handleKeyboardShortcuts);

            // Initialize tooltips
            const tooltipElements = document.querySelectorAll('[data-tooltip]');
            tooltipElements.forEach(element => {
                tippy(element, {
                    content: element.dataset.tooltip,
                    placement: 'top'
                });
            });
        }

        // Final initialization call
        document.addEventListener('DOMContentLoaded', () => {
            initializeApp();
            finalizeApp();

            // Add final UI elements
            addFinalUIElements();
            
            // Initialize analytics
            initializeAnalytics();
        });

        function addFinalUIElements() {
            // Add statistics panel
            const statsPanel = `
                <div class="stats-panel">
                    <h3>Task Statistics</h3>
                    <div class="stats-content"></div>
                </div>
            `;

            // Add quick actions panel
            const quickActions = `
                <div class="quick-actions">
                    <button onclick="markAllComplete()" class="action-btn">
                        Mark All Complete
                    </button>
                    <button onclick="clearCompleted()" class="action-btn">
                        Clear Completed
                    </button>
                    <button onclick="exportAsCSV()" class="action-btn">
                        Export CSV
                    </button>
                </div>
            `;

            // Add settings panel
            const settingsPanel = `
                <div class="settings-panel">
                    <h3>Settings</h3>
                    <div class="setting-item">
                        <label>Auto-save Interval (minutes)</label>
                        <input type="number" id="auto-save-interval" min="1" max="60" value="5">
                    </div>
                    <div class="setting-item">
                        <label>Show Completed Tasks</label>
                        <input type="checkbox" id="show-completed" checked>
                    </div>
                    <div class="setting-item">
                        <label>Default Priority</label>
                        <select id="default-priority">
                            <option value="high">High</option>
                            <option value="medium" selected>Medium</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                </div>
            `;

            document.querySelector('.container').insertAdjacentHTML('beforeend', 
                statsPanel + quickActions + settingsPanel
            );
        }

        // Add utility functions for the new features
        function markAllComplete() {
            todos = todos.map(todo => ({...todo, completed: true}));
            history.push([...todos]);
            renderTodos();
            showNotification('All tasks marked as complete');
        }

        function clearCompleted() {
            const completedCount = todos.filter(todo => todo.completed).length;
            todos = todos.filter(todo => !todo.completed);
            history.push([...todos]);
            renderTodos();
            showNotification(`Cleared ${completedCount} completed tasks`);
        }

        function initializeAnalytics() {
            // Simple analytics implementation
            const analytics = {
                trackEvent(category, action, label) {
                    console.log('Analytics:', { category, action, label });
                    // Here you would typically send this to your analytics service
                },
                
                trackTodoCompletion(todo) {
                    this.trackEvent('Todo', 'Complete', todo.category);
                },

                trackTodoCreation(todo) {
                    this.trackEvent('Todo', 'Create', todo.priority);
                }
            };

            // Attach analytics to relevant actions
            const originalAddTodo = window.addTodo;
            window.addTodo = function(...args) {
                const result = originalAddTodo.apply(this, args);
                analytics.trackTodoCreation(todos[todos.length - 1]);
                return result;
            };
        }

        // Add final styles
        const finalStyles = `
            <style>
                .stats-panel,
                .quick-actions {
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                }

                .action-btn {
                    flex: 1;
                    min-width: 150px;
                    padding: 10px;
                    border: none;
                    border-radius: 4px;
                    background-color: #4CAF50;
                    color: white;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }

                .action-btn:hover {
                    background-color: #45a049;
                }

                .setting-item {
                    margin: 10px 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .stats-content {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 10px;
                    margin-top: 10px;
                }

                .stat-card {
                    padding: 10px;
                    background-color: #f5f5f5;
                    border-radius: 4px;
                    text-align: center;
                }

                .stat-number {
                    font-size: 24px;
                    font-weight: bold;
                    color: #4CAF50;
                }

                .stat-label {
                    font-size: 12px;
                    color: #666;
                }

                /* Responsive design improvements */
                @media (max-width: 600px) {
                    .quick-actions {
                        flex-direction: column;
                    }

                    .action-btn {
                        width: 100%;
                    }

                    .setting-item {
                        flex-direction: column;
                        align-items: flex-start;
                        gap: 5px;
                    }
                }

                /* Animation improvements */
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                .todo-item {
                    animation: fadeIn 0.3s ease;
                }

                /* Accessibility improvements */
                @media (prefers-reduced-motion: reduce) {
                    * {
                        animation: none !important;
                        transition: none !important;
                    }
                }

                /* Focus styles */
                :focus-visible {
                    outline: 3px solid #4CAF50;
                    outline-offset: 2px;
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', finalStyles);

        // Add final functionality
        function updateStatistics() {
            const stats = {
                total: todos.length,
                completed: todos.filter(todo => todo.completed).length,
                pending: todos.filter(todo => !todo.completed).length,
                highPriority: todos.filter(todo => todo.priority === 'high').length,
                overdue: todos.filter(todo => {
                    if (!todo.completed && todo.date) {
                        return new Date(todo.date) < new Date();
                    }
                    return false;
                }).length
            };

            const statsContent = document.querySelector('.stats-content');
            statsContent.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${stats.total}</div>
                    <div class="stat-label">Total Tasks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.completed}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.pending}</div>
                    <div class="stat-label">Pending</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.highPriority}</div>
                    <div class="stat-label">High Priority</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.overdue}</div>
                    <div class="stat-label">Overdue</div>
                </div>
            `;
        }

        // Add settings management
        const settings = {
            autoSaveInterval: 5,
            showCompleted: true,
            defaultPriority: 'medium',

            load() {
                const savedSettings = localStorage.getItem('todoSettings');
                if (savedSettings) {
                    const parsed = JSON.parse(savedSettings);
                    Object.assign(this, parsed);
                    this.updateUI();
                }
            },

            save() {
                localStorage.setItem('todoSettings', JSON.stringify({
                    autoSaveInterval: this.autoSaveInterval,
                    showCompleted: this.showCompleted,
                    defaultPriority: this.defaultPriority
                }));
            },

            updateUI() {
                document.getElementById('auto-save-interval').value = this.autoSaveInterval;
                document.getElementById('show-completed').checked = this.showCompleted;
                document.getElementById('default-priority').value = this.defaultPriority;
            }
        };

        // Add settings event listeners
        document.getElementById('auto-save-interval').addEventListener('change', (e) => {
            settings.autoSaveInterval = parseInt(e.target.value);
            settings.save();
            updateAutoSave();
        });

        document.getElementById('show-completed').addEventListener('change', (e) => {
            settings.showCompleted = e.target.checked;
            settings.save();
            renderTodos();
        });

        document.getElementById('default-priority').addEventListener('change', (e) => {
            settings.defaultPriority = e.target.value;
            settings.save();
        });

        // Add search functionality with highlighting
        function searchAndHighlight(searchTerm) {
            const filteredTodos = todos.filter(todo => 
                todo.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                todo.category.toLowerCase().includes(searchTerm.toLowerCase())
            );

            const todoList = document.getElementById('todo-list');
            todoList.innerHTML = '';

            filteredTodos.forEach(todo => {
                const todoElement = createTodoElement(todo);
                const highlightedText = todo.text.replace(
                    new RegExp(searchTerm, 'gi'),
                    match => `<mark>${match}</mark>`
                );
                todoElement.querySelector('.todo-text').innerHTML = highlightedText;
                todoList.appendChild(todoElement);
            });
        }

        // Add final helper functions
        function updateAutoSave() {
            clearInterval(window.autoSaveInterval);
            window.autoSaveInterval = setInterval(() => {
                saveToIndexedDB();
                showNotification('Auto-saved');
            }, settings.autoSaveInterval * 60 * 1000);
        }

        // Add error handling
        window.onerror = function(msg, url, lineNo, columnNo, error) {
            console.error('Error: ', msg, url, lineNo, columnNo, error);
            showNotification('An error occurred. Please try again.', 'error');
            return false;
        };

        // Add final event listeners
        window.addEventListener('online', () => {
            showNotification('Back online - syncing data...');
            saveToIndexedDB();
        });

        window.addEventListener('offline', () => {
            showNotification('You are offline. Changes will be saved locally.');
        });

        // Initialize everything
        function initializeEverything() {
            settings.load();
            updateAutoSave();
            updateStatistics();
            
            // Check for unsaved changes before closing
            window.addEventListener('beforeunload', (e) => {
                if (history.past.length > 0) {
                    e.preventDefault();
                    e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                }
            });

            // Add performance monitoring
            const performance = {
                measures: {},
                
                start(label) {
                    this.measures[label] = performance.now();
                },

                end(label) {
                    if (this.measures[label]) {
                        const duration = performance.now() - this.measures[label];
                        console.log(`${label}: ${duration.toFixed(2)}ms`);
                        delete this.measures[label];
                    }
                }
            };

            // Add accessibility improvements
            function improveAccessibility() {
                // Add ARIA labels
                document.querySelectorAll('button').forEach(button => {
                    if (!button.getAttribute('aria-label')) {
                        button.setAttribute('aria-label', button.textContent.trim());
                    }
                });

                // Add keyboard navigation
                const focusableElements = document.querySelectorAll(
                    'button, input, select, [tabindex]:not([tabindex="-1"])'
                );

                focusableElements.forEach(el => {
                    el.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            el.click();
                        }
                    });
                });
            }

            // Add final utility functions
            const utils = {
                // Generate unique ID with prefix
                generateId(prefix = 'todo') {
                    return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                },

                // Format date with options
                formatDate(date, options = {}) {
                    if (!date) return '';
                    const defaultOptions = {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    };
                    return new Date(date).toLocaleString(undefined, { ...defaultOptions, ...options });
                },

                // Deep clone object
                clone(obj) {
                    return JSON.parse(JSON.stringify(obj));
                }
            };

            // Add final notification improvements
            function showNotification(message, type = 'info', duration = 3000) {
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                notification.innerHTML = `
                    <div class="notification-content">
                        <span class="notification-message">${message}</span>
                        <button class="notification-close" aria-label="Close notification">×</button>
                    </div>
                `;

                document.body.appendChild(notification);

                // Add click handler to close button
                notification.querySelector('.notification-close').addEventListener('click', () => {
                    notification.remove();
                });

                // Auto remove after duration
                setTimeout(() => {
                    notification.classList.add('notification-fade-out');
                    setTimeout(() => notification.remove(), 300);
                }, duration);
            }

            // Add final styles for notifications
            const finalNotificationStyles = `
                <style>
                    .notification {
                        position: fixed;
                        bottom: 20px;
                        right: 20px;
                        padding: 15px;
                        border-radius: 4px;
                        background-color: #333;
                        color: white;
                        z-index: 1000;
                        animation: slideIn 0.3s ease;
                        max-width: 300px;
                    }

                    .notification-content {
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        gap: 10px;
                    }

                    .notification-close {
                        background: none;
                        border: none;
                        color: white;
                        cursor: pointer;
                                        }
                    
                    .notification.notification-info {
                        background-color: #007bff;
                    }

                    .notification.notification-success {
                        background-color: #28a745;
                    }

                    .notification.notification-warning {
                        background-color: #ffc107;
                        color: #333;
                    }

                    .notification.notification-error {
                        background-color: #dc3545;
                    }

                    .notification-fade-out {
                        opacity: 0;
                        transition: opacity 0.3s ease;
                    }

                    @keyframes slideIn {
                        from {
                            transform: translateY(20px);
                            opacity: 0;
                        }
                        to {
                            transform: translateY(0);
                            opacity: 1;
                        }
                    }
                </style>
            `;

            // Append the styles to the document head
            document.head.insertAdjacentHTML('beforeend', finalNotificationStyles);

            // Call the accessibility improvements function on page load
            window.addEventListener('DOMContentLoaded', improveAccessibility);

            // Example usage
            document.querySelector('#someButton').addEventListener('click', () => {
                showNotification('This is an info message!', 'info');
                performance.start('example');
                
                // Simulate some process
                setTimeout(() => {
                    performance.end('example');
                    showNotification('Process completed!', 'success');
                }, 1000);
            });
