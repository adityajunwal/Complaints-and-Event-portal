"""
migrate.py — Safe schema migrations for community.db

Run with: python migrate.py

- Checks if columns already exist before adding them (idempotent / safe to re-run)
- Add new migrations to the MIGRATIONS list in order
"""

import sqlite3

DB_PATH = "community.db"


def get_columns(cursor, table: str) -> set:
    """Return the set of existing column names for a table."""
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def add_column_if_missing(cursor, table: str, column: str, col_type: str, default=None):
    """ALTER TABLE only if the column doesn't already exist."""
    if column not in get_columns(cursor, table):
        default_clause = f" DEFAULT {default}" if default is not None else ""
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}{default_clause}")
        print(f"  ✅ Added '{column}' to '{table}'")
    else:
        print(f"  ⏭️  '{column}' already exists in '{table}', skipping")


# ── MIGRATIONS (add new ones at the bottom) ───────────────────────────────────

def m001_add_is_admin(cursor):
    """Add is_admin flag to users table."""
    add_column_if_missing(cursor, "users", "is_admin", "BOOLEAN", default=0)


def m002_add_resolve_reason(cursor):
    """Add resolve_reason to complaints table."""
    add_column_if_missing(cursor, "complaints", "resolve_reason", "VARCHAR")


MIGRATIONS = [
    ("m001 — add users.is_admin",             m001_add_is_admin),
    ("m002 — add complaints.resolve_reason",  m002_add_resolve_reason),
]

# ── RUNNER ────────────────────────────────────────────────────────────────────

def run():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"\n🗄️  Running migrations on '{DB_PATH}'\n")

    for name, migration_fn in MIGRATIONS:
        print(f"▶  {name}")
        migration_fn(cursor)

    conn.commit()
    conn.close()
    print("\n✅ All migrations complete.\n")


if __name__ == "__main__":
    run()
