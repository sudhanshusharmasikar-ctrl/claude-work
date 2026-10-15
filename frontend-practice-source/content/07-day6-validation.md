:::chapter 6 | Checking What the User Typed: Form Validation | Exercise 07 · else if · regular expressions · a flag
- Why the form says **`novalidate`**, and what that means for you
- Chains of decisions with **`else if`**
- Reading a **regular expression** for emails, and testing text with `.test()`
- The length of a string, and the **not** operator `!`
- A **flag** variable that remembers "was anything wrong?"
:::

:::day Today's plan (2 hours)
One exercise with a lot of `if`s. **0–25** new ideas · **25–35** starter files · **35–90** build · **90–100** grade · **100–120** review. If you finish early, redo **Exercise 05** from the starter files with a 25-minute timer.
:::

## Exercise 07 · Form Validation

### What you are building

![The validation form before and after](content/img/07.png){.shot}

On **Create account**, each field is checked. A problem shows a red message under that field; if everything is fine, a green success message appears instead. The grader checks:

| Test | Fills in | Expects |
|---|---|---|
| blocks an empty submission and shows all errors | nothing | all three `.error` paragraphs have text; `#form-msg` is empty |
| flags an invalid email format | `ada` · `not-an-email` · `secret1` | `#email-error` has text; `#form-msg` empty |
| flags a short password | `ada` · `ada@example.com` · `123` | `#password-error` has text |
| accepts a valid submission | `ada` · `ada@example.com` · `secret1` | `#form-msg` has text; all three errors are empty |

### New ideas

#### 1. `novalidate`: you're in charge

The form tag is `<form id="signup" class="card" novalidate>`. `novalidate` switches **off** the browser's built-in checks (the little bubbles you saw on Day 2), so the `submit` event always reaches your code and **you** decide what is valid and what message to show. Companies do this to control the wording and the look of errors.

#### 2. `else if`: more than two choices

```js title="checking a field in order"
if (emailValue === '') {
  // empty
} else if (!emailPattern.test(emailValue)) {
  // not empty, but the wrong shape
} else {
  // fine
}
```

The browser tries each condition **from the top** and runs only the **first** block whose condition is true. Order matters: check *empty* before *wrong format*, so an empty field says *"Email is required"*, not *"invalid email"*.

`!` means **not**: `!true` is `false`. So `!emailPattern.test(emailValue)` reads *"the email does **not** match the pattern"*.

#### 3. A regular expression for emails

A **regular expression** (regex) describes the **shape** of text. The task suggests this one:

```js title="the email pattern"
const emailPattern = /^\S+@\S+\.\S+$/;
```

