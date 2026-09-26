:::chapter 5 | Promises | Lecture 19 · Day 19 code
- What a **Promise** is (a placeholder for a future value)
- The 3 states: **pending**, **fulfilled**, **rejected**
- Creating promises with `new Promise((resolve, reject) => …)`
- Consuming them with `.then()`, `.catch()`, `.finally()`
- **Promise chaining** — the cure for callback hell
- `fetch()`, the `Response` object and `response.json()`
- The **Day 19** code: GitHub avatars + Zomato with Promises
:::

## 5.1 What is a Promise?

:::def Promise
The `Promise` object represents the **eventual completion (or failure)** of an asynchronous operation and its resulting value.

In simple words: a Promise is a **placeholder** — an object that says *"I don't have the value yet, but I will give it to you later (or tell you why I couldn't)"*.
:::

**Promise characteristics:**

1. **A Promise is an object** — you can store it in a variable, pass it around, return it from a function.
2. **It represents a future value** — the value isn't available yet, but will be.
3. **It has states** — it changes state over time (pending → fulfilled or rejected).
4. **One-time use** — once it is settled, it never changes again.

:::analogy Tracking an online order
When you order something online, you **immediately** get an **Order ID** — that's the Promise. At first the status is *Pending* (being packed, shipped…). Later it becomes either **Delivered** (you get the parcel = the **value**) or **Cancelled** (you get a **reason**, like "out of stock"). Once it is delivered or cancelled, the status never changes again.
:::

:::cpp C++ has promises too: `std::promise` / `std::future`
```cpp
std::promise<int> p;
std::future<int> f = p.get_future();

std::thread worker([&p] {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    p.set_value(42);           // like resolve(42)   (set_exception is like reject)
});

int x = f.get();               // ⛔ BLOCKS this thread until the value arrives
worker.join();
```
```js
const p = new Promise(resolve => setTimeout(() => resolve(42), 1000));
p.then(x => console.log(x));          // ✅ does NOT block — "call this later"
console.log("I am not blocked!");     // printed first, then 42
```
Same idea — a *producer* sets the value later, a *consumer* reads it. The **big difference**: C++ `future.get()` **blocks** the thread. JavaScript has no `.get()` — you give a callback to `.then()`, and the single thread keeps working.
:::

## 5.2 The three states of a Promise

A Promise is in **exactly one** of three states at any time:

[[fig:promise-states|The life of a Promise. It starts **pending**, and settles **once** — either fulfilled (with a value) or rejected (with a reason).]]

| State | Meaning | Caused by | Which handler runs |
|---|---|---|---|
| **Pending** | "I'm working on it…" (initial state) | — | none yet |
| **Fulfilled** | "I got the result!" | calling `resolve(value)` | `.then(...)` |
| **Rejected** | "Something went wrong!" | calling `reject(reason)` (or an error is thrown) | `.catch(...)` |

Once a promise is **fulfilled or rejected**, we say it is **settled** — final, it can never change again.

```js
// Create a promise
const myPromise = new Promise((resolve, reject) => {
  // At this moment: the promise is PENDING
  setTimeout(() => {
    const success = true;
    if (success) {
      resolve("Success!");   // → the promise becomes FULFILLED
    } else {
      reject("Failed!");     // → the promise becomes REJECTED
    }
  }, 2000);
});
// myPromise is PENDING for 2 seconds, then becomes FULFILLED with the value "Success!"
```

### A promise can settle only ONCE

```js
const promise = new Promise((resolve, reject) => {
  console.log("State: PENDING");
  setTimeout(() => {
    resolve("Done");
    console.log("State: FULFILLED");
    // ❌ These do nothing — the promise is already settled!
    reject("Error");    // ignored!
    resolve("Again");   // ignored!
  }, 1000);
});

promise.then(value => console.log("Value:", value));
```

```output
State: PENDING
State: FULFILLED   #> 1 second later
Value: Done
```

**Key point:** only the **first** `resolve` or `reject` counts. Everything after it is ignored.

