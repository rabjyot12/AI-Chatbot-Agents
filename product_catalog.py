"""Telecom product catalog used by the sales agent.

Keep factual product information here. Replace the placeholder descriptions
with the company's approved product/brochure content when available.
"""

PRODUCTS = {
    "Bulk SMS": {
        "key": "bulk_sms",
        "description": "Bulk SMS is a business messaging solution for sending SMS campaigns at scale.",
        "best_for": "Businesses that need to communicate with a large customer audience through SMS.",
        "facts": [
            "Bulk SMS is one of the communication solutions offered by the company.",
            "The right campaign setup depends on the customer's use case and audience size.",
        ],
    },
    "RCS SMS": {
        "key": "rcs",
        "description": "RCS SMS is a business messaging option for richer customer communication.",
        "best_for": "Businesses evaluating richer messaging experiences beyond standard SMS.",
        "facts": [
            "RCS SMS is one of the communication solutions offered by the company.",
            "Exact features, pricing and availability should be confirmed from the approved product material.",
        ],
    },
    "WhatsApp": {
        "key": "whatsapp",
        "description": "WhatsApp can be used as a conversational channel for customer communication and sales.",
        "best_for": "Businesses that want customers to interact with them through WhatsApp.",
        "facts": [
            "WhatsApp is a required channel for the prototype.",
            "Production WhatsApp API integration will be connected later.",
        ],
    },
    "Voice OBD/IBD": {
        "key": "voice",
        "description": "Voice OBD/IBD is a business voice communication solution.",
        "best_for": "Businesses that need voice-based customer communication.",
        "facts": [
            "Voice OBD/IBD is one of the communication solutions identified for the project.",
            "The senior requirement also mentions WhatsApp integration with the voice solution.",
        ],
    },
    "IVR": {
        "key": "ivr",
        "description": "IVR is an interactive voice response solution for structured customer interactions over calls.",
        "best_for": "Businesses that need menu-driven or automated voice interactions.",
        "facts": [
            "IVR is one of the communication solutions identified for the project.",
        ],
    },
    "Toll-Free": {
        "key": "toll_free",
        "description": "Toll-Free numbers provide a dedicated calling route for customer communication.",
        "best_for": "Businesses that want customers to contact them through a toll-free number.",
        "facts": [
            "Toll-Free numbers are one of the communication solutions identified for the project.",
        ],
    },
}

PRODUCT_ALIASES = {
    "bulk sms": "Bulk SMS",
    "bulk message": "Bulk SMS",
    "sms": "Bulk SMS",
    "rcs": "RCS SMS",
    "rcs sms": "RCS SMS",
    "whatsapp": "WhatsApp",
    "wa": "WhatsApp",
    "voice": "Voice OBD/IBD",
    "obd": "Voice OBD/IBD",
    "ibd": "Voice OBD/IBD",
    "ivr": "IVR",
    "toll free": "Toll-Free",
    "tollfree": "Toll-Free",
    "toll-free": "Toll-Free",
}


def normalize_product_name(value):
    if not value:
        return None

    text = value.strip().lower()

    for alias, product_name in PRODUCT_ALIASES.items():
        if alias in text:
            return product_name

    return None


def get_product(product_name):
    return PRODUCTS.get(product_name)


def catalog_text():
    lines = []

    for name, product in PRODUCTS.items():
        lines.append(
            f"{name}: {product['description']} "
            f"Best for: {product['best_for']}"
        )

    return "\n".join(lines)
