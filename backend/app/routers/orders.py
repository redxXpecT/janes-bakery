import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin, get_current_customer
from app.models.custom_order import CustomOrder
from app.models.shopping_cart import ShoppingCart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.customer_order import CustomerOrder
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.schemas.customer_order import OrderCheckoutRequest, OrderStatus

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"]
)


class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus


def validate_fulfilment(order_data: OrderCheckoutRequest):
    if order_data.delivery_method == "Delivery":
        if not order_data.delivery_address or not order_data.delivery_address.strip():
            raise HTTPException(
                status_code=400,
                detail="A delivery address is required"
            )


@router.post("/checkout", status_code=201)
def checkout(
    order_data: OrderCheckoutRequest,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    validate_fulfilment(order_data)
    customer_id = customer["user_id"]

    try:
        cart = db.query(ShoppingCart).filter(
            ShoppingCart.customer_id == customer_id,
            ShoppingCart.cart_status == "Active"
        ).with_for_update().first()

        if not cart:
            raise HTTPException(status_code=404, detail="Active shopping cart not found")

        cart_items = db.query(CartItem).filter(
            CartItem.cart_id == cart.cart_id
        ).all()

        if not cart_items:
            raise HTTPException(status_code=400, detail="Your shopping cart is empty")

        order_lines = []
        total_amount = Decimal("0.00")

        for cart_item in cart_items:
            product = db.query(Product).filter(
                Product.product_id == cart_item.product_id
            ).with_for_update().first()

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {cart_item.product_id} no longer exists"
                )

            if cart_item.quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for {product.product_name}"
                )

            unit_price = Decimal(str(product.selling_price))
            cost_price = Decimal(str(product.cost_price))
            subtotal = unit_price * cart_item.quantity
            order_lines.append({
                "cart_item": cart_item,
                "product": product,
                "unit_price": unit_price,
                "cost_price": cost_price,
                "subtotal": subtotal
            })
            total_amount += subtotal

        new_order = CustomerOrder(
            customer_id=customer_id,
            total_amount=total_amount,
            order_status="Pending",
            delivery_method=order_data.delivery_method,
            delivery_address=(
                (order_data.delivery_address or "").strip()
                if order_data.delivery_method == "Delivery"
                else None
            )
        )
        db.add(new_order)
        db.flush()

        for line in order_lines:
            product = line["product"]
            cart_item = line["cart_item"]

            db.add(OrderItem(
                order_id=new_order.order_id,
                product_id=product.product_id,
                quantity=cart_item.quantity,
                unit_price=line["unit_price"],
                cost_price=line["cost_price"]
            ))

            # Stock is reserved when checkout succeeds.
            product.stock_quantity -= cart_item.quantity

        cart.cart_status = "Converted"
        db.commit()
        db.refresh(new_order)

        return {
            "message": "Order placed successfully. Complete payment to confirm your order.",
            "order_id": new_order.order_id,
            "order_date": new_order.order_date,
            "total_amount": new_order.total_amount,
            "order_status": new_order.order_status,
            "delivery_method": new_order.delivery_method,
            "delivery_address": new_order.delivery_address
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Cart checkout failed for customer_id=%s", customer_id)
        raise HTTPException(
            status_code=500,
            detail="Order could not be placed. Check the backend terminal for the detailed database error."
        ) from exc


@router.post("/custom-checkout/{custom_order_id}", status_code=201)
def checkout_custom_order(
    custom_order_id: int,
    order_data: OrderCheckoutRequest,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    validate_fulfilment(order_data)
    customer_id = customer["user_id"]

    try:
        custom_order = db.query(CustomOrder).filter(
            CustomOrder.custom_order_id == custom_order_id,
            CustomOrder.customer_id == customer_id
        ).with_for_update().first()

        if not custom_order:
            raise HTTPException(status_code=404, detail="Custom order not found")

        if custom_order.order_id is not None:
            raise HTTPException(
                status_code=409,
                detail="This custom order has already been checked out"
            )

        product = db.query(Product).filter(
            Product.product_id == custom_order.product_id
        ).with_for_update().first()

        if not product:
            raise HTTPException(status_code=404, detail="Selected product no longer exists")

        if custom_order.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.product_name}"
            )

        unit_price = Decimal(str(product.selling_price))
        cost_price = Decimal(str(product.cost_price))
        total_amount = unit_price * custom_order.quantity

        new_order = CustomerOrder(
            customer_id=customer_id,
            total_amount=total_amount,
            order_status="Pending",
            delivery_method=order_data.delivery_method,
            delivery_address=(
                (order_data.delivery_address or "").strip()
                if order_data.delivery_method == "Delivery"
                else None
            )
        )
        db.add(new_order)
        db.flush()

        db.add(OrderItem(
            order_id=new_order.order_id,
            product_id=product.product_id,
            quantity=custom_order.quantity,
            unit_price=unit_price,
            cost_price=cost_price
        ))

        product.stock_quantity -= custom_order.quantity
        custom_order.order_id = new_order.order_id

        db.commit()
        db.refresh(new_order)

        return {
            "message": "Custom order checkout successful. Complete payment to confirm your order.",
            "custom_order_id": custom_order.custom_order_id,
            "order_id": new_order.order_id,
            "product_name": product.product_name,
            "quantity": custom_order.quantity,
            "unit_price": unit_price,
            "total_amount": new_order.total_amount,
            "order_status": new_order.order_status,
            "delivery_method": new_order.delivery_method,
            "delivery_address": new_order.delivery_address
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception(
            "Custom checkout failed for custom_order_id=%s customer_id=%s",
            custom_order_id,
            customer_id
        )
        raise HTTPException(
            status_code=500,
            detail="Custom order checkout failed. Check the backend terminal for the detailed database error."
        ) from exc


@router.get("/my-orders")
def get_my_orders(
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    return db.query(CustomerOrder).filter(
        CustomerOrder.customer_id == customer["user_id"]
    ).order_by(CustomerOrder.order_date.desc()).all()


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer)
):
    order = db.query(CustomerOrder).filter(
        CustomerOrder.order_id == order_id,
        CustomerOrder.customer_id == customer["user_id"]
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_items = db.query(OrderItem).filter(
        OrderItem.order_id == order.order_id
    ).all()

    return {"order": order, "items": order_items}


@router.get("/")
def get_all_orders(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    return db.query(CustomerOrder).order_by(
        CustomerOrder.order_date.desc()
    ).all()


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    try:
        order = db.query(CustomerOrder).filter(
            CustomerOrder.order_id == order_id
        ).with_for_update().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        new_status = status_data.order_status

        if order.order_status == "Cancelled" and new_status != "Cancelled":
            raise HTTPException(
                status_code=409,
                detail="A cancelled order cannot be reopened"
            )

        if new_status == "Cancelled" and order.order_status != "Cancelled":
            payment = db.query(Payment).filter(
                Payment.order_id == order.order_id
            ).with_for_update().first()

            if payment and payment.payment_status == "Successful":
                raise HTTPException(
                    status_code=409,
                    detail="This order has already been paid. Process the refund before cancelling it."
                )

            if payment and payment.payment_status == "Pending":
                raise HTTPException(
                    status_code=409,
                    detail="This order has a payment awaiting verification. Verify the payment before cancelling the order."
                )

            order_items = db.query(OrderItem).filter(
                OrderItem.order_id == order.order_id
            ).all()

            for item in order_items:
                product = db.query(Product).filter(
                    Product.product_id == item.product_id
                ).with_for_update().first()

                if product:
                    product.stock_quantity += item.quantity

        order.order_status = new_status
        db.commit()
        db.refresh(order)

        return {
            "message": "Order status updated successfully",
            "order_id": order.order_id,
            "order_status": order.order_status
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Order status could not be updated"
        ) from exc
