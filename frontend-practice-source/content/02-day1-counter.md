:::chapter 1 | Your First JavaScript: the Click Counter | Exercise 03 · variables · functions · click events
- **Variables:** `let` and `const`, boxes with names
- **Functions:** a recipe you write once and run many times
- The pattern behind every exercise: **select → listen → change**
- CSS: styling a second button, and **which rule wins** when two rules disagree
:::

:::day Today's plan (2 hours)
Setup should be done (Day 0). If it isn't, do it first and finish this exercise tomorrow morning.

**0–30** New ideas · **30–40** read the starter files · **40–90** build · **90–100** grade · **100–120** solution, mistakes, interview questions, twist
:::

## Exercise 03 · Click Counter

### What you are building

![The click counter before and after](content/img/03.png){.shot}

The HTML and most of the CSS are done. You make the two buttons work and give **Reset** its own look. The grader checks four things:

| Test | What it does |
|---|---|
| starts at 0 | opens the page; `#count` must show `0` |
| increments on each click | clicks **Click me** 3 times; `#count` must show `3` |
| reset returns the count to 0 | clicks twice (expects `2`), clicks **Reset**, expects `0` |
| the secondary button is visually distinct | the background of `.secondary` must **not** be the purple of the main button |

### New ideas

#### 1. Variables: boxes with names

A **variable** is a named box that holds a value. You create one with `let` or `const`:

```js title="variables"
let count = 0;
count = count + 1;
count = count + 1;
console.log(count);

const greeting = 'Hello';
console.log(greeting + ', Ada');
console.log(typeof count, typeof greeting);
```

```output
2
Hello, Ada
number string
```

- `let` makes a box whose value **can change later** (`count` goes 0 → 1 → 2).
- `const` makes a box that **can never be given a new value**. Try `greeting = 'Hi'` and you get *TypeError: Assignment to constant variable.*
- Text goes inside quotes: `'Hello'` or `"Hello"`. Text is called a **string**.
- `count = count + 1` means: *read count, add 1, put the result back in count*. The `=` sign means **"store"**, not "is equal to".

:::tip The rule you will follow all week
Use **`const` by default.** Use **`let` only for values that must change**, such as a counter or the index of the current slide. You will also see `var` in old code: it is the old way, with confusing rules. Don't use it.
:::

:::cpp C++ Corner
`let count = 0;` is like `int count = 0;`, except JavaScript has **no types in declarations**: the same variable could hold a number now and a string later. `const` works like C++ `const` for the box itself.
:::

#### 2. Functions: a recipe with a name

A **function** is a block of code with a name. Writing it does **nothing**; it runs only when it is **called**.

```js title="defining and calling a function"
function increase() {      // define: write the recipe
  count = count + 1;
}

increase();                // call: cook it once
increase();                // cook it again
```

Notice the difference between `increase` and `increase()`:

- `increase()` **with brackets** runs the function **now**.
- `increase` **without brackets** is the function **itself**, like handing someone the recipe card so they can cook it **later**. This is exactly what you give to an event listener.

#### 3. Select → listen → change

Every interactive exercise follows these three steps:

1. **Select:** find the element and keep it in a `const`.

    ```js title="select"
    const incrementBtn = document.getElementById('increment');
    ```

    You pass the id **without** `#`. You get back the element object, or `null` if no element has that id.

2. **Listen:** tell the browser *"when this happens to this element, run this function"*.

    ```js title="listen"
    incrementBtn.addEventListener('click', increase);
    ```

    `'click'` is the **event name**. `increase` (no brackets!) is the function the browser will call on every click. A function you hand over to be called later is called a **callback**.

3. **Change:** inside the function, change the page.

    ```js title="change"
    countEl.textContent = count;
    ```

    `textContent` is the text inside an element. Setting it replaces that text, and the screen updates at once. A number is turned into text automatically.

[[fig:fp-event-flow|What happens on a click. Your code runs once at page load to **select** and **listen**. After that, the browser calls your function on every click, your function **changes** the DOM, and the browser redraws.]]

#### 4. CSS: which rule wins?

Look at these two rules from this exercise:

```css title="two rules that both style the Reset button"
button:hover {            /* from the starter file */
  background: #6d28d9;
}
.secondary {              /* the rule you will write */
  background: #ffffff;
}
```

When the mouse is over Reset, both rules match and they disagree. The browser picks the **more specific** selector. Count it like a score:

| Selector contains | Points |
|---|---|
| an id (`#count`) | 100 |
| a class (`.secondary`) or a pseudo-class (`:hover`) | 10 each |
| an element name (`button`) | 1 each |

`button:hover` scores 1 + 10 = **11**. `.secondary` scores only **10**, so on hover the purple wins and Reset turns purple. The fix is a rule with a higher score: `.secondary:hover` scores **20**. If two selectors have the **same** score, the one **written later** in the file wins.

### Read the starter files

Open the three files in `exercises/03-click-counter/`.

