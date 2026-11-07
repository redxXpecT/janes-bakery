from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer, Numeric, DateTime, String,
    ForeignKey, Enum, func, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CustomerOrder(Base):
    __tablename__ = "customer_order"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    customer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("customer.customer_id"),
        nullable=False
    )

    order_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=True,
    )

    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order_status: Mapped[str | None] = mapped_column(
        Enum(
            "Pending", "Confirmed", "Processing",
            "Ready", "Out for Delivery", "Completed",
            "Cancelled"
        ),
        default="Pending",
        nullable=True,
    )

    delivery_method: Mapped[str] = mapped_column(
        Enum("Delivery", "Pickup"),
        nullable=False
    )

    delivery_address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "total_amount >= 0",
            name="check_order_total"
        ),
    )