:::chapter 10 | The this Keyword, call / apply / bind, and Arrow Functions | Lecture 22 · Day 22 code
- The first principle: `this` is decided by **how** a function is **called**
- The global object: `window`, `global`, `globalThis`
- The 4 rules: **method**, **simple**, **explicit** (`call`/`apply`/`bind`), **constructor** (`new`)
- The big exception: **arrow functions** take `this` from outside
- `this` at the top level: browser vs Node.js
- The Stopwatch problem, `that = this`, `.bind(this)` and arrows
- When NOT to use arrow functions
- Every experiment from the **Day 22** code
:::

## 10.1 The idea: "You are wearing a red shirt"

Imagine I write a sentence on a piece of paper: **"You are wearing a red shirt."**

Who is "you"? You can't know by just looking at the paper. The meaning of "you" depends entirely on **who I am speaking to when I say the sentence**:

- If I say it to Alice, "you" is Alice.
- If I say it to Bob, "you" is Bob.
- If I shout it into an empty room, "you" is… nobody? Or the room itself? (This is where it gets interesting.)

The sentence (the **function**) is the same. The **context of the call** (*how I say it*) determines the meaning of "you" (**`this`**).

:::cpp In C++, `this` is simple — in JavaScript it's flexible
In C++, `this` is a **pointer to the object the member function was called on**: `alice.speak()` → `this == &alice`; `bob.speak()` → `this == &bob`. And a member function **can't** be called without an object.

JavaScript's **Rule 1** (below) is exactly the same as C++. The difference: in JavaScript a function is a normal **value**. You can copy it out of an object, pass it as a callback, call it on its own, or force it onto another object. **Each way of calling gives a different `this`.** That's why we need rules.
:::

## 10.2 The first principle: the call-site

This leads us to the single most important principle for understanding `this`:

:::def The first principle
The value of `this` is **not** determined by **where** a function is written. It is determined by **HOW** that function is **called**.
:::

That's it — this is the bedrock. To know what `this` is, you don't look at the function's code; you find the line where the function is being invoked (the **call-site**) and look at **how** it's being called. (Arrow functions are the one big exception — section 10.8.)

## 10.3 The global object: `window`, `global`, `globalThis`

Before the rules, meet the "ultimate boss" object that appears in some of them — the **global object**:

- In the **browser** it is **`window`** (it holds `document`, `setTimeout`, `console`…).
- In **Node.js** it is **`global`**.
- **`globalThis`** is the modern, standard name that points to the global object in **any** environment.

:::day Day 22 — experiment 1: the global object
```js title="Day 22 · index.js — experiment 1"
var a = 10;
var b = 20;

console.log(a, b);

function greet(name1, name2) {
    console.log(name1, name2);
}

greet("Rohit", "Mohit");

document.getElementById("first");
console.log(globalThis);
```

```output label="Console (browser)"
10 20
Rohit Mohit
Window {window: Window, self: Window, document: document, name: '', …}
```

