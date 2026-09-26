:::chapter 4 | Callbacks and Callback Hell | Lecture 18 · Day 18 code
- Why async code needs **callbacks**
- The **Zomato order** story: 4 steps, each takes time
- The full **Day 18** code, line by line, with a timeline
- Why we can't just call the steps one after another
- Why nesting works (Russian dolls)
- The **Pyramid of Doom** and the 8 problems of callback hell
:::

## 4.1 The problem: some work takes time

JavaScript is **single-threaded** — imagine a single worker who can do only **one** task at a time:

```js
console.log("Task 1");
console.log("Task 2");
console.log("Task 3");
// Executes line by line, top to bottom
```

But some operations take time:

- Making **API calls** (network requests)
- **Reading files**
- **Database queries**
- **Timers**

If JavaScript **waited** for these, everything would freeze:

```js
// ❌ BAD — imaginary blocking function: everything stops here
let data = waitForAPI();                  // blocks for 3 seconds
console.log(data);
console.log("This waits 3 seconds too!");
```

**The solution: asynchronous programming.** Don't wait — instead say *"call me back when you're done"*:

```js
// ✅ GOOD — non-blocking (fetchAPI is an imaginary async function)
fetchAPI(function () {
  console.log("Data received!");
});
console.log("I run immediately!");
```

```output
I run immediately!
Data received!   #> after the delay
```

This *"call me back"* function is a **CALLBACK**.

## 4.2 What exactly is a callback?

:::def Callback
A **callback** is a function that you pass **as an argument** to another function. The other function decides **when** to call it — immediately, or later when some work is finished.
:::

A **synchronous** callback — it is called right away:

```js
function greetUser(name, callback) {
  console.log(`Hi ${name}`);
  callback();                     // call the function we were given
}

greetUser("Rohit", () => console.log("Welcome to the course!"));
```

```output
Hi Rohit
Welcome to the course!
```

An **asynchronous** callback — it is called later:

```js
function afterTwoSeconds(callback) {
  setTimeout(() => {
    callback("done!");            // we can also PASS DATA to the callback
  }, 2000);
}

afterTwoSeconds(result => console.log("Result:", result));
console.log("waiting...");
```

```output
waiting...
Result: done!   #> 2 seconds later
```

Notice the second example: the function that **calls** the callback decides **what data to give it** (`"done!"`). The Day 18 code uses exactly this to pass the order details from one step to the next.

:::cpp Callbacks in C++
A callback in C++ is a **function pointer**, a **`std::function`**, or a **lambda** passed as an argument. You have used one with `std::sort`:

```cpp
// std::sort calls YOUR lambda back again and again:
std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });
```
The difference in JavaScript: callbacks are used for **time-based** work too ("call me after 3 seconds", "call me when the server replies"), because JavaScript's single thread must never wait.
:::

## 4.3 The real-world story: ordering food on Zomato

Think of ordering food online:

1. **Place order** → wait → payment done, order placed
2. **Prepare food** → wait → food ready
3. **Pick up order** → wait → the delivery partner has it
4. **Deliver order** → wait → food delivered 🎉

Each step:

- **takes time** (asynchronous),
- **depends on the previous step** finishing,
- **produces data** needed by the next step.

You can't prepare food before the order is placed! You can't pick up food before it's prepared! This is called **sequential async operations** — and it is the root of callback hell.

[[fig:zomato-steps|The four steps. One `orderDetail` object travels through all of them, and each step adds some information to it.]]

## 4.4 The Day 18 code, step by step

:::day Day 18 — `03JS/Day18/index.js`
This is the teacher's "Zomato application". Each step uses `setTimeout(…, 3000)` to **pretend** that it takes 3 seconds (a real app would talk to a payment gateway, the restaurant, the delivery partner…).
:::

### The order object

```js title="Day 18 · index.js"
// zomato application

const orderDetail = {
    orderId: 123123,
    food: ["Pizza", "biryani", "coke"],
    cost: 620,
    customer_name: "Rohit",
    customer_location: "Dwarka",
    restaurant_location: "Delhi"
}
```

This object holds all the order information. It will flow through **every** step, and each step will add a new property to it.

### Step 1: place the order (payment)

```js title="Day 18 · index.js"
function placedOrder(orderDetail, Callback) {
    console.log(`${orderDetail.cost} Payment is in progress`);

    setTimeout(() => {
        console.log("Payment is received and order get placed");
        orderDetail.status = true;       // ✅ add new data
        Callback(orderDetail);           // 👉 pass the order to the NEXT step
    }, 3000)
}
```

What happens when this function is called:

1. It **immediately** prints `620 Payment is in progress`.
2. It hands a **3-second timer** to the browser (this simulates the payment taking time) — and the function **returns right away**.
3. After 3 s, the timer's callback runs: it prints `Payment is received and order get placed` and adds `status: true` to the order.
4. It calls **`Callback(orderDetail)`** — *"payment is done, here is the updated order, do the next thing"*.

