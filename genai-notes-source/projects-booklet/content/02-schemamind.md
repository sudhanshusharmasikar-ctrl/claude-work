:::chapter 2 | SchemaMind: Ask a Database in Plain English | Text-to-SQL · sqlglot · read-only SQLite
- What problem SchemaMind solves, and the three ways text-to-SQL goes wrong
- The sample shop database, table by table
- **The whole pipeline in one picture**
- Each step: table cards, picking tables, writing SQL, checking it, running it, the repair loop
- **The safety layers**, and why safe is not the same as correct
- One question followed from start to finish, with real output
- What we changed in each session, and what we tried
- **Questions and answers**
:::

## 2.1 The problem, in plain words

Companies keep their data in a **database**: tables of customers, orders and payments. To get an answer out of it you write **SQL**, a language for asking databases questions. Most people can't, so they wait for someone who can.

SchemaMind lets you type the question in English, *"How many orders came from Pune?"*. It writes the SQL, runs it **safely**, and shows you both the answer and the SQL.

Letting an LLM write SQL goes wrong in three ways, and SchemaMind has a mechanism for each:

| What can go wrong | Example | SchemaMind's answer |
|---|---|---|
| Too many tables to describe | a real company database has hundreds of tables; describing them all in every prompt doesn't fit | **retrieve** only the 3 most relevant table descriptions |
| Destructive SQL | a confusing question produces `DROP TABLE customers` | a **validator**, a **read-only** connection and **limits** |
| Silent wrongness | valid SQL that runs fine but answers a different question | show the SQL; template mode refuses what it doesn't fully understand; the evaluation compares results |

## 2.2 The sample shop database

