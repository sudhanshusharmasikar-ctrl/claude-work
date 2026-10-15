<h1 class="front notoc">How to Use This Guide</h1>

This guide takes you through **14 of the 20 exercises** in
[dexterhere04/accenture-frontend-practice](https://github.com/dexterhere04/accenture-frontend-practice) in **10 days of 2 hours**.
It assumes you know very little HTML, CSS or JavaScript. Every idea is explained the first time you need it, right before the exercise that uses it.

Each exercise follows the same steps:

1. **What you are building:** a picture of the starter page next to the finished one, and the list of things the grader checks.
2. **New ideas:** only what this exercise needs, with tiny examples and their real output.
3. **Read the starter files:** what is already written, and the ids and classes you will use.
4. **The plan in plain English:** the steps before any code.
5. **Hints:** three, from a gentle push to almost the answer. Read one at a time.
6. **The solution, line by line,** to read **after** you have tried.
7. **Mistakes beginners make, interview questions,** and a **practice twist** to do on your own.

:::note What was checked
Every solution in this guide was run against the repository's own grader (its Playwright tests): **all 57 tests of the 14 exercises pass**. The outputs printed under the small examples come from running them. The scripts that did this are in `frontend-practice-source/verify/`.
:::

## The 10-day plan

[[fig:fp-plan|Fourteen exercises in nine days, then a mock round on Day 10. The two stars mark the questions that candidates reported from the real Accenture round.]]

| Day | Exercises | New ideas |
|---|---|---|
| **0** · evening before, 45 min | Setup | Node.js, VS Code, cloning the repo, running the grader |
| **1** | 03 Click Counter | variables, functions, the **select → listen → change** pattern |
| **2** | 01 Fix the Form · 08 Show / Hide Password | labels and input types, form submit, `if` / `else` |
| **3** | 02 Profile Card · 04 Center It | the box model, flexbox, grid, absolute positioning |
| **4** | 05 Search Box ⭐ | arrays, `filter`, creating elements, the **render function** |
| **5** | 06 To-Do List · 09 Dark Mode | building elements, `classList`, CSS variables |
| **6** | 07 Form Validation | `else if`, regular expressions, a "valid" flag |
| **7** | 13 Accordion · 14 Tab Switcher | `querySelectorAll`, `forEach`, `data-*`, **all off, one on** |
| **8** | 16 Carousel · 17 Live Clock ⭐ | an index with wrap-around, `Date`, `setInterval` |
| **9** | 15 Dynamic Table | objects, filter + sort, **state + render** |
| **10** | Mock round + revision | timed redo of 05 and 17, cheat sheets, interview questions |

**Why these 14?** The real round gives you pre-built files and asks you to change them, with DOM changes, events and dynamic lists at the centre. The 14 cover all of that, plus the HTML and CSS basics you need to read any starter file. The other six (10, 11, 12, 18, 19, 20) are good practice but either mostly CSS or need ideas (fetching data, saving to the browser) that are easier once these 14 feel normal. They are in the **Bonus** chapter for after Day 10.

## Your 2 hours, every day

| Minutes | What you do |
|---|---|
| 0–25 | Read the day's **New ideas**. Type every small example into the browser console (Day 0 shows how). |
| 25–35 | Read `task.md` and the starter files. Write the plan as comments at the top of `script.js`. |
| 35–90 | **Build it.** Stuck for 10 minutes? Read Hint 1. Still stuck after 10 more? Hint 2. |
| 90–100 | Run the grader. Fix what fails. |
| 100–120 | Read the solution explanation and compare it with yours. Answer the interview questions **out loud**. Do the practice twist. |

On days with two exercises, give the first one about 70 minutes and the second about 50.

:::remember The five rules
1. **Type the code, never paste it.** Your fingers learn too.
2. **Try for 10 minutes before every hint.** Being stuck is where the learning happens.
3. **Run the grader after every exercise.** Green means it really works.
4. **Explain your code out loud** as if to an interviewer. If you can't explain a line, read its explanation again.
5. **Hard exercise? Redo it the next morning from the starter files,** without looking. That is how confidence is built.
:::

## Progress tracker

Tick each box as you go. "Redone from blank" means you deleted your code and wrote it again without help.

| Ex | Name | Day | Tests pass | Redone from blank | Confidence (1–5) |
|---|---|---|---|---|---|
| 03 | Click Counter | 1 | ☐ | ☐ | |
| 01 | Fix the Form | 2 | ☐ | ☐ | |
| 08 | Show / Hide Password | 2 | ☐ | ☐ | |
| 02 | Style the Profile Card | 3 | ☐ | ☐ | |
| 04 | Center It | 3 | ☐ | ☐ | |
| 05 | E-commerce Search Box ⭐ | 4 | ☐ | ☐ | |
| 06 | To-Do List | 5 | ☐ | ☐ | |
| 09 | Dark-Mode Toggle | 5 | ☐ | ☐ | |
| 07 | Form Validation | 6 | ☐ | ☐ | |
| 13 | Accordion | 7 | ☐ | ☐ | |
| 14 | Tab Switcher | 7 | ☐ | ☐ | |
| 16 | Image Carousel | 8 | ☐ | ☐ | |
| 17 | Live Digital Clock ⭐ | 8 | ☐ | ☐ | |
| 15 | Dynamic Table | 9 | ☐ | ☐ | |

<h1 class="toc-title notoc">Contents</h1>

[[toc]]
