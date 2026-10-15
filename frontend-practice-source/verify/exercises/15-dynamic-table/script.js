// The employee data is fixed — do not change it.
const employees = [
  { name: 'Grace Hopper', age: 45, city: 'New York' },
  { name: 'Ada Lovelace', age: 36, city: 'London' },
  { name: 'Alan Turing', age: 41, city: 'Manchester' },
  { name: 'Linus Torvalds', age: 54, city: 'Helsinki' },
  { name: 'Margaret Hamilton', age: 33, city: 'Boston' },
  { name: 'Dennis Ritchie', age: 62, city: 'Murray Hill' },
];

const filterInput = document.getElementById('filter');
const sortNameBtn = document.getElementById('sort-name');
const sortAgeBtn = document.getElementById('sort-age');
const tableBody = document.getElementById('table-body');
const rowCount = document.getElementById('row-count');

let sortBy = ''; // '' (no sorting), 'name' or 'age'

function render() {
  const query = filterInput.value.trim().toLowerCase();

  // 1. Filter: keep employees whose name or city contains the query
  const rows = employees.filter((emp) => {
    const name = emp.name.toLowerCase();
    const city = emp.city.toLowerCase();
    return name.includes(query) || city.includes(query);
  });

  // 2. Sort the filtered list
  if (sortBy === 'name') {
    rows.sort((a, b) => a.name.localeCompare(b.name));
  } else if (sortBy === 'age') {
    rows.sort((a, b) => a.age - b.age);
  }

  // 3. Draw one <tr> per employee
  tableBody.innerHTML = '';
  rows.forEach((emp) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${emp.name}</td><td>${emp.age}</td><td>${emp.city}</td>`;
    tableBody.appendChild(tr);
  });

  // 4. Update the count
  const word = rows.length === 1 ? 'employee' : 'employees';
  rowCount.textContent = `${rows.length} ${word}`;
}

filterInput.addEventListener('input', render);

sortNameBtn.addEventListener('click', () => {
  sortBy = 'name';
  render();
});

sortAgeBtn.addEventListener('click', () => {
  sortBy = 'age';
  render();
});

render();
