:::chapter 1 | How LLMs Really Work | Lectures 1–3 · Lecture02 & Lecture03 code · Must-know
- What an LLM **really** does: predict the **next token**
- What a **token** is, and why "strawberry" is hard
- **Temperature**: how the next token is chosen
- **"Thinking"** = more tokens before the answer
- Your **first Gemini API call**, line by line
- Why the model has **no memory**, and how **history** fixes it
- **Chat sessions** and **system instructions**
- **Tokens = money**, the **context window**, common API errors
:::

Everything in this book — RAG, agents, LangGraph — is built on top of one simple machine. If you understand this chapter properly, the rest becomes "just engineering". Rohit starts the course with first principles, so we do too.

## 1.1 The one-sentence truth: an LLM predicts the next token %%MUST%%

A **Large Language Model (LLM)** — Gemini, GPT, Claude, Llama — does **one** thing:

> Given some text, it predicts **which token is most likely to come next**.

That's it. Every answer, every poem, every piece of code is made by repeating this one step again and again.

[[fig:next-token|Text generation is a loop: read all tokens so far → get a probability for every possible next token → pick one → append it → repeat until an end token.]]

If you type *"The capital of France is"*, the model gives a probability to every token it knows. `" Paris"` gets a very high probability, so it is picked and **appended**. Now the input is *"The capital of France is Paris"* and the model predicts again (maybe `"."`), and so on, until it predicts a special **end** token. This one-token-at-a-time style is called **autoregressive generation**.

Where do those probabilities come from? During **training**, the model read a huge amount of text and adjusted billions of numbers (its **weights**) so that its predictions matched the real next words in that text. Chapter 2 shows how a tiny version of this training works in C++.

:::analogy Your phone keyboard, but huge
When you type "I am going to", your phone suggests "the", "be", "school". That is next-word prediction trained on your messages. An LLM is the same idea, trained on a large part of the internet, books and code, with billions of weights instead of a small table.
:::

:::cpp The model as a C++ function
Think of the model as a **pure function**: `vector<float> nextTokenProbs(const vector<int>& tokens);` — token ids in, one probability per vocabulary entry out. Generation is just a `while` loop that calls it, picks a token, and `push_back`s it. No variables inside the function survive between calls — keep this in mind for Section 1.6.
:::

:::mistake "The model understands and reasons like a person"
Rohit's notes say it bluntly: *LLMs don't think, reason or understand — they predict the next token.* Researchers still argue about how much "understanding" is inside, but for engineering, the safe mental model is: **the output is the most plausible continuation, not a checked fact.** That is exactly why LLMs **hallucinate** — they produce fluent, confident text that is wrong, because "plausible" and "true" are different things.
:::

## 1.2 Tokens: the pieces the model reads %%MUST%%

A **token** is a small piece of text: a whole word, part of a word, a space plus a word, a digit, or a symbol. The model never sees letters — it sees token **ids** (integers).

| Text | Possible tokens |
|---|---|
| `Hello world` | `Hello` · ` world` (2 tokens) |
| `JavaScript` | `Java` · `Script`, or one token |
| `strawberry` | `straw` · `berry`, or one token |
| `unbelievable` | `un` · `believ` · `able` |

Rule of thumb for English: **1 token ≈ 4 characters ≈ ¾ of a word**. Hindi or Hinglish usually needs **more** tokens for the same meaning, so it costs more.

Tokens matter for three practical reasons:

1. **Money** — APIs bill you per token (input tokens + output tokens).
2. **Limits** — the **context window** (Section 1.10) is measured in tokens.
3. **Weird failures** — "How many r's are in strawberry?" is hard because the model sees `straw` + `berry`, not `s-t-r-a-w-b-e-r-r-y`. It has to *remember* the spelling instead of reading it.

## 1.3 How the next token is chosen: temperature %%MUST%%

The model gives probabilities; **your settings decide how to pick**.

- **Temperature 0** → almost always take the most likely token. Output is focused and repeatable. Use it for **code, SQL, JSON, extraction, RAG answers**.
- **Higher temperature (e.g. 0.8–1.0)** → less likely tokens get a real chance. Output is more varied and "creative". Use it for **stories, brainstorming, marketing text**.
- **top-p / top-k** → only sample from the best few candidates (top-k) or from the smallest group whose probabilities add up to *p* (top-p). They cut off the silly long tail.

