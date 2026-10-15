:::chapter 3 | CSS Day: Boxes, Rows and Centering | Exercise 02 Profile Card · Exercise 04 Center It
- The **box model**: content, padding, border, margin
- Units and colours: `px`, `rem`, `%`, `#hex`, `rgba()`
- Rounded corners, shadows and text styles
- **Flexbox**: putting things in a row and lining them up
- Three ways to **center** anything: flexbox, grid and absolute positioning
:::

:::day Today's plan (2 hours)
Both exercises are **CSS only**: you don't touch the HTML or JavaScript. **Exercise 02** (70 min) · **Exercise 04** (50 min). Keep the browser open next to the editor and refresh after every few lines: CSS is learned by watching it change.
:::

## Exercise 02 · Style the Profile Card

### What you are building

![The profile card before and after](content/img/02.png){.shot}

The HTML is complete but unstyled. You write seven CSS rules. The grader measures the result with `getComputedStyle`, the browser's final answer for each property:

| Test | What it checks |
|---|---|
| card has rounded corners, padding and a shadow | `.profile-card`: radius ≥ 12px, padding ≥ 16px, a `box-shadow`, a background colour |
| avatar is a circle | `.avatar`: width ≥ 64px, width = height, radius at least half the width |
| name is bold and role is muted | `.name` weight ≥ 600; `.role` colour differs from the normal text colour |
| tags render as styled chips in a row | `.tags`: no bullets, `display: flex`; `.tag`: padding, background, rounded corners |
| follow button looks clickable | `.follow-btn`: `cursor: pointer`, a background, **white** text, padding |

### New ideas

#### 1. The box model

Every element is a rectangle made of four layers:

[[fig:fp-box-model|From the inside out: the **content**, the **padding** (space inside the border, which shows the background colour), the **border**, and the **margin** (space outside, always transparent, that pushes other elements away).]]

```css title="the four layers in CSS"
.card {
  width: 320px;           /* content width                         */
  padding: 24px;          /* inside space, on all four sides       */
  border: 1px solid #ddd; /* thickness, style, colour              */
  margin: 0 auto 12px;    /* top 0, left & right auto, bottom 12px */
}
```

Every starter file begins with `* { box-sizing: border-box; }`. It makes `width` include the padding and border, so a `320px` card is really 320px wide. Without it, padding is **added** to the width, which surprises everyone.

**Shorthand with several values** goes clockwise from the top: `margin: 4px 0 12px` means top 4, left and right 0, bottom 12. One value means all four sides; two values mean *top-and-bottom* then *left-and-right*.

#### 2. Units and colours

| Unit | Means | Use it for |
|---|---|---|
| `px` | screen pixels | borders, small fixed sizes, shadows |
| `rem` | times the page's base font size (usually 16px): `1.5rem` = 24px | font sizes |
| `%` | percent of something else: `border-radius: 50%` = half of the element's size | circles, widths |

Colours: `#7c3aed` (red, green, blue in hex), `white`, or `rgba(0, 0, 0, 0.12)`, which is black at 12% opacity, perfect for soft shadows.

#### 3. Corners, shadows and text

| Property | Example | Effect |
|---|---|---|
| `border-radius` | `16px` · `50%` · `999px` | rounded corners · a circle (if width = height) · a pill |
| `box-shadow` | `0 10px 30px rgba(0,0,0,0.12)` | x offset, y offset, blur, colour: a soft shadow below |
| `font-size` | `1.4rem` | text size |
| `font-weight` | `400` normal · `600` semi-bold · `700` bold | thickness |
| `color` | `#64748b` | **text** colour (`background` is the fill) |
| `text-align` | `center` | lines up the text inside the box |

#### 4. Flexbox: a row of items

`display: flex` on a parent lines up its **children** in a row:

```css title="the four flexbox properties you need"
.tags {
  display: flex;            /* children side by side            */
  gap: 8px;                 /* space between them               */
  justify-content: center;  /* along the row: start | center | space-between */
  align-items: center;      /* across the row: vertical alignment */
}
```

A `<ul>` has bullets and a left padding by default: remove them with `list-style: none` and `padding: 0`.

Flexbox also centers **one** child: on `.avatar`, `display: flex` + `align-items: center` + `justify-content: center` puts the letters "AL" in the middle of the circle.

#### 5. Centering a block horizontally

