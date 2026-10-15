:::chapter 8 | Counting in Circles, and Time | Exercise 16 Image Carousel · Exercise 17 Live Clock ⭐
- Keeping **which slide is showing** in a number, and picking an element by index
- **Wrap-around** with the remainder operator `%` (and its trap with negative numbers)
- Turning text into a number with **`Number()`**
- The **`Date`** object: the current hours, minutes and seconds
- **Zero-padding** with `padStart`, and running code **every second** with `setInterval`
:::

:::day Today's plan (2 hours)
**Exercise 16** (65 min): new ideas 20 · build 30 · grade and review 15. **Exercise 17** (55 min): new ideas 15 · build 25 · grade and review 15. The clock is the second question reported from the real round: after finishing it, close the file, reopen the starter (Day 10 shows how) and build it again in **under 15 minutes**.
:::

## Exercise 16 · Image Carousel

### What you are building

![The carousel before and after](content/img/16.jpg){.shot}

Four coloured slides, one visible at a time. **Next** and **Prev** move through them, the dots jump to a slide, and the ends **wrap around**: Next on slide 4 goes to slide 1, Prev on slide 1 goes to slide 4. The grader checks:

| Test | What it does | Expects |
|---|---|---|
| shows the first slide and dot on load | opens the page | slide 1 and dot 1 have `active`; exactly one `.slide.active` |
| Next and Prev move between slides | Next, then Prev | slide 2 active (and slide 1 not), then slide 1 again |
| dots jump to a specific slide | clicks dot 3 | slide 3 and dot 3 active |
| navigation wraps around at the ends | dot 4, Next, Prev | slide 1, then slide 4 |

### New ideas

#### 1. A number as the state

The whole carousel is described by **one number**: the index of the slide being shown, from 0 to 3. Keep it in `let index = 0;`. Every button only changes that number and then **shows** the slide it points to: `slides[index]` is the slide element at that position, just like an array.

#### 2. Wrap-around with `%`

`%` gives the **remainder** of a division: `5 % 4` is 1, because 5 = 4 + **1**. With 4 slides, `% 4` folds every number back into 0…3:

```js title="remainders with 4 slides"
const n = 4; // number of slides
console.log(1 % n, 3 % n, 4 % n, 5 % n);
console.log(-1 % n);
console.log((-1 + n) % n, (4 + n) % n, (2 + n) % n);
```

```output
1 3 0 1
-1                                     #> the trap
3 0 2                                  #> the fix: add n first
```

So **Next** from the last slide (3 + 1 = 4) gives `4 % 4` = **0**: back to the first. But **Prev** from the first slide (0 − 1 = −1) gives **−1** in JavaScript, not 3, and `slides[-1]` doesn't exist. Adding `n` before taking the remainder fixes both directions: `(i + n) % n`.

[[fig:fp-carousel-ring|Four slides in a circle. Next adds 1 and Prev subtracts 1; `(i + 4) % 4` turns 4 into 0 and −1 into 3, so you can never fall off either end.]]

#### 3. One function for every button

Next, Prev and the four dots all do the same thing with a different target, so write it **once**:

```js title="the shape of the carousel"
function show(i) {
  // 1. wrap i into 0..3 and store it in index
  // 2. all slides and dots off
  // 3. slide[index] and dot[index] on
}
nextBtn.addEventListener('click', () => show(index + 1));
```

`() => show(index + 1)` is a short arrow function: when clicked, call `show` with one more than the current index. It's the "all off, one on" pattern from Day 7, chosen by a number instead of a click.

#### 4. Text into numbers

Each dot stores its position in `data-index="2"`. Attribute values are **text**, and `+` on text **joins** instead of adding:

```js title="text versus numbers"
console.log(Number('2') + 1, '2' + 1);
```

```output
3 21
```

So turn the value into a number first: `Number(dot.dataset.index)`.

#### 5. CSS: the later rule wins

The starter CSS has `.slide { display: grid; ... }` near the top and an empty `.slide { }` further down, where you write `display: none`. Both selectors have the same score, so the **later** one wins and all slides hide. `.slide.active` scores higher (two classes), so you give it `display: grid` back for the one active slide.

### Read the starter files

| File | What is there | What you will use |
|---|---|---|
| `index.html` | complete | four `.slide`s (the first is `active`), `#prev`, `#next`, four `.dot`s with `data-index` 0–3 |
| `style.css` | four empty rules | `.slide`, `.slide.active`, `.dot`, `.dot.active` |
| `script.js` | comments only | everything |

### The plan in plain English

