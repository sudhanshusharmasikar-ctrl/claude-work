:::chapter 2 | Forms and Toggles | Exercise 01 Fix the Form · Exercise 08 Show / Hide Password
- **HTML forms done properly:** labels, input types, `required`, `fieldset`
- The **submit** event, the **event object** and `preventDefault()`
- Reading what the user typed: `.value` and `.trim()`
- **Template literals** and **arrow functions**
- Decisions with **`if` / `else`** and `===`
- Changing an element's **properties** and **attributes**
:::

:::day Today's plan (2 hours)
**Exercise 01** (70 min): new ideas 20 · build 35 · grade and review 15. **Exercise 08** (50 min): new ideas 10 · build 25 · grade and review 15.
:::

## Exercise 01 · Fix the Form

### What you are building

![The form before and after](content/img/01.png){.shot}

The form **looks** fine, but its HTML is poor: no labels, every field is plain text (even the password is visible), nothing is required. You fix the HTML, add a focus style in CSS, and make the button show a thank-you message. The grader checks:

| Test | What it checks |
|---|---|
| every field has an associated, non-empty label | a `<label for="fullname">` (and email, phone, password) exists and has text |
| inputs use the correct types | `#email` is `type="email"`, `#phone` is `type="tel"`, `#password` is `type="password"` |
| required fields are marked required | `#fullname`, `#email`, `#password` have the `required` attribute |
| fields are grouped in a fieldset with a legend | exactly one `<fieldset>` inside the form, with a `<legend>` directly inside it |
| submitting shows a message containing the entered name | fills the form, clicks **Sign up**, expects `#result` to contain `Ada Lovelace` |

### New ideas

#### 1. Labels: the text that belongs to an input

A **placeholder** (the grey text inside an empty box) disappears as soon as you type, and screen readers used by blind users may not read it. A **label** stays visible and is officially connected to its input:

```html title="a label connected to an input"
<label for="email">Email</label>
<input type="email" id="email" />
```

The label's `for` must be **exactly** the input's `id`. Bonus: clicking the label puts the cursor in the input.

#### 2. Input types do real work

| Type | What the browser does for you |
|---|---|
| `type="text"` | nothing special |
| `type="email"` | checks there's an `@` before submitting; phones show a keyboard with `@` |
| `type="tel"` | phones show a number pad |
| `type="password"` | hides the characters as dots |

#### 3. `required` and `fieldset`

`required` is a **boolean attribute**: it is either there or not, so you write just the word, `<input ... required />`. The browser then **refuses to submit** while that field is empty and shows a small message.

`<fieldset>` draws a group around related fields, and its first child `<legend>` names the group. Screen readers announce the legend when the user enters the group.

#### 4. The submit event and `preventDefault()`

A `<form>` was invented to **send data to a server**. When it is submitted, the browser sends the data and **loads a new page**. That reload wipes out anything your script showed. Since we have no server, we listen for the form's `submit` event and cancel the reload:

```js title="listen to the form, not the button"
form.addEventListener('submit', (event) => {
  event.preventDefault();      // stop the page from reloading
  // ... now do our own thing
});
```

- Listen to **`submit` on the form**, not `click` on the button. `submit` fires however the form is sent (a click on the button **or** Enter in a field), and only **after** the browser's own checks, such as `required`, have passed.
- The browser passes your function an **event object** (here named `event`) with details about what happened. `event.preventDefault()` means *"don't do your default action"*.

#### 5. Arrow functions

`(event) => { ... }` is a function without a name, written in place. These two do the same thing:

```js title="the same listener, two ways"
function handleSubmit(event) {
  event.preventDefault();
}
form.addEventListener('submit', handleSubmit);

form.addEventListener('submit', (event) => {
  event.preventDefault();
});
```

The arrow form is shorter and keeps the code next to the element it belongs to. From now on, most listeners in this guide use it.

#### 6. Reading the input and building a message

```js title="trim and template literals"
const raw = '   Ada Lovelace  ';
console.log('[' + raw + ']');
console.log('[' + raw.trim() + ']');

const name = raw.trim();
console.log(`Thanks, ${name}! Your account was created.`);
```

