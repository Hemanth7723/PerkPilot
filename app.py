"""PerkPilot — AI-Powered Credit Card Recommendation Dashboard."""
import streamlit as st
import pandas as pd
from agent import run_agent_on_prompt
from db.seed_db import seed_if_empty

# Page Configuration
st.set_page_config(
    page_title="PerkPilot — AI Credit Card Optimizer",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize and seed database if not already done
seed_if_empty()

# Custom CSS matching ui-theme.md tokens
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1140px;
    }
    
    .demo-badge {
        display: inline-block;
        background-color: #EEF2F8;
        color: #647089;
        font-size: 0.8rem;
        font-weight: 550;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid #DCE3EE;
    }
    
    .winner-card {
        background-color: #FFFFFF;
        border: 1.5px solid #4F46E5;
        border-radius: 14px;
        padding: 24px;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.06);
    }
    
    .winner-badge {
        display: inline-block;
        background-color: #EEF0FF;
        color: #4F46E5;
        font-size: 0.8rem;
        font-weight: 650;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-bottom: 8px;
    }
    
    .winner-title {
        color: #172033;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .winner-issuer {
        color: #647089;
        font-size: 0.95rem;
        margin-bottom: 16px;
    }
    
    .savings-highlight {
        color: #15803D;
        font-size: 1.75rem;
        font-weight: 750;
    }
    
    .price-highlight {
        color: #172033;
        font-size: 1.25rem;
        font-weight: 650;
    }
    
    .condition-pill {
        display: inline-block;
        background-color: #FFF5E6;
        color: #B45309;
        font-size: 0.78rem;
        padding: 3px 8px;
        border-radius: 6px;
        margin-right: 6px;
        margin-top: 4px;
        border: 1px solid #FDE68A;
    }
    
    .agent-box {
        background-color: #F8FAFC;
        border-left: 3px solid #4F46E5;
        padding: 14px 18px;
        border-radius: 6px;
        color: #172033;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-top: 14px;
    }

    .extracted-chip {
        display: inline-block;
        background-color: #EEF2F8;
        color: #172033;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# App Header
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.title("PerkPilot 💳")
    st.caption("AI Credit Card Deal Optimizer — Tell the agent what you want to buy, and it finds the highest saving card.")
with col_badge:
    st.markdown("<div style='text-align: right; padding-top: 1rem;'><span class='demo-badge'>Demo offers · AI Agent</span></div>", unsafe_allow_html=True)

st.markdown("---")

# Single Natural Language Prompt Interface (No filters)
with st.form("agent_prompt_form"):
    user_prompt = st.text_area(
        "Enter your purchase prompt:",
        value="",
        height=90,
        placeholder="e.g. I want to buy Sony headphones for ₹8,999 on Amazon. Which credit card gives the best deal?",
        help="Describe what you want to buy, the merchant, and amount in natural language."
    )
    submit_button = st.form_submit_button("🤖 Ask PerkPilot Agent", type="primary", use_container_width=True)

if submit_button:
    if not user_prompt.strip():
        st.warning("Please enter your purchase requirements in the prompt box.")
    else:
        with st.spinner("🤖 AI Agent is parsing your prompt, querying card offers, and calculating rewards..."):
            agent_output = run_agent_on_prompt(user_prompt)
            st.session_state["agent_output"] = agent_output

# Render Agent Results
if "agent_output" in st.session_state and st.session_state["agent_output"]:
    res = st.session_state["agent_output"]
    tool_res = res["tool_result"]
    extracted = res["extracted_params"]
    explanation = res["agent_response"]
    mode_label = res["agent_mode"]

    # Agent Extraction Summary Banner
    st.markdown(f"""
    <div style="background-color: #F8FAFC; border: 1px solid #DCE3EE; border-radius: 8px; padding: 12px 16px; margin-top: 1rem; margin-bottom: 1rem;">
        <span style="color: #647089; font-size: 0.85rem; font-weight: 600;">🤖 AGENT INTERPRETATION:</span><br/>
        <div style="margin-top: 6px;">
            <span class="extracted-chip">Store: {extracted.get('merchant', '—')}</span>
            <span class="extracted-chip">Category: {extracted.get('category', '—')}</span>
            <span class="extracted-chip">Amount: ₹{extracted.get('amount', 0):,.2f}</span>
            <span style="color: #647089; font-size: 0.8rem; float: right;">Mode: {mode_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not tool_res["success"]:
        st.error(f"⚠️ {tool_res['error']}")
    elif tool_res["status"] == "no_match" or not tool_res["best_option"]:
        st.warning("No matching eligible card offers found for this purchase.")
    else:
        best = tool_res["best_option"]
        other_offers = tool_res["eligible_offers"][1:]

        b_type_label = {
            "instant_discount_percent": "Instant Discount",
            "cashback_percent": "Statement Cashback",
            "reward_percent": "Reward Points"
        }.get(best["benefit_type"], best["benefit_type"])

        eff_price_html = ""
        if best["effective_price"]:
            eff_price_html = (
                f"<div style='margin-top: 6px;'>"
                f"<span style='color: #647089; font-size: 0.9rem;'>Effective Payable Price:</span><br/>"
                f"<span class='price-highlight'>₹{best['effective_price']}</span>"
                f"</div>"
            )

        cond_html = "".join([f"<span class='condition-pill'>{c}</span>" for c in best["conditions"]])

        winner_html = (
            f"<div class='winner-card'>"
            f"<span class='winner-badge'>⭐ Best Recommended Card</span>"
            f"<div class='winner-title'>{best['card_name']}</div>"
            f"<div class='winner-issuer'>{best['issuer']} · {best['rate_percent']}% {b_type_label}</div>"
            f"<div style='display: flex; gap: 40px; align-items: baseline; margin-top: 10px;'>"
            f"<div>"
            f"<span style='color: #647089; font-size: 0.9rem;'>Calculated Savings:</span><br/>"
            f"<span class='savings-highlight'>₹{best['benefit_amount']}</span>"
            f"</div>"
            f"{eff_price_html}"
            f"</div>"
            f"<div style='margin-top: 14px;'>{cond_html}</div>"
            f"<div class='agent-box'>💡 <b>Agent Recommendation:</b><br/>{explanation}</div>"
            f"</div>"
        )
        st.markdown(winner_html, unsafe_allow_html=True)

        # Ranked Comparison Table
        if other_offers:
            st.markdown("##### 📊 Full Ranked Card Comparison")
            table_data = []
            for rank, o in enumerate(other_offers, start=2):
                t_label = {
                    "instant_discount_percent": "Instant Discount",
                    "cashback_percent": "Cashback",
                    "reward_percent": "Rewards"
                }.get(o["benefit_type"], o["benefit_type"])
                
                table_data.append({
                    "Rank": f"#{rank}",
                    "Card Name": o["card_name"],
                    "Issuer": o["issuer"],
                    "Type": t_label,
                    "Rate": f"{o['rate_percent']}%",
                    "Savings (₹)": f"₹{o['benefit_amount']}",
                    "Effective Price (₹)": f"₹{o['effective_price']}" if o['effective_price'] else "—",
                    "Key Conditions": ", ".join(o["conditions"]),
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        # Excluded Offers
        if tool_res.get("ineligible_offers"):
            with st.expander("⚠️ Excluded Cards (Minimum Spend Not Met)"):
                for inelig in tool_res["ineligible_offers"]:
                    st.markdown(f"- **{inelig['card_name']}** ({inelig['issuer']}): *{inelig['reason']}*")

        # Transparency Expanders
        col_calc, col_agent = st.columns(2)
        with col_calc:
            with st.expander("🧮 Mathematical Calculation Breakdown"):
                st.write(f"**Target Purchase:** ₹{tool_res['purchase']['amount']} at {extracted.get('merchant')}")
                st.write(f"**Applied Offer Rate:** {best['rate_percent']}%")
                st.write(f"**Gross Computed Benefit:** ₹{best['gross_benefit']}")
                if best['cap_amount']:
                    st.write(f"**Cap Applied:** ₹{best['cap_amount']}")
                st.write(f"**Final Benefit (Savings):** ₹{best['benefit_amount']}")
                if best['effective_price']:
                    st.write(f"**Final Price:** ₹{tool_res['purchase']['amount']} − ₹{best['benefit_amount']} = ₹{best['effective_price']}")
                st.caption("Deterministic arithmetic using Python Decimal precision.")

        with col_agent:
            with st.expander("⚡ Agent Execution Trace"):
                st.markdown(f"""
                1. **Intent Analysis:** Extracted `{extracted.get('merchant')}`, `{extracted.get('category')}`, `₹{extracted.get('amount')}` from user prompt.
                2. **Tool Invocation:** Executed `analyze_card_offers(merchant='{extracted.get('merchant')}', category='{extracted.get('category')}', amount={extracted.get('amount')})`.
                3. **Database Query:** Candidate cards and offers retrieved from SQLite repository.
                4. **Evaluation:** Applied caps, minimum-spend filters, and deduplicated offers.
                5. **Agent Synthesis:** Produced grounded natural language recommendations.
                """)
                st.caption(f"Status: **{tool_res['status']}** | Engine: **{mode_label}**")
