from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, String, Text, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "product"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("administrator.admin_id"),
        nullable=False
    )

    product_name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    cost_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    date_added: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=True,
    )