```output
[   Ada Lovelace  ]
[Ada Lovelace]
Thanks, Ada Lovelace! Your account was created.
```

- `input.value` is the text currently in an input (always a string).
- `.trim()` removes spaces from **both ends**.
- Text in **backticks** `` ` `` is a **template literal**: `${...}` inside it is replaced by the value. It is much easier to read than `'Thanks, ' + name + '!'`.

#### 7. CSS: `:focus`

`input:focus` styles an input **while the cursor is in it**. Keyboard users rely on it to see where they are. `outline` draws a line outside the border that doesn't change the element's size.

### Read the starter files

| File | What is there | What you will change |
|---|---|---|
| `index.html` | a form `#signup` with four `<input>`s (all `type="text"`), a button, and `<p id="result">` | add labels, fix types, add `required`, wrap in `fieldset` + `legend` |
| `style.css` | styles for `label`, `input`, `fieldset`, `button` are ready | add an `input:focus` rule |
| `script.js` | only comments | the submit handler |

### The plan in plain English

1. **HTML:** put a `<fieldset>` around the inputs; its first child is a `<legend>`. Before each input, add a `<label for="...">` with the input's id. Fix the three types. Add `required` to name, email and password.
2. **CSS:** write `input:focus` with a coloured outline.
3. **JS:** select the form, the name input and `#result`. On `submit`: prevent the reload, read and trim the name, write the message into `#result`.

:::tip Hint 1
The `<h1>Create your account</h1>` can become the `<legend>`: the legend **is** the heading of the group. Keep the button and `#result` after the `</fieldset>`.
:::

:::tip Hint 2
The JavaScript is 3 selects plus one listener with 3 lines inside. The listener goes on the **form** (`'submit'`), not on the button.
:::

:::tip Hint 3
```js title="the inside of the submit listener"
event.preventDefault();
const name = nameInput.value.trim();
result.textContent = `Thanks, ${name}! Your account was created.`;
```
:::

:::note Stop here and build it
Then run `npm test -- 01-fix-the-form`.
:::

### The solution, line by line

```html title="01/index.html (the form)"
<form id="signup" class="card">
  <fieldset>
    <legend>Create your account</legend>

    <label for="fullname">Full name</label>
    <input type="text" id="fullname" placeholder="Full name" required />

    <label for="email">Email</label>
    <input type="email" id="email" placeholder="Email" required />

    <label for="phone">Phone</label>
    <input type="tel" id="phone" placeholder="Phone" />

    <label for="password">Password</label>
    <input type="password" id="password" placeholder="Password" required />
  </fieldset>

  <button type="submit">Sign up</button>
  <p id="result" class="result" aria-live="polite"></p>
</form>
```

- The heading moved into `<legend>`, so the form still has a title and the grader finds the legend **directly inside** the fieldset.
- Every `for` matches an `id` exactly. The phone is not required (the task lists only name, email and password).
- `aria-live="polite"` on `#result` was already there: it tells screen readers to read the message aloud when it appears.

```css title="01/style.css (the new rule, where the TODO was)"
input:focus {
  outline: 2px solid #7c3aed;
  border-color: #7c3aed;
}
```

```css title="01/style.css (two lines added to the existing fieldset rule)"
fieldset {
  border: 0;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}
```