## 5.3 Creating a Promise

```js
const promise = new Promise((resolve, reject) => {
  // this function is called the "executor"
  // it runs IMMEDIATELY when the promise is created
});
```

The **executor** function receives two functions from JavaScript:

- **`resolve(value)`** — call it when the operation **succeeds**.
- **`reject(reason)`** — call it when the operation **fails**.

:::mistake The executor runs immediately (synchronously)!
Many students think the code inside `new Promise(...)` runs "later". It doesn't — it runs **right away**. Only the `.then` callbacks run later.

```js
console.log("1. before");
const p = new Promise((resolve) => {
  console.log("2. inside the executor — runs immediately!");
  resolve("done");
});
console.log("3. after");
p.then(value => console.log("4. then:", value));
```
```output
1. before
2. inside the executor — runs immediately!
3. after
4. then: done
```
:::

### Five small examples (from the lecture)

```js
// Example 1: a promise that immediately resolves with "Hello!"
const simplePromise = new Promise((resolve, reject) => {
  resolve("Hello!");
});

// Example 2: a promise with setTimeout
const delayedPromise = new Promise((resolve, reject) => {
  setTimeout(() => {
    resolve("Done after 2 seconds");
  }, 2000);
});
```

```js
// Example 3: a promise with conditional logic
function checkAge(age) {
  return new Promise((resolve, reject) => {
    if (age >= 18) {
      resolve("Access granted");
    } else {
      reject("Access denied - Too young");
    }
  });
}
const ageCheck = checkAge(20);   // returns a promise
```

```js
// Example 4: real-world style — simulating an API call
function fetchUserData(userId) {
  return new Promise((resolve, reject) => {
    console.log(`Fetching user ${userId}...`);
    setTimeout(() => {
      // Simulate a successful API response
      const user = { id: userId, name: "John Doe", email: "john@example.com" };
      resolve(user);
    }, 2000);
  });
}

// Example 5: a promise with error handling
function divideNumbers(a, b) {
  return new Promise((resolve, reject) => {
    if (b === 0) {
      reject("Cannot divide by zero!");
    } else {
      resolve(a / b);
    }
  });
}
```

Notice the **most common pattern** (Examples 3, 4, 5): *a normal function that **returns** a new Promise*. The Day 19 Zomato code uses exactly this pattern.

## 5.4 Consuming a Promise: `.then()`, `.catch()`, `.finally()`

Once you have a promise, you need to **consume** it to get the result.

```js
promise.then((result) => {
  // runs when the promise is FULFILLED
  console.log(result);
});

promise.catch((error) => {
  // runs when the promise is REJECTED
  console.error(error);
});

promise.finally(() => {
  // runs ALWAYS — whether fulfilled or rejected
  console.log("Promise settled");
});
```

### Complete example

```js
function fetchData() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const success = Math.random() > 0.5;   // 50% chance
      if (success) {
        resolve({ data: "Some data" });
      } else {
        reject("Network error");
      }
    }, 1000);
  });
}

// Consuming the promise:
fetchData()
  .then((result) => {
    console.log("Success:", result);
  })
  .catch((error) => {
    console.error("Error:", error);
  })
  .finally(() => {
    console.log("Request completed");
  });
```

:::cols
```output title="If it succeeds"
Success: { data: 'Some data' }
Request completed
```
|||
```output title="If it fails"
Error: Network error
Request completed
```
:::

`Math.random()` gives a random decimal between 0 (included) and 1 (not included), so `Math.random() > 0.5` is `true` about half of the time.

Using `checkAge` from Example 3:

```js
checkAge(20)
  .then(message => console.log(message))    // Access granted
  .catch(error => console.log(error));

checkAge(15)
  .then(message => console.log(message))
  .catch(error => console.log(error));      // Access denied - Too young
```

### `.then()` can take TWO functions

