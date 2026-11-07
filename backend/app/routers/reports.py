from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.payment import Payment
from app.models.customer_order import CustomerOrder
from app.models.order_item import OrderItem
from app.models.product import Product

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)


@router.get("/summary")
def get_report_summary(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    total_sales = db.query(
        func.coalesce(func.sum(Payment.payment_amount), 0)
    ).filter(
        Payment.payment_status == "Successful"
    ).scalar()

    total_orders = db.query(
        func.count(CustomerOrder.order_id)
    ).scalar()

    successful_payments = db.query(
        func.count(Payment.payment_id)
    ).filter(
        Payment.payment_status == "Successful"
    ).scalar()

    pending_orders = db.query(
        func.count(CustomerOrder.order_id)
    ).filter(
        CustomerOrder.order_status == "Pending"
    ).scalar()

    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "successful_payments": successful_payments,
        "pending_orders": pending_orders
    }


@router.get("/profit")
def get_profit_report(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    item_profit = (
        OrderItem.unit_price - func.coalesce(
            getattr(OrderItem, "cost_price", Product.cost_price),
            Product.cost_price
        )
    ) * OrderItem.quantity

    estimated_profit = db.query(
        func.coalesce(func.sum(item_profit), 0)
    ).join(
        Product,
        OrderItem.product_id == Product.product_id
    ).join(
        CustomerOrder,
        OrderItem.order_id == CustomerOrder.order_id
    ).join(
        Payment,
        Payment.order_id == CustomerOrder.order_id
    ).filter(
        Payment.payment_status == "Successful"
    ).scalar()

    return {
        "estimated_profit": estimated_profit,
        "calculation": (
            "Uses the cost price saved with each order item. Older order items "
            "without a saved cost price use the product's current cost price."
        )
    }


@router.get("/stock")
def get_stock_report(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    products = db.query(Product).order_by(Product.product_name).all()

    return [
        {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "cost_price": product.cost_price,
            "selling_price": product.selling_price,
            "stock_quantity": product.stock_quantity
        }
        for product in products
    ]