In the course code you will see `temperature: 0.3` for the RAG chatbot (Chapter 8) and `temperature: 0` for Graph RAG planning (Chapter 12) — both are "be precise" jobs.

:::deep Temperature 0 is not a 100% guarantee
Even at temperature 0, the same prompt can occasionally give a slightly different answer (tiny floating-point differences on shared GPU servers can flip a near-tie). That is one reason production systems **validate** model output (parse the JSON, check the SQL) instead of trusting that it will always be identical. Your SchemaMind project does exactly this (Chapter 18).
:::

## 1.4 "Thinking" is just more tokens (Lecture 2) %%MUST%%

Newer models are sold as "thinking" or "reasoning" models. Rohit's first-principles explanation:

> The model generates **extra tokens that look like working-out** before it gives the final answer.

Take *"What is 547 + 832?"*

- **Without thinking**, the model must jump straight to the answer token. Suppose `1379` gets 60% and `1478` gets 30% — a real chance of a wrong answer.
- **With thinking**, it first writes (hidden from you) *"7 + 2 = 9 … 40 + 30 = 70 … 500 + 800 = 1300 … total 1379"*. Now, with those tokens in the input, `1379` becomes far more likely (say 95%).

The model did not "switch on a calculator". It produced tokens that **changed the input**, and that made the right answer more probable. Same for counting letters: spelling out `s-t-r-a-w-b-e-r-r-y` first helps, but it can still fail on unusual inputs like `rrrrrr`, because it is still predicting, not executing a loop.

| Use thinking for ✅ | Don't waste thinking on ❌ |
|---|---|
| Multi-step maths and logic | Simple facts ("capital of France?") |
| Debugging code, tracing execution | Simple definitions ("what is a variable?") |
| Planning with constraints (budget, time) | Creative writing (no better with thinking) |
| Explaining a concept step by step | Formatting or translating short text |

With Gemini 2.5 you control this with a **thinking budget** — the maximum number of thinking tokens:

```js title="Lecture 2 notes — controlling thinking" hl=6
const response = await ai.models.generateContent({
  model: "gemini-2.5-flash",
  contents: "What is 547 + 832?",
  config: {
    // 0 = answer directly; 500 or 1000 = allow that much thinking
    thinkingConfig: { thinkingBudget: 0 },
  },
});
```

:::remember Thinking costs real money
Thinking tokens are **billed like output tokens**, and they make the answer slower. A good system decides per question: Rohit's "learning assistant" example turns thinking on only when the message is long or contains words like *why*, *explain* or *debug*. (Details differ by model: on 2.5 Flash `0` switches thinking off and `-1` lets the model decide; newer Gemini 3 models use a `thinkingLevel` setting instead of a number. Check the docs for the model you use.)
:::

## 1.5 Your first API call (Lecture 2 code) %%MUST%%

:::day Lecture02/index.js
The course's first program. The API key string in the real file is empty; I show the safe version that reads the key from the environment. The commented-out conversation in the original file is used in Section 1.6.
:::

```js title="Lecture02/index.js (key removed, comments trimmed)" lines
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});    // reads GEMINI_API_KEY from the env

async function main() {
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: [
      {
        role: "user",
        parts: [{ text: "What is current date" }]
      }
    ]
  });
  console.log(response.text);
}

await main();
```

Line by line:

- **Line 1** — imports the official Google Gen AI SDK (`npm install @google/genai`). Because `package.json` has `"type": "module"`, we can use `import` and top-level `await`.
- **Line 3** — creates the client object `ai`. With `{}` the SDK looks for `GEMINI_API_KEY` in the environment (Lecture 3 loads it from `.env` with `import 'dotenv/config'`).
- **Line 5** — `async function`, because the network call takes time and returns a Promise (you learned this in the JavaScript PDF).
- **Line 6** — `ai.models.generateContent({...})` sends **one request** to Gemini and waits for the full answer.
- **Line 7** — which model to use. Flash = fast and cheap; Pro = stronger and slower.
- **Lines 8–13** — `contents` is an **array of messages**. Each message has a `role` (`"user"` or `"model"`) and `parts`. `parts` is an array because one message can mix text, images, PDFs, and later function calls and function results (Chapter 3).
- **Line 15** — `response.text` is a helper that joins all the text parts of the answer.
- **Line 18** — top-level `await` runs `main()`.

