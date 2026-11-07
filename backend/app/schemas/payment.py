
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


PaymentMethod = Literal[
    "Mobile Money",
    "Cash",
    "Card",
    "Bank Transfer"
]

PaymentStatus = Literal[
    "Pending",
    "Successful",
    "Failed",
    "Refunded"
]


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: PaymentMethod


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    order_id: int
    payment_method: PaymentMethod
    payment_amount: Decimal
    payment_date: datetime
    payment_status: PaymentStatus
    transaction_reference: str | None
