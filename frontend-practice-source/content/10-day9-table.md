:::chapter 9 | Data on Screen: the Dynamic Table | Exercise 15 · objects · filter + sort · state + render
- **Objects**: one employee as `{ name, age, city }`, and arrays of objects
- Filtering on **two fields** with `||` (or)
- **Sorting** numbers and names correctly, and the default `sort()` trap
- **State + render**: remember the choices in variables, redraw from them every time
- Building table rows with a template
:::

:::day Today's plan (2 hours)
The hardest exercise in the 14, but you already know most of it from Day 4. **0–30** new ideas · **30–40** starter files · **40–95** build · **95–105** grade · **105–120** review. Tonight, read the Day 10 plan so you can start the mock round tomorrow without preparation.
:::

## Exercise 15 · Dynamic Table

### What you are building

![The table before and after](content/img/15.png){.shot}

A table of six employees, built by JavaScript from an array. A filter box keeps rows whose **name or city** contains the text, and two buttons sort by name (A–Z) or by age (youngest first). A line under the table counts the rows. The grader checks:

| Test | What it does | Expects |
|---|---|---|
| renders all rows on load | opens the page | 6 `<tr>`s in `#table-body`; `#row-count` contains `6` |
| filters by city, case-insensitively | types `LONDON` | 1 row, containing *Ada Lovelace* |
| a non-matching filter shows no rows | types `zzzz` | 0 rows |
| sorts by name A-Z | clicks **Sort by name** | the first row's name is *Ada Lovelace* |
| sorts by age ascending | clicks **Sort by age** | the first row's name is *Margaret Hamilton* (33) |

### New ideas

#### 1. Objects

An **object** groups named values (its **properties**) in curly braces. An array of objects is how almost all real data looks, from a list of products to a JSON reply from a server:

```js title="an array of objects"
const people = [
  { name: 'Grace', age: 45 },
  { name: 'Ada', age: 36 },
  { name: 'Alan', age: 41 },
];
console.log(people[1].name, people[1].age);
```

```output
Ada 36
```

`people[1]` is the second object; `.name` reads one property from it.

:::cpp C++ Corner
An object here is like a `struct Person { std::string name; int age; };`, written as a value on the spot, with no type declared first.
:::

#### 2. Filtering on two fields

The filter keeps an employee if the query is in the name **or** in the city. `||` means *or*: it's true if either side is true. When the test takes more than one line, the arrow function needs `{ }` and a `return`:

```js title="a filter test on two fields"
const rows = employees.filter((emp) => {
  const name = emp.name.toLowerCase();
  const city = emp.city.toLowerCase();
  return name.includes(query) || city.includes(query);
});
```

As on Day 4, an empty query is included in every name, so all rows are kept.

#### 3. Sorting: the trap and the fix

```js title="sort() without and with a compare function"
const nums = [10, 9, 100, 1];
console.log([...nums].sort());
console.log([...nums].sort((a, b) => a - b));
```

```output
[ 1, 10, 100, 9 ]                      #> sorted as TEXT: "10" < "9"
[ 1, 9, 10, 100 ]                      #> sorted as numbers
```

Without arguments, `sort()` compares items **as text**, letter by letter, so `'100'` comes before `'9'` (because `'1'` comes before `'9'`). Give it a **compare function** `(a, b) => ...` that returns:

- a **negative** number if `a` should come first,
- a **positive** number if `b` should come first,
- **0** if they're equal.

For numbers, `a - b` does exactly that (ascending). For text, use `localeCompare`:

```js title="localeCompare returns -1, 1 or 0"
console.log('Ada'.localeCompare('Grace'));
console.log('Grace'.localeCompare('Ada'));
console.log('Ada'.localeCompare('Ada'));
```

```output
-1                                     #> Ada comes first
1                                      #> Ada (b) comes first
0                                      #> equal
```

