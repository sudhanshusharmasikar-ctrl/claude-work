:::chapter 10 | Mock Round and Revision | 60-minute timed round · three patterns · cheat sheets · interview questions
- A **mock round** under real conditions: two reported questions and one exercise you have never seen
- The **three patterns** that solve every exercise, on one page
- **Cheat sheets** for the DOM, the JavaScript you used, CSS and HTML
- A **debugging checklist** for when something doesn't work
- **Rapid-fire interview questions** to answer out loud
:::

:::day Today's plan (2 hours)
**0–10** set up a fresh copy · **10–70** mock round (timer on, no notes) · **70–85** grade and review · **85–120** revision pages and interview questions, out loud.
:::

## 10.1 The mock round

### Set up a fresh copy

Your own folder holds your finished solutions, so make a **second, untouched copy** for the mock round. In the folder **above** `accenture-frontend-practice`:

```bash title="a clean copy for the mock round"
git clone https://github.com/dexterhere04/accenture-frontend-practice.git mock-round
cd mock-round
npm install
```

The Playwright browser is already installed from Day 0, so you don't need that step again. Open `mock-round` in VS Code.

### The rules

- **60 minutes in total**, with a timer you can see.
- **No** guide, **no** `solution/` folders, **no** internet. The browser console is allowed.
- Read each `task.md` **fully** before you write anything (2 minutes well spent).
- Grade each task as soon as you finish it. In the real round, partial scores count, so a task with 4 of 5 tests passing is worth a lot.

| Task | Exercise | Time | Why |
|---|---|---|---|
| A | **05** E-commerce Search Box | 25 min | reported from the real round |
| B | **17** Live Digital Clock | 15 min | reported from the real round |
| C | **12** Progress Bar + Spinner | 20 min | **new to you**: the real round won't be an exercise you've practised |

For Task C, this card is your "documentation". Real tasks often include a hint like this.

:::def Documentation card for Task C
- `transition: width 0.4s ease;` on an element makes any later change of its `width` **animate** over 0.4 seconds instead of jumping.
- In JavaScript, `el.style.width = '100%';` sets the width directly on the element.
- A **keyframe animation** has two parts. Define the movement once, then attach it:

```css title="a continuous spin"
@keyframes spin {
  to { transform: rotate(360deg); }
}
.thing {
  animation: spin 0.8s linear infinite;   /* name, duration, speed curve, repeat */
}
```

- Give the bar `width: 0` at first, or it starts full (a `<div>` is as wide as its parent by default).
:::

### After the round

Run the grader on all three (`npm test -- 05-ecommerce`, `npm test -- 17-live`, `npm test -- 12-progress`). Then, for every test that failed or every minute you lost, write one line: *what slowed me down?* Common answers, and the fix:

| What slowed you down | Fix |
|---|---|
| Didn't know where to start | Always the same first lines: select every id the task mentions. Then the listener. Then `render()` or the toggle. |
| A typo in an id or class | Copy ids from `index.html` instead of typing them. |
| Forgot to call `render()` / `updateClock()` at load | Add it to your personal checklist: *"Does the page look right before any click?"* |
| Spent long on CSS polish | Do the JavaScript first: most tests check behaviour. Style last. |

## 10.2 The three patterns

Every exercise in this guide is one of these, built on **select → listen → change**.

:::cols
#### Pattern 1 · Toggle

One element, two states: exercises **08** and **09** (and bonus 10). The state lives in the page itself (a class, or `input.type`), and CSS decides how each state looks.
|||
#### Pattern 2 · Render from data

A list drawn from an array: exercises **05** and **15** (and bonus 19, 20). One `render()` rebuilds everything; call it at load and after every change.
|||
#### Pattern 3 · All off, one on

Many elements, one active: exercises **13**, **14** and **16**. Read the old state first if a second click should close it (13).
:::

```js title="pattern 1 · toggle"
btn.addEventListener('click', () => {
  const on = el.classList.toggle('open');
  btn.setAttribute('aria-expanded', String(on));
});
```

```js title="pattern 2 · render from data"
function render() {
  const query = input.value.trim().toLowerCase();
  const items = data.filter((item) => item.toLowerCase().includes(query));
  list.innerHTML = '';
  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    list.appendChild(li);
  });
}
input.addEventListener('input', render);
render();
```

```js title="pattern 3 · all off, one on"
items.forEach((item) => {
  item.addEventListener('click', () => {
    items.forEach((x) => x.classList.remove('active'));
    item.classList.add('active');
  });
});
```

[[pagebreak]]

## 10.3 Cheat sheets

### The DOM