```js
promise.then(
  (result) => { console.log("Success:", result); },   // success handler
  (error) => { console.error("Error:", error); }       // error handler (optional)
);

// But it's better (clearer) to use .catch() for errors:
promise
  .then((result) => { console.log("Success:", result); })
  .catch((error) => { console.error("Error:", error); });
```

## 5.5 Promise chaining — the power of Promises

This is where promises truly shine: **flat, sequential async operations** — no pyramid!

:::def The 4 rules of chaining
1. **`.then()` always returns a NEW promise.** That's why you can write `.then(...).then(...)`.
2. **Whatever you `return`** from a `.then` callback becomes the value for the **next** `.then`.
3. If you return a **Promise**, the next `.then` **waits** for it to settle and receives its value.
4. If anything **throws** (or a promise **rejects**), JavaScript **skips** the following `.then`s and jumps to the nearest **`.catch()`**.
:::

### Example 1: basic chaining

```js
Promise.resolve(5)
  .then((value) => {
    console.log(value);   // 5
    return value * 2;
  })
  .then((value) => {
    console.log(value);   // 10
    return value + 3;
  })
  .then((value) => {
    console.log(value);   // 13
  });
```

`Promise.resolve(5)` is a shortcut for *"a promise that is already fulfilled with 5"* (and `Promise.reject(x)` makes an already-rejected one).

[[fig:promise-chain|Top: each `.then` receives what the previous one returned. Bottom: when a step throws, the error skips all the remaining `.then`s and lands in `.catch`.]]

### Example 2: chaining real async steps

```js
function step1() {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log("Step 1 complete");
      resolve("Result from step 1");
    }, 1000);
  });
}
function step2(previousResult) {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log("Step 2 complete, got:", previousResult);
      resolve("Result from step 2");
    }, 1000);
  });
}
function step3(previousResult) {
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log("Step 3 complete, got:", previousResult);
      resolve("Final result");
    }, 1000);
  });
}

// ✅ Clean chain (no nesting!)
step1()
  .then((result1) => {
    return step2(result1);     // returning a promise → the next .then waits for it
  })
  .then((result2) => {
    return step3(result2);
  })
  .then((finalResult) => {
    console.log("All done:", finalResult);
  })
  .catch((error) => {
    console.error("Something failed:", error);
  });
```

```output
Step 1 complete                              #> 1 s
Step 2 complete, got: Result from step 1     #> 2 s
Step 3 complete, got: Result from step 2     #> 3 s
All done: Final result
```

Even cleaner — you can pass the function itself, because `.then(step2)` will call `step2(result)` for you:

```js
step1()
  .then(step2)
  .then(step3)
  .then((finalResult) => console.log("All done:", finalResult))
  .catch((error) => console.error("Something failed:", error));
```

### Errors jump to `.catch()`

```js
Promise.resolve(1)
  .then(x => { console.log("step 1:", x); return x + 1; })
  .then(x => { throw new Error("Boom at step 2"); })
  .then(x => { console.log("step 3 (skipped!)"); })
  .catch(err => console.log("Caught:", err.message))
  .then(() => console.log("the chain continues after catch"));
```

```output
step 1: 1
Caught: Boom at step 2
the chain continues after catch
```

One `.catch()` at the end handles errors from **every** step above it. Compare that with callback hell, where we had to check for errors at every level!

:::mistake Forgetting to `return` inside `.then`
```js
fetch(url)
  .then(response => { response.json(); })   // ❌ braces but no return!
  .then(data => console.log(data));          // undefined
```
Fix: `.then(response => response.json())` (no braces) or `.then(response => { return response.json(); })`.
:::

## 5.6 The `.finally()` method

`.finally()` runs **regardless** of whether the promise succeeds or fails. Use it for **cleanup code** that must always run:

- hide loading spinners
- close database connections
- re-enable buttons
- stop timers
- release resources