`Callback` is just the parameter's name (the teacher wrote it with a capital C). You could call it `next`, `done` or `cb` — it is simply *"the function to run after me"*.

### Step 2: prepare the food

```js title="Day 18 · index.js"
function preparingOrder(orderDetail, Callback) {
    console.log(`Your food preparation started of ${orderDetail.food}`);

    setTimeout(() => {
        console.log("Your order is now prepared");
        orderDetail.token = 123;         // ✅ add a token number
        Callback(orderDetail)            // 👉 pass to the next step
    }, 3000);
}
```

**Key point:** this function receives the `orderDetail` that **already has `status: true`** from the previous step. And `${orderDetail.food}` prints the array joined with commas: `Pizza,biryani,coke`.

### Step 3: pick up the order

```js title="Day 18 · index.js"
function pickupOrder(orderDetail, Callback) {
    console.log(`Delivery boy is on way to pickup order from ` +
                `${orderDetail.restaurant_location} `);

    setTimeout(() => {
        console.log("I have picked up the order");
        orderDetail.received = true;     // ✅ mark as picked up
        Callback(orderDetail);           // 👉 pass to the next step
    }, 3000);
}
```

Now `orderDetail` has `status`, `token` **and** `received`!

### Step 4: deliver the order

```js title="Day 18 · index.js"
function deliverOrder(orderDetail) {
    console.log(`I am on my way to deliver order ${orderDetail.customer_location}`);

    setTimeout(() => {
        console.log("Order delivered succesfully");
        orderDetail.delivery = true;     // ✅ final status
    }, 3000)
}
```

This is the **last step**, so it doesn't need a callback — nothing comes after it.

### Putting it together: the callback-hell structure

```js title="Day 18 · index.js"
placedOrder(orderDetail, (orderDetail) => {           // ⬇ Level 1: after payment
    preparingOrder(orderDetail, (orderDetail) => {    // ⬇ Level 2: after preparation
        pickupOrder(orderDetail, (orderDetail) => {   // ⬇ Level 3: after pickup
            deliverOrder(orderDetail);                // ⬇ Level 4: final delivery
        });
    });
});
```

**See the pattern?** Each step is **nested inside** the previous step's callback.

```output title="What you see in the console (verified by running the file)"
620 Payment is in progress                           #> 0 s
Payment is received and order get placed             #> 3 s
Your food preparation started of Pizza,biryani,coke  #> 3 s
Your order is now prepared                           #> 6 s
Delivery boy is on way to pickup order from Delhi    #> 6 s
I have picked up the order                           #> 9 s
I am on my way to deliver order Dwarka               #> 9 s
Order delivered succesfully                          #> 12 s
```

[[fig:callback-gantt|Top: the nested version — each step starts only when the previous step calls its callback. Bottom: calling the functions one after another (next section) — everything starts at 0 s.]]

:::cpp One object, shared by all steps (like a pointer)
Remember from Chapter 0: objects are passed **by reference**. Every step receives the **same** `orderDetail` object — like passing the same pointer `Order*` to four functions in C++. That's why a property added in step 1 (`status`) is visible in step 2, 3 and 4.

The arrow functions' parameter is also named `orderDetail`. Inside each arrow function, this parameter **shadows** (hides) the outer `const orderDetail` — just like an inner-scope variable with the same name in C++. Here it doesn't matter, because they all point to the same object anyway.
:::

## 4.5 Why can't we just call them one after another?

It looks simpler to write:

```js
placedOrder(orderDetail, preparingOrder);
preparingOrder(orderDetail, pickupOrder);
pickupOrder(orderDetail, deliverOrder);
```

**Problem:** these three lines all execute **immediately**, one after another, **without waiting**. JavaScript doesn't know it should wait for `placedOrder` to finish before calling `preparingOrder` — `placedOrder` returned as soon as it handed its timer to the browser!

```output title="Real output of the wrong version"
620 Payment is in progress                           #> 0 s
Your food preparation started of Pizza,biryani,coke  #> 0 s  — before payment!
Delivery boy is on way to pickup order from Delhi    #> 0 s  — before cooking!
Payment is received and order get placed             #> 3 s
Your food preparation started of Pizza,biryani,coke  #> 3 s  — AGAIN
...
Uncaught TypeError: Callback is not a function       #> 6 s  — crash!
```

Everything starts at 0 s, some steps run **twice** (once directly, once as a callback), and then it **crashes**: when `placedOrder` calls `preparingOrder(orderDetail)` as its callback, it passes only **one** argument — so inside `preparingOrder`, `Callback` is `undefined`, and calling `undefined(...)` is a `TypeError`.

