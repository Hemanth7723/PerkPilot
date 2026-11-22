"""Google ADK tool adapter for credit card offer analysis."""
from typing import Any
from services.offer_service import analyze_purchase

def analyze_card_offers(merchant: str, category: str, amount: float) -> dict[str, Any]:
    """
    Analyzes eligible credit card offers from SQLite database for a given purchase.
    
    Args:
        merchant: Name of the merchant or store (e.g. 'Amazon', 'Flipkart', 'Swiggy').
        category: Purchase category (e.g. 'Electronics', 'Food & Dining', 'Grocery', 'Travel').
        amount: Total purchase amount in INR (must be positive).
        
    Returns:
        Structured JSON-compatible dictionary with eligible offers, calculated benefits,
        best recommended card, and conditions.
    """
    return analyze_purchase(merchant=merchant, category=category, amount=amount)
