:::chapter 11 | Final Revision: Everything on a Few Pages | All lectures · All Day code
- How all the topics connect (one big picture)
- A cheat sheet for every chapter
- Browser vs Node.js differences in one table
- 30 rapid-fire questions with short answers
- 8 mixed "predict the output" puzzles
:::

Use this chapter the night before an exam or an interview. If any line here feels unclear, go back to the chapter mentioned in brackets.

## 11.1 The big picture

[[fig:big-picture|The two big stories of these notes. Top: how JavaScript handles waiting. Bottom: how objects share behaviour and how `this` finds the right object.]]

## 11.2 Cheat sheets

### Arrays, Set and Map (Chapters 1–2)

| You want to… | Use | Returns |
|---|---|---|
| do something with each item | `arr.forEach(fn)` | `undefined` |
| transform every item | `arr.map(fn)` | new array, same length |
| keep only some items | `arr.filter(fn)` | new array, same or shorter |
| combine into one value | `arr.reduce(fn, initial)` | anything |
| get the first match | `arr.find(fn)` | the element or `undefined` |
| check "at least one" / "all" | `arr.some(fn)` / `arr.every(fn)` | `true` / `false` |
| remove duplicates | `[...new Set(arr)]` | new array |
| fast "have I seen it?" | `set.has(x)` | `true` / `false` |
| keys of any type | `new Map()` + `set` / `get` / `has` | — |

### The event loop (Chapter 3)

:::remember The order of execution
1. All **synchronous** code (the call stack runs your file top to bottom).
2. **All microtasks**: `.then` / `.catch` / `.finally` callbacks, code after `await`.
3. **One macrotask**: a `setTimeout` / `setInterval` callback, a click handler…
4. Back to step 2. Forever.
:::

### Async patterns (Chapters 4, 5, 7)

| | Callback | Promise | `async` / `await` |
|---|---|---|---|
| Success | call `cb(data)` | `resolve(data)`, read it in `.then` | `const data = await p;` |
| Failure | extra error parameter | `reject(err)`, read it in `.catch` | `try` / `catch` |
| Cleanup | manual | `.finally(…)` | `finally { … }` |
| Many at once | messy flags | `Promise.all([…])` | `await Promise.all([…])` |

### JSON (Chapter 6)

`JSON.stringify(obj)` → text · `JSON.parse(text)` → object · keys and strings in **double quotes** · no functions, no `undefined`, no comments, no trailing commas · `await response.json()` parses a `fetch` body.

### Prototypes and classes (Chapter 8)

- Lookup: **own property → `[[Prototype]]` → … → `Object.prototype` → `null`**.
- `new F()` = create `{}` → link to `F.prototype` → run `F` with `this` = new object → return it.
- `class` = sugar over constructor functions; methods live on `Class.prototype`; `extends` + `super(...)` (before `this`!).

### `this` (Chapters 9–10)

| How the function is called | `this` is |
|---|---|
| arrow function | the `this` of the surrounding code (where it is written) |
| `new Fn()` | the new object |
| `fn.call(x)` / `fn.apply(x)` / `fn.bind(x)` | `x` |
| `obj.fn()` | `obj` |
| plain `fn()` | `undefined` in strict mode, the global object in sloppy mode |
| event listener with a regular function | the element (`button`) |

## 11.3 Browser vs Node.js — the differences you met in these notes

| Thing | Browser | Node.js |
|---|---|---|
| Global object | `window` | `global` |
| `globalThis` | `window` | `global` |
| Top-level `this` | `window` | `{}` (`module.exports`) |
| Top-level `var x` | becomes `window.x` | stays local to the file |
| `setTimeout(...)` returns | a number (timer ID) | a `Timeout` object |
| `console.log(promise)` | `Promise {<pending>}` | `Promise { <pending> }` |
| `document`, buttons, `localStorage` | ✅ | ❌ |
| Files (`fs.readFile`) | ❌ | ✅ |
| Arrow method `this.name` | `""` (because `window.name` exists) | `undefined` |

## 11.4 Rapid-fire questions

