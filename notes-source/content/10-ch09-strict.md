:::chapter 9 | Strict Mode | Lecture 22 · Day 22 code
- Why strict mode exists: **silent errors → loud errors**
- How to switch it on with `'use strict'`
- The 4 big differences (+ 2 small ones)
- Why modern code is already strict (modules, classes)
:::

## 9.1 The first principle: turning silent errors into loud errors

Early versions of JavaScript were designed to be **extremely forgiving**. The philosophy was: *"Don't stop the code from running, even if something looks wrong. Just make a guess and keep going."* This is **non-strict mode**, often called **"sloppy mode"**.

The problem with this forgiveness is that it **hides bugs**. Your code might run, but it might be doing something completely different from what you intended. These are called **silent errors**.

**Strict mode** was introduced in **ES5 (2009)** as a way to opt in to a less forgiving, more secure and more sensible version of the language.

:::def The first principle of strict mode
Its purpose is to change "sloppy" JavaScript — code with silent errors or "bad syntax" — into code that **throws immediate, obvious errors**. It helps you write better, safer code by forcing you to be more explicit.
:::

:::analogy The lenient parent vs. the strict teacher
- **Non-strict mode (the lenient parent):** you make a mess in your room (write bad code). The lenient parent just shrugs and cleans it up for you — the code runs, but maybe not how you expect. You might not even realise you made a mess.
- **Strict mode (the strict teacher):** you make a mess in your homework. The strict teacher immediately gives you an "F" and tells you **exactly** what you did wrong. It's harsh, but you learn from your mistake and don't make it again.
:::

:::cpp Like compiling with `-Wall -Werror`
C++ compilers can warn you about suspicious code, and `-Werror` turns those warnings into **errors** that stop the build. Strict mode is JavaScript's version of that: code that was *silently accepted* now **fails loudly**. (And some things strict mode forbids — like using a variable you never declared — are compile errors in C++ anyway!)
:::

## 9.2 How to use it

Put this string at the **very top** of a file, or at the very top of a function:

```js
'use strict';
```

```js
// File-level strict mode (recommended) — must be the FIRST statement of the file
'use strict';

function myStrictFunction() {
  // This whole function runs in strict mode
}
```

```js
// Function-level strict mode
function mySloppyFunction() {
  // This function is in non-strict mode
}

function myInnerStrictFunction() {
  'use strict';
  // Only this function is in strict mode
}
```

:::mistake Spelling matters — and so does position
- It must be exactly **`'use strict'`** (with a **space**). A version with a hyphen, `'use-strict'`, is just an ordinary string that does **nothing** — the code stays sloppy. (Watch out: one of the lecture examples has this typo.)
- It must be the **first statement** of the file or function. If any other code comes before it, it is ignored.
:::

## 9.3 The core differences in detail

### 1. Prevents accidental global variables

This is the **biggest and most important** feature. In non-strict mode, if you assign a value to a variable that was never declared, JavaScript "helpfully" **creates a global variable** for you (on `window` in the browser). This is a huge source of bugs — for example, a simple typo in a variable name silently creates a new global.

```js
// Non-strict mode (sloppy)
function createMistake() {
  // Forgot to use let, const or var
  mistake = "I am now a global variable!";   // no error!
}
createMistake();
console.log(window.mistake);   // "I am now a global variable!"
```

```js
// Strict mode (safe)
'use strict';
function avoidMistake() {
  mistake = "This will not work";   // loud error!
}
avoidMistake();   // ❌ ReferenceError: mistake is not defined
```

### 2. Changes the behaviour of `this`

In a **simple function call** (no object before the dot), `this` behaves differently. (Chapter 10 explains `this` completely.)

```js
// Non-strict mode: this defaults to the global object (window in the browser)
function logThis() {
  console.log(this);
}
logThis();   // logs the window object
```

```js
// Strict mode: this is undefined
'use strict';
function logThis() {
  console.log(this);
}
logThis();   // logs undefined
```

