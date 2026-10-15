const form = document.getElementById('todo-form');
const input = document.getElementById('todo-input');
const list = document.getElementById('todo-list');
const emptyText = document.getElementById('empty');

function updateEmpty() {
  emptyText.hidden = list.children.length > 0;
}

function createTodo(text) {
  const li = document.createElement('li');
  li.className = 'todo-item';

  const span = document.createElement('span');
  span.className = 'todo-text';
  span.textContent = text;

  const toggleBtn = document.createElement('button');
  toggleBtn.type = 'button';
  toggleBtn.className = 'todo-toggle';
  toggleBtn.textContent = 'Done';
  toggleBtn.addEventListener('click', () => {
    li.classList.toggle('completed');
  });

  const deleteBtn = document.createElement('button');
  deleteBtn.type = 'button';
  deleteBtn.className = 'todo-delete';
  deleteBtn.textContent = 'Delete';
  deleteBtn.addEventListener('click', () => {
    li.remove();
    updateEmpty();
  });

  li.appendChild(span);
  li.appendChild(toggleBtn);
  li.appendChild(deleteBtn);
  return li;
}

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const text = input.value.trim();
  if (text === '') {
    return;
  }

  list.appendChild(createTodo(text));
  input.value = '';
  updateEmpty();
});

updateEmpty();