1. CSS: hide `.slide`, show `.slide.active` with `display: grid` (to keep the number centered). Dots: 10px circles, half-transparent white; the active dot solid white.
2. JS: select all slides, all dots, Prev and Next. `let index = 0;`
3. `show(i)`: `index = (i + slides.length) % slides.length`; remove `active` from all slides and dots; add it to `slides[index]` and `dots[index]`.
4. Next → `show(index + 1)`; Prev → `show(index - 1)`; each dot → `show(Number(dot.dataset.index))`.
5. Call `show(0)` at the end.

:::tip Hint 1
Use `slides.length` instead of writing `4`. Add a fifth slide to the HTML later and the code still works.
:::

:::tip Hint 2
If Prev on the first slide makes everything disappear, you have the negative remainder problem: `index` became −1.
:::

:::note Stop here and build it
Then run `npm test -- 16-image-carousel`.
:::

### The solution, line by line

```css title="16/style.css"
.slide {
  display: none;
}

.slide.active {
  display: grid;
}
```

```css title="16/style.css (the dots)"
.dot {
  width: 10px;
  height: 10px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.45);
  cursor: pointer;
}

.dot.active {
  background: #ffffff;
}
```

```js title="16/script.js" lines
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');
const prevBtn = document.getElementById('prev');
const nextBtn = document.getElementById('next');

let index = 0;

function show(i) {
  // wrap around: -1 becomes the last slide, 4 becomes 0
  index = (i + slides.length) % slides.length;

  slides.forEach((slide) => slide.classList.remove('active'));
  dots.forEach((dot) => dot.classList.remove('active'));

  slides[index].classList.add('active');
  dots[index].classList.add('active');
}

nextBtn.addEventListener('click', () => show(index + 1));
prevBtn.addEventListener('click', () => show(index - 1));

dots.forEach((dot) => {
  dot.addEventListener('click', () => show(Number(dot.dataset.index)));
});

show(0);
```

| Lines | What they do |
|---|---|
| 6 | The state: which slide is showing. |
| 10 | Wrap the requested position into 0…3 and **store** it. Next and Prev compute from this stored value. |
| 12–13 | All off (short arrow functions with one statement need no braces). |
| 15–16 | One on: the slide and the dot at the same position. |
| 19–20 | Next and Prev only say **where to go**; `show` does the rest. |
| 22–24 | Each dot jumps to its own position, converted from text to a number. |
| 26 | Make the page consistent at load. |

### Mistakes beginners make

:::mistake `index = i % slides.length`
Next works, but Prev on the first slide gives −1, `slides[-1]` is `undefined`, and `undefined.classList` throws *Cannot read properties of undefined*. Add the length first.
:::

:::mistake Forgetting to store the new index
`show(index + 1)` with a `show` that never sets `index` moves to slide 2 and then stays there, because `index` is still 0 every time.
:::

### Interview questions

:::qa -
Q: How do you make a carousel wrap around?
Keep the current index and compute the next one with `(i + n) % n`, where `n` is the number of slides. Adding `n` first handles going backwards from 0, because `%` in JavaScript keeps the sign of the left number.

Q: How would you make it play automatically, and pause on hover?
`const timer = setInterval(() => show(index + 1), 3000);` starts it. On `mouseenter`, `clearInterval(timer)`; on `mouseleave`, start a new interval.
:::

### Practice twist

Add **autoplay**: move to the next slide every 3 seconds (`setInterval`, which you'll learn in a minute), and stop when the mouse is over the carousel.

## Exercise 17 · Live Digital Clock ⭐

### What you are building

![The clock before and after](content/img/17.png){.shot}

A clock showing the current time as `HH:MM:SS`, updating every second. The grader checks that `#clock` matches the shape two digits, colon, two digits, colon, two digits; that the hours and minutes equal the real current time; and that the text **changes** within 3 seconds.

### New ideas

#### 1. `Date`

`new Date()` creates an object holding **this exact moment**. Ask it for parts:

```js title="reading a date"
const d = new Date(2026, 9, 15, 9, 5, 3); // 15 Oct 2026, 09:05:03
console.log(d.getHours(), d.getMinutes(), d.getSeconds());
```

```output
9 5 3
```

With no arguments, `new Date()` is **now**, in the user's own time zone. The hours go from 0 to 23. (The example builds a fixed date so the output stays the same. Note month 9 is **October**: months count from 0, days don't.)

#### 2. Zero-padding

`9:5:3` is not `HH:MM:SS`. Each part must be two digits:

```js title="padStart"
console.log(String(7).padStart(2, '0'));
console.log(String(12).padStart(2, '0'));
```

