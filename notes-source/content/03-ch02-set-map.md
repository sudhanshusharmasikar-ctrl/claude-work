:::chapter 2 | Set and Map | Lecture 12
- `Set`: a collection with **no duplicates**
- `add`, `has`, `delete`, `clear` and `.size`
- Removing duplicates from an array in one line
- `Map`: key → value pairs where the key can be **anything**
- Why plain objects fail with object keys
- `set`, `get`, `has`, `delete`, looping with `for…of`
- When to use Array vs Set, Object vs Map
:::

## 2.1 `Set` — a list that never has duplicates

**First thought:** *A `Set` is a list that enforces uniqueness. It is a collection where duplicates are impossible.*

:::analogy A members-only club
Think of a club's member list. You can add a person to the list, but you **can't add the same person twice** — the list automatically ignores the second attempt. A `Set` handles this for you, automatically.
:::

### Creating a Set

You create a Set with `new Set()`. You can optionally pass an array (any *iterable*) to fill it. Duplicates are removed automatically.

```js
// Create an empty Set
const mySet = new Set();

// Create a Set from an array (duplicates are ignored)
const numbersArray = [1, 2, 3, 3, 4, 2, 5];
const numbersSet = new Set(numbersArray);
console.log(numbersSet);   // Set(5) { 1, 2, 3, 4, 5 }
```

[[fig:set-dedupe|Creating a Set from an array: the second `3` and the second `2` are dropped.]]

### Core methods (CRUD)

| Method | What it does | Returns |
|---|---|---|
| `.add(value)` | Adds a value. If it already exists, **does nothing**. | the Set itself (so you can chain `.add().add()`) |
| `.has(value)` | Checks if the value exists. | `true` / `false` |
| `.delete(value)` | Removes that value. | `true` if something was removed, else `false` |
| `.clear()` | Removes **everything**. | `undefined` |
| `.size` | How many values are inside (a **property**, no `()`). | a number |

```js
const userRoles = new Set();

// Add elements (add returns the Set, so we can chain calls)
userRoles.add("editor").add("viewer");
console.log(userRoles);                // Set(2) { 'editor', 'viewer' }

// Add a duplicate — nothing happens
userRoles.add("editor");
console.log(userRoles);                // Set(2) { 'editor', 'viewer' }

// Check for an element
console.log(userRoles.has("admin"));   // false
console.log(userRoles.has("editor"));  // true

// Delete an element
userRoles.delete("viewer");
console.log(userRoles.has("viewer"));  // false

// Clear the entire Set
userRoles.clear();
console.log(userRoles);                // Set(0) {}
```

:::mistake `.size`, not `.length`
Arrays have `.length`, but a Set has **`.size`** — and it is a property, so no parentheses: `numbersSet.size` → `5`. Writing `numbersSet.length` gives `undefined`.
:::

### Looping over a Set

A Set is **iterable**, so the best way to loop is `for…of`. Items come out in **insertion order** (the order you added them).

```js
const permissions = new Set(["read", "write", "execute"]);

for (const permission of permissions) {
  console.log(permission);
}
// read
// write
// execute

permissions.forEach(p => console.log(p.toUpperCase()));   // READ, WRITE, EXECUTE
```

A Set has **no index**: `permissions[0]` is `undefined`. If you really need positions, turn it into an array first: `[...permissions][0]` → `"read"`.

### Real-world use 1: remove duplicates from an array (the #1 use case)

```js
const duplicateEmails = ["a@a.com", "b@b.com", "a@a.com"];

// Convert to a Set to remove duplicates, then spread it back into a new array
const uniqueEmails = [...new Set(duplicateEmails)];
console.log(uniqueEmails);   // [ 'a@a.com', 'b@b.com' ]
```

Read `[...new Set(arr)]` from the inside out: **(1)** `new Set(arr)` removes the duplicates, **(2)** `[... ]` spreads the Set's values into a brand-new array. (`Array.from(new Set(arr))` does the same.)

### Real-world use 2: fast "have I seen this before?" checks

```js
// Imagine tracking unique visitors to a page
const visitedUsers = new Set();

function userVisits(userId) {
  if (!visitedUsers.has(userId)) {
    console.log(`Welcome, new visitor #${userId}!`);
    visitedUsers.add(userId);
  } else {
    console.log(`Welcome back, visitor #${userId}!`);
  }
}

