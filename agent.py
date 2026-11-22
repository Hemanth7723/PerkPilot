"""Agent module for PerkPilot: Prompt-driven credit card recommendation agent."""
import re
from typing import Any
from config import get_settings
from tools.offer_tool import analyze_card_offers

AGENT_SYSTEM_INSTRUCTION = """You are PerkPilot, an expert AI credit card deal optimizer.
When a user describes their intended purchase in natural language, your job is to:
1. Extract the merchant, purchase category, and amount (in INR).
2. Call the `analyze_card_offers` tool with merchant, category, and amount.
3. NEVER guess, invent, or calculate rewards yourself. Rely strictly on the tool's output.
4. After receiving the tool output, provide a concise, structured response (3-4 sentences):
   - Declare the best recommended card and issuer.
   - State the net savings/rewards (₹) and the effective price if an instant discount applies.
   - Explain why it won over alternatives.
   - Mention key conditions (like minimum spend or caps).
"""

def extract_purchase_details_heuristically(text: str) -> tuple[str, str, float]:
    """
    Intelligent entity extraction for purchase prompt when running locally without external LLM.
    Extracts: merchant, category, amount.
    """
    text_lower = text.lower()
    
    # 1. Extract Amount
    amt_match = re.search(r'(?:₹|rs\.?|inr)\s*([0-9,]+(?:\.[0-9]+)?)', text_lower)
    if not amt_match:
        amt_match = re.search(r'([0-9,]+(?:\.[0-9]+)?)\s*(?:₹|rs\.?|inr|rupees|bucks)', text_lower)
    if not amt_match:
        amt_match = re.search(r'\b([0-9]{3,7}(?:\.[0-9]+)?)\b', text_lower)
    
    if amt_match:
        raw_amt = amt_match.group(1).replace(',', '')
        try:
            amount = float(raw_amt)
        except ValueError:
            amount = 1000.0
    else:
        amount = 1000.0

    # 2. Extract Merchant
    known_merchants = [
        "amazon", "flipkart", "swiggy", "zomato", "myntra", 
        "croma", "uber", "ola", "cafe mocha", "starbucks", 
        "reliance digital", "tata 1mg", "apple", "samsung"
    ]
    merchant = "Amazon"
    for m in known_merchants:
        if m in text_lower:
            merchant = m.title()
            break
    else:
        # Check patterns like "from X", "on X", "at X"
        prep_match = re.search(r'(?:on|from|at)\s+([a-zA-Z0-9\s&]+?)(?:\s+for|\s+worth|\s+which|\s+to|\.|\,|$)', text, re.IGNORECASE)
        if prep_match:
            candidate = prep_match.group(1).strip()
            if candidate and len(candidate) < 30:
                merchant = candidate.title()

    # 3. Extract Category
    categories_map = {
        "Electronics": [
            "headphone", "headphones", "phone", "mobile", "laptop", "tv", 
            "television", "gadget", "earbuds", "electronics", "ipad", "macbook", 
            "camera", "watch", "smartwatch", "speaker", "audio"
        ],
        "Food & Dining": [
            "food", "dining", "swiggy", "zomato", "cafe", "coffee", "restaurant", 
            "dinner", "lunch", "pizza", "burger", "meal", "eats"
        ],
        "Grocery": [
            "grocery", "groceries", "instamart", "blinkit", "zepto", "supermarket", 
            "vegetables", "milk", "fruits"
        ],
        "Travel": [
            "flight", "hotel", "travel", "trip", "uber", "ola", "ticket", 
            "airline", "booking", "train", "cab"
        ],
        "Fashion": [
            "clothing", "clothes", "fashion", "shoes", "shirt", "dress", 
            "jeans", "apparel", "wear", "myntra"
        ],
    }

    category = "Other"
    for cat, keywords in categories_map.items():
        if any(kw in text_lower for kw in keywords):
            category = cat
            break
            
    # Category fallback from merchant
    if category == "Other":
        if merchant.lower() in ["swiggy", "zomato", "cafe mocha"]:
            category = "Food & Dining"
        elif merchant.lower() in ["amazon", "flipkart"]:
            category = "Electronics"

    return merchant, category, amount

def generate_grounded_explanation(tool_result: dict[str, Any]) -> str:
    """Generate a clean explanation grounded in tool output."""
    best = tool_result.get("best_option")
    if not best:
        return (
            "No eligible credit card offers were found matching your purchase criteria. "
            "You may want to use a standard all-around rewards card."
        )

    card_name = best["card_name"]
    issuer = best["issuer"]
    benefit_type = best["benefit_type"]
    benefit_amt = best["benefit_amount"]
    rate = best["rate_percent"]
    conditions = ", ".join(best["conditions"])

    if benefit_type == "instant_discount_percent":
        eff_price = best["effective_price"]
        return (
            f"**{card_name}** ({issuer}) is your best option, giving you an instant discount of **₹{benefit_amt}** ({rate}%), "
            f"reducing your total checkout price to **₹{eff_price}**. Conditions: {conditions}."
        )
    elif benefit_type == "cashback_percent":
        return (
            f"**{card_name}** ({issuer}) delivers the highest return with **₹{benefit_amt}** ({rate}%) "
            f"statement cashback. Conditions: {conditions}."
        )
    else:
        return (
            f"**{card_name}** ({issuer}) provides accelerated reward points worth approximately **₹{benefit_amt}** "
            f"({rate}% equivalent return). Conditions: {conditions}."
        )

def run_agent_on_prompt(user_prompt: str) -> dict[str, Any]:
    """
    Main entrypoint: AI Agent parses natural language prompt, calls analyze_card_offers,
    and returns full structured results and agent explanation.
    """
    settings = get_settings()
    captured_tool_result: dict[str, Any] | None = None
    agent_text = ""
    agent_mode = "local-agent"
    extracted_params = {}

    # Tool wrapper to intercept and save tool output
    def intercepted_tool(merchant: str, category: str, amount: float) -> dict[str, Any]:
        nonlocal captured_tool_result, extracted_params
        extracted_params = {"merchant": merchant, "category": category, "amount": amount}
        res = analyze_card_offers(merchant=merchant, category=category, amount=amount)
        captured_tool_result = res
        return res

    # 1. Try Gemini via Google GenAI SDK if API key is provided
    if settings.google_api_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(
                api_key=settings.google_api_key,
                http_options=types.HttpOptions(timeout=15000)
            )
            config = types.GenerateContentConfig(
                system_instruction=AGENT_SYSTEM_INSTRUCTION,
                tools=[intercepted_tool],
                temperature=0.1,
            )
            chat = client.chats.create(model=settings.model_name, config=config)
            response = chat.send_message(user_prompt)
            agent_text = response.text or ""
            agent_mode = f"Gemini ({settings.model_name})"
        except Exception:
            # Fall through to local agent if network/key issues occur
            agent_mode = "local-agent"

    # 2. Local intelligent agent fallback
    if captured_tool_result is None:
        m, c, a = extract_purchase_details_heuristically(user_prompt)
        captured_tool_result = intercepted_tool(merchant=m, category=c, amount=a)
        agent_text = generate_grounded_explanation(captured_tool_result)
    elif not agent_text:
        agent_text = generate_grounded_explanation(captured_tool_result)

    return {
        "user_prompt": user_prompt,
        "extracted_params": extracted_params,
        "tool_result": captured_tool_result,
        "agent_response": agent_text,
        "agent_mode": agent_mode,
    }
