# PerkPilot UI Theme & Design System

## 1. Design direction

**Theme name:** PerkPilot — Smart Money, Calm UI  
**Style:** Modern fintech dashboard, clean, trustworthy, slightly playful, data-forward.  
**Principle:** Make the best card and its savings instantly obvious. Keep details and conditions accessible without clutter.

Design for a hackathon demo: polished, responsive, quick to scan, and easy to understand in a few seconds. Avoid a generic chatbot-first layout. PerkPilot is a purchase decision dashboard with an AI assistant as the interaction layer.

## 2. Color palette

Use a light theme as the default, with strong contrast and restrained accent colors. Avoid using multiple competing gradients or neon colors.

| Token | Hex | Usage |
|---|---|---|
| `bg` | `#F6F8FC` | Main app background |
| `surface` | `#FFFFFF` | Cards, panels, input surfaces |
| `surface-muted` | `#EEF2F8` | Secondary areas, subtle backgrounds |
| `text-primary` | `#172033` | Main text and headings |
| `text-secondary` | `#647089` | Supporting text, labels |
| `border` | `#DCE3EE` | Card borders, dividers, input outlines |
| `primary` | `#4F46E5` | Primary actions, active state, links |
| `primary-hover` | `#4338CA` | Hover state for primary actions |
| `primary-soft` | `#EEF0FF` | Selected chips, soft accent backgrounds |
| `success` | `#15803D` | Savings, successful eligibility, positive status |
| `success-soft` | `#EAF7EE` | Savings highlights |
| `warning` | `#B45309` | Conditions, caps, attention-needed messages |
| `warning-soft` | `#FFF5E6` | Warning backgrounds |
| `danger` | `#B42318` | Errors, invalid inputs, failed tool status |
| `danger-soft` | `#FDECEC` | Error backgrounds |

**Color rules**
- Purple/indigo is the main brand accent. Reserve it for action, focus, selection, and key interactive elements.
- Green indicates real savings or verified success only. Never use green merely for decoration.
- Amber indicates conditions, limits, incomplete verification, or warnings.
- Red indicates errors or invalid data—not ordinary low-ranking cards.
- Maintain readable contrast. Do not place low-contrast text on colored surfaces.

## 3. Typography

Use a clean sans-serif font. Preferred: **Inter**; fall back to system UI sans-serif if unavailable.

| Element | Suggested size | Weight |
|---|---:|---:|
| App/page title | 26–30 px | 650–700 |
| Section title | 18–21 px | 600–650 |
| Card title | 15–17 px | 600 |
| Body | 14–16 px | 400–500 |
| Secondary/help text | 12–13 px | 400 |
| Metric/value | 24–32 px | 650–700 |
| Small labels | 11–12 px | 550–600 |

Use sentence case, not all-caps headings. Use tabular numerals for currency, percentages, and reward values when possible.

## 4. Layout and spacing

- Use a centered content area with a comfortable maximum width (approximately 1100–1240 px on desktop).
- Use a 12-column grid conceptually; simplify to two-column layouts where appropriate.
- Spacing scale: 4, 8, 12, 16, 20, 24, 32 px. Prefer consistent multiples rather than arbitrary spacing.
- Main page padding: 24 px desktop, 16 px tablet, 12–16 px mobile.
- Panel/card padding: 16–20 px.
- Keep sections separated by whitespace, not excessive dividers.
- Cards should be visually grouped, not nested in multiple layers of containers.

## 5. Shape, borders, and shadows

- Cards: 12–16 px radius.
- Buttons and inputs: 9–12 px radius.
- Small chips/badges: pill shape.
- Use 1 px borders in `border` color for most surfaces.
- Shadows should be subtle and rare (e.g. small elevation on the recommendation card or popover). Avoid heavy drop shadows and glassmorphism.
- No decorative gradients by default. If a gradient is used, keep it subtle and only on a hero or primary recommendation surface.

## 6. App shell

### Desktop
- Compact sidebar or top navigation; do not let navigation dominate the demo.
- Brand: PerkPilot wordmark with a small simple icon (wallet/card/spark motif).
- Navigation items: **Analyze Purchase** (primary), **My Cards** (optional MVP), **Offers** (optional MVP), **About / How it works**.
- Show a small “Demo data” indicator so mock offers are never mistaken for live offers.