userVisits(101);
userVisits(102);
userVisits(101);
```

```output
Welcome, new visitor #101!
Welcome, new visitor #102!
Welcome back, visitor #101!
```

`Set.has()` is **much faster** than `Array.includes()` for large data. `includes` checks the items one by one (O(n)); a Set uses hashing, so `has` is about O(1) — like a C++ `unordered_set`. With 10 items you won't notice; with 1,000,000 items the difference is huge.

:::cpp `Set` ≈ `std::unordered_set` (that remembers order)
| JavaScript `Set` | C++ `std::unordered_set` |
|---|---|
| `s.add(x)` | `s.insert(x)` |
| `s.has(x)` | `s.count(x)` / `s.contains(x)` (C++20) |
| `s.delete(x)` | `s.erase(x)` |
| `s.clear()` / `s.size` | `s.clear()` / `s.size()` |

One difference: a JavaScript Set **remembers insertion order**. `std::unordered_set` has no order, and `std::set` **sorts** the values. A JS Set never sorts.
:::

:::deep Objects are compared by reference
For objects, a Set checks **"is it the same object in memory?"** — not "does it look the same?":

```js
const s = new Set();
s.add({ id: 1 });
s.add({ id: 1 });    // a different object that only LOOKS the same
console.log(s.size); // 2
```
It is like a C++ set of **pointers**: two different pointers are two different keys, even if the objects they point to have equal contents. Strings and numbers are compared by value: `new Set(["a", "a"]).size` → `1`.
:::

| Use… | When you need… |
|---|---|
| **Array** | An **ordered list** where **duplicates are allowed** and you need index-based access (`arr[0]`). |
| **Set** | A collection of **unique values** where the main jobs are adding, deleting and checking whether something exists. |

## 2.2 `Map` — keys can be *anything*

**First thought:** *A `Map` is like an object, but its keys can be **anything** (not just strings).*

This is the most important difference. In a normal object `{}`, keys are **automatically converted to strings**. A `Map` keeps the key's real type, so you can use objects, functions, numbers, booleans… as keys.

### The problem with plain objects

```js
let myObject = {};
let keyObject1 = { id: 1 };
let keyObject2 = { id: 2 };

// Both keys get converted to the SAME string: "[object Object]"
myObject[keyObject1] = "Value for key 1";
myObject[keyObject2] = "Value for key 2";   // this overwrites the first one!

console.log(myObject);   // { '[object Object]': 'Value for key 2' }
```

[[fig:object-vs-map|With an object, every object key turns into the same string `"[object Object]"`. A Map keeps each object as its own key.]]

The same thing happens with numbers: `obj[1]` and `obj["1"]` are the **same** property, because `1` is converted to the string `"1"`.

### Creating a Map

Use `new Map()`. You can fill it at creation time with an array of `[key, value]` pairs:

```js
// Create an empty Map
const myMap = new Map();

// Create a Map with initial values — notice the different key types!
const userMap = new Map([
  ["name", "Alice"],       // string key
  [true, "is verified"],   // boolean key
  [100, "points"],         // number key
]);

console.log(userMap.get(true));    // "is verified"
console.log(userMap.get(100));     // "points"
console.log(userMap.get("100"));   // undefined — "100" (string) is not 100
```

### Core methods (CRUD)

| Method | What it does |
|---|---|
| `.set(key, value)` | Adds or updates a pair. Returns the Map, so you can chain. |
| `.get(key)` | Gives the value for that key, or `undefined` if the key doesn't exist. |
| `.has(key)` | `true` / `false` — does this key exist? |
| `.delete(key)` | Removes that pair. |
| `.clear()` | Removes all pairs. |
| `.size` | Number of pairs (property, no `()`). |

```js
const metadata = new Map();
let user1 = { name: "Alice" };
let user2 = { name: "Bob" };

// Set values using OBJECTS as keys
metadata.set(user1, { lastLogin: "2023-10-27" });
metadata.set(user2, { lastLogin: "2023-10-26" });

// Get a value using the exact same object reference
console.log(metadata.get(user1));   // { lastLogin: '2023-10-27' }
console.log(metadata.has(user2));   // true
console.log(metadata.size);         // 2

console.log(metadata.get({ name: "Alice" })); // undefined — a NEW object!
```

The last line is important: object keys work **by reference**, exactly like the Set in the previous section. You must use the *same* object (`user1`) to get the value back.

### Looping over a Map

A Map is iterable too. Each item is a `[key, value]` pair, so we use `for…of` with **destructuring**. Items come out in **insertion order**.

```js
const userMap = new Map([
  ["name", "Alice"],
  ["age", 30],
]);

// Use destructuring to unpack the [key, value] pair
for (const [key, value] of userMap) {
  console.log(`${key} -> ${value}`);
}
// name -> Alice
// age -> 30