| Goal | Code |
|---|---|
| one element by id | `document.getElementById('count')` (no `#`) |
| first match of a CSS selector | `document.querySelector('.tab.active')` |
| all matches | `document.querySelectorAll('.tab')` → loop with `forEach` |
| search inside an element | `item.querySelector('.icon')` |
| listen | `el.addEventListener('click', fn)` · events: `click`, `input`, `submit`, `keydown` |
| stop the default action | `event.preventDefault()` (forms, links) |
| read typed text | `input.value` |
| set text | `el.textContent = 'Hi'` |
| set HTML (trusted text only) / empty | `el.innerHTML = '<b>Hi</b>'` · `el.innerHTML = ''` |
| classes | `el.classList.add / remove / toggle / contains('x')` |
| attributes | `el.setAttribute('aria-pressed', 'true')` · `el.getAttribute('x')` |
| `data-*` | `el.dataset.tab` reads `data-tab` |
| show / hide | `el.hidden = true / false` |
| create and attach | `document.createElement('li')` → fill → `parent.appendChild(li)` |
| remove | `el.remove()` |
| count children | `list.children.length` |

### JavaScript you used

| Topic | Code |
|---|---|
| variables | `const` by default, `let` when it changes |
| compare | `===`, `!==`, `<`, `>=`; combine with `&&` (and), `||` (or), `!` (not) |
| decide | `if (...) { } else if (...) { } else { }` · `cond ? a : b` |
| functions | `function name(x) { return x; }` · `(x) => { ... }` · `(x) => x * 2` |
| strings | `.trim()` `.toLowerCase()` `.includes('a')` `.length` `.padStart(2, '0')` · `` `Hi ${name}` `` |
| numbers | `Number('2')` · `String(7)` · `a % b` (remainder) |
| arrays | `.length` `[0]` `.forEach(fn)` `.filter(fn)` `.map(fn)` `.sort((a, b) => a - b)` |
| objects | `{ name: 'Ada', age: 36 }` · `emp.name` |
| time | `new Date()` · `.getHours()` · `setInterval(fn, 1000)` · `setTimeout(fn, ms)` |
| regex | `/^\S+@\S+\.\S+$/.test(text)` |

### CSS

| Goal | Code |
|---|---|
| select | `tag` · `.class` · `#id` · `.a .b` (b inside a) · `.a.b` (both) · `:hover` `:focus` · `[data-x="y"]` |
| who wins | id 100 · class / pseudo-class 10 · tag 1; equal → the later rule |
| box | `padding` (inside) · `border` · `margin` (outside) · `box-sizing: border-box` |
| row | `display: flex; gap; justify-content; align-items` |
| grid | `display: grid; place-items: center` · `grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))` |
| center | flex: `justify-content: center; align-items: center` · grid: `place-items: center` · absolute: `top/left: 50%; transform: translate(-50%, -50%)` |
| hide | `display: none` (no space) · `visibility: hidden` (keeps space) |
| looks | `border-radius` · `box-shadow: 0 10px 30px rgba(0,0,0,.12)` · `cursor: pointer` · `font: inherit` |
| variables | `:root { --bg: #fff; }` · `background: var(--bg)` |
| motion | `transition: transform 0.2s` · `@keyframes` + `animation` |
| responsive | `@media (max-width: 600px) { ... }` |

### HTML

| Element / attribute | Use |
|---|---|
| `<label for="id">` | names an input; `for` = the input's `id` |
| `<input type="email / tel / password / text">` | the right keyboard, check or masking |
| `required` | a boolean attribute: write the bare word |
| `<fieldset>` + `<legend>` | group related fields with a title |
| `<button type="button">` | a normal button; inside a form, the default type is `submit` |
| `aria-pressed`, `aria-expanded`, `aria-selected` | tell screen readers the state; keep them in sync |
| `data-*` | your own information on an element |
| `<script src>` before `</body>` | the elements exist when the script runs |

## 10.4 When something doesn't work

Go through this list **in order**. Most problems are found by step 3.

1. **Open the console (F12).** Is there red text? Read it: it gives the file and line.
2. **`Cannot read properties of null`:** a `getElementById` / `querySelector` found nothing. Check the spelling against `index.html`, and remember: no `#` in `getElementById`, a `#` or `.` **is** needed in `querySelector`.
3. **A click does nothing and there's no error:** put `console.log('clicked')` as the first line of the listener. Nothing printed? The listener isn't attached (wrong element, or brackets after the function name). Printed? The problem is inside the listener: log the values you use.
4. **Works once, then goes wrong:** state isn't stored (Day 8's `index`), a list isn't cleared before redrawing (Day 4), or an old message isn't cleared (Day 6).
5. **CSS has no effect:** a typo in the selector, a missing `;` on the line above, or a more specific rule winning. Right-click the element → **Inspect**: the **Styles** panel shows which rules apply and crosses out the ones that lose.
6. **The page looks right but a test fails:** read *Expected* / *Received* and the locator. The grader looks for **exact** ids, classes and attribute values (`'true'`, not `true` in some other place; `completed` on the `<li>`, not the `<span>`).