### Mobile
- Collapse navigation to a compact top bar or sidebar toggle.
- Stack all panels vertically.
- Ensure inputs and buttons have comfortable touch targets (minimum around 44 px height).

## 7. Primary page: Analyze Purchase

This is the main demo screen and should be the default landing page.

### Header
- Title: **Find the best card for this purchase**
- Subtitle: “Compare eligible rewards, cashback, and discounts before you pay.”
- A subtle data disclaimer: **Demo offers · Not live bank data**

### Purchase input panel
Use a clean white card containing:
- Merchant (text input or select with common demo merchants)
- Purchase amount (₹ input; positive numeric validation)
- Category (select: Electronics, Grocery, Food & Dining, Travel, Fashion, Other)
- Optional notes (keep hidden or secondary in the MVP)
- Primary button: **Find best card**

The form should be compact. Avoid conversational input being the only way to trigger analysis; structured fields make the demo predictable.

## 8. Results presentation

Show the results only after valid input and successful analysis.

### Best recommendation card
This should be the visual focal point. Include:
- “Best match” or “Recommended card” label
- Card name and issuer
- Reward amount in ₹ (largest result value)
- Effective purchase price after estimated benefit
- Reward type and rate
- Short reason explaining why it wins
- Eligibility / cap / minimum-spend conditions in a readable secondary section

Use `success` color for the computed savings amount, not for the whole card background. Keep the recommendation panel light and calm.

### Ranked alternatives
Show the next eligible cards in a compact table or cards with:
- Card name
- Benefit type and rate
- Reward value (₹)
- Effective cost
- Any key limit/condition

Highlight the recommended row with a subtle `primary-soft` background and a “Best” badge. Do not use rank colors like gold/silver/bronze unless the ranking itself is meaningful.

### Calculation transparency
Provide an expandable section such as **How savings were calculated** showing:
- Purchase amount
- Applied offer / reward rate
- Cap (if applicable)
- Minimum spend eligibility
- Estimated reward calculation
- Effective price

The calculation must be produced by deterministic Python logic, not generated by the LLM. Clearly label estimates and assumptions.

## 9. Agent activity and explainability

Show agent activity in a small collapsible panel or status area, not as a noisy chat transcript.

Possible activity steps:
1. Interpreting purchase details
2. Looking up matching card offers
3. Checking eligibility and caps
4. Calculating rewards
5. Ranking results

Only show steps that actually occurred. Never fake tool calls or success states. For demo/fallback mode, label it honestly as **Rule-based analysis**. For agent mode, show **AI-assisted analysis** and the tool result status.

A short natural-language explanation may appear after the recommendation. Keep it to 2–4 sentences. Show the structured calculation alongside it.

## 10. Statuses and feedback

Use consistent status badges and messages:
- **Eligible** — green, only when eligibility checks pass
- **Condition applies** — amber, when a limitation is relevant
- **Unavailable / Not verified** — neutral or amber; do not imply failure if the source is simply missing
- **Tool error** — red with clear retry or fallback guidance
- **No eligible offers** — neutral empty state with helpful next step
- **Demo data** — neutral badge visible near results or header

Errors should be human-readable, actionable, and never expose stack traces or secrets.


## 11. Empty, loading, and error states

### Initial state
Use a concise welcoming prompt and a purchase form. Avoid an empty dashboard with meaningless charts.

### Loading state
Show a simple progress indicator and text such as “Checking eligible offers…” Avoid long fake progress animations.

### No offers found
Say no matching eligible offers were found for the selected merchant/category/amount. Offer a neutral fallback such as comparing cards with general rewards, if the dataset supports it.

### Tool/model unavailable
Offer deterministic analysis mode when possible and label the result accordingly. Do not invent current offer data.

### Invalid input
Inline validation: amount must be a valid positive amount; merchant and category are required. Keep errors close to the field.

## 12. Icons and imagery

- Prefer consistent line icons (Lucide-style) for cards, wallet, shopping bag, calculator, check, alert, database, and AI activity.
- Use icons sparingly; pair with text labels for clarity.
- Do not use stock photos of people, decorative finance imagery, or large hero illustrations in the functional dashboard. The data and recommendation should be the visual focus.
- Card logos may be used only if readily available and appropriate; otherwise use issuer/card text and a simple neutral card illustration. Avoid unofficial or misleading bank branding.

## 13. Tables, charts, and data density

