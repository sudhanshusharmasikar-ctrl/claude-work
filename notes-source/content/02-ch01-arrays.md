:::chapter 1 | Array Superpowers: forEach, map, filter, reduce | Lecture 12
- What a **higher-order function** is
- `forEach` — the simple looper
- `map` — the transformer
- `filter` — the bouncer
- `reduce` — the snowball
- `find`, `some`, `every`
- Chaining methods together
- Which method to choose (cheat sheet)
:::

## 1.1 The big idea: tell the array *what*, not *how*

In C++ you usually write a `for` loop and manage the index yourself. JavaScript arrays come with built-in methods where **you only say what should happen to each item** — the method does the looping for you.

```js
const prices = [100, 200, 300];

// Old way (C++ style): we manage everything ourselves
const doubled = [];
for (let i = 0; i < prices.length; i++) {
  doubled.push(prices[i] * 2);
}

// New way: we only say WHAT to do with each price
const doubled2 = prices.map(price => price * 2);

console.log(doubled);    // [ 200, 400, 600 ]
console.log(doubled2);   // [ 200, 400, 600 ]
```

Both give the same answer, but the second one is shorter and says clearly what we want.

:::def Higher-Order Function
A **higher-order function** is a function that **takes another function as an argument** (or returns a function). `map`, `filter`, `reduce`, `forEach`… are higher-order functions. The function you pass in (like `price => price * 2`) is the **callback**.
:::

### What happens inside? (No magic!)

`map` is just a normal loop written for you. If you wrote it yourself, it would look like this:

```js
function myMap(array, callback) {
  const result = [];
  for (let i = 0; i < array.length; i++) {
    result.push(callback(array[i], i, array));   // call YOUR function for each item
  }
  return result;
}

console.log(myMap([1, 2, 3], x => x * 10));   // [ 10, 20, 30 ]
```

So the array method **calls your callback once for every element**, and gives it three things: the **element**, its **index**, and the **whole array**. Most of the time we only use the first one (sometimes the second).

:::cpp You already know these from the STL!
The C++ Standard Library has the same ideas, only with longer syntax:

| JavaScript | C++ STL (`<algorithm>` / `<numeric>`) |
|---|---|
| `arr.forEach(fn)` | `std::for_each(v.begin(), v.end(), fn)` or `for (auto& x : v)` |
| `arr.map(fn)` | `std::transform(v.begin(), v.end(), out.begin(), fn)` |
| `arr.filter(fn)` | `std::copy_if(v.begin(), v.end(), std::back_inserter(out), fn)` |
| `arr.reduce(fn, init)` | `std::accumulate(v.begin(), v.end(), init, fn)` |
| `arr.find(fn)` | `std::find_if(v.begin(), v.end(), fn)` |
| `arr.some(fn)` / `arr.every(fn)` | `std::any_of(...)` / `std::all_of(...)` |
:::

## 1.2 Our sample data

All examples in this chapter use this array of products (from the lecture):

```js
const products = [
  { id: 1, name: "Laptop",       category: "Electronics", price: 1200, inStock: true  },
  { id: 2, name: "Book",         category: "Books",       price: 30,   inStock: true  },
  { id: 3, name: "Coffee Maker", category: "Appliances",  price: 150,  inStock: false },
  { id: 4, name: "Headphones",   category: "Electronics", price: 200,  inStock: true  },
];
```

It is an **array of objects**. Picture it as a small table:

| index | id | name | category | price | inStock |
|---|---|---|---|---|---|
| 0 | 1 | Laptop | Electronics | 1200 | `true` |
| 1 | 2 | Book | Books | 30 | `true` |
| 2 | 3 | Coffee Maker | Appliances | 150 | `false` |
| 3 | 4 | Headphones | Electronics | 200 | `true` |

## 1.3 `forEach()` — the simple looper

**First thought:** *"I want to walk along the conveyor belt and do something with each item, but I am not creating a new list."*

**Purpose:** run a function once for each element. It is a modern replacement for a simple `for` loop.

```js
array.forEach((element, index) => {
  // ... your code ...
});
```

- `element` — the current item being processed.
- `index` (optional) — the position of the current item.

```js
console.log("--- Our Products ---");
products.forEach(product => {
  console.log(`- ${product.name}`);
});
```

