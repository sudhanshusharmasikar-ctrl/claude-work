const passwordInput = document.getElementById('password');
const toggleBtn = document.getElementById('toggle-password');

toggleBtn.addEventListener('click', () => {
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    toggleBtn.textContent = 'Hide';
    toggleBtn.setAttribute('aria-pressed', 'true');
  } else {
    passwordInput.type = 'password';
    toggleBtn.textContent = 'Show';
    toggleBtn.setAttribute('aria-pressed', 'false');
  }
});