- `globalThis` in the browser **is** `window`.
- `var` at the top level of a normal browser script becomes a **property of `window`**: `window.a` → `10` (`let`/`const` don't do this).
- `document.getElementById(...)` is really `window.document.getElementById(...)` — `document` lives on the global object.
- In Node.js, `console.log(globalThis)` prints the `global` object instead (and there is no `document`).
:::

## 10.4 Rule 1 — the method call (the most intuitive)

When a function is called **on an object, using a dot**.

- **How it's called:** `object.myFunction()`
- **Intuition:** the object is the one "in charge" of the call.
- **`this` is:** the object to the **left of the dot**.

```js
const person = {
  name: "Alice",
  speak: function () {
    // Call-site: person.speak()
    // The object to the left of the dot is 'person'. So, `this` is `person`.
    console.log(`My name is ${this.name}`);
  },
};

person.speak();   // My name is Alice
```

:::mistake Losing `this` by taking the method out
```js
const speak = person.speak;   // copy the function out of the object
speak();                      // ❌ no dot anymore → Rule 2 → this is undefined/window
```
The function is the same, but the **call-site** changed. This is exactly what happens when you pass `person.speak` as a **callback** (e.g. to `setTimeout`) — see the Stopwatch problem in 10.10.
:::

## 10.5 Rule 2 — the simple call (the most confusing)

When a function is called **by itself**, with **no object on the left**.

- **How it's called:** `myFunction()`
- **Intuition:** no one is in charge of the call. It's just… called. This is the **default** case.
- **`this` is:** it depends on the **strictness** of the code (Chapter 9).

**Case 2a — non-strict mode (the "sloppy" old way).** If nobody is in charge, the ultimate boss — the **global object** — takes over. In a browser that's `window`; in Node.js it's `global`.

```js
// Running in a browser, in non-strict mode
function whoAmI() {
  // Call-site: whoAmI() — no object on the left. Non-strict mode.
  // `this` defaults to the global object.
  console.log(this === window);   // true
}
whoAmI();
```

**Case 2b — strict mode (the modern, safe way).** If nobody is in charge, then **nobody** is in charge: **`this` is `undefined`**. This is much safer, because it prevents you from accidentally modifying the global object — your code throws an error immediately if you try, which is a good thing!

```js
'use strict';
function whoAmI() {
  // Call-site: whoAmI() — no object on the left. Strict mode is on.
  // `this` is undefined.
  console.log(this === undefined);   // true
  // console.log(this.name);         // this would throw a clear error!
}
whoAmI();
```

:::day Day 22 — experiment 4: a plain function call
```js title="Day 22 · index.js — experiment 4"
// 'use strict'

function greet() {
    console.log(this);
}

greet();
```

| Where you run it | Output |
|---|---|
| Browser, **without** `'use strict'` | `Window {…}` |
| Browser, **with** `'use strict'` | `undefined` |
| Node.js, without `'use strict'` | `<ref *1> Object [global] {…}` (the global object) |
| Node.js, with `'use strict'` | `undefined` |
:::

## 10.6 Rule 3 — the explicit call: `call`, `apply`, `bind` (the "bossy" way)

When you want to **force** a specific value for `this`, no matter how the function is called.

- **How it's called:** `myFunction.call(...)`, `myFunction.apply(...)` or `myFunction.bind(...)`
- **Intuition:** you are explicitly telling the function: *"Run now, and when you do, `this` **must** be this specific object I'm giving you."*
- **`this` is:** the **first argument** you pass.

```js
function speak() {
  console.log(`My name is ${this.name}`);
}

const person1 = { name: "Alice" };
const person2 = { name: "Bob" };

speak.call(person1);   // We force `this` to be person1 → My name is Alice
speak.call(person2);   // Now we force `this` to be person2 → My name is Bob
```

**Why is this useful?** Remember the Day 22 comment: *"100 users → greet function → 100 × memory, code copy-paste"*. With `call`, you write **one** function and **borrow** it for any object — no copies.

### `call` vs `apply` vs `bind`

<div class="tbl-nowrap" markdown="1">

| | Syntax | Runs the function? | Other arguments |
|---|---|---|---|
| **call** | `fn.call(obj, a, b)` | **yes**, right now | one by one, with **commas** |
| **apply** | `fn.apply(obj, [a, b])` | **yes**, right now | all together, in an **array** |
| **bind** | `fn.bind(obj, a, b)` | **no** — it **returns a new function** whose `this` is permanently `obj` | pre-filled, one by one |

</div>

:::tip A trick to remember
**C**all = **C**ommas. **A**pply = **A**rray. **B**ind = **B**ook it for later (you get a new function back).
:::

:::day Day 22 — experiment 3: `call`, `apply` and `bind`
```js title="Day 22 · index.js — experiment 3"
function greet() {
    console.log(`hi ${this.name}`);
}

function incrementAge(value, name) {
    this.age += value;
    this.name = name;
    console.log(this.age);
    console.log(this.name)
}

const user = {
    name: "Rohit",
    age: 30,
}

const user2 = {
    name: "Mohit",
    age: 10
}

greet.call(user);                                   // hi Rohit
greet.call(user2);                                  // hi Mohit

incrementAge.call(user2, 10, "Mohan");              // 20, Mohan
// incrementAge.apply(user2, [10, "Mohan"]);        // same, arguments in an array
// const incr = incrementAge.bind(user2, 10, "Mohan");
// incr();                                          // same, but called later
```

- `greet.call(user)` → inside `greet`, `this` is `user` → prints `hi Rohit`. Then `this` is `user2` → `hi Mohit`. **One** function, used by **two** objects.
- `incrementAge.call(user2, 10, "Mohan")` → `this` is `user2`; `value` is `10`, `name` is `"Mohan"`. So `user2.age` becomes `10 + 10 = 20` and `user2.name` becomes `"Mohan"` → prints `20` and `Mohan`.
- `apply` does the same, but the arguments go in an **array**: `[10, "Mohan"]`.
- `bind` **doesn't run anything** — it returns a new function `incr` with `this` locked to `user2` and the arguments pre-filled. Calling `incr()` later prints `20` and `Mohan`.

(In the file the teacher runs only one of them at a time. If you ran `call`, then `apply`, then `bind`+`incr()` one after another on the same `user2`, you'd see the age grow: 20, 30, 40.)
:::

## 10.7 Rule 4 — the constructor call with `new` (the "factory" way)

When you call a function using the **`new`** keyword.

- **How it's called:** `new MyFunction()` (or `new MyClass()`)
- **Intuition:** `new` is a special instruction to **build a brand-new object**.
- **`this` is:** the brand-new, empty object that was just created. The constructor's job is to populate it (Chapter 8).

```js
class Person {
  constructor(name) {
    // Call-site: new Person(...)
    // `new` creates an empty object and makes `this` point to it.
    this.name = name;   // populating the new object
  }
}

const person1 = new Person("Alice");
// `this` inside the constructor was the object that became person1
console.log(person1);   // { name: 'Alice' }  (the console shows: Person {name: 'Alice'})
```

:::day Day 22 — experiment 5: `this` in a class constructor
```js title="Day 22 · index.js — experiment 5"
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
}

// this = { name: "Rohit", age: 20 }   ← the teacher's comment: the new object

const p1 = new Person("Rohit", 20);

console.log(p1);
```

```output label="Console (browser)"
Person {name: 'Rohit', age: 20}
```
:::

[[fig:this-rules|The four ways to call a regular function — and the arrow-function exception.]]

## 10.8 The big exception — arrow functions

Arrow functions (`=>`) are special. They were designed to solve common frustrations with `this`, and they **break the first principle on purpose**:

:::def Arrow functions and `this`
Arrow functions **do not have their own `this`**. They **inherit `this` from their parent scope**, just like any other variable. They don't care **how** they are called — they only care **where they are written**. This is called **lexical `this`**.
:::

:::analogy The loyal assistant
An arrow function is like a **loyal assistant**. If you ask the assistant *"Who is your boss?"*, they don't say *"Me!"*. They point to **their** boss — the `this` of the function they were written inside.
:::

```js
const user = {
  name: "Alice",
  hobbies: ['reading', 'coding'],
  printHobbies: function () {
    // For this regular function, `this` is `user` (Rule 1).
    this.hobbies.forEach(hobby => {
      // This is an arrow function. It doesn't have its own `this`.
      // It inherits `this` from its parent, printHobbies. So `this` here is also `user`.
      console.log(`${this.name} likes ${hobby}`);
    });
  },
};

user.printHobbies();
```

```output
Alice likes reading
Alice likes coding
```

Because arrow functions ignore the call-site, `call`, `apply` and `bind` **cannot change** an arrow function's `this` either.

## 10.9 `this` outside of any function (the global context)

What is `this` when it's not inside any function at all?

**Intuition:** if you're not in any specific room (a function), you must be in the main building (the **global scope**). So `this` refers to the "main building" object.

- **In a browser** (a regular, non-module `<script>` tag): the main building is the **`window`** object. `console.log(this === window)` → `true`. This is true **even with `'use strict'`** — strict mode only changes `this` inside plain function calls.
- **In Node.js** — the tricky one. **Every file in Node.js is its own module.** Node wraps your file's code in a function, and because of how Node calls that function, `this` at the top level is **`module.exports`**, which is an **empty object `{}`** by default — **not** the `global` object. (This is for normal `.js` files. In ES-module files — `.mjs`, or `"type": "module"` — top-level `this` is `undefined`.)

```js
// In a Node.js file
console.log(this === global);          // false
console.log(this);                     // {}
console.log(this === module.exports);  // true
```

:::day Day 22 — experiments 2, 6 and 10: `this` at the top level, and a top-level arrow
```js title="Day 22 · index.js — experiments 2 / 6 / 10"
// 'use strict'

console.log(this);

const greet = () => {
    console.log(this);
}

greet();
```

| | Browser | Node.js |
|---|---|---|
| `console.log(this)` at the top | `Window {…}` | `{}` |
| … with `'use strict'` | still `Window {…}` | still `{}` |
| `greet()` (arrow, written at the top level) | `Window {…}` — it copies the top-level `this` | `{}` |

The teacher's summary comment says exactly this: *"this keyword in global scope: NodeJS (Empty Object), in browser it will point to global Object"* and *"arrow function take this keyword from its lexical environment scope"*.
:::

## 10.10 Arrow functions in detail: the problem they were born to solve

### Part 1 — the classic problem

Before arrow functions, a very common and frustrating bug appeared in JavaScript. To understand the genius of arrow functions, you must first **feel the pain** of the problem they solve. Let's build a simple `Stopwatch` object:

```js
// The Old, Painful Way
function Stopwatch() {
  this.seconds = 0;
  this.start = function () {
    // We want to increment `this.seconds` every second.
    setInterval(function () {
      // Uh oh. We have a problem here.
      // What is `this` inside THIS function?
      console.log(this.seconds);
      this.seconds++;
    }, 1000);
  };
}

const myWatch = new Stopwatch();
myWatch.start();
```

When you run `myWatch.start()`, you don't get 0, 1, 2… Instead the first tick prints `undefined`, and after that **`NaN`** (Not a Number) every second.

**Why did this fail?** Apply the first principle — *the value of `this` is determined by how the function is called*:

1. When we call `myWatch.start()`, the `this` inside `start` is correctly `myWatch` (Rule 1: method call).
2. But the function we pass to `setInterval` is a **regular function**, and `setInterval` calls it later **without** `myWatch.` in front of it — so it is **not** a method call on `myWatch`.
3. So `this` inside the callback is **not** `myWatch`. The browser calls timer callbacks with `this` set to the global object **`window`** — and it does this even in strict mode, because the timer passes `window` on purpose. (In Node.js, `this` there is a `Timeout` object.)
4. So inside our callback we have **lost the context of `myWatch`**. We are doing `window.seconds++` → `undefined + 1` → `NaN`.

[[fig:arrow-scope|A regular function creates its own `this` (a one-way mirror). An arrow function is transparent glass: it sees the `this` of the room it was written in.]]

### The old, clumsy workarounds

**Workaround 1: `that = this` (the closure trick).** Save the correct `this` in a normal variable **before** you lose it:

```js
function Stopwatch() {
  this.seconds = 0;
  const that = this;   // capture the correct `this`
  this.start = function () {
    setInterval(function () {
      // Use the captured variable instead of the wrong `this`
      console.log(that.seconds);
      that.seconds++;
    }, 1000);
  };
}
```

**Workaround 2: `.bind(this)` (the explicit way).** Create a new function whose `this` is permanently locked to the correct value:

```js
function Stopwatch() {
  this.seconds = 0;
  this.start = function () {
    setInterval(function () {
      console.log(this.seconds);
      this.seconds++;
    }.bind(this), 1000);   // bind the callback to the correct `this`
  };
}
```

Both of these work, but they are verbose and add extra noise to the code. We are fighting against the language's own rules.

### Part 2 — the solution: the arrow function

The designers of ES6 saw this common problem and created a new kind of function with one special, game-changing rule: **an arrow function does not have its own `this`; it lexically inherits `this` from its parent scope.**

- **"Does not have its own `this`":** it completely ignores the four rules of `this` (method call, simple call, etc.). They do not apply to it.
- **"Lexically inherits":** this is the key. It doesn't care how it's **called**. It only cares where it is physically **written** in the code. It looks outside itself to the surrounding code block and uses whatever `this` is in there.

:::analogy One-way mirror vs. transparent glass
Think of a **regular function** as a **one-way mirror**. You can't see the `this` of the room outside — it creates its own reflection, its own `this`.

An **arrow function** is like a sheet of **perfectly transparent glass**. It doesn't have its own reflection. It just lets you see the `this` of the room it's in.
:::

```js
function Stopwatch() {
  this.seconds = 0;
  this.start = function () {
    // The `this` in this scope correctly points to the stopwatch instance.
    setInterval(() => {
      // This is an arrow function. It has no `this` of its own.
      // It inherits `this` from its parent, the `start` function.
      // Therefore `this` here is the stopwatch instance. It just works.
      console.log(this.seconds);
      this.seconds++;
    }, 1000);
  };
}

const myWatch = new Stopwatch();
myWatch.start();   // 0, 1, 2, 3 … — this works perfectly!
```

The code is clean, intuitive, and does exactly what we want without any workarounds. The context is preserved automatically.

:::day Day 22 — experiments 7, 8 and 9: `that = this` and the arrow stopwatch
```js title="Day 22 · index.js — experiment 7: an inner function loses this"
const user = {
    name: "Rohit",
    greet: function () {
        // console.log(this);            // here `this` is user (method call)
        const that = this;               // save it!
        function meet() {
            console.log(that);           // inner function: use `that`, not `this`
        }
        meet();                          // plain call: inside meet, `this` is NOT user
    }
}

user.greet();                            // {name: 'Rohit', greet: ƒ}
```

```js title="Day 22 · index.js — experiment 8: stopwatch with that = this"
const stopWatch = {
    second: 0,
    start: function () {
        const that = this;
        setInterval(function () {
            that.second++;
            console.log(that.second);
        }, 1000);
    }
}
```

```js title="Day 22 · index.js — experiment 9: stopwatch with an arrow function"
const stopWatch = {
    second: 0,
    start: function () {
        console.log(this);               // {second: 0, start: ƒ}
        setInterval(() => {
            this.second++;               // arrow → `this` from start() → stopWatch
            console.log(this.second);
        }, 1000)
    }
};

stopWatch.start();
```

```output label="Output of experiment 9 (experiment 8 prints the same numbers, without the first line)"
{second: 0, start: ƒ}
1   #> after 1 s
2   #> after 2 s
3   #> after 3 s … and so on, forever
```

If you wrote experiment 8 with `this` instead of `that` inside the regular callback, `this` would be `window` → `this.second++` makes `NaN`, and you would see `NaN` every second.
:::

### Part 3 — the consequences: when NOT to use arrow functions

Because arrow functions **always** inherit `this`, they are the **wrong tool** when you **want** your function to have its own `this` based on how it's called.

**1. Object methods (the most common mistake).** If you define a method on an object using an arrow function, it inherits `this` from the **outside** (the global scope), which is not what you want:

```js
const person = {
  name: "Alice",

  // WRONG WAY — using an arrow function for a method
  sayHi: () => {
    // This `this` is inherited from the global scope (where the object is written).
    // In Node it's module.exports ({}). In a browser it's `window`.
    console.log(`Hi, my name is ${this.name}`);
  },

  // CORRECT WAY — using a regular function
  speak: function () {
    // This `this` is decided by the call-site (person.speak()), so `this` is person.
    console.log(`Hi, my name is ${this.name}`);
  },
};

person.sayHi();   // Hi, my name is undefined   (Node.js)
person.speak();   // Hi, my name is Alice
```

:::note Why might the browser show an empty name?
In a browser, `person.sayHi()` prints **`Hi, my name is `** with an **empty** name, not `undefined`. That's because `window` happens to have a built-in property called `name` whose value is `""`. Either way, it is **not** `"Alice"` — the arrow method did not get `person` as `this`.
:::

**2. Event listeners in HTML.** When you add an event listener, you often want `this` to refer to the **element that was clicked**. A regular function does this automatically (the browser calls it with `this` = the element). An arrow function does not.

```js
const button = document.getElementById('myButton');

// CORRECT WAY — regular function: `this` is the button element itself
button.addEventListener('click', function () {
  console.log(this);            // <button id="myButton">…</button>
  this.textContent = 'Clicked!';
});

// WRONG WAY — arrow function: `this` comes from the outside (window)
button.addEventListener('click', () => {
  console.log(this);            // Window {…}
  // this.textContent = 'Clicked!';   // would NOT change the button
});
```

:::day Day 22 — experiments 11 and 12: arrow method and arrow listener
```js title="Day 22 · index.js — experiment 11"
// 'use strict'
console.log(this);

const user = {
    name: "Rohit",
    greet: () => {
        console.log(this);
    }
}

user.greet();
```

Browser: both lines print `Window {…}` (Node.js: both print `{}`). The dot in `user.greet()` doesn't matter — **arrow functions ignore the call-site**.

```js title="Day 22 · index.js — experiment 12"
const button = document.getElementById("first");

button.addEventListener('click', () => {
    console.log(this);
})
```

Clicking the red square button prints **`Window {…}`**, not the button — because the arrow function took `this` from the top level of the script. Change it to `function () { console.log(this); }` and it prints the **button element**.
:::

## 10.11 The final intuitive summary — how to find `this`

Ask these questions **in this order** (the order matters when several apply):

1. **Is it an arrow function?** → `this` is whatever `this` was in the **parent scope** (where it was written). **Stop here.**
2. **Is the `new` keyword used?** (`new Person()`) → `this` is the **brand-new object** being created.
3. **Is `.call()`, `.apply()` or `.bind()` used?** (`speak.call(person)`) → `this` is the **object passed as the first argument**.
4. **Is the function called with a dot?** (`person.speak()`) → `this` is the **object to the left of the dot**.
5. **None of the above** — a simple call like `speak()`:
    - in `'use strict'` mode → `this` is **`undefined`**;
    - in sloppy mode → `this` is the **global object** (`window` in the browser, `global` in Node.js).

And **outside any function**: browser → `window`; Node.js → `{}` (`module.exports`).

[[fig:this-flowchart|Follow the questions from top to bottom. The first "yes" gives you the answer.]]

## 10.12 All Day 22 experiments at a glance

<div class="tbl-nowrap" markdown="1">

| Experiment | Code | Browser | Node.js |
|---|---|---|---|
| Global object | `globalThis` | `Window {…}` | `Object [global] {…}` |
| `var` at the top | `var a = 10` | `window.a` is `10` | not on `global` |
| Top-level `this` | `console.log(this)` | `Window {…}` (strict too) | `{}` |
| Plain call, sloppy | `greet()` | `Window {…}` | the global object |
| Plain call, strict | `greet()` | `undefined` | `undefined` |
| Explicit | `greet.call(user)` | `hi Rohit` | `hi Rohit` |
| call / apply / bind | `incrementAge.call(…)` | `20`, `Mohan` | `20`, `Mohan` |
| Constructor | `new Person(…)` | `Person {name: 'Rohit', age: 20}` | same object |
| Arrow at the top | `greet()` (arrow) | `Window {…}` | `{}` |
| Inner fn + `that` | `user.greet()` | the `user` object | the `user` object |
| Stopwatch, `that` | `stopWatch.start()` | `1, 2, 3…` | `1, 2, 3…` |
| Stopwatch, arrow | `stopWatch.start()` | `1, 2, 3…` | `1, 2, 3…` |
| Arrow as a method | `user.greet()` | `Window {…}` | `{}` |
| Arrow listener | click the button | `Window {…}` | (no buttons) |

</div>

## 10.13 Things to Remember

:::remember
- For **regular functions**, `this` is decided by **how the function is called** (the call-site), not where it is written.
- **Method call** `obj.fn()` → `obj`. **Simple call** `fn()` → `undefined` (strict) / global object (sloppy). **Explicit** `fn.call(x)` / `fn.apply(x)` / `fn.bind(x)` → `x`. **Constructor** `new Fn()` → the new object.
- `call(obj, a, b)` runs now with commas; `apply(obj, [a, b])` runs now with an array; `bind(obj, a, b)` returns a **new function** for later.
- **Arrow functions have no own `this`** — they use the `this` of the place where they are **written**. `call`/`apply`/`bind`/dot can't change it.
- Use **arrows for callbacks inside methods** (`setInterval`, `forEach`) to keep `this`. **Don't** use arrows for **object methods** or when you need `this` to be the **clicked element**.
- Top-level `this`: browser → `window`; Node.js → `{}` (`module.exports`). `globalThis` always means the global object.
- Old fixes for lost `this`: `const that = this;` or `.bind(this)`. Modern fix: an arrow function.
:::

:::quiz
1. What is printed (in a browser, sloppy mode)?

    ```js
    const obj = { name: "X", show() { console.log(this.name); } };
    const f = obj.show;
    obj.show();
    f();
    ```

2. What does `fn.bind(obj)` return?
3. What is printed?

    ```js
    function add(a, b) { return this.base + a + b; }
    const o = { base: 100 };
    console.log(add.call(o, 1, 2), add.apply(o, [3, 4]));
    ```

4. Inside `setInterval(function () { … }, 1000)` written in a method, what is `this` (browser, sloppy mode)? How do you fix it?
5. What is `this` at the top level of a Node.js file?
6. Why is `sayHi: () => console.log(this.name)` a bad way to write an object method?
:::

:::answer
1. `X`, then an empty line — `f()` is a plain call, so `this` is `window`, and `window.name` is `""`. (In strict mode `f()` would throw a `TypeError`, because `this` is `undefined`.)
2. A **new function** whose `this` is permanently `obj` (it doesn't run anything by itself).
3. `103 107`
4. The global object `window` — the timer calls your callback without your object, and browsers pass `window` as `this`. Fix: use an arrow function `setInterval(() => { … })`, or `const that = this`, or `.bind(this)`.
5. `{}` — `module.exports`, not `global`.
6. Arrow functions don't get `this` from the call-site, so `this` is the outer (global) `this`, not the object.
:::