```output
--- Our Products ---
- Laptop
- Book
- Coffee Maker
- Headphones
```

Using the index too:

```js
products.forEach((product, index) => {
  console.log(`${index + 1}. ${product.name} costs $${product.price}`);
});
```

```output
1. Laptop costs $1200
2. Book costs $30
3. Coffee Maker costs $150
4. Headphones costs $200
```

(In `$${product.price}` the first `$` is just a dollar sign; `${ ... }` is the placeholder.)

**Key characteristics:**

- It does **not** return anything — it returns `undefined`.
- It does **not** create a new array.
- You **cannot** use `break` or `continue` inside it. A `return` inside the callback only ends the *current* call — it behaves like `continue`.

**When to use:** when you want to *do something* with each item and you don't need a new array — printing, updating the web page, saving each item to a database.

:::mistake Expecting forEach to give you something back
```js
const result = products.forEach(p => p.name);
console.log(result);   // undefined  ❌  — forEach never returns anything
```
If you want a new array, use `map`. If you need to stop early, use a normal `for…of` loop (or `find` / `some` / `every`, which stop by themselves).
:::

## 1.4 `map()` — the transformer

**First thought:** *"I have a list of raw materials. I want to put each one through a machine to create a **new list** of finished products."*

**Purpose:** create a **new array** by transforming **every** element of the original array.

```js
const newArray = array.map((element, index) => {
  return newValue;   // this value goes into the new array at the same position
});
```

**Key characteristics:**

- It **always** returns a **new array**.
- The new array **always** has the **same length** as the original.
- It is **non-mutating** — the original array is not changed.

Example — a list of only the product names:

```js
const productNames = products.map(product => {
  return product.name;
});
console.log(productNames);   // [ 'Laptop', 'Book', 'Coffee Maker', 'Headphones' ]
console.log(products.length); // 4  — the original `products` array is unchanged!

// Short form (arrow function without { } returns automatically):
const names = products.map(product => product.name);
```

Example — make new objects with a 10% discount:

```js
const sale = products.map(p => ({ name: p.name, price: p.price * 0.9 }));
console.log(sale);
```

```output
[
  { name: 'Laptop', price: 1080 },
  { name: 'Book', price: 27 },
  { name: 'Coffee Maker', price: 135 },
  { name: 'Headphones', price: 180 }
]
```

**When to use:** when you need a new array that is a modified version of the original. This is one of the most-used methods in JavaScript (and in React, later in your course!).

:::mistake Forgetting `return` inside `{ }`
```js
const names = products.map(p => { p.name; });   // ❌ curly braces, but no return
console.log(names);   // [ undefined, undefined, undefined, undefined ]
```
Fix: `products.map(p => p.name)` or `products.map(p => { return p.name; })`.
:::

## 1.5 `filter()` — the sieve (the bouncer)

**First thought:** *"I have a big list. I want to run each item through a test and create a **new, shorter list** with only the items that pass."* Think of a bouncer at a club door: only people who pass the check get in.

**Purpose:** create a new array containing only the elements that meet a condition.

```js
const newArray = array.filter((element, index) => {
  return trueOrFalse;   // true → keep this element, false → throw it away
});
```

**Key characteristics:**

- It **always** returns a **new array**.
- The new array has the **same length or fewer** items — never more.
- It is **non-mutating**.
- If nothing passes, you get an **empty array** `[]` (not `undefined`).

Example — only products that are in stock **and** in the "Electronics" category:

```js
const availableElectronics = products.filter(product => {
  // The condition must evaluate to true or false.
  // We combine two conditions with && (AND).
  return product.inStock === true && product.category === "Electronics";
});
console.log(availableElectronics);
```

```output
[
  { id: 1, name: 'Laptop', category: 'Electronics', price: 1200, inStock: true },
  { id: 4, name: 'Headphones', category: 'Electronics', price: 200, inStock: true }
]
```

A simple number example:

```js
const nums = [5, 12, 8, 130, 44];
console.log(nums.filter(n => n > 10));    // [ 12, 130, 44 ]
console.log(nums.filter(n => n > 999));   // []   (nobody passed)
```

**When to use:** whenever you need to select a subset of data based on one or more conditions (search results, "in stock only", "price below 500"…).

