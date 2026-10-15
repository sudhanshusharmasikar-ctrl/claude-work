:::chapter Bonus | The Other Six Exercises | After Day 10 · one new idea each
- **10** Responsive Navbar: media queries
- **11** Responsive Card Grid: `auto-fill` and `minmax`, hover lifts
- **12** Progress Bar + Spinner: transitions and `@keyframes` (your mock-round Task C)
- **19** Persistent Notes: saving to `localStorage` with JSON
- **20** Quiz: several pieces of state and step-by-step screens
- **18** Fetch & Render: loading data with `fetch`, `async` / `await` and errors
:::

Each of these adds **one** idea to what you already know. They're in the order to do them. For each one: what's new, the plan, and the hint that unlocks it. There's no line-by-line solution here; when you're done, compare with the exercise's `solution/` folder, which passes all its tests.

## Exercise 10 · Responsive Navbar

**Pattern:** toggle (Day 2 and 5), plus **media queries**.

A **media query** applies CSS only when a condition is true, usually the screen width:

```css title="from exercises/10-responsive-navbar/solution/style.css (part)"
@media (max-width: 600px) {
  .nav-toggle {
    display: inline-block;
  }

  .nav-links {
    display: none;
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }

  .nav-links.open {
    display: flex;
  }
}
```

**Plan:** on desktop, `.nav-links` is a flex row and `.nav-toggle` has `display: none`. Inside the media query: show the toggle, hide the links, and show them as a **column** when they have the class `open`. The JavaScript is Exercise 09 again: toggle `open` on `#nav-links` and keep `aria-expanded` in sync.

**Hint:** test it by making the browser window narrow, or open DevTools (F12) and click the phone icon (**device toolbar**) to choose a width.

## Exercise 11 · Responsive Card Grid

**Pattern:** CSS only. **New:** a grid that picks its own number of columns.

```css title="from exercises/11-responsive-card-grid/solution/style.css (part)"
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
```

Read it as: *"make as many columns as fit (`auto-fill`), each at least 220px and at most an equal share of the space (`minmax(220px, 1fr)`)."* On a wide screen that's 4 or 5 columns, on a phone 1, with **no media query**. `1fr` means *one fraction of the free space*.

**Plan:** the grid rule above; on `.card`, a background, padding, radius, shadow and `transition: transform 0.18s ease, box-shadow 0.18s ease;`; on `.card:hover`, `transform: translateY(-4px)` and a stronger shadow.

**Hint:** `transition` goes on the **normal** state (`.card`), not on `:hover`, so the card animates both up and back down.

## Exercise 12 · Progress Bar + Spinner

**Pattern:** toggle-like (one click, three changes). **New:** `transition`, `@keyframes`, `el.style`.

You met this in the mock round with the documentation card (10.1). If it didn't pass then, do it now: `.progress-bar` gets `height: 100%`, `width: 0`, a colour and `transition: width 0.4s ease`; `.spinner` gets `animation: spin 0.8s linear infinite`; define `@keyframes spin { to { transform: rotate(360deg); } }`. On click of `#start`: `bar.style.width = '100%'`, the label `'100%'`, and `setAttribute('aria-valuenow', '100')` on the `.progress` track.

## Exercise 19 · Persistent Notes

**Pattern:** render from data (Day 4), with the data in an **array you change**. **New:** `localStorage` and JSON.

`localStorage` is a small store in the browser that **survives a reload**. It only stores **strings**, so an array of objects is turned into a string (**JSON**) to save it and parsed back to load it:

```js title="from exercises/19-persistent-todo/solution/script.js (part)"
function loadNotes() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (error) {
    return [];
  }
}

function saveNotes() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
}
```

`STORAGE_KEY` is a `const` at the top of the file: `'accenture-notes'`, the name the data is saved under. `getItem` returns `null` the first time (nothing saved yet), hence `raw ? ... : []`. The `try` / `catch` handles the rare case of broken saved data.

**Plan:**

1. `let notes = loadNotes();`, an array of `{ id, text }`.
2. `render()`: clear the list; for each note, create `<li class="note">` with a `<span>` and a `<button class="note-delete">`; hide or show `#empty`.
3. **Add:** on submit, guard against empty text, ``notes.push({ id: `${Date.now()}-${Math.random()}`, text })`` (the time plus a random number, so two notes never share an id), `saveNotes()`, clear the input, `render()`.
4. **Delete:** `notes = notes.filter((n) => n.id !== note.id)`, then save and render.
5. **Clear all:** `notes = []`, save, render. And call `render()` once at load.

**Hint:** the rule is **change the array → save → render**, every time. Unlike Exercise 06, you never remove an `<li>` directly; the array is the truth and the page is redrawn from it. Open DevTools → **Application** → **Local Storage** to watch the saved string change.

## Exercise 20 · Quiz

**Pattern:** render from data, with **three pieces of state**: which question (`current`), the `score`, and which option is `selected`.

**Plan:**

1. `let current = 0; let score = 0; let selected = null;`
2. `renderQuestion()`: reset `selected` to `null` and disable Next (`nextBtn.disabled = true`); show `Question ${current + 1} of ${questions.length}` and the question text; clear `#options`; create a `<button class="option">` per option. Each option's click sets `selected` to its index, gives **only** that button the class `selected` (all off, one on!), and sets `nextBtn.disabled = false`.
3. **Next:** if `selected === questions[current].answer`, add 1 to `score`. Then `current += 1`; if there's another question, `renderQuestion()`, otherwise `showScore()`.
4. `showScore()`: `quizEl.hidden = true; scoreEl.hidden = false;` and the text `You scored ${score} / ${questions.length}`.

**Hint:** `forEach((option, index) => ...)` gives you the **position** as the second argument; that's the number to compare with `answer`.

## Exercise 18 · Fetch & Render

**Pattern:** render from data, where the data arrives **later**, from a file. **New:** `fetch`, `async` / `await`, `try` / `catch`. Chapters 5 and 7 of your JavaScript notes explain Promises and `async` / `await` in depth.

```js title="from exercises/18-fetch-and-render/solution/script.js (shortened)"
try {
  const response = await fetch('./data.json');
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  const users = await response.json();
  // ... create one <li class="user"> per user
  statusEl.textContent = '';
} catch (error) {
  statusEl.textContent = 'Something went wrong while loading users.';
}
```

- `fetch` returns a **Promise**: a value that arrives later. `await` waits for it, and only works inside a function marked `async`.
- `fetch` doesn't fail on a 404 or 500 error. Check `response.ok` and `throw` yourself, so the `catch` shows the error message. The grader tests exactly this by making the server answer 500.
- Show `Loading...` in `#status` **before** the `fetch`, and clear it after rendering.

:::mistake Opening exercise 18 by double-clicking `index.html`
Browsers block `fetch` from pages opened as files. We tried it: the console says *Access to fetch at 'file:///…/data.json' from origin 'null' has been blocked by CORS policy*, and the page shows the error message. Run `npm run dashboard` and open the exercise through **http://localhost:4173** instead. (The grader uses its own server, so the tests work either way.)
:::