| File | What is there | What you will use |
|---|---|---|
| `index.html` | complete | `<span id="count">0</span>`, `<button id="increment">`, `<button id="reset" class="secondary">` |
| `style.css` | almost complete; `button` makes **every** button purple | the empty rule `.secondary { }` |
| `script.js` | only `TODO` comments | everything |

### The plan in plain English

1. Select the three elements: the count text and the two buttons.
2. Make a variable `count` that starts at 0. It will change, so use `let`.
3. Write a function `increase` that adds 1 to `count` and shows the new value.
4. Write a function `reset` that sets `count` back to 0 and shows it.
5. Connect them: `increase` runs on a click of **Click me**, `reset` on a click of **Reset**.
6. In CSS, give `.secondary` a white background, grey text and a thin border, plus a hover colour.

:::tip Hint 1
You need `document.getElementById(...)` three times, once for each id in the plan. Store each result in a `const` with a clear name, for example `countEl`, `incrementBtn` and `resetBtn`.
:::

:::tip Hint 2
The shape of the file is: three selects, one `let`, two functions, two `addEventListener` lines. Each function has two lines inside: one changes `count`, the other copies `count` into `countEl.textContent`.
:::

:::tip Hint 3
```js title="the inside of increase()"
count = count + 1;
countEl.textContent = count;
```
And the connection: `incrementBtn.addEventListener('click', increase);` (no brackets after `increase`).
:::

:::note Stop here and build it
Write your code, save, refresh the page and click. Then run `npm test -- 03-click-counter`. Only after that, read on.
:::

### The solution, line by line

```js title="03/script.js" lines
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
```

| Lines | What they do |
|---|---|
| 1–3 | **Select.** Find the three elements once, at page load, and keep them in `const`s. They never change, so `const` is right, even though we will change what the elements *show*. |
| 5 | The **state** of the app: the number we are counting. `let`, because it changes. It lives **outside** the functions so it remembers its value between clicks. |
| 7–10 | `increase`: add 1, then copy the number onto the screen. Changing `count` alone would change nothing visible: the screen only changes when you set `textContent`. |
| 12–15 | `reset`: same idea with 0. |
| 17–18 | **Listen.** Hand each function to the browser. Nothing runs yet; the browser will call `increase` on every click of `#increment`. |

```css title="03/style.css"
.secondary {
  background: #ffffff;
  color: #475569;
  border: 1px solid #cbd5e1;
}

.secondary:hover {
  background: #f1f5f9;
}
```

`.secondary` beats the plain `button` rule (10 points against 1), so Reset becomes white with a grey border. Without `.secondary:hover`, the `button:hover` rule (11 points) would turn it purple under the mouse.

:::deep Another way: the repository's `solution/`
The reference solution moves the "copy count onto the screen" line into its own function and writes the listeners as **arrow functions** (you will learn these tomorrow). Both versions pass all four tests.

```js title="exercises/03-click-counter/solution/script.js (part)"
function render() {
  countEl.textContent = String(count);
}

incrementBtn.addEventListener('click', () => {
  count += 1;
  render();
});
```
`count += 1` is a short way of writing `count = count + 1`.
:::

### Mistakes beginners make

:::mistake Brackets after the function name
`incrementBtn.addEventListener('click', increase());` **calls** `increase` once, immediately, while the page loads, and hands the browser its result (`undefined`) instead of the function. The count shows 1 and clicks do nothing. Remove the brackets.
:::

:::mistake `let count = 0` inside the function
```js title="wrong"
function increase() {
  let count = 0;           // a NEW box, created on every click
  count = count + 1;
  countEl.textContent = count;
}
```
Every click creates a fresh `count` that starts at 0, so the page shows 1 forever. The state must live **outside** the function.
:::

:::mistake A `#` inside `getElementById`
`document.getElementById('#count')` returns `null` because no element has the id `#count`. The `#` belongs in CSS selectors, not in `getElementById`.
:::

### Interview questions

:::qa -
Q: What is the DOM?
The **Document Object Model**: the tree of objects the browser builds from the HTML. JavaScript reads and changes this tree, and the browser redraws the page to match. The HTML file itself never changes.

Q: What is the difference between `let`, `const` and `var`?
`const` can't be reassigned; `let` can. Both exist only inside the `{ }` block where they are declared. `var` is the old keyword: it belongs to the whole function, not the block, and can be used before its line (as `undefined`), which causes bugs. Use `const` by default and `let` when the value changes.

Q: What does `addEventListener` do?
It registers a function (a **callback**) that the browser calls whenever the named event happens on that element. You can add several listeners for the same event, which you can't do with the older `onclick = ...` property (a second assignment replaces the first).

Q: What is CSS specificity?
The rule that decides which CSS rule wins when several match the same element: ids beat classes, classes and pseudo-classes beat element names, and when the scores are equal the later rule wins.
:::

### Practice twist

Add a **−1** button. In `index.html`, add `<button id="decrement" type="button">−1</button>` next to the others; in `script.js`, select it, write `decrease()`, and connect it. Then make sure the count can **never go below 0**. (You'll need `if (count > 0) { ... }`, which you'll meet properly tomorrow. Try it anyway!)