## 4.6 Why nesting works

```js
placedOrder(orderDetail, (orderDetail) => {
  // This function doesn't run immediately.
  // It WAITS for placedOrder to finish, THEN it runs with the updated orderDetail.
  preparingOrder(orderDetail, (orderDetail) => {
    // This WAITS for preparingOrder to finish, then runs with the updated orderDetail.
    pickupOrder(orderDetail, (orderDetail) => {
      // And so on...
      deliverOrder(orderDetail);
    });
  });
});
```

**The intuition:**

- Each callback is a **"what to do NEXT"** instruction.
- It is wrapped **inside** the previous step, so it waits.
- It is a chain of *"when you're done, do this"*.

:::analogy Russian nesting dolls 🪆
Open doll 1 → find doll 2 inside. Open doll 2 → find doll 3 inside. Open doll 3 → find doll 4 inside. Each step **reveals** the next step. Nested callbacks work the same way: finishing step 1 is what "opens" step 2.
:::

[[fig:nesting-dolls|Every callback lives inside the previous one — that's why the code keeps moving to the right.]]

## 4.7 The problems with callback hell

### 1. Readability — the Pyramid of Doom

```js
step1((data) => {
  step2(data, (data) => {
    step3(data, (data) => {
      step4(data, (data) => {
        step5(data, (data) => {
          step6(data, (data) => {
            // Code keeps moving right →→→
          });
        });
      });
    });
  });
});
```

- The code doesn't read naturally from top to bottom.
- It is hard to see the flow.
- The indentation grows until it is unmanageable.

### 2. Error handling nightmare

What if the payment fails? What if the kitchen is closed? What if the driver cancels? You must check for errors **at every level**:

```js
placedOrder(orderDetail, (orderDetail, error) => {
  if (error) {
    console.log("Payment failed:", error);
    return;                 // ❌ but what about refund? notification?
  }
  preparingOrder(orderDetail, (orderDetail, error) => {
    if (error) {
      console.log("Kitchen error:", error);
      return;               // ❌ need to cancel order, refund payment
    }
    pickupOrder(orderDetail, (orderDetail, error) => {
      if (error) {
        console.log("Pickup failed:", error);
        return;             // ❌ food is ready but stuck!
      }
      deliverOrder(orderDetail, (error) => {
        if (error) {
          console.log("Delivery failed:", error);   // ❌ customer charged, food gone
        }
      });
    });
  });
});
```

Problems: error handling at **every** level, lots of repeated code, proper error recovery is hard, and one error can leave the system in an inconsistent state.

### 3. Hard to modify

Want to add a *"Send SMS notification"* step between pickup and delivery?

```js
placedOrder(orderDetail, (orderDetail) => {
  preparingOrder(orderDetail, (orderDetail) => {
    pickupOrder(orderDetail, (orderDetail) => {
      // 🆕 NEW STEP — must break and re-nest everything below it
      sendSMS(orderDetail, (orderDetail) => {
        deliverOrder(orderDetail);
      });
    });
  });
});
```

You have to break the chain, re-indent everything, and it's easy to introduce bugs — touching old code is risky.

### 4. You can't use normal control flow (`try`/`catch`, `return`)

**`try`/`catch` doesn't work:**

```js
try {
  placedOrder(orderDetail, (orderDetail) => {
    throw new Error("Payment failed");   // ❌ thrown LATER, after try/catch is done
  });
} catch (error) {
  console.log("Won't catch it!");        // this never runs
}
```

**Why?** Think about the call stack (Chapter 3). The `try` block only calls `placedOrder`, which starts a timer and returns immediately — so the `try`/`catch` is **finished and gone** from the stack. Three seconds later, the callback runs from the event loop with a fresh, empty stack. There is no `try` around it anymore.

**`return` doesn't work as expected:**

```js
function processOrder() {
  placedOrder(orderDetail, (orderDetail) => {
    if (orderDetail.cost > 1000) {
      return "Too expensive";   // ❌ this only exits the callback, not processOrder
    }
    preparingOrder(orderDetail, (orderDetail) => {
      // This still runs even though we "returned"!
    });
  });
  return "Order processed";     // ❌ this returns IMMEDIATELY, before the order even starts
}
```

### 5. Variable scope confusion

```js
let finalStatus;

placedOrder(orderDetail, (orderDetail) => {
  preparingOrder(orderDetail, (orderDetail) => {
    pickupOrder(orderDetail, (orderDetail) => {
      deliverOrder(orderDetail);
      finalStatus = "Delivered";   // set it here...
    });
  });
});

console.log(finalStatus);   // ❌ undefined! The callbacks haven't run yet
```

It is hard to get data **out** of a callback chain — the last line runs at 0 s, long before the callbacks.

### 6. Debugging is painful

When an error happens deep inside the chain, the stack trace looks like this:

```output label="Error"
Error: Delivery failed
    at anonymous (line 45)
    at anonymous (line 38)
    at anonymous (line 31)
    at anonymous (line 24)
```

All functions show as **"anonymous"**, it's hard to trace which step failed, and the stack trace doesn't show the flow.

### 7. Testing is difficult

You can't easily test `preparingOrder` alone — it is buried inside `placedOrder`'s callback. You can't mock just one step, and you can't easily test error scenarios.

### 8. Parallel operations are messy

What if you want to **prepare food AND assign a driver at the same time**, and continue only when **both** are done?

```js
// With callbacks, you need manual coordination:
let foodReady = false;
let driverAssigned = false;

prepareFood(() => {
  foodReady = true;
  if (driverAssigned) startDelivery();
});

assignDriver(() => {
  driverAssigned = true;
  if (foodReady) startDelivery();
});
// ❌ Messy! Easy to get wrong! Duplicate code!
```

(In Chapter 7 we'll see `Promise.all`, which solves this in one line.)

### Summary table

| Aspect | Problem | Impact |
|---|---|---|
| **Readability** | Pyramid shape, deep nesting | Hard to understand the flow |
| **Error handling** | Must repeat at every level | Repetitive, easy to miss |
| **Maintainability** | Hard to add/remove steps | Risky to modify |
| **Control flow** | Can't use `try`/`catch`, `return` | Can't write normal code |
| **Debugging** | Anonymous function traces | Hard to find bugs |
| **Testing** | Steps are tightly coupled | Can't test in isolation |
| **Parallelism** | Manual coordination needed | Complex, error-prone |
| **Scope** | Variables trapped in closures | Data access issues |

## 4.8 Key takeaways

1. **Callback hell exists because:** sequential async operations need to wait for each other, each step needs data from the previous step, and callbacks are the only way to say *"do this next"*.
2. **The nesting happens because:** JavaScript doesn't wait for async operations, so we wrap the next step **inside** the previous step's callback to get the right order.
3. **Why it's called "hell":** unreadable and unmaintainable code, error handling becomes a nightmare, normal JavaScript features (`try`/`catch`, `return`) don't work, and debugging/testing is very hard.
4. **The fundamental insight:** we are trying to express **sequential** logic (A → B → C → D) using **nested** functions (which represent *scope*, not *sequence*). This mismatch creates all the problems.

:::tip What's next?
Modern JavaScript has solutions. With **Promises** (Chapter 5) the same order flow becomes a flat, readable chain with **one** place for errors:

```js
placedOrder(orderDetail)
  .then(preparingOrder)
  .then(pickupOrder)
  .then(deliverOrder)
  .catch(error => console.log("Error:", error));
```
And with **`async`/`await`** (Chapter 7) it looks almost like normal synchronous code.
:::

## 4.9 Things to Remember

:::remember
- A **callback** = a function passed to another function, to be called now or later. The caller can pass data into it: `Callback(orderDetail)`.
- Async steps that depend on each other must **start inside the previous step's callback** — otherwise they all start at 0 s.
- In the Day 18 code, the **same** `orderDetail` object (a reference) travels through all 4 steps; each step adds a property (`status`, `token`, `received`, `delivery`).
- `${array}` inside a template literal joins the items with commas (`Pizza,biryani,coke`).
- Nesting → **Pyramid of Doom**: hard to read, change, debug and test.
- `try`/`catch` around async code **cannot** catch errors thrown later in callbacks; `return` inside a callback only leaves that callback.
- The fix: **Promises** and **async/await**.
:::

:::quiz
1. In one sentence, what is a callback?
2. In the Day 18 code, why is `deliverOrder` the only function without a `Callback` parameter?
3. What is printed, and when?

    ```js
    function task(name, ms, cb) {
      setTimeout(() => { console.log(name); cb(); }, ms);
    }
    task("A", 300, () => task("B", 100, () => console.log("done")));
    console.log("start");
    ```

4. Will `"Caught!"` be printed?

    ```js
    try {
      setTimeout(() => { throw new Error("Oops"); }, 0);
    } catch (e) {
      console.log("Caught!");
    }
    ```

5. How long does the whole Day 18 order take, and why not 3 seconds?
:::

:::answer
1. A function passed as an argument to another function, which calls it back (now or later).
2. Because it is the **last** step — nothing needs to happen after delivery.
3. `start` (0 ms), `A` (≈300 ms), `B` (≈400 ms), `done` (right after B). Task B starts only inside A's callback.
4. **No.** The error is thrown later from the event loop, after the `try`/`catch` has already finished. It becomes an *uncaught* error.
5. About **12 seconds** (4 steps × 3 s), because each step starts only after the previous step's callback is called.
:::
