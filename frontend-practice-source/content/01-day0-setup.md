:::chapter 0 | Start Here: Setup and the Big Picture | 45 minutes, the evening before Day 1
- What the Accenture frontend task looks like
- **Installing the tools** and getting the 20 exercises onto your laptop
- Opening an exercise in the browser, and running the **grader**
- How a web page works: **HTML, CSS and JavaScript** in one picture
- The **DOM**: the page as a tree that JavaScript can change
- The browser **console**, your best friend for finding mistakes
:::

## 0.1 What the real task looks like

From the candidate reports collected in the repository's README:

- The coding round is about **60 minutes for 3 tasks** (SQL, backend and frontend). The frontend task is the **easy** one.
- You do **not** start from an empty file. You get an `index.html`, a `style.css` and a `script.js` that already exist, and you **change** them: *"Task 1: Modify the HTML file. Task 2: Make changes in the CSS file. Task 3: Update logic in the JavaScript file."*
- What it tests: **finding elements on the page, reacting to clicks and typing, and changing what the page shows**. No React, no frameworks. Plain JavaScript.

Every exercise in this repository is built the same way, so practising here is practising the real thing.

## 0.2 Install the tools

You need three programs. All are free.

| Tool | What it is for | Where to get it |
|---|---|---|
| **Node.js** (the LTS version) | runs the grader; also gives you `npm` | nodejs.org |
| **VS Code** | the editor you write code in | code.visualstudio.com |
| **Git** | downloads the exercises | git-scm.com (on Windows, keep the default options; it also installs **Git Bash**) |

After installing, open a terminal (on Windows: **Git Bash** or **PowerShell**; on a Mac: **Terminal**) and check:

```bash title="check that the tools are installed"
node --version
npm --version
git --version
```

Each command should print a version number, such as `v22.x.x`. If one says *command not found*, close the terminal, open a new one and try again. If it still fails, install that tool again.

## 0.3 Get the exercises

Pick a folder for your work (for example `Documents`), then run these four commands one by one:

```bash title="download the exercises and install the grader"
git clone https://github.com/dexterhere04/accenture-frontend-practice.git
cd accenture-frontend-practice
npm install
npx playwright install chromium
```

What each one does:

1. `git clone` downloads the repository into a new folder.
2. `cd` (*change directory*) moves the terminal into that folder.
3. `npm install` downloads **Playwright**, the tool that tests your pages.
4. `npx playwright install chromium` downloads the browser Playwright uses. It is more than 100 MB, so wait for it to finish.

Now open the folder in VS Code (**File → Open Folder…**). You will see `exercises/` with 20 folders. Each one has:

| File | What it is |
|---|---|
| `task.md` | the question, written like the real assessment |
| `index.html`, `style.css`, `script.js` | **your** files, with `TODO` comments where you must write code |
| `test.spec.js` | the grader for this exercise (read it, don't change it) |
| `solution/` | the reference answer (don't open it before you've tried!) |

:::tip Save your progress with Git (optional, but useful)
After finishing an exercise, run `git add -A` and then `git commit -m "Finish exercise 03"`. Git keeps a copy of every finished version, so you can never lose working code.
:::

## 0.4 Open an exercise in the browser

There are two easy ways:

- **Double-click** `exercises/03-click-counter/index.html` in your file explorer. It opens in your browser. This works for all 14 exercises in this guide.
- Or run `npm run dashboard` in the terminal and open **http://localhost:4173**. You get a page listing all 20 exercises with links. Stop the server with **Ctrl + C**.

After you change a file, **save it** (Ctrl + S) and **refresh** the browser (F5). The browser does not notice changes on its own.

## 0.5 Run the grader

The grader opens your page in a hidden browser, clicks and types like a user, and checks the result. Run it from the repository folder:

```bash title="grade one exercise"
npm test -- 03-click-counter
```

The part after `--` is the exercise folder's name. You can type just the start of it, but make sure it matches only one folder. Here is the **real** output for the untouched starter files of exercise 03 (lines shortened to fit the page):

```output title="npm test -- 03-click-counter, before writing any code"
Running 4 tests using 2 workers

  ✓  1 … › starts at 0 (259ms)
  ✘  2 … › increments on each click (5.5s)
  ✘  3 … › reset returns the count to 0 (5.3s)
  ✘  4 … › the secondary button is visually distinct (291ms)

  1) … › increments on each click

    Error: expect(locator).toHaveText(expected) failed

    Locator:  locator('#count')
    Expected: "3"                      #> the test clicked 3 times
    Received: "0"                      #> but the page still shows 0
```

How to read it:

- **✓** means a check passed, **✘** means it failed. The first test passes already because the HTML shows `0` before you write any code.
- For each failure, Playwright tells you **which element** it looked at (`#count`), what it **expected** and what it **received**. That is usually enough to know what to fix.

After you finish the exercise, the same command prints:

```output title="npm test -- 03-click-counter, after the solution"
  ✓  1 … › starts at 0 (329ms)
  ✓  2 … › increments on each click (401ms)
  ✓  3 … › reset returns the count to 0 (343ms)
  ✓  4 … › the secondary button is visually distinct (191ms)

  4 passed (1.7s)
```

:::mistake Windows: `npm run test:solutions` does not work in PowerShell or cmd
That script starts with `SOLUTION=1`, which only works in Git Bash, macOS and Linux. To see the reference solution pass on Windows, either use **Git Bash**, or in **PowerShell** type:

`$env:SOLUTION="1"; npx playwright test 03-click-counter; Remove-Item Env:SOLUTION`

You will rarely need this. It is only a way to check that the grader itself works.
:::

## 0.6 How a web page works: three files, three jobs

[[fig:fp-three-files|`index.html` says **what is on the page**, `style.css` says **how it looks**, and `script.js` says **what happens** when the user does something. The HTML file links the other two.]]

Think of a page as a person: **HTML** is the skeleton, **CSS** is the clothes, and **JavaScript** is the muscles that move. Let's read one line of each.

### HTML: elements

```html title="one HTML element"
<button id="increment" class="primary" type="button">Click me</button>
```

| Piece | Name | Meaning |
|---|---|---|
| `<button>` … `</button>` | **opening and closing tag** | this is a button; everything between the tags is inside it |
| `id="increment"` | **attribute** `id` | a unique name. **Only one** element on the page may use it. |
| `class="primary"` | **attribute** `class` | a group name. **Many** elements can share a class, and one element can have several, separated by spaces: `class="tab active"` |
| `type="button"` | **attribute** `type` | what kind of button |
| `Click me` | **content** | the text the user sees |

Elements live **inside** other elements, like boxes inside boxes. A `<section>` can hold an `<h1>`, a `<p>` and a `<div>`; the `<div>` can hold two buttons. Some elements have **no closing tag** because they can't contain anything, for example `<input />` and `<img />`.

### CSS: rules

```css title="one CSS rule"
.secondary {
  background: #ffffff;
  border: 1px solid #cbd5e1;
}
```

A rule is a **selector** (which elements?) followed by `{ property: value; }` pairs (how should they look?). The selectors you will use most:

| Selector | Selects | Example |
|---|---|---|
| `button` | every `<button>` | `button { cursor: pointer; }` |
| `.secondary` | every element with **class** `secondary` (note the dot) | |
| `#count` | the element with **id** `count` (note the hash) | |
| `.card h1` | every `<h1>` **inside** an element with class `card` (space = inside) | |
| `.tab.active` | elements that have **both** classes (no space) | |
| `button:hover` | a button **while the mouse is over it** | |

### JavaScript: statements

```js title="one line of JavaScript"
document.getElementById('count').textContent = 5;
```

Read it from left to right: *"In the page (`document`), get the element whose id is `count`, and set its text to 5."* The page now shows 5. That one line is what every exercise is about: **find something on the page, then change it**.

## 0.7 The DOM: the page as a tree

When the browser reads `index.html`, it builds a tree of objects in memory, one object per element. This tree is called the **DOM** (Document Object Model). JavaScript never edits the HTML file; it edits the **DOM**, and the browser redraws the page immediately.

[[fig:fp-dom-tree|The click counter's HTML (left) becomes a tree of objects (right). `getElementById('count')` hands your code the `<span>` object; changing its `textContent` changes what the user sees.]]

:::analogy The DOM is a live puppet
The HTML file is the **instruction sheet** for building the puppet. Once it is built, JavaScript holds the strings: pull one (`textContent = 5`) and the puppet moves right away. Nobody rewrites the instruction sheet.
:::

## 0.8 The browser console: where you test and debug

Open any page in Chrome or Edge and press **F12** (on a Mac: **Cmd + Option + J**). Click the **Console** tab. Two uses:

**1. Try code.** Type a line and press Enter. The answer appears below it.

```js title="type these into the console of the click-counter page"
2 + 3
document.getElementById('count')
document.getElementById('count').textContent = 99
```

The third line changes the page right in front of you. **Every small example in this guide can be typed into the console like this.**

**2. See what your code is doing.** Put `console.log(...)` in `script.js` to print a value:

```js title="printing from your script"
console.log('script loaded');
console.log('count is now', count);
```

If something doesn't work, open the console first. **Red text is an error message**, with the file and line number. This is the one you will meet most:

```output title="the most common beginner error"
Uncaught TypeError: Cannot read properties of null (reading 'addEventListener')
    at script.js:5:13                 #> file : line : column
```

It means `getElementById` returned **`null`**: no element has that id. Almost always the id is misspelled (`'Count'` instead of `'count'`, or `'#count'` with a hash). Compare it letter by letter with `index.html`.

:::tip Why the `<script>` tag is at the bottom
Every exercise puts `<script src="script.js"></script>` **just before `</body>`**. The browser reads HTML from top to bottom, so by the time it runs your script, every element above already exists and `getElementById` can find it. If the script were at the top, the elements wouldn't exist yet and you'd get the `null` error above.
:::

## 0.9 The six moves you will use in every exercise

You don't need to learn all of JavaScript. These six moves solve every exercise in this guide. Each one is explained properly on the day you first need it.

| # | Move | Code | First used |
|---|---|---|---|
| 1 | **Select** an element | `document.getElementById('count')`, `document.querySelectorAll('.tab')` | Day 1 |
| 2 | **Listen** for something | `button.addEventListener('click', () => { ... })` | Day 1 |
| 3 | **Read** what the user typed | `input.value` | Day 2 |
| 4 | **Change** the page | `el.textContent = ...`, `el.classList.add('open')`, `el.hidden = true` | Day 1 |
| 5 | **Create** new elements | `document.createElement('li')`, `list.appendChild(li)` | Day 4 |
| 6 | **Loop** over a list | `array.forEach(...)`, `array.filter(...)` | Day 4 |

:::quiz Day 0 check
1. Which file decides **what happens** when a button is clicked?
2. What is the difference between `id` and `class`?
3. In CSS, what does `.card h1` select? And `#count`?
4. You see `Cannot read properties of null (reading 'addEventListener')`. What do you check first?
5. You changed `script.js` but the browser shows the old behaviour. What did you forget?
:::

:::answer
1. `script.js` (JavaScript).
2. An `id` is unique (one element per page); a `class` can be shared by many elements, and one element can have several classes.
3. Every `<h1>` inside an element with class `card`; the element with id `count`.
4. The id inside `getElementById(...)`: compare its spelling with `index.html`, and don't put a `#` in it.
5. Saving the file (Ctrl + S) or refreshing the page (F5).
:::
