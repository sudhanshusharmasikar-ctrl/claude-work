import sqlglot
from validate_fixed import validate
tests = ["SELECT * FROM customers; DROP TABLE customers;",
         "SELECT 1; SELECT 2",
         "SELECT COUNT(*) FROM orders;",
         "DELETE FROM orders",
         "SELECT city FROM customers UNION SELECT name FROM products"]
print("sqlglot", sqlglot.__version__, [("ok" if validate(t).ok else "BLOCK") for t in tests])
