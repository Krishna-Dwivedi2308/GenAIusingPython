const taskInput = document.getElementById('taskInput');
const addBtn = document.getElementById('addBtn');
const todoList = document.getElementById('todoList');

function createTaskItem(text) {
  const li = document.createElement('li');
  const span = document.createElement('span');
  span.className = 'task';
  span.textContent = text;

  span.addEventListener('click', () => {
    span.classList.toggle('completed');
  });

  const removeBtn = document.createElement('button');
  removeBtn.className = 'removeBtn';
  removeBtn.innerHTML = '🗑️';
  removeBtn.onclick = function() {
    li.remove();
  };
  li.appendChild(span);
  li.appendChild(removeBtn);
  return li;
}

addBtn.addEventListener('click', () => {
  const taskValue = taskInput.value.trim();
  if (taskValue !== "") {
    todoList.appendChild(createTaskItem(taskValue));
    taskInput.value = '';
    taskInput.focus();
  }
});

taskInput.addEventListener('keypress', function(e){
  if (e.key === 'Enter') {
    addBtn.click();
  }
});