| Piece | Means |
|---|---|
| `/ ... /` | the slashes start and end the regex (like quotes for a string) |
| `^` | the **start** of the text |
| `\S+` | one or more characters that are **not spaces** |
| `@` | an actual `@` |
| `\.` | an actual dot (a plain `.` means *any character*, so it needs a `\`) |
| `$` | the **end** of the text |

In words: *some non-space characters, an `@`, more non-space characters, a dot, more non-space characters, and nothing else*. `.test(text)` answers `true` or `false`:

```js title="testing the pattern"
console.log(emailPattern.test('ada@example.com'));
console.log(emailPattern.test('not-an-email'));
console.log(emailPattern.test('ada@example'));
console.log(emailPattern.test('ada lovelace@example.com'));
console.log('secret'.length, 'abc'.length < 6);
```

```output
true
false                                  #> no @
false                                  #> no dot after the @
false                                  #> a space breaks \S+
6 true
```

The last line: `.length` on a **string** counts its characters. That's the password check.

:::note You don't need to master regex
For interviews, it's enough to read this one pattern and explain each piece. Real projects usually take a tested pattern from a library rather than writing one.
:::

#### 4. A flag

You need to check **all three** fields (so all three messages appear together), and then decide the overall result. Start with a variable that assumes the best, and switch it off whenever a check fails:

```js title="the flag pattern"
let isValid = true;
if (/* something is wrong */) {
  isValid = false;
}
// ... more checks, each one may set isValid = false
if (isValid) {
  // everything passed
}
```

### Read the starter files

| File | What is there | What you will use |
|---|---|---|
| `index.html` | complete, with `novalidate` | inputs `#username`, `#email`, `#password`; error paragraphs `#username-error`, `#email-error`, `#password-error`; `#form-msg` |
| `style.css` | two empty rules | `.error` (small, red) and `.success` (green) |
| `script.js` | comments only | everything |

### The plan in plain English

1. Select the form, the three inputs, the three error paragraphs and `#form-msg`. Write the email pattern as a `const`.
2. On `submit`: prevent the reload; set `isValid = true`.
3. **Username:** empty after trim? Write an error and set the flag false. Otherwise clear the error.
4. **Email:** empty? *"Email is required."* Else, doesn't match the pattern? *"Please enter a valid email."* Else clear. Set the flag false in both error cases.
5. **Password:** empty? Required. Else shorter than 6? Too short. Else clear.
6. If the flag is still true, show a success message; otherwise **clear** `#form-msg`.

:::tip Hint 1
Every field must end in a known state after each submit: either an error text or `''`. That's why each `if` chain ends with an `else` that clears the message. Otherwise an old error stays on screen after the user fixes the field.
:::

:::tip Hint 2
Don't `trim()` the password: spaces can be a real part of a password. The task only says *required* and *at least 6 characters*.
:::

:::tip Hint 3
The email chain:
```js title="the email checks"
if (emailValue === '') {
  emailError.textContent = 'Email is required.';
  isValid = false;
} else if (!emailPattern.test(emailValue)) {
  emailError.textContent = 'Please enter a valid email.';
  isValid = false;
} else {
  emailError.textContent = '';
}
```
:::

:::note Stop here and build it
Then run `npm test -- 07-form-validation`.
:::

### The solution, line by line

```js title="07/script.js" lines
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
```

| Lines | What they do |
|---|---|
| 1–11 | Select eight elements and define the pattern once, outside the listener. |
| 14 | No reload. |
| 16 | The flag: innocent until proven guilty. |
| 19–24 | Username: one check, two outcomes. |
| 27–36 | Email: three outcomes, in the right order. The value is trimmed once and reused. |
| 39–47 | Password: same shape as the email, with `.length` instead of the pattern. |
| 50–54 | The overall result. Clearing `#form-msg` on failure matters: after one successful submit, a later failed one must not still say *success*. |

The repository's `solution/` puts the checks in a separate `validate()` function that **returns** `true` or `false`, and the listener calls `if (validate()) { ... }`. That's a good next step once this version makes sense: it separates *checking* from *reacting*.

### Mistakes beginners make

:::mistake Stopping at the first error with `return`
If you `return` as soon as the username is empty, the email and password errors never appear, and the first test (all three errors at once) fails. Check everything, **then** decide.
:::

:::mistake Writing `.` instead of `\.` in the pattern
`/^\S+@\S+.\S+$/` accepts `ada@examplecom`, because a plain `.` matches **any** character. Escape it: `\.`.
:::

:::mistake Never clearing old errors
Without the `else { error.textContent = ''; }` branches, an error from a previous attempt stays on screen: submit an empty form, then type a username and submit again, and *Username is required.* is still there. The grader won't catch this (each test starts on a freshly loaded page), but anyone trying your page will.
:::

### Interview questions

:::qa -
Q: Why validate in JavaScript if the server validates anyway?
Client-side validation gives **instant feedback** and saves a round trip. But it can be bypassed (anyone can turn off JavaScript or send a request directly), so the **server must always validate too**. Client-side is for the user's comfort, server-side is for security.

Q: Explain `/^\S+@\S+\.\S+$/`.
Start of text, one or more non-space characters, `@`, one or more non-space characters, a literal dot, one or more non-space characters, end of text. It's a basic shape check, not a full email validator.

Q: What does the `novalidate` attribute do?
It turns off the browser's built-in form checks (`required`, `type="email"` and so on) on submit, so the page's JavaScript can handle validation and messages itself.
:::

### Practice twist

Validate **as the user types**: listen for `input` on each field and update only that field's error. Hint: move each field's check into its own function (`checkUsername()`, `checkEmail()`, `checkPassword()`) that writes the error and returns `true` or `false`. The submit listener then becomes:

```js title="the submit listener after the twist"
const okName = checkUsername();
const okEmail = checkEmail();
const okPassword = checkPassword();
if (okName && okEmail && okPassword) { /* success */ }
```

Why not simply `if (checkUsername() && checkEmail() && checkPassword())`? (Answer: `&&` stops at the first `false`, so the later checks wouldn't run and their errors wouldn't show.)