1. **What does single-threaded mean?** One call stack; only one piece of your code runs at a time. (Ch 3)
2. **Who counts the time for `setTimeout`?** The browser (a Web API) — not the JavaScript thread. (Ch 3)
3. **Microtask vs macrotask?** Microtasks = Promise callbacks and code after `await` — **all** of them run first. Macrotasks = `setTimeout`, `setInterval`, events — **one** at a time, after the microtasks. (Ch 3)
4. **Why does `Promise.resolve().then(f)` run before `setTimeout(g, 0)`?** Microtasks run before macrotasks. (Ch 3)
5. **Is the `setTimeout` delay exact?** No — it is a *minimum*; the callback also waits for an empty stack. (Ch 3)
6. **What is a callback?** A function passed to another function to be called now or later. (Ch 0, 4)
7. **What is callback hell?** Deeply nested callbacks for sequential async steps: hard to read, change, debug; errors must be handled at every level. (Ch 4)
8. **What are the states of a Promise?** Pending → fulfilled or rejected (settled, final). (Ch 5)
9. **When does the executor of `new Promise` run?** Immediately, synchronously. (Ch 5)
10. **What does `.then()` return?** A **new** promise — that's why chaining works. (Ch 5)
11. **Where does an error in a promise chain go?** It skips the `.then`s and goes to the nearest `.catch`. (Ch 5)
12. **What does `.finally()` receive?** Nothing. It runs in both cases and passes the value through. (Ch 5)
13. **Does `fetch` reject on 404?** No — check `response.ok`. It rejects only on network failure. (Ch 5, 7)
14. **Why is `response.json()` a Promise?** Reading and parsing the body takes time. (Ch 5, 6)
15. **What does an `async` function return?** Always a Promise. (Ch 7)
16. **What does `await` do?** Pauses **this function** until the promise settles; gives the value or throws the error. (Ch 7)
17. **Where can you use `await`?** Inside `async` functions (or at the top level of modules). (Ch 7)
18. **How do you run independent requests in parallel?** `await Promise.all([p1, p2])`. (Ch 7)
19. **JSON vs a JS object?** JSON is text with strict rules; an object is data in memory. (Ch 6)
20. **What does `JSON.stringify` drop?** Functions and `undefined` properties. (Ch 6)
21. **What is `[[Prototype]]`?** The hidden link from an object to its parent object, used for property lookup. (Ch 8)
22. **`obj.__proto__` vs `Fn.prototype`?** The first is the link on every object; the second is an object on a function that becomes the `[[Prototype]]` of instances created with `new`. (Ch 8)
23. **Is `class` a new object model?** No — syntactic sugar over prototypes. `typeof MyClass === "function"`. (Ch 8)
24. **Why must `super()` come before `this` in a child constructor?** The parent part of the object must be built first (like C++ base-class construction). (Ch 8)
25. **What does `'use strict'` change?** Undeclared assignment → error; `this` in plain calls → `undefined`; duplicate params, `delete x`, `010` → errors. (Ch 9)
26. **How is `this` decided for a regular function?** By **how it is called** (the call-site). (Ch 10)
27. **And for an arrow function?** From the surrounding code where it is written (lexical `this`). (Ch 10)
28. **`call` vs `apply` vs `bind`?** `call` = run now, args with commas; `apply` = run now, args in an array; `bind` = return a new function for later. (Ch 10)
29. **`map` vs `forEach`?** `map` returns a new array; `forEach` returns `undefined`. (Ch 1)
30. **`Set` vs `Array`, `Map` vs `Object`?** Set = unique values, fast `has`; Map = any type of key, `.size`, keeps order. (Ch 2)

## 11.5 Mixed practice — predict the output

Try each one on paper first. Answers are in the box at the end.

**Puzzle 1 — event loop + async**

```js
console.log("A");
setTimeout(() => console.log("B"), 0);
(async () => {
  console.log("C");
  await null;
  console.log("D");
})();
Promise.resolve().then(() => console.log("E"));
console.log("F");
```

**Puzzle 2 — `this` and chaining**

```js
const counter = {
  count: 0,
  inc() {
    this.count++;
    return this;      // return the object itself
  },
};
counter.inc().inc().inc();
console.log(counter.count);
```

**Puzzle 3 — array methods**

```js
const nums = [1, 2, 3, 4, 5];
const result = nums
  .filter(n => n % 2)          // hint: 0 is falsy
  .map(n => n * n)
  .reduce((a, b) => a + b, 0);
console.log(result);
```

**Puzzle 4 — classes and overriding**

```js
class Animal {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} makes a sound`; }
}
class Dog extends Animal {
  speak() { return `${this.name} barks`; }
}
const d = new Dog("Tommy");
console.log(d.speak());
console.log(Object.getPrototypeOf(Dog.prototype) === Animal.prototype);
```

**Puzzle 5 — regular vs arrow method (in Node.js)**

```js
const obj = {
  name: "JS",
  regular() { return this.name; },
  arrow: () => this.name,
};
console.log(obj.regular());
console.log(obj.arrow());
```

**Puzzle 6 — promise chain with recovery**

```js
Promise.reject("oops")
  .then(() => console.log("then 1"))
  .catch(e => { console.log("caught", e); return "recovered"; })
  .then(v => console.log("then 2", v))
  .finally(() => console.log("finally"));
```

**Puzzle 7 — Map and Set**

```js
const m = new Map();
m.set("a", 1).set("b", 2).set("a", 3);
console.log(m.size, m.get("a"), [...new Set([3, 1, 3, 2, 1])]);
```

**Puzzle 8 — JSON**

```js
console.log(JSON.stringify({ a: [1, 2], b: null, c: undefined, d: "x" }));
```

:::answer Answers (all verified by running the code) !break
1. `A`, `C`, `F`, `D`, `E`, `B` — sync first (the async function runs until `await`), then microtasks in the order they were queued (`D`, then `E`), then the timer.
2. `3` — each `inc()` returns the object, so the next `.inc()` is again a method call on `counter`.
3. `35` — odd numbers `[1, 3, 5]` → squares `[1, 9, 25]` → sum 35.
4. `Tommy barks` and `true` — `speak` is found first on `Dog.prototype` (it **overrides** the parent's, like a C++ virtual function); `Dog.prototype` is linked to `Animal.prototype`. `Dog` has no constructor, so JavaScript adds a default one that calls `super(...)` for you.
5. `JS`, then `undefined` — the arrow function takes `this` from the file's top level (`{}` in Node.js). In a browser the second line would be an empty string.
6. `caught oops`, `then 2 recovered`, `finally` — the first `.then` is skipped; `.catch` returns a value, so the chain continues.
7. `2 3 [ 3, 1, 2 ]` — setting `"a"` again **updates** it; the Set keeps the first occurrence of each value in order.
8. `{"a":[1,2],"b":null,"d":"x"}` — `null` is kept, the `undefined` property is dropped.
:::

## 11.6 A last word from your teacher

You now understand the parts of JavaScript that confuse most beginners: **how asynchronous code really runs**, **how objects share methods**, and **how `this` is decided**. The best way to make it permanent is to **type the examples yourself** — change a line, predict the output, run it, and see if you were right. Every wrong prediction teaches you something.

All the best for the next part of the course (React!) — everything you learned here (`map`, `filter`, promises, `async`/`await`, classes, arrow functions and `this`) is used there every day. 🚀
