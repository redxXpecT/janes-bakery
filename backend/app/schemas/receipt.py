
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ReceiptCreate(BaseModel):
    order_id: int


class ReceiptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    receipt_id: int
    order_id: int
    receipt_date: datetime
    total_amount: Decimal
