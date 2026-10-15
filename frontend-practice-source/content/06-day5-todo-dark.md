:::chapter 5 | Building Elements and Switching Classes | Exercise 06 To-Do List · Exercise 09 Dark Mode
- Building an element **with children**: an `<li>` with a text and two buttons
- **`classList`**: `add`, `remove`, `toggle` and `contains`
- Removing an element with **`remove()`**
- Leaving a function early with **`return`**
- Why each Delete button deletes **its own** item: **closures**
- **CSS variables** and a whole dark theme from one class
:::

:::day Today's plan (2 hours)
**Exercise 06** (75 min): new ideas 20 · build 40 · grade and review 15. **Exercise 09** (45 min): new ideas 10 · build 20 · grade and review 15.
:::

## Exercise 06 · To-Do List

### What you are building

![The to-do list before and after](content/img/06.png){.shot}

Type a task and press **Add** (or Enter): it appears in the list with a **Done** button (crosses it out) and a **Delete** button (removes it). A message shows while the list is empty. The grader checks:

| Test | What it does | Expects |
|---|---|---|
| shows the empty message until a task is added | adds *Buy milk* | `#empty` visible before, hidden after; 1 `.todo-item` containing *Buy milk* |
| ignores empty submissions | submits three spaces | 0 items |
| toggling marks a task as completed | clicks the item's `.todo-toggle` | the `<li>` has class `completed` |
| deleting removes the task | adds two, deletes the first | 1 item left, containing *Task two* |
| empty message returns when all tasks are deleted | adds one, deletes it | `#empty` visible |

### New ideas

#### 1. An element with children

Yesterday each `<li>` held only text. Today each one holds **three children**, so you create four elements and put three inside the fourth:

[[fig:fp-todo-item|One to-do item. `createTodo()` builds the `<li>` and its three children, then hands the `<li>` back. Each button's listener remembers **this** `<li>`.]]

```js title="children go in before the parent goes on the page"
const li = document.createElement('li');
const span = document.createElement('span');
span.textContent = 'Buy milk';
li.appendChild(span);            // span goes inside li
list.appendChild(li);            // li goes inside the list: now visible
```

#### 2. `classList`

Changing classes is how JavaScript and CSS work together: **JavaScript decides the state, CSS decides how each state looks**.

| Code | Does |
|---|---|
| `el.classList.add('completed')` | adds the class (nothing happens if it's already there) |
| `el.classList.remove('completed')` | removes it |
| `el.classList.toggle('completed')` | adds it if missing, removes it if present |
| `el.classList.contains('completed')` | `true` or `false`: is it there? |

`classList` changes **one** class and leaves the others alone. `el.className = 'x'` replaces **all** of them, which is fine for a new element but dangerous for an existing one.

#### 3. `remove()` and counting children

`li.remove()` takes the element off the page. `list.children.length` counts the elements currently inside the list, which tells you if it's empty.

#### 4. Leaving early with `return`

```js title="a guard at the top of the handler"
const text = input.value.trim();
if (text === '') {
  return;          // stop here: nothing to add
}
// ... only runs when there is text
```

`return` ends the function immediately. Checking for bad input at the top and returning is called a **guard**, and it keeps the rest of the function simple.

#### 5. Functions that give something back

`createTodo(text)` will **build** an item and `return` it, without putting it on the page. The caller decides where it goes: `list.appendChild(createTodo(text))`. Building and placing are separate jobs.

#### 6. Closures: each button remembers its own item

Inside `createTodo`, the listener for the Delete button uses the variable `li`. Every call of `createTodo` makes a **new** `li`, and each listener **remembers the `li` that existed when it was created**, even after `createTodo` has finished. That's why Delete on the third item deletes the third item, with no ids and no searching. A function that remembers variables from where it was written is called a **closure**.

### Read the starter files

| File | What is there | What you will use |
|---|---|---|
| `index.html` | complete | `form#todo-form`, `input#todo-input`, `ul#todo-list`, `p#empty` (visible) |
| `style.css` | four empty rules | `.todo-item`, `.todo-item.completed .todo-text`, `.todo-toggle`, `.todo-delete` |
| `script.js` | comments only | everything |

The class names the grader looks for are **`todo-item`**, **`todo-text`**, **`todo-toggle`** and **`todo-delete`**. Spell them exactly.

### The plan in plain English

1. Select the form, the input, the list and the empty message.
2. Write `updateEmpty()`: hide `#empty` when the list has children, show it otherwise.
3. Write `createTodo(text)` that builds and returns:
    - an `<li class="todo-item">` containing
    - a `<span class="todo-text">` with the text,
    - a `<button class="todo-toggle">Done</button>` whose click toggles `completed` on the `<li>`,
    - a `<button class="todo-delete">Delete</button>` whose click removes the `<li>` and calls `updateEmpty()`.
4. On the form's `submit`: prevent the reload; trim the text; **return** if it's empty; append `createTodo(text)` to the list; clear the input; `updateEmpty()`.
5. CSS: the item is a flex row with a light background; `.completed .todo-text` is crossed out and grey; the buttons get two different colours.

:::tip Hint 1
Get the **add** part working first, with only the `<span>` inside the `<li>`. Add the buttons once you see items appear.
:::

:::tip Hint 2
Give the new buttons `type = 'button'`. A `<button>` inside a form is a **submit** button by default, so without it, clicking Done would also submit the form.
:::

:::tip Hint 3
```js title="the Delete button's listener"
deleteBtn.addEventListener('click', () => {
  li.remove();
  updateEmpty();
});
```
:::

:::note Stop here and build it
Then run `npm test -- 06-todo-list`.
:::

### The solution, line by line

```js title="06/script.js" lines
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
```

| Lines | What they do |
|---|---|
| 6–8 | One small function for the empty message, used in two places (after adding and after deleting). |
| 10–39 | `createTodo` builds one complete item and returns it. Nothing appears on screen until line 49. |
| 22–24 | **Done:** toggles `completed` on the `<li>`. CSS turns that class into a line-through. |
| 30–33 | **Delete:** removes this `<li>` (the closure) and updates the empty message. |
| 41–52 | **Submit:** cancel the reload, read and trim, guard against empty text, add the item, clear the input, update the message. |
| 54 | Set the message correctly at load. |

```css title="06/style.css"
.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 9px;
}

.todo-item.completed .todo-text {
  text-decoration: line-through;
  color: #94a3b8;
}
```

Read the second selector from right to left: *"a `.todo-text` that is inside a `.todo-item` which **also** has the class `completed`"*. JavaScript only adds a class to the `<li>`; this selector reaches down to the text. (The two button rules just set `background` and `color`.)

### Mistakes beginners make

:::mistake Toggling the class on the wrong element
If you toggle `completed` on the `<span>`, the selector `.todo-item.completed .todo-text` no longer matches, and the grader, which looks for the class on the **`<li>`**, fails. Read the task: *"toggles a `completed` class on the `<li>`"*.
:::

:::mistake Selecting the item with `getElementById` inside the listener
Ids must be unique, and you'd need a new id for every item. The closure already gives you the right `li`; use it.
:::

:::mistake Forgetting `updateEmpty()` after a delete
The grader's last test deletes the only task and expects the empty message back. Every place that changes the list must update the message.
:::

### Interview questions

:::qa -
Q: What is a closure? Give an example from your code.
A function that remembers the variables of the place where it was created. In the to-do list, each Delete button's listener remembers the `li` created in the same `createTodo` call, so it always removes its own item.

Q: What is the difference between `classList.toggle` and `className`?
`classList` adds, removes or toggles **one** class and keeps the others. Assigning `className` replaces the entire class list.

Q: How would you handle clicks if there were 1,000 items?
**Event delegation:** one listener on the `<ul>` instead of two per item. Clicks bubble up from the button to the list; in the listener, `event.target` is the element that was clicked, and `event.target.closest('li')` finds its item.

Q: Why `type="button"` on buttons created inside a form?
A `<button>` in a form defaults to `type="submit"`, so clicking it would submit the form. `type="button"` makes it an ordinary button.
:::

### Practice twist

Show the number of tasks still to do above the list: *2 tasks left*. Hint: `list.querySelectorAll('.todo-item:not(.completed)').length`. Update it everywhere you call `updateEmpty()`.

## Exercise 09 · Dark-Mode Toggle

### What you are building

![The dark-mode toggle before and after](content/img/09.png){.shot}

One button switches the whole page between light and dark. The grader checks that the page starts light (`body` has no `dark` class, `aria-pressed="false"`), that one click adds `dark` to `<body>`, sets `aria-pressed="true"` and **changes the background colour**, and that a second click undoes all three.

### New ideas

#### 1. CSS variables

The starter CSS doesn't write colours directly. It defines them **once** as **custom properties** on `:root` (the `<html>` element) and uses them with `var()`:

```css title="from the starter style.css"
:root {
  --bg: #f8fafc;
  --text: #0f172a;
}

body {
  background: var(--bg);
  color: var(--text);
}
```

A custom property's name starts with two dashes. Like `color` or `font`, it is **inherited**: every element inside reads the value from its closest ancestor that sets it.

#### 2. A theme is just new values for the same variables

[[fig:fp-css-vars|`:root` sets the light values. When `<body>` gets the class `dark`, the rule `body.dark` sets **new values** for the same variables. Everything inside `<body>` uses the closer, dark values, so the whole page changes from one class.]]

So the CSS job is **one rule**, `body.dark { ... }`, giving each variable a dark value. And the JavaScript job is **one line**, adding or removing the class.

#### 3. `toggle` tells you what it did

`document.body` is the `<body>` element (no need to select it). `classList.toggle('dark')` adds or removes the class, and **returns** `true` if the class is now present, `false` if not. You can also ask afterwards with `classList.contains('dark')`.

### The plan in plain English

1. CSS: in `body.dark { }`, give `--bg`, `--surface`, `--text`, `--muted` and `--border` dark-theme values (dark backgrounds, light text).
2. CSS: style `#theme-toggle` as a real button.
3. JS: on click of `#theme-toggle`, toggle `dark` on `document.body`; then set `aria-pressed` to `'true'` or `'false'`, and change the label to *Light mode* / *Dark mode*.

:::tip Hint
`setAttribute` needs a string. `String(true)` is `'true'`.
:::

:::note Stop here and build it
Then run `npm test -- 09-dark-mode-toggle`.
:::

### The solution, line by line

```css title="09/style.css"
body.dark {
  --bg: #0f172a;
  --surface: #1e293b;
  --text: #f8fafc;
  --muted: #94a3b8;
  --border: #334155;
}
```

```js title="09/script.js" lines
const themeBtn = document.getElementById('theme-toggle');

themeBtn.addEventListener('click', () => {
  document.body.classList.toggle('dark');

  const isDark = document.body.classList.contains('dark');
  themeBtn.setAttribute('aria-pressed', String(isDark));
  themeBtn.textContent = isDark ? 'Light mode' : 'Dark mode';
});
```

| Lines | What they do |
|---|---|
| 4 | Switch the theme. CSS does the rest through the variables. |
| 6 | Ask the page which state we're in now. |
| 7 | Keep the ARIA state in sync: `'true'` when dark. |
| 8 | The button offers the **other** mode. |

The repository's `solution/` saves one line by using the value `toggle` returns: `const isDark = document.body.classList.toggle('dark');`.

### Mistakes beginners make

:::mistake Writing `.dark` instead of `body.dark`
`.dark { ... }` would also work here, but the task asks for `body.dark`. Read the selector you're given and keep it.
:::

:::mistake Changing colours one by one in JavaScript
`document.body.style.background = '#0f172a'` for every element is long, easy to get wrong, and hard to undo. Toggle a class and let CSS hold the colours.
:::

### Interview questions

:::qa -
Q: What are CSS custom properties, and why use them for themes?
Variables in CSS (`--name: value;`, read with `var(--name)`). They are inherited and can be changed per element or class, so a theme only overrides the variables and every rule that uses them updates at once.

Q: How would you remember the user's choice after a page reload?
Save it with `localStorage.setItem('theme', 'dark')` when it changes, and on page load read `localStorage.getItem('theme')` and add the class if it says `dark`. (Bonus exercise 19 practises `localStorage`.)
:::

### Practice twist

Start in dark mode when the user's computer is set to dark: `window.matchMedia('(prefers-color-scheme: dark)').matches` is `true` in that case. Remember to set `aria-pressed` and the label correctly at load too.
