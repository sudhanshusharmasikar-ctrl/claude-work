:::chapter 3 | The Event Loop: How JavaScript Runs Your Code | Lecture 17 · Day 17 code
- What **single-threaded** means
- The **call stack** (same idea as in C++)
- Why synchronous code **blocks** the page
- **Web APIs** — the browser's helpers
- The **event loop**, microtasks and macrotasks
- Why "JavaScript never waits"
- What an **API** is
- Every experiment from the **Day 17** code
:::

This is the most important chapter for understanding **asynchronous** JavaScript. Callbacks (Chapter 4), Promises (Chapter 5) and `async`/`await` (Chapter 7) all make sense only after you understand the event loop. Go slowly here.

## 3.1 What does "single-threaded" mean?

**First principle:** your JavaScript code runs on **one** call stack. Only **one** thing executes at a time.

```js
console.log('First');
console.log('Second');
console.log('Third');
```

```output
First
Second
Third
```

This **always** runs in this order. JavaScript can't run `Second` and `Third` at the same time. It is like a **single-lane road** — the cars must go one at a time.

:::cpp One thread for your code
In C++ you can create extra threads with `std::thread` and run functions truly in parallel. JavaScript does **not** give your code extra threads — all your code runs on **one main thread**. The good news: no `std::mutex`, no data races on your variables. The challenge: if one piece of code is slow, **everything else waits**.
:::

## 3.2 The call stack (you already know it from C++)

The **call stack** is exactly the same idea as in C++ — the thing you see when you learn recursion. When a function is **called**, a *frame* is **pushed** on top of the stack. When the function **returns**, its frame is **popped**. JavaScript always runs whatever is on the **top**.

```js
function multiply(a, b) {
  return a * b;
}
function square(n) {
  return multiply(n, n);
}
function printSquare(n) {
  const result = square(n);
  console.log(result);
}
printSquare(4);   // 16
```

[[fig:call-stack|The call stack while `printSquare(4)` runs. Frames are pushed when a function is called and popped when it returns.]]

If a function keeps calling itself forever, the stack overflows — in C++ you get a crash (segmentation fault); in JavaScript you get `RangeError: Maximum call stack size exceeded`. Same idea!

## 3.3 Synchronous = blocking

**First principle:** each line **blocks** the next line until it completes.

```js
function slowFunction() {
  // Simulate slow work
  let sum = 0;
  for (let i = 0; i < 3000000000; i++) {
    sum += i;
  }
  return sum;
}

console.log('Start');
slowFunction();        // This BLOCKS everything
console.log('End');    // This waits for slowFunction to finish
```

While `slowFunction()` runs, the page **freezes**: you can't click buttons, you can't scroll, animations stop. Why? Because the one and only thread is busy with the loop. Clicking a button needs the same thread to run the click code — so the click has to wait. **This is the problem** that the rest of this chapter solves.

## 3.4 Web APIs: JavaScript's helpers

If JavaScript has only one thread, how can `setTimeout` wait 2 seconds without freezing the page?

**First principle:** the **browser** gives JavaScript extra powers called **Web APIs**, and they run **outside** JavaScript's single thread. JavaScript doesn't do the waiting — **the browser does**.

```js
console.log('1. Start');

// setTimeout is a Web API, NOT part of JavaScript itself
setTimeout(() => {
  console.log('2. Inside timeout');
}, 2000);

console.log('3. End');
```

```output
1. Start
3. End
2. Inside timeout   #> 2 seconds later
```

**What happened?**

1. JavaScript calls `setTimeout` and gives it a callback and a time (2000 ms).
2. The **browser** takes over the timer (not JavaScript!).
3. JavaScript immediately continues to line 3 and prints `3. End`.
4. After 2 seconds the browser says: *"Hey, run this callback"* — and `2. Inside timeout` is printed.