[[fig:pb-er|The five tables of `data/shop.db`. Each table has its own ID (PK); an FK column points to another table's ID, which is how the tables connect.]]

`python -m app.seed_db` builds this database with made-up data (always the same data, because it uses a fixed random seed). A few words you'll need:

- A **table** is a grid: each **row** is one thing (one customer, one order), each **column** is one fact about it.
- A **primary key (PK)** is a row's own ID, like `order_id`.
- A **foreign key (FK)** points to a row in another table. `orders.customer_id = 12` means "this order belongs to customer 12".
- A **JOIN** connects two tables through such a pair of IDs. The city lives in `customers` and the orders live in `orders`, so counting orders from Pune needs a JOIN.

## 2.3 The whole pipeline in one picture

[[fig:pb-schemamind-pipeline|At startup SchemaMind writes a short card for every table and turns each card into numbers. For each question it picks the 3 most relevant tables, writes SQL, checks it, runs it safely, and returns the rows together with the SQL. Failures go back through the repair loop.]]

## 2.4 Each step, in order

### A · Table cards, made once at startup

`introspect()` in `app/schema_introspect.py` reads the database's own description of itself: the table names, every column with its type, which columns are keys, and two sample rows. `describe()` turns each table into a short text card. This one is **real** (lines wrapped here):

```output title="the card for the orders table (real output, wrapped)"
Table orders: order_id (INTEGER, PK),
  customer_id (INTEGER, -> customers.customer_id),
  order_date (DATE), status (TEXT)
Sample rows from orders:
  order_id=1, customer_id=12, order_date=2025-09-07, status=placed
  order_id=2, customer_id=8, order_date=2026-06-09, status=delivered
```

The sample rows matter: they show that `status` holds words like `delivered`, not number codes, which a plain list of columns can't tell. Each card is then turned into numbers with MiniLM, the same model PaperRAG uses. Because the cards are read from the database itself, the project works on any SQLite database, not just this one.

### B1–B2 · Pick the relevant tables

The question is turned into numbers too, and compared with every table card. The **3 most similar** cards are picked (`SchemaRetriever.relevant_tables()` in `app/schema_retriever.py`).

With 5 tables this is barely needed. It is here because a real database has hundreds of tables, and you can only show a model a few of them. One honest detail: **template mode ignores the picked tables**, because its SQL is pre-written. The picked tables are shown in the reply, and they matter only in Mistral mode.

### B3 · Write the SQL

There are two ways, set by `SCHEMAMIND_GEN_MODE`:

**Template mode** (the default; no API key needed) knows a fixed list of question shapes:

| Shape | Example | Real answer |
|---|---|---|
| how many *status* orders | how many cancelled orders | 24 |
| how many orders from/in *city* | how many orders from Pune | 22 |
| how many orders / customers / products | how many customers | 40 |
| top *N* customers by spend | top 3 customers by spend | Customer 7, 26, 15 |
| top *N* customers by orders | top 3 customers by orders | 9, 7, 7 orders |
| orders from/in *city* | orders from Indore | the 31 orders, listed |
| revenue by category / city | revenue by category | Electronics 4,703,200, Accessories 88,000 |
| *status* orders | cancelled orders | the 24 orders, listed |

[[fig:pb-template-matching|Template mode first tidies the question, then needs a shape that matches the whole question. A question with words left over is refused instead of half-answered.]]

The rule that matters: the **whole** question has to match a shape. Matching only part of it is how template mode used to give wrong answers without any error (see 2.7).

**Mistral mode** is the real text-to-SQL. The 3 table cards and the question go to the Mistral LLM with rules: write a single SQLite `SELECT`, use only the given tables and columns, never write `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER` or `CREATE`, return only the SQL, and reply `CANNOT_ANSWER` if the tables can't answer the question. Temperature is 0. It needs a `MISTRAL_API_KEY`.

### B4 · Check the SQL: the validator

The validator (`app/validate.py`) doesn't search the text for bad words. It uses **sqlglot** to **parse** the SQL into a tree, the same way a compiler reads code, and checks the tree:

[[fig:pb-sql-tree|Left: how sqlglot sees a normal query. Right: two statements give two trees, which is refused.]]

1. **Exactly one statement.** `SELECT …; DROP TABLE customers` is two statements, so it is refused.
2. **It must be a read query:** a `SELECT`, or several `SELECT`s joined with `UNION`, `INTERSECT` or `EXCEPT`.
3. **No write hidden anywhere inside**, for example a `DELETE` tucked into a `WITH` part. It walks every node of the tree to check.

### B5 · Run the SQL: the executor

`execute()` in `app/executor.py` runs the checked SQL with three protections:

- The database file is opened **read-only** (`mode=ro`). If a write ever got past the validator, SQLite itself refuses it: *attempt to write a readonly database*.
- A **5-second limit**. SQLite calls a small function every 10,000 steps of work; that function looks at the clock and, after 5 seconds, tells SQLite to stop. This stops queries that would run forever, like an endless recursive query or a join of four big tables.
- At most **200 rows** come back, so a huge result can't flood the page.

Together with the validator, these make the safety layers:

[[fig:pb-safety-layers|Each layer stops what the one before might miss. A normal read passes all three. None of them can tell whether a valid query answers the right question.]]

### B6 · The repair loop

If the SQL fails the validator or the database returns an error, the error message and the failed SQL go back to the SQL writer with a note to fix it, and it tries again. There are at most **3 tries** (1 + `MAX_REPAIR_ATTEMPTS` = 2), then SchemaMind stops and reports the error. In Mistral mode the model can read an error like `no such column: city` and correct itself. In template mode the same SQL would come back, so a repair can't help there.

### B7 · The reply

```json title="what /ask sends back (real shape and values, template mode)"
{"question": "How many orders from Pune?",
 "sql": "SELECT COUNT(*) AS count FROM orders o JOIN customers c ...",
 "ok": true, "error": null, "columns": ["count"], "rows": [[22]],
 "attempts": 1, "tables_used": ["orders", "customers", "payments"],
 "used_full_schema": false, "latency_ms": 12.4}
```

`tables_used` and `latency_ms` above are examples. Every answer comes **with its SQL**, so anyone who knows SQL can check how the number was produced.

## 2.5 One question, from start to finish (real output)

Question: *"How many orders from Pune?"*, in template mode.

| Step | Result |
|---|---|
| Tidied question | `how many orders from pune` |
| Shape that matches the whole question | *how many orders from/in city* |
| SQL | the query below |
| Validator | one statement, a `Select`, no writes inside: OK |
| Executor | read-only, finished in milliseconds |
| Answer | `count = 22` |

```sql title="the SQL that template mode wrote (real)"
SELECT COUNT(*) AS count
FROM orders o JOIN customers c ON c.customer_id = o.customer_id
WHERE c.city = 'Pune';
```

Before session 5, the same question returned **150**, the total of all orders: "how many orders" matched first, and "from Pune" was ignored. The SQL was valid, so no safety layer noticed.

## 2.6 How it is measured and tested

**Tests:** 52, run with `pytest`, offline, in a few seconds. They build their own copy of the database and never load MiniLM. Since session 6, GitHub runs them after every push, on Python 3.11 and 3.14 (see 3.3).

| Test file | What it checks | Tests |
|---|---|---|
| `test_validate.py` | read queries pass; a second statement, writes, `PRAGMA`, `ATTACH`, `VACUUM` are refused | 23 |
| `test_executor.py` | writes refused by the read-only file; runaway queries stopped at the time limit; row limit | 8 |
| `test_templates.py` | each shape gives the right answer; the five old wrong answers; partial matches refused; one definition of revenue | 19 |
| `test_agent_safety.py` | end to end: an injected `DROP` is refused, the loop gives up, all 40 customers are still there | 2 |

**Evaluation** (`eval/run_eval.py`) measures **execution accuracy**: you write questions together with the SQL you consider correct (the **gold** SQL), and it compares the **rows** SchemaMind returns with the gold rows, ignoring their order. It runs everything twice, with the 3 retrieved tables and with all tables, to see whether retrieval helps. It needs Mistral mode, because template mode would score the same either way. On 5 tables the two will probably be close; that's the honest result to expect.

## 2.7 What we changed, and what we tried

| Session | Change | Why it matters |
|---|---|---|
| 1 | Every library fixed to a tested version | the same install everywhere |
| 4 | The validator checks every statement | a `DROP` hidden behind a `SELECT` was blocked only by luck, on newer sqlglot versions |
| 4 | A real 5-second limit | `timeout=10` only waited for locked files; endless queries ran forever |
| 4 | `INTERSECT` and `EXCEPT` allowed | they are reads but were refused; "customers who never ordered" is an `EXCEPT` |
| 4 | The first 33 tests | including the attacks above |
| 5 | Template mode needs the whole question to match | five valid-but-wrong answers fixed |
| 5 | One definition of revenue | "revenue by category" and "by city" now agree with total payments, 4,791,200 |
| 6 | The tests run on GitHub after every push (CI) | a change that breaks something shows a red cross before it is merged |

**What we tried and found.** The hidden second statement came from `parse_one()`, which in sqlglot 26–28 looked only at the first statement; the new check was tested on sqlglot 26, 27, 28, 29 and 30. The time limit was found by writing a recursive query that never ends and watching it keep running. The five wrong template answers were found by asking natural questions and comparing with SQL written by hand: *how many orders from Pune* (150, not 22), *Revenue by Category* (grouped by city), *orders in the last month* (searched for a city called "The"), *top 3 customers by orders* (ranked by money), *how many cancelled orders* (listed rows instead of a count).

:::honest Still missing
No accuracy numbers for Mistral mode yet: they need an API key and a set of questions with gold SQL. No per-user permissions, and no clarifying questions for ambiguous words like "best".
:::

## 2.8 Questions and answers

:::qa How does it work?
Q: How does SchemaMind know which tables a question needs?
At startup it writes a short card for every table (columns, keys, two sample rows) and turns each card into numbers with MiniLM. The question is turned into numbers the same way, and the 3 most similar cards are picked.

Q: How does it stop a `DROP TABLE`?
The validator parses the SQL into a tree and refuses anything that isn't a single read query. If something ever got past it, the database file is open read-only, so SQLite refuses any write. The prompt also forbids writes, but that's a request, not a control.

Q: How does it stop a query that would run forever?
SQLite calls a small function every 10,000 steps of work. The function checks the clock and, after 5 seconds, tells SQLite to stop. The query ends with "interrupted", which SchemaMind turns into a clear message.

Q: How does the repair loop work?
If the SQL fails a check or the database returns an error, the error text and the failed SQL go back to the SQL writer to fix. It gets up to two more tries; after three failures it stops and reports the error.

Q: How does template mode turn a question into SQL?
It lower-cases the question and removes openings like "show me" and the question mark. Then it tries a fixed list of patterns, most specific first. A pattern must match the whole question; its blanks (a city, a status, a number) are filled into ready-made SQL. If nothing matches completely, it refuses.

Q: How does a JOIN answer "orders from Pune"?
The city is stored in `customers` and the orders in `orders`. Join them on `customer_id`, keep the rows where the city is Pune, and count them: 22.
:::

:::qa Why was it built this way?
Q: Why retrieve tables instead of sending the whole schema?
With 5 tables you could send everything. A real company has hundreds of tables, which don't fit in a prompt and would confuse the model. Picking the relevant ones is the technique the project shows; the evaluation is built to measure whether it helps.

Q: Why parse the SQL instead of searching for words like DROP?
Word searches are easy to fool and easy to get wrong: a column named `dropped_at` would be blocked, while tricks with comments or spacing might slip through. A parser understands the structure, so it can count statements and check their type reliably.

Q: Why have both a validator and a read-only connection?
Because any single check can have a bug, and ours did (the hidden second statement). With two independent layers, a mistake in one is caught by the other. The read-only file is enforced by SQLite itself, so no trick against the parser can make it write.

Q: Why show the SQL with every answer?
A wrong JOIN gives a believable number, not an error. Showing the SQL lets a person check how the answer was produced.

Q: Why a 5-second limit and only 200 rows?
On this database a normal query takes milliseconds, so anything past 5 seconds is a runaway. Answers are read by people, so 200 rows is plenty. Both are settings that a bigger database could raise.

Q: Why one definition of revenue?
Two templates computed "revenue" from different tables and disagreed by 631,600 (5,422,800 vs 4,791,200), because one counted cancelled orders. Defining revenue once, as items in orders that weren't cancelled, makes every answer consistent. Real companies call such shared definitions a **semantic layer**.
:::

:::qa What if…?
Q: What if the LLM writes valid SQL that answers the wrong question?
The safety layers won't notice, because nothing unsafe happened. That's why the SQL is shown, why the evaluation compares results against gold SQL, and why template mode refuses questions it only partly understands. A next step would be asking a clarifying question when a word is ambiguous.

Q: What if the database had 500 tables?
That's what retrieval is for: only the top few cards go to the model. I'd also add the tables needed for joins by following foreign keys, write good table descriptions, and measure whether retrieval picks the tables that the gold SQL uses.

Q: What if a user asks for data they shouldn't see, like salaries?
Today every user can read every table. In a real company I'd connect with a database user that may read only allowed tables or columns, filter rows per user (row-level security), and hide personal data.

Q: What if Mistral is down or slow?
The request fails after its 60-second timeout and the API returns an error. Next steps: retry with a growing wait, fall back to template mode for the shapes it knows, and show a clear message.

Q: What if the question is ambiguous, like "best customers"?
"Best" could mean most money or most orders. Template mode knows only "by spend" and "by orders", so it refuses plain "best". An LLM would guess; a better system would ask which one you mean.

Q: What if someone types SQL instead of a question?
In template mode it matches no shape and is refused. In Mistral mode the model might copy it, but it still has to pass the validator and run on the read-only file.
:::

:::qa What more could you add?
Q: What would you add next?
1) A set of questions with gold SQL, and accuracy numbers for Mistral mode. 2) Better error handling for the LLM: retries and a clear message. 3) A glossary of business words ("revenue", "active customer") given to the model. 4) Clarifying questions. 5) Per-user permissions.

