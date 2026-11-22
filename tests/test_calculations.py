"""Tests for pure financial calculation helpers."""
import pytest
from decimal import Decimal
from services.calculations import calculate_benefit, format_inr, to_decimal

def test_raw_benefit_calculation():
    # 5% of 1000 = 50.00
    res = calculate_benefit(amount=1000, rate_percent=5.0, cap_amount=None, benefit_type="cashback_percent")
    assert res["gross_benefit"] == "50.00"
    assert res["benefit_amount"] == "50.00"
    assert res["cap_amount"] is None
    assert res["effective_price"] is None

def test_cap_limiting():
    # 10% of 8999 = 899.90, cap 500 => 500.00
    res = calculate_benefit(amount=8999, rate_percent=10.0, cap_amount=500.0, benefit_type="cashback_percent")
    assert res["gross_benefit"] == "899.90"
    assert res["benefit_amount"] == "500.00"
    assert res["cap_amount"] == "500.00"
    assert res["effective_price"] is None

def test_instant_discount_effective_price():
    # 5% instant discount on 2000 = 100 => effective price 1900.00
    res = calculate_benefit(amount=2000, rate_percent=5.0, cap_amount=None, benefit_type="instant_discount_percent")
    assert res["gross_benefit"] == "100.00"
    assert res["benefit_amount"] == "100.00"
    assert res["effective_price"] == "1900.00"

def test_rounding_precision():
    # 3.33% of 100 = 3.33
    res = calculate_benefit(amount=100, rate_percent=3.33, cap_amount=None, benefit_type="cashback_percent")
    assert res["benefit_amount"] == "3.33"
