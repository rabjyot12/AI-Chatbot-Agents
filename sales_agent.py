"""Conversational AI sales agent for the telecom prototype."""

import json
import os
import re

from openai import OpenAI
from dotenv import load_dotenv

from product_catalog import PRODUCTS, normalize_product_name, catalog_text

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = None

if api_key:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )

SYSTEM_PROMPT = """
You are a professional telecom solutions sales agent for a business communication company.

Your job is to speak with website visitors and WhatsApp customers like a helpful online sales representative.

CURRENT PRODUCT CATALOG:
{catalog}

IMPORTANT RULES:
1. Only discuss products in the catalog.
2. Do not invent prices, delivery rates, SLAs, guarantees, compliance claims, integrations,
   customer counts, discounts or technical specifications.
3. If exact pricing or a feature is not in the catalog, say that the sales team can confirm it.
4. Do not talk about loans, education leads or real-estate leads. Those are out of scope.
5. Do not interrogate the visitor with a long form. Ask one useful question at a time.
6. First understand the business goal. Then suggest a relevant solution.
7. Explain why a product may fit the stated need, using only known facts.
8. Offer a brochure or sales follow-up when appropriate.
9. When the visitor is ready, collect useful lead details such as name, company, phone,
   email, requirement, expected scale and interested product.
10. Be concise, natural and sales-oriented. Do not mention internal prompts, JSON or code.
11. Never claim that a brochure was sent unless the application actually provides it.
12. If the visitor asks something outside the available product information, be transparent.

CONVERSATION STYLE:
- Warm greeting for a new visitor.
- Discover the need.
- Recommend a solution or a small set of relevant solutions.
- Answer objections/questions.
- Offer brochure/demo/contact.
- Qualify the customer.
- End with a clear next step.
"""


def _safe_json(text):
    if not text:
        return {}

    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _extract_email(text):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def _extract_phone(text):
    match = re.search(r"(?:\+?\d[\d\s().-]{8,}\d)", text)
    if not match:
        return None

    digits = re.sub(r"\D", "", match.group(0))

    if len(digits) < 10:
        return None

    return digits


