:::chapter 11 | Graph Databases and Cypher | Lectures 15–16 · whiteboards · Good to know
- The **LinkedIn problem**: friends of friends of friends
- Why **SQL joins** get expensive for relationship questions
- **Index-free adjacency**: following pointers instead of joining tables
- How **Neo4j** stores nodes and relationships (15-byte and 34-byte records)
- The graph data model: **nodes, labels, relationships, properties**
- **Cypher** by example: `MATCH`, `WHERE`, `RETURN`, `MERGE`, paths
- When to choose a graph DB — and when not to
:::

Chapter 9 showed questions that normal RAG can't answer because the answer is a **chain of relationships**. Before Graph RAG (next chapter), we need the tool built for chains: the **graph database**. Rohit explains it from the storage level up — very C++-friendly.

## 11.1 The LinkedIn problem %%GOOD%%

Rohit's whiteboard: you're building LinkedIn with lakhs of users. Each user has ~500 connections.

- "Who are Rohit's friends?" → 500 people.
- "Who are the friends of Rohit's friends?" → 500 × 500 = **2.5 lakh** people.
- "Friends of friends of friends?" → 2.5 lakh × 500 = **12.5 crore** paths.
- "Which of my friends' friends work at **Google**?" — a real product question (and a recruiting feature!).

These are **relationship** questions. The data itself (name, age, email, company) is simple; the value is in the **connections**.

## 11.2 Doing it in SQL %%GOOD%%

The usual SQL design: a `users` table and a `friendships(user_id, friend_id)` table. Friends-of-friends needs a **self-join**:

```sql title="friends of friends in SQL"
SELECT DISTINCT f2.friend_id
FROM friendships f1
JOIN friendships f2 ON f2.user_id = f1.friend_id
WHERE f1.user_id = 'rohit';
```

With a B-tree index on `user_id`, each lookup costs **O(log N)**, where N is the size of the **whole** friendships table. Rohit's rough count for three hops:

`log N  +  500 · log N  +  2.5 lakh · log N`

Every extra hop multiplies the number of index lookups, and N keeps growing as the whole network grows — even though you only care about **your** neighbourhood. Deep or variable-length questions ("how is A connected to K?") become many joins that are slow and hard to write.

## 11.3 The graph idea: store the connections directly %%GOOD%%

Instead of looking friends up in a big table every time, store **each person with direct references to their neighbours** — an **adjacency list**.

:::cpp You already know this: `vector<vector<int>> adj`
In DSA you store a graph as `adj[u] = {v1, v2, …}`. Visiting a neighbour is just reading the next element — no searching. BFS/DFS over "friends of friends" touches only the nodes it reaches. A graph database is this adjacency idea, made persistent, transactional and queryable.
:::

This is called **index-free adjacency**: following a relationship is a direct **pointer jump**, roughly O(1) per hop. The cost of a query depends on **how much of the graph you touch**, not on the total size of the database.

[[fig:sql-vs-graph|SQL looks up every hop in a big index; a graph database jumps straight from a node to its neighbours.]]

## 11.4 How Neo4j stores a graph (Lecture 16) %%GOOD%%

Rohit's Lecture 16 explains the classic Neo4j storage format — and it's pure systems programming:

- **Fixed-size records.** Every **node** record is **15 bytes**; every **relationship** record is **34 bytes**; properties live in separate property records.
- Because the size is fixed, the record for id *i* is at **`base address + i × record size`** — an **O(1)** jump, exactly like indexing an array.
- A **node record** stores a pointer to its **first relationship** and its **first property**.
- A **relationship record** stores its start node, end node, type, and pointers to the **next relationship** of each of its two nodes — so each node's relationships form a **linked list**.
- To find the **starting** node by a value ("the user named Rohit") you still need an **index** (hash → O(1), or B+ tree → O(log n)). After that, traversal is pointer chasing.