- Use a table for ranked alternatives when several offers must be compared.
- Right-align currency and numeric columns.
- Use clear labels for cashback, discount, reward points, caps, and effective price; do not mix reward types without converting them to a comparable value transparently.
- Avoid pie charts and decorative analytics in the MVP. A simple comparison is more useful than a chart.
- Use tooltips/help text for jargon, but ensure important eligibility details remain visible or one click away.

## 14. Accessibility and responsive behavior

- Keyboard-accessible controls, focus indicators, and labels for all fields.
- Never rely on color alone to convey status.
- Respect text zoom and avoid fixed-height text containers.
- Provide sufficient contrast and readable text sizes.
- On narrow screens, stack recommendation and alternatives, and allow table horizontal scrolling or switch to comparison cards.
- Buttons should have clear action verbs and disabled states when input is invalid or analysis is running.

## 15. Streamlit implementation guidance

- Apply theme through Streamlit configuration where supported (primary color, background, secondary background, text color, font).
- Use Streamlit-native widgets first; avoid custom component dependencies unless they materially improve the demo.
- Use `st.container`, `st.columns`, `st.metric`, `st.dataframe`/`st.table`, `st.expander`, `st.status` or equivalent supported components to create structure.
- Keep styling overrides minimal and centralized. If CSS is used, store it in one theme/style helper and avoid brittle selectors tied to internal Streamlit DOM implementation.
- Define a reusable set of style tokens in a dedicated module (e.g. `ui/theme.py`) and keep page components consistent.
- Do not let the UI layer implement offer rules or reward calculations. It only collects input, invokes the service/agent, and renders returned results.

## 16. Suggested theme configuration

Create `.streamlit/config.toml` with a theme similar to:

```toml
[theme]
base = "light"
primaryColor = "#4F46E5"
backgroundColor = "#F6F8FC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#172033"
font = "sans serif"
```

## 17. Suggested screen hierarchy

```text
┌──────────────────────────────────────────────────────────────┐
│ PerkPilot  [Analyze Purchase] [Cards] [Offers]  Demo data  │
├──────────────────────────────────────────────────────────────┤
│ Find the best card for this purchase                        │
│ Compare rewards, cashback, and discounts before you pay.      │
│                                                              │
│ ┌──────────────────── Purchase details ────────────────────┐ │
│ │ Merchant [ Amazon                       ]                │ │
│ │ Amount  [ ₹ 8,999                      ]                │ │
│ │ Category[ Electronics                  ]                │ │
│ │                  [ Find best card ]                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────── Best match ──────────────────────────┐ │
│ │ HDFC Millennia                     Estimated savings    │ │
│ │                                    ₹450                │ │
│ │ Effective price ₹8,549                                   │ │
│ │ Why it wins · eligible offer · conditions                │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ Other eligible cards                                         │
│ Card             Reward       Savings       Effective price  │
│ ...                                                          │
│                                                              │
│ [How savings were calculated ▾] [Agent activity ▾]            │
└──────────────────────────────────────────────────────────────┘
```

The sketch is illustrative; implement with Streamlit layout primitives and adapt for screen width.

## 18. UX acceptance checklist

- [ ] Default screen is the purchase-analysis flow, not a blank dashboard or chat window.
- [ ] Theme colors and typography are consistent across all components.
- [ ] Purchase inputs are clearly labeled and validate correctly.
- [ ] The best recommendation and estimated savings are immediately visible.
- [ ] Alternative cards are easy to compare and understand.
- [ ] Eligibility conditions and calculations can be inspected.
- [ ] Demo/mock data is clearly labeled and never mistaken for live offers.
- [ ] Agent/tool activity reflects real execution only.
- [ ] Loading, error, empty, and fallback states are designed.
- [ ] Responsive layout works on desktop and mobile widths.
- [ ] Keyboard focus and contrast are usable.
- [ ] No unnecessary charts, decoration, or nested cards distract from the decision.

## 19. Instructions to the implementation agent

Treat this document as the UI design source of truth. Follow its palette, typography, spacing, layout, status semantics, and result hierarchy consistently. Do not invent a second theme. Keep the interface clean and modern, prioritize the recommendation and transparent savings calculations, and ensure the demo-data disclaimer is visible. If an existing component or library is reused, adapt it to this theme rather than allowing inconsistent styles. Any deviation should be intentional and documented briefly.
