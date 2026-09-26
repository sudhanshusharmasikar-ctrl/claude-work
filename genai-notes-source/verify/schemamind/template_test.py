"""Run from a copy of the schemamind repo: template mode needs no model."""
import sqlite3, sys
sys.path.insert(0, ".")
from app.sql_generate import generate_sql
from app.executor import execute

def short(s, n=64):
    return s if len(s) <= n else s[:n - 1] + "…"

for q in ["How many orders from Pune?", "Revenue by Category",
          "Show orders in the last month"]:
    sql = generate_sql(q, [], mode="template")
    r = execute(sql)
    print(f"Q: {q}\n   SQL : {short(sql)}\n   rows: {short(str(r.rows[:2]))}")

db = sqlite3.connect("file:data/shop.db?mode=ro", uri=True)
one = lambda s: db.execute(s).fetchone()[0]
print("truth: orders from Pune =", one(
    "SELECT COUNT(*) FROM orders o JOIN customers c "
    "ON c.customer_id = o.customer_id WHERE c.city = 'Pune'"))
print("revenue = SUM(payments.amount)          =", one(
    "SELECT SUM(amount) FROM payments"))
print("revenue = SUM(quantity * unit_price)    =", one(
    "SELECT SUM(quantity * unit_price) FROM order_items"))
