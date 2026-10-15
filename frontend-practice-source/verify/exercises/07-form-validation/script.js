const form = document.getElementById('signup');
const username = document.getElementById('username');
const email = document.getElementById('email');
const password = document.getElementById('password');

const usernameError = document.getElementById('username-error');
const emailError = document.getElementById('email-error');
const passwordError = document.getElementById('password-error');
const formMsg = document.getElementById('form-msg');

const emailPattern = /^\S+@\S+\.\S+$/;

form.addEventListener('submit', (event) => {
  event.preventDefault();

  let isValid = true;

  // 1. Username: required
  if (username.value.trim() === '') {
    usernameError.textContent = 'Username is required.';
    isValid = false;
  } else {
    usernameError.textContent = '';
  }

  // 2. Email: required + must look like an email
  const emailValue = email.value.trim();
  if (emailValue === '') {
    emailError.textContent = 'Email is required.';
    isValid = false;
  } else if (!emailPattern.test(emailValue)) {
    emailError.textContent = 'Please enter a valid email.';
    isValid = false;
  } else {
    emailError.textContent = '';
  }

  // 3. Password: required + at least 6 characters
  if (password.value === '') {
    passwordError.textContent = 'Password is required.';
    isValid = false;
  } else if (password.value.length < 6) {
    passwordError.textContent = 'Password must be at least 6 characters.';
    isValid = false;
  } else {
    passwordError.textContent = '';
  }

  // 4. The overall message
  if (isValid) {
    formMsg.textContent = 'Account created successfully!';
  } else {
    formMsg.textContent = '';
  }
});