## 10.5 Rapid-fire interview questions

Cover the answers, say yours out loud in under 30 seconds, then check.

:::qa -
Q: What happens when the browser loads a page?
It reads the HTML from top to bottom and builds the DOM, loads the CSS to style it, runs each `<script>` when it reaches it, and draws the page. Afterwards, JavaScript reacts to events and changes the DOM, and the browser redraws.

Q: What is the DOM?
The tree of objects the browser builds from the HTML, which JavaScript reads and changes.

Q: `let`, `const`, `var`?
`const` can't be reassigned, `let` can; both are block-scoped. `var` is function-scoped and hoisted. Prefer `const`, then `let`.

Q: `==` versus `===`?
`===` compares without converting types; `==` converts first (`5 == '5'` is `true`). Use `===`.

Q: `textContent` versus `innerHTML`?
`textContent` sets plain text; `innerHTML` parses HTML, which is a security risk (XSS) with user input.

Q: What is an event listener? What is a callback?
`addEventListener(type, fn)` registers `fn` to be called when the event happens. A callback is a function you pass to be called later, like `fn` here or the function given to `setInterval`.

Q: What does `preventDefault()` do?
Cancels the browser's default action: a form submit's page reload, a link's navigation.

Q: What is event bubbling, and what is event delegation?
An event on an element also fires on each of its ancestors, up to the document (**bubbling**). **Delegation** uses this: one listener on a parent handles events from many children, using `event.target` to see which child was clicked. Useful for long or changing lists.

Q: What is a closure?
A function that remembers variables from where it was created, like each to-do's Delete listener remembering its `li`.

Q: `forEach`, `map`, `filter`?
`forEach` runs a function per item and returns nothing; `map` returns a new array of transformed items; `filter` returns a new array of the items that pass a test.

Q: Why does `[10, 9, 1].sort()` give `[1, 10, 9]`?
Without a compare function, items are compared as strings. Use `(a, b) => a - b`.

Q: `setTimeout` versus `setInterval`?
Once after a delay, versus repeatedly. Both can be cancelled with their id.

Q: What is the box model?
Content, padding, border, margin; `box-sizing: border-box` makes `width` include padding and border.

Q: Flexbox or grid?
Flexbox for one direction (a row or a column), grid for two (rows and columns).

Q: How do you center a div?
`display: flex; justify-content: center; align-items: center;` on the parent, or `display: grid; place-items: center;`.

Q: `display: none` versus `visibility: hidden`?
`none` removes it from the layout; `hidden` hides it but keeps its space.

Q: What is CSS specificity?
The scoring that decides which rule wins: ids > classes and pseudo-classes > elements; ties go to the later rule.

Q: What are CSS variables?
Custom properties (`--bg`) read with `var(--bg)`. They inherit and can be overridden per element or class, which is ideal for themes.

Q: What is semantic HTML, and what is ARIA?
Semantic HTML uses elements for their meaning (`button`, `label`, `nav`). ARIA attributes add information screen readers can't get from HTML alone, such as `aria-expanded`.

Q: What is `localStorage`?
A small key-value store in the browser that survives reloads. Values are strings, so objects are saved with `JSON.stringify` and read back with `JSON.parse`. (Bonus 19.)

Q: What is `fetch`, and what do `async` / `await` do?
`fetch(url)` requests data and returns a **Promise**. `await` pauses an `async` function until the Promise settles, so asynchronous code reads like normal code; wrap it in `try` / `catch` to handle errors. (Bonus 18; Chapters 5 and 7 of your JavaScript notes.)

Q: Walk me through your search box.
Select the input, list, count and empty message. One `render()` function lower-cases the query, filters the products with `includes`, clears the list, creates an `<li>` per match, updates the count and shows the empty message when nothing matches. It runs at load and on every `input` event.
:::

## 10.6 After Day 10

You have done 14 exercises, each with tests passing. To keep it fresh until the assessment:

- **Every other day:** redo one exercise from a fresh copy, timed. Rotate through 05, 17, 06, 15, 13.
- **The six bonus exercises** in the next chapter, in the order given. Each one adds one new idea to what you know.
- Before the real round, read 10.2 and 10.4 again. They fit on two pages for a reason.
