import os
import httpx

from dotenv import load_dotenv

load_dotenv()

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE_URL = "https://api.paystack.co"


def initialize_transaction(
    email: str,
    amount: int,
    reference: str,
    currency: str,
    channels: list[str],
    callback_url: str
):
    if not PAYSTACK_SECRET_KEY:
        raise RuntimeError("PAYSTACK_SECRET_KEY is missing from .env")

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "amount": amount,
        "reference": reference,
        "currency": currency,
        "channels": channels,
        "callback_url": callback_url
    }

    try:
        response = httpx.post(
            f"{PAYSTACK_BASE_URL}/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

    except httpx.HTTPError as error:
        raise RuntimeError("Could not communicate with Paystack") from error

    if not result.get("status"):
        raise RuntimeError("Paystack could not initialize the transaction")

    return result["data"]



def verify_transaction(reference: str):
    if not PAYSTACK_SECRET_KEY:
        raise RuntimeError("PAYSTACK_SECRET_KEY is missing from .env")

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    try:
        response = httpx.get(
            f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

    except httpx.HTTPError as error:
        raise RuntimeError("Could not verify transaction with Paystack") from error

    if not result.get("status"):
        raise RuntimeError("Paystack verification request failed")

    return result["data"]