console.log([...userMap.keys()]);     // [ 'name', 'age' ]
console.log([...userMap.values()]);   // [ 'Alice', 30 ]
userMap.forEach((value, key) => console.log(key, value)); // VALUE comes first!
```

:::cpp `Map` ≈ `std::unordered_map` / `std::map`
```cpp
std::unordered_map<std::string, int> m;
m["age"] = 30;                         // like  m.set("age", 30)
for (auto& [key, value] : m)           // C++17 structured bindings
    std::cout << key << " -> " << value << "\n";
```
Two differences to remember:

1. In C++, `m[key]` **inserts a default value** if the key is missing. In JavaScript, `map.get(key)` just returns `undefined` and **inserts nothing**.
2. A JavaScript Map keeps **insertion order**; `std::map` sorts by key and `std::unordered_map` has no order.
:::

:::mistake Using `[ ]` on a Map
```js
const m = new Map();
m["name"] = "Rohit";         // ❌ a normal object property, NOT a Map entry!
console.log(m.get("name"));  // undefined
console.log(m.size);         // 0

m.set("name", "Rohit");      // ✅ the correct way
console.log(m.get("name"));  // Rohit
```
:::

### Real-world uses of Map

1. **Storing extra data about objects (metadata).** This is the killer use case. You can "attach" data to an object without changing the object itself — great for keeping web-page elements clean:

    ```js
    const elementData = new Map();
    const button1 = document.querySelector("#btn1");

    // Associate some data with this specific button element
    elementData.set(button1, { clicks: 0, lastClickTime: null });

    // Now we can store and read data about button1 without ever doing
    // button1.mydata = ...  (which would pollute the DOM object)
    ```

2. **Caching (remembering results).** If a function does a slow calculation, store the answer in a Map. The argument is the key and the result is the value:

    ```js
    const cache = new Map();

    function slowSquare(n) {
      if (cache.has(n)) {
        console.log(`From cache: ${n}`);
        return cache.get(n);
      }
      console.log(`Calculating: ${n}`);
      const result = n * n;          // imagine a very heavy calculation here
      cache.set(n, result);
      return result;
    }

    slowSquare(4);   // Calculating: 4
    slowSquare(4);   // From cache: 4   (instant!)
    ```

3. **A "dictionary" with non-string keys.** Whenever your keys are not simple strings (objects, numbers you don't want converted, booleans…), a Map is the correct choice.

### Object or Map?

| Use… | When you need… |
|---|---|
| **Object** | A simple, fixed set of **string keys** that describe **one thing** — like a `user` with `name`, `age`, `email`. Easy to write, and works directly with JSON (Chapter 6). |
| **Map** | A **collection** of key → value pairs where keys can be **any type**, you add/remove entries often, you need `.size`, or insertion order matters. |

| Feature | Object `{}` | Map |
|---|---|---|
| Key types | strings (other types get converted to strings) | **anything** — objects, numbers, booleans, functions… |
| Number of entries | `Object.keys(obj).length` | `map.size` |
| Loop directly with `for…of` | No (use `Object.entries(obj)`) | Yes |
| Converts to JSON with `JSON.stringify` | Yes | Not directly (you get `{}`) |

## 2.3 Things to Remember

:::remember
- `new Set(array)` removes duplicates. `[...new Set(array)]` gives back a **unique array**.
- Set methods: `add` (chainable), `has`, `delete`, `clear`; count with **`.size`**.
- `Set.has` is fast (hashing, like `unordered_set`); `Array.includes` checks one by one.
- Sets and Maps keep **insertion order** and have **no index**.
- Objects inside a Set / as Map keys are compared **by reference** (same object in memory), not by content.
- In a plain object, keys become **strings** → two object keys collide as `"[object Object]"`. A **Map keeps the key's real type**.
- Map methods: `set` (chainable), `get` (→ `undefined` if missing), `has`, `delete`, `clear`, `.size`.
- Loop a Map with `for (const [key, value] of map)`. Never use `map[key] = value`.
:::

:::quiz
1. What is `new Set([1, 1, 2, 2, 3]).size`?
2. What does `[...new Set("hello")]` give? (Hint: a string is iterable.)
3. What does this print?

    ```js
    const m = new Map();
    const k = { id: 1 };
    m.set(k, "first");
    console.log(m.get(k), m.get({ id: 1 }));
    ```

4. What does this print? `const o = {}; o[1] = "a"; o["1"] = "b"; console.log(o[1]);`
5. You need to store the number of clicks for each button element on a page. Object or Map? Why?
:::

:::answer
1. `3`
2. `[ 'h', 'e', 'l', 'o' ]` — the second `l` is a duplicate, so it is dropped.
3. `first undefined` — the second `{ id: 1 }` is a brand-new object (a different reference).
4. `b` — the key `1` becomes the string `"1"`, so both lines write the **same** property.
5. A **Map**, because the keys are objects (button elements). In a plain object all of them would become `"[object Object]"`.
:::