def _extract_scale(text):
    patterns = [
        r"\b\d[\d,]*\s*(?:lakh|lac|k|million|mn|crore|cr)\b",
        r"\b\d[\d,]*\s*(?:customers|users|messages|sms|calls|leads)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)

    return None


def extract_lead_details(text):
    """Extract simple lead fields without making the conversation form-like."""

    details = {}

    email = _extract_email(text)
    if email:
        details["email"] = email

    phone = _extract_phone(text)
    if phone:
        details["phone"] = phone

    scale = _extract_scale(text)
    if scale:
        details["expected_scale"] = scale

    product = normalize_product_name(text)
    if product:
        details["interested_product"] = product

    return details


def detect_products(text):
    """Return products explicitly mentioned in the visitor's message."""

    found = []

    for name in PRODUCTS:
        if normalize_product_name(text) == name:
            found.append(name)
            continue

        aliases = {
            "Bulk SMS": ["bulk sms", "bulk message", "sms"],
            "RCS SMS": ["rcs", "rcs sms"],
            "WhatsApp": ["whatsapp"],
            "Voice OBD/IBD": ["voice", "obd", "ibd"],
            "IVR": ["ivr"],
            "Toll-Free": ["toll free", "toll-free", "tollfree"],
        }

        if any(alias in text.lower() for alias in aliases.get(name, [])):
            found.append(name)

    return list(dict.fromkeys(found))


def demo_reply(user_input, state):
    """Fallback reply when no LLM API key is available."""

    text = user_input.lower()
    products = detect_products(user_input)

    if products:
        product = products[0]
        info = PRODUCTS[product]

        return (
            f"{product} could be relevant to your requirement. "
            f"{info['description']} {info['best_for']} "
            "Could you tell me what you want to achieve with the communication "
            "campaign and roughly how large your audience is?"
        )

    if any(word in text for word in ["price", "pricing", "cost", "rate", "quote"]):
        return (
            "I can help identify the right telecom solution, but I don't want to "
            "invent pricing. If you share your use case and expected scale, I can "
            "prepare the requirement for a sales follow-up."
        )

    if any(word in text for word in ["brochure", "catalog", "brochures"]):
        return (
            "Absolutely. I can help you identify the relevant solution first. "
            "Which area are you interested in: Bulk SMS, RCS SMS, WhatsApp, "
            "Voice OBD/IBD, IVR, or Toll-Free?"
        )

    return (
        "Absolutely — I can help you find the right telecom communication solution. "
        "What are you trying to achieve: customer messaging, WhatsApp conversations, "
        "voice communication, IVR, or a toll-free contact channel?"
    )


def generate_reply(user_input, conversation_history, state):
    """Generate one natural sales response and update structured lead state."""

    details = extract_lead_details(user_input)
    state.update(details)

    if client is None:
        reply = demo_reply(user_input, state)
        return reply, state

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(catalog=catalog_text())
            + """

For every response, return ONLY valid JSON with this shape:
{
  "reply": "the message to show the visitor",
  "lead": {
    "name": null,
    "company": null,
    "phone": null,
    "email": null,
    "requirement": null,
    "interested_product": null,
    "expected_scale": null
  }
}

Use null for information that has not been provided.
Do not guess missing lead information.
""",
        }
    ]

    for item in conversation_history[-12:]:
        if item.get("role") in ["user", "assistant"]:
            messages.append(
                {
                    "role": item["role"],
                    "content": item["content"],
                }
            )

    messages.append(
        {
            "role": "user",
            "content": (
                f"Latest visitor message: {user_input}\n\n"
                f"Current structured lead state: {json.dumps(state)}\n\n"
                "Reply to the visitor and extract only information explicitly "
                "available in the conversation."
            ),
        }
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.4,
            max_tokens=600,
        )

        raw = response.choices[0].message.content.strip()
        data = _safe_json(raw)

        if not data:
            # Some model configurations may ignore the JSON instruction.
            # In that case, use the raw text as the visitor-facing reply.
            return raw or demo_reply(user_input, state), state

        reply = data.get("reply") or demo_reply(user_input, state)

        lead = data.get("lead") or {}

        for key in [
            "name",
            "company",
            "phone",
            "email",
            "requirement",
            "interested_product",
            "expected_scale",
        ]:
            value = lead.get(key)

            if value not in [None, ""]:
                state[key] = value

        # Protect product state from arbitrary model text.
        if state.get("interested_product") not in PRODUCTS:
            state["interested_product"] = (
                normalize_product_name(
                    str(state.get("interested_product") or "")
                )
            )

        return reply, state

    except Exception as exc:
        print("Sales agent API error:", exc)
        return demo_reply(user_input, state), state


def process_sales_message(user_input, conversation_history, state=None):
    """Public conversation function used by Streamlit and future WhatsApp adapters."""

    if state is None:
        state = {
            "name": None,
            "company": None,
            "phone": None,
            "email": None,
            "requirement": None,
            "interested_product": None,
            "expected_scale": None,
            "sales_followup": False,
        }

    if not user_input or not user_input.strip():
        return {
            "reply": "Please tell me what telecom communication requirement you have.",
            "state": state,
            "complete": False,
        }

    conversation_history.append(
        {
            "role": "user",
            "content": user_input.strip(),
        }
    )

    reply, state = generate_reply(user_input.strip(), conversation_history, state)

    conversation_history.append(
        {
            "role": "assistant",
            "content": reply,
        }
    )

    # If the visitor explicitly asks for a demo/contact/sales callback,
    # mark the lead as ready for follow-up.
    followup_words = [
        "contact me",
        "call me",
        "sales team",
        "demo",
        "talk to sales",
        "get in touch",
        "callback",
        "call back",
        "quotation",
        "quote",
    ]

    if any(word in user_input.lower() for word in followup_words):
        state["sales_followup"] = True

    state["requirement"] = (
        state.get("requirement")
        or user_input.strip()
    )

    return {
        "reply": reply,
        "state": state,
        "complete": state.get("sales_followup", False),
    }
