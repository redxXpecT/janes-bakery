from datetime import date

from sqlalchemy import (
    Integer, String, Text, Date,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CustomOrder(Base):
    __tablename__ = "customorder"

    custom_order_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    customer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("customer.customer_id"),
        nullable=False
    )

    order_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("customer_order.order_id"),
        nullable=True
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.product_id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    customization_details: Mapped[str] = mapped_column(Text, nullable=False)

    special_request: Mapped[str | None] = mapped_column(Text, nullable=True)

    required_date: Mapped[date] = mapped_column(Date, nullable=False)

    custom_order_status: Mapped[str | None] = mapped_column(
        String(30),
        default="Pending",
        nullable=True,
    )