[[fig:mfr|`map`, `filter` and `reduce` on the same input. `map` keeps the length, `filter` keeps only some items, `reduce` produces one value.]]

## 1.6 `reduce()` — the accumulator (the snowball)

**First thought:** *"I want to roll this whole list into a **single final value**."* For example: the sum of all numbers, the total price, the most expensive item, or a count per category.

Imagine rolling a small snowball down a hill. At every step it picks up more snow. At the end you have **one** big snowball.

```js
const finalValue = array.reduce((accumulator, currentValue, index) => {
  // ... combine accumulator with currentValue ...
  return newAccumulator;   // becomes `accumulator` in the NEXT step
}, initialValue);
```

- `accumulator` — the value carried over from the previous step (the snowball).
- `currentValue` — the current element being processed.
- `initialValue` — the **starting value** of the accumulator (the small snowball you start with). This is a very important argument.

### A simple example first: sum of numbers

```js
const nums = [10, 20, 30, 40];
const total = nums.reduce((acc, curr) => acc + curr, 0);
console.log(total);   // 100
```

Let's trace it step by step:

| Step | `acc` (before) | `curr` | returned `acc + curr` → next `acc` |
|---|---|---|---|
| 1 | 0 *(initialValue)* | 10 | 10 |
| 2 | 10 | 20 | 30 |
| 3 | 30 | 30 | 60 |
| 4 | 60 | 40 | **100** ← final answer |

[[fig:snowball|The accumulator grows like a snowball: whatever you **return** becomes the accumulator of the next step.]]

### Lecture example: total value of items in stock

```js
const totalStockValue = products.reduce((total, product) => {
  console.log(`Current Total: ${total}, Current Product: ${product.name}, ` +
              `Price: ${product.price}`);
  if (product.inStock) {
    // The return value of this step becomes the 'total' for the NEXT step.
    return total + product.price;
  }
  // If not in stock, just return the current total without adding anything.
  return total;
}, 0); // Our initial value for the total is 0.

console.log(`\nFinal Total Stock Value: $${totalStockValue}`);
```

```output
Current Total: 0, Current Product: Laptop, Price: 1200
Current Total: 1200, Current Product: Book, Price: 30
Current Total: 1230, Current Product: Coffee Maker, Price: 150
Current Total: 1230, Current Product: Headphones, Price: 200

Final Total Stock Value: $1430
```

Notice the Coffee Maker step: it is **not** in stock, so we return `total` unchanged (1230 stays 1230). **You must return something in every step** — if a step returns nothing, the accumulator becomes `undefined`.

### `reduce` can build any type — even an object

The lecture says reduce is the most powerful method because it can return *anything*: a number, a string, an array or an object. Here we count products per category:

```js
const countByCategory = products.reduce((counts, product) => {
  counts[product.category] = (counts[product.category] || 0) + 1;
  return counts;
}, {});   // start with an empty object

console.log(countByCategory);   // { Electronics: 2, Books: 1, Appliances: 1 }
```

`(counts[x] || 0)` means *"the current count, or 0 if there is none yet"* (because a missing property is `undefined`).

:::cpp `reduce` = `std::accumulate`
```cpp
std::vector<int> nums = {10, 20, 30, 40};
int total = std::accumulate(nums.begin(), nums.end(), 0,
                            [](int acc, int x) { return acc + x; });   // 100
```
Same three ingredients: the data, the **initial value** (`0`), and a function that combines the accumulator with the current element.
:::

:::mistake Forgetting the initial value
If you skip `initialValue`, `reduce` uses the **first element** as the starting accumulator and begins from the second element. On an **empty array** this crashes:

```js
[].reduce((a, b) => a + b);    // ❌ TypeError: Reduce of empty array
                               //    with no initial value
[].reduce((a, b) => a + b, 0); // ✅ 0
```
Beginners: **always pass an initial value.**
:::

**When to use:** whenever you need one summary value from an array — sum, average, maximum, grouping items into an object.

## 1.7 `find()`, `some()` and `every()`

These three are for *finding and testing*. They all **stop early** as soon as they know the answer.

### `find()` — give me the first match

Like `filter`, but it **stops** and returns **the first element itself** that matches. If nothing matches, it returns `undefined`.

