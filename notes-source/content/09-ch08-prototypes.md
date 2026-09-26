:::chapter 8 | Prototypes and Classes | Lecture 21 · Day 21 code
- The **problem**: copying the same method into every object
- The **prototype chain**: objects linked to other objects
- `[[Prototype]]`, `__proto__`, `Object.create()`, `hasOwnProperty`
- **Constructor functions** and what `new` really does
- The two "prototypes": `obj.__proto__` vs `Func.prototype`
- `class`, `constructor`, `extends`, `super` — and why they are "syntactic sugar"
- `this` inside a constructor
- Every experiment from the **Day 21** code
:::

By the end of this chapter you won't just know **how** to use prototypes and classes — you will understand **what they are**, so you can *reason* about object behaviour instead of guessing. We go step by step, exactly like the lecture: **Part 1** the problem → **Part 2** the prototype chain → **Part 3** constructor functions → **Part 4** classes.

## 8.1 Part 1 — the problem of repetition

The atom of JavaScript is the **object**: a simple bag of key → value pairs. Imagine we are making a small game with users:

```js
let user1 = {
  name: "Alice",
  score: 100,
  sayHi: function () {
    console.log("Hi, I'm " + this.name);
  },
};

let user2 = {
  name: "Bob",
  score: 50,
  sayHi: function () {
    console.log("Hi, I'm " + this.name);
  },
};

user1.sayHi();   // Hi, I'm Alice
user2.sayHi();   // Hi, I'm Bob
```

It works — but look at it from first principles. **What's the problem?**

1. **Inefficiency (memory):** the `sayHi` function is identical for both users, but JavaScript creates and stores **two separate copies** of it. With 1,000,000 users we'd have 1,000,000 copies of the same function — a huge waste. You can even prove they are different: `user1.sayHi === user2.sayHi` is **`false`**.
2. **Inefficiency (maintenance):** want to add an `increaseScore()` method to all users? You have to go back and add it to `user1`, `user2` and every other object. Want to fix a bug in `sayHi`? Fix it in every single object. A nightmare.

:::def The fundamental question
**How can many objects *share* one method without each owning a copy of it?**

The answer to this question is the reason prototypes exist: we need a **central place** to store the shared stuff, and a **way for each object to find it**.
:::

:::cpp In C++ you never had this problem
In C++, a member function is stored **once** in the program's code. Each object only stores its **data members** — `sizeof(User)` doesn't grow when you add methods. When you call `user1.sayHi()`, the compiler just passes `&user1` as the hidden `this` pointer.

A JavaScript object literal is different: `sayHi: function () {…}` creates a **new function object** every time the literal runs. Prototypes are how JavaScript gets the C++ behaviour: *methods stored once, shared by all objects*.
:::

[[fig:copies-vs-shared|Left: with object literals, each object carries its own copy of `sayHi`. Right: with a prototype, the data stays in each object but the method lives in ONE shared place.]]

## 8.2 Part 2 — the solution: the prototype chain

The creators of JavaScript solved the problem with one simple, powerful idea: **objects can be linked to other objects.**

Let's make a central object for all the shared methods and call it `userFunctions`:

```js
// A central place for all shared methods
const userFunctions = {
  sayHi: function () {
    console.log("Hi, I'm " + this.name);
  },
  increaseScore: function () {
    this.score++;
  },
};
```

How do our user objects find `userFunctions`? Through a secret link. **Every object in JavaScript has a hidden internal property called `[[Prototype]]`.** Think of it as a secret **"parent"** or **"fallback"** object.

When you try to read a property, JavaScript does this:

1. Does the **object itself** have this property? (`user1.name` → yes, `"Alice"`.)
2. If not, does its **`[[Prototype]]`** object have it?
3. If not, does **that** object's `[[Prototype]]` have it?
4. …and so on, until it reaches a `[[Prototype]]` that is **`null`** — then the answer is `undefined`.

This sequence of linked objects is called the **prototype chain**.

### Creating the link with `Object.create()`

`Object.create(proto)` creates a **new empty object** whose `[[Prototype]]` is `proto`:

