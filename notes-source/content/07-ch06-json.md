:::chapter 6 | JSON vs JavaScript Objects | Lecture 19 · Day 19 code
- What **JSON** is and why every language understands it
- The rules that make JSON different from a JS object
- `JSON.stringify()` — object → text
- `JSON.parse()` — text → object
- What JSON **drops** (functions, `undefined`)
- Why `fetch()` gives you JSON, and what `response.json()` does
- The Day 19 JSON experiments
:::

## 6.1 What is JSON, and why do we need it?

**JSON** = **J**ava**S**cript **O**bject **N**otation. It is a **text format** for storing and sending data. It *looks* like a JavaScript object, but it is really just a **string** that follows strict rules.

Why do we need a text format at all? When your browser talks to a server, it cannot send a JavaScript object "as it is" — an object lives in your computer's memory, and the server may be written in a completely different language (C++, Python, Java, Go…). So both sides agree on a **common text format**. JSON is that format — the "language" different systems use to talk to each other.

[[fig:json-journey|A JavaScript object is turned into JSON text, travels over the network, and any language can turn the text back into its own kind of object.]]

## 6.2 Quick visual comparison

```js
// JavaScript Object — lives in memory, used by your code
const jsObject = {
  name: "John",          // no quotes needed around the key
  age: 30,               // number
  active: true,          // boolean
  greet: function () {   // can have functions
    console.log("Hi!");
  },
  date: new Date(),      // can have Date objects
  score: undefined,      // can have undefined
};

// JSON — just a STRING with strict rules
const jsonString = `{
  "name": "John",
  "age": 30,
  "active": true
}`;
// Note: must use double quotes — no functions, no undefined, etc.
```

## 6.3 Key differences

| Feature | JavaScript Object | JSON |
|---|---|---|
| **Type** | a JavaScript data structure (in memory) | text / a string |
| **Keys** | can be unquoted: `name` | **must** use double quotes: `"name"` |
| **Strings** | single `'…'` or double `"…"` quotes | **only** double quotes `"…"` |
| **Data types** | string, number, boolean, array, object, function, Date, `undefined`, `null`, Symbol… | string, number, boolean, array, object, `null` — **only these** |
| **Functions** | ✅ allowed | ❌ not allowed |
| **`undefined`** | ✅ allowed | ❌ not allowed (`null` is fine) |
| **Date objects** | ✅ allowed | ❌ not allowed (stored as a string) |
| **Comments** | ✅ allowed | ❌ not allowed |
| **Trailing commas** | ✅ allowed | ❌ not allowed |

### Valid or not? Test yourself

| This text… | Valid JSON? | Why |
|---|---|---|
| `{"name": "John", "age": 30}` | <span class="pill yes">yes</span> | keys and strings in double quotes |
| `{name: "John"}` | <span class="pill no">no</span> | the key is not in double quotes |
| `{'name': 'John'}` | <span class="pill no">no</span> | single quotes are not allowed |
| `{"age": 30,}` | <span class="pill no">no</span> | trailing comma after the last value |
| `{"city": null}` | <span class="pill yes">yes</span> | `null` is a valid JSON value |
| `{"age": undefined}` | <span class="pill no">no</span> | `undefined` doesn't exist in JSON |
| `{"greet": function() {}}` | <span class="pill no">no</span> | functions are not data |
| `{"a": 1} // note` | <span class="pill no">no</span> | comments are not allowed |
| `[1, "two", true, null, {"x": [2, 3]}]` | <span class="pill yes">yes</span> | arrays and nesting are fine |

## 6.4 Converting between JSON and JavaScript objects

### JavaScript object → JSON string: `JSON.stringify()`

```js
const user = { name: "John", age: 30, active: true };

// Convert to a JSON string
const jsonString = JSON.stringify(user);
console.log(jsonString);          // {"name":"John","age":30,"active":true}
console.log(typeof jsonString);   // "string"
```

Want it readable? Pass `null, 2` to indent with 2 spaces:

```js
console.log(JSON.stringify(user, null, 2));
```

```output
{
  "name": "John",
  "age": 30,
  "active": true
}
```

### JSON string → JavaScript object: `JSON.parse()`

```js
const jsonString = '{"name":"John","age":30,"active":true}';

// Convert to a JavaScript object
const user = JSON.parse(jsonString);
console.log(user);          // { name: 'John', age: 30, active: true }
console.log(typeof user);   // "object"
console.log(user.name);     // "John"
```

:::remember An easy way to remember the names
**stringify** = make it a **string** (object → text). **parse** = read the text and build the object (text → object). Parse means "read and understand" — like a compiler *parses* your C++ source code.
:::

### What happens to things JSON can't store?

```js
const data = {
  name: "Alice",
  greet() { return "hi"; },               // function
  age: undefined,                         // undefined
  born: new Date("2000-01-01T00:00:00Z"), // Date
};

console.log(JSON.stringify(data));
// {"name":"Alice","born":"2000-01-01T00:00:00.000Z"}
```

- The **function** and the **`undefined`** property are **silently dropped**.
- The **Date** becomes a plain **string**. (After `JSON.parse` it stays a string — not a `Date` object.)

### Invalid JSON makes `JSON.parse` throw

```js
try {
  JSON.parse("{name: 'Rohit'}");   // ❌ not valid JSON (no double quotes)
} catch (error) {
  console.log(error.name);          // SyntaxError
}
```

If the text comes from outside (a server, a file, the user), wrap `JSON.parse` in `try`/`catch`.

## 6.5 Why does `fetch()` give us JSON?