So sorting objects by a property is `(a, b) => a.age - b.age` or `(a, b) => a.name.localeCompare(b.name)`. (`[...nums]` makes a copy so the example's `nums` stays as it was; you don't need it in the exercise, as you'll see next.)

#### 4. `sort` changes the array; `filter` makes a new one

```js title="sorting a filtered copy leaves the original alone"
const copy = people.filter(() => true);
copy.sort((a, b) => a.age - b.age);
console.log(copy.map((p) => p.name));
console.log(people.map((p) => p.name));
```

```output
[ 'Ada', 'Alan', 'Grace' ]             #> the copy is sorted by age
[ 'Grace', 'Ada', 'Alan' ]             #> the original order is unchanged
```

`sort` rearranges the array **in place**. That would be a problem if you sorted `employees` itself, but `filter` always returns a **new** array, so sorting the filtered `rows` leaves the original data untouched. (`map` makes a new array with each item transformed; here it just picks out the names to print.)

#### 5. State + render

The table depends on **two** things the user controls: the filter text and the chosen sort. Keep the sort choice in a variable (the text is already in the input box), and let **one** `render()` build the table from both, every time anything changes:

[[fig:fp-table-flow|Two controls, one `render()`. Each listener only updates the state (or nothing, for the filter, whose state is the input box) and calls `render()`, which always runs the same four steps: filter, sort, draw, count.]]

Because `render()` always applies **both** the filter and the sort, they combine for free: filter for `o`, then sort by age, and you get the matching rows in age order.

#### 6. A row from a template

A `<tr>` with three `<td>` cells can be built in one line with a template literal and `innerHTML`:

```js title="one table row"
tr.innerHTML = `<td>${emp.name}</td><td>${emp.age}</td><td>${emp.city}</td>`;
```

This is safe **here** because the data is fixed in the file. If the text came from users, you would create each `<td>` and set its `textContent` (Day 4's XSS warning).

### Read the starter files

| File | What is there | What you will use |
|---|---|---|
| `index.html` | complete | `#filter`, `#sort-name`, `#sort-age`, an empty `<tbody id="table-body">`, `#row-count` |
| `style.css` | two empty rules | `th` and `td` |
| `script.js` | the `employees` array (**don't change it**) and comments | everything below it |

### The plan in plain English

1. Select the five elements.
2. State: `let sortBy = '';` (no sorting yet).
3. `render()`:
    1. The query: the input's text, trimmed and lower-cased.
    2. **Filter** employees whose name or city includes the query.
    3. **Sort** the result if `sortBy` is `'name'` or `'age'`.
    4. **Draw:** empty the `<tbody>`, then one `<tr>` per employee.
    5. **Count:** `6 employees` (or `1 employee`).
4. Listeners: `input` on the filter calls `render`; each sort button sets `sortBy` and calls `render()`.
5. Call `render()` at the end.
6. CSS: `th` gets a background, padding and left-aligned text; `td` gets padding and a bottom border.

:::tip Hint 1
Copy the structure of your Exercise 05 `render()`. The new parts are the second field in the filter, the sort step, and `<tr>` instead of `<li>`.
:::

:::tip Hint 2
Get the drawing working first, with no filter and no sort: `employees.forEach(...)` making rows. Then add the filter, then the sort.
:::

:::tip Hint 3
```js title="the sort step"
if (sortBy === 'name') {
  rows.sort((a, b) => a.name.localeCompare(b.name));
} else if (sortBy === 'age') {
  rows.sort((a, b) => a.age - b.age);
}
```
:::

:::note Stop here and build it
Then run `npm test -- 15-dynamic-table`.
:::

### The solution, line by line

```js title="15/script.js (below the employees array)" lines start=11
const filterInput = document.getElementById('filter');
const sortNameBtn = document.getElementById('sort-name');
const sortAgeBtn = document.getElementById('sort-age');
const tableBody = document.getElementById('table-body');
const rowCount = document.getElementById('row-count');

let sortBy = ''; // '' (no sorting), 'name' or 'age'

function render() {
  const query = filterInput.value.trim().toLowerCase();

  // 1. Filter: keep employees whose name or city contains the query
  const rows = employees.filter((emp) => {
    const name = emp.name.toLowerCase();
    const city = emp.city.toLowerCase();
    return name.includes(query) || city.includes(query);
  });

  // 2. Sort the filtered list
  if (sortBy === 'name') {
    rows.sort((a, b) => a.name.localeCompare(b.name));
  } else if (sortBy === 'age') {
    rows.sort((a, b) => a.age - b.age);
  }

  // 3. Draw one <tr> per employee
  tableBody.innerHTML = '';
  rows.forEach((emp) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${emp.name}</td><td>${emp.age}</td><td>${emp.city}</td>`;
    tableBody.appendChild(tr);
  });

  // 4. Update the count
  const word = rows.length === 1 ? 'employee' : 'employees';
  rowCount.textContent = `${rows.length} ${word}`;
}

