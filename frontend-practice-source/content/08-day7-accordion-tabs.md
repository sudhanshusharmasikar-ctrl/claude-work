:::chapter 7 | One Open at a Time: Accordion and Tabs | Exercise 13 Accordion · Exercise 14 Tab Switcher
- Selecting **many** elements with `querySelectorAll`, and searching **inside** an element
- The pattern behind accordions, tabs and carousels: **switch all off, then one on**
- Remembering the state **before** you change it
- **`data-*` attributes** and `dataset`: storing a name on an element
- Attribute selectors such as `.panel[data-panel="pricing"]`
:::

:::day Today's plan (2 hours)
**Exercise 13** (65 min): new ideas 20 · build 30 · grade and review 15. **Exercise 14** (55 min): new ideas 10 · build 30 · grade and review 15. The two exercises use the same pattern, so the second one should feel faster.
:::

## Exercise 13 · Accordion

### What you are building

![The accordion before and after](content/img/13.png){.shot}

A FAQ list. Every answer starts hidden. Clicking a question opens its answer and closes any other; clicking an open question closes it. The `+` becomes `-` while open. The grader checks:

| Test | What it does | Expects |
|---|---|---|
| all panels start closed | opens the page | every `.accordion-body` hidden |
| clicking a header opens its panel | clicks header 1 | body 1 visible; header 1 has `aria-expanded="true"` |
| opening one panel closes the others | clicks header 1, then header 2 | body 1 hidden, body 2 visible |
| clicking an open header closes it again | clicks header 2 twice | body 2 hidden |

### New ideas

#### 1. Selecting many elements

| Method | Returns |
|---|---|
| `document.getElementById('x')` | the one element with id `x` (or `null`) |
| `document.querySelector('.tab')` | the **first** element matching a **CSS selector** (or `null`) |
| `document.querySelectorAll('.tab')` | **all** matching elements, as a list (empty if none) |

The list from `querySelectorAll` (a **NodeList**) has `.length`, `[0]`, `[1]`… and `forEach`, which is all you need today.

#### 2. Searching inside one element

`querySelector` also works **on an element**, and then it only searches inside that element:

```js title="find the header of this item, not any header"
const header = item.querySelector('.accordion-header');
const icon = item.querySelector('.icon');
```

This is how you go from "one accordion item" to "its own header and its own icon".

#### 3. A listener for every item

`forEach` + `addEventListener` gives each item its own listener, and thanks to the **closure** from Day 5, each listener remembers its own `item` and `header`:

```js title="one listener per item"
items.forEach((item) => {
  const header = item.querySelector('.accordion-header');
  header.addEventListener('click', () => {
    // here, `item` is the item whose header was clicked
  });
});
```

#### 4. Switch all off, then one on