```js
// Shared methods
const userFunctions = {
  sayHi: function () {
    console.log("Hi, I'm " + this.name);
  },
};

// Create a new user, but tell it to use userFunctions as its fallback/prototype
let user1 = Object.create(userFunctions);
user1.name = "Alice";
user1.score = 100;

let user2 = Object.create(userFunctions);
user2.name = "Bob";
user2.score = 50;

// LET'S TEST IT
user1.sayHi();   // "Hi, I'm Alice"
```

**What just happened when we called `user1.sayHi()`?**

1. JavaScript looked for `sayHi` on the `user1` object. It couldn't find it — `user1` only has `name` and `score`.
2. JavaScript didn't give up. It followed the hidden `[[Prototype]]` link from `user1` to the `userFunctions` object.
3. It looked for `sayHi` on `userFunctions`. **Found it!**
4. It executed the function. Crucially, the value of **`this`** inside the function was still **`user1`** — the object that *started* the call (the one before the dot).

[[fig:proto-chain|Looking up `user1.sayHi`: not on `user1` → follow the link → found on `userFunctions`. `toString` would be found one step higher, on `Object.prototype`. Past `null`, the answer is `undefined`.]]

We have solved the problem! There is **one** copy of `sayHi`, and both `user1` and `user2` can use it (`user1.sayHi === user2.sayHi` is now `true`). This is **prototypal inheritance** in its purest form. Let that sink in — this is the bedrock. Everything else in this chapter is just a more convenient way of creating this link.

:::cpp The prototype link ≈ the hidden vtable pointer
In C++, an object of a class with `virtual` functions secretly contains a **vptr** — a pointer to a shared **vtable** of functions. JavaScript's `[[Prototype]]` is a similar hidden pointer to a shared object. Two big differences:

- The prototype is a **normal object** — you can look at it and even change it while the program runs.
- Lookup happens **by name, at run time**, walking the chain like a **linked list** (`node = node->next` until `nullptr`). C++ resolves member names at **compile time**.
:::

## 8.3 Every object already has a prototype

You have been using prototypes all along without knowing it! A normal object literal is automatically linked to **`Object.prototype`**, which contains methods like `toString` and `hasOwnProperty`. Arrays are linked to **`Array.prototype`** (which has `push`, `map`, `filter`…), which is linked to `Object.prototype`.

[[fig:builtin-chains|The chains you get for free. This is why a plain object can call `toString()` and an array can call `map()` — the methods live on the prototypes, not on your object.]]

:::day Day 21 — experiment 1: methods you never wrote
```js title="Day 21 · index.js — experiment 1"
const obj = {
    name: "Rohit",
    age: 38,
    greet: function () {
        console.log("Hello Ji")
    }
};

console.log(obj.greet());                   // prints "Hello Ji", then undefined
obj.greet()                                 // prints "Hello Ji"

console.log(obj.hasOwnProperty("names"));   // false
console.log(obj.toString());                // [object Object]

const arr = [10, 20, 30];
console.log(arr.length)                     // 3
```

```output
Hello Ji
undefined
Hello Ji
false
[object Object]
3
```

- `console.log(obj.greet())` prints **two** lines: first `greet()` itself prints `Hello Ji`, then `console.log` prints what `greet()` **returned** — and it returns nothing, i.e. `undefined`.
- `obj.hasOwnProperty("names")` → `false`: `obj` has no **own** property called `names` (there's a typo on purpose — it's `name`).
- Where do `hasOwnProperty` and `toString` come from? We never wrote them! JavaScript didn't find them on `obj`, followed `[[Prototype]]`, and found them on **`Object.prototype`**.
- `arr.length` is the array's **own** property; `arr.push`, `arr.map`… come from **`Array.prototype`**.
:::

:::def `hasOwnProperty(key)`
Returns `true` only if the property is **directly on the object itself** — not somewhere up the prototype chain. So `obj.hasOwnProperty("name")` is `true`, but `obj.hasOwnProperty("toString")` is `false` (even though `obj.toString()` works).
:::

### `__proto__` — seeing and changing the link

The hidden `[[Prototype]]` can be read and written through the old accessor **`__proto__`** (two underscores on each side). Browsers show it in the console as `[[Prototype]]`.

:::day Day 21 — experiment 2: linking two objects by hand
```js title="Day 21 · index.js — experiment 2"
const obj2 = {
    account: 30
}

obj2.__proto__ = obj;      // obj2's parent/fallback is now obj

console.log(obj.hasOwnProperty("name"))   // true
```

