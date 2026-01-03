const todoForm = document.getElementById('todo-form');
const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');

// Load tasks from localStorage
window.addEventListener('DOMContentLoaded', loadTodos);

todoForm.addEventListener('submit', function(e) {
  e.preventDefault();
  const value = todoInput.value.trim();
  if (value) {
    addTodo(value);
    saveTodo(value);
    todoInput.value = '';
  }
});

todoList.addEventListener('click', function(e) {
  if (e.target.classList.contains('remove-btn')) {
    const li = e.target.closest('li');
    removeTodo(li.querySelector('.todo-text').textContent);
    li.remove();
  } else if (e.target.classList.contains('todo-text')) {
    const li = e.target.closest('li');
    li.classList.toggle('completed');
    toggleCompleted(e.target.textContent);
  }
});

function addTodo(text, completed = false) {
  const li = document.createElement('li');
  if (completed) li.classList.add('completed');
  li.innerHTML = `
    <span class="todo-text">${text}</span>
    <button class="remove-btn" title="Remove">✕</button>
  `;
  todoList.appendChild(li);
}

function saveTodo(text) {
  let todos = JSON.parse(localStorage.getItem('todos') || '[]');
  todos.push({ text, completed: false });
  localStorage.setItem('todos', JSON.stringify(todos));
}

function loadTodos() {
  const todos = JSON.parse(localStorage.getItem('todos') || '[]');
  todos.forEach(todo => addTodo(todo.text, todo.completed));
}

function removeTodo(text) {
  let todos = JSON.parse(localStorage.getItem('todos') || '[]');
  todos = todos.filter(todo => todo.text !== text);
  localStorage.setItem('todos', JSON.stringify(todos));
}

function toggleCompleted(text) {
  let todos = JSON.parse(localStorage.getItem('todos') || '[]');
  todos = todos.map(todo => {
    if (todo.text === text) return { ...todo, completed: !todo.completed };
    return todo;
  });
  localStorage.setItem('todos', JSON.stringify(todos));
}
