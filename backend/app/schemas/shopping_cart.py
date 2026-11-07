
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


CartStatus = Literal[
    "Active",
    "Converted",
    "Abandoned"
]


class ShoppingCartCreate(BaseModel):
    customer_id: int


class ShoppingCartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cart_id: int
    customer_id: int
    date_created: datetime
    cart_status: CartStatus
