:::chapter 3 | Seeing Them Together | Shared design · one-minute explanations · glossary
- **The same four steps** inside both projects
- PaperRAG and SchemaMind side by side
- How to explain each project in one minute
- Questions that cover both projects
- **Glossary** of every word in this guide
:::

## 3.1 The same skeleton

Put the two pipelines next to each other and the same four steps appear. Once you see them, you can explain either project in the same order, and you already have an answer to *"What do your projects have in common?"*.

[[fig:pb-skeleton|Both projects first find the right material, then make an answer from it, check it, and show the evidence.]]

**What each one does**

| | PaperRAG | SchemaMind |
|---|---|---|
| You ask about | a folder of research papers | the database of a small shop |
| What is searched | text chunks of up to 900 characters | one card per table |
| How it searches | MiniLM numbers, FAISS, top 5 | MiniLM numbers, top 3 |
| The answer is made of | the passages, or Mistral's answer written from them | an SQL query and the rows it returns |

**How each one stays honest**

| | PaperRAG | SchemaMind |
|---|---|---|
| The main check | is the best score at least 0.50? | one read query only, then read-only, 5 s, 200 rows |
| The evidence shown | file and page of every passage | the SQL itself |
| Its honest "no" | "I don't have enough supporting material…" | "Could not generate a query for this question." |
| Without an API key | extractive mode | template mode |
| Tests, run by CI on every push | 51 | 52 |
| Biggest open item | only 63% of answers cite the right page | accuracy numbers for Mistral mode |

Two differences are worth noticing. PaperRAG's worst mistake is a **wrong answer**; SchemaMind's output is **code that runs on a database**, so its worst mistake could be a deleted table. That's why SchemaMind has three safety layers where PaperRAG has one guard. And SchemaMind doesn't need FAISS: comparing a question with 5 table cards takes one line of numpy.

## 3.2 Explaining each project in one minute

Every project story has the same five parts. Here they are for both projects, so you can see the structure before you read the full versions.

| Part | PaperRAG | SchemaMind |
|---|---|---|
| The problem | LLMs make things up and don't say where an answer came from | most people can't write SQL, and SQL written by an LLM can be unsafe or quietly wrong |
| How it works | blocks → chunks → numbers → top 5 → guard → answer | table cards → top 3 tables → SQL → validator → read-only run |
| A decision you can defend | a chunk never crosses a page, so every chunk has one page number | the SQL is parsed into a tree instead of being searched for bad words |
| How you know it works | 51 tests; on 51 questions the guard refused 14 of 17 unanswerable ones and 4 of 34 good ones | 52 tests, including real attacks, and an execution-accuracy script |
| What comes next | keyword search and a reranker, measured with the same 51 questions | questions with gold SQL; per-user permissions |

:::pitch PaperRAG in one minute
"PaperRAG answers questions about a folder of research papers and gives the **file and page** of every passage it used. It reads each PDF in visual text blocks, puts two-column pages in reading order, and packs the blocks into chunks of at most 900 characters that **never cross a page**, so every chunk carries exactly one page number. Each chunk becomes a 384-number MiniLM vector in a FAISS index. For a question it finds the five closest chunks, and if even the best one scores below a threshold, it **refuses instead of guessing**. By default it returns the passages word for word, so it can't invent anything; with an API key, Mistral writes a short answer from them, with a second refusal check. It has a FastAPI server, a Streamlit page and 51 offline tests. On 51 hand-checked questions about 8 papers, the guard refused 14 of the 17 unanswerable questions while wrongly refusing 4 of the 34 answerable ones, and I picked the threshold, 0.50, from that sweep."
:::

:::pitch SchemaMind in one minute
"SchemaMind lets you ask a database a question in plain English and shows the answer **together with the SQL** that produced it. It reads the database's own structure and writes a short card for every table, with columns, keys and two sample rows. For a question it picks the three most relevant cards with MiniLM, so the prompt stays small even when a database has hundreds of tables. The SQL comes from Mistral, or from a template mode that needs no API key and **refuses any question it doesn't match completely**. Every query then passes **three safety layers**: sqlglot parses it and allows exactly one read statement, the database file is opened read-only, and a five-second limit and a 200-row cap stop runaway queries. Errors go back to the SQL writer for at most two repairs. 52 offline tests include real attacks, such as a `DROP` hidden behind a `SELECT`."
:::