A block with a fixed width is centered by `margin: 0 auto`. The browser shares the leftover space equally between the left and right margins.

### Read the starter files

The HTML is an `<article class="profile-card">` with these children, in order: `.avatar` ("AL"), `h1.name`, `p.role`, `p.bio`, `ul.tags` with three `li.tag`, and `button.follow-btn`. The CSS file has **seven empty rules** with a `TODO` above each. Fill them in; don't change the HTML.

### The plan in plain English

Go rule by rule, refreshing the browser after each:

1. **Card:** a width (and `max-width: 100%` for small screens), white background, radius 16px, padding 24px, a soft shadow, centered text.
2. **Avatar:** 72 × 72, `border-radius: 50%`, purple background, white bold text, flexbox to center the letters, `margin: 0 auto 12px` to center the circle itself.
3. **Name:** bigger and bold.
4. **Role:** a grey colour.
5. **Tags:** remove bullets and padding, make it a centered flex row with a gap. **Tag:** small padding, light purple background, pill corners, smaller text.
6. **Button:** padding, no border, rounded, purple background, white text, `font: inherit`, `cursor: pointer`.

:::tip Hint 1
If the avatar is an oval, its width and height differ. If it's a rounded square, the radius is less than 50%.
:::

:::tip Hint 2
The tags still show dots? You set `list-style` on `.tag` instead of `.tags`. The bullets belong to the list, the `<ul>`.
:::

:::tip Hint 3
The grader wants the button text **exactly white**: `color: #ffffff` (or `#fff`, or `white`) all become `rgb(255, 255, 255)`.
:::

:::note Stop here and build it
Then run `npm test -- 02-style-the-profile-card`.
:::

### The solution

```css title="02/style.css"
.profile-card {
  width: 320px;
  max-width: 100%;
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  text-align: center;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #7c3aed;
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.name {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
}

.role {
  color: #64748b;
  margin: 4px 0 12px;
}

.tags {
  list-style: none;
  padding: 0;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.tag {
  padding: 4px 12px;
  background: #ede9fe;
  color: #5b21b6;
  border-radius: 999px;
  font-size: 0.8rem;
}

.follow-btn {
  padding: 10px 28px;
  border: none;
  border-radius: 8px;
  background: #7c3aed;
  color: #ffffff;
  font: inherit;
  cursor: pointer;
}
```

A few choices explained:

- **`max-width: 100%`** lets the 320px card shrink on a phone narrower than 320px.
- **`.avatar` uses flexbox twice over:** its own `display: flex` centers the letters inside it, while `margin: 0 auto` centers the circle inside the card. (`text-align: center` on the card centers **text**, not a block with its own width.)
- **`margin: 0` on `.name`** removes the large default margin every `<h1>` has.
- **`border-radius: 999px`** is a trick for a pill shape: any radius bigger than half the height gives perfectly round ends.
- **`font: inherit`** on the button makes it use the page font, as you saw on Day 2.

### Mistakes beginners make

:::mistake `color` when you meant `background`
`color` is the **text** colour. A purple button needs `background: #7c3aed` **and** `color: #ffffff`.
:::

:::mistake Forgetting the semicolon
```css title="one missing ; breaks the next line too"
.name {
  font-size: 1.4rem
  font-weight: 700;
}
```
The browser reads `1.4rem font-weight: 700` as one broken value and ignores **both** lines. If a property "does nothing", check the line above it.
:::

### Interview questions

:::qa -
Q: Explain the CSS box model.
Every element is a box: content, then padding, then border, then margin. Padding is inside the border and shows the background; margin is outside and transparent. `box-sizing: border-box` makes `width` include padding and border, which is easier to reason about.

Q: What is the difference between `rem` and `px`?
`px` is a fixed size. `rem` is relative to the root font size (16px by default), so text in `rem` grows when a user increases their browser's font size. That's better for accessibility.

Q: How do you make a circle in CSS?
Equal width and height plus `border-radius: 50%`.
:::

### Practice twist

Add a `.follow-btn:hover` rule with a darker purple, and a `transition: background 0.2s;` on `.follow-btn` so the colour fades instead of jumping. Then give the card a hover effect: `transform: translateY(-4px)`.

## Exercise 04 · Center It

### What you are building

![The three stages before and after](content/img/04.png){.shot}

