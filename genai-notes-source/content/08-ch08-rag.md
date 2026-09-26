:::chapter 8 | RAG from Zero | Lectures 12–13 · indexing.js + query.js · Must-know
- **Why** RAG exists: cutoff, hallucination, private data
- The **open-book exam** idea
- The two phases: **indexing** and **query**
- **Chunking**: size, overlap, and the recursive splitter
- **LangChain** as the "STL of RAG"
- `indexing.js` and `query.js`, line by line
- The 2026 update: `gemini-embedding-001` and index dimensions
- What this basic RAG **can't** do yet
:::

This is the most important chapter for your interviews and for **PaperRAG**. Every company building with LLMs builds some RAG. If you can draw the pipeline, explain each step and its trade-offs, and show the code, you are ahead of most candidates.

## 8.1 The problem RAG solves %%MUST%%

From Rohit's RAG notes — a normal LLM has three limits:

1. **Knowledge cutoff** — its knowledge is frozen at training time. Ask about something after that date and it doesn't know.
2. **Hallucinations** — when it doesn't know, it may produce a plausible, confident, **false** answer, because its goal is the likely next token, not the truth.
3. **No private data** — it has never read your company's documents, your notes, your course PDF, or last week's research papers.

> **Core question:** how can an LLM answer from **up-to-date, specific or private** information **without making things up**?

Why not just paste all the documents into the prompt? Rohit's whiteboard example: a chat history or a 120-page PDF can be **lakhs of tokens**. You'd pay for all of it on **every** question, hit context limits, get slower answers, and the model would still miss details in the middle. We need to send **only the relevant pieces**.

## 8.2 RAG = Retrieval-Augmented Generation %%MUST%%

- **Retrieval** — find and fetch the relevant information (like fetching a book from a library).
- **Augmented** — add that information to the user's question.
- **Generation** — the LLM writes the answer from it.

:::analogy The open-book exam
A normal LLM is a clever student writing an exam **from memory** — good, but may forget or invent details. A RAG system is the same student in an **open-book exam**: before answering, they look up the exact page in the official textbook and answer from it. RAG gives the LLM a textbook to consult in real time.
:::

## 8.3 The two phases %%MUST%%

[[fig:rag-phases|RAG has an offline indexing phase (prepare the "textbook") and an online query phase (answer each question). Both must use the same embedding model.]]

**Phase A — Indexing (done once, updated when documents change):**

1. **Load** the documents (PDFs, web pages, tickets, wiki).
2. **Chunk** them into small pieces (paragraph-sized).
3. **Embed** each chunk into a vector (Chapter 6).
4. **Store** vectors + chunk text + metadata in a vector database (Chapter 7).

**Phase B — Query (every question):**

1. **Embed the question** with the **same** embedding model.
2. **Search** the vector DB for the top-k most similar chunks.
3. **Augment**: build a prompt = instructions + retrieved chunks (context) + question.
4. **Generate**: the LLM answers from the context.

