const countEl = document.getElementById('count');
const incrementBtn = document.getElementById('increment');
const resetBtn = document.getElementById('reset');

let count = 0;

function increase() {
  count = count + 1;
  countEl.textContent = count;
}

function reset() {
  count = 0;
  countEl.textContent = count;
}

incrementBtn.addEventListener('click', increase);
resetBtn.addEventListener('click', reset);
