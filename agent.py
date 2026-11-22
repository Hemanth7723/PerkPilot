"""Agent module for PerkPilot: Gemini-only credit card recommendation agent."""
from typing import Any
from google import genai
from google.genai import types
from config import get_settings
from tools.offer_tool import analyze_card_offers

AGENT_SYSTEM_INSTRUCTION = """You are PerkPilot, an expert AI credit card deal optimizer.
When a user describes their intended purchase in natural language, your job is to:
1. Extract the merchant name, purchase category, and amount (in INR).
2. Call the `analyze_card_offers` tool with merchant, category, and amount.
3. NEVER guess, invent, or calculate rewards yourself. Rely strictly on the tool's output.
4. After receiving the tool output, provide a concise, structured response (3-4 sentences):
   - Declare the best recommended card and issuer.
   - State the net savings/rewards (₹) and the effective price if an instant discount applies.
   - Explain why it won over alternatives.
   - Mention key conditions (like minimum spend or caps).
"""

def run_agent_on_prompt(user_prompt: str) -> dict[str, Any]:
    """
    Main entrypoint: Gemini AI model interprets the prompt, invokes analyze_card_offers tool,
    and produces the grounded recommendation. Uses Gemini model only (no local agents).
    """
    settings = get_settings()
    captured_tool_result: dict[str, Any] | None = None
    extracted_params: dict[str, Any] = {}
    model_name = settings.model_name
    agent_mode = f"Gemini ({model_name})"

    if not settings.google_api_key:
        err = "GOOGLE_API_KEY is not configured in .env. A valid Gemini API key is required."
        return {
            "user_prompt": user_prompt,
            "extracted_params": {},
            "tool_result": {
                "success": False,
                "status": "internal_error",
                "purchase": {"merchant": "", "category": "", "amount": "0.00", "currency": "INR"},
                "eligible_offers": [],
                "ineligible_offers": [],
                "best_option": None,
                "assumptions": [],
                "error": err,
            },
            "agent_response": err,
            "agent_mode": agent_mode,
        }

    # Intercept tool call to capture structured parameters and result
    def intercepted_tool(merchant: str, category: str, amount: float) -> dict[str, Any]:
        nonlocal captured_tool_result, extracted_params
        extracted_params = {
            "merchant": merchant,
            "category": category,
            "amount": amount
        }
        res = analyze_card_offers(merchant=merchant, category=category, amount=amount)
        captured_tool_result = res
        return res

    try:
        client = genai.Client(
            api_key=settings.google_api_key,
            http_options=types.HttpOptions(timeout=25000)
        )
        config = types.GenerateContentConfig(
            system_instruction=AGENT_SYSTEM_INSTRUCTION,
            tools=[intercepted_tool],
            temperature=0.1,
        )
        chat = client.chats.create(model=model_name, config=config)
        response = chat.send_message(user_prompt)
        agent_text = response.text or ""

        # If the model produced a response but tool wasn't called (e.g. conversational prompt)
        if captured_tool_result is None:
            # Fallback to general query search on Amazon 1000
            captured_tool_result = intercepted_tool("Amazon", "Other", 1000.0)

        return {
            "user_prompt": user_prompt,
            "extracted_params": extracted_params,
            "tool_result": captured_tool_result,
            "agent_response": agent_text,
            "agent_mode": agent_mode,
        }

    except Exception as exc:
        err_msg = f"Gemini model execution error: {exc}"
        return {
            "user_prompt": user_prompt,
            "extracted_params": extracted_params,
            "tool_result": {
                "success": False,
                "status": "internal_error",
                "purchase": {"merchant": "", "category": "", "amount": "0.00", "currency": "INR"},
                "eligible_offers": [],
                "ineligible_offers": [],
                "best_option": None,
                "assumptions": [],
                "error": err_msg,
            },
            "agent_response": err_msg,
            "agent_mode": agent_mode,
        }
