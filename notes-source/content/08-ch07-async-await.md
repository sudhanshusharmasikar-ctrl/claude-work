:::chapter 7 | async / await | Lecture 20 · Day 20 code
- `async` functions **always return a Promise**
- `await` pauses **only this function** — not the program
- Error handling with `try` / `catch`
- The important rules (and the most common mistakes)
- **Sequential vs parallel** — `Promise.all`
- The **Day 20** code: GitHub user cards, Zomato with `async`/`await`
- Callbacks vs Promises vs `async`/`await` — the same app 3 ways
:::

## 7.1 What is `async` / `await`?

**`async`/`await`** is a modern JavaScript feature (ES2017) that gives us a **cleaner way to work with promises**. Instead of chaining `.then()` calls, you can write asynchronous code that **reads like synchronous code** — top to bottom.

It is **not** a new mechanism. Underneath, it is still Promises and the event loop. That's why people call it **"syntactic sugar"** over Promises: the same thing, but sweeter to write.

## 7.2 `async` functions always return a Promise

Put the word `async` before a function and it will **always return a Promise** — even if you return a normal value:

```js
async function myFunction() {
  return "Hello";
}

// is equivalent to:
function myFunction() {
  return Promise.resolve("Hello");
}
```

- `return value` inside an async function → the promise is **fulfilled** with `value`.
- `throw error` inside an async function → the promise is **rejected** with `error`.

:::day Day 20 — experiment 1: `greet()`
```js title="Day 20 · index.js — experiment 1"
// async await
// aysnc function always return a promise
async function greet() {
    return "Rohit";

    // return new Promise((resolve, reject) => {
    //     reject("Rohit");
    // })
}

const response = greet();
// console.log(response);
response.then((data) => console.log(data))
.catch((error) => {
    console.log("Error:", error);
})
```

```output
Rohit
```

- `greet()` returns a **Promise**, not the string. That's why we need `.then` to get `"Rohit"` out of it.
- If you un-comment `console.log(response)`, Chrome shows `Promise {<fulfilled>: 'Rohit'}` (Node.js shows `Promise { 'Rohit' }`).
- If you replace `return "Rohit"` with the commented code (a promise that **rejects**), the async function's promise rejects too, and the output becomes `Error: Rohit`.
:::

## 7.3 `await` — "pause this function until the promise settles"

`await` can be written in front of a promise **inside an async function**. It pauses **that function** until the promise settles:

- If the promise is **fulfilled** → `await` gives you its **value**.
- If the promise is **rejected** → `await` **throws** the error (so you can catch it with `try`/`catch`).

```js
async function fetchData() {
  const response = await fetch('https://api.example.com/data'); // wait for the Response
  const data = await response.json();                            // wait for the body
  return data;
}
```

Compare with Chapter 5: no `.then`, no nested callbacks — just normal-looking lines.

### `await` pauses ONLY this function — the rest of the program keeps running

This is the most important thing to understand:

```js
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function demo() {
  console.log("2. demo started");
  await wait(1000);                 // demo() pauses here for 1 second...
  console.log("4. demo resumed");   // ...and continues from here later
}

console.log("1. before calling demo");
demo();
console.log("3. after calling demo — main code is NOT blocked");
```

```output
1. before calling demo
2. demo started
3. after calling demo — main code is NOT blocked
4. demo resumed   #> 1 second later
```

[[fig:await-timeline|`demo()` runs until its first `await`, then steps aside. The main code continues; one second later the rest of `demo()` is resumed (as a microtask).]]

:::cpp `future.get()` blocks — `await` doesn't
In C++, `int x = f.get();` **blocks the whole thread** until the value is ready. `await` is different: it **suspends only this function** and gives the thread back to the event loop, which can run other code (clicks, timers, other functions) in the meantime. If you have heard of **C++20 coroutines**, `co_await` is the same idea.

Under the hood, JavaScript turns "the rest of the function after `await`" into a `.then()` callback:

```js
// This async function...
async function getUserName() {
  const response = await fetch("/api/user");
  const user = await response.json();
  console.log(user.name);
}

// ...does the same as this promise chain:
function getUserName() {
  return fetch("/api/user")
    .then(response => response.json())
    .then(user => { console.log(user.name); });
}
```
:::

## 7.4 Promises vs `async`/`await` — side by side

**With Promises:**

```js
function getUser() {
  return fetch('/api/user')
    .then(response => response.json())
    .then(user => {
      return fetch(`/api/posts/${user.id}`);
    })
    .then(response => response.json())
    .then(posts => {
      console.log(posts);
      return posts;
    })
    .catch(error => console.error(error));
}
```

**With `async`/`await`:**

```js
async function getUser() {
  try {
    const response = await fetch('/api/user');
    const user = await response.json();
    const postsResponse = await fetch(`/api/posts/${user.id}`);
    const posts = await postsResponse.json();
    console.log(posts);
    return posts;
  } catch (error) {
    console.error(error);
  }
}
```

The second version reads like a normal recipe. And notice another win: `user` is a normal variable, so every later line can use it — no more "how do I get data out of the callback?" problem.

## 7.5 Error handling with `try` / `catch`

Use `try`/`catch` blocks for error handling — this feels more natural than `.catch()`, and it's the same `try`/`catch` you know from C++:

```js
async function riskyOperation() {
  try {
    const result = await mightFail();
    return result;
  } catch (error) {
    // Handle specific errors
    if (error.code === 'NETWORK_ERROR') {
      console.error('Network failed');
    }
    throw error;   // re-throw if needed
  }
}
```

### What gets caught?

When you use `try`/`catch` with `async`/`await`, the `catch` block handles:

1. **Rejected promises** — when a promise you `await` rejects.
2. **Thrown errors** — anything thrown with `throw` inside the `try` block.
3. **Synchronous errors** — runtime errors like `TypeError`, `ReferenceError`, etc.

```js
// 1. Rejected promise
async function example1() {
  try {
    const result = await Promise.reject(new Error('Promise rejected!'));
  } catch (error) {
    console.log(error.message);   // "Promise rejected!"
  }
}

// 2. Thrown error
async function example2() {
  try {
    throw new Error('Something went wrong');
  } catch (error) {
    console.log(error.message);   // "Something went wrong"
  }
}

// 3. Runtime error
async function example3() {
  try {
    const obj = null;
    console.log(obj.property);    // TypeError
  } catch (error) {
    console.log(error.message);   // "Cannot read properties of null (reading 'property')"
  }
}
```

(Older browsers word the last message a bit differently, e.g. *"Cannot read property 'property' of null"* — same error.)

### Real-world example with `fetch`

```js
async function fetchUser(id) {
  try {
    const response = await fetch(`/api/user/${id}`);

    // fetch doesn't reject on HTTP errors (404, 500, etc.)
    // So you need to check manually:
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const user = await response.json();
    return user;
  } catch (error) {
    // This catches:
    // - network failures (promise rejection from fetch)
    // - the thrown error for a bad HTTP status
    // - JSON parsing errors
    console.error('Failed to fetch user:', error);
  } finally {
    console.log("done");   // like .finally() — runs in every case
  }
}
```

:::note Important note about `fetch()`
A common gotcha: `fetch()` only rejects on **network failures**, not on HTTP error statuses like 404 or 500. You need to check `response.ok` manually and `throw` an error if needed. And yes — rejected promises go into the `catch` block, along with any other errors thrown during the `try` block!
:::

## 7.6 Important rules

1. **`await` only works inside `async` functions** (or at the top level of ES modules). In a normal function it's an error:
   `SyntaxError: await is only valid in async functions and the top level bodies of modules`.
2. **`await` pauses execution of *that* function**, but it doesn't block the entire program.
3. **You await promises.** If you `await` a normal value, it is simply wrapped in a resolved promise: `await 5` gives `5`.

:::mistake Forgetting `await`
```js
async function getData() {
  const response = fetch("/api/data");   // ❌ forgot await → response is a Promise!
  console.log(response.ok);              // undefined
  const data = response.json();          // ❌ TypeError: not a function
}
```
Without `await` you get the **ticket** (the Promise), not the result. Fix: `const response = await fetch("/api/data");`.
:::

## 7.7 Sequential vs parallel

**Sequential (slower):**

```js
const user = await fetchUser();     // wait…
const posts = await fetchPosts();   // …then wait again
```

**Parallel (faster):**

```js
const [user, posts] = await Promise.all([
  fetchUser(),
  fetchPosts(),
]);
```

In the sequential version, `fetchPosts()` doesn't even **start** until `fetchUser()` has finished. In the parallel version, **both start immediately**, and we wait for both together.

[[fig:seq-vs-par|If each request takes 2 s: sequential = 2 + 2 = 4 s; parallel = about 2 s.]]

:::def `Promise.all([p1, p2, …])`
- Takes an **array of promises** and returns **one** promise.
- It **fulfills** when **all** of them are fulfilled — with an **array of results**, in the **same order** as the input (not the order in which they finished).
- It **rejects** as soon as **any one** of them rejects (with that error) — "fail fast".
:::

You can measure the difference yourself:

```js
const wait = (ms, value) => new Promise(resolve => setTimeout(() => resolve(value), ms));

async function sequential() {
  console.time("sequential");
  const a = await wait(1000, "A");
  const b = await wait(1000, "B");
  console.timeEnd("sequential");   // sequential: ~2000 ms
}

async function parallel() {
  console.time("parallel");
  const [a, b] = await Promise.all([wait(1000, "A"), wait(1000, "B")]);
  console.timeEnd("parallel");     // parallel: ~1000 ms
}
```

**When to use which?** Use **sequential** when a step **needs the result** of the previous one (like the Zomato order: you can't cook before payment). Use **parallel** when the tasks are **independent** (like loading a user's comments, photos and chats). This also solves "Problem 8" of callback hell from Chapter 4.

## 7.8 Common patterns

**Handling multiple operations:**

```js
async function loadDashboard() {
  try {
    const [user, notifications, stats] = await Promise.all([
      getUser(),
      getNotifications(),
      getStats(),
    ]);
    return { user, notifications, stats };
  } catch (error) {
    console.error('Failed to load dashboard:', error);
  }
}
```

(`{ user, notifications, stats }` is a shortcut for `{ user: user, notifications: notifications, stats: stats }`.)

**Conditional awaits:**

```js
async function getData(useCache) {
  if (useCache) {
    return getCachedData();
  }
  return await fetchFreshData();
}
```

The beauty of `async`/`await`: asynchronous code becomes much easier to read and reason about, especially when you have complex logic with multiple asynchronous operations.

## 7.9 Day 20 code, experiment by experiment

:::day Day 20 — `index.html` + `style.css` + `index.js`
The page has a heading and an empty container. The CSS turns every user into a **card**:

```html title="03JS/Day20/index.html"
<head>
    <link rel="stylesheet" href="./style.css">
</head>
<body>
    <h1>Github User</h1>
    <div id="first"></div>
</body>
<script src="./index.js"></script>
```
:::

The important CSS rules (from `style.css`):

```css title="03JS/Day20/style.css (important parts)"
body   { height: 100vh; background-color: black; color: white; }
h1     { font-size: 40px; text-align: center; margin: 20px 0; }

#first {                      /* the container of all cards */
    display: flex;            /* put cards in a row...      */
    flex-wrap: wrap;          /* ...and wrap to new lines   */
    justify-content: center;
    gap: 30px;
    width: 80%;
    margin: auto;
}

.user {                       /* one card */
    width: 200px;
    text-align: center;
    padding: 10px;
    border: 2px solid white;
    border-radius: 5px;
    transition: transform 1s ease;
}
.user:hover { transform: scale(1.2); }   /* grows 1.2x when the mouse is on it */

img { width: 100%; height: 200px; object-fit: cover; }
a   { text-decoration: none; color: orange; }
```

