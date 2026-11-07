
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


FulfilmentMethod = Literal["Delivery", "Pickup"]

DeliveryStatus = Literal[
    "Pending",
    "Dispatched",
    "Delivered",
    "Failed"
]


class DeliveryStatusUpdate(BaseModel):
    delivery_status: DeliveryStatus


class DeliveryCreate(BaseModel):
    order_id: int
    fulfilment_method: FulfilmentMethod
    delivery_date: datetime | None = None


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    delivery_id: int
    order_id: int
    fulfilment_method: FulfilmentMethod
    delivery_address: str | None
    delivery_date: datetime | None
    delivery_status: DeliveryStatus