This is safer: it prevents you from accidentally reading or modifying the global object.

### 3. Prohibits duplicate parameter names

This is just bad practice, and strict mode forbids it.

```js
// Non-strict mode: the last parameter wins, and there is no error
function sloppy(param1, param1) {
  console.log(param1);   // the value of the SECOND param1 is used
}
sloppy(10, 20);   // logs 20
```

```js
// Strict mode: this is a SyntaxError — the code won't even run
'use strict';
function strict(param1, param1) { }
// ❌ SyntaxError: Duplicate parameter name not allowed in this context
```

### 4. Makes `eval()` safer

`eval()` is powerful and dangerous, because it can run any **string** as code. Strict mode puts a cage around it.

```js
// Non-strict mode: eval() can create new variables in the surrounding scope
eval("var x = 2;");
console.log(x);   // 2
```

```js
// Strict mode: variables created inside eval() stay inside eval()'s own scope
'use strict';
eval("var x = 2;");
console.log(x);   // ❌ ReferenceError: x is not defined
```

(In real code, avoid `eval` completely.)

### Summary table

| Feature / behaviour | Non-strict mode (sloppy) 🚨 | Strict mode ✅ |
|---|---|---|
| **Undeclared variables** | creates a global variable | throws a `ReferenceError` |
| **`this` in simple calls** | points to the global object (`window`) | is `undefined` |
| **Duplicate parameters** | allowed, the last one wins | `SyntaxError` |
| **`eval()` scope** | can create variables in the surrounding scope | variables stay inside `eval()` |
| **Deleting a variable** (`delete myVar`) | silently fails | `SyntaxError` |
| **Octal literals** (`010`) | `010` is 8 (surprise!) | `SyntaxError` (write `0o10` if you really mean octal) |

## 9.4 Is this still relevant today?

**Yes, more than ever!** The good news is that you often get strict mode **for free**:

- **JavaScript modules** (files using `import` / `export`) are **always** in strict mode.
- **Code inside a `class` body** is **always** in strict mode.

Because modern JavaScript development (React, Node.js projects…) is almost entirely based on modules, most of the code you write is already running in strict mode by default.

**Recommendation:** always write in strict mode. Put `'use strict';` at the top of any standalone script file that isn't a module, to make sure you are writing safe, modern, robust code.

:::day Day 22 — strict mode in the code
The Day 22 file uses `'use strict'` many times (commented in and out) to compare behaviours. The teacher's notes at the top of the file summarise it:

```js title="Day 22 · index.js (the teacher's notes)"
// strict mode vs non strict mode
// 'use strict'
// normal function: non strict mode, this will point to global object
// in strict mode: It will point to undefined
```
We'll run all those experiments in the next chapter, together with the `this` keyword.
:::

## 9.5 Things to Remember

:::remember
- Strict mode turns **silent errors into loud errors**. Enable it with `'use strict';` as the **first statement** of a file or function (spelled with a space!).
- Assigning to an undeclared variable → `ReferenceError` (instead of silently creating a global).
- In a plain function call, `this` is `undefined` (instead of `window`/`global`).
- Duplicate parameter names, `delete` of a variable, and `010` octal literals → `SyntaxError`.
- `eval` can't leak variables into the surrounding scope.
- **Modules and class bodies are always strict.**
:::

:::quiz
1. What happens in sloppy mode vs strict mode? `function f() { total = 5; } f();`
2. Which one enables strict mode: `'use-strict'` or `'use strict'`?
3. In strict mode, what does `function show() { return this; } show()` return?
4. Name two places where code is automatically strict.
:::

:::answer
1. Sloppy: a **global variable** `total` is silently created. Strict: `ReferenceError: total is not defined`.
2. `'use strict'` (with a space). The hyphen version does nothing.
3. `undefined`.
4. ES modules (`import`/`export` files) and `class` bodies.
:::
