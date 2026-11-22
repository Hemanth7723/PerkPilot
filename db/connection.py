"""Database connection helper with foreign key enforcement."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from config import get_settings

def _resolve_db_path(db_path: str | None = None) -> Path:
    if db_path is None:
        db_path = get_settings().db_path
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

@contextmanager
def get_connection(db_path: str | None = None) -> Generator[sqlite3.Connection, None, None]:
    path = _resolve_db_path(db_path)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
