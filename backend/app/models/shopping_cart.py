from datetime import datetime

from sqlalchemy import (
    Integer, DateTime,
    ForeignKey, Enum, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ShoppingCart(Base):
    __tablename__ = "shopping_cart"

    cart_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    customer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("customer.customer_id"),
        nullable=False
    )

    date_created: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=True,
    )

    cart_status: Mapped[str | None] = mapped_column(
        Enum("Active", "Converted", "Abandoned"),
        default="Active",
        nullable=True,
    )