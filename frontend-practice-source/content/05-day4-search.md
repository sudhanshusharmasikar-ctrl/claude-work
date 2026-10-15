:::chapter 4 | The Real Question: E-commerce Search Box | Exercise 05 ⭐ · arrays · filter · creating elements
- **Arrays**: lists of values, and looping with `forEach`
- **`filter`**: keeping only the items you want
- Case-insensitive matching with `toLowerCase()` and `includes()`
- The **`input`** event: reacting to every key press
- **Creating elements** with `createElement` and `appendChild`
- The most useful pattern in this guide: **one `render()` function** that redraws from the data
:::

:::day Today's plan (2 hours)
This is the question a candidate reported **word for word** from the real round, so today has one exercise and extra time. **0–35** new ideas (type every example in the console) · **35–45** starter files · **45–95** build · **95–105** grade · **105–120** review. Tomorrow morning, redo it from the starter files in under 25 minutes.
:::

## Exercise 05 · E-commerce Search Box ⭐

### What you are building

![The search box before and after](content/img/05.png){.shot}

A list of 8 products under a search input. As you type, only matching products stay, a counter says how many, and *No results found* appears when nothing matches. The grader checks:

| Test | What it does | Expects |
|---|---|---|
| renders all 8 products before typing | just opens the page | 8 `.result-item`s; `#count` contains `8` |
| filters case-insensitively as the user types | types `APPLE` | 3 items; `#count` contains `3`; `#empty` hidden |
| shows "No results found" for a non-matching query | types `zzzz` | 0 items; `#empty` visible |
| clearing the query restores all results | types `apple`, then clears the box | 8 items; `#empty` hidden |
| a partial query matches substrings | types `phone` | 2 items (Apple **iPhone**, Sony Head**phone**s) |

### New ideas

#### 1. Arrays and `forEach`

An **array** is an ordered list in square brackets. Positions are counted **from 0**, and `.length` is how many items there are. `forEach` runs a function **once for each item**, passing the item in:

```js title="an array and forEach"
const products = ['Apple iPhone', 'Samsung Galaxy', 'Apple Watch'];

products.forEach((product) => {
  console.log('->', product);
});
```

```output
-> Apple iPhone
-> Samsung Galaxy
-> Apple Watch
```

Read it as: *"for each product in products, print it"*. `products[0]` is `'Apple iPhone'`, and `products.length` is 3.

:::cpp C++ Corner
`products.forEach((product) => { ... })` is the same idea as `for (const auto& product : products) { ... }`. A normal `for (let i = 0; i < products.length; i++)` loop also works in JavaScript.
:::

#### 2. `filter`: keep only what you want

`filter` also calls your function once per item, but your function must **answer true or false**. Items that get `true` are kept in a **new** array; the original is not changed.

```js title="filter with a case-insensitive match"
const query = 'APPLE'.toLowerCase();
const matches = products.filter((product) => {
  return product.toLowerCase().includes(query);
});
console.log(query);
console.log(matches);
console.log(matches.length);
```

```output
apple
[ 'Apple iPhone', 'Apple Watch' ]
2
```

- `toLowerCase()` gives a lower-case copy of a string. Lower-casing **both sides** makes the match ignore case: `'APPLE'`, `'apple'` and `'Apple'` all become `'apple'`.
- `a.includes(b)` is `true` if the text `b` appears anywhere inside `a`. That's why `'phone'` finds *Sony Head**phone**s*.
- `return` sends the answer back to `filter`.

#### 3. A free gift: the empty string

```js title="every string contains the empty string"
console.log('Apple Watch'.includes(''));
console.log(products.filter((p) => p.toLowerCase().includes('')).length);
```

```output
true
3
```

When the search box is empty, the query is `''`, which every product contains, so the filter **keeps everything**. You don't need a special case for "show all when empty".

The second line also shows a **short arrow function**: with no `{ }`, the value after `=>` is returned automatically. `(p) => p.toLowerCase().includes('')` is the same as `(p) => { return p.toLowerCase().includes(''); }`.

