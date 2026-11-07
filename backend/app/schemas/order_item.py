
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderStatusUpdate(BaseModel):
    order_status: Literal[
        "Pending",
        "Confirmed",
        "Processing",
        "Ready",
        "Out for Delivery",
        "Completed",
        "Cancelled"
    ]