Common Web APIs (from the lecture's diagram):

| Web API | What the browser does for you | Your callback runs… |
|---|---|---|
| `setTimeout` / `setInterval` | counts time | after the time is over (once / again and again) |
| `fetch()` | sends a network request and waits for the reply | when the response arrives |
| DOM events: `addEventListener('click', …)` | watches the page for clicks, key presses… | every time the event happens |
| `localStorage`, `location` | stores data, reads/changes the URL | (these answer immediately) |
| `console.log` | prints to the console | (runs immediately) |
| Node.js: `fs.readFile(...)` | reads a file from disk | when the file has been read |

:::note `console.log` is given by the browser too — but it is synchronous
`console`, `document`, `localStorage` are also provided by the browser (they are not part of the JavaScript language itself). But they do their job **immediately** and return. Only APIs that have to *wait* for something (time, network, disk, the user) use a callback later.
:::

:::analogy A chef working alone
You are a chef working **alone** in a kitchen (one thread). You put rice in an **automatic rice cooker** (a Web API) and set its buzzer. You don't stand and stare at the cooker — you keep chopping vegetables. When the buzzer rings, you add *"serve the rice"* to your to-do list (the **queue**). You do it as soon as your hands are free (the **call stack is empty**).
:::

## 3.5 The event loop — the coordinator

**First principle:** the **event loop** connects single-threaded JavaScript with the asynchronous Web APIs. Here are all the parts:

- **Call Stack** — where your JavaScript runs, one frame at a time.
- **Web APIs** — the browser's helpers (timers, network, DOM events). They work outside the JS thread.
- **Task queues** — waiting areas for callbacks that are ready to run:
    - **Microtask queue** — Promise callbacks (`.then`, `.catch`, `.finally`, code after `await`). **Higher priority** — the VIP line.
    - **Macrotask queue** (also called the *callback queue* or *task queue*) — `setTimeout`, `setInterval`, clicks and other events, I/O. **Lower priority.**
- **Event Loop** — keeps checking: *"Is the call stack empty? Then move the next callback from a queue onto the stack."*

[[fig:event-loop|The whole machine. Your code runs on the call stack; slow work is handed to Web APIs; finished work waits in a queue; the event loop moves it to the stack when the stack is empty.]]

The event loop follows one simple rule, forever:

:::def The event loop rule
**When the call stack is empty:** first run **ALL** the microtasks (Promises), then run **ONE** macrotask (`setTimeout`, click…). Then check the microtasks again, and repeat forever.
:::

:::cpp The event loop in C++-style pseudo-code
If you have ever written a game loop or a GUI message loop, the event loop is the same idea:

```pseudo
runWholeScript();                     // 1. your file runs top to bottom (sync code)

while (true) {                        // the event loop
    while (!microtaskQueue.empty())   // 2. run ALL microtasks (Promise callbacks)
        runAndPop(microtaskQueue);

    if (!macrotaskQueue.empty())      // 3. run ONE macrotask (setTimeout, click...)
        runAndPop(macrotaskQueue);

    // 4. the browser may repaint the screen here, then loop again
}
```
Notice: a callback can only run when **nothing else** is running. JavaScript never interrupts running code in the middle.
:::

### Example: who prints first?

```js
console.log('1. Synchronous');

setTimeout(() => {
  console.log('2. Timeout 0ms');
}, 0);

Promise.resolve().then(() => {
  console.log('3. Promise');
});

console.log('4. Synchronous');
```

```output
1. Synchronous
4. Synchronous
3. Promise
2. Timeout 0ms
```

**Why this order?** Normal (synchronous) code always runs first — lines 1 and 4. Then the stack is empty, so the event loop runs the **microtasks** (the Promise → `3`). Only after that does it run a **macrotask** (the timeout → `2`), even though the timeout was 0 ms.

## 3.6 Step-by-step example: A, E, C, D, B

```js
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve()
  .then(() => console.log('C'))
  .then(() => console.log('D'));
console.log('E');
```

```output
A
E
C
D
B
```

Let's play the event loop ourselves:

| Step | What happens | Microtask queue | Macrotask queue | Printed so far |
|---|---|---|---|---|
| 1 | Call stack runs `console.log('A')` | — | — | A |
| 2 | `setTimeout` → handed to the browser's timer. 0 ms passes, so its callback waits in the macrotask queue | — | `B` | A |
| 3 | `Promise.resolve().then(C)` → the promise is already resolved, so callback `C` goes to the microtask queue | `C` | `B` | A |
| 4 | Call stack runs `console.log('E')`. The script is finished → **stack empty** | `C` | `B` | A E |
| 5 | Event loop: microtasks first! `C` runs. The second `.then` is now ready → `D` is added | `D` | `B` | A E C |
| 6 | Still a microtask left: `D` runs | — | `B` | A E C D |
| 7 | Microtasks empty → **one** macrotask: `B` runs | — | — | A E C D B |

Notice step 5: `D` is not in the queue from the beginning. A chained `.then` becomes ready only **after the previous one has finished**.

:::mistake `setTimeout(fn, 0)` does NOT mean "run now"
The time you give to `setTimeout` is the **minimum** waiting time, not an exact time. The callback runs only when (1) the time is over **and** (2) the call stack is empty **and** (3) all microtasks are done.

```js
setTimeout(() => console.log("timer"), 0);
for (let i = 0; i < 1e9; i++) {}   // keeps the stack busy for about a second
console.log("loop done");
```
```output
loop done
timer   #> only after the loop finished
```
:::

## 3.7 JavaScript never waits

The lecture's big idea: **JavaScript doesn't know and doesn't care** whether a function is "slow". It just calls the function, takes whatever the function **returns**, and moves to the next line. The **browser** decides what happens later.

From JavaScript's point of view, **all function calls look the same**:

```js
const result1 = Math.random();                    // call function
const result2 = document.getElementById('btn');   // call function
const result3 = setTimeout(() => {}, 1000);       // call function
const result4 = fetch('/api/data');               // call function

// JavaScript just:
// 1. calls the function
// 2. gets whatever is returned
// 3. moves to the next line
// JavaScript NEVER waits!
```

### The key: return value vs. callback

- A **synchronous** function returns the **actual result** immediately. Example: `window.innerWidth` gives `1920` right away and JavaScript uses it.
- An **asynchronous** function returns a **"ticket"** immediately (a timer ID, or a Promise). The **real result comes later** through a callback.

```js
console.log('1');

// JavaScript doesn't know this is "async" — it just calls it and gets a return value
const timerId = setTimeout(() => {
  console.log('3');
}, 1000);

console.log('2', timerId);   // timerId is returned immediately!
```

```output
1
2 1   #> the ticket: a timer ID (a number in the browser)
3     #> 1 second later
```

JavaScript never stopped! It called `setTimeout`, got the ticket `timerId`, and moved on. (In Node.js the ticket is a `Timeout` object instead of a number — still just a ticket, not the result.)

:::analogy The token at a food counter
At a busy food court you pay at the counter and **immediately** get a **token number** (the ticket). You don't stand frozen at the counter until the food is ready — you go and sit with your friends. When your number is called (the callback), you collect the food (the result). `setTimeout` gives you a timer ID token; `fetch` gives you a Promise token.
:::

### Proof: JavaScript doesn't "wait" even for `fetch`

```js
console.log('A');
fetch('/api/data');   // looks like it should wait… but it doesn't!
console.log('B');     // runs immediately

const promise = fetch('/api/data');
console.log(promise); // Promise { <pending> }  — a ticket, not the data
```

```output
A
B
Promise { <pending> }
```

`fetch()` returns a **Promise immediately** — JavaScript got *something* back (the ticket) and moved on. The data will arrive later.

| Code | What comes back immediately | Is it the real result? |
|---|---|---|
| `add(2, 3)` | `5` | <span class="pill yes">yes</span> |
| `Math.random()` | `0.234…` | <span class="pill yes">yes</span> |
| `window.innerWidth` | `1920` | <span class="pill yes">yes</span> |
| `setTimeout(fn, 1000)` | a timer ID, e.g. `1` | <span class="pill no">no</span> — the work happens later, in `fn` |
| `fetch('/api')` | a `Promise` (pending) | <span class="pill no">no</span> — the data comes later, via `.then` |

### A visual timeline

```js
console.log('1');
const id = setTimeout(() => console.log('3'), 1000);
console.log('2');
```

[[fig:never-waits|Timeline of the code above. JavaScript finishes its own work in a few milliseconds; the browser counts the 1000 ms separately and then hands the callback back.]]

### JavaScript's "contract" with every function

```js
// ALL functions work the same way from JavaScript's perspective:
//   1. Call the function
//   2. Get the return value (might be a number, undefined, a Promise, a timer ID...)
//   3. Continue immediately

function sync() {
  return 42;
}
function async() {
  return new Promise(resolve => {
    setTimeout(() => resolve(42), 1000);
  });
}

const a = sync();    // gets 42
const b = async();   // gets a Promise (not 42!)
// JavaScript calls both the SAME way. It doesn't "know" or "care" which is which.
```

### Three ways an async function can give you the result later

```js
// Method 1: Callback — "I'll call YOU when I'm done"
setTimeout(() => {
  console.log('Result!');          // called later
}, 1000);

// Method 2: Promise — "Here's a Promise, use .then()"
const promise = fetch('/api/data');
promise.then(result => {
  console.log('Result!', result);  // called later
});

// Method 3: async/await — looks like waiting, but it's just Promise syntax!
async function load() {
  const result = await fetch('/api/data');
  // Only THIS function pauses here. The JavaScript engine keeps doing other work.
}
```

We will study Method 1 in Chapter 4, Method 2 in Chapter 5 and Method 3 in Chapter 7.

## 3.8 What is an API?

:::def API (Application Programming Interface)
An **API** is **any way for code to talk to other code**. It has three parts:

- **Interface** — *how* to interact with it (which function to call, which arguments to give).
- **Abstraction** — you **don't need to know how it works inside**.
- **Contract** — *what to send* and *what you'll get back*.
:::

Example: `setTimeout(callback, ms)`. **Interface:** give a function and a number. **Contract:** you get a timer ID now, and your function is called after at least `ms` milliseconds. **Abstraction:** you have no idea how the browser's timer works inside — and you don't need to.

:::cpp You use APIs in C++ every day
When you call `std::sort(v.begin(), v.end())` you know the **contract** (give two iterators → the range becomes sorted), but not the **internal algorithm** (it's usually introsort). The header file is the **interface**. That is exactly what an API is.

Two meanings you will hear in web development:

- **Web APIs** — features the *browser* gives to your code (`setTimeout`, `fetch`, the DOM).
- **A server's API**, like `https://api.github.com/users` — a URL you *send a request to* over the internet, and it sends data back. Same idea: a contract between two pieces of code.
:::

## 3.9 Day 17 code, experiment by experiment

:::day Day 17 — `index.html` + `first.js`
The page has three coloured buttons on a black background. The script tag is written **after** the body, so the buttons already exist when `first.js` runs (that's why `getElementById` can find them).

```html title="03JS/Day17/index.html"
<body style="background-color: black; color: white;">
    <button id="button1" style="background-color: red;">Button1</button>
    <button id="button2" style="background-color: orange;">Button2</button>
    <button id="button3" style="background-color: green;">Button3</button>
</body>
<script src="./first.js"></script>
```
:::

### Experiment 1 — a loop that blocks everything

```js title="Day 17 · first.js — experiment 1"
console.log("First");
let sum = 0;
for (let i = 0; i < 3000000000; i++)
    sum += i;

console.log(sum);
console.log("Last");
```

```output
First
4499999997067114000   #> after a few seconds of freezing
Last
```

- 3 billion loop steps take a few seconds (about 4 s on my machine). During that time the page is **frozen** — nothing else can run, because the one thread is busy.
- `"Last"` is printed only after the loop ends: synchronous code **blocks**.

:::cpp Why is the number slightly "wrong"?
The exact sum 0 + 1 + … + 2,999,999,999 is 4,499,999,998,500,000,000. JavaScript printed 4,499,999,997,067,114,000. That's because **every JavaScript number is a 64-bit `double`** (like C++ `double`), which stores integers exactly only up to 2<sup>53</sup> ≈ 9 × 10<sup>15</sup>. After that, each `+=` is rounded a little, and the tiny errors add up. The same loop with a C++ `double` would behave the same way (with `long long` you would get the exact answer).
:::

### Experiment 2 — `setTimeout` doesn't block

```js title="Day 17 · first.js — experiment 2"
console.log("Hello Ji");

setTimeout(() => {
    console.log("Time Out Executed");
}, 5000);

console.log("I am the end");
```

```output
Hello Ji
I am the end
Time Out Executed   #> 5 seconds later
```

The timer is handed to the browser (Web API). JavaScript immediately continues and prints `"I am the end"`. After 5 s, the callback goes to the macrotask queue, and the event loop runs it (the stack is empty by then).

### Experiment 3 — button click listeners

```js title="Day 17 · first.js — experiment 3"
console.log("Hi Ji");

const button1 = document.getElementById("button1");
button1.addEventListener('click', () => {
    console.log("Button 1 is clicked");
});

const button2 = document.getElementById("button2");
button2.addEventListener('click', () => {
    console.log("Button 2 is clicked");
});

const button3 = document.getElementById("button3");
button3.addEventListener('click', () => {
    console.log("Button 3 is clicked");
});

console.log("I am the end");
```

```output
Hi Ji
I am the end
Button 2 is clicked   #> only when you click the orange button
Button 1 is clicked   #> ...in whatever order you click
Button 1 is clicked   #> every click prints again
```

- `document.getElementById("button1")` finds the button element on the page (DOM API).
- `addEventListener('click', callback)` does **not** run the callback. It **registers** it with the browser: *"when this button is clicked, call this function"*. Then JavaScript moves on — that's why `"I am the end"` is printed right away.
- Each time you click, the browser puts the callback into the **macrotask queue**, and the event loop runs it when the stack is empty.
- Unlike `setTimeout` (runs once), a listener runs **every time** the event happens.

[[fig:click-flow|What happens when you click Button 1.]]

### Experiment 4 — the same idea again

```js title="Day 17 · first.js — experiment 4"
console.log("I am first");

setTimeout(() => {
    console.log("I am timeOut");
}, 5000);

console.log("I am end");
```

```output
I am first
I am end
I am timeOut   #> 5 seconds later
```

### Experiment 5 — `fetch` (the code that is active in the file)

```js title="Day 17 · first.js — experiment 5 (not commented out)"
console.log("Start the Operation");

fetch("https://api.github.com/users").then(() => {
    console.log("Git Hub user info");
})

console.log("end of operation");
```

```output
Start the Operation
end of operation
Git Hub user info   #> when GitHub's server replies (a few hundred ms later)
```

- `fetch(url)` asks the **browser** to send a network request to GitHub's server. It immediately returns a Promise (a ticket).
- `.then(callback)` says: *"when the response arrives, run this callback"*.
- JavaScript doesn't wait for the internet — it prints `"end of operation"` first. When the reply arrives, the callback becomes a **microtask** and runs.

### The other small experiments at the bottom of the file

```js title="Day 17 · first.js — other experiments"
let arr = [100, 20, 90, 70];
arr.push(10);            // [100, 20, 90, 70, 10] — normal synchronous work
arr.map(x => x * 10);    // creates [1000, 200, 900, 700, 100] (result not stored)

function hello() {
    console.log("Hi ji");
}
hello();                 // a frame for hello() is pushed on the call stack, then popped
console.log("Hello Ji");

ahsdjsah("Hello Ji");    // ❌ ReferenceError: ahsdjsah is not defined
```

These show that array work and normal function calls are plain **synchronous** code on the call stack. The last line calls a function that doesn't exist, so JavaScript throws a `ReferenceError` and the script **stops there** — an error in synchronous code stops everything after it.

## 3.10 Things to Remember

:::remember
- JavaScript runs your code on **one thread** with **one call stack** (push on call, pop on return — like C++).
- Synchronous code **blocks**: a long loop freezes the whole page.
- Timers, network requests and DOM events are handled by the **browser (Web APIs)**, outside the JS thread.
- When their work is done, their callbacks wait in a **queue**: Promise callbacks → **microtask queue**; `setTimeout`/`setInterval`/events → **macrotask queue**.
- **Event loop rule:** when the stack is empty → run **all** microtasks → then **one** macrotask → repeat.
- Order to remember: **synchronous code → microtasks (Promises) → macrotasks (setTimeout)**.
- The `setTimeout` delay is a **minimum**, not an exact time.
- **JavaScript never waits**: an async function returns a *ticket* (timer ID / Promise) immediately; the result comes later via a callback.
- A `setTimeout` callback runs **once**; an event-listener callback runs **every time** the event happens.
- An **API** = interface + abstraction + contract.
:::

:::quiz Predict the output!
1. What is printed?

    ```js
    console.log("X");
    setTimeout(() => console.log("Y"), 0);
    console.log("Z");
    ```

2. What is printed?

    ```js
    setTimeout(() => console.log("timeout"), 0);
    Promise.resolve().then(() => console.log("promise"));
    console.log("sync");
    ```

3. What is printed?

    ```js
    console.log(1);
    setTimeout(() => console.log(2), 1000);
    setTimeout(() => console.log(3), 0);
    Promise.resolve().then(() => console.log(4));
    console.log(5);
    ```

4. What does `setTimeout(...)` return: the result of the callback, or something else?
5. A button has a click listener. The user clicks it while a 5-second loop is running. When does the listener run?
:::

:::answer
1. `X`, `Z`, `Y`
2. `sync`, `promise`, `timeout` — synchronous first, then microtasks, then macrotasks.
3. `1`, `5`, `4`, `3`, `2` — sync (1, 5), microtask (4), then timers: the 0 ms timer (3) before the 1000 ms timer (2).
4. A **timer ID** (a ticket). The callback's result is not returned to you.
5. Only **after the loop finishes** — the click callback waits in the macrotask queue until the call stack is empty.
:::
