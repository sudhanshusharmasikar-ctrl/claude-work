// The product list is fixed — do not change it.
const products = [
  'Apple iPhone',
  'Apple MacBook',
  'Apple Watch',
  'Samsung Galaxy',
  'Sony Headphones',
  'Dell XPS Laptop',
  'Google Pixel',
  'Xiaomi Redmi',
];

const searchInput = document.getElementById('search');
const resultsList = document.getElementById('results');
const countText = document.getElementById('count');
const emptyText = document.getElementById('empty');

function render() {
  const query = searchInput.value.trim().toLowerCase();

  const matches = products.filter((product) => {
    return product.toLowerCase().includes(query);
  });

  resultsList.innerHTML = '';
  matches.forEach((product) => {
    const li = document.createElement('li');
    li.className = 'result-item';
    li.textContent = product;
    resultsList.appendChild(li);
  });

  const word = matches.length === 1 ? 'result' : 'results';
  countText.textContent = `${matches.length} ${word}`;

  emptyText.hidden = matches.length > 0;
}

searchInput.addEventListener('input', render);

render();
