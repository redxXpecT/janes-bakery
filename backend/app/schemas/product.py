
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductCreate(BaseModel):
    product_name: str = Field(min_length=1)
    description: str | None = None
    cost_price: Decimal = Field(ge=0)
    selling_price: Decimal = Field(ge=0)
    stock_quantity: int = Field(ge=0)
    image_url: str | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    admin_id: int
    product_name: str
    description: str | None
    cost_price: Decimal
    selling_price: Decimal
    stock_quantity: int
    image_url: str | None
    date_added: datetime


class ProductUpdate(BaseModel):
    product_name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    cost_price: Decimal | None = Field(default=None, ge=0)
    selling_price: Decimal | None = Field(default=None, ge=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    image_url: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_null_required_fields(cls, value: object) -> object:
        if isinstance(value, dict):
            required_fields = {
                "product_name",
                "cost_price",
                "selling_price",
                "stock_quantity",
            }
            if any(value.get(field) is None for field in required_fields & value.keys()):
                raise ValueError("Required product fields cannot be null")
        return value