:::mistake "What is current date" — the model cannot know!
Run it and Gemini will either admit it doesn't know or confidently guess a wrong date. The model has **no clock** and its knowledge stops at its **training cutoff**. It can't check live prices, today's weather or your database either. This limitation is the reason for **tools** (Chapter 3) and **RAG** (Chapter 8).
:::

## 1.6 The model has no memory %%MUST%%

Rohit's commented-out experiment in the same file:

```js title="Lecture02/index.js — the commented-out 'memory' experiment"
contents: [
  { role: 'user',  parts: [{ text: "What is my name" }] },
  { role: 'model',
    parts: [{ text: "As an AI, I don't have access to personal information" }] },
  { role: 'user',  parts: [{ text: "My name is Rohit Negi" }] },
  { role: 'model', parts: [{ text: "Thank you, Rohit. It's nice to meet you!" }] },
  { role: 'user',  parts: [{ text: "What is my name" }] },
]
```

If you send only the last message, the model says it doesn't know your name. If you send **all five** messages, it answers "Rohit Negi". Why?

> **Every API call is independent. The model keeps NO memory between calls.** The only "memory" is the conversation **you send again** inside `contents`.

[[fig:stateless|The API is stateless. "Memory" is an illusion created by your code sending the whole conversation every time.]]

:::cpp Like calling a function with no static variables
In C++, a function that has no `static` locals and no globals behaves the same every time you call it; if you want it to "know" earlier values, **you pass them as arguments**. The LLM API is exactly that: the history is just an argument. It is also like HTTP: every request carries everything the server needs.
:::

Two consequences you must remember:

1. **Cost grows** — every new message re-sends the whole history (Section 1.9).
2. **Limits** — very long chats eventually don't fit the context window, so real apps **trim** old messages or **summarise** them.

## 1.7 A chatbot with memory (Lecture 3 code) %%MUST%%

Lecture 3 turns this into a real terminal chatbot. The SDK's **chat session** keeps the history array for you.

```js title="Lecture03/app.js" lines
import { GoogleGenAI } from "@google/genai";
import 'dotenv/config'
import readlineSync from "readline-sync";

const ai = new GoogleGenAI({});

async function main() {
  const chat = ai.chats.create({
    model: "gemini-2.5-flash",
    history: [],
  });

  while (true) {
    const question = readlineSync.question("Ask me Question: ");

    if (question == 'exit') {
      break;
    }

    const response = await chat.sendMessage({
      message: question
    });

    console.log("Response: ", response.text);
  }
}

await main();
```

- **Line 2** — `import 'dotenv/config'` reads the `.env` file and puts `GEMINI_API_KEY` into `process.env`.
- **Line 3** — `readline-sync` reads a line from the keyboard **synchronously** (the program waits). Fine for a terminal toy; never use blocking input in a server.
- **Lines 8–11** — `ai.chats.create` makes a **chat object** that stores the history (starting empty).
- **Lines 13–26** — a normal `while (true)` loop: ask, check for `exit`, send, print.
- **Lines 20–22** — `chat.sendMessage({ message })` does three things for you: appends your message to the stored history, sends the **whole** history to Gemini, and appends the reply to the history.

So `chats.create` is not magic memory inside Google's servers — it is the Lecture 2 array, managed by the SDK **inside your program**. Restart the program and the memory is gone.

## 1.8 System instructions %%MUST%%

A **system instruction** sets the model's role and rules for the whole conversation. Lecture 3 has a (deliberately funny) example: a coding tutor that answers only coding questions and is rude to everything else.

```js title="Lecture 3 (commented example, cleaned) — system instruction" hl=4-9
const response = await ai.models.generateContent({
  model: "gemini-2.5-flash",
  config: {
    systemInstruction: `You are a Coding tutor.
      Strict rules to follow:
      - Only answer questions related to coding.
      - Politely refuse anything that is not about coding.`,
  },
  contents: "What is an array",
});
```

For a chat session, put it in the chat's config:

```js title="system instruction for a chat session" hl=3-5
const chat = ai.chats.create({
  model: "gemini-2.5-flash",
  config: {
    systemInstruction: "Programming tutor: simple words, analogies, one example.",
  },
});
```

