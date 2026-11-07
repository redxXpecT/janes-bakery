
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


OrderStatus = Literal[
    "Pending",
    "Confirmed",
    "Processing",
    "Ready",
    "Out for Delivery",
    "Completed",
    "Cancelled"
]

DeliveryMethod = Literal["Delivery", "Pickup"]


class CustomerOrderCreate(BaseModel):
    customer_id: int
    delivery_method: DeliveryMethod
    delivery_address: str | None = None


class CustomerOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    customer_id: int
    order_date: datetime
    total_amount: Decimal
    order_status: OrderStatus
    delivery_method: DeliveryMethod
    delivery_address: str | None
    
    



class OrderCheckoutRequest(BaseModel):
    delivery_method: Literal["Delivery", "Pickup"]
    delivery_address: str | None = None