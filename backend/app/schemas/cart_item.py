
from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
    cart_id: int
    product_id: int
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cart_item_id: int
    cart_id: int
    product_id: int
    quantity: int



class AddCartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(gt=0)