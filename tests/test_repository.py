"""Tests for repository queries using an isolated temporary SQLite database."""
import pytest
import sqlite3
from pathlib import Path
from db.init_db import initialize_database
from db.seed_db import seed_if_empty
from db.repository import find_candidate_offers, has_seeded_offers

@pytest.fixture
def temp_db(tmp_path: Path):
    db_file = str(tmp_path / "test_perkpilot.db")
    initialize_database(db_file)
    seed_if_empty(db_file)
    return db_file

def test_seed_idempotency(temp_db):
    assert has_seeded_offers(temp_db) is True
    # Calling seed_if_empty again should return False (no duplicate inserts)
    assert seed_if_empty(temp_db) is False

def test_find_candidate_offers_exact_and_wildcard(temp_db):
    # Searching Amazon and Electronics should match Amazon-specific offers AND wildcard '*' offers
    offers = find_candidate_offers("Amazon", "Electronics", db_path=temp_db)
    assert len(offers) > 0

    merchants = {o["merchant"] for o in offers}
    assert "amazon" in merchants
    assert "*" in merchants

def test_sql_injection_attempt(temp_db):
    # An injection string should be safely treated as a literal merchant name
    injection = "Amazon' OR '1'='1"
    offers = find_candidate_offers(injection, "Electronics", db_path=temp_db)
    # Should only return wildcard '*' offers, not expose arbitrary rows
    for o in offers:
        assert o["merchant"] == "*"
