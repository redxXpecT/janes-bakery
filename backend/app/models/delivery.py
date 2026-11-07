from datetime import datetime

from sqlalchemy import (
    Integer, String, DateTime,
    ForeignKey, Enum
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Delivery(Base):
    __tablename__ = "delivery"

    delivery_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("customer_order.order_id"),
        unique=True,
        nullable=False
    )

    fulfilment_method: Mapped[str] = mapped_column(
        Enum("Delivery", "Pickup"),
        nullable=False
    )

    delivery_address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    delivery_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    delivery_status: Mapped[str | None] = mapped_column(
        Enum("Pending", "Dispatched", "Delivered", "Failed"),
        default="Pending",
        nullable=True,
    )