```js
// Example 1: loading spinner
function fetchData() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const success = Math.random() > 0.5;
      if (success) {
        resolve({ data: "Data loaded" });
      } else {
        reject("Failed to load");
      }
    }, 2000);
  });
}

// Show spinner
console.log("🔄 Loading...");
let isLoading = true;

fetchData()
  .then((result) => {
    console.log("✅ Success:", result);
  })
  .catch((error) => {
    console.error("❌ Error:", error);
  })
  .finally(() => {
    // Always runs — hide the spinner
    isLoading = false;
    console.log("⏹️ Loading stopped");
  });
```

```js
// Example 2: database connection (connectToDatabase is imaginary)
function queryDatabase(query) {
  let connection;
  return connectToDatabase()
    .then((conn) => {
      connection = conn;
      return connection.execute(query);
    })
    .then((results) => {
      console.log("Query results:", results);
      return results;
    })
    .catch((error) => {
      console.error("Query failed:", error);
      throw error;
    })
    .finally(() => {
      // Always close the connection
      if (connection) {
        connection.close();
        console.log("Connection closed");
      }
    });
}
```

### Key characteristics of `.finally()`

1. **It doesn't receive any arguments** — it doesn't know if the promise succeeded or failed.

    ```js
    promise
      .then((result) => console.log("Result:", result))   // has the result
      .catch((error) => console.log("Error:", error))     // has the error
      .finally(() => console.log("Done"));                // no arguments!
    ```

2. **It doesn't change the promise's value** — the value passes through it.

    ```js
    Promise.resolve("Original")
      .finally(() => {
        return "Modified";            // ignored!
      })
      .then((value) => {
        console.log(value);           // "Original"
      });
    ```

3. **But if `.finally()` throws, that error propagates.**

    ```js
    Promise.resolve("Success")
      .finally(() => {
        throw new Error("Cleanup failed");
      })
      .then((value) => {
        console.log(value);           // SKIPPED
      })
      .catch((error) => {
        console.error(error.message); // "Cleanup failed"
      });
    ```

## 5.7 Promises and the event loop

Remember Chapter 3: **`.then`, `.catch` and `.finally` callbacks are microtasks.** They go into the **microtask queue**, which the event loop empties **before** it runs any `setTimeout` callback. That's why `Promise.resolve().then(...)` prints before `setTimeout(..., 0)`.

Also remember: a `.then` callback **never** runs immediately, even if the promise is already fulfilled. It always waits until the current synchronous code has finished.

## 5.8 `fetch()` — a real Promise from the browser

`fetch(url)` asks the browser to send a network request. It **immediately** returns a Promise, which later **fulfills with a `Response` object**.

