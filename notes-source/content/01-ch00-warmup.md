:::chapter 0 | JavaScript Warm-up for a C++ Brain | Basics used in every chapter
- Where JavaScript runs (browser vs Node.js)
- `let`, `const`, `var` — and how `const` is like a C++ constant pointer
- Types, `undefined`, `null`, `===`
- Objects and arrays (vs C++ `struct` and `std::vector`)
- Functions as values, arrow functions vs C++ lambdas
- Callbacks, destructuring, spread, `try`/`catch`
:::

You already know C++, so JavaScript will look familiar: `if`, `for`, `while`, `{ }`, `;`, functions — all the same. The differences are in **how values and functions behave**. This short chapter teaches only the basics that the later chapters use again and again. If something in a later chapter looks strange, come back here.

## 0.1 Where does JavaScript run?

In C++ you **compile** your code into a program (`a.out` / `.exe`) and then run it. In JavaScript you don't compile anything yourself — a **JavaScript engine** reads your code and runs it directly. The most famous engine is **V8** (used by Chrome and by Node.js).

JavaScript has two common "homes":

| | Browser (Chrome, Firefox…) | Node.js |
|---|---|---|
| Used for | Web pages: buttons, forms, animations | Servers, command-line tools |
| Special global object | `window` | `global` |
| Can touch the web page (DOM)? | Yes — `document.getElementById(...)` | No page, no `document` |
| Extra powers ("APIs") | timers, `fetch`, DOM events, `localStorage` | timers, `fetch`, files (`fs`), network |
| How to run | `<script src="index.js">` in an HTML file, or the console (F12) | `node index.js` |

Most of the code in these notes works in both. When something behaves differently in the browser and in Node.js, I will tell you clearly.

## 0.2 Variables: `let`, `const` and `var`

```js
let age = 20;          // can be changed later
age = 21;              // ✅ fine

const name = "Rohit";  // cannot be re-assigned
// name = "Mohit";     // ❌ TypeError: Assignment to constant variable.

var old = 5;           // old style (before 2015). Avoid it in new code.
```

- Use **`const` by default**. Use **`let`** only when the value must change (like a loop counter).
- `var` is the old way. It ignores `{ }` blocks (it is *function-scoped*) and at the top level of a browser script it even becomes a property of `window`. We will see this in Chapter 10.

:::cpp `const` in JavaScript = a constant *pointer*, not a constant *object*
A JavaScript `const` means *"this name will always point to the same thing"*. It does **not** freeze the object itself. That is exactly like a C++ **constant pointer**:

```cpp
User* const p = new User{"Rohit"};
p->name = "Mohit";   // ✅ allowed: we change the object, not the pointer
// p = new User{};   // ❌ error: the pointer itself is const
```

```js
const user = { name: "Rohit" };
user.name = "Mohit";   // ✅ allowed (changing inside the object)
// user = {};          // ❌ TypeError: Assignment to constant variable.
```
:::

## 0.3 Types: no `int`, no `string` keyword

In C++ you write the type (`int x = 5;`). In JavaScript you never write the type. A variable can hold **any** type, and can even change type later:

```js
let x = 10;             // a number
x = "ten";              // now a string — JavaScript allows this!
console.log(typeof x);  // "string"
```

The main types you will meet:

| JavaScript type | Example | C++ cousin |
|---|---|---|
| `number` | `42`, `3.14`, `-7` | `double` — **all** numbers are 64-bit floating point |
| `string` | `"hi"`, `'hi'`, `` `hi` `` | `std::string` |
| `boolean` | `true`, `false` | `bool` |
| `undefined` | a variable with no value yet | (an uninitialised variable — but safe to read) |
| `null` | "intentionally empty" | `nullptr` |
| `object` | `{ name: "Rohit" }`, `[1, 2, 3]`, functions | `struct` / class objects |

- **`undefined`** means *"no value has been given"*. Reading a missing property does **not** crash — it just gives `undefined`:

```js
const user = { name: "Rohit" };
console.log(user.age);   // undefined   (in C++ this would not even compile)
```

- **`null`** means *"I am saying on purpose that there is nothing here"*.

## 0.4 Printing and strings

`console.log()` is JavaScript's `std::cout`. It can print many values separated by commas — they are printed with a space between them.

```js
const name = "Rohit";
const age = 30;
console.log("Name:", name, "Age:", age);        // Name: Rohit Age: 30
console.log(`Hello ${name}, you are ${age}`);    // Hello Rohit, you are 30
```

The second line uses a **template literal**: a string written with backticks `` ` `` in which `${ ... }` puts a value inside the string. You will see this in almost every example (C++20 has something similar: `std::format("Hello {}", name)`).

:::tip Arrays inside a template literal
If you put an array inside `${ }`, JavaScript joins its items with commas: `` `${["Pizza", "coke"]}` `` becomes `"Pizza,coke"`. Remember this — it appears in the Day 18 code.
:::

## 0.5 `===` instead of `==`

Always compare with **`===`** (and `!==`). It checks **type and value**. The double `==` first *converts* types, which gives strange results:

```js
console.log(5 === 5);     // true
console.log(5 === "5");   // false  (number vs string)
console.log(5 == "5");    // true   (!) "5" was converted to a number
```

## 0.6 Objects — like a `struct`, but flexible

```js
const user = { name: "Rohit", age: 30 };