```output
07
12
```

`padStart(2, '0')` adds `'0'`s **at the start** until the text is 2 characters long. It's a string method, so turn the number into a string first with `String(...)`. Put this in a tiny function, `pad(n)`, because you need it three times.

#### 3. Run something every second

```js title="setInterval and setTimeout"
setInterval(updateClock, 1000);   // call updateClock every 1000 ms, forever
setTimeout(updateClock, 1000);    // call it ONCE, after 1000 ms
```

`setInterval` keeps calling your function. It returns an id; `clearInterval(id)` stops it. Note that you pass `updateClock` **without** brackets again: the browser calls it later.

**Call it once yourself first.** The interval's first call happens after a full second, so without an immediate call the page shows `--:--:--` for one second.

#### 4. CSS for digits

In most fonts a `1` is narrower than an `8`, so the time would wobble left and right as it changes. A **monospace** font (every character the same width) keeps it still.

### Read the starter files

`index.html` has `<div id="clock" class="clock">--:--:--</div>`. `style.css` has an empty `.clock` rule (large monospace text in a purple colour). `script.js` has only comments.

### The plan in plain English

1. Select `#clock`.
2. Write `pad(number)`: turn it into a string and pad it to 2 characters with `'0'`.
3. Write `updateClock()`: make a `new Date()`, read the hours, minutes and seconds, pad each, and write `` `${hours}:${minutes}:${seconds}` `` into the clock.
4. Call `updateClock()` once, then `setInterval(updateClock, 1000)`.
5. CSS: monospace font, about `3rem`, bold, a purple colour, some letter spacing.

:::note Stop here and build it
Then run `npm test -- 17-live-clock`. One test waits up to 3 seconds for the clock to change, so this exercise takes a moment longer to grade.
:::

### The solution, line by line

```js title="17/script.js" lines
const clock = document.getElementById('clock');

function pad(number) {
  return String(number).padStart(2, '0');
}

function updateClock() {
  const now = new Date();
  const hours = pad(now.getHours());
  const minutes = pad(now.getMinutes());
  const seconds = pad(now.getSeconds());
  clock.textContent = `${hours}:${minutes}:${seconds}`;
}

updateClock();
setInterval(updateClock, 1000);
```

| Lines | What they do |
|---|---|
| 3–5 | A helper that **returns** a value: 7 → `'07'`, 12 → `'12'`. |
| 8 | A fresh `Date` on every call. Creating it once outside the function would freeze the clock at the page's load time. |
| 9–12 | Read, pad and show. |
| 15 | Show the time immediately. |
| 16 | Then refresh it every second. |

```css title="17/style.css"
.clock {
  font-family: Consolas, "Courier New", monospace;
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #a78bfa;
}
```

`font-family` is a list: the browser uses the first font it has. `monospace` at the end means *"any fixed-width font"*, so there's always a fallback.

### Mistakes beginners make

:::mistake `const now = new Date()` outside the function
The clock shows the load time and never changes: each call reads the **same** old moment. The grader's third test fails.
:::

:::mistake `now.getHours().padStart(2, '0')`
*TypeError: now.getHours(...).padStart is not a function*. `getHours()` returns a **number**, and `padStart` exists only on strings. Wrap it: `String(now.getHours())`.
:::

:::mistake `setInterval(updateClock(), 1000)`
The brackets call `updateClock` once and pass its result (`undefined`) to `setInterval`. The clock shows the time but never updates. Same rule as Day 1: hand over the function, don't call it.
:::

### Interview questions

:::qa -
Q: What is the difference between `setTimeout` and `setInterval`?
`setTimeout(fn, ms)` calls `fn` **once** after `ms` milliseconds; `setInterval(fn, ms)` calls it **repeatedly** every `ms`. Both return an id you can pass to `clearTimeout` / `clearInterval` to cancel.

Q: Is `setInterval(fn, 1000)` exactly one second?
No. It's **at least** about 1000 ms: if the browser is busy, or the tab is in the background, calls can be late. That's why the clock reads `new Date()` on every call instead of adding 1 to a counter: the time shown is always correct, even if one tick was late.

Q: How do you show a 12-hour clock with AM/PM?
`const suffix = h >= 12 ? 'PM' : 'AM';` and `const h12 = h % 12 || 12;` (`h % 12` turns 13 into 1, and `|| 12` turns 0 into 12).
:::

### Practice twist

Add the date under the clock, such as *Thursday, 15 October 2026*. Look up `toLocaleDateString` with the options `{ weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }`. Then add a button that switches between 24-hour and 12-hour format.