The `fieldset` rule already existed; adding `display: grid` and `gap: 8px` spaces the labels and inputs evenly. (You'll learn grid on Day 3. For now: *"stack the children with an 8px gap"*.) The grader doesn't check it, but without it the labels sit right on top of the inputs above them.

```js title="01/script.js" lines
const form = document.getElementById('signup');
const nameInput = document.getElementById('fullname');
const result = document.getElementById('result');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const name = nameInput.value.trim();
  result.textContent = `Thanks, ${name}! Your account was created.`;
});
```

| Lines | What they do |
|---|---|
| 1–3 | **Select** the form, the name box and the message paragraph. |
| 5 | **Listen** for `submit` on the form. The browser hands us the event object. |
| 6 | Cancel the page reload, or the message would vanish a moment after it appears. |
| 7 | **Read** what was typed, without spaces at the ends. |
| 8 | **Change** the page: put the message in `#result`. |

### Mistakes beginners make

:::mistake `required="true"`
It looks logical but the grader **fails** it (we tried: *Expected "" · Received "true"*). A boolean attribute is written as the bare word: `required`. Even `required="false"` would still make the field required, because only the **presence** of the attribute matters.
:::

:::mistake Forgetting `event.preventDefault()`
The message appears for a split second, then the page reloads and it's gone. We removed that line and ran the grader: the last test failed with *Received string: ""*.
:::

:::mistake Listening for `click` on the button
It seems to work, but the click happens **before** the browser checks the `required` fields. Your code runs even when the form is half empty, and if you call `preventDefault()` on the click, the browser's check never runs at all. A `submit` listener runs only once the checks have passed.
:::

### Interview questions

:::qa -
Q: Why use a `<label>` instead of a placeholder?
A label is always visible, is read by screen readers, and clicking it focuses its input. A placeholder vanishes when you type and is not a reliable name for the field.

Q: What does `event.preventDefault()` do? Give two uses.
It cancels the browser's default action for that event. Stopping a form submit from reloading the page, and stopping a link (`<a>`) from navigating, are the two classic uses.

Q: Why `type="email"` and not `type="text"`?
The browser checks the format before submitting, and mobile phones show a keyboard with `@`. It's free validation and better usability.

Q: What is semantic HTML?
Using the element that **means** the right thing: `<button>` for buttons, `<label>` for labels, `<nav>`, `<main>`, `<fieldset>`. It helps screen readers, search engines and other developers, at no cost.
:::

### Practice twist

Make the message friendlier: if the name is empty after trimming (someone typed only spaces), show *"Please enter your name."* instead. Use `if (name === '') { ... } else { ... }`. You'll see `if` properly in the next exercise.

## Exercise 08 · Show / Hide Password

### What you are building

![The password field before and after](content/img/08.png){.shot}

A **Show** button next to a password field. Clicking it reveals the password and the button says **Hide**; clicking again hides it. The grader checks:

| Test | What it checks |
|---|---|
| starts masked with a "Show" button | `#password` has `type="password"`, the button says *Show* |
| reveals the password on click and updates the label | after one click: `type="text"` and *Hide* |
| hides the password again on the second click | after two clicks: back to `password` and *Show* |
| keeps aria-pressed in sync | after one click `aria-pressed="true"`, after two `"false"` |

### New ideas

#### 1. Decisions: `if` / `else`

```js title="if / else"
if (passwordInput.type === 'password') {
  // runs when the condition is true
} else {
  // runs otherwise
}
```

Compare with **three** equals signs, `===`. Two (`==`) converts types before comparing, which gives surprises:

```js title="== versus ==="
console.log(5 == '5', 5 === '5');
console.log('password' === 'password', 'password' === 'text');
```

```output
true false
true false
```

`5 == '5'` is `true` because `==` turns the text `'5'` into a number first. `===` says the number 5 and the text `'5'` are different, which is what you almost always want. **Always use `===`** (and `!==` for "not equal").

#### 2. Element properties: read them and change them

An element object has **properties** you can read and change with a dot. For an input, `input.type` is its type:

```js title="type into the console of exercise 08"
const input = document.getElementById('password');
input.type             // 'password'
input.type = 'text'    // the dots turn into letters
```

#### 3. Attributes with `setAttribute`

Some information lives only in **attributes**, such as `aria-pressed`. **ARIA** attributes describe the page to screen readers: `aria-pressed="true"` says *"this toggle button is switched on"*. Set any attribute with:

```js title="setAttribute"
toggleBtn.setAttribute('aria-pressed', 'true');
```

Attribute values are always **strings**, so write `'true'` with quotes.

### Read the starter files

| File | What is there | What you will use |
|---|---|---|
| `index.html` | complete | `<input id="password" type="password">`, `<button id="toggle-password" aria-pressed="false">Show</button>` |
| `style.css` | almost complete | the empty `#toggle-password { }` rule |
| `script.js` | only comments | everything |

### The plan in plain English

1. Select the input and the button.
2. On a click of the button, **ask**: is the password hidden right now (type is `'password'`)?
3. **If yes:** show it (type `'text'`), set the label to *Hide*, set `aria-pressed` to `'true'`.
4. **Otherwise:** hide it (type `'password'`), label *Show*, `aria-pressed` `'false'`.
5. CSS: padding, rounded corners, a light background and `cursor: pointer`.

:::tip Hint 1
The current state is stored in the page itself: `passwordInput.type` **is** the answer to "hidden or not?". You don't need a separate variable.
:::

:::tip Hint 2
Inside the listener: one `if (...) { 3 lines } else { 3 lines }`. The three lines change `type`, `textContent` and `aria-pressed`.
:::

:::tip Hint 3
```js title="the first branch"
passwordInput.type = 'text';
toggleBtn.textContent = 'Hide';
toggleBtn.setAttribute('aria-pressed', 'true');
```
:::

:::note Stop here and build it
Then run `npm test -- 08-show-hide-password`.
:::

### The solution, line by line

```js title="08/script.js" lines
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
```

| Lines | What they do |
|---|---|
| 1–2 | Select the input and the button. |
| 4 | Listen for clicks. The arrow function has no parameter because we don't need the event object. |
| 5 | Read the current state: hidden or visible? |
| 6–8 | It was hidden: reveal it, and make the button and its ARIA state say so. |
| 10–12 | It was visible: hide it again. |

```css title="08/style.css"
#toggle-password {
  padding: 10px 16px;
  border: 1px solid #cbd5e1;
  border-radius: 9px;
  background: #f8fafc;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
```

`font: inherit` matters: **buttons and inputs don't use the page's font by default**. Without it, the button text appears in a small system font.

:::deep Another way: the ternary operator
`condition ? a : b` means *"if condition is true, the value is `a`, otherwise `b`"*. The repository's `solution/` uses it to shrink the listener:

```js title="exercises/08-show-hide-password/solution/script.js (part)"
toggle.addEventListener('click', () => {
  const isMasked = input.type === 'password';
  input.type = isMasked ? 'text' : 'password';
  toggle.textContent = isMasked ? 'Hide' : 'Show';
  toggle.setAttribute('aria-pressed', String(isMasked));
});
```

`isMasked` is `true` or `false` (a **boolean**). `String(isMasked)` turns it into `'true'` or `'false'`. Use whichever version you can explain better; in an interview, clear beats short.
:::

### Mistakes beginners make

:::mistake One `=` inside the `if`
`if (passwordInput.type = 'password')` **sets** the type instead of comparing it, and the condition is always true. One `=` stores, three `===` compare.
:::

:::mistake Comparing with the wrong case
`'Password' === 'password'` is `false`. Strings must match exactly, letter for letter.
:::

### Interview questions

:::qa -
Q: What is the difference between `==` and `===`?
`===` (strict equality) compares value **and** type without converting anything. `==` converts types first, so `5 == '5'` and `0 == ''` are both `true`. Always use `===` unless you have a specific reason.

Q: What is the difference between a property and an attribute?
Attributes are written in the HTML (`aria-pressed="false"`) and are always strings. Properties live on the element object in JavaScript (`input.type`, `input.value`). Many attributes have a matching property; `input.value` holds what the user typed **now**, while the `value` attribute is only the starting value.

Q: What are ARIA attributes for?
They give screen readers information that plain HTML doesn't: whether a toggle is pressed (`aria-pressed`), whether a section is expanded (`aria-expanded`), and which tab is selected (`aria-selected`). Graders and interviewers like to see them kept in sync.
:::

### Practice twist

Make the button show an eye icon instead of text: `'👁'` for Show and `'🙈'` for Hide. Then add a second password field, **Confirm password**, with its own toggle. Can you write one function that works for both buttons?
