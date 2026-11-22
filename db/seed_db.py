"""Idempotent seed script with diverse fictional cards and offers."""
from db.connection import get_connection
from db.init_db import initialize_database
from db.repository import has_seeded_offers

CARDS_DATA = [
    {"name": "HDFC Millennia (Demo)", "issuer": "HDFC Bank"},
    {"name": "Axis Flipkart (Demo)", "issuer": "Axis Bank"},
    {"name": "ICICI Amazon Pay (Demo)", "issuer": "ICICI Bank"},
    {"name": "SBI SimplyCLICK (Demo)", "issuer": "SBI Card"},
    {"name": "Standard Chartered Smart (Demo)", "issuer": "Standard Chartered"},
    {"name": "Swiggy HDFC (Demo)", "issuer": "HDFC Bank"},
    {"name": "Amex SmartEarn (Demo)", "issuer": "American Express"},
]

OFFERS_DATA = [
    # HDFC Millennia
    {
        "card_name": "HDFC Millennia (Demo)",
        "merchant": "amazon",
        "category": "*",
        "benefit_type": "cashback_percent",
        "rate_percent": 5.0,
        "minimum_spend": 1000.0,
        "cap_amount": 750.0,
        "description": "5% cashback on Amazon shopping up to ₹750/mo. Min spend ₹1,000."
    },
    {
        "card_name": "HDFC Millennia (Demo)",
        "merchant": "*",
        "category": "food & dining",
        "benefit_type": "cashback_percent",
        "rate_percent": 5.0,
        "minimum_spend": 500.0,
        "cap_amount": 500.0,
        "description": "5% cashback on dining and food delivery. Min spend ₹500."
    },
    {
        "card_name": "HDFC Millennia (Demo)",
        "merchant": "*",
        "category": "*",
        "benefit_type": "cashback_percent",
        "rate_percent": 1.0,
        "minimum_spend": 0.0,
        "cap_amount": None,
        "description": "1% base cashback on all other eligible spends."
    },
    # Axis Flipkart
    {
        "card_name": "Axis Flipkart (Demo)",
        "merchant": "flipkart",
        "category": "*",
        "benefit_type": "instant_discount_percent",
        "rate_percent": 5.0,
        "minimum_spend": 500.0,
        "cap_amount": None,
        "description": "5% instant discount on Flipkart with no upper cap."
    },
    {
        "card_name": "Axis Flipkart (Demo)",
        "merchant": "*",
        "category": "*",
        "benefit_type": "cashback_percent",
        "rate_percent": 1.5,
        "minimum_spend": 0.0,
        "cap_amount": None,
        "description": "1.5% unlimited cashback on all retail spends."
    },
    # ICICI Amazon Pay
    {
        "card_name": "ICICI Amazon Pay (Demo)",
        "merchant": "amazon",
        "category": "*",
        "benefit_type": "cashback_percent",
        "rate_percent": 5.0,
        "minimum_spend": 0.0,
        "cap_amount": None,
        "description": "5% unlimited cashback for Prime members on Amazon purchases."
    },
    {
        "card_name": "ICICI Amazon Pay (Demo)",
        "merchant": "*",
        "category": "*",
        "benefit_type": "cashback_percent",
        "rate_percent": 1.0,
        "minimum_spend": 0.0,
        "cap_amount": None,
        "description": "1% flat unlimited cashback on all other transactions."
    },
    # SBI SimplyCLICK
    {
        "card_name": "SBI SimplyCLICK (Demo)",
        "merchant": "amazon",
        "category": "electronics",
        "benefit_type": "reward_percent",
        "rate_percent": 10.0,
        "minimum_spend": 1000.0,
        "cap_amount": 1000.0,
        "description": "10% equivalent reward points on Amazon Electronics, capped at ₹1,000."
    },
    {
        "card_name": "SBI SimplyCLICK (Demo)",
        "merchant": "*",
        "category": "electronics",
        "benefit_type": "reward_percent",
        "rate_percent": 5.0,
        "minimum_spend": 500.0,
        "cap_amount": 500.0,
        "description": "5% equivalent reward points on all electronics retail."
    },
    # Standard Chartered Smart
    {
        "card_name": "Standard Chartered Smart (Demo)",
        "merchant": "*",
        "category": "*",
        "benefit_type": "cashback_percent",
        "rate_percent": 2.0,
        "minimum_spend": 1000.0,
        "cap_amount": 1000.0,
        "description": "2% flat cashback on all online spends above ₹1,000 up to ₹1,000/mo."
    },
    # Swiggy HDFC
    {
        "card_name": "Swiggy HDFC (Demo)",
        "merchant": "swiggy",
        "category": "*",
        "benefit_type": "instant_discount_percent",
        "rate_percent": 10.0,
        "minimum_spend": 300.0,
        "cap_amount": 300.0,
        "description": "10% instant discount on Swiggy food & Instamart up to ₹300. Min spend ₹300."
    },
    {
        "card_name": "Swiggy HDFC (Demo)",
        "merchant": "*",
        "category": "food & dining",
        "benefit_type": "cashback_percent",
        "rate_percent": 5.0,
        "minimum_spend": 500.0,
        "cap_amount": 500.0,
        "description": "5% cashback on dining spends above ₹500."
    },
    # Amex SmartEarn
    {
        "card_name": "Amex SmartEarn (Demo)",
        "merchant": "zomato",
        "category": "*",
        "benefit_type": "reward_percent",
        "rate_percent": 10.0,
        "minimum_spend": 250.0,
        "cap_amount": 500.0,
        "description": "10% accelerated rewards on Zomato spends up to ₹500 benefit."
    },
    {
        "card_name": "Amex SmartEarn (Demo)",
        "merchant": "*",
        "category": "*",
        "benefit_type": "reward_percent",
        "rate_percent": 1.25,
        "minimum_spend": 0.0,
        "cap_amount": None,
        "description": "1.25% base rewards on everyday transactions."
    },
]

def seed_if_empty(db_path: str | None = None) -> bool:
    """Seeds cards and offers if the database offers table is currently empty."""
    initialize_database(db_path)
    if has_seeded_offers(db_path):
        return False

    with get_connection(db_path) as conn:
        card_id_map = {}
        for card in CARDS_DATA:
            cursor = conn.execute(
                "INSERT INTO cards (card_name, issuer, active) VALUES (?, ?, 1);",
                (card["name"], card["issuer"])
            )
            card_id_map[card["name"]] = cursor.lastrowid

        for offer in OFFERS_DATA:
            card_id = card_id_map[offer["card_name"]]
            conn.execute(
                """
                INSERT INTO offers (
                    card_id, merchant, category, benefit_type, rate_percent,
                    minimum_spend, cap_amount, active, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?);
                """,
                (
                    card_id,
                    offer["merchant"].lower(),
                    offer["category"].lower(),
                    offer["benefit_type"],
                    offer["rate_percent"],
                    offer["minimum_spend"],
                    offer["cap_amount"],
                    offer["description"]
                )
            )
    return True

if __name__ == "__main__":
    seeded = seed_if_empty()
    if seeded:
        print("Database seeded with demo cards and offers.")
    else:
        print("Database already contains offers; skipping seed.")
