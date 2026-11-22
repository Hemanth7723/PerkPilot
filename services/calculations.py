"""Pure deterministic financial calculation helpers for PerkPilot."""
from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict

class BenefitResult(TypedDict):
    gross_benefit: str
    benefit_amount: str
    cap_amount: str | None
    effective_price: str | None

def to_decimal(val: float | int | str | Decimal) -> Decimal:
    """Safely convert values to Decimal avoiding binary float artifacts."""
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))

def format_inr(d: Decimal) -> str:
    """Format decimal to 2 places as standard currency representation."""
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def calculate_benefit(
    amount: float | Decimal,
    rate_percent: float | Decimal,
    cap_amount: float | Decimal | None,
    benefit_type: str,
) -> BenefitResult:
    """
    Calculate raw benefit, apply cap, and compute effective price if instant discount.
    Cashback and reward points do not reduce checkout price immediately.
    """
    amt_d = to_decimal(amount)
    rate_d = to_decimal(rate_percent)
    
    raw_benefit = (amt_d * rate_d) / Decimal("100")
    
    if cap_amount is not None:
        cap_d = to_decimal(cap_amount)
        final_benefit = min(raw_benefit, cap_d)
        cap_str = format_inr(cap_d)
    else:
        final_benefit = raw_benefit
        cap_str = None
        
    gross_str = format_inr(raw_benefit)
    net_str = format_inr(final_benefit)
    
    if benefit_type == "instant_discount_percent":
        effective_d = max(Decimal("0.00"), amt_d - final_benefit)
        effective_str = format_inr(effective_d)
    else:
        effective_str = None
        
    return {
        "gross_benefit": gross_str,
        "benefit_amount": net_str,
        "cap_amount": cap_str,
        "effective_price": effective_str,
    }