After `obj2.__proto__ = obj`:

- `obj2.account` → `30` (its own property)
- `obj2.name` → `"Rohit"` — not on `obj2`, found on `obj` through the chain
- `obj2.greet()` → prints `Hello Ji`
- `obj.hasOwnProperty("name")` → `true` (`obj` itself has `name`), but `obj2.hasOwnProperty("name")` → `false`
:::

:::tip Modern, cleaner ways
`__proto__` is old and mostly kept for compatibility. Prefer `Object.create(proto)` to create a linked object, and `Object.getPrototypeOf(obj)` to read the link: `Object.getPrototypeOf(obj2) === obj` → `true`.
:::

## 8.4 Part 3 — constructor functions and `new` (the old way)

Creating objects with `Object.create()` and then adding properties one by one works, but it's tedious. For years, JavaScript developers used a standard pattern with normal functions.

**Any function** can become a "**constructor function**" if you call it with the **`new`** keyword. By convention we **capitalise** their names, to signal they're meant to be used this way.

```js
function User(name, score) {
  this.name = name;
  this.score = score;
}

// Where do we put the shared methods?
// Every function automatically gets a special public property called 'prototype'.
// This is NOT the hidden [[Prototype]]. It is a plain object.
User.prototype.sayHi = function () {
  console.log("Hi, I'm " + this.name);
};
User.prototype.increaseScore = function () {
  this.score++;
};

// Now we use the 'new' keyword
const user1 = new User("Alice", 100);
const user2 = new User("Bob", 50);

user1.sayHi();              // "Hi, I'm Alice"
user2.increaseScore();
console.log(user2.score);   // 51
```

This looks very different, but it achieves the **exact same result** as Part 2. The `new` keyword is the key.

### Demystifying `new`

When you call `new User("Alice", 100)`, **four things happen automatically** behind the scenes:

1. **Create an empty object:** a brand-new object is created, like `{}`.
2. **Link the prototype:** the new object's hidden `[[Prototype]]` is set to the constructor's **`prototype`** object (`User.prototype`). This is the most critical step — this is how `user1` gets connected to the shared methods.
3. **Execute the constructor:** the `User` function is called, and **`this` is set to the new object**. So `this.name = name;` really means `newObject.name = "Alice";`.
4. **Return `this`:** the function automatically returns the new object.

[[fig:new-steps|The four steps of `new User("Alice", 100)`.]]

So `new` is just an **automated recipe** for creating an object and setting up its prototype link for us.