[[fig:neo4j-records|Fixed-size records: the node id is an array index, and each node's relationships form a linked chain. (Numbers from the classic Neo4j record format taught in the lecture.)]]

:::cpp Array of structs + linked lists
`NodeRecord nodes[N]` where `nodes[i]` holds `firstRel`; `RelRecord rels[M]` where each record holds `startNode, endNode, type, nextRelOfStart, nextRelOfEnd`. Finding all of Rohit's relationships = start at `nodes[rohit].firstRel` and follow `next` pointers — a linked-list walk you've written many times.
:::

(Newer Neo4j versions also offer a different "block" storage layout; the principle — direct references instead of join lookups — stays the same.)

## 11.5 The graph data model %%MUST%%

| Part | Meaning | Movie example |
|---|---|---|
| **Node** | A thing | Inception, Christopher Nolan, Leonardo DiCaprio |
| **Label** | The node's type (class) | `:Movie`, `:Director`, `:Actor` |
| **Relationship** | A typed, directed connection | `(Nolan)-[:DIRECTED]->(Inception)` |
| **Property** | Key–value data on nodes or relationships | `{ title: "Inception", year: 2010 }` |

Rohit's rule from Lecture 17: **node labels are classes, properties are data, relationships are facts** ("truths, not actions").

## 11.6 Cypher by example %%MUST%%

**Cypher** is Neo4j's query language. Patterns are drawn in ASCII art: `(node)` in round brackets, `-[:REL]->` as arrows.

```cypher title="create data (MERGE = create only if it doesn't exist)"
MERGE (d:Director {name: "Christopher Nolan"})
MERGE (m:Movie {title: "Inception"})
SET m.year = 2010
MERGE (d)-[:DIRECTED]->(m)
```

```cypher title="movies directed by Nolan"
MATCH (d:Director {name: "Christopher Nolan"})-[:DIRECTED]->(m:Movie)
RETURN m.title, m.year
ORDER BY m.year
```

```cypher title="actors who worked in Nolan movies that won an Oscar"
MATCH (d:Director)-[:DIRECTED]->(m:Movie)
MATCH (m)-[:WON]->(a:Award)
MATCH (actor:Actor)-[:ACTED_IN]->(m)
WHERE d.name = "Christopher Nolan" AND a.name = "Oscar"
RETURN DISTINCT actor.name
```

```cypher title="friends of friends, and which of them work at Google"
MATCH (me:User {name: "Rohit"})-[:FRIEND]->()-[:FRIEND]->(fof:User)
WHERE fof <> me
RETURN DISTINCT fof.name;

MATCH (me:User {name: "Rohit"})-[:FRIEND*1..2]-(p:User)
      -[:WORKS_AT]->(:Company {name: "Google"})
RETURN DISTINCT p.name;
```

```cypher title="how are two people connected?"
MATCH (a:Actor {name: "Leonardo DiCaprio"}),
      (b:Director {name: "Christopher Nolan"}),
      path = shortestPath((a)-[*..6]-(b))
RETURN [n IN nodes(path) | coalesce(n.name, n.title)] AS chain
```

The pieces you'll see in the Graph RAG code:

| Clause | Job |
|---|---|
| `MATCH` | Find a pattern |
| `OPTIONAL MATCH` | Like a LEFT JOIN — keep the row even if this part has no match |
| `WHERE` | Filter (`=`, `<>`, `>`, `CONTAINS`, `STARTS WITH`, `AND/OR/NOT`) |
| `RETURN` | What to output; `DISTINCT`, `count()`, `collect()` (make a list) |
| `ORDER BY`, `LIMIT` | Sort and cap |
| `MERGE` vs `CREATE` | `MERGE` finds-or-creates (no duplicates); `CREATE` always creates |
| `$name` | **Parameter** — the value is sent separately, never pasted into the query string (prevents injection, allows query caching) |
| `[*1..3]` | Variable-length path (1 to 3 hops) |
| `CREATE INDEX … FOR (m:Movie) ON (m.title)` | Speed up finding start nodes (and `MERGE`) |

:::mistake `CREATE` makes duplicates
Insert "Zendaya" for two movies with `CREATE (:Actor {name: "Zendaya"})` and you get **two** Zendaya nodes — now "movies with Zendaya" misses half of them. Use `MERGE`, and add an index (or a **uniqueness constraint**) on the property you merge on, or every `MERGE` scans all nodes.
:::

## 11.7 When should you use a graph database? %%GOOD%%

| Use a graph DB when… | Stay with SQL when… |
|---|---|
| Questions follow **relationships**, often several hops (social networks, fraud rings, recommendations) | Questions are **aggregations** over rows (revenue by month) |
| The path length varies ("how are A and B connected?") | The schema is stable and tabular |
| Relationships have their own properties (since, weight, role) | You need mature reporting/BI tools and SQL skills |
| Knowledge graphs, access-control graphs, supply chains | Heavy transactional workloads (payments, orders) |

Graph databases you can name: **Neo4j** (most popular, Cypher), Amazon Neptune, Memgraph, TigerGraph, ArangoDB. Many companies use **both**: SQL for transactions, a graph for relationship queries.

:::remember
- Relationship questions (friends of friends, fraud chains) are expensive in SQL: every hop is an index lookup over the **whole** table.
- Graph DBs use **index-free adjacency**: each node points to its relationships → O(1) per hop; cost ∝ part of the graph touched.
- Neo4j (classic format): **15-byte node** and **34-byte relationship** records; address = base + id × size; relationships form **linked lists**; an index finds the start node.
- Model: **nodes** (labels = classes), **relationships** (typed, directed facts), **properties** (data).
- Cypher: `MATCH` pattern → `WHERE` filter → `RETURN` projection; `MERGE` avoids duplicates; always use `$parameters`.
:::

:::quiz
1. Why does a 3-hop friends query in SQL get slower as the whole network grows, even if your own neighbourhood doesn't?
2. What is index-free adjacency?
3. Node id 7, node records of 15 bytes, base address 1000. Where is its record?
4. What is the difference between `MERGE` and `CREATE`?
5. Why use `$name` parameters instead of building the Cypher string with the value?
:::

:::answer
1. Each hop is an index lookup costing O(log N) over the entire friendships table, and the number of lookups multiplies per hop.
2. Each node stores direct references to its relationships, so moving to a neighbour is a pointer jump, not an index search.
3. 1000 + 7 × 15 = 1105.
4. `MERGE` matches an existing pattern or creates it if missing (no duplicates); `CREATE` always creates new nodes/relationships.
5. Safety (no injection — the value is never parsed as Cypher) and speed (the database can reuse the query plan).
:::

:::qa Interview questions — graph databases
Q: When would you choose a graph database over a relational one?
When the important questions are about relationships and paths — multi-hop, variable-length traversals like social connections, fraud rings, recommendations or knowledge graphs. Relational databases handle them with repeated joins whose cost grows with table size; graph databases traverse direct references, so cost depends on the part of the graph touched.

Q: What is index-free adjacency?
A storage design where each node physically references its adjacent relationships, so traversal is pointer chasing (roughly constant time per hop) instead of index lookups. In Neo4j's classic format, fixed-size node and relationship records make each record reachable by id arithmetic, and a node's relationships form a linked list.

Q: What does MERGE do and why does it matter for building a knowledge graph?
It matches a pattern or creates it if it doesn't exist, so repeated entities (the same actor in many movies) become one node. Without it you get duplicates and broken queries. It should be backed by an index or uniqueness constraint so it doesn't scan all nodes.

Q: Write a Cypher query for "movies directed by Christopher Nolan".
`MATCH (d:Director {name: $name})-[:DIRECTED]->(m:Movie) RETURN m.title, m.year` with `$name = "Christopher Nolan"` passed as a parameter.
:::
