from sqlalchemy import (
    Integer, ForeignKey,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CartItem(Base):
    __tablename__ = "cart_item"

    cart_item_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    cart_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shopping_cart.cart_id"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.product_id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_cart_item_quantity"
        ),
        UniqueConstraint(
            "cart_id",
            "product_id",
            name="unique_product_per_cart"
        ),
    )