### Experiment 1 — `greet()`

Explained in section 7.2 above.

### Experiment 2 — GitHub user cards with `async`/`await`

```js title="Day 20 · index.js — experiment 2"
async function github() {

    try {
        const response = await fetch("https://api.github.com/users");
        if (!response.ok) {
            throw new Error("Data is not persent");
        }

        const data = await response.json();
        // console.log(data);

        const parent = document.getElementById("first");

        for (let user of data) {

            const element = document.createElement("div");
            element.classList.add("user");

            const image = document.createElement('img');
            image.src = user.avatar_url;

            const userName = document.createElement('h2');
            userName.textContent = user.login;

            const anchor = document.createElement('a');
            anchor.href = user.html_url;
            anchor.textContent = "Visit Profile";

            element.append(image, userName, anchor);
            parent.append(element);
        }
    }
    catch (error) {
        console.log("error");
    }
}

github();

console.log("Hello Ji kaise ho");
```

**Step by step:**

1. `await fetch(...)` — pause `github()` until GitHub answers; `response` is the `Response` object.
2. `if (!response.ok) throw ...` — turn an HTTP error (404, 500…) into a real error → jumps to `catch`.
3. `await response.json()` — pause again until the body is parsed; `data` is an array of users.
4. `for (let user of data)` — for each user object (a `for…of` loop, like C++ range-for):
    - create a `<div>` and give it the CSS class `user` (`classList.add`) → it becomes a card;
    - create an `<img>` with the user's avatar, an `<h2>` with their `login` name, and an `<a>` link to their GitHub profile (`html_url`) with the text "Visit Profile";
    - `element.append(image, userName, anchor)` — `append` can add **several** children at once;
    - `parent.append(element)` — put the finished card inside `#first`.
5. Any problem (network error, bad status, parsing error) jumps to `catch`, which prints `"error"`.

```output
Hello Ji kaise ho   #> printed FIRST!
```

**Why is `"Hello Ji kaise ho"` printed first?** `github()` runs until its first `await`, then **pauses** and returns a (pending) promise. The main code continues and prints the message. When GitHub replies, `github()` resumes and builds the cards. `await` pauses the **function**, not the program.

[[fig:github-cards|Roughly what the page looks like: a centred heading and one card per user, wrapping onto new rows. The user names shown are examples.]]

### Experiment 3 — the Zomato app with `async`/`await`

The four step functions (`placedOrder`, `preparingOrder`, `pickupOrder`, `deliverOrder`) are **exactly the same** as in Day 19 — each one returns a Promise. Only the code that **uses** them changes:

```js title="Day 20 · index.js — experiment 3"
async function ordering() {

    try {
        const response1 = await placedOrder(orderDetail);
        const response2 = await preparingOrder(response1);
        const response3 = await pickupOrder(response2);
        const response4 = await deliverOrder(response3);

        console.log(response4);
    }
    catch (error) {
        console.log("Error: ", error);
    }
}

ordering();
```

- Each `await` waits for one step's promise and gives us its value (the updated `orderDetail`).
- The steps run **in order** because each line waits for the previous one — exactly what we need (sequential!).
- If any step **rejects**, `await` **throws**, the remaining lines are skipped, and `catch` prints the reason — e.g. `Error:  Payment is failed`.
- The output is the same as the Day 19 version, just without the `"I am doing cleanup"` line (there is no `finally` here — you could add `finally { console.log("I am doing cleanup"); }`).

### Experiment 4 — `Promise.all` (the active code in the file)

```js title="Day 20 · index.js — experiment 4"
async function userDetail(params) {

    // const comment = await fetch("userComment");
    // const photos = await fetch("userPhoto");
    // const chat = await fetch("chat");

    const [comment, photos, chat] = await Promise.all([
        fetch("userComment"),
        fetch("photo"),
        fetch("chat"),
    ]);
}
```

