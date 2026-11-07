from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer, Numeric, String, DateTime,
    ForeignKey, Enum, func, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Payment(Base):
    __tablename__ = "payment"

    payment_id: Mapped[int] = mapped_column(
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

    payment_method: Mapped[str] = mapped_column(
        Enum("Mobile Money", "Cash", "Card", "Bank Transfer"),
        nullable=False
    )

    payment_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    payment_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=True,
    )

    payment_status: Mapped[str | None] = mapped_column(
        Enum("Pending", "Successful", "Failed", "Refunded"),
        default="Pending",
        nullable=True,
    )

    transaction_reference: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "payment_amount >= 0",
            name="check_payment_amount"
        ),
    )