#### 4. The `input` event

`'input'` fires on **every change** to a text box: each key press, each delete, a paste. (The `'change'` event only fires when the user **leaves** the box, which is too late for live search.)

```js title="react to typing"
searchInput.addEventListener('input', render);
```

Inside, `searchInput.value` is the full text in the box **at that moment**.

#### 5. Creating elements

To add an item to the page, you **create** an element, **fill** it, and **attach** it to a parent that's already on the page:

```js title="create, fill, attach"
const li = document.createElement('li');   // 1. create (not on the page yet)
li.className = 'result-item';               // 2. fill: give it a class...
li.textContent = 'Apple iPhone';            //    ...and its text
resultsList.appendChild(li);                // 3. attach: now it appears
```

`className` sets the whole `class` attribute. To **empty** a parent, set `resultsList.innerHTML = ''`, which removes everything inside it.

#### 6. Showing and hiding with `hidden`

Every element has a `hidden` property. `el.hidden = true` hides it; `el.hidden = false` shows it. `#empty` starts with the `hidden` attribute in the HTML, so it's invisible at first.

`matches.length > 0` is itself `true` or `false`, so this one line hides the message when there are matches and shows it when there are none:

```js title="a comparison is already a true/false value"
emptyText.hidden = matches.length > 0;
```

#### 7. The render pattern

Here is the idea that makes this exercise (and Days 5 and 9) easy:

[[fig:fp-render|One `render()` function rebuilds the list **from the data** every time. It doesn't try to work out which items to add or remove: it throws the old list away and draws the new one.]]

1. **Data:** the `products` array never changes.
2. **Input:** whatever is in the search box now.
3. **`render()`:** compute the matches, empty the list, create one `<li>` per match, update the count and the empty message.
4. Call `render()` **once at the start** (so 8 products show before any typing) and **again on every `input`**.

### Read the starter files

| File | What is there | What you will use |
|---|---|---|
| `index.html` | complete | `#search` (input), `#count` (p), `#results` (empty ul), `#empty` (p, `hidden`) |
| `style.css` | done except two rules | `.result-item` and `.empty` |
| `script.js` | the `products` array (**don't change it**) and `TODO` comments | everything below the array |

### The plan in plain English

1. Select `#search`, `#results`, `#count` and `#empty`.
2. Write `render()`:
    1. Read the box, trim it, lower-case it: that's the **query**.
    2. `filter` the products: keep those whose lower-cased name `includes` the query.
    3. Empty `#results`.
    4. For each match: create an `<li class="result-item">` with the name and append it.
    5. Set `#count` to, for example, `3 results`.
    6. Hide `#empty` when there are matches; show it when there are none.
3. Listen for `input` on the search box and call `render`.
4. Call `render()` once at the end of the file.
5. CSS: give `.result-item` padding, a light background, rounded corners and a hover colour; make `.empty` centered and grey.

:::tip Hint 1
Write `render()` so that it only does step 2.4 first, with `products` instead of `matches`. When you see all 8 items on load, add the filter.
:::

:::tip Hint 2
The skeleton:
```js title="render() skeleton"
function render() {
  const query = /* box text, trimmed, lower-cased */;
  const matches = products.filter((product) => /* true or false */);
  resultsList.innerHTML = '';
  matches.forEach((product) => { /* create, fill, attach */ });
  countText.textContent = /* `${...} results` */;
  emptyText.hidden = /* true when there are matches */;
}
```
:::

:::tip Hint 3
The filter test is `product.toLowerCase().includes(query)`. Show `#empty` when `matches.length` is 0. Make sure the last line of the file is `render();`.
:::

:::note Stop here and build it
Then run `npm test -- 05-ecommerce-search-box`.
:::

### The solution, line by line

```js title="05/script.js (below the products array)" lines start=13
const searchInput = document.getElementById('search');
const resultsList = document.getElementById('results');
const countText = document.getElementById('count');
const emptyText = document.getElementById('empty');

function render() {
  const query = searchInput.value.trim().toLowerCase();

  const matches = products.filter((product) => {
    return product.toLowerCase().includes(query);
  });

  resultsList.innerHTML = '';
  matches.forEach((product) => {
    const li = document.createElement('li');
    li.className = 'result-item';
    li.textContent = product;
    resultsList.appendChild(li);
  });

  const word = matches.length === 1 ? 'result' : 'results';
  countText.textContent = `${matches.length} ${word}`;

  emptyText.hidden = matches.length > 0;
}

searchInput.addEventListener('input', render);

render();
```

| Lines | What they do |
|---|---|
| 13–16 | **Select** the four elements. |
| 19 | The query: `'  APPle '` becomes `'apple'`. Methods are **chained**: each one works on the result of the one before. |
| 21–23 | **Filter**: a new array with only the matching names. The original `products` is untouched, so the next search starts from all 8 again. |
| 25 | Throw away the old list. Without this line, every key press would **add** items below the old ones. |
| 26–31 | **Create** one `<li>` per match. `textContent` (not `innerHTML`) puts the name in as plain text. |
| 33–34 | The count, with correct grammar: *1 result*, *3 results* (the ternary from Day 2). |
| 36 | Hide the empty message when there are matches, show it when there are none. |
| 39 | Re-render on every change to the box. `render` without brackets: we hand the function over. |
| 41 | Render once at load, so the page doesn't start empty. The grader's first test needs this. |

```css title="05/style.css"
.result-item {
  padding: 10px 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.result-item:hover {
  background: #ede9fe;
}

.empty {
  text-align: center;
  color: #94a3b8;
}
```

### Mistakes beginners make

:::mistake Forgetting `resultsList.innerHTML = ''`
Type `a`, then `p`: the list shows 8 + 7 + 4 = **19** items, because each `render()` appends its matches below the old ones. Always clear before you redraw.
:::

:::mistake Forgetting the `render()` call at the end
The page starts with an empty list and the first test fails (*expected 8 items, received 0*). The list only appears after you type.
:::

:::mistake `display: block` on `.empty`
If you add `display: block` to `.empty`, the `hidden` property stops working, because your CSS rule beats the browser's built-in `[hidden] { display: none }`. The *No results found* text would show all the time. Don't set `display` on elements you hide with `hidden`.
:::

:::mistake Lower-casing only one side
`product.includes(query.toLowerCase())` finds nothing for `apple`, because the product is `'Apple iPhone'` with a capital A. Lower-case **both**.
:::

### Interview questions

:::qa -
Q: What is the difference between `forEach`, `map` and `filter`?
All three call a function for each item. `forEach` returns nothing (use it for side effects such as creating elements). `map` returns a new array of the **same length** with each item transformed. `filter` returns a new array with only the items for which the function returned `true`.

Q: What is the difference between the `input` and `change` events?
`input` fires on every change to the value (each key press); `change` fires when the user commits the value, usually by leaving the field. Live search needs `input`.

Q: Why use `textContent` and not `innerHTML` to show a product name?
`textContent` treats the value as plain text. `innerHTML` parses it as HTML, so text coming from users could inject tags or scripts (an **XSS** attack). Use `innerHTML` only with text you control, and `innerHTML = ''` to empty an element.

Q: What if the list had 10,000 products coming from a server?
Rebuilding on every key press would get slow. Two common fixes: **debouncing** (wait until the user stops typing for about 300 ms, then search once), and asking the server to filter and return only the first few matches.
:::

### Practice twist

1. Add a **Clear** button: `<button id="clear" type="button">Clear</button>` after the input. On click, set the input's value to `''` and call `render()`.
2. Show `Showing all 8 products` when the box is empty, and `3 results` only while searching.
3. Harder: make `apple   watch` (several spaces) still find *Apple Watch*. Hint: remove the spaces from **both** the query and the product name before comparing, with `.replaceAll(' ', '')`.