- The commented lines are the **sequential** way: the photo request would start only after the comment request finished, and so on.
- `Promise.all` starts **all three requests at the same time** and waits until all three have finished. The three results come back in an array, and **array destructuring** puts them into `comment`, `photos` and `chat` (in the same order as the input array).
- `"userComment"`, `"photo"` and `"chat"` are just **example addresses** to show the idea (they don't exist on a real server). The function is also never called in the file, and `params` isn't used — it's a demo of the pattern.

## 7.10 One app, three styles

| | Callbacks (Day 18) | Promises (Day 19) | `async`/`await` (Day 20) |
|---|---|---|---|
| Step function | takes a `Callback` | returns a Promise | returns a Promise (same as Day 19) |
| Running the steps | nested callbacks | `.then().then()…` chain | `await` line by line |
| Shape of the code | pyramid → | flat chain | looks like normal sync code |
| Handling errors | at every level (hard) | one `.catch()` | one `try`/`catch` |
| Cleanup | manual | `.finally()` | `finally { }` |
| Getting data out | hard (scope problem) | inside `.then` | normal variables (`response1`…) |

```js
// 1. Callbacks (Day 18) — nested
placedOrder(orderDetail, (o) =>
  preparingOrder(o, (o) =>
    pickupOrder(o, (o) =>
      deliverOrder(o))));

// 2. Promises (Day 19) — a flat chain
placedOrder(orderDetail)
  .then(preparingOrder)
  .then(pickupOrder)
  .then(deliverOrder);

// 3. async / await (Day 20) — reads like normal code (inside an async function)
const o1 = await placedOrder(orderDetail);
const o2 = await preparingOrder(o1);
const o3 = await pickupOrder(o2);
await deliverOrder(o3);
```

## 7.11 Things to Remember

:::remember
- `async` function → **always returns a Promise**. `return x` → fulfilled with `x`; `throw e` → rejected with `e`.
- `await promise` → pauses **this function** until the promise settles: gives the **value**, or **throws** the error.
- `await` does **not** block the program: code after the call to an async function runs **before** the code after its first `await`.
- Use `try`/`catch`/`finally` for errors and cleanup. It catches rejected promises, thrown errors and runtime errors.
- `await` works only inside `async` functions (or top-level modules). Forgetting `await` gives you a **Promise** instead of the value.
- `fetch` doesn't reject on 404/500 → check `response.ok`.
- **Sequential** awaits for dependent steps; **`Promise.all`** for independent ones (faster, results in input order, fails fast).
- `async`/`await` is just **nicer syntax for Promises** — the event loop works exactly the same.
:::

:::quiz
1. What does `async function f() { return 10; }` return when you call `f()`?
2. What is printed, and in which order?

    ```js
    async function f() {
      console.log("B");
      await null;
      console.log("D");
    }
    console.log("A");
    f();
    console.log("C");
    ```

3. Two independent requests take 3 s each. How long do sequential awaits take? And `Promise.all`?
4. In Day 20's `ordering()`, the restaurant rejects with `"Food item is not persent at restaurant"`. What is printed after `Your food preparation started of Pizza,biryani,coke`?
5. Why does `"Hello Ji kaise ho"` appear before the GitHub cards in Day 20?
:::

:::answer
1. A **Promise** that is fulfilled with `10` (use `await f()` or `f().then(...)` to get 10).
2. `A`, `B`, `C`, `D` — `f` runs synchronously until `await`, then the main code continues; `D` runs later as a microtask.
3. Sequential ≈ **6 s**; `Promise.all` ≈ **3 s**.
4. `Error:  Food item is not persent at restaurant` — `await` throws, the rest of the `try` is skipped, `catch` runs.
5. `github()` pauses at its first `await`; meanwhile the main code prints the message. The cards are built later, when the data arrives.
:::