[[fig:fp-one-active|The pattern for "only one at a time". **1.** Remember whether the clicked item was open. **2.** Switch every item off. **3.** Switch the clicked one on (for the accordion: only if it wasn't open before, so a second click closes it).]]

You never have to work out *which* item is currently open. Turning **all** of them off is simpler and can't go wrong.

The order of steps 1 and 2 matters: if you closed everything first and then asked *"was this item open?"*, the answer would always be *no*. **Read the state before you change it.**

#### 5. Hiding with a class

CSS hides every body by default and shows a body only when its item has the class `open`:

```css title="state in a class, looks in CSS"
.accordion-body { display: none; }
.accordion-item.open .accordion-body { display: block; }
```

`display: none` removes the element from the page completely (as if it weren't there). The JavaScript only adds and removes `open`.

### Read the starter files

Each FAQ entry looks like this:

```html title="one item in index.html"
<div class="accordion-item">
  <button class="accordion-header" type="button" aria-expanded="false">
    What is HTML?
    <span class="icon">+</span>
  </button>
  <div class="accordion-body">
    <p>HTML is the standard markup language ...</p>
  </div>
</div>
```

`style.css` has two empty rules: `.accordion-body` and `.accordion-item.open .accordion-body`. `script.js` has only comments.

### The plan in plain English

1. CSS: hide `.accordion-body`; show it inside `.accordion-item.open`.
2. JS: select all `.accordion-item`s.
3. For each item, find its header and listen for clicks. On a click:
    1. Remember `wasOpen`: does this item have the class `open`?
    2. For **every** item: remove `open`, set its header's `aria-expanded` to `'false'`, set its icon to `+`.
    3. If it **wasn't** open: add `open` to this item, set its header's `aria-expanded` to `'true'`, its icon to `-`.

:::tip Hint 1
Get it working without the "click again to close" rule first: switch all off, then switch the clicked one on. Then add `wasOpen`.
:::

:::tip Hint 2
Inside the "all off" loop, use a different name for the loop variable (`other`), so you don't mix it up with the clicked `item`.
:::

:::note Stop here and build it
Then run `npm test -- 13-accordion`.
:::

### The solution, line by line

```css title="13/style.css"
.accordion-body {
  display: none;
}

.accordion-item.open .accordion-body {
  display: block;
}
```

```js title="13/script.js" lines
const items = document.querySelectorAll('.accordion-item');

items.forEach((item) => {
  const header = item.querySelector('.accordion-header');

  header.addEventListener('click', () => {
    const wasOpen = item.classList.contains('open');

    // 1. Close every item
    items.forEach((other) => {
      const otherHeader = other.querySelector('.accordion-header');
      other.classList.remove('open');
      otherHeader.setAttribute('aria-expanded', 'false');
      other.querySelector('.icon').textContent = '+';
    });

    // 2. Open the clicked one, unless it was already open
    if (!wasOpen) {
      item.classList.add('open');
      header.setAttribute('aria-expanded', 'true');
      item.querySelector('.icon').textContent = '-';
    }
  });
});
```

| Lines | What they do |
|---|---|
| 1 | All three items, in page order. |
| 3–4 | For each item, find **its** header once. |
| 6 | One listener per header. |
| 7 | Read the state **before** changing anything. |
| 10–15 | All off: class, ARIA and icon, for every item (the clicked one included). |
| 18–22 | One on, but only if it was closed. If it was open, step 1 already closed it, which is exactly the "click again to close" behaviour. |

### Mistakes beginners make

:::mistake Asking "was it open?" after closing everything
The answer is always *no*, so a second click re-opens the item instead of closing it, and the last test fails.
:::

:::mistake `document.querySelector('.icon')` inside the loop
`document.querySelector` searches the **whole page** and always returns the **first** icon, so only the first `+` ever changes. Search inside the item: `other.querySelector('.icon')`.
:::

### Interview questions

:::qa -
Q: What is the difference between `querySelector` and `querySelectorAll`?
`querySelector` returns the first element that matches a CSS selector (or `null`); `querySelectorAll` returns all matches as a NodeList, which you can loop over with `forEach`.

Q: What is the difference between `display: none` and `visibility: hidden`?
`display: none` removes the element from the layout: it takes no space. `visibility: hidden` makes it invisible but keeps its space.

Q: How would you let several panels be open at once?
Remove the "close every item" loop and just toggle the clicked one: `item.classList.toggle('open')`, then set `aria-expanded` and the icon from the result.
:::

### Practice twist

Animate the opening. Instead of `display`, use `max-height: 0; overflow: hidden; transition: max-height 0.3s;` on `.accordion-body`, and `max-height: 200px` when open. Note that the grader checks visibility, so it may fail with this version. That's fine for a twist; keep a copy of the passing version.

## Exercise 14 · Tab Switcher

### What you are building

![The tabs before and after](content/img/14.png){.shot}

Three tabs; clicking one underlines it and shows its panel. The grader checks that on load the first tab is `active` and only the *overview* panel is visible; that clicking *Features* shows its panel and hides *overview*; and that after clicking *Pricing*, that tab has `active` and `aria-selected="true"` while *Overview* has neither.

### New ideas

#### 1. `data-*` attributes

How does a tab know which panel is its own? The HTML **labels** both with the same word:

```html title="from index.html"
<button class="tab" data-tab="features" ...>Features</button>
...
<div class="panel" data-panel="features">...</div>
```

Any attribute starting with `data-` is yours to invent: it stores extra information on an element. JavaScript reads it through `dataset`, without the `data-` prefix:

```js title="reading a data attribute"
tab.dataset.tab        // 'features'   (from data-tab)
panel.dataset.panel    // 'features'   (from data-panel)
```

A name with a dash such as `data-panel-id` becomes **camelCase** in `dataset`: `dataset.panelId`.

#### 2. Attribute selectors

CSS (and so `querySelector`) can select by **attribute value**:

```js title="find the panel with a given name"
const panel = document.querySelector(`.panel[data-panel="${name}"]`);
```

With `name` equal to `'pricing'`, the selector becomes `.panel[data-panel="pricing"]`. The backticks build the selector text, exactly as they built messages on Day 2.

### Read the starter files

`index.html` is complete: three `.tab` buttons (the first already has `active` and `aria-selected="true"`) and three `.panel`s (the first is `active`). In `style.css`, four rules are empty: `.tab`, `.tab.active`, `.panel` and `.panel.active`. `script.js` has only comments.

### The plan in plain English

1. CSS: plain tabs (no border except a transparent bottom line, transparent background, pointer); the active tab coloured with a coloured bottom border; `.panel` hidden, `.panel.active` shown.
2. JS: select all tabs and all panels.
3. For each tab, on click:
    1. Read its name from `dataset.tab`.
    2. All off: remove `active` from every tab (and set `aria-selected="false"`) and from every panel.
    3. One on: add `active` to the clicked tab (`aria-selected="true"`) and to the panel whose `data-panel` equals the name.

:::tip Hint
This is the accordion's pattern without `wasOpen`: a tab can't be "closed" by clicking it again. Write it from memory before looking back.
:::

:::note Stop here and build it
Then run `npm test -- 14-tab-switcher`.
:::

### The solution, line by line

```css title="14/style.css"
.tab {
  padding: 10px 16px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: #64748b;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.tab.active {
  color: #7c3aed;
  border-bottom-color: #7c3aed;
}

.panel {
  display: none;
}

.panel.active {
  display: block;
}
```

Every tab gets a **transparent** 2px bottom border, and the active one only changes its colour. That way the text doesn't jump down by 2px when a tab becomes active.

```js title="14/script.js" lines
const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.panel');

tabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    const name = tab.dataset.tab;

    // 1. Switch every tab and every panel off
    tabs.forEach((t) => {
      t.classList.remove('active');
      t.setAttribute('aria-selected', 'false');
    });
    panels.forEach((panel) => {
      panel.classList.remove('active');
    });

    // 2. Switch on the clicked tab and the panel with the same name
    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');
    const panel = document.querySelector(`.panel[data-panel="${name}"]`);
    panel.classList.add('active');
  });
});
```

| Lines | What they do |
|---|---|
| 1–2 | All tabs and all panels. |
| 6 | Which panel do we want? Read the name stored on the tab. |
| 9–15 | All off. |
| 18–19 | The clicked tab on. |
| 20–21 | Find the panel with the same name and switch it on. |

:::deep Another way: `toggle` with a second argument
`classList.toggle('active', condition)` **adds** the class when the condition is `true` and **removes** it when `false`. The repository's `solution/` uses it to do "all off, one on" in a single loop:

```js title="exercises/14-tab-switcher/solution/script.js (part)"
tabs.forEach((t) => {
  const isActive = t === tab;
  t.classList.toggle('active', isActive);
  t.setAttribute('aria-selected', String(isActive));
});

panels.forEach((panel) => {
  panel.classList.toggle('active', panel.dataset.panel === name);
});
```
:::

### Mistakes beginners make

:::mistake `tab.dataset['data-tab']` or `tab.dataset.dataTab`
`dataset` drops the `data-` prefix: `data-tab` is `dataset.tab`.
:::

:::mistake Using the tab's index to find the panel
`panels[i]` works only while the tabs and panels are in the same order. The `data-*` names keep working even if someone reorders the HTML. That robustness is the point of the exercise.
:::

### Interview questions

:::qa -
Q: What are `data-*` attributes for?
Storing custom information on HTML elements, such as an id, a name or a state, which JavaScript reads through `element.dataset`. They're valid HTML and don't affect how the page looks.

Q: Why use classes to show and hide, instead of setting `style.display` in JavaScript?
It keeps the looks in CSS and the logic in JavaScript. One class can change many properties, and the CSS can change (for example to add an animation) without touching the script.

Q: What ARIA attributes does a tab component need?
`role="tablist"` on the container, `role="tab"` and `aria-selected` on each tab, and `role="tabpanel"` on each panel. The starter HTML has the first two; you keep `aria-selected` in sync.
:::

### Practice twist

Make the arrow keys work: when a tab has focus, **→** activates the next tab and **←** the previous one. Hint: listen for `keydown` on each tab; `event.key` is `'ArrowRight'` or `'ArrowLeft'`. Move the activation code into a function `activate(tab)` so the click and the key both call it.