[[fig:fetch-flow|Your code talks to GitHub's server. `p1` stays pending until the server answers (fulfilled) — or until it's clear the request can't be completed at all (rejected).]]

The `Response` object is **not** your data yet. The body arrives as a stream of text, and reading + parsing it also takes time — so **`response.json()` returns another Promise**. That's why you always see **two** `.then` steps with `fetch`:

```js
fetch("https://api.github.com/users")
  .then(response => {
    // response is a Response object: status, ok, headers, body...
    console.log(typeof response);   // "object"
    return response.json();         // read the body + parse JSON → a Promise
  })
  .then(data => {
    // Now 'data' is a real JavaScript array of user objects
    console.log(data[0].login);     // "mojombo" (the first GitHub user)
  });
```

Useful parts of a `Response`:

| Property / method | What it gives you |
|---|---|
| `response.ok` | `true` if the status is 200–299 (success), otherwise `false` |
| `response.status` | the HTTP status code: `200`, `404` (not found), `500` (server error)… |
| `response.json()` | a Promise → the body parsed as JSON (a JS object/array) |
| `response.text()` | a Promise → the body as a plain string |

:::mistake `fetch()` does NOT reject on 404 or 500!
`fetch()` only rejects on **network failures** (no internet, DNS failure, server unreachable). If the server **answers** with an error status like 404 or 500, the promise is still **fulfilled** — with `response.ok === false`. You must check it yourself and `throw`:

```js
fetch(url)
  .then((response) => {
    if (!response.ok) {
      // → jumps to .catch:
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then((data) => console.log(data))
  .catch((error) => console.log(error.message));
```
The Day 19 code does exactly this.
:::

## 5.9 Day 19 code, experiment by experiment

:::day Day 19 — `03JS/Day19/index.html` + `index.js`
The page is just an empty box where the code will put the GitHub avatars:

```html title="03JS/Day19/index.html"
<body>
    <div id="first">
    </div>
</body>
<script src="./index.js"></script>
```
:::

### Experiment 1 — `fetch` with two separate promises

```js title="Day 19 · index.js — experiment 1"
const p1 = fetch("https://api.github.com/users");

// fullfilled , reject

const p2 = p1.then((response) => {
   return response.json();
})

p2.then((data) => {
    console.log(data);
})
```

- `p1` is the Promise from `fetch`. It will be **fulfilled** with a `Response` (or **rejected** if there's no network — that's what the teacher's comment `// fullfilled , reject` reminds us).
- `p1.then(...)` returns a **new** promise, `p2`. Because the callback **returns** `response.json()` (itself a promise), `p2` waits for the JSON parsing and is fulfilled with the **data**.
- `p2.then(...)` finally prints the data: an array of 30 GitHub users.

```output label="Console (browser)"
(30) [{…}, {…}, {…}, …]
  0: {login: 'mojombo', id: 1, avatar_url: '…', html_url: '…', …}
  1: {login: 'defunkt', id: 2, avatar_url: '…', html_url: '…', …}
  …
```

### Experiment 2 — the same thing, chained

```js title="Day 19 · index.js — experiment 2"
fetch("https://api.github.com/users")
.then((response) => {
   return response.json();
})
.then((data) => {
    console.log(data);
})
```

Same result, but without the extra variables `p1` and `p2`. This is how you will normally write it.

### Experiment 3 — making our own Promise

```js title="Day 19 · index.js — experiment 3"
const p1 = new Promise((resolve, reject) => {

    resolve({
        name: "Rohit",
        age: 30,
    });
})

p1.then((response) => {
    console.log(response);
}).catch((error) => {
    console.log(error);
})
```

```output
{ name: 'Rohit', age: 30 }
```

The executor calls `resolve` with an object, so the promise is **fulfilled** and `.then` receives that object. `.catch` doesn't run. Try changing `resolve({...})` to `reject("Something went wrong")` — now only `.catch` runs and prints the message.

### Experiment 4 — show GitHub avatars on the page

```js title="Day 19 · index.js — experiment 4"
fetch("https://api.github.com/users")
.then((response) => {

    console.log(response);
    if (!response.ok) {
        throw new Error("Data is not persent in server");
    }
    return response.json();
})
.then((data) => {
    // console.log(data);

    const parent = document.getElementById("first");

    for (let i = 0; i < data.length; i++) {
        const image = document.createElement('img');
        image.src = data[i].avatar_url;
        image.style.height = "40px";
        image.style.width = "40px";

        parent.append(image);
    }
})
.catch((error) => {
    const parent = document.getElementById("first");
    parent.textContent = error.message;
})
```

[[fig:avatars-flow|The path through experiment 4: success draws 30 avatars; an HTTP error or a network error ends in `.catch`, which writes the message on the page.]]

What each DOM line does:

| Code | Meaning |
|---|---|
| `document.getElementById("first")` | find the `<div id="first">` on the page |
| `document.createElement('img')` | create a brand-new `<img>` element (not on the page yet) |
| `image.src = data[i].avatar_url` | which picture to show (each user's avatar URL) |
| `image.style.height = "40px"` | set CSS directly on the element (40 × 40 pixels) |
| `parent.append(image)` | put the image **inside** the div → now it appears on the page |
| `parent.textContent = error.message` | replace everything in the div with the error text |

**Result:** 30 small avatars appear in a row. Now try these experiments:

- Change the URL to `https://api.github.com/userss` → GitHub answers **404** → `response.ok` is `false` → we `throw` → `.catch` puts **"Data is not persent in server"** on the page.
- Turn off your internet → `fetch` **rejects** → `.catch` shows the browser's message, e.g. **"Failed to fetch"**.

The line `console.log(response)` shows the Response object, something like `Response {type: 'cors', url: 'https://api.github.com/users', status: 200, ok: true, …}`.

### Experiment 5 — JSON

The next part of the file (`JSON.stringify` / `JSON.parse`) is explained in **Chapter 6**.

### Experiment 6 — the Zomato app, rebuilt with Promises

This is the Day 18 app again, but now **each step returns a Promise** instead of taking a callback. There is one more new idea: steps can now **fail**. `Math.random()` is used to simulate failures.

```js title="Day 19 · index.js — experiment 6 (the active code)"
const orderDetail = {
    orderId: 123123,
    food: ["Pizza", "biryani", "coke"],
    cost: 620,
    customer_name: "Rohit",
    customer_location: "Dwarka",
    restaurant_location: "Delhi"
}

function placedOrder(orderDetail) {
    console.log(`${orderDetail.cost} Payment is in progress`);

    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.1) {                  // 90% chance of success
                console.log("Payment is received and order get placed");
                orderDetail.status = true;
                resolve(orderDetail);                   // success: pass the order on
            }
            else {
                reject("Payment is failed");            // failure: give a reason
            }
        }, 3000)
    })
}

function preparingOrder(orderDetail) {
    console.log(`Your food preparation started of ${orderDetail.food}`);

    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.05) {                 // 95% chance of success
                console.log("Your order is now prepared");
                orderDetail.token = 123;
                resolve(orderDetail);
            }
            else {
                reject("Food item is not persent at restaurant");
            }
        }, 3000);
    })
}
```

```js title="Day 19 · index.js — experiment 6 (continued)"
function pickupOrder(orderDetail) {
    console.log(`Delivery boy is on way to pickup order from ` +
                `${orderDetail.restaurant_location} `);

    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.05) {                 // 95% chance of success
                console.log("I have picked up the order");
                orderDetail.received = true;
                resolve(orderDetail);
            }
            else {
                reject("Delivery boy Unable to reach restaurant")
            }
        }, 3000);
    })
}

function deliverOrder(orderDetail) {
    console.log(`I am on my way to deliver order ${orderDetail.customer_location}`);

    return new Promise((resolve, reject) => {
        setTimeout(() => {
            console.log("Order delivered succesfully");
            orderDetail.delivery = true;
            resolve(orderDetail);                       // this step never fails
        }, 3000)
    })
}

placedOrder(orderDetail)
.then((orderDetail) => preparingOrder(orderDetail))
.then((orderDetail) => pickupOrder(orderDetail))
.then((orderDetail) => deliverOrder(orderDetail))
.then((orderDetail) => {
    console.log(orderDetail);
})
.catch((error) => {
    console.log("Error: ", error);
}).
finally(() => {
    console.log("I am doing cleanup");
})
```

**How it works:**

- Each function prints its first message **immediately**, then returns a **new Promise** that settles after 3 s.
- `.then((orderDetail) => preparingOrder(orderDetail))` **returns** the next step's promise, so the next `.then` **waits** for it (rule 3 of chaining). You could also write it as `.then(preparingOrder)`.
- If **any** step calls `reject(...)`, all the remaining `.then`s are **skipped** and `.catch` prints the reason.
- `.finally` runs at the very end in **both** cases.
- The strange-looking `}).` + new line + `finally(` is fine: JavaScript doesn't care that the dot is at the end of the line.

```output title="When everything succeeds (verified by running the file)"
620 Payment is in progress                           #> 0 s
Payment is received and order get placed             #> 3 s
Your food preparation started of Pizza,biryani,coke  #> 3 s
Your order is now prepared                           #> 6 s
Delivery boy is on way to pickup order from Delhi    #> 6 s
I have picked up the order                           #> 9 s
I am on my way to deliver order Dwarka               #> 9 s
Order delivered succesfully                          #> 12 s
{
  orderId: 123123,
  food: [ 'Pizza', 'biryani', 'coke' ],
  cost: 620,
  customer_name: 'Rohit',
  customer_location: 'Dwarka',
  restaurant_location: 'Delhi',
  status: true,
  token: 123,
  received: true,
  delivery: true
}
I am doing cleanup
```

```output title="If the restaurant fails (at 6 s)"
620 Payment is in progress
Payment is received and order get placed
Your food preparation started of Pizza,biryani,coke
Error:  Food item is not persent at restaurant
I am doing cleanup
```

```output title="If the payment fails (at 3 s)"
620 Payment is in progress
Error:  Payment is failed
I am doing cleanup
```

(There are **two** spaces after `Error:` because the string `"Error: "` already ends with a space, and `console.log` adds another space between its arguments.)

How often does the whole order succeed? 0.9 × 0.95 × 0.95 ≈ 0.81, so about **81 %** of the time. Run the file several times and you'll see different endings!

### Callbacks (Day 18) vs Promises (Day 19)

| | Day 18 — callbacks | Day 19 — Promises |
|---|---|---|
| Function signature | `placedOrder(orderDetail, Callback)` | `placedOrder(orderDetail)` → **returns a Promise** |
| "I'm done, here's the data" | `Callback(orderDetail)` | `resolve(orderDetail)` |
| "I failed, here's why" | no clean way | `reject("Payment is failed")` |
| Shape of the code | nested pyramid | **flat** chain of `.then` |
| Error handling | at every level | **one** `.catch` at the end |
| Cleanup | manual | `.finally` |

## 5.10 Things to Remember

:::remember
- A **Promise** is an object = a placeholder for a future value. States: **pending → fulfilled** (`resolve`) **or rejected** (`reject`). Settled = final.
- Only the **first** `resolve`/`reject` counts.
- The **executor** inside `new Promise(...)` runs **immediately**; `.then/.catch/.finally` callbacks run **later** (as microtasks).
- `.then` for success, `.catch` for failure, `.finally` for cleanup (no arguments, value passes through).
- **`.then()` returns a new promise.** Return a value → next `.then` gets it. Return a promise → next `.then` waits for it.
- A thrown error or rejection **skips** to the nearest `.catch()`. One `.catch` at the end handles the whole chain.
- **Always `return`** inside `.then` when the next step needs the value.
- `fetch()` → Promise of a `Response`; `response.json()` → another Promise → the data.
- `fetch()` **doesn't reject on 404/500** — check `response.ok` and `throw`.
- Unlike C++ `future.get()`, nothing in a Promise **blocks** the thread.
:::

:::quiz
1. What is printed?

    ```js
    const p = new Promise((resolve, reject) => {
      resolve("A");
      reject("B");
      resolve("C");
    });
    p.then(v => console.log(v)).catch(e => console.log(e));
    ```

2. What is printed?

    ```js
    Promise.resolve(2)
      .then(x => x * 3)
      .then(x => { console.log(x); })
      .then(x => console.log(x));
    ```

3. In what order are these printed?

    ```js
    console.log("start");
    new Promise(r => { console.log("executor"); r(); })
      .then(() => console.log("then"));
    console.log("end");
    ```

4. The server answers `404 Not Found`. Does `fetch()` reject? What should you do?
5. In Day 19's Zomato code, the payment fails. Which messages are printed after `620 Payment is in progress`?
:::

:::answer
1. `A` — only the first `resolve`/`reject` counts.
2. `6`, then `undefined` — the second `.then` has `{ }` and no `return`.
3. `start`, `executor`, `end`, `then` — the executor runs immediately; `.then` is a microtask.
4. **No**, the promise is fulfilled with `response.ok === false`. Check `response.ok` and `throw` an error yourself.
5. `Error:  Payment is failed` and then `I am doing cleanup` — all the `.then` steps are skipped.
:::
