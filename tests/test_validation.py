"""Tests for input validation."""
import pytest
from services.offer_service import validate_purchase_inputs

def test_valid_inputs():
    valid, err, amt = validate_purchase_inputs("Amazon", "Electronics", 8999)
    assert valid is True
    assert err is None
    assert amt == 8999.0

def test_empty_merchant():
    valid, err, _ = validate_purchase_inputs("   ", "Electronics", 1000)
    assert valid is False
    assert "Merchant name is required" in err

def test_empty_category():
    valid, err, _ = validate_purchase_inputs("Amazon", "", 1000)
    assert valid is False
    assert "Category is required" in err

def test_non_positive_amount():
    valid, err, _ = validate_purchase_inputs("Amazon", "Electronics", 0)
    assert valid is False
    assert "greater than zero" in err

    valid, err, _ = validate_purchase_inputs("Amazon", "Electronics", -50)
    assert valid is False
    assert "greater than zero" in err

def test_excessive_amount():
    valid, err, _ = validate_purchase_inputs("Amazon", "Electronics", 99999999)
    assert valid is False
    assert "exceeds maximum demo limit" in err

def test_invalid_amount_type():
    valid, err, _ = validate_purchase_inputs("Amazon", "Electronics", "not_a_number")
    assert valid is False
    assert "valid numeric value" in err