The augmented prompt looks like this (Rohit's HR-policy example):

```prompt title="an augmented prompt"
CONTEXT:
- [Chunk 1] ...the new policy for 2025 states that employees can work
  remotely up to 3 days a week...
- [Chunk 2] ...approval for remote work must be obtained from a direct manager...
- [Chunk 3] ...all remote work must be conducted from within the country...

QUESTION: What are the new HR policies on remote work for 2025?

INSTRUCTION: Based only on the context provided above, answer the user's question.
```

What RAG gives you: **fresh knowledge** (just re-index new documents), **fewer hallucinations** (answers are grounded in the context), **private/domain data**, **citations** (you know which chunks were used — "HR-Policy-2025.pdf, page 4"), and it's **much cheaper than fine-tuning**.

## 8.4 Chunking: cutting documents into pieces %%MUST%%

Why chunk at all?

- One vector for a whole book **blurs** all its topics together — search becomes useless.
- The LLM needs **small, relevant** pieces, not 120 pages.
- Embedding models have an **input limit**.

Two numbers control chunking: **chunk size** and **overlap**. The course uses `chunkSize: 1000` characters and `chunkOverlap: 200`. Rohit's whiteboard shows what overlap means:

[[fig:chunk-overlap|chunkSize = 1000, chunkOverlap = 200: each new chunk starts 800 characters after the previous one, so the last 200 characters are repeated.]]

Why overlap? If an important sentence sits exactly on a boundary, the overlap makes sure it appears **whole** in at least one chunk.

| Chunks too **small** | Chunks too **big** |
|---|---|
| Lose context ("it" — what is "it"?) | Mix several topics; the embedding gets "averaged" and matches worse |
| More vectors to store and search | Fewer chunks fit in the prompt; more tokens per answer |
| Answers need many chunks | Irrelevant text distracts the LLM |

**RecursiveCharacterTextSplitter** (LangChain) is smart about **where** it cuts: it first tries to split on paragraph breaks (`"\n\n"`), then line breaks (`"\n"`), then spaces, and only as a last resort in the middle of a word — always keeping pieces under `chunkSize`. So paragraphs stay together when possible.

## 8.5 LangChain: the STL of RAG %%GOOD%%

Rohit's first-principles point on the whiteboard: loading a PDF, splitting text, calling embedding APIs, talking to Pinecone — you *could* write 50 lines for each. **LangChain** gives you tested building blocks ("utility functions") so each is one line.

:::cpp Like the STL
You can write your own linked list and sort in C++, but you use `std::list` and `std::sort` because they're tested and standard. LangChain is the same for LLM apps: `PDFLoader`, `RecursiveCharacterTextSplitter`, `GoogleGenerativeAIEmbeddings`, `PineconeStore`, `PromptTemplate`… And like the STL, you should still know what happens **inside** — interviewers ask.
:::

Honest trade-off: LangChain speeds you up, but adds abstraction layers and version churn (the course hits a version conflict in Lecture 19 and calls the Pinecone SDK directly). Your projects (PaperRAG, SchemaMind) deliberately use **no framework**, so every step is visible — that's a fine interview answer too.

## 8.6 The indexing code (Lecture 12) %%MUST%%

Setup from the notes:

```bash title="install (from the RAG System notes)"
npm i @langchain/core @langchain/pinecone @pinecone-database/pinecone \
      @langchain/community @langchain/google-genai @langchain/textsplitters \
      dotenv pdf-parse readline-sync
```

```env title=".env (placeholders — the real notes page contained live keys; never do that)"
GEMINI_API_KEY=your_gemini_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=your_index_name
```

```js title="Lecture12and13/indexing.js" lines
import * as dotenv from 'dotenv';
dotenv.config();
import { PDFLoader } from '@langchain/community/document_loaders/fs/pdf';
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters';
import { GoogleGenerativeAIEmbeddings } from '@langchain/google-genai';
import { Pinecone } from '@pinecone-database/pinecone';
import { PineconeStore } from '@langchain/pinecone';

async function indexing() {
  // load the PDF
  const PDF_PATH = './Node.pdf';
  const pdfLoader = new PDFLoader(PDF_PATH);
  const rawDocs = await pdfLoader.load();

  // create chunks
  const textSplitter = new RecursiveCharacterTextSplitter({
    chunkSize: 1000,
    chunkOverlap: 200,
  });
  const chunkedDocs = await textSplitter.splitDocuments(rawDocs);
  // console.log(chunkedDocs.length);  266 chunks --> vectors

  // configure the embedding model
  const embeddings = new GoogleGenerativeAIEmbeddings({
    apiKey: process.env.GEMINI_API_KEY,
    model: 'text-embedding-004',
  });

  // configure Pinecone
  const pinecone = new Pinecone();
  const pineconeIndex = pinecone.Index(process.env.PINECONE_INDEX_NAME);

  // single step: chunkedDocs --> embeddings --> vector DB
  await PineconeStore.fromDocuments(chunkedDocs, embeddings, {
    pineconeIndex,
    maxConcurrency: 5,
  });
}

indexing();
```

- **Lines 1–2** — load `.env` into `process.env`.
- **Lines 11–13** — `PDFLoader` reads `Node.pdf` (a Node.js course PDF) and returns an array of **Documents** — by default **one per page**, each with `pageContent` (text) and `metadata` (source file, page number).
- **Lines 16–20** — split every page into ~1000-character chunks with 200 overlap. Rohit's comment: this PDF became **266 chunks**.
- **Lines 24–27** — the embedding model object (text → vector). The key could also come from the environment automatically.
- **Lines 30–31** — the Pinecone client reads `PINECONE_API_KEY` from the environment; `.Index(name)` points at one index (like one table).
- **Lines 34–37** — the magic line: for every chunk, **embed** it and **upsert** vector + metadata (including the chunk text) into Pinecone. `maxConcurrency: 5` = at most 5 embedding requests at the same time (faster, but gentle on rate limits).

:::mistake 2026 update — this exact code no longer runs as-is
`text-embedding-004` was **shut down on 14 January 2026**. Change the model to `gemini-embedding-001`. That model returns **3072** numbers by default, so the Pinecone index must be created with **dimension 3072** (metric: cosine). An index made for the old 768-d vectors will reject the new ones — and you must re-embed all chunks anyway, because vectors from different models can't be mixed (Chapter 6).
:::

## 8.7 The query code (Lecture 13) %%MUST%%

```js title="Lecture12and13/query.js" lines
import readlineSync from 'readline-sync';
import { GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI }
  from '@langchain/google-genai';
import { Pinecone } from '@pinecone-database/pinecone';
import * as dotenv from 'dotenv';
dotenv.config();
import { PromptTemplate } from '@langchain/core/prompts';
import { StringOutputParser } from '@langchain/core/output_parsers';
import { RunnableSequence } from '@langchain/core/runnables';

const embeddings = new GoogleGenerativeAIEmbeddings({
  apiKey: process.env.GEMINI_API_KEY,
  model: 'text-embedding-004',        // → 'gemini-embedding-001' in 2026
});
const model = new ChatGoogleGenerativeAI({
  apiKey: process.env.GEMINI_API_KEY,
  model: 'gemini-2.5-flash',
  temperature: 0.3,
});
const pinecone = new Pinecone();
const pineconeIndex = pinecone.Index(process.env.PINECONE_INDEX_NAME);

async function chatting(question) {
  // 1. embed the question
  const queryVector = await embeddings.embedQuery(question);

  // 2. search the vector DB: top 10
  const searchResults = await pineconeIndex.query({
    topK: 10,
    vector: queryVector,
    includeMetadata: true,
  });
  const context = searchResults.matches
                   .map(match => match.metadata.text)
                   .join("\n\n---\n\n");

  // 3. question + top 10 → LLM
  const promptTemplate = PromptTemplate.fromTemplate(`
You are a helpful assistant answering questions based on the provided documentation.
Context from the documentation:
{context}
Question: {question}
Instructions:
- Answer the question using ONLY the information from the context above
- If the answer is not in the context, say "I don't have enough information to answer that question."
- Be concise and clear
- Use code examples from the context if relevant
Answer:`);

  const chain = RunnableSequence.from([
    promptTemplate,
    model,
    new StringOutputParser(),
  ]);
  const answer = await chain.invoke({ context: context, question: question });
  console.log(answer);
}

async function main() {
  const userProblem = readlineSync.question("Ask me anything--> ");
  await chatting(userProblem);
  main();
}
main();
```

- **Lines 11–14** — the **same** embedding model as indexing. Different model = meaningless search.
- **Lines 15–19** — the chat model through LangChain; `temperature: 0.3` = mostly factual, a little natural wording.
- **Line 25** — `embedQuery` turns the question into a vector.
- **Lines 28–32** — ask Pinecone for the **10 nearest** chunk vectors, and include their metadata (which holds the chunk text).
- **Lines 33–35** — pull the text out of each match and join them with a visible separator `---`, so the LLM sees 10 distinct passages.
- **Lines 38–48** — the prompt template. `{context}` and `{question}` are placeholders. The instructions are the anti-hallucination part: **use ONLY the context**, and a fixed sentence to say when the answer isn't there.
- **Lines 50–54** — a **chain**: prompt → model → parser. The template fills the placeholders, the model generates, and `StringOutputParser` turns the model's message object into a plain string. (It's function composition, like `parser(model(prompt(input)))` — or a Unix pipe.)
- **Line 55** — run the chain with the real values.
- **Lines 59–64** — ask again forever. `main()` calls itself after each answer; a `while (true)` loop would be cleaner, and there's no `try/catch`, so one network error ends the program.

