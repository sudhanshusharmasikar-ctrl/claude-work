:::chapter 3 | Tools and Function Calling: Your First AI Agent | Lectures 4–5 · Lecture04 + Lecture05 code · Must-know
- Why an LLM alone can't tell you the **bitcoin price**
- Why **keyword `if/else` routing** fails (Lecture 4)
- **Function calling**: the model *asks*, **your code runs**
- Writing a **function declaration** (name, description, parameters)
- The **agent loop** in Lecture 5, line by line
- What goes into **History**: `functionCall` and `functionResponse`
- Bugs to avoid: one call only, no step limit, keys in URLs
- An **improved agent** you can explain in interviews
- **Structured output** (JSON mode) — function calling's cousin
:::

In Chapter 1 the model couldn't even tell the date. Real products need **live data** (prices, weather, news, your database) and **actions** (send an email, create a file). This chapter gives the model **hands**.

## 3.1 The problem: the LLM has no live data %%MUST%%

Rohit's Lecture 4 whiteboard starts with three questions a user might type:

- *"Bitcoin ka price bata de"* → needs the **crypto price API**
- *"Delhi ka weather kaisa hai?"* → needs the **weather API**
- *"Bhai Delhi ki news bata"* → needs a **news API**

The LLM can't call these APIs — it only produces tokens. So who decides **which** API to call, and with **what** argument ("bitcoin", "delhi")?

## 3.2 First attempt: write the routing logic yourself (Lecture 4) %%MUST%%

```js title="Lecture04/app.js (the idea)" lines
import readlineSync from "readline-sync";

async function get_crypto_price(coin) {
  const response = await fetch(
    `https://api.coingecko.com/api/v3/coins/markets?vs_currency=inr&ids=${coin}`);
  const data = await response.json();
  console.log(data);
}

async function getWeather(city) { /* ... */ }
async function news(topic) { /* ... */ }

const question = readlineSync.question("Ask me about anything:-> ");
// question = "Bhai delhi ki news bata";
// Which function? With which argument? "delhi"? "news"? ...
```

The functions are easy. The hard part is the **routing**: turning *"Bhai delhi ki news bata"* into `news("delhi")`. You could try `if (question.includes("news"))` — but users write *"kya chal raha hai Delhi mein?"*, *"latest headlines"*, typos, Hinglish, two questions in one. Rohit's homework ("JavaScript: LLM use nahi karna") is to try it — and discover that keyword rules never cover real language.

> The one thing an LLM **is** great at is understanding messy language. So let the LLM do the **routing**, and let **our code** do the **work**.

## 3.3 Function calling: the model asks, your code runs %%MUST%%

**Function calling** (also called **tool calling**) works like this:

1. You send the question **plus a menu of tools** (name, what it does, what arguments it needs).
2. The model replies **either** with normal text **or** with a structured request: *"please call `cryptoCurrency` with `{ coin: "bitcoin" }`"*.
3. **Your code** runs that function — the model never executes anything.
4. You send the result back to the model.
5. The model uses the result to write the final answer (or asks for another tool).

[[fig:fc-sequence|One round of function calling. The model only ever produces a request; your program executes the tool and returns the result.]]

:::analogy The restaurant menu (Lecture 7 notes)
**Menu** = the tools you declare. **Customer** = the AI ("I'd like `list_files` with `directory = ./src`"). **Kitchen** = your code, which cooks each order safely and decides what actually happens. The customer can only order what is on the menu.
:::

:::cpp A name → function-pointer table
In C++ you might keep `std::unordered_map<std::string, std::function<json(json)>> tools;` and call `tools[name](args)`. That is exactly the `toolFunctions` object in the course code. The LLM just picks the **key** and fills the **arguments**.
:::

## 3.4 Describing a tool: the function declaration %%MUST%%

The model can only choose a tool well if the **description** is good. The declaration is a small JSON schema:

```js title="Lecture05/index.js — declaring the crypto tool" lines hl=2-4,10-11
const cryptoInfo = {
  name: "cryptoCurrency",
  description: "We can give you the current price or other information related "
             + "to cryptocurrency like bitcoin and ethereum etc",
  parameters: {
    type: Type.OBJECT,
    properties: {
      coin: {
        type: Type.STRING,
        description: "It will be the name of the cryptocurrency like bitcoin, "
                   + "ethereum, etc"
      }
    },
    required: ['coin']
  }
}
```

- **`name`** — must match the key in your `toolFunctions` table.
- **`description`** — the model reads this to decide **when** to use the tool. Vague description → wrong or missed tool calls. This is prompt engineering too!
- **`parameters`** — an OpenAPI-style schema: an object whose `properties` are the arguments, with types (`Type.STRING`, `Type.NUMBER`, `Type.BOOLEAN`, `Type.ARRAY`, `Type.OBJECT`) and their own descriptions.
- **`required`** — arguments the model must always fill.

## 3.5 The agent loop (Lecture 5 code, line by line) %%MUST%%

:::day Lecture05/index.js
A terminal assistant with two tools: crypto prices (CoinGecko) and weather (weatherapi.com). The original file has the weather API key typed inside the URL — I replaced it with `process.env.WEATHER_API_KEY`.
:::

```js title="Lecture05/index.js — tools and the tool table" lines
import { GoogleGenAI, Type } from '@google/genai';
import readlineSync from "readline-sync"
import 'dotenv/config'