:::deep Write your own `new` (to prove there's no magic)
```js
function myNew(Constructor, ...args) {
  const obj = Object.create(Constructor.prototype);   // steps 1 + 2
  Constructor.apply(obj, args);                       // step 3: run it with this = obj
  return obj;                                         // step 4
}

const u = myNew(User, "Zed", 1);
u.sayHi();                        // Hi, I'm Zed
```
(`apply` calls a function with a chosen `this` — Chapter 10 explains it. `...args` collects all the other arguments into an array.)
:::

:::cpp `new` in C++ vs `new` in JavaScript
C++ `new User("Alice", 100)`: allocate memory → run the constructor with `this` pointing to the new memory → return a **pointer**. JavaScript's `new` is the same recipe (create → link prototype → run constructor with `this` → return the object reference). The extra step is **linking the prototype**, which in C++ happens "for free" because methods belong to the class at compile time.
:::

:::mistake Arrow functions can't be constructors
`const Arrow = () => {}; new Arrow();` → `TypeError: Arrow is not a constructor`. Arrow functions have no `prototype` property and no own `this` (Chapter 10), so `new` can't use them.
:::

## 8.5 The two "prototypes" (the most confusing part!)

| | What it is | Where it lives |
|---|---|---|
| `user1.[[Prototype]]` — read it with `user1.__proto__` or `Object.getPrototypeOf(user1)` | the **actual hidden link** from an object to its parent / fallback | on **every object** |
| `User.prototype` | a **regular object** that sits on a constructor function; it will become the `[[Prototype]]` of every instance created with `new User()` | on **functions** (constructors and classes) |

[[fig:two-prototypes|`User.prototype` is an object hanging off the function. `new User()` makes each instance's hidden `[[Prototype]]` point to it.]]

```js
console.log(Object.getPrototypeOf(user1) === User.prototype); // true
console.log(user1.__proto__ === User.prototype);             // true
console.log(User.prototype.constructor === User);            // true (points back)
console.log(user1.prototype);   // undefined — plain objects have no .prototype
```

Understanding this distinction is the key to mastering prototypes. This pattern worked for over a decade, but it is a bit weird: the methods are defined **outside** the function body, and the `prototype` property is confusing. Programmers coming from Java, C++ or Python wanted a cleaner syntax…

## 8.6 Part 4 — the modern abstraction: `class`

The `class` keyword was introduced in ES2015 to make the Part 3 process look nicer and more familiar.

:::def Let me be clear
**`class` does not introduce a new object model to JavaScript.** It is **"syntactic sugar"** over the existing prototypal inheritance system. It does the **exact same thing** as the constructor-function pattern, just with a cleaner syntax.
:::

Let's rewrite `User` from Part 3 using `class`:

```js
class User {
  constructor(name, score) {
    this.name = name;
    this.score = score;
  }

  // Methods defined here are automatically put on User.prototype!
  sayHi() {
    console.log("Hi, I'm " + this.name);
  }

  increaseScore() {
    this.score++;
  }
}

const user1 = new User("Alice", 100);
const user2 = new User("Bob", 50);

user1.sayHi();              // "Hi, I'm Alice"
console.log(user2.score);   // 50
user2.increaseScore();
console.log(user2.score);   // 51
```

Let's break it down and prove it's the same thing:

- The **`constructor`** method is the same as our old `function User(...)`. It's what gets called when you use `new`.
- Any other methods you write inside the class (`sayHi`, `increaseScore`) are **automatically placed on `User.prototype`** for you. No more typing `User.prototype.whatever = …`.

**The proof:**

```js
// A class is really just a special kind of function
console.log(typeof User);                                 // "function"

// The methods are on the prototype, not on the instance
console.log(user1.hasOwnProperty('sayHi'));               // false
console.log(User.prototype.hasOwnProperty('sayHi'));      // true

// The instance's [[Prototype]] is linked to the class's .prototype
console.log(Object.getPrototypeOf(user1) === User.prototype);   // true
```

The evidence is clear. The `class` syntax is a clean, modern wrapper around the constructor function and prototype mechanism we built from first principles.

Small differences from a plain constructor function:

- A class **must** be called with `new`: `User("x", 1)` → `TypeError: Class constructor User cannot be invoked without 'new'`.
- The code inside a class body always runs in **strict mode** (Chapter 9).

:::cpp C++ class vs JavaScript class
| | C++ | JavaScript |
|---|---|---|
| Constructor | same name as the class: `User(...)` | always called `constructor(...)` |
| Data members | declared with types in the class | created by assigning `this.name = …` in the constructor |
| Methods stored | once, in the code | once, on `User.prototype` |
| Create an object | `User u("Alice", 100);` or `new User(...)` (pointer) | always `new User("Alice", 100)` (a reference) |
| Inheritance | `class Customer : public Person` | `class Customer extends Person` |
| Call parent constructor | initializer list `: Person(name, age)` | `super(name, age)` |
| Access the object | `this->name` (a pointer) | `this.name` |
| private / protected | keywords | everything public by default (`#field` makes it private) |
:::

## 8.7 Inheritance with `extends` and `super`

`extends` makes one class's prototype link to another's — something that used to be a very messy manual process. Here is the Day 21 example:

:::day Day 21 — experiments 4 & 5: `Person` and `Customer`
```js title="Day 21 · index.js"
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    sayHi() {
        console.log(`Hi ${this.name}`);
    }
}

class Customer extends Person {
    constructor(name, age, account, balance) {
        super(name, age);          // call Person's constructor FIRST
        this.account = account;
        this.balance = balance;
    }

    checkBalance() {
        return this.balance;
    }
}

const c1 = new Customer("Mohan", 20, 12, 540);

console.log(c1.checkBalance());   // 540
```

```output
540
```

- `class Customer extends Person` — every Customer **is a** Person, plus more.
- `super(name, age)` calls the **parent's constructor**, which sets `this.name` and `this.age`. Then the child adds its own properties.
- `c1.checkBalance()` is found on `Customer.prototype`. And `c1.sayHi()` works too (prints `Hi Mohan`) — it is found one step higher, on `Person.prototype`.
:::

[[fig:extends-chain|The prototype chain of `c1`. Data lives on the object; methods are found by walking up the chain.]]

```cpp
// The same thing in C++
class Person {
public:
    std::string name; int age;
    Person(std::string name, int age) : name(name), age(age) {}
    void sayHi() { std::cout << "Hi " << name << "\n"; }
};

class Customer : public Person {
public:
    int account; double balance;
    Customer(std::string name, int age, int account, double balance)
        : Person(name, age), account(account), balance(balance) {}
    double checkBalance() { return balance; }
};
```

:::mistake Using `this` before `super()`
In a child class constructor you **must** call `super(...)` **before** you touch `this`:

```js
class Customer extends Person {
  constructor(name, age) {
    this.account = 10;   // ❌ too early!
    super(name, age);
  }
}
new Customer("A", 1);
// ReferenceError: Must call super constructor in derived class
// before accessing 'this' or returning from derived constructor
```
Think of it like C++: the base part of the object must be constructed before the derived part.
:::

## 8.8 `this` inside a constructor

The `this` keyword is a special identifier whose value is decided by **how a function is called** (the whole story is in Chapter 10). In a **constructor**, `this` has a very specific and crucial job.

:::analogy The blank nametag
Imagine a conference registration desk:

1. The **`constructor`** is the **registration process**.
2. The parameters (`name`, `score`) are the **details you write on the registration form**.
3. The **`new`** keyword hands the constructor a **brand-new, blank nametag**. This blank nametag is **`this`**.

The constructor's job is to copy the details from the form onto that blank nametag:

- `this.name = name;` means *"take the `name` ('Alice') from the form and write it in the Name field of **this specific nametag**"*.
- `this.score = score;` means *"take the `score` (100) from the form and write it in the Score field of **this specific nametag**"*.

At the end, the constructor hands back the filled-out nametag — a complete object.
:::

**Technically**, when you call `new User("Alice", 100)`:

1. **Creates a brand-new, empty object** — call it `newInstance = {}`.
2. **Links the prototype** — `newInstance`'s prototype is set to `User.prototype`.
3. **Calls the constructor** — and (the most important part) sets **`this` to be `newInstance`**. Inside the constructor, `this` *is* the empty object created in step 1.
4. **Returns `this`** — the `new` expression gives back `newInstance`, now filled with properties.

So `this` is the mechanism that lets the constructor **populate the new object**.

### What would happen without `this`?

```js
class User {
  constructor(name, score) {
    // This is WRONG and does not work.
    // 'name' here just refers to the local parameter, not a property.
    name = name;
    score = score;
    // We never attached anything to the new object being created.
  }
}

const user1 = new User("Alice", 100);
console.log(user1.name);    // undefined
console.log(user1.score);   // undefined
```

The `user1` object is created, but it's **empty**, because we never used `this` to attach `name` and `score` to it. We only had local variables that disappeared when the constructor finished — like assigning to a parameter in a C++ constructor instead of to a member.

## 8.9 Day 21 code: the other experiments

### Experiment 3 — the repetition problem, live

```js title="Day 21 · index.js — experiment 3"
const obj1 = {
    name: "Rohit",
    age: 30,
    greet: function () {
        console.log(`Hello ${this.name}`);
    }
}

const obj2 = {
    name: "Mohit",
    age: 20,
    greet: function () {
        console.log(`Hello ${this.name}`);
    }
}

const obj3 = {
    name: "Mohan",
    age: 10,
    greet: function () {
        console.log(`Hello ${this.name}`);
    }
}
```

Three objects, **three copies** of the same `greet` function — exactly the Part 1 problem. In the Day 22 file the teacher writes a comment about exactly this: *"100 user: greet function: 100\*memory, code copy paste"*. This is what motivates prototypes and classes.

### Experiment 4 — a class instance vs an object literal in the console

```js title="Day 21 · index.js — experiment 4"
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    sayHi() {
        console.log(`Hi ${this.name}`);
    }
}

const person1 = new Person("Rohit", 20);
const person2 = new Person("Mohit", 10);
console.log(person1);

const ob1 = {
    name: "Mohan",
    age: 20,
    greet: function () {
    }
};
console.log(ob1);
```

```output label="Console (browser)"
Person {name: 'Rohit', age: 20}
{name: 'Mohan', age: 20, greet: ƒ}
```

Look closely: `person1` shows **only data** (`name`, `age`) — `sayHi` is not inside it, because it lives on `Person.prototype` (expand `[[Prototype]]` in the console to see it). But `ob1` shows `greet: ƒ` as its **own** property — every such literal carries its own copy. (Node.js prints `Person { name: 'Rohit', age: 20 }` and `greet: [Function: greet]`.)

### Experiment 6 — `Object.create()` (the active code in the file)

```js title="Day 21 · index.js — experiment 6"
const obj = {
    name: "Rohit",
    age: 20
}

const obj2 = Object.create(obj);
obj2.account = 10;

console.log(obj2.account);
```

```output
10
```

`Object.create(obj)` makes a new, empty object whose `[[Prototype]]` is `obj`. We give it one own property, `account`. So `obj2.account` → `10` (own property), and — even though `obj2` looks like `{ account: 10 }` — `obj2.name` → `"Rohit"`, found through the chain.

## 8.10 Final summary from first principles

1. **Problem:** creating many similar objects is inefficient because you duplicate shared functions in memory.
2. **Fundamental solution:** create a link (`[[Prototype]]`) from each instance object to a shared "prototype" object.
3. **Mechanism:** when you access a property, JavaScript checks the instance first, then follows the `[[Prototype]]` links up the chain until it finds the property or the chain ends (`null`).
4. **Old implementation:** a **constructor function** with the `new` keyword, which automates creating a new object and linking its `[[Prototype]]` to the function's `.prototype` property.
5. **Modern abstraction:** the **`class`** keyword — a much cleaner syntax for doing the exact same thing.

## 8.11 Things to Remember

:::remember
- Every object has a hidden **`[[Prototype]]`** link (read it with `Object.getPrototypeOf(obj)` or `obj.__proto__`).
- Property lookup: **own property → prototype → prototype's prototype → … → `null` → `undefined`**.
- `this` inside a method found on the prototype is still **the object before the dot**.
- `Object.create(proto)` → a new empty object linked to `proto`.
- `hasOwnProperty(key)` → `true` only for the object's **own** properties.
- `new F()`: ① create `{}` ② link it to `F.prototype` ③ run `F` with `this` = the new object ④ return it.
- `F.prototype` (on functions) ≠ `obj.[[Prototype]]` (on every object). `new` connects them.
- `class` = syntactic sugar: `typeof MyClass === "function"`; methods go on `MyClass.prototype`; must use `new`; strict mode inside.
- `extends` links the prototypes; in a child constructor call **`super(...)` before using `this`**.
- In a constructor, **`this` is the new object** being built; without `this.x = …` nothing is stored on it.
:::

:::quiz
1. What is printed?

    ```js
    const parent = { greet() { return "hi"; } };
    const child = Object.create(parent);
    console.log(child.greet(), child.hasOwnProperty("greet"));
    ```

2. Name the four things `new` does.
3. What is `typeof class A {}`?
4. What is wrong here, and what error do you get when you run `new B()`?

    ```js
    class B extends A {
      constructor() {
        this.x = 1;
        super();
      }
    }
    ```

5. Why does `console.log(person1)` in Day 21 not show `sayHi`?
6. `const arr = [1, 2]`. Is `push` an own property of `arr`? Where is it?
:::

:::answer
1. `hi false` — `greet` is found on the prototype, not on `child` itself.
2. Create an empty object → link its `[[Prototype]]` to `Constructor.prototype` → run the constructor with `this` = the new object → return it.
3. `"function"` — a class is a special function.
4. `this` is used before `super()` → `ReferenceError: Must call super constructor in derived class before accessing 'this'…`. Call `super()` first.
5. Because `sayHi` is stored on `Person.prototype`, not on the object itself. The object only holds its data.
6. No (`arr.hasOwnProperty("push")` is `false`). It lives on `Array.prototype`.
:::
