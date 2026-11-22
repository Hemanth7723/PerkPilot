"""Tests for natural language prompt entity extraction and agent workflow."""
import pytest
from agent import extract_purchase_details_heuristically, run_agent_on_prompt

def test_extract_amazon_headphones():
    prompt = "I'm buying Sony headphones for ₹8,999 on Amazon. Which card should I use?"
    merchant, category, amount = extract_purchase_details_heuristically(prompt)
    assert merchant == "Amazon"
    assert category == "Electronics"
    assert amount == 8999.0

def test_extract_swiggy_food():
    prompt = "Ordering food from Swiggy for 650 rupees"
    merchant, category, amount = extract_purchase_details_heuristically(prompt)
    assert merchant == "Swiggy"
    assert category == "Food & Dining"
    assert amount == 650.0

def test_extract_flipkart_phone():
    prompt = "Planning to buy a new smartphone on Flipkart for Rs. 15,000"
    merchant, category, amount = extract_purchase_details_heuristically(prompt)
    assert merchant == "Flipkart"
    assert category == "Electronics"
    assert amount == 15000.0

def test_run_agent_on_prompt_end_to_end():
    prompt = "I am purchasing headphones for ₹8,999 on Amazon."
    res = run_agent_on_prompt(prompt)
    assert res["tool_result"]["success"] is True
    assert res["tool_result"]["status"] == "ok"
    assert res["tool_result"]["best_option"] is not None
    assert "SBI SimplyCLICK (Demo)" in res["tool_result"]["best_option"]["card_name"]
    assert res["extracted_params"]["merchant"] == "Amazon"
    assert res["extracted_params"]["category"] == "Electronics"
    assert res["extracted_params"]["amount"] == 8999.0