:::tip How to practise the pitches
Say each one out loud with a timer: aim for 60–70 seconds. Don't learn the words by heart; learn the five parts in the table above and say them your own way. Then stop and let the interviewer pick what to dig into. The question sections in Parts 1 and 2 are where they will dig.
:::

## 3.3 Questions that cover both projects

:::qa -
Q: What do your two projects have in common?
Both find the right material first and answer only from it. Both check before answering, show their evidence (pages or SQL), and refuse instead of guessing. Both also run without an API key, which made them easy to test offline.

Q: Both use MiniLM. Why the same model?
It is small (about 80 MB), runs on a normal laptop CPU in milliseconds, and is good enough for matching short texts. In SchemaMind it only has to pick 3 of 5 table cards, so even a weak model works. In PaperRAG it matters more, and the evaluation is where you would test whether a bigger model is worth it.

Q: PaperRAG uses FAISS and SchemaMind doesn't. Why?
SchemaMind compares the question with 5 cards, which numpy does in one step. PaperRAG may hold thousands of chunks and saves them to disk, so a real vector index is worth it. Use the simplest tool that fits the size of the problem.

Q: Which project is harder to evaluate?
PaperRAG. You need questions, the pages that answer them, and a judgement of whether each answer is supported. SchemaMind has an exact referee: run the gold SQL and compare the rows.

Q: How are the two "I don't know"s different?
PaperRAG refuses when its search finds nothing close enough, or when Mistral says the passages don't contain the answer. SchemaMind refuses when it can't write a query: no template matches the whole question, or Mistral replies `CANNOT_ANSWER`. Both prefer a clear "no" to a believable wrong answer.

Q: Could you combine the two projects?
Yes, as one assistant with two tools: questions about documents go to PaperRAG's search, questions about numbers go to SchemaMind. A router, either simple rules or an LLM, picks the tool, and each tool keeps its own checks. Letting a model choose its tools like this is what **agentic RAG** means.

Q: How do you know a change didn't break anything?
Both projects have offline tests, 51 and 52, that finish in seconds. **GitHub Actions** runs all of them after every push, on a fresh Linux machine, with Python 3.11 and with 3.14. A pull request shows a green tick or a red cross before it is merged, and the badge in each README shows the state of `main`.

Q: Why does CI install the CPU-only build of PyTorch?
PyTorch comes in with sentence-transformers, and its default Linux build includes several GB of GPU libraries. The tests never run a model and GitHub's machines have no GPU, so the much smaller CPU-only build is enough. A whole run takes about a minute and a half.

Q: Why test on Python 3.11 and 3.14?
3.11 is the oldest version the READMEs promise, and 3.14 is the one on your Mac. Testing both ends catches code, or a pinned library, that works on one version but not on the other.

Q: What would you do with one more week?
PaperRAG has real numbers now, so: write 15–20 questions with gold SQL and measure SchemaMind's Mistral mode, then add keyword search to PaperRAG and re-run its 51 questions to see whether the right page goes up from 63%. CI already runs all 103 tests on every push, so each change would be checked automatically.

Q: What did building both projects teach you?
Testing finds bugs that reading the code doesn't: two chunking bugs, an injection check that worked only by luck, a timeout that never fired and five wrong template answers. And an honest refusal beats a confident wrong answer, so both projects are built to say no.
:::

## 3.4 Glossary

Every word in this guide, in one line each. The last column says which project uses it.

| Word | What it means | Used in |
|---|---|---|
| Agentic RAG | an LLM decides which search or tool to use for each question | idea |
| API | a way for one program to ask another for something; here, over HTTP | both |
| Band | a strip of a two-column page between two wide blocks | PaperRAG |
| Block | a paragraph-sized piece of text on a PDF page, with its position | PaperRAG |
| Chunk | up to 900 characters of text from one page; the piece PaperRAG searches | PaperRAG |
| CI | continuous integration: GitHub runs the tests on every push | both |
| Citation | the file and page that a passage came from | PaperRAG |
| Citation hit rate | how often the right page is among the cited ones (63% in PaperRAG) | PaperRAG |
| Cosine similarity | how closely two vectors point the same way; 1 = same meaning | both |
| Dot product | multiply two lists number by number, then add; for vectors normalised to length 1 it equals cosine similarity | both |
| Embedding | a vector: a list of numbers (384 here) that describes what a text means | both |
| Endpoint | an address on a server that does one job, like `/ask` or `/health` | both |
| Evidence phrase | a short phrase copied from the page that answers a test question | PaperRAG |
| Execution accuracy | how often SchemaMind's rows equal the rows of the gold SQL | SchemaMind |
| Extractive mode | PaperRAG's default: return the passages word for word | PaperRAG |
| FAISS | a library that finds the closest vectors quickly | PaperRAG |
| False refusal | a question the system could answer but refused | PaperRAG |
| FastAPI | the Python library both web servers are built with | both |
| Foreign key (FK) | a column that points to a row in another table | SchemaMind |
| Gold SQL | SQL you wrote by hand as the correct answer, used for grading | SchemaMind |
| Guard | refuse when the best score is below the threshold | PaperRAG |
| Hallucination | an LLM stating something false in a confident voice | both |
| Index | a structure built for fast searching; PaperRAG's is a FAISS index | PaperRAG |
| JOIN | connect the rows of two tables through matching IDs | SchemaMind |
| JSON | a simple text format for data, like `{"question": "..."}` | both |
| LLM | large language model, such as Mistral or GPT | both |
| MiniLM | all-MiniLM-L6-v2, the small embedding model both projects use | both |
| Mistral mode | the LLM writes the answer (PaperRAG) or the SQL (SchemaMind) | both |
| Overlap | the end of one chunk repeated at the start of the next, 150 characters | PaperRAG |
| Parse | read text into a structure (a tree) by following grammar rules | SchemaMind |
| Primary key (PK) | a row's own ID, like `order_id` | SchemaMind |
| Progress handler | a function SQLite calls every 10,000 steps; used for the time limit | SchemaMind |
| PyMuPDF | the library that reads text and positions out of PDFs | PaperRAG |
| pytest | the tool that finds and runs the tests (code that checks other code) | both |
| RAG | retrieval-augmented generation: find relevant text first, then answer from it | PaperRAG |
| Read-only | opened so that nothing can be changed (`mode=ro`) | SchemaMind |
| Regex | a pattern for matching text; template mode's shapes are regexes | SchemaMind |
| Repair loop | send the error back to the SQL writer and try again; 3 tries at most | SchemaMind |
| Retrieval | finding the pieces most relevant to a question | both |
| Schema | the structure of a database: its tables, columns and keys | SchemaMind |
| Semantic layer | one shared definition of business words like "revenue" | SchemaMind |
| sqlglot | a Python library that parses SQL into a tree | SchemaMind |
| SQLite | a small database stored in a single file, here `shop.db` | SchemaMind |
| Streamlit | a library for quick web pages in Python; both projects' UI | both |
| Sweep | running the evaluation once for every threshold, to pick one | PaperRAG |
| Table card | SchemaMind's short description of one table, with two sample rows | SchemaMind |
| Temperature | how random an LLM's output is; 0 gives the same answer every time | both |
| Template mode | SchemaMind's default: fixed question shapes with ready-made SQL | SchemaMind |
| Threshold | the cut-off score; PaperRAG uses 0.50, picked from its evaluation | PaperRAG |
| Top-k | the k best matches: 5 chunks, or 3 tables | both |
| Validator | SchemaMind's SQL checker (`app/validate.py`) | SchemaMind |
| Word piece | the small text pieces a model reads; MiniLM reads up to 256 | both |
