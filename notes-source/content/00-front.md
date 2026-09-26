<h1 class="front">How to Use These Notes</h1>

Hello! 👋 These notes are written for **you** — a student who is comfortable with **C++** and knows a *little bit* of JavaScript. I will teach every idea slowly, in simple words, with small examples, pictures, and the exact output you will see on your screen. Whenever a JavaScript idea is similar to something in C++, I will show you the C++ version side by side, so your brain can connect the new thing to something it already knows.

You do **not** need to read everything in one go. Read one chapter, run the code yourself, answer the quiz at the end, and only then move to the next chapter.

### What is inside

| # | Chapter | From lecture | Code from GitHub |
|---|---|---|---|
| 0 | JavaScript warm-up for a C++ brain | basics used everywhere | — |
| 1 | Array superpowers: `forEach`, `map`, `filter`, `reduce`, `find`, `some`, `every` | Lecture 12 | — |
| 2 | `Set` and `Map` | Lecture 12 | — |
| 3 | The Event Loop — how JavaScript runs your code | Lecture 17 | Day 17 |
| 4 | Callbacks and Callback Hell | Lecture 18 | Day 18 |
| 5 | Promises | Lecture 19 | Day 19 |
| 6 | JSON vs JavaScript objects | Lecture 19 | Day 19 |
| 7 | `async` / `await` | Lecture 20 | Day 20 |
| 8 | Prototypes and Classes | Lecture 21 | Day 21 |
| 9 | Strict mode | Lecture 22 | Day 22 |
| 10 | The `this` keyword, `call` / `apply` / `bind`, arrow functions | Lecture 22 | Day 22 |
| 11 | Final revision: everything on a few pages | all | all |

### How every chapter is organised

1. **Opener** — a dark box that tells you what you will learn.
2. **Explanation in small steps** — first the *idea*, then the *syntax*, then *examples with output*.
3. **Diagrams** — whenever a picture makes it easier (event loop, promise states, prototype chain…).
4. **Code from GitHub (Day 17 – Day 22)** — every experiment from the course files, explained line by line, with the output.
5. **Things to Remember** — the points you must not forget (perfect for revision before an exam or interview).
6. **Quick Quiz + Answers** — test yourself. Try first, then check the answer box.

### The coloured boxes you will see

<div class="legend" markdown="1">

:::cpp
Compares the JavaScript idea with C++ (STL, pointers, threads, classes…).
:::

:::remember
The most important points. Read these again before exams.
:::

:::mistake
A bug that almost every beginner makes — and how to avoid it.
:::

:::analogy
A real-world story (Zomato order, token at a food counter…) that makes the idea obvious.
:::

:::deep
Extra detail for the curious. Safe to skip on the first reading.
:::

:::day Code from GitHub
Explains the code from the course repository (Day 17 – Day 22).
:::

</div>

### How to run the code yourself

There are three easy ways. Use whichever is convenient:

| Way | How | Good for |
|---|---|---|
| Browser console | Open any web page → press <span class="kbd">F12</span> (or right-click → *Inspect*) → **Console** tab → paste code → <span class="kbd">Enter</span> | Quick experiments |
| HTML + JS file | Create `index.html` with `<script src="./index.js"></script>` and open it in the browser (VS Code *Live Server* is great) | Anything that uses buttons, `document`, the page (DOM) |
| Node.js | Save as `index.js`, then run `node index.js` in the terminal | Plain JavaScript without a web page |

:::note About the GitHub code in these notes
The course files keep many small experiments in one file, most of them commented out with `//`. In these notes I show **each experiment separately, un-commented**, in the same order as the file. I only changed spacing/indentation and split very long lines so they fit on the page — the logic is exactly the same. Spelling in the original strings (like `"persent"` or `"succesfully"`) is kept, so the output matches what you will see when you run the real file.
:::

[[pagebreak]]

<h1 class="toc-title notoc">Contents</h1>

[[toc]]