filterInput.addEventListener('input', render);

sortNameBtn.addEventListener('click', () => {
  sortBy = 'name';
  render();
});

sortAgeBtn.addEventListener('click', () => {
  sortBy = 'age';
  render();
});

render();
```

| Lines | What they do |
|---|---|
| 17 | The state the user can change with buttons. The empty string means "keep the original order". |
| 20 | The current filter text, read fresh on every render. |
| 23–27 | A new array with only the matching employees. |
| 30–34 | Sort that new array in place, if a sort was chosen. |
| 37–42 | Clear the old rows and draw the new ones. |
| 45–46 | The count, with the right word. |
| 49 | Typing re-renders. |
| 51–59 | Each button changes the state, then re-renders. |
| 61 | Draw the table at load: 6 rows before any action. |

```css title="15/style.css"
th {
  text-align: left;
  background: #f8fafc;
  padding: 10px 12px;
  color: #64748b;
}

td {
  padding: 10px 12px;
  border-bottom: 1px solid #e2e8f0;
}
```

The repository's `solution/` keeps both pieces of state in one object, `const state = { query: '', sort: null };`, and updates `state.query` in the input listener. That shape is common in bigger apps (and in React); for one input and two buttons, both versions are fine.

### Mistakes beginners make

:::mistake `rows.sort()` with no compare function
Sorting objects without a compare function compares them as text (`"[object Object]"`), so nothing useful happens. Always pass `(a, b) => ...`.
:::

:::mistake `return a.age > b.age` in the compare function
It returns `true` / `false`, never a negative number, so `sort` can't tell which item comes first. In Chrome and Node.js it doesn't sort at all: we tried it on the six ages and got them back in their original order. Use `a.age - b.age`.
:::

:::mistake Sorting inside the button listener only
If the button sorts and draws, but `render()` (called while typing) doesn't sort, the sort is lost as soon as the user types. Put **all** the steps in `render()` and let the listeners only change the state.
:::

### Interview questions

:::qa -
Q: How does `sort` decide the order, and why does `[10, 9, 1].sort()` give `[1, 10, 9]`?
With no compare function, items are converted to strings and compared character by character, so `'10'` comes before `'9'`. Pass a compare function that returns negative, zero or positive, such as `(a, b) => a - b` for numbers.

Q: Does `sort` change the original array?
Yes, it sorts **in place** and also returns the same array. To keep the original, sort a copy: `[...arr].sort(...)`, `arr.slice().sort(...)`, or, in newer browsers, `arr.toSorted(...)`. `filter` and `map` always return new arrays.

Q: What does "state + render" mean, and why is it useful?
Keep everything the page depends on in a few variables (the **state**) and have one function that rebuilds the view from the state. Every event just updates the state and calls render. Bugs from forgetting to update one part of the page disappear, and this is exactly the idea behind React.

Q: How would you sort Z–A, or toggle the direction on a second click?
Swap the arguments: `b.name.localeCompare(a.name)`. To toggle, keep a `direction` variable (`1` or `-1`), flip it on a second click of the same button, and multiply: `(a, b) => direction * (a.age - b.age)`.
:::

### Practice twist

1. Make the column headers clickable for sorting, and remove the two buttons.
2. Make a second click on **Sort by age** sort oldest first (see the last interview answer).
3. Add a fourth column, **Senior**, that shows *Yes* for employees aged 50 or more.