const ai = new GoogleGenAI({});

async function cryptoCurrency({coin}) {
  const response = await fetch(
    `https://api.coingecko.com/api/v3/coins/markets?vs_currency=inr&ids=${coin}`);
  const data = await response.json();
  return data;
}

async function weatherInformation({city}) {
  const response = await fetch(`http://api.weatherapi.com/v1/current.json`
    + `?key=${process.env.WEATHER_API_KEY}&q=${city}&aqi=no`);
  const data = await response.json();
  return data;
}

// cryptoInfo (above) and weatherInfo are the two declarations
const tools = [{
  functionDeclarations: [cryptoInfo, weatherInfo]
}];

const toolFunctions = {
  "cryptoCurrency": cryptoCurrency,
  "weatherInformation": weatherInformation
}

const History = [];
```

- **Line 1** — `Type` is an enum of schema types used in declarations.
- **Lines 7 and 14** — each tool takes **one object** and destructures it (`{coin}`, `{city}`). The model's `args` will be exactly such an object, e.g. `{ coin: "bitcoin" }`.
- **Line 15** — `http://` sends your API key **unencrypted** over the network. Use `https://` (weatherapi.com supports it).
- **Lines 22–24** — `tools` is an **array** of tool groups; `functionDeclarations` is the menu.
- **Lines 26–29** — the **dispatch table**: name → real function. The commented-out code in the original file shows the `if (name == "cryptoCurrency") … else if …` version; the table replaces that `if/else` chain.
- **Line 31** — one shared conversation history, exactly like Chapter 1.

```js title="Lecture05/index.js — the agent loop" lines start=33
async function runAgent() {
  while (true) {
    const result = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: History,
      config: { tools },
    });

    if (result.functionCalls && result.functionCalls.length > 0) {
      console.log("My function is called");
      const functionCall = result.functionCalls[0];
      const {name, args} = functionCall;

      const response = await toolFunctions[name](args);

      const functionResponsePart = {
        name: functionCall.name,
        response: { result: response },
      };

      History.push({ role: "model", parts: [{ functionCall: functionCall }] });
      History.push({ role: 'user',
                     parts: [{ functionResponse: functionResponsePart }] });
    }
    else {
      History.push({ role: 'model', parts: [{ text: result.text }] });
      console.log(result.text);
      break;
    }
  }
}

while (true) {
  const question = readlineSync.question('Ask me anything: ');
  if (question == 'exit') break;
  History.push({ role: 'user', parts: [{ text: question }] });
  await runAgent();
}
```

- **Lines 35–39** — send the **whole history** and the **tool menu**.
- **Line 41** — did the model ask for a tool? `result.functionCalls` is a helper that collects all `functionCall` parts of the answer.
- **Lines 43–44** — take the **first** call and destructure its `name` and `args`.
- **Line 46** — **our code runs the tool**: `toolFunctions["cryptoCurrency"]({ coin: "bitcoin" })`.
- **Lines 48–51** — wrap the result in the shape Gemini expects: `{ name, response: { result } }`.
- **Line 53** — record the model's request in history (role `model`, part `functionCall`).
- **Lines 54–55** — record the tool's answer (role `user`, part `functionResponse`). Now the model will "see" the price on the next loop.
- **Line 56 → back to line 35** — `while (true)` asks the model again. It may call another tool, or answer.
- **Lines 57–61** — no tool call means the model has written the **final answer**: save it, print it, `break`.
- **Lines 65–70** — the outer chat loop: read a question, add it to history, run the agent.

Trace for *"What is the bitcoin price, and how is the weather in Goa?"*:

| Loop | Model returns | Our code does |
|---|---|---|
| 1 | `functionCall: cryptoCurrency({coin:"bitcoin"})` (maybe also a weather call) | runs the **first** call, pushes call + result |
| 2 | `functionCall: weatherInformation({city:"Goa"})` | runs it, pushes call + result |
| 3 | text: "Bitcoin is ₹… and Goa is 29 °C, sunny." | prints it, `break` |

> This **loop** — *think → call tool → observe result → think again* — is what turns an LLM into an **agent**. The model decides the next step; the code gives it hands.

## 3.6 What can go wrong (and how interviewers test you) %%MUST%%

The course code is a teaching version. Five things break in real use:

1. **Only `functionCalls[0]` is handled.** Gemini can return **several calls at once** (parallel function calling) — "bitcoin price **and** Goa weather". The other calls are silently dropped (the model usually asks again, costing an extra round). Lecture 7 fixes this by looping over all calls.
2. **No step limit.** `while (true)` + a confused model = an infinite, expensive loop. Always cap the steps.
3. **No error handling.** If the API is down or the coin name is wrong, `fetch`/`json()` throws and the whole program crashes. Better: catch the error and send it back as the tool result, so the model can apologise or try another argument.
4. **Model text goes straight into a URL.** `ids=${coin}` — if the model (or a tricky user) produces `bitcoin&vs_currency=usd`, it changes your request. Use `encodeURIComponent` and validate arguments like any user input.
5. **The key is in the code.** Lecture 5's original URL contains the weather API key in plain text. Keys belong in `.env`.

:::security Tool arguments are untrusted input
The model writes the arguments, and the model is influenced by whatever text reaches it — including text from web pages, files and tool results (**indirect prompt injection**, Chapter 5). Validate every argument (type, allowed values, length), and give tools the **least power** they need. A "get weather" tool is harmless; a "run any shell command" tool (next chapter) is not.
:::

## 3.7 An improved agent loop (our version) %%GOOD%%

This is the Lecture 5 loop with the five fixes. The tool declarations stay the same. I tested this loop against the current `@google/genai` SDK with a scripted fake model that returns **two** tool calls at once; both tools ran and the final history was `user → model(2 calls) → user(2 results) → model(text)`.

```js title="improved runAgent — handles every call, errors and a step limit" lines
const MAX_STEPS = 8;                             // stop runaway loops

async function runAgent(history) {
  for (let step = 1; step <= MAX_STEPS; step++) {
    const result = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: history,
      config: { tools },
    });

    const calls = result.functionCalls ?? [];
    history.push(result.candidates[0].content);  // the model's turn, unchanged

    if (calls.length === 0) return result.text;   // no tool → final answer

    const responses = [];
    for (const { name, args } of calls) {         // EVERY call, not only [0]
      let output;
      try {
        if (!toolFunctions[name]) throw new Error(`Unknown tool: ${name}`);
        output = await toolFunctions[name](args);
      } catch (err) {
        output = { error: err.message };          // the model sees the failure
      }
      responses.push({ functionResponse: { name, response: { result: output } } });
    }
    history.push({ role: "user", parts: responses });
  }
  return "Sorry, I could not finish within the step limit.";
}
```

- **Line 12** — instead of rebuilding `{ functionCall }` by hand, push the model's **own** content object. Newer thinking models attach hidden **thought signatures** to their turns; rebuilding the object can drop them, and some models then reject the next request.
- **Lines 17–27** — all calls are executed; all results go back in **one** `user` message, in the same order.
- **Line 23** — a failure becomes data for the model instead of a crash.
- **Line 29** — a clear stop instead of burning money forever.

(And inside the tools: `encodeURIComponent(coin)`, `https://` with `process.env.WEATHER_API_KEY`, and `if (!res.ok) throw …`.)

## 3.8 How does the model "choose"? And how many tools? %%GOOD%%

The model was **fine-tuned** on many examples of "user question + tool menu → correct tool call". At run time it reads your tool **names and descriptions** and predicts the tokens of a function call, just like any other tokens. That's why:

- **Descriptions are prompts.** Say what the tool does, when to use it, and give argument examples.
- **Fewer, clearer tools work better.** Rohit's whiteboard mentions "1000 tools" — with that many, the model gets confused and every call pays for a huge menu. Real systems **select** the relevant tools first (by category, or by embedding search over tool descriptions) and show only those.
- You can force behaviour with a **function-calling mode**: `AUTO` (model decides), `ANY` (must call some tool), `NONE` (never call tools).

## 3.9 Cousin feature: structured output (JSON mode) %%GOOD%%

Sometimes you don't want a tool call — you just want the answer **as JSON** your code can parse. Gemini supports this directly:

```js title="asking for JSON output"
const result = await ai.models.generateContent({
  model: "gemini-2.5-flash",
  contents: "Extract the movie, year and director: 'Inception (2010) by Nolan'",
  config: {
    responseMimeType: "application/json",
    responseSchema: {
      type: Type.OBJECT,
      properties: {
        title: { type: Type.STRING },
        year: { type: Type.NUMBER },
        director: { type: Type.STRING },
      },
      required: ["title", "year", "director"],
    },
  },
});
const movie = JSON.parse(result.text);   // { title: "Inception", year: 2010, ... }
```

The multi-agent project (Chapter 16) uses `responseMimeType: "application/json"` for every agent, and the Graph RAG project (Chapter 12) asks for JSON plans. **Still wrap `JSON.parse` in `try/catch`** and validate the fields — a schema makes bad output rare, not impossible.

| | Function calling | Structured output |
|---|---|---|
| Purpose | Let the model **request an action/data** | Get the model's **answer** in a fixed shape |
| Who acts next | Your code runs the tool, then the model continues | Your code uses the JSON directly |
| Example | "get the weather for Goa" | "extract title/year/director as JSON" |

:::remember
- The LLM **never runs code**. It returns `functionCall { name, args }`; **your program** executes it and returns a `functionResponse`.
- A tool = **declaration** (name + description + JSON-schema parameters) + **implementation** (a real function).
- History after a tool round: `user(question) → model(functionCall) → user(functionResponse) → model(answer)`.
- **Agent = LLM + tools + loop.** The loop ends when the model answers with text.
- Real agents need: **all** parallel calls handled, a **step limit**, **try/catch** around tools, **validated arguments**, keys in **`.env`**.
- Good **descriptions** decide good tool choice. Too many tools → select a relevant subset.
- JSON mode (`responseMimeType` + `responseSchema`) gives parseable answers; still validate.
:::

:::quiz
1. In Lecture 5, which line actually fetches the bitcoin price — the model's or ours?
2. Why is the tool result pushed with `role: 'user'`?
3. The user asks for two coins at once and the model returns two function calls. What does Lecture 5 do? What should it do?
4. Name three risks of `while (true)` in an agent.
5. When would you use JSON mode instead of function calling?
:::

:::answer
1. Ours — `await toolFunctions[name](args)` runs `cryptoCurrency`, which calls `fetch`.
2. Gemini's conversation alternates `user` and `model` turns; function results are sent back to the model as input, which is the `user` side.
3. It runs only `functionCalls[0]` and drops the second. It should run every call and send all results back together.
4. Infinite loops, unbounded cost (every step re-sends the history), and no way to stop a confused model (plus no timeout).
5. When you just need the model's answer in a fixed shape (extraction, classification, a plan), and no external action is needed.
:::

:::qa Interview questions — function calling
Q: What is function calling in LLMs? Does the model execute the function?
It lets the model respond with a structured request — a function name and JSON arguments — chosen from tools I declared. The model never executes anything; my code runs the function, sends the result back as a function response, and the model continues. That separation is what keeps control and security on my side.

Q: How does the model decide which tool to call?
It was trained on examples of tool use and, at run time, reads the tool names, descriptions and parameter schemas in the request. It predicts a function-call just like other tokens. So clear descriptions and a small, relevant tool set improve accuracy.

Q: Walk me through an agent loop.
Send history + tools → if the response has function calls, run each one, append the model's call and my results to the history, and call the model again → when it replies with plain text, that's the final answer. I add a max-step limit, error handling per tool, and logging of each step.

Q: How do you handle a tool that fails?
Catch the error and return it as the tool result (e.g. `{ error: "API returned 503" }`) so the model can retry with other arguments or explain the problem. Also add timeouts and retries with backoff for flaky APIs, and a step limit so errors can't loop forever.

Q: What is parallel function calling?
The model can return several independent calls in one turn (e.g. price of bitcoin and weather in Goa). Run them (possibly concurrently with `Promise.all`), then return all results together in one message, in the same order.

Q: What are the security risks of giving an LLM tools?
Arguments are model-generated, so they're untrusted: injection into URLs, SQL or shell commands; excessive permissions (a tool that can delete files); and indirect prompt injection where a web page or document tells the model to misuse a tool. Mitigations: validate arguments, least-privilege tools, allowlists, human approval for dangerous actions, sandboxing, and never exposing secrets to the model.

Q: Function calling vs structured output — what's the difference?
Function calling asks the model to request an action that my code performs, after which the model continues the conversation. Structured output constrains the model's own answer to a JSON schema so my code can parse it directly. Both use schemas; I use function calling for actions and live data, structured output for extraction and plans.
:::
