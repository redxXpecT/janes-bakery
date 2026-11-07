from decimal import Decimal

from sqlalchemy import (
    Integer, Numeric, ForeignKey,
    CheckConstraint, Computed
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OrderItem(Base):
    __tablename__ = "order_item"

    order_item_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("customer_order.order_id"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.product_id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    cost_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    subtotal: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        Computed("quantity * unit_price", persisted=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_item_quantity"),
        CheckConstraint("unit_price >= 0", name="check_item_price"),
        CheckConstraint("cost_price IS NULL OR cost_price >= 0", name="check_item_cost_price"),
    )
