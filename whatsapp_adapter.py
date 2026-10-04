"""Future WhatsApp adapter.

The sales engine is intentionally independent from WhatsApp.
When the official WhatsApp provider/API is configured, route the incoming
message text to process_sales_message() and send the returned reply back.

This file is a small adapter boundary for the prototype; it does not contain
provider credentials or pretend that a WhatsApp API is already connected.
"""

from sales_agent import process_sales_message


def handle_whatsapp_message(
    message_text,
    conversation_history,
    sales_state,
):
    return process_sales_message(
        message_text,
        conversation_history,
        sales_state,
    )