Three grey boxes (`.stage`), each with a purple dot. Center each dot **horizontally and vertically**, using a different technique each time. *"How do you center a div?"* is one of the most asked CSS interview questions, and after today you'll have three answers. The grader checks that `#stage-flex` uses `display: flex`, `#stage-grid` uses `display: grid`, the third dot has `position: absolute`, and in all three the dot's center is within 2 pixels of the box's center.

### New ideas

[[fig:fp-center-three|Three ways to center. **Flexbox:** one property per direction. **Grid:** one property for both. **Absolute:** move the dot's top-left corner to the middle, then pull it back by half its own size.]]

#### 1. Flexbox has two axes

In a flex row, `justify-content` works **along** the row (left ↔ right) and `align-items` works **across** it (top ↕ bottom). Center on both and the child sits in the middle:

```css title="centering with flexbox"
.box {
  display: flex;
  justify-content: center;  /* horizontal */
  align-items: center;      /* vertical   */
}
```

#### 2. Grid centers in one line

`display: grid` turns the box into a grid; with one child, it's a single cell. `place-items: center` centers the child in both directions at once.

#### 3. Positioning

| `position` | What it does |
|---|---|
| `static` | the default: the element sits in the normal flow |
| `relative` | stays in place, but becomes the **reference box** for absolute children |
| `absolute` | taken out of the flow and placed with `top` / `left` / `right` / `bottom`, measured from the nearest **positioned** ancestor (`relative`, `absolute` or `fixed`) |

`top: 50%; left: 50%` moves the dot's **top-left corner** to the middle of the stage, so the dot hangs down and to the right. `transform: translate(-50%, -50%)` then moves it up and left by **half of its own** width and height. In `translate`, percentages refer to the element **itself**, not its parent: that is the whole trick.

### Read the starter files

`.stage` already has `position: relative` (so it's the reference box), a fixed size, and a grey background. `.dot` is a 56px purple circle. Three rules are empty: `#stage-flex`, `#stage-grid`, and `#stage-abs .dot`. Notice the third one targets the **dot**, while the other two target the **stage**.

### The plan in plain English

1. `#stage-flex`: make it a flex container and center on both axes.
2. `#stage-grid`: make it a grid and use `place-items`.
3. `#stage-abs .dot`: position the dot absolutely at 50% / 50%, then translate it back by −50% / −50%.

:::tip Hint
For flexbox and grid, the rule goes on the **parent** (the stage): a parent controls where its children sit. For the absolute method, the rule goes on the **child** (the dot): the child places itself.
:::

:::note Stop here and build it
Then run `npm test -- 04-center-it`.
:::

### The solution

```css title="04/style.css"
#stage-flex {
  display: flex;
  justify-content: center;
  align-items: center;
}

#stage-grid {
  display: grid;
  place-items: center;
}

#stage-abs .dot {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
```

Which should you use in real work? **Flexbox or grid**, because they keep the element in the normal flow. The absolute method is useful for something that must sit **on top** of other content, such as a badge on a card or a loading spinner over a page.

### Mistakes beginners make

:::mistake `align-items` without `display: flex`
`justify-content` and `align-items` do nothing unless the same element has `display: flex` (or `grid`). They are instructions **for a flex container**.
:::

:::mistake Absolute without a positioned parent
If no ancestor has `position: relative`, an absolute element is placed relative to the **whole page**: the dot flies to the middle of the screen. Here `.stage` already has `position: relative`, but in your own projects you must add it.
:::

### Interview questions

:::qa -
Q: How do you center a div horizontally and vertically?
On the parent, `display: flex; justify-content: center; align-items: center;`, or `display: grid; place-items: center;`. Without flex or grid: `position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);` with a positioned parent.

Q: What is the difference between `position: relative` and `absolute`?
`relative` keeps the element in the normal flow (you can nudge it with `top` / `left`) and makes it the reference for absolute children. `absolute` removes the element from the flow and places it relative to the nearest positioned ancestor.

Q: When would you use grid instead of flexbox?
Flexbox lays things out in **one** direction (a row or a column); grid lays them out in **two** (rows and columns at once). Navbars and button groups suit flexbox; card galleries and page layouts suit grid.
:::

### Practice twist

Add a fourth stage to the HTML, `<section class="stage" id="stage-margin">`, and center its dot with **flexbox on the stage plus `margin: auto` on the dot**, without `justify-content` or `align-items`. (Inside a flex container, `margin: auto` soaks up the free space on every side.)