:::remember What "temperature 0.3" and the prompt rules are doing
The prompt says "ONLY the context" and gives an **escape sentence**. That doesn't *guarantee* faithfulness, but it strongly reduces invented answers. Your PaperRAG goes further: a **similarity threshold** refuses before calling the LLM at all, and a second check (`INSUFFICIENT_CONTEXT`) catches on-topic-but-unanswerable questions (Chapter 17).
:::

## 8.8 What this basic RAG can't do yet %%MUST%%

Run it for a while and you'll hit these — each is a section of Chapter 9:

1. **Follow-up questions fail.** Ask "What is Node.js?" then "Explain **it** in detail". The second query embeds the words "explain it in detail" — which match nothing useful — because the code keeps **no chat history**. (Rohit's whiteboard shows exactly this.)
2. **Top-10 always returns 10**, even when nothing is relevant — there's no minimum similarity. Garbage in, confident garbage out.
3. **No citations** shown to the user, although the metadata (page numbers) is available.
4. **Multi-hop questions fail**: "Who is the friend of the friend of the Tesla owner's friend?" needs facts from several places **connected** step by step — similarity search finds each piece's neighbourhood, not the chain (Chapter 11–12: graphs).
5. **Exact terms** (error codes, function names) may be missed by pure vector search → hybrid search.
6. **No evaluation**: you don't know how often it's right.

:::remember
- RAG fixes **cutoff**, **hallucination** and **private data** by retrieving relevant chunks and adding them to the prompt — an **open-book exam**.
- **Indexing**: load → chunk → embed → store. **Query**: embed question → top-k search → augment prompt → generate.
- **Same embedding model** for both phases; index dimension must match the model (3072 for `gemini-embedding-001`).
- Chunking: **size** (course: 1000 chars) and **overlap** (200) — trade-off between context and precision. Recursive splitter cuts at paragraphs first.
- The prompt: "answer ONLY from context" + an escape sentence; low temperature.
- `RunnableSequence` = prompt → model → parser pipeline.
- Basic RAG lacks: history for follow-ups, a similarity cut-off, citations, multi-hop reasoning, exact-term matching, evaluation.
:::

:::quiz
1. Name the four steps of the indexing phase.
2. With chunkSize 1000 and overlap 200, where does the third chunk start?
3. Why must `query.js` use the same embedding model as `indexing.js`?
4. What does `StringOutputParser` do in the chain?
5. The user asks "Explain it in detail" after a question about the V8 engine. Why does basic RAG fail?
:::

:::answer
1. Load → chunk → embed → store.
2. At character 1600 (chunks start at 0, 800, 1600 — the whiteboard's 1–1000, 801–1800, 1601–2600).
3. Each model has its own vector space; a question vector from a different model can't be compared with the stored vectors.
4. Converts the chat model's message object into a plain string.
5. The retrieval query is only "Explain it in detail" — "it" is unresolved because no history is used, so the embedding matches nothing about V8.
:::

:::qa Interview questions — RAG basics
Q: What is RAG and why use it instead of fine-tuning?
Retrieval-Augmented Generation: retrieve relevant chunks from an external knowledge base and put them in the prompt so the LLM answers from them. It handles fresh and private data without retraining, reduces hallucinations by grounding, gives citations, and is far cheaper to update than fine-tuning. Fine-tuning is better for changing behaviour or style, not for adding changing facts.

Q: Walk me through a RAG pipeline end to end.
Offline: load documents, chunk them (size + overlap), embed each chunk, store vectors with text and metadata in a vector store. Online: embed the user question with the same model, retrieve top-k similar chunks (optionally with filters), build a prompt with instructions + context + question, call the LLM with low temperature, and return the answer with citations. Then evaluate retrieval and answer quality on a labelled set.

Q: How do you choose chunk size and overlap?
Start from the document structure and the embedding model's input limit: paragraph-sized chunks (a few hundred tokens) with 10–20% overlap is a common starting point. Too small loses context; too large mixes topics and wastes tokens. Then tune on an evaluation set by measuring retrieval recall and answer quality. Layout-aware chunking often beats fixed sizes — in PaperRAG I chunk by PDF text blocks and never cross a page, so every chunk has one page number.

Q: What does top-k mean and how do you pick it?
The number of most-similar chunks retrieved. Higher k raises the chance the answer is included (recall) but adds noise, cost and "lost in the middle" effects. Typical values are 3–10; better: retrieve more (say 20–50), rerank, and keep the best few.

Q: How do you reduce hallucinations in RAG?
Good retrieval first (chunking, hybrid search, reranking), a prompt that restricts the model to the context with an explicit "I don't know" option, low temperature, a similarity threshold to abstain when nothing relevant is found, citations so users can verify, and evaluation of faithfulness.

Q: What metadata would you store with each chunk and why?
Source file, page/section, title, date, author/owner, access-control ids and the chunk text. It enables citations, filtering (by user, date, document type), debugging and re-indexing specific documents.
:::
