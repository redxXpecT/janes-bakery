from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer, Numeric, DateTime,
    ForeignKey, func, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Receipt(Base):
    __tablename__ = "receipt"

    receipt_id: Mapped[int] = mapped_column(
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

    receipt_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=True,
    )

    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "total_amount >= 0",
            name="check_receipt_total"
        ),
    )