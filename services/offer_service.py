"""Core business logic for eligibility evaluation, benefit calculations, and offer ranking."""
import math
from decimal import Decimal
from typing import Any
from config import get_settings
from db.repository import find_candidate_offers
from services.calculations import calculate_benefit, format_inr, to_decimal

BENEFIT_TYPE_PRIORITY = {
    "instant_discount_percent": 1,
    "cashback_percent": 2,
    "reward_percent": 3,
}

def validate_purchase_inputs(merchant: Any, category: Any, amount: Any) -> tuple[bool, str | None, float]:
    """Validate purchase inputs deterministically."""
    if not isinstance(merchant, str) or not merchant.strip():
        return False, "Merchant name is required and cannot be empty.", 0.0
    if len(merchant.strip()) > 100:
        return False, "Merchant name exceeds maximum length of 100 characters.", 0.0

    if not isinstance(category, str) or not category.strip():
        return False, "Category is required and cannot be empty.", 0.0
    if len(category.strip()) > 100:
        return False, "Category exceeds maximum length of 100 characters.", 0.0

    try:
        amt_f = float(amount)
    except (ValueError, TypeError):
        return False, "Purchase amount must be a valid numeric value.", 0.0

    if math.isnan(amt_f) or math.isinf(amt_f):
        return False, "Purchase amount must be a finite number.", 0.0

    if amt_f <= 0:
        return False, "Purchase amount must be greater than zero.", 0.0

    max_amt = get_settings().max_purchase_amount
    if amt_f > max_amt:
        return False, f"Purchase amount exceeds maximum demo limit of ₹{max_amt:,.2f}.", 0.0

    return True, None, amt_f

def analyze_purchase(
    merchant: str,
    category: str,
    amount: float | int | str,
    db_path: str | None = None
) -> dict[str, Any]:
    """
    Main offer analysis engine:
    1. Validates inputs.
    2. Queries candidate card offers from SQLite repository.
    3. Evaluates minimum-spend eligibility and caps.
    4. Deduplicates per card (highest benefit wins).
    5. Ranks deterministically.
    """
    is_valid, err_msg, validated_amount = validate_purchase_inputs(merchant, category, amount)
    
    clean_merchant = str(merchant).strip() if merchant else ""
    clean_category = str(category).strip() if category else ""
    amount_str = format_inr(to_decimal(validated_amount)) if is_valid else str(amount)

    base_purchase = {
        "merchant": clean_merchant,
        "category": clean_category,
        "amount": amount_str,
        "currency": "INR",
    }

    if not is_valid:
        return {
            "success": False,
            "status": "invalid_input",
            "purchase": base_purchase,
            "eligible_offers": [],
            "ineligible_offers": [],
            "best_option": None,
            "assumptions": ["Input validation failed; analysis aborted."],
            "error": err_msg,
        }

    try:
        candidates = find_candidate_offers(clean_merchant, clean_category, db_path=db_path)
    except Exception as exc:
        return {
            "success": False,
            "status": "unavailable",
            "purchase": base_purchase,
            "eligible_offers": [],
            "ineligible_offers": [],
            "best_option": None,
            "assumptions": ["Database unavailable."],
            "error": "Card offer database is currently unavailable. Please try again later.",
        }

    eligible_by_card: dict[int, dict[str, Any]] = {}
    ineligible_offers: list[dict[str, Any]] = []

    for c in candidates:
        min_spend = float(c["minimum_spend"] or 0.0)
        card_id = c["card_id"]
        
        # Check minimum spend
        if validated_amount < min_spend:
            ineligible_offers.append({
                "card_name": c["card_name"],
                "issuer": c["issuer"],
                "reason": f"Minimum purchase amount of ₹{min_spend:,.2f} not reached.",
                "description": c["description"] or "",
            })
            continue

        calc = calculate_benefit(
            amount=validated_amount,
            rate_percent=c["rate_percent"],
            cap_amount=c["cap_amount"],
            benefit_type=c["benefit_type"],
        )

        conditions = []
        if min_spend > 0:
            conditions.append(f"Min spend ₹{min_spend:,.0f}")
        if c["cap_amount"] is not None:
            conditions.append(f"Capped at ₹{float(c['cap_amount']):,.0f}")
        if not conditions:
            conditions.append("No cap / standard terms")

        offer_dict = {
            "card_id": card_id,
            "card_name": c["card_name"],
            "issuer": c["issuer"],
            "benefit_type": c["benefit_type"],
            "rate_percent": format_inr(to_decimal(c["rate_percent"])),
            "gross_benefit": calc["gross_benefit"],
            "benefit_amount": calc["benefit_amount"],
            "cap_amount": calc["cap_amount"],
            "effective_price": calc["effective_price"],
            "conditions": conditions,
            "description": c["description"] or "",
        }

        # Deduplicate per card: select highest net benefit
        if card_id not in eligible_by_card:
            eligible_by_card[card_id] = offer_dict
        else:
            existing = eligible_by_card[card_id]
            curr_amt = Decimal(offer_dict["benefit_amount"])
            prev_amt = Decimal(existing["benefit_amount"])
            if curr_amt > prev_amt:
                eligible_by_card[card_id] = offer_dict
            elif curr_amt == prev_amt:
                # Prefer instant discount over cashback over rewards
                curr_prio = BENEFIT_TYPE_PRIORITY.get(offer_dict["benefit_type"], 99)
                prev_prio = BENEFIT_TYPE_PRIORITY.get(existing["benefit_type"], 99)
                if curr_prio < prev_prio:
                    eligible_by_card[card_id] = offer_dict

    eligible_offers = list(eligible_by_card.values())

    # Sort descending by benefit_amount, then benefit type priority, then card name
    eligible_offers.sort(
        key=lambda x: (
            Decimal(x["benefit_amount"]),
            -BENEFIT_TYPE_PRIORITY.get(x["benefit_type"], 99),
            x["card_name"]
        ),
        reverse=True
    )

    best_option = eligible_offers[0] if eligible_offers else None
    status = "ok" if eligible_offers else "no_match"

    assumptions = [
        "Fictional mock card data for illustrative purposes only.",
        "Cashback and rewards are credited post-transaction and do not discount checkout price immediately.",
    ]
    if any(o["benefit_type"] == "reward_percent" for o in eligible_offers):
        assumptions.append("Reward points are represented at their illustrative rupee-equivalent valuation.")

    return {
        "success": True,
        "status": status,
        "purchase": base_purchase,
        "eligible_offers": eligible_offers,
        "ineligible_offers": ineligible_offers,
        "best_option": best_option,
        "assumptions": assumptions,
        "error": None,
    }