```js
fetch("https://api.github.com/users")
  .then(response => {
    // response.body is a stream of JSON text
    console.log(typeof response);   // "object" (a Response object)
    return response.json();         // parses the JSON string → a JS object
  })
  .then(data => {
    // Now 'data' is a JavaScript array of objects
    console.log(typeof data);       // "object"
    console.log(data[0].login);     // you can access properties
  });
```

**The flow:**

1. The server sends the data as a **JSON string** (text).
2. `fetch()` receives it as a **Response object**.
3. `.json()` parses the JSON string → **JavaScript object** (it's like `JSON.parse`, but async, because the body may still be arriving).
4. Now you can use it like a normal JS object: `data[0].login`.

## 6.6 Practical example: sending and receiving

```js
// Creating a user object in JavaScript
const user = {
  name: "Alice",
  age: 25,
  greet() {
    console.log(`Hi, I'm ${this.name}`);
  },
};
user.greet();   // Works fine: Hi, I'm Alice

// Sending to a server (must convert to JSON)
const jsonToSend = JSON.stringify(user);
console.log(jsonToSend);   // {"name":"Alice","age":25}
// Notice: the greet() function is gone! JSON can't store functions.

// Receiving from a server
const jsonReceived = '{"name":"Bob","age":30}';
const userFromServer = JSON.parse(jsonReceived);
console.log(userFromServer.name);   // "Bob"
// userFromServer.greet();          // ❌ TypeError: userFromServer.greet is not a function
```

JSON carries only **data**, never **behaviour** (functions). That's why a parsed object has no methods.

## 6.7 Day 19 code: the JSON experiments

:::day Day 19 — `index.js`, the JSON part
These two small experiments sit between the `fetch` experiments and the Zomato code in the Day 19 file.
:::

### Object → JSON

```js title="Day 19 · index.js — JSON experiment 1"
const j1 = {
    name: "Rohit",
    age: 30,
    address: "dwarka",
}

// convert to json

const jsonFormat = JSON.stringify(j1);

console.log(jsonFormat);
```

```output
{"name":"Rohit","age":30,"address":"dwarka"}
```

Look at the differences: the keys now have **double quotes**, there are **no spaces**, and the **trailing comma** after `"dwarka"` (allowed in a JS object) is **gone** — it's not allowed in JSON.

### JSON → object

```js title="Day 19 · index.js — JSON experiment 2"
const jsonFormat = `{
    "name":"Rohit",
    "age": 30,
    "address": "dwarka"
}`;

// java script object

const JsObject = JSON.parse(jsonFormat);

console.log(JsObject);
```

```output
{ name: 'Rohit', age: 30, address: 'dwarka' }
```

- The JSON text is written with **backticks** because a template literal can span **multiple lines**.
- After `JSON.parse`, it is a real object: `JsObject.name` is `"Rohit"`, `JsObject.age + 1` is `31`.

:::mistake Running both experiments at the same time
Both experiments declare `const jsonFormat`. If you un-comment both together you get `SyntaxError: Identifier 'jsonFormat' has already been declared` — exactly like a C++ *redefinition* error. That's why the teacher keeps one of them commented out.
:::

:::cpp JSON in C++ (serialization)
Turning an object into text and back is called **serialization** / **deserialization**. C++ has no built-in JSON, but libraries like *nlohmann/json* do the same job:

```cpp
#include <nlohmann/json.hpp>
using json = nlohmann::json;

json j = { {"name", "Rohit"}, {"age", 30} };
std::string text = j.dump();        // like JSON.stringify  → {"age":30,"name":"Rohit"}
json back = json::parse(text);      // like JSON.parse
std::cout << back["name"];          // "Rohit"
```
Because JSON is plain text with fixed rules, a **C++ server** and a **JavaScript browser** can exchange data without knowing anything about each other's memory layout.
:::

## 6.8 Summary

- **JavaScript object:** the native JS data structure; can hold functions, dates, `undefined`, etc.
- **JSON:** a text format for data exchange; strict rules; only basic data types.
- **`JSON.stringify()`:** JS object → JSON string.
- **`JSON.parse()`:** JSON string → JS object.
- **`fetch().json()`:** automatically parses a JSON response → JS object (returns a Promise).

Think of **JSON** as the language different systems use to talk to each other, while **JavaScript objects** are what you actually work with in your code!

## 6.9 Things to Remember

:::remember
- JSON is **text** (a string). A JS object is a **data structure in memory**.
- JSON rules: **double quotes** for keys and strings, **no** functions, **no** `undefined`, **no** comments, **no** trailing commas. `null` is allowed.
- `JSON.stringify(obj)` → string. `JSON.stringify(obj, null, 2)` → pretty string.
- `JSON.parse(text)` → object. Invalid text → `SyntaxError` (use `try`/`catch`).
- `stringify` **drops** functions and `undefined` properties; Dates become strings.
- `response.json()` = "read the body and `JSON.parse` it" — and it returns a **Promise**.
:::

:::quiz
1. What is `typeof JSON.stringify({ a: 1 })`?
2. What does `JSON.stringify({ a: 1, b: undefined, c: () => 1 })` return?
3. Is `{'name': 'Rohit'}` valid JSON? Why?
4. After `const o = JSON.parse('{"x": 5}')`, what is `o.x * 2`?
5. Why does `response.json()` return a Promise instead of the data directly?
:::

:::answer
1. `"string"`
2. `'{"a":1}'` — `undefined` and functions are dropped.
3. **No** — JSON allows only double quotes.
4. `10` — after parsing, `o.x` is a real number.
5. Because reading the whole response body (and parsing it) takes time — it's asynchronous work.
:::
