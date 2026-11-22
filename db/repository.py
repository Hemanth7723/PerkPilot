"""Repository layer for parameterized SQLite queries."""
from db.connection import get_connection

def find_candidate_offers(merchant: str, category: str, db_path: str | None = None) -> list[dict]:
    """
    Retrieve active offers matching:
    - exact merchant or wildcard '*'
    - exact category or wildcard '*'
    for active cards.
    """
    m_clean = merchant.strip().lower()
    c_clean = category.strip().lower()

    query = """
    SELECT 
        c.id AS card_id,
        c.card_name,
        c.issuer,
        o.id AS offer_id,
        o.merchant,
        o.category,
        o.benefit_type,
        o.rate_percent,
        o.minimum_spend,
        o.cap_amount,
        o.description
    FROM offers o
    JOIN cards c ON o.card_id = c.id
    WHERE o.active = 1
      AND c.active = 1
      AND (LOWER(o.merchant) = ? OR o.merchant = '*')
      AND (LOWER(o.category) = ? OR o.category = '*')
    """

    with get_connection(db_path) as conn:
        rows = conn.execute(query, (m_clean, c_clean)).fetchall()
        return [dict(row) for row in rows]

def has_seeded_offers(db_path: str | None = None) -> bool:
    """Check if the offers table already has records."""
    query = "SELECT COUNT(*) as count FROM offers;"
    with get_connection(db_path) as conn:
        row = conn.execute(query).fetchone()
        return bool(row and row["count"] > 0)

def get_all_cards(db_path: str | None = None) -> list[dict]:
    """List all cards in the database."""
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM cards WHERE active = 1 ORDER BY card_name;").fetchall()
        return [dict(row) for row in rows]

def get_all_offers(db_path: str | None = None) -> list[dict]:
    """List all offers with card details."""
    query = """
    SELECT o.*, c.card_name, c.issuer
    FROM offers o
    JOIN cards c ON o.card_id = c.id
    WHERE o.active = 1 AND c.active = 1
    ORDER BY c.card_name;
    """
    with get_connection(db_path) as conn:
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
