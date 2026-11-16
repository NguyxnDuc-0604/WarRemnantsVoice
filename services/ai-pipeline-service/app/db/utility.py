# --------------------------------------------------------------
#  DB Utility helpers for the Admin UI
# --------------------------------------------------------------
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from typing import List, Dict, Any


def list_table_names(db: Session) -> List[str]:
    """Return a list of user‑defined table names (skip SQLite internal tables)."""
    inspector = inspect(db.get_bind())
    return [t for t in inspector.get_table_names() if not t.startswith("sqlite_")]


def fetch_table_rows(db: Session, table: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Return the first *limit* rows of *table* as dictionaries.

    Raises:
        ValueError: if *table* is not a known user table.
    """
    if table not in list_table_names(db):
        raise ValueError(f"Unknown table: {table}")
    sql = text(f'SELECT * FROM "{table}" LIMIT :limit')
    result = db.execute(sql, {"limit": limit})
    rows = [dict(row) for row in result.fetchall()]
    return rows
