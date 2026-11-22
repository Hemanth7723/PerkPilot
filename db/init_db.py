"""Database schema initialization."""
from pathlib import Path
from db.connection import get_connection

def initialize_database(db_path: str | None = None) -> None:
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    with get_connection(db_path) as conn:
        conn.executescript(sql)

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