console.log(user.name);     // "Rohit"      (dot notation)
console.log(user["age"]);   // 30           (bracket notation)

user.city = "Delhi";        // add a new property at any time!
delete user.age;            // remove a property
console.log(user);          // { name: 'Rohit', city: 'Delhi' }
```

A C++ `struct` has a fixed list of members decided at compile time. A JavaScript object is more like a **bag of key → value pairs** that can grow and shrink while the program runs. A good mental picture is `std::unordered_map<std::string, anything>`.

:::cpp Objects are shared, like pointers
In JavaScript, a variable does not *contain* an object — it holds a **reference** to it (think: a pointer). Copying the variable copies the reference, not the object:

```js
const a = { x: 1 };
const b = a;        // b points to the SAME object
b.x = 99;
console.log(a.x);   // 99  — like two C++ pointers to one object
```

This matters a lot in Chapter 4, where the same `orderDetail` object travels through many functions.
:::

## 0.7 Arrays — like `std::vector`

```js
const arr = [10, 20, 30];
arr.push(40);              // like v.push_back(40)
console.log(arr.length);   // 4     (like v.size())
console.log(arr[0]);       // 10
console.log(arr);          // [ 10, 20, 30, 40 ]
```

Arrays grow automatically and can even hold mixed types: `[1, "two", true]`.

## 0.8 Functions are values

This is the **most important difference** from C++ for these notes. In JavaScript a function is a normal value: you can store it in a variable, pass it to another function, and return it from a function. There are three common ways to write one:

```js
function add(a, b) {            // 1. function declaration
  return a + b;
}

const sub = function (a, b) {   // 2. function expression (stored in a variable)
  return a - b;
};

const mul = (a, b) => a * b;    // 3. arrow function (short and modern)

console.log(add(2, 3), sub(9, 4), mul(3, 4));   // 5 5 12
```

### Arrow function rules (read carefully!)

```js
const square = x => x * x;              // 1 parameter: ( ) optional
const hello  = () => console.log("Hi"); // 0 parameters: ( ) required
const add2   = (a, b) => a + b;         // 2+ parameters: ( ) required

// Without { } the value is returned automatically.
// With { } you MUST write return yourself:
const sum = (a, b) => {
  const s = a + b;
  return s;
};

// To return an object directly, wrap it in ( ):
const makeUser = name => ({ name: name });
console.log(makeUser("Rohit"));   // { name: 'Rohit' }
```

:::cpp Arrow functions ≈ C++ lambdas
```cpp
auto square = [](int x) { return x * x; };
auto add2   = [](int a, int b) { return a + b; };
```
```js
const square = x => x * x;
const add2 = (a, b) => a + b;
```
JavaScript arrow functions can use outside variables automatically (no capture list `[&]` needed). They also handle `this` in a special way — Chapter 10 explains it.
:::

## 0.9 Callbacks — the idea behind this whole book

:::def Callback
A **callback** is a function that you **give to another function**, so that the other function can **call it back** — now, or later.
:::

```js
function doTwice(action) {   // action is a function!
  action();
  action();
}

doTwice(() => console.log("Hello"));
```

```output
Hello
Hello
```

```cpp
// The same idea in C++
void doTwice(std::function<void()> action) { action(); action(); }
doTwice([]() { std::cout << "Hello\n"; });
```

You already used callbacks in C++ without calling them that: the comparator you pass to `std::sort` is a callback! In JavaScript they are everywhere: array methods (Chapter 1), timers and events (Chapter 3), and async code (Chapters 4–7).

## 0.10 Loops, destructuring and spread

`for`, `while` and `do…while` are the same as C++. JavaScript adds **`for…of`**, which is exactly C++'s range-based `for`:

```js
for (const x of [10, 20, 30]) {
  console.log(x);          // 10, then 20, then 30
}
// C++:  for (int x : v) std::cout << x;
```

**Destructuring** unpacks arrays and objects into variables (like C++17 structured bindings `auto [a, b] = pair;`):

```js
const [a, b] = [10, 20];                          // a = 10, b = 20
const { name, age } = { name: "Rohit", age: 30 }; // name = "Rohit", age = 30
```

**Spread** `...` "opens the box" and spreads the items out:

```js
const nums = [1, 2, 3];
const more = [...nums, 4, 5];
console.log(more);   // [ 1, 2, 3, 4, 5 ]
```

## 0.11 Errors: `throw`, `try`, `catch`

Very similar to C++:

```js
try {
  throw new Error("Something went wrong");
} catch (error) {
  console.log(error.message);   // Something went wrong
}
```

```cpp
try {
    throw std::runtime_error("Something went wrong");
} catch (const std::exception& e) {
    std::cout << e.what();
}
```

In JavaScript you can `throw` any value (even a plain string), and a real `Error` object has a `.message` property.

## 0.12 Things to Remember

:::remember
- JavaScript runs inside an **engine** (V8). The browser gives you `window` and `document`; Node.js gives you `global` and files.
- Use `const` by default, `let` when the value changes, avoid `var`. A `const` object can still be modified inside.
- All numbers are 64-bit floating point (like C++ `double`).
- Missing property → `undefined` (no crash). `null` = "empty on purpose".
- Always use `===` / `!==`.
- Objects and arrays are handled by **reference** (like pointers).
- Functions are **values**. Arrow functions: `x => x * 2`. With `{ }` you must write `return`.
- A **callback** is a function passed to another function to be called later.
:::
