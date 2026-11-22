"""Tests for offer service eligibility, caps, and ranking."""
import pytest
from pathlib import Path
from db.init_db import initialize_database
from db.seed_db import seed_if_empty
from services.offer_service import analyze_purchase

@pytest.fixture
def test_db(tmp_path: Path):
    db_file = str(tmp_path / "service_test.db")
    initialize_database(db_file)
    seed_if_empty(db_file)
    return db_file

def test_analyze_purchase_amazon_electronics(test_db):
    res = analyze_purchase("Amazon", "Electronics", 8999, db_path=test_db)
    assert res["success"] is True
    assert res["status"] == "ok"
    assert res["best_option"] is not None
    assert len(res["eligible_offers"]) > 0

    # Ensure best option has highest benefit
    best = res["best_option"]
    for alt in res["eligible_offers"][1:]:
        assert float(best["benefit_amount"]) >= float(alt["benefit_amount"])

def test_analyze_purchase_minimum_spend_exclusion(test_db):
    # Small spend of ₹100: offers with min_spend ₹500/₹1000 should be excluded
    res = analyze_purchase("Swiggy", "Food & Dining", 100, db_path=test_db)
    assert res["success"] is True
    # Ineligible offers list should contain reasons
    assert any("Minimum purchase amount" in inelig["reason"] for inelig in res["ineligible_offers"])

def test_analyze_purchase_no_match_fallback(test_db):
    # Unknown merchant with obscure category still matches generic wildcard card offers
    res = analyze_purchase("UnknownLocalShop99", "RandomCategory", 500, db_path=test_db)
    assert res["success"] is True
    # Generic cards (like ICICI 1% or Axis 1.5%) should match
    assert len(res["eligible_offers"]) > 0
