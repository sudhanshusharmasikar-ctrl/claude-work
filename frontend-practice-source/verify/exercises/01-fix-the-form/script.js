const form = document.getElementById('signup');
const nameInput = document.getElementById('fullname');
const result = document.getElementById('result');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const name = nameInput.value.trim();
  result.textContent = `Thanks, ${name}! Your account was created.`;
});