Q: How would you measure SchemaMind properly?
Write 15–20 questions with the SQL you consider correct. Run each through SchemaMind, run the gold SQL, and compare the rows, ignoring order: that's execution accuracy. Do it with retrieved tables and with all tables to see whether retrieval helps.

Q: What is self-consistency, and would it help?
Generate several SQL queries for the same question, run them all, and keep the answer most of them agree on. It catches some one-off mistakes, at the cost of more LLM calls.
:::

:::qa Why not something else?
Q: Why not a list of banned words?
It blocks harmless queries and misses tricky ones. A parser works on structure, so it can count statements and check their type reliably.

Q: Why not let the LLM run SQL on a normal connection and trust the prompt?
A prompt is a request, not a control: the model can misunderstand, or be tricked by the question. Safety has to be enforced by code and by the database itself.

Q: Why not a longer limit, like 60 seconds?
Every running query ties up the server, and minute-long runaways would make the app feel broken. 5 seconds is generous for this database, and it's a setting (`SCHEMAMIND_QUERY_TIMEOUT`) if a bigger database needs more.

Q: Why not LangChain's SQL agent?
It would work, but it hides the parts I wanted to build and explain: table retrieval, the validator, the limits and the repair loop. Building them myself means I can test each one.
:::

:::qa What did you try, and what did you learn?
Q: Tell me about the hidden second statement.
The validator used `parse_one()`, which in older sqlglot versions read only the first statement, so a `DROP` after a `SELECT` went unchecked. It was safe on newer versions only by luck. I changed it to parse every statement and allow exactly one, and tested it on sqlglot 26 to 30.

Q: How did you find that the timeout didn't work?
I wrote a recursive query that never ends and ran it: it kept running. `timeout=10` only limits waiting for a locked file. I added SQLite's progress handler with a deadline, and a test proves that such a query stops at the limit.

Q: What were the five wrong template answers?
Template mode took the first pattern that matched part of a question. "How many orders from Pune" gave 150 instead of 22, "Revenue by Category" grouped by city, "orders in the last month" searched for a city called "The", "top 3 customers by orders" ranked by money, and "how many cancelled orders" listed rows. Now the whole question must match, specific shapes come first, and everything else is refused.

Q: What was wrong with INTERSECT and EXCEPT?
They are read queries ("customers who never ordered" is all customers EXCEPT those with orders), but the validator refused them because it accepted only `SELECT` and `UNION`. Now any combination of `SELECT`s is allowed.

Q: What did you learn?
That safe and correct are different problems: three safety layers can't stop a believable wrong number. And that every claim in a README needs a test that tries to break it: the injection check worked only by luck, and template mode, marked "tested, works", gave wrong answers to five natural questions.
:::
