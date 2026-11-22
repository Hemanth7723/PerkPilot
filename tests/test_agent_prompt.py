"""Tests for Gemini-only agent prompt workflow."""
import pytest
from unittest.mock import MagicMock, patch
from agent import run_agent_on_prompt
from config import get_settings

def test_missing_api_key_returns_error(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    res = run_agent_on_prompt("Buy shoes for ₹2000 on Flipkart")
    assert res["tool_result"]["success"] is False
    assert "GOOGLE_API_KEY is not configured" in res["agent_response"]

def test_gemini_agent_with_configured_model():
    settings = get_settings()
    if not settings.google_api_key:
        pytest.skip("GOOGLE_API_KEY not configured for live test")

    prompt = "I want to buy headphones for ₹8,999 on Amazon. Which card should I use?"
    res = run_agent_on_prompt(prompt)
    assert "Gemini" in res["agent_mode"]
    assert res["tool_result"]["success"] is True
    assert res["tool_result"]["best_option"] is not None
    assert "SBI SimplyCLICK (Demo)" in res["tool_result"]["best_option"]["card_name"]
    assert len(res["agent_response"]) > 20
