
import os
import secrets

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr

from database import save_sales_customer

app = FastAPI(title="Telecom Sales Voice Webhook")


class CustomerDetails(BaseModel):
    name: str | None = None
    company: str | None = None
    phone: str | None = None
    email: str | None = None
    requirement: str | None = None
    interested_product: str | None = None
    expected_scale: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/voice/save-customer")
def save_voice_customer(
    customer: CustomerDetails,
    x_webhook_secret: str = Header(default=""),
):
    expected_secret = os.getenv("VOICE_WEBHOOK_SECRET", "")

    if not expected_secret or not secrets.compare_digest(
        x_webhook_secret, expected_secret
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    details = customer.model_dump()

    # Remove blank values.
    details = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in details.items()
    }
    details = {key: value or None for key, value in details.items()}

    if not any(
        details.get(key)
        for key in ("name", "company", "phone", "email", "requirement")
    ):
        raise HTTPException(
            status_code=422,
            detail="At least one useful customer detail is required.",
        )

    try:
        customer_id = save_sales_customer(
            details,
            channel="website_voice",
        )
        return {
            "success": True,
            "customer_id": str(customer_id),
            "message": "Customer details saved successfully.",
        }
    except Exception:
        # Avoid returning database internals to the external caller.
        raise HTTPException(
            status_code=500,
            detail="Could not save customer details.",
        )
    