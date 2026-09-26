from dataclasses import dataclass

import sqlglot
from sqlglot import exp

FORBIDDEN = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create,
             exp.Alter, exp.TruncateTable)


@dataclass
class ValidationResult:
    ok: bool
    reason: str | None = None
    parsed: object | None = None


def validate(sql: str, dialect: str = "sqlite") -> ValidationResult:
    try:
        # parse() returns EVERY statement; parse_one() may silently keep only the first
        statements = [s for s in sqlglot.parse(sql, dialect=dialect) if s is not None]
    except Exception as e:
        return ValidationResult(False, f"SQL does not parse: {e}")
    if len(statements) != 1:
        return ValidationResult(False, f"Exactly one statement allowed, got {len(statements)}.")
    parsed = statements[0]
    if not isinstance(parsed, (exp.Select, exp.Union)):
        return ValidationResult(False, f"Only SELECT queries are allowed, got {type(parsed).__name__}.")
    for node in parsed.walk():
        n = node[0] if isinstance(node, tuple) else node
        if isinstance(n, FORBIDDEN):
            return ValidationResult(False, "Write operation found nested inside query.")
    return ValidationResult(True, parsed=parsed)