```js
const coffeeMaker = products.find(product => product.name === "Coffee Maker");
console.log(coffeeMaker);
// { id: 3, name: 'Coffee Maker', category: 'Appliances', price: 150, inStock: false }

const phone = products.find(product => product.name === "Phone");
console.log(phone);   // undefined
```

| | `filter` | `find` |
|---|---|---|
| Returns | an **array** of **all** matches | **one element** — the first match |
| Nothing matches | `[]` | `undefined` |
| Stops early? | No, checks every element | Yes, at the first match |

### `some()` — is there at least one?

Returns `true` if **at least one** element passes the test, otherwise `false`. It stops as soon as it finds one.

```js
const hasOutOfStockItems = products.some(product => product.inStock === false);
console.log(hasOutOfStockItems);   // true   (the Coffee Maker)
```

### `every()` — do all of them pass?

Returns `true` only if **all** elements pass the test. It stops as soon as one fails.

```js
const areAllItemsInStock = products.every(product => product.inStock === true);
console.log(areAllItemsInStock);   // false  (the Coffee Maker fails)
```

:::cpp STL cousins
`find` ≈ `std::find_if` (but C++ gives you an *iterator* and you compare it with `end()`; JavaScript gives you the element or `undefined`). `some` ≈ `std::any_of`, `every` ≈ `std::all_of`. Bonus: JavaScript also has `findIndex` (returns the index or `-1`) and `includes(value)` (true/false for simple values).
:::

## 1.8 Chaining: using methods one after another

`map` and `filter` return arrays, so you can call another method directly on the result. Read a chain from top to bottom like a recipe:

```js
// Names of products that are in stock
const inStockNames = products
  .filter(p => p.inStock)    // step 1: keep in-stock products
  .map(p => p.name);         // step 2: take only their names
console.log(inStockNames);   // [ 'Laptop', 'Book', 'Headphones' ]

// Total price of in-stock electronics
const total = products
  .filter(p => p.inStock && p.category === "Electronics")
  .reduce((sum, p) => sum + p.price, 0);
console.log(total);          // 1400
```

## 1.9 Cheat sheet: which method should I use?

| Method | What it returns | New array? | Changes original? | Use it when you want to… |
|---|---|---|---|---|
| `forEach` | `undefined` | No | No | **do something** for each item |
| `map` | new array, **same length** | Yes | No | **change** every item |
| `filter` | new array, **same or shorter** | Yes | No | **keep only some** items |
| `reduce` | **any single value** | — | No | **combine** everything into one value |
| `find` | first match or `undefined` | No | No | get **one** item |
| `some` | `true` / `false` | No | No | ask "is there **at least one**?" |
| `every` | `true` / `false` | No | No | ask "do **all** of them pass?" |

## 1.10 Things to Remember

:::remember
- These methods are **higher-order functions**: you pass them a **callback**, and they call it for each element with `(element, index, array)`.
- `map`, `filter` and `reduce` **never change the original array** (non-mutating).
- `map` → same length. `filter` → same or shorter. `reduce` → one value of any type.
- An arrow function **with `{ }` needs `return`**. Without `{ }` it returns automatically.
- In `reduce`, **return the accumulator in every step** and **always give an initial value**.
- `forEach` returns `undefined` and cannot `break`.
- `find` returns the element (or `undefined`); `filter` returns an array (maybe `[]`).
- `find`, `some` and `every` stop early. `some` = "at least one", `every` = "all".
:::

:::quiz
1. What does `[1, 2, 3].map(x => x * 2)` return?
2. What does `[1, 2, 3, 4].filter(x => x > 2)` return?
3. What is `[1, 2, 3].reduce((a, b) => a + b, 10)`?
4. What is `[5, 10, 15].find(x => x > 7)`?
5. What is printed? `const r = [1, 2].forEach(x => x * 2); console.log(r);`
6. For `[2, 4, 5]`, what do `every(x => x % 2 === 0)` and `some(x => x % 2 === 0)` return?
7. Why does `products.map(p => { p.price * 2 })` give an array of `undefined`?
:::

:::answer
1. `[2, 4, 6]`
2. `[3, 4]`
3. `16` (the accumulator starts from 10)
4. `10` — the first match itself, not an array
5. `undefined` — `forEach` never returns anything
6. `every` → `false` (5 is odd), `some` → `true`
7. Because the arrow function uses `{ }` but has no `return`, so every call returns `undefined`.
:::
