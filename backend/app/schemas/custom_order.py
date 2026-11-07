
from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class CustomOrderRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    customization_details: str
    special_request: str | None = None
    required_date: date


class CustomOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    custom_order_id: int
    customer_id: int
    order_id: int | None
    product_id: int
    quantity: int
    customization_details: str
    special_request: str | None
    required_date: date
    selling_price: Decimal




OrderStatus = Literal[
    "Pending",
    "Confirmed",
    "Processing",
    "Ready",
    "Out for Delivery",
    "Completed",
    "Cancelled"
]


class OrderCheckoutRequest(BaseModel):
    delivery_method: Literal["Delivery", "Pickup"]
    delivery_address: str | None = None


class OrderCheckoutResponse(BaseModel):
    order_id: int
    total_amount: float
    order_status: OrderStatus
    delivery_method: Literal["Delivery", "Pickup"]
    delivery_address: str | None = None