:::mistake Where does `systemInstruction` go?
In the current `@google/genai` SDK it goes **inside `config`**. Some notes put it directly inside `ai.chats.create({ model, systemInstruction })`. Plain JavaScript will not complain — it will **silently ignore** it, and your bot will behave like a normal assistant. Quick test: ask your bot "What are your rules?".
:::

Three things to know about system instructions:

- They are **sent with every request**, so a long one costs tokens every time (next section). Keep them short **but clear** — clarity beats saving 50 tokens.
- They are **strong hints, not security**. A clever user can try to talk the model out of its rules ("ignore previous instructions…"). That is **prompt injection** — Chapter 5.
- The best structure: **role → goal → rules → output format → examples**. You will see this exact structure in the multi-agent project's prompts (Chapter 16).

## 1.9 Tokens = money %%MUST%%

Every API call is billed for:

1. the **system instruction** (sent every time),
2. the **whole history** (grows with each message),
3. the **new message**,
4. the **output** (and **thinking** tokens, billed like output).

[[fig:token-growth|The same system instruction is paid for on every call, and the history part keeps growing. Output tokens are usually priced higher than input tokens.]]

Rohit's example: a 100-token system instruction and a 2-token "Hello" cost 102 input tokens; the next short message already costs 125 input tokens, because the first exchange is now part of the history. You can see real numbers in every response:

```js title="printing token usage"
const response = await ai.models.generateContent({
  model: "gemini-2.5-flash",
  contents: "Hi",
});
console.log(response.usageMetadata);
// { promptTokenCount, candidatesTokenCount, thoughtsTokenCount,
//   totalTokenCount, ... }
```

Ways to cut cost (interviewers love this list):

| Trick | Why it works |
|---|---|
| Short, clear system instruction | Paid on every call |
| Trim or summarise old history | History is the part that grows |
| Smaller/faster model for easy steps | Flash-class models cost a fraction of Pro-class |
| `thinkingBudget: 0` for simple questions | Thinking tokens are output tokens |
| Limit output length (`maxOutputTokens`) | Output is the expensive side |
| Retrieve only what's needed (RAG, SchemaMind) | Don't paste whole documents or whole schemas |
| Prompt/context caching | Providers can bill a repeated prefix (system prompt, documents) cheaper |

## 1.10 Context window, knowledge cutoff and common errors %%MUST%%

- **Context window** = the maximum number of tokens the model can look at in one call (input + output). Gemini 2.5 Flash accepts around **1 million** input tokens. Bigger is not automatically better: models are worse at using information buried in the **middle** of a very long prompt (Chapter 9), and you pay for every token.
- **Knowledge cutoff** = the date where the training data ends. Anything later is unknown unless you give it in the prompt (RAG) or let the model fetch it (tools).
- **Hallucination** = fluent, confident, wrong output. Main defences: give the facts in the prompt (RAG), ask it to say "I don't know", lower temperature, and **validate** outputs.

Errors you will actually see:

| Error | Meaning | What to do |
|---|---|---|
| `429` / `RESOURCE_EXHAUSTED` | Too many requests, or your quota is used up | Wait and **retry with exponential backoff** (1 s, 2 s, 4 s…) |
| `503` / overloaded | The provider is busy | Retry later; have a fallback model |
| `400` / invalid argument | Your request is wrong (bad field, too long) | Fix the request; retrying won't help |
| JSON parse error in your code | The model returned text that isn't valid JSON | Ask for JSON mode, strip code fences, retry a few times |

You will see all of these handled in the Graph RAG and multi-agent code (Chapters 12 and 16) with retry loops.

## 1.11 LLM vs chatbot vs agent

| | What it is | Example |
|---|---|---|
| **LLM** | The model: tokens in → next token out | `gemini-2.5-flash` |
| **Chatbot** | LLM + history + a UI | Lecture 3 app, the Gemini app |
| **Agent** | LLM + **tools** + a **loop** that decides the next step | Lecture 5 crypto/weather agent, Lecture 7 code reviewer |

Chapter 3 builds your first agent.

:::remember
- An LLM **predicts the next token**, one token at a time. Plausible ≠ true → **hallucinations**.
- **Tokens** are the units of reading, writing and **billing**; ~4 English characters per token.
- **Temperature** low = precise and repeatable (code, SQL, RAG); high = creative.
- **Thinking** = extra hidden tokens before the answer. Helps multi-step problems, costs output tokens and time.
- `contents` = array of `{ role, parts }`; roles are `user` and `model`.
- The API is **stateless**: memory = the history **you** resend. `ai.chats.create` just manages that array for you.
- The **system instruction** goes in `config`, is sent **every call**, and is **not a security control**.
- Cost = system + history + new message + output (+ thinking). Handle `429` with **exponential backoff**.
:::

:::quiz
1. Why can't Lecture 2's program tell you today's date?
2. You set temperature 0 for a SQL generator. Is the output now guaranteed identical every time? What should you still do?
3. A chat has a 300-token system instruction and 20 turns. Which part of the input grows, and which part is paid again and again?
4. Where does `systemInstruction` go in `ai.chats.create`, and what happens if you put it at the top level?
5. When is `thinkingBudget: 0` the right choice? Give two examples.
:::

:::answer
1. The model has no clock and its knowledge stops at the training cutoff. It needs a **tool** (or the date in the prompt).
2. No — it becomes very repeatable, but not guaranteed. Still **validate** the SQL (parse it, check it is a read) before running it.
3. The **history** grows every turn; the **system instruction** (300 tokens) is paid on **every** call.
4. Inside `config: { systemInstruction }`. At the top level, plain JavaScript silently ignores it.
5. Simple, one-step requests: a definition ("what is `const`?"), a simple fact, formatting or translating a short sentence.
:::

:::qa Interview questions — LLM basics
Q: What does an LLM actually do?
It predicts the next token given all previous tokens. Generation is a loop: predict a probability for every token in the vocabulary, pick one (greedy or sampled, controlled by temperature/top-p), append it, and repeat until an end token. Everything else — chat, code, "reasoning" — is built from that loop.

Q: Why do LLMs hallucinate, and how do you reduce it?
Because training rewards the most **plausible** continuation, not the **true** one. When the model lacks the fact, a fluent guess is still plausible. Reduce it by grounding (RAG — put the facts in the prompt and say "answer only from the context"), letting it say "I don't know" (abstention, like PaperRAG), low temperature for factual tasks, and validating outputs with code.

Q: Is the Gemini/OpenAI chat API stateful? How does the chatbot remember?
No, it is stateless. The client sends the whole conversation (as `contents` / `messages`) on every call. SDK chat objects like `ai.chats.create` just keep that array in your program. That is why cost grows with conversation length and why long chats need trimming or summarising.

Q: What is a token and why should an engineer care?
A token is a sub-word piece of text; the model reads and writes token ids. Engineers care because pricing, rate limits and the context window are all measured in tokens, and tokenisation explains odd failures like counting letters.

Q: What is temperature? What value would you use for a text-to-SQL system?
It controls how random the choice of the next token is. For text-to-SQL, extraction or RAG I use a low value (0–0.3) for precise, repeatable output — and I still validate the result, because even temperature 0 is not a hard guarantee.

Q: What are "reasoning" or "thinking" models?
Models trained to produce intermediate reasoning tokens before answering. Those tokens change the context and make correct answers more likely on multi-step problems. The trade-off is latency and cost, because thinking tokens are billed as output. I enable it for complex tasks and turn it off for simple lookups.

Q: How would you reduce the cost of a chatbot?
Shorter system prompt, trim or summarise history, use a smaller model for easy turns, disable thinking for simple questions, cap output length, retrieve only relevant context instead of pasting documents, and use prompt caching for a fixed prefix. Then measure with `usageMetadata`.

Q: What is a context window, and does a 1-million-token window make RAG unnecessary?
It is the maximum number of tokens per call. A huge window does not remove the need for RAG: you pay for every token on every call, latency grows, models miss facts buried in the middle of long prompts, and RAG gives you citations, fresh data and access control. Long context and RAG are often combined.

Q: You get HTTP 429 from the API. What do you do?
It means rate limit or quota exhausted. Retry with exponential backoff (plus a little random jitter), cap the number of retries, reduce concurrency, and if it keeps happening, upgrade the quota or queue requests.
:::
