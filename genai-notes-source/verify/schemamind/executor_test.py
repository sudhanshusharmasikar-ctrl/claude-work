"""Run from a copy of the schemamind repo: python executor_test.py"""
import sqlite3, sys, time
sys.path.insert(0, ".")
from app.executor import execute
from app.validate import validate

for sql in ["SELECT * FROM customers; DROP TABLE customers;",
            "DROP TABLE customers;",
            "UPDATE orders SET status='x';",
            "DELETE FROM orders;",
            "SELECT COUNT(*) FROM orders"]:
    r = execute(sql)
    print(sql)
    print("   ->", f"ok=True rows={r.rows}" if r.ok else f"ok=False  {r.error}")

runaway = ("WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM c) "
           "SELECT COUNT(*) FROM c")
print("validator on the never-ending CTE ->",
      "ALLOWED" if validate(runaway).ok else "blocked")

# the fix: a real time limit, using SQLite's progress handler
conn = sqlite3.connect("file:data/shop.db?mode=ro", uri=True)
deadline = time.time() + 2.0
conn.set_progress_handler(lambda: 1 if time.time() > deadline else 0, 100_000)
t0 = time.time()
try:
    conn.execute(runaway).fetchall()
except sqlite3.OperationalError as e:
    print(f"with the progress handler: stopped after {time.time() - t0:.1f}